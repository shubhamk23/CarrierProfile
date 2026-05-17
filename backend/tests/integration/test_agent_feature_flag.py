"""Integration tests for the Phase B agent surface (feature-flagged off)."""

import pytest

pytestmark = pytest.mark.integration


class TestAgentDisabledByDefault:
    @pytest.mark.asyncio
    async def test_ask_returns_501(self, app_with_db):
        client, _, _ = app_with_db
        res = await client.post(
            "/api/knowledge/agent/ask",
            json={"question": "What is attention?"},
        )
        assert res.status_code == 501
        assert "not enabled" in res.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_draft_returns_501(self, app_with_db):
        client, _, _ = app_with_db
        res = await client.post(
            "/api/knowledge/agent/draft",
            json={
                "topic": "Diffusion models",
                "outline": ["intro", "math", "examples"],
                "section_slug": "ai-models",
            },
        )
        assert res.status_code == 501

    @pytest.mark.asyncio
    async def test_related_returns_501(self, app_with_db):
        client, _, _ = app_with_db
        res = await client.post(
            "/api/knowledge/agent/related",
            json={"note_id": 1},
        )
        assert res.status_code == 501

    @pytest.mark.asyncio
    async def test_ingest_returns_501(self, app_with_db):
        client, _, _ = app_with_db
        res = await client.post(
            "/api/knowledge/agent/ingest",
            json={
                "source_url": "https://arxiv.org/abs/1706.03762",
                "section_slug": "nlp",
            },
        )
        assert res.status_code == 501


class TestAgentEnabledStub:
    """When the flag is on the endpoints should STILL 501 (not implemented)
    rather than crash with a misconfiguration error — proving the guard is
    distinct from the implementation."""

    @pytest.mark.asyncio
    async def test_ask_returns_501_even_when_enabled(
        self, app_with_db, monkeypatch
    ):
        from app.config import settings as s

        monkeypatch.setattr(s, "knowledge_enable_agent", True)
        client, _, _ = app_with_db
        res = await client.post(
            "/api/knowledge/agent/ask",
            json={"question": "What is attention?"},
        )
        assert res.status_code == 501
