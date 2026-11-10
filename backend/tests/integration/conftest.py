"""Fixtures for integration tests that run against a real PostgreSQL.

These are skipped unless DATABASE_URL is set (CI provides a Postgres
service). They never touch settings.database_url, which is read once at
import time by app.database.connection; instead each test builds its own
engine and overrides the get_db dependency.

DANGER: the schema is dropped and rebuilt between tests. Only point
DATABASE_URL at a throwaway database.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

BACKEND_DIR = Path(__file__).resolve().parents[2]
DATABASE_URL = os.environ.get("DATABASE_URL", "")


def pytest_collection_modifyitems(config, items):
    if DATABASE_URL:
        return
    skip = pytest.mark.skip(reason="DATABASE_URL not set; integration tests skipped")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip)


def run_alembic(*args: str) -> subprocess.CompletedProcess:
    """Run the alembic CLI exactly as the deploy checklist does."""
    return subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        cwd=BACKEND_DIR,
        env={**os.environ, "DATABASE_URL": DATABASE_URL},
        capture_output=True,
        text=True,
        check=True,
    )


def reset_schema() -> None:
    """Wipe everything, including alembic_version, whatever state a test left."""
    engine = create_engine(DATABASE_URL, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
    engine.dispose()


@pytest.fixture
def migrated_db():
    """A database freshly migrated to head, wiped again afterwards.

    Wiping the schema (rather than running `alembic downgrade base`) keeps
    teardown working even when a test dropped tables behind Alembic's back.
    """
    reset_schema()
    run_alembic("upgrade", "head")
    yield
    reset_schema()


@pytest_asyncio.fixture
async def db_session_factory(migrated_db):
    url = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    # NullPool: TestClient runs the app on its own event loop, so a pooled
    # asyncpg connection created on the test's loop would be reused across loops.
    engine = create_async_engine(
        url, connect_args={"statement_cache_size": 0}, poolclass=NullPool
    )
    yield async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    await engine.dispose()


@pytest.fixture
def integration_client(db_session_factory):
    """TestClient whose get_db hands out sessions on the real database."""
    from fastapi.testclient import TestClient

    from app.database.connection import get_db
    from app.main import app
    from app.middleware import limiter

    async def override_get_db():
        async with db_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    limiter.reset()
    with TestClient(app, raise_server_exceptions=True) as client:
        yield client
    app.dependency_overrides.clear()
