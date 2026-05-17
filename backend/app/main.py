"""FastAPI application entrypoint.

Composes:
  * Portfolio surfaces (profile, blog, contact).
  * Knowledge-hub surfaces (sections, notes, search, admin, agent) under
    ``/api/knowledge/*``.

Lifespan responsibilities:
  * Initialise the shared async DB engine (already configured in
    ``app.database.connection``).
  * Seed the knowledge admin user if absent.
  * Bootstrap the knowledge index when ``KNOWLEDGE_INDEX_ON_BOOT`` is True
    AND the notes table is empty (avoids re-running on every cold start).
  * Optionally start the filesystem watcher (local dev only).
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.config import settings
from app.database import connection as db_connection
from app.database.connection import close_db, init_db
from app.middleware import RateLimitMiddleware, limiter  # noqa: F401
from app.routers import blog, contact, profile

logger = logging.getLogger(__name__)


async def _seed_knowledge_admin() -> None:
    """Create the knowledge-hub admin user from settings if it doesn't exist."""
    from app.knowledge.auth import hash_password
    from app.knowledge.models import AdminUser

    if db_connection.async_session_maker is None:
        return

    async with db_connection.async_session_maker() as db:
        result = await db.execute(
            select(AdminUser).where(
                AdminUser.username == settings.knowledge_admin_username
            )
        )
        if result.scalar_one_or_none() is None:
            user = AdminUser(
                username=settings.knowledge_admin_username,
                password_hash=hash_password(
                    settings.knowledge_admin_password
                ),
            )
            db.add(user)
            await db.commit()
            logger.info(
                "Seeded knowledge admin user '%s'",
                settings.knowledge_admin_username,
            )


async def _bootstrap_knowledge_index() -> None:
    """Reindex content on cold start *only* when the notes table is empty."""
    from app.knowledge.indexer import full_reindex, note_count

    if not settings.knowledge_index_on_boot:
        return
    if db_connection.async_session_maker is None:
        return

    async with db_connection.async_session_maker() as db:
        if await note_count(db) > 0:
            logger.info("Knowledge index already populated; skipping bootstrap.")
            return
        result = await full_reindex(db)
        logger.info(
            "Bootstrap reindex complete: %d notes, %d errors.",
            result.indexed,
            len(result.errors),
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup + shutdown."""
    logger.info("Starting CarrierProfile API...")

    try:
        if settings.database_url:
            await init_db()
            logger.info("Database initialised.")
            await _seed_knowledge_admin()
            await _bootstrap_knowledge_index()
        else:
            logger.warning(
                "DATABASE_URL not set — knowledge hub features will be limited."
            )
    except Exception as exc:
        logger.exception("Startup error: %s", exc)

    # Optional file watcher (local dev only — opt-in via env var)
    try:
        from app.knowledge.indexer import start_watcher

        start_watcher(db_connection.async_session_maker)
    except Exception as exc:
        logger.warning("Watcher start failed (non-fatal): %s", exc)

    yield

    logger.info("Shutting down CarrierProfile API...")
    try:
        from app.knowledge.indexer import stop_watcher

        stop_watcher()
    except Exception:
        pass

    try:
        await close_db()
    except Exception as exc:
        logger.warning("Error closing database: %s", exc)


app = FastAPI(
    title="Shubham Khanapure Portfolio API",
    description=(
        "Portfolio backend (profile, blog, contact) + AI Notes Knowledge Hub."
    ),
    version="1.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# ── Portfolio routers (unchanged) ───────────────────────────────────────────
app.include_router(profile.router, prefix="/api", tags=["Profile"])
app.include_router(blog.router, prefix="/api", tags=["Blog"])
app.include_router(contact.router, prefix="/api", tags=["Contact"])

# ── Knowledge hub routers ───────────────────────────────────────────────────
from app.knowledge.routers import (  # noqa: E402  (deferred to keep startup deps tidy)
    admin as knowledge_admin,
    agent as knowledge_agent,
    auth_router as knowledge_auth,
    notes as knowledge_notes,
    search as knowledge_search,
    sections as knowledge_sections,
)

app.include_router(
    knowledge_auth.router,
    prefix="/api/knowledge/auth",
    tags=["Knowledge — Auth"],
)
app.include_router(
    knowledge_sections.router,
    prefix="/api/knowledge",
    tags=["Knowledge — Sections"],
)
app.include_router(
    knowledge_notes.router,
    prefix="/api/knowledge",
    tags=["Knowledge — Notes"],
)
app.include_router(
    knowledge_search.router,
    prefix="/api/knowledge",
    tags=["Knowledge — Search"],
)
app.include_router(
    knowledge_admin.router,
    prefix="/api/knowledge/admin",
    tags=["Knowledge — Admin"],
)
app.include_router(
    knowledge_agent.router,
    prefix="/api/knowledge/agent",
    tags=["Knowledge — Agent (Phase B)"],
)


@app.get("/")
async def root():
    return {
        "message": "Shubham Khanapure Portfolio API",
        "version": app.version,
    }


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/knowledge/health")
async def knowledge_health():
    """Knowledge-hub-scoped health probe (counts notes + sections)."""
    if db_connection.async_session_maker is None:
        return {"status": "unconfigured", "note_count": 0, "section_count": 0}

    from sqlalchemy import func

    from app.knowledge.models import Note, Section

    async with db_connection.async_session_maker() as db:
        notes_q = await db.execute(select(func.count(Note.id)))
        sections_q = await db.execute(select(func.count(Section.id)))
        return {
            "status": "ok",
            "note_count": int(notes_q.scalar_one() or 0),
            "section_count": int(sections_q.scalar_one() or 0),
        }
