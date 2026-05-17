"""Phase B scaffolding: agentic-learning endpoints (feature-flagged).

Surfaces ``/api/knowledge/agent/*`` in OpenAPI so the platform direction is
visible to portfolio visitors, but every handler returns 501 until the
``KNOWLEDGE_ENABLE_AGENT`` flag is True and an Anthropic / OpenAI key is wired up.
"""

from typing import List

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.config import settings

router = APIRouter()


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(5, ge=1, le=20)


class DraftRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)
    outline: List[str] = Field(default_factory=list)
    section_slug: str


class RelatedRequest(BaseModel):
    note_id: int


class IngestRequest(BaseModel):
    source_url: str = Field(..., min_length=1)
    section_slug: str


def _guard() -> None:
    if not settings.knowledge_enable_agent:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=(
                "Agentic endpoints are not enabled in this environment. "
                "Set KNOWLEDGE_ENABLE_AGENT=true plus a model API key to "
                "enable Phase B."
            ),
        )


@router.post("/ask")
async def agent_ask(req: AskRequest):
    """RAG Q&A over the note corpus (Phase B — not yet implemented)."""
    _guard()
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/draft")
async def agent_draft(req: DraftRequest):
    """Generate a draft note from a topic + outline (Phase B — not implemented)."""
    _guard()
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/related")
async def agent_related(req: RelatedRequest):
    """Return notes similar to a given note (Phase B — not implemented)."""
    _guard()
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/ingest")
async def agent_ingest(req: IngestRequest):
    """Ingest an external source (e.g. arXiv) as a draft note (Phase B — not implemented)."""
    _guard()
    raise HTTPException(status_code=501, detail="Not implemented yet")
