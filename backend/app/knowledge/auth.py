"""JWT helpers for the knowledge-hub admin namespace.

Kept independent from any future portfolio auth: reads `knowledge_*`
settings from the global ``settings`` object so the admin panel can be
secured with its own secret and credentials.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/knowledge/auth/token")


def hash_password(password: str) -> str:
    """Bcrypt-hash a plaintext password."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against its bcrypt hash."""
    return pwd_context.verify(plain, hashed)


def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """Create a signed JWT for an admin session."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(hours=settings.knowledge_jwt_expire_hours)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.knowledge_jwt_secret_key,
        algorithm=settings.knowledge_jwt_algorithm,
    )


async def get_current_admin(token: str = Depends(oauth2_scheme)) -> str:
    """FastAPI dependency: return the admin username for a valid JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.knowledge_jwt_secret_key,
            algorithms=[settings.knowledge_jwt_algorithm],
        )
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError as exc:
        raise credentials_exception from exc
