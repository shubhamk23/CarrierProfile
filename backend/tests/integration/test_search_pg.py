"""Postgres-only integration tests for the FTS search router.

Skipped automatically when ``TEST_DATABASE_URL`` is not set. CI runs these
against a Postgres service container.
"""

import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

pytestmark = [pytest.mark.integration, pytest.mark.postgres]


def _require_pg() -> str:
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL not set — skipping Postgres FTS tests.")
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


@pytest_asyncio.fixture
async def pg_app(monkeypatch, tmp_path):
    """A full app instance backed by a real Postgres test database."""
    url = _require_pg()

    # Fixture content with diverse vocabulary for ranking checks.
    root = tmp_path / "content"
    (root / "nlp").mkdir(parents=True)
    (root / "nlp" / "_section.json").write_text(
        '{"title":"NLP","sort_order":1}'
    )
    (root / "nlp" / "attention.md").write_text(
        '---\n'
        'title: "Attention Mechanism"\n'
        'slug: attention\n'
        'summary: "Self-attention and multi-head attention"\n'
        'tags: ["transformer", "attention"]\n'
        '---\n\nAttention computes weighted sums.\n'
    )
    (root / "nlp" / "rag.md").write_text(
        '---\n'
        'title: "Retrieval-Augmented Generation"\n'
        'slug: rag\n'
        'summary: "Grounding LLMs with retrieval"\n'
        'tags: ["rag", "retrieval"]\n'
        '---\n\nRAG combines retrieval with generation.\n'
    )

    from app.config import settings as s

    monkeypatch.setattr(s, "knowledge_content_dir", str(root))
    monkeypatch.setattr(s, "knowledge_index_on_boot", False)
    monkeypatch.setattr(s, "knowledge_enable_watcher", False)
    monkeypatch.setattr(s, "database_url", url)
    monkeypatch.setattr(s, "allowed_origins", ["http://localhost:3000"])

    engine = create_async_engine(url, pool_pre_ping=True)
    factory = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    # Drop+create the knowledge tables for a clean slate.
    from app.database.connection import Base
    from app.knowledge.indexer import full_reindex
    from app.knowledge.models import AdminUser, Note, Section  # noqa: F401

    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS notes CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS sections CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS admin_users CASCADE"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        await conn.run_sync(
            lambda c: Base.metadata.create_all(
                c,
                tables=[
                    Base.metadata.tables["sections"],
                    Base.metadata.tables["notes"],
                    Base.metadata.tables["admin_users"],
                ],
            )
        )
        # The generated tsvector + GIN index aren't created by create_all
        # because they live outside the SQLAlchemy schema definition. We
        # add them here so the search router has something to query.
        await conn.execute(
            text(
                "ALTER TABLE notes ADD COLUMN search_vector tsvector "
                "GENERATED ALWAYS AS ( "
                "setweight(to_tsvector('english', coalesce(title,'')), 'A') || "
                "setweight(to_tsvector('english', coalesce(summary,'')), 'B') || "
                "setweight(to_tsvector('english', coalesce(tags,'')), 'C') "
                ") STORED"
            )
        )
        await conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS notes_search_idx "
                "ON notes USING GIN (search_vector)"
            )
        )

    async with factory() as session:
        await full_reindex(session)

    import app.database.connection as conn_mod

    monkeypatch.setattr(conn_mod, "engine", engine)
    monkeypatch.setattr(conn_mod, "async_session_maker", factory)

    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS notes CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS sections CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS admin_users CASCADE"))
    await engine.dispose()


class TestSearchRanking:
    @pytest.mark.asyncio
    async def test_finds_attention_note(self, pg_app):
        res = await pg_app.get("/api/knowledge/search?q=attention")
        assert res.status_code == 200
        body = res.json()
        assert body["total"] >= 1
        titles = [r["title"] for r in body["results"]]
        assert "Attention Mechanism" in titles

    @pytest.mark.asyncio
    async def test_finds_rag_note(self, pg_app):
        body = (await pg_app.get("/api/knowledge/search?q=retrieval")).json()
        slugs = {r["slug"] for r in body["results"]}
        assert "rag" in slugs

    @pytest.mark.asyncio
    async def test_empty_query_is_rejected(self, pg_app):
        # q is required + min_length=1 → 422 on empty.
        assert (await pg_app.get("/api/knowledge/search?q=")).status_code == 422

    @pytest.mark.asyncio
    async def test_gibberish_returns_empty(self, pg_app):
        body = (
            await pg_app.get(
                "/api/knowledge/search?q=zzzqqqzzzqqqzzzqqq"
            )
        ).json()
        assert body["total"] == 0
        assert body["results"] == []

    @pytest.mark.asyncio
    async def test_title_outranks_body(self, pg_app):
        # "attention" is in the attention title (weight A) and in the rag body.
        body = (
            await pg_app.get("/api/knowledge/search?q=attention")
        ).json()
        assert body["results"][0]["title"] == "Attention Mechanism"
