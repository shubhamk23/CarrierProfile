"""Public read-only section endpoints."""

import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.knowledge.models import Note, Section
from app.knowledge.schemas import NoteCardOut, SectionOut

router = APIRouter()


@router.get("/sections", response_model=List[SectionOut])
async def list_sections(db: AsyncSession = Depends(get_db)):
    """List all sections with public note counts, ordered by sort_order."""
    result = await db.execute(
        select(Section).order_by(Section.sort_order, Section.title)
    )
    sections = result.scalars().all()

    out: List[SectionOut] = []
    for section in sections:
        count_result = await db.execute(
            select(func.count(Note.id)).where(
                Note.section_id == section.id, Note.visibility == "public"
            )
        )
        out.append(
            SectionOut(
                id=section.id,
                slug=section.slug,
                title=section.title,
                description=section.description,
                icon=section.icon,
                sort_order=section.sort_order,
                note_count=int(count_result.scalar_one()),
            )
        )
    return out


@router.get("/sections/{section_slug}")
async def get_section(section_slug: str, db: AsyncSession = Depends(get_db)):
    """Return a section plus its public notes (most-recent first)."""
    result = await db.execute(
        select(Section).where(Section.slug == section_slug)
    )
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    notes_result = await db.execute(
        select(Note)
        .where(Note.section_id == section.id, Note.visibility == "public")
        .order_by(Note.created_at.desc())
    )
    notes = notes_result.scalars().all()

    section_out = SectionOut(
        id=section.id,
        slug=section.slug,
        title=section.title,
        description=section.description,
        icon=section.icon,
        sort_order=section.sort_order,
        note_count=len(notes),
    )

    notes_out = [
        NoteCardOut(
            id=n.id,
            slug=n.slug,
            section_slug=section.slug,
            title=n.title,
            summary=n.summary,
            tags=json.loads(n.tags or "[]"),
            read_time=n.read_time,
            level=n.level or "beginner",
            created_at=n.created_at,
            updated_at=n.updated_at,
        )
        for n in notes
    ]

    return {"section": section_out, "notes": notes_out}
