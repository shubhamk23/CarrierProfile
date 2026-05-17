from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
from app.config import settings

# Create async engine
# For PostgreSQL, replace postgresql:// with postgresql+asyncpg://
database_url = settings.database_url
if database_url and database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = None
async_session_maker = None


def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")


if database_url:
    if _is_sqlite(database_url):
        # SQLite (in-memory and on-disk) — minimal config, no Postgres pool args.
        engine = create_async_engine(
            database_url,
            echo=settings.debug,
            connect_args={"check_same_thread": False},
        )
    else:
        engine = create_async_engine(
            database_url,
            echo=settings.debug,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_recycle=settings.database_pool_recycle,
            pool_pre_ping=settings.database_pool_pre_ping,
            # Important for serverless: don't maintain persistent connections
            pool_timeout=30,
            connect_args={
                "server_settings": {
                    "application_name": "carrier_profile_api"
                },
            },
        )

    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

# Base class for SQLAlchemy models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions in FastAPI routes.

    Usage:
        @router.post("/contact")
        async def create_contact(message: ContactMessage, db: AsyncSession = Depends(get_db)):
            ...
    """
    if not async_session_maker:
        raise RuntimeError("Database is not configured. Set DATABASE_URL environment variable.")

    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables (creates tables if they don't exist)"""
    if not engine:
        return

    async with engine.begin() as conn:
        # Import all models here to ensure they are registered with Base
        from app.database import models  # noqa: F401

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections (cleanup on shutdown)"""
    if engine:
        await engine.dispose()
