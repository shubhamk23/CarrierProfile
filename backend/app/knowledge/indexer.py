"""Filesystem → Postgres indexer for the knowledge hub.

Phase 4 hardening:
  * Postgres-only. The legacy SQLite/FTS5 branch is gone; ``notes.search_vector``
    is a STORED generated column maintained by Postgres itself.
  * The watchdog file watcher is opt-in via ``settings.knowledge_enable_watcher``.
    Vercel serverless functions can't host long-lived threads — keep this False
    in production and rely on the empty-DB bootstrap reindex + the admin
    ``POST /api/knowledge/admin/reindex`` endpoint instead.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.knowledge.markdown_utils import parse_note_file
from app.knowledge.models import Note, Section

logger = logging.getLogger(__name__)


class IndexResult:
    """Tally for a single reindex pass."""

    def __init__(self) -> None:
        self.indexed: int = 0
        self.errors: List[str] = []


def _content_root() -> Path:
    """Resolve the absolute content-dir from settings."""
    root = Path(settings.knowledge_content_dir)
    if not root.is_absolute():
        # Resolve relative to the backend package root (parent of `app/`).
        root = Path(__file__).resolve().parents[2] / root
    return root


async def _upsert_section(db: AsyncSession, folder: Path) -> Optional[int]:
    """Read ``_section.json`` and upsert the section row. Returns the row id."""
    section_json_path = folder / "_section.json"

    if section_json_path.exists():
        try:
            meta = json.loads(section_json_path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.error("Failed to parse %s: %s", section_json_path, exc)
            return None
    else:
        meta = {
            "title": folder.name.replace("-", " ").title(),
            "description": None,
            "icon": None,
            "sort_order": 99,
        }

    slug = folder.name
    result = await db.execute(select(Section).where(Section.slug == slug))
    section = result.scalar_one_or_none()

    if section is None:
        section = Section(
            slug=slug,
            title=meta.get("title", slug),
            description=meta.get("description"),
            icon=meta.get("icon"),
            sort_order=meta.get("sort_order", 99),
        )
        db.add(section)
        await db.flush()
    else:
        section.title = meta.get("title", section.title)
        section.description = meta.get("description", section.description)
        section.icon = meta.get("icon", section.icon)
        section.sort_order = meta.get("sort_order", section.sort_order)
        await db.flush()

    return section.id


async def _upsert_note(
    db: AsyncSession, md_path: Path, section_id: int
) -> bool:
    """Parse a markdown file and upsert the note row. Returns True on success."""
    try:
        parsed = parse_note_file(md_path)
    except Exception as exc:
        logger.error("Failed to parse %s: %s", md_path, exc)
        return False

    file_path_str = str(md_path.resolve())
    tags_json = json.dumps(parsed["tags"])

    result = await db.execute(
        select(Note).where(Note.file_path == file_path_str)
    )
    note = result.scalar_one_or_none()

    if note is None:
        note = Note(
            slug=parsed["slug"],
            section_id=section_id,
            title=parsed["title"],
            summary=parsed["summary"],
            tags=tags_json,
            visibility=parsed["visibility"],
            level=parsed["level"],
            file_path=file_path_str,
            word_count=parsed["word_count"],
            read_time=parsed["read_time"],
        )
        db.add(note)
    else:
        note.slug = parsed["slug"]
        note.section_id = section_id
        note.title = parsed["title"]
        note.summary = parsed["summary"]
        note.tags = tags_json
        note.visibility = parsed["visibility"]
        note.level = parsed["level"]
        note.word_count = parsed["word_count"]
        note.read_time = parsed["read_time"]

    await db.flush()
    return True


async def full_reindex(db: AsyncSession) -> IndexResult:
    """Scan the content directory and rebuild all sections + notes.

    Idempotent: re-running against an already-indexed DB produces no diff
    apart from updated_at timestamps.
    """
    result = IndexResult()
    content_dir = _content_root().resolve()

    if not content_dir.exists():
        content_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Created content directory: %s", content_dir)

    for folder in sorted(content_dir.iterdir()):
        if not folder.is_dir():
            continue

        section_id = await _upsert_section(db, folder)
        if section_id is None:
            result.errors.append(f"Could not index section: {folder.name}")
            continue

        for md_path in sorted(folder.glob("*.md")):
            ok = await _upsert_note(db, md_path, section_id)
            if ok:
                result.indexed += 1
            else:
                result.errors.append(str(md_path))

    await db.commit()
    logger.info(
        "Reindex complete: %d notes indexed, %d errors",
        result.indexed,
        len(result.errors),
    )
    return result


async def note_count(db: AsyncSession) -> int:
    """How many notes are currently indexed (used for bootstrap decisions)."""
    from sqlalchemy import func

    result = await db.execute(select(func.count(Note.id)))
    return int(result.scalar_one() or 0)


# ── Filesystem watcher (local dev only) ──────────────────────────────────────

_observer = None


def start_watcher(session_factory) -> None:
    """Start the watchdog observer when ``knowledge_enable_watcher`` is True.

    No-op on Vercel/production. Local development opts in via the env var
    ``KNOWLEDGE_ENABLE_WATCHER=true``.
    """
    global _observer
    if not settings.knowledge_enable_watcher:
        logger.info("Knowledge watcher disabled (serverless-safe default).")
        return

    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except Exception as exc:
        logger.warning("watchdog not available, watcher disabled: %s", exc)
        return

    handler_impl = _WatcherHandler(session_factory)

    class _FSHandler(FileSystemEventHandler):
        def on_modified(self, event):
            handler_impl.on_modified(event)

        def on_created(self, event):
            handler_impl.on_created(event)

        def on_deleted(self, event):
            handler_impl.on_deleted(event)

    content_dir = str(_content_root().resolve())
    _observer = Observer()
    _observer.schedule(_FSHandler(), content_dir, recursive=True)
    _observer.start()
    logger.info("File watcher started on: %s", content_dir)


def stop_watcher() -> None:
    """Stop the file watcher (no-op if it was never started)."""
    global _observer
    if _observer is not None:
        _observer.stop()
        _observer.join()
        _observer = None
        logger.info("File watcher stopped.")


class _WatcherHandler:
    """Bridges watchdog sync events to the async indexer."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def _run_async(self, coro) -> None:
        import asyncio

        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(coro)
        finally:
            loop.close()

    async def _handle_md_change(self, path: str) -> None:
        md_path = Path(path)
        if not md_path.exists() or md_path.name == "_section.json":
            return
        section_folder = md_path.parent
        async with self._session_factory() as db:
            section_id = await _upsert_section(db, section_folder)
            if section_id:
                await _upsert_note(db, md_path, section_id)
                await db.commit()
                logger.info("Re-indexed: %s", md_path.name)

    async def _handle_delete(self, path: str) -> None:
        md_path = Path(path)
        file_path_str = str(md_path.resolve())
        async with self._session_factory() as db:
            result = await db.execute(
                select(Note).where(Note.file_path == file_path_str)
            )
            note = result.scalar_one_or_none()
            if note:
                await db.delete(note)
                await db.commit()
                logger.info("Removed from index: %s", md_path.name)

    def on_modified(self, event) -> None:
        if not event.is_directory and event.src_path.endswith(".md"):
            self._run_async(self._handle_md_change(event.src_path))

    def on_created(self, event) -> None:
        if not event.is_directory and event.src_path.endswith(".md"):
            self._run_async(self._handle_md_change(event.src_path))

    def on_deleted(self, event) -> None:
        if not event.is_directory and event.src_path.endswith(".md"):
            self._run_async(self._handle_delete(event.src_path))
