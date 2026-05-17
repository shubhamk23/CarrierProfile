"""Admin endpoints for the knowledge hub (JWT-protected)."""

import json
from pathlib import Path
from typing import List

import frontmatter
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.connection import get_db
from app.knowledge.auth import get_current_admin
from app.knowledge.indexer import full_reindex
from app.knowledge.markdown_utils import (
    build_frontmatter_string,
    extract_first_paragraph,
    slugify,
)
from app.knowledge.models import Note, Section
from app.knowledge.schemas import (
    NoteAdminOut,
    NoteCreateRequest,
    NoteUpdateRequest,
    SectionAdminOut,
    SectionCreateRequest,
    SectionUpdateRequest,
)

router = APIRouter()


def _content_root() -> Path:
    root = Path(settings.knowledge_content_dir)
    if not root.is_absolute():
        root = Path(__file__).resolve().parents[3] / root
    return root


def _read_body(file_path: str) -> str:
    try:
        raw = Path(file_path).read_text(encoding="utf-8")
        return frontmatter.loads(raw).content
    except Exception:
        return ""


# ── Notes ────────────────────────────────────────────────────────────────────

@router.get("/notes", response_model=List[NoteAdminOut])
async def admin_list_notes(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    """List every note (including drafts) for the admin UI."""
    result = await db.execute(
        select(Note, Section.slug.label("section_slug"))
        .join(Section, Note.section_id == Section.id)
        .order_by(Note.updated_at.desc())
    )

    return [
        NoteAdminOut(
            id=note.id,
            slug=note.slug,
            section_slug=section_slug,
            title=note.title,
            summary=note.summary,
            tags=json.loads(note.tags or "[]"),
            read_time=note.read_time,
            level=note.level or "beginner",
            word_count=note.word_count,
            visibility=note.visibility,
            content=_read_body(note.file_path),
            file_path=note.file_path,
            created_at=note.created_at,
            updated_at=note.updated_at,
        )
        for note, section_slug in result.all()
    ]


@router.get("/notes/{note_id}", response_model=NoteAdminOut)
async def admin_get_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    result = await db.execute(
        select(Note, Section.slug.label("section_slug"))
        .join(Section, Note.section_id == Section.id)
        .where(Note.id == note_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Note not found")

    note, section_slug = row
    return NoteAdminOut(
        id=note.id,
        slug=note.slug,
        section_slug=section_slug,
        title=note.title,
        summary=note.summary,
        tags=json.loads(note.tags or "[]"),
        read_time=note.read_time,
        level=note.level or "beginner",
        word_count=note.word_count,
        visibility=note.visibility,
        content=_read_body(note.file_path),
        file_path=note.file_path,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )


@router.post(
    "/notes",
    response_model=NoteAdminOut,
    status_code=status.HTTP_201_CREATED,
)
async def admin_create_note(
    req: NoteCreateRequest,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    section_result = await db.execute(
        select(Section).where(Section.slug == req.section_slug)
    )
    section = section_result.scalar_one_or_none()
    if not section:
        raise HTTPException(
            status_code=404, detail=f"Section '{req.section_slug}' not found"
        )

    slug = req.slug or slugify(req.title)

    existing = await db.execute(
        select(Note).where(
            Note.slug == slug, Note.section_id == section.id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail=f"Note with slug '{slug}' already exists in this section",
        )

    folder = _content_root() / req.section_slug
    folder.mkdir(parents=True, exist_ok=True)

    summary = extract_first_paragraph(req.content) if req.content else ""
    file_content = build_frontmatter_string(
        title=req.title,
        slug=slug,
        tags=req.tags,
        visibility=req.visibility,
        summary=summary,
        content=req.content,
        level=req.level,
    )

    file_path = folder / f"{slug}.md"
    file_path.write_text(file_content, encoding="utf-8")

    word_count = len(req.content.split())
    tags_json = json.dumps(req.tags)

    note = Note(
        slug=slug,
        section_id=section.id,
        title=req.title,
        summary=summary,
        tags=tags_json,
        visibility=req.visibility,
        level=req.level,
        file_path=str(file_path),
        word_count=word_count,
        read_time=max(1, word_count // 200),
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)

    return NoteAdminOut(
        id=note.id,
        slug=note.slug,
        section_slug=req.section_slug,
        title=note.title,
        summary=note.summary,
        tags=json.loads(note.tags or "[]"),
        read_time=note.read_time,
        level=note.level or "beginner",
        word_count=note.word_count,
        visibility=note.visibility,
        content=req.content,
        file_path=note.file_path,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )


@router.put("/notes/{note_id}", response_model=NoteAdminOut)
async def admin_update_note(
    note_id: int,
    req: NoteUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    result = await db.execute(
        select(Note, Section.slug.label("section_slug"))
        .join(Section, Note.section_id == Section.id)
        .where(Note.id == note_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Note not found")

    note, current_section_slug = row
    current_content = _read_body(note.file_path)

    new_title = req.title if req.title is not None else note.title
    new_content = req.content if req.content is not None else current_content
    new_tags = (
        req.tags if req.tags is not None else json.loads(note.tags or "[]")
    )
    new_visibility = (
        req.visibility if req.visibility is not None else note.visibility
    )
    new_level = (
        req.level if req.level is not None else (note.level or "beginner")
    )
    new_slug = req.slug if req.slug is not None else note.slug
    new_section_slug = (
        req.section_slug
        if req.section_slug is not None
        else current_section_slug
    )

    if new_section_slug != current_section_slug:
        sec_result = await db.execute(
            select(Section).where(Section.slug == new_section_slug)
        )
        new_section = sec_result.scalar_one_or_none()
        if not new_section:
            raise HTTPException(
                status_code=404,
                detail=f"Section '{new_section_slug}' not found",
            )
        note.section_id = new_section.id

    new_summary = extract_first_paragraph(new_content)
    new_folder = _content_root() / new_section_slug
    new_folder.mkdir(parents=True, exist_ok=True)
    new_file_path = new_folder / f"{new_slug}.md"

    file_content = build_frontmatter_string(
        title=new_title,
        slug=new_slug,
        tags=new_tags,
        visibility=new_visibility,
        summary=new_summary,
        content=new_content,
        level=new_level,
    )
    new_file_path.write_text(file_content, encoding="utf-8")

    old_file = Path(note.file_path)
    if old_file != new_file_path and old_file.exists():
        old_file.unlink()

    word_count = len(new_content.split())
    note.slug = new_slug
    note.title = new_title
    note.summary = new_summary
    note.tags = json.dumps(new_tags)
    note.visibility = new_visibility
    note.level = new_level
    note.file_path = str(new_file_path)
    note.word_count = word_count
    note.read_time = max(1, word_count // 200)

    await db.commit()
    await db.refresh(note)

    return NoteAdminOut(
        id=note.id,
        slug=note.slug,
        section_slug=new_section_slug,
        title=note.title,
        summary=note.summary,
        tags=json.loads(note.tags or "[]"),
        read_time=note.read_time,
        level=note.level or "beginner",
        word_count=note.word_count,
        visibility=note.visibility,
        content=new_content,
        file_path=note.file_path,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )


@router.delete("/notes/{note_id}")
async def admin_delete_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    try:
        file_path = Path(note.file_path)
        if file_path.exists():
            file_path.unlink()
    except Exception:
        pass

    await db.delete(note)
    await db.commit()
    return {"deleted": True}


@router.post("/reindex")
async def admin_reindex(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    """Force a full filesystem → DB reindex."""
    result = await full_reindex(db)
    return {"indexed": result.indexed, "errors": result.errors}


# ── Sections ─────────────────────────────────────────────────────────────────

@router.get("/sections", response_model=List[SectionAdminOut])
async def admin_list_sections(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    result = await db.execute(
        select(Section).order_by(Section.sort_order, Section.title)
    )
    sections = result.scalars().all()

    out: List[SectionAdminOut] = []
    for section in sections:
        count_result = await db.execute(
            select(func.count(Note.id)).where(Note.section_id == section.id)
        )
        out.append(
            SectionAdminOut(
                id=section.id,
                slug=section.slug,
                title=section.title,
                description=section.description,
                icon=section.icon,
                sort_order=section.sort_order,
                note_count=int(count_result.scalar_one()),
                created_at=section.created_at,
                updated_at=section.updated_at,
            )
        )
    return out


@router.post(
    "/sections",
    response_model=SectionAdminOut,
    status_code=status.HTTP_201_CREATED,
)
async def admin_create_section(
    req: SectionCreateRequest,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    existing = await db.execute(
        select(Section).where(Section.slug == req.slug)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409, detail=f"Section '{req.slug}' already exists"
        )

    folder = _content_root() / req.slug
    folder.mkdir(parents=True, exist_ok=True)

    section_json = {
        "title": req.title,
        "description": req.description,
        "icon": req.icon,
        "sort_order": req.sort_order,
    }
    (folder / "_section.json").write_text(
        json.dumps(section_json, indent=2), encoding="utf-8"
    )

    section = Section(
        slug=req.slug,
        title=req.title,
        description=req.description,
        icon=req.icon,
        sort_order=req.sort_order,
    )
    db.add(section)
    await db.commit()
    await db.refresh(section)

    return SectionAdminOut(
        id=section.id,
        slug=section.slug,
        title=section.title,
        description=section.description,
        icon=section.icon,
        sort_order=section.sort_order,
        note_count=0,
        created_at=section.created_at,
        updated_at=section.updated_at,
    )


@router.put("/sections/{section_id}", response_model=SectionAdminOut)
async def admin_update_section(
    section_id: int,
    req: SectionUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    result = await db.execute(
        select(Section).where(Section.id == section_id)
    )
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    if req.title is not None:
        section.title = req.title
    if req.description is not None:
        section.description = req.description
    if req.icon is not None:
        section.icon = req.icon
    if req.sort_order is not None:
        section.sort_order = req.sort_order

    folder = _content_root() / section.slug
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "_section.json").write_text(
        json.dumps(
            {
                "title": section.title,
                "description": section.description,
                "icon": section.icon,
                "sort_order": section.sort_order,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    await db.commit()
    await db.refresh(section)

    count_result = await db.execute(
        select(func.count(Note.id)).where(Note.section_id == section.id)
    )
    return SectionAdminOut(
        id=section.id,
        slug=section.slug,
        title=section.title,
        description=section.description,
        icon=section.icon,
        sort_order=section.sort_order,
        note_count=int(count_result.scalar_one()),
        created_at=section.created_at,
        updated_at=section.updated_at,
    )
