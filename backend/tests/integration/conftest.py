"""Integration-test fixtures: in-memory SQLite + AsyncClient.

We hand-wire the FastAPI app over an in-memory SQLite engine so we don't
need Docker for the bulk of integration coverage. The Postgres-only search
ranking path lives in tests/integration/test_search_pg.py.
"""

from __future__ import annotations

from pathlib import Path
from typing import AsyncIterator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool


@pytest_asyncio.fixture
async def app_with_db(
    monkeypatch, tmp_path: Path
) -> AsyncIterator[tuple[AsyncClient, AsyncEngine, async_sessionmaker]]:
    """Yield (client, engine, session_factory) bound to a fresh in-memory DB.

    Disables the lifespan auto-bootstrap so each test controls its own
    seeding. CORS origin is fixed to a known value so we can verify the
    headers.
    """
    # Build a sample content tree the indexer can pick up if a test asks.
    content_root = tmp_path / "content"
    (content_root / "nlp").mkdir(parents=True)
    (content_root / "nlp" / "_section.json").write_text(
        '{"title":"NLP","description":"LLMs.","icon":"💬","sort_order":1}'
    )
    (content_root / "nlp" / "attention.md").write_text(
        '---\n'
        'title: "Attention Mechanism"\n'
        'slug: attention\n'
        'summary: "Self-attention deep dive"\n'
        'tags: ["transformer", "attention"]\n'
        'visibility: public\n'
        '---\n\nAttention computes weighted sums.\n'
    )

    from app.config import settings as s

    monkeypatch.setattr(s, "knowledge_content_dir", str(content_root))
    monkeypatch.setattr(s, "knowledge_index_on_boot", False)
    monkeypatch.setattr(s, "knowledge_enable_watcher", False)
    monkeypatch.setattr(
        s, "allowed_origins", ["http://localhost:3000"]
    )

    # Build engine + override the app's session factory + get_db dep.
    # StaticPool keeps a single shared connection so ":memory:" data
    # survives across sessions for the duration of the test.
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    factory = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    from app.database.connection import Base

    # Drop the Postgres-only generated column for SQLite create_all.
    notes_table = Base.metadata.tables.get("notes")
    removed = None
    if notes_table is not None and "search_vector" in notes_table.c:
        removed = notes_table.c["search_vector"]
        notes_table._columns.remove(removed)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Patch the app's own connection module so it uses our engine.
    import app.database.connection as conn_mod

    monkeypatch.setattr(conn_mod, "engine", engine)
    monkeypatch.setattr(conn_mod, "async_session_maker", factory)

    # Disable Resend so the contact router doesn't try to send mail.
    monkeypatch.setattr(s, "resend_api_key", "")

    # Build a fresh app instance whose lifespan is short-circuited.
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client, engine, factory

    await engine.dispose()
    if removed is not None and notes_table is not None:
        notes_table._columns.add(removed)


@pytest_asyncio.fixture
async def seeded_app(app_with_db):
    """Same as app_with_db, but pre-runs full_reindex + seeds the admin user."""
    client, engine, factory = app_with_db
    from app.knowledge.auth import hash_password
    from app.knowledge.indexer import full_reindex
    from app.knowledge.models import AdminUser

    async with factory() as session:
        await full_reindex(session)
        session.add(
            AdminUser(
                username="admin",
                password_hash=hash_password("test-password"),
            )
        )
        await session.commit()

    return client, engine, factory
