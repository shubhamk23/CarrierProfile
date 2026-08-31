from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator, Optional
from app.config import settings

# Create async engine
# For PostgreSQL, replace postgresql:// with postgresql+asyncpg://
database_url = settings.database_url
if database_url and database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = None
async_session_maker = None

if database_url:
    engine = create_async_engine(
        database_url,
        echo=settings.debug,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_recycle=settings.database_pool_recycle,
        pool_pre_ping=settings.database_pool_pre_ping,
        # Fail fast on serverless instead of holding the function open
        pool_timeout=5,
        connect_args={
            "server_settings": {"application_name": "carrier_profile_api"},
            # Required when connecting through Supabase's PgBouncer pooler in
            # transaction mode: asyncpg's server-side prepared statement cache
            # produces "prepared statement already exists" errors otherwise.
            "statement_cache_size": 0,
        },
    )

    # Create async session factory
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

# Base class for SQLAlchemy models
Base = declarative_base()


async def get_db() -> AsyncGenerator[Optional[AsyncSession], None]:
    """
    Dependency for getting async database sessions in FastAPI routes.

    Yields None when DATABASE_URL is not configured so callers can fall back
    (e.g. to email-only delivery) instead of the request failing outright.
    Callers own their own commit/rollback; this dependency only manages the
    session lifecycle.
    """
    if not async_session_maker:
        yield None
        return

    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables (creates tables if they don't exist).

    This only covers first-deploy bootstrap; schema changes after that go
    through Alembic migrations (see alembic/versions/), not create_all.
    """
    if not engine:
        return

    async with engine.begin() as conn:
        # Import all models here to ensure they are registered with Base
        from app.database import models  # noqa: F401

        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections (cleanup on shutdown)"""
    if engine:
        await engine.dispose()
