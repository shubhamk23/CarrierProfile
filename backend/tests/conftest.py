"""Shared pytest fixtures for backend tests.

Two engine flavours:
  * ``sqlite_engine`` — used by **unit** tests where we exercise the indexer
    + markdown_utils + sections endpoint without depending on Postgres-specific
    features (FTS, generated columns). The notes ``search_vector`` column is
    skipped on SQLite by selectively dropping it from the model metadata copy
    used in these tests.
  * ``pg_engine`` — opt-in via the ``TEST_DATABASE_URL`` env var. Tests
    decorated with ``@pytest.mark.postgres`` skip cleanly when it isn't set,
    so the CI pipeline that has a Postgres service container runs them while
    a local dev machine without Postgres still gets a green pytest run.

All fixtures live here so individual test files stay focused on assertions.
"""

from __future__ import annotations

import asyncio
import os
import shutil
from pathlib import Path
from typing import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

# Ensure a deterministic settings load that does not need a real DATABASE_URL.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("KNOWLEDGE_JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("KNOWLEDGE_ADMIN_USERNAME", "admin")
os.environ.setdefault("KNOWLEDGE_ADMIN_PASSWORD", "test-password")
os.environ.setdefault("KNOWLEDGE_CONTENT_DIR", "app/content")
os.environ.setdefault("KNOWLEDGE_INDEX_ON_BOOT", "False")
os.environ.setdefault("KNOWLEDGE_ENABLE_WATCHER", "False")


# ── Sample content factory ───────────────────────────────────────────────────


@pytest.fixture
def temp_content_dir(tmp_path: Path) -> Iterator[Path]:
    """A throwaway content/ directory with two sections and three notes."""
    root = tmp_path / "content"
    (root / "nlp").mkdir(parents=True)
    (root / "vision").mkdir()

    (root / "nlp" / "_section.json").write_text(
        '{"title":"NLP","description":"Language stuff.",'
        '"icon":"💬","sort_order":1}'
    )
    (root / "vision" / "_section.json").write_text(
        '{"title":"Vision","description":"Pixels.",'
        '"icon":"👁️","sort_order":2}'
    )

    (root / "nlp" / "attention.md").write_text(
        '---\n'
        'title: "Attention Mechanism"\n'
        'slug: attention\n'
        'summary: "Self-attention deep dive"\n'
        'tags: ["transformer", "attention"]\n'
        'visibility: public\n'
        'level: intermediate\n'
        '---\n\n'
        '# Attention\n\n'
        'Self-attention computes weighted sums over a sequence.\n\n'
        '$$\\text{Attention}(Q,K,V) = \\text{softmax}(QK^T/\\sqrt{d_k})V$$\n'
    )
    (root / "nlp" / "rag.md").write_text(
        '---\n'
        'title: "Retrieval-Augmented Generation"\n'
        'slug: rag\n'
        'summary: "Grounding LLMs with retrieved context."\n'
        'tags: ["rag", "retrieval"]\n'
        'visibility: public\n'
        '---\n\n'
        'RAG combines retrieval with generation.\n'
    )
    (root / "vision" / "yolo.md").write_text(
        '---\n'
        'title: "YOLO Object Detection"\n'
        'slug: yolo\n'
        'tags: ["vision", "detection"]\n'
        'visibility: public\n'
        'level: advanced\n'
        '---\n\n'
        'YOLO is a single-shot detector.\n'
    )

    yield root

    shutil.rmtree(root, ignore_errors=True)


# ── SQLite in-memory engine (unit/integration without Postgres) ──────────────


@pytest_asyncio.fixture
async def sqlite_engine() -> AsyncIterator[AsyncEngine]:
    """A fresh in-memory SQLite engine with the portfolio + knowledge schema.

    We strip the Postgres-only generated ``search_vector`` column when running
    create_all on SQLite so the tables build cleanly. Tests that exercise
    Postgres FTS use the ``pg_engine`` fixture instead.
    """
    from app.database.connection import Base
    from app.knowledge.models import Note  # noqa: F401  (registers model)

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Temporarily drop the Postgres-only generated column so SQLite's
    # create_all does not blow up on "GENERATED ALWAYS AS" syntax.
    notes_table = Base.metadata.tables.get("notes")
    removed = None
    if notes_table is not None and "search_vector" in notes_table.c:
        removed = notes_table.c["search_vector"]
        notes_table._columns.remove(removed)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()
    if removed is not None and notes_table is not None:
        notes_table._columns.add(removed)


@pytest_asyncio.fixture
async def sqlite_session(
    sqlite_engine: AsyncEngine,
) -> AsyncIterator[AsyncSession]:
    """Async session bound to the in-memory SQLite engine."""
    factory = async_sessionmaker(
        sqlite_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with factory() as session:
        yield session


# ── Postgres engine (opt-in via TEST_DATABASE_URL) ───────────────────────────


@pytest_asyncio.fixture
async def pg_engine() -> AsyncIterator[AsyncEngine]:
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is not set — skipping Postgres test.")

    # Accept postgresql:// and convert to asyncpg if needed.
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    engine = create_async_engine(url, pool_pre_ping=True)
    yield engine
    await engine.dispose()
