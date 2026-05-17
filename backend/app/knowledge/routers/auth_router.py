"""Knowledge-hub admin auth router: ``POST /api/knowledge/auth/token``."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.connection import get_db
from app.knowledge.auth import create_access_token, verify_password
from app.knowledge.models import AdminUser
from app.knowledge.schemas import TokenRequest, TokenResponse

router = APIRouter()


@router.post("/token", response_model=TokenResponse)
async def login(req: TokenRequest, db: AsyncSession = Depends(get_db)):
    """Exchange admin credentials for a JWT access token."""
    result = await db.execute(
        select(AdminUser).where(AdminUser.username == req.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    token = create_access_token({"sub": user.username})
    return TokenResponse(
        access_token=token,
        expires_in=settings.knowledge_jwt_expire_hours * 3600,
    )
