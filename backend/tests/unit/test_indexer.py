"""Unit tests for app.knowledge.indexer against an in-memory SQLite engine.

These tests don't rely on Postgres-only features (the ``search_vector`` column
is dropped from the metadata copy used here — see ``conftest.sqlite_engine``).
What we verify here is the *filesystem → DB upsert* behaviour, which is the
indexer's actual contract.
"""

import pytest
from sqlalchemy import select

from app.knowledge.indexer import IndexResult, full_reindex, note_count
from app.knowledge.models import Note, Section

pytestmark = pytest.mark.unit


@pytest.fixture
def patched_content_dir(monkeypatch, temp_content_dir):
    """Point ``settings.knowledge_content_dir`` at the fixture content dir."""
    from app.config import settings as s

    monkeypatch.setattr(s, "knowledge_content_dir", str(temp_content_dir))
    return temp_content_dir


class TestFullReindex:
    @pytest.mark.asyncio
    async def test_indexes_sections_and_notes(
        self, sqlite_session, patched_content_dir
    ):
        result = await full_reindex(sqlite_session)
        assert isinstance(result, IndexResult)
        assert result.indexed == 3
        assert result.errors == []

        sections = (await sqlite_session.execute(select(Section))).scalars().all()
        assert {s.slug for s in sections} == {"nlp", "vision"}

        notes = (await sqlite_session.execute(select(Note))).scalars().all()
        slugs = {n.slug for n in notes}
        assert slugs == {"attention", "rag", "yolo"}

    @pytest.mark.asyncio
    async def test_is_idempotent(
        self, sqlite_session, patched_content_dir
    ):
        first = await full_reindex(sqlite_session)
        second = await full_reindex(sqlite_session)
        assert first.indexed == second.indexed
        count = await note_count(sqlite_session)
        assert count == 3   # not 6 — upsert, not insert

    @pytest.mark.asyncio
    async def test_picks_up_new_files_on_rerun(
        self, sqlite_session, patched_content_dir
    ):
        await full_reindex(sqlite_session)
        (patched_content_dir / "nlp" / "transformers.md").write_text(
            '---\n'
            'title: "Transformers"\n'
            'slug: transformers\n'
            '---\n\n'
            'Transformers are made of attention blocks.\n'
        )
        second = await full_reindex(sqlite_session)
        assert second.indexed == 4
        assert await note_count(sqlite_session) == 4

    @pytest.mark.asyncio
    async def test_updates_existing_note_on_content_change(
        self, sqlite_session, patched_content_dir
    ):
        await full_reindex(sqlite_session)
        note_before = (
            await sqlite_session.execute(
                select(Note).where(Note.slug == "attention")
            )
        ).scalar_one()
        words_before = note_before.word_count

        (patched_content_dir / "nlp" / "attention.md").write_text(
            '---\n'
            'title: "Attention Mechanism v2"\n'
            'slug: attention\n'
            'tags: ["transformer", "attention", "new"]\n'
            '---\n\n'
            '# Attention Mechanism v2\n\n'
            'Self-attention computes weighted sums over a sequence using '
            'query, key, and value projections. The dot-product between '
            'query and key vectors determines attention scores, which are '
            'then normalised via softmax and used to weight the value '
            'vectors. Multi-head attention runs several such operations '
            'in parallel to capture different relational patterns.\n'
        )

        await full_reindex(sqlite_session)
        note_after = (
            await sqlite_session.execute(
                select(Note).where(Note.slug == "attention")
            )
        ).scalar_one()
        assert note_after.title == "Attention Mechanism v2"
        assert note_after.word_count != words_before
        # Tag mutation reflected in JSON column.
        assert "new" in note_after.tags

    @pytest.mark.asyncio
    async def test_auto_creates_section_when_section_json_missing(
        self, sqlite_session, tmp_path, monkeypatch
    ):
        root = tmp_path / "content2"
        (root / "no-meta").mkdir(parents=True)
        (root / "no-meta" / "a.md").write_text(
            "---\ntitle: A\nslug: a\n---\nbody\n"
        )

        from app.config import settings as s

        monkeypatch.setattr(s, "knowledge_content_dir", str(root))
        result = await full_reindex(sqlite_session)
        assert result.indexed == 1

        section = (
            await sqlite_session.execute(
                select(Section).where(Section.slug == "no-meta")
            )
        ).scalar_one()
        assert section.title == "No Meta"   # derived from folder name


class TestWatcherGuard:
    """The watchdog watcher must be off by default — Vercel can't host threads."""

    def test_start_watcher_is_noop_when_disabled(self, monkeypatch):
        from app.config import settings as s
        from app.knowledge import indexer

        monkeypatch.setattr(s, "knowledge_enable_watcher", False)
        # If this raised, the test would fail. We also assert no observer set.
        indexer._observer = None
        indexer.start_watcher(session_factory=None)
        assert indexer._observer is None
