"""Postgres full-text search for knowledge notes.

Uses the ``search_vector`` STORED generated column + GIN index created by
migration ``002_knowledge_schema``. Ranking via ``ts_rank``; excerpt via
``ts_headline``.
"""

import json
import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.knowledge.schemas import SearchResponse, SearchResultOut

logger = logging.getLogger(__name__)
router = APIRouter()


_SEARCH_SQL = text(
    """
    SELECT
        n.id,
        n.slug,
        s.slug AS section_slug,
        n.title,
        n.tags,
        ts_headline(
            'english',
            COALESCE(n.summary, '') || ' ' || COALESCE(n.tags, ''),
            plainto_tsquery('english', :query),
            'MaxFragments=1,MaxWords=32,MinWords=5,StartSel=<mark>,StopSel=</mark>'
        ) AS excerpt
    FROM notes n
    JOIN sections s ON n.section_id = s.id
    WHERE n.search_vector @@ plainto_tsquery('english', :query)
      AND n.visibility = 'public'
    ORDER BY ts_rank(n.search_vector, plainto_tsquery('english', :query)) DESC
    LIMIT :limit OFFSET :offset
    """
)

_COUNT_SQL = text(
    """
    SELECT COUNT(*)
    FROM notes n
    WHERE n.search_vector @@ plainto_tsquery('english', :query)
      AND n.visibility = 'public'
    """
)


@router.get("/search", response_model=SearchResponse)
async def search_notes(
    q: str = Query(..., min_length=1, max_length=200),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Ranked full-text search across public notes."""
    query = q.strip()
    if not query:
        return SearchResponse(results=[], total=0, query=q)

    try:
        rows = await db.execute(
            _SEARCH_SQL,
            {"query": query, "limit": limit, "offset": offset},
        )
        count = await db.execute(_COUNT_SQL, {"query": query})
        total = int(count.scalar_one())

        results = [
            SearchResultOut(
                id=row.id,
                slug=row.slug,
                section_slug=row.section_slug,
                title=row.title,
                excerpt=row.excerpt or "",
                tags=json.loads(row.tags or "[]"),
            )
            for row in rows
        ]
    except Exception:
        logger.exception("Search error for query %r", q)
        results = []
        total = 0

    return SearchResponse(results=results, total=total, query=q)
