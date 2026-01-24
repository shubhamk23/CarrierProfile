from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import json
from pathlib import Path

from app.models import ContactMessage, ContactResponse
from app.database.models import ContactMessage as ContactMessageDB
from app.database.connection import get_db
from app.middleware import limiter
from app.config import settings

router = APIRouter()

# Store messages in a JSON file (fallback when database is unavailable)
MESSAGES_PATH = Path(__file__).parent.parent / "data" / "messages.json"


def save_message_to_file(message: ContactMessage, request: Request) -> None:
    """Save contact message to file (fallback storage)"""
    messages = []

    # Ensure data directory exists
    MESSAGES_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Load existing messages
    if MESSAGES_PATH.exists():
        try:
            with open(MESSAGES_PATH, "r") as f:
                messages = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            messages = []

    # Add new message
    messages.append({
        "id": len(messages) + 1,
        "name": message.name,
        "email": message.email,
        "subject": message.subject,
        "message": message.message,
        "timestamp": datetime.now().isoformat(),
        "read": False,
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    })

    # Save back to file
    with open(MESSAGES_PATH, "w") as f:
        json.dump(messages, f, indent=2)


async def send_email_notification(message: ContactMessage) -> None:
    """Send email notification via Resend"""
    if not settings.resend_api_key:
        print("⚠️  Resend API key not configured, skipping email notification")
        return

    try:
        import resend
        resend.api_key = settings.resend_api_key

        params = {
            "from": settings.resend_from_email,
            "to": [settings.resend_to_email],
            "subject": f"Portfolio Contact: {message.subject}",
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
                            <span class="label">From:</span> {message.name}
                        </div>
                        <div class="field">
                            <span class="label">Email:</span> {message.email}
                        </div>
                        <div class="field">
                            <span class="label">Subject:</span> {message.subject}
                        </div>
                        <div class="field">
                            <span class="label">Message:</span>
                            <div class="message-box">
                                {message.message.replace(chr(10), '<br>')}
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
        }

        email = resend.Emails.send(params)
        print(f"✅ Email notification sent successfully: {email}")
    except ImportError:
        print("⚠️  Resend package not installed, skipping email notification")
    except Exception as e:
        print(f"❌ Failed to send email notification: {e}")


@router.post("/contact", response_model=ContactResponse)
@limiter.limit(f"{settings.rate_limit_times}/{settings.rate_limit_seconds} seconds")
async def submit_contact_form(
    request: Request,
    message: ContactMessage,
    db: AsyncSession = Depends(get_db)
):
    """Submit a contact form message"""
    try:
        # Save to database
        db_message = ContactMessageDB(
            name=message.name,
            email=message.email,
            subject=message.subject,
            message=message.message,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        db.add(db_message)
        await db.commit()
        print(f"✅ Message saved to database: {message.name} - {message.subject}")

    except Exception as db_error:
        print(f"⚠️  Database save failed: {db_error}")
        # Fallback to file storage
        try:
            save_message_to_file(message, request)
            print(f"✅ Message saved to file (fallback): {message.name}")
        except Exception as file_error:
            print(f"❌ File save also failed: {file_error}")
            raise HTTPException(
                status_code=500,
                detail="Failed to save message. Please try again later."
            )

    # Send email notification (non-blocking, errors are logged but don't fail the request)
    try:
        await send_email_notification(message)
    except Exception as email_error:
        print(f"⚠️  Email notification failed: {email_error}")
        # Don't fail the request if email fails

    return ContactResponse(
        success=True,
        message="Thank you for your message! I'll get back to you soon."
    )


@router.get("/contact/messages")
async def get_messages(db: AsyncSession = Depends(get_db)):
    """Get all contact messages (admin endpoint)"""
    try:
        from sqlalchemy import select
        result = await db.execute(
            select(ContactMessageDB).order_by(ContactMessageDB.timestamp.desc())
        )
        messages = result.scalars().all()
        return [msg.to_dict() for msg in messages]
    except Exception as db_error:
        print(f"⚠️  Database query failed: {db_error}")
        # Fallback to file storage
        if not MESSAGES_PATH.exists():
            return []

        try:
            with open(MESSAGES_PATH, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
