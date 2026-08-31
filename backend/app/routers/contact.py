import html
import logging

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.concurrency import run_in_threadpool
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ContactMessage, ContactResponse
from app.database.models import ContactMessage as ContactMessageDB
from app.database.connection import get_db
from app.middleware import limiter
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


async def send_email_notification(message: ContactMessage) -> None:
    """Send email notification via Resend. Raises on failure; caller decides
    whether that failure is fatal for the request."""
    import resend

    resend.api_key = settings.resend_api_key

    safe_name = html.escape(message.name)
    safe_email = html.escape(message.email)
    safe_subject = html.escape(message.subject)
    safe_message = html.escape(message.message).replace(chr(10), "<br>")

    # The subject goes into an email header, so strip CR/LF to remove any
    # header-injection primitive before it reaches the mail provider.
    header_subject = " ".join(message.subject.split())

    params = {
        "from": settings.resend_from_email,
        "to": [settings.resend_to_email],
        "subject": f"Portfolio Contact: {header_subject}",
        "html": f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #4F46E5; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9fafb; padding: 20px; border-radius: 0 0 8px 8px; }}
                .field {{ margin-bottom: 15px; }}
                .label {{ font-weight: bold; color: #4F46E5; }}
                .message-box {{ background: white; padding: 15px; border-left: 4px solid #4F46E5; margin-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>New Contact Form Submission</h2>
                </div>
                <div class="content">
                    <div class="field">
                        <span class="label">From:</span> {safe_name}
                    </div>
                    <div class="field">
                        <span class="label">Email:</span> {safe_email}
                    </div>
                    <div class="field">
                        <span class="label">Subject:</span> {safe_subject}
                    </div>
                    <div class="field">
                        <span class="label">Message:</span>
                        <div class="message-box">
                            {safe_message}
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """,
    }

    # resend's SDK is synchronous; keep it off the event loop
    await run_in_threadpool(resend.Emails.send, params)


@router.post("/contact", response_model=ContactResponse)
@limiter.limit(f"{settings.rate_limit_times}/{settings.rate_limit_seconds} seconds")
async def submit_contact_form(
    request: Request,
    message: ContactMessage,
    db: Optional[AsyncSession] = Depends(get_db),
):
    """Submit a contact form message.

    Delivery has two independent channels: persisting to the database and
    emailing a notification. The request succeeds if either one lands; it
    only 500s if both fail (or neither is configured), since the visitor's
    message would otherwise silently vanish.
    """
    db_ok = False
    email_attempted = False
    email_ok = False

    if db is not None:
        try:
            db.add(
                ContactMessageDB(
                    name=message.name,
                    email=message.email,
                    subject=message.subject,
                    message=message.message,
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                )
            )
            await db.commit()
            db_ok = True
        except Exception:
            await db.rollback()
            logger.exception("Failed to save contact message to database")

    if settings.resend_api_key and settings.resend_to_email:
        email_attempted = True
        try:
            await send_email_notification(message)
            email_ok = True
        except Exception:
            logger.exception("Failed to send contact form email notification")

    if db_ok or email_ok:
        return ContactResponse(
            success=True,
            message="Thank you for your message! I'll get back to you soon.",
        )

    logger.error(
        "Contact form submission failed on every channel (db_configured=%s, email_attempted=%s)",
        db is not None,
        email_attempted,
    )
    raise HTTPException(
        status_code=500,
        detail="Failed to submit your message. Please try again later.",
    )
