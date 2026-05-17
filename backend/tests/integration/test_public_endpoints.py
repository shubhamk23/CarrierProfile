"""Integration tests for the public knowledge endpoints."""

import pytest

pytestmark = pytest.mark.integration


class TestSectionsEndpoint:
    @pytest.mark.asyncio
    async def test_lists_sections_with_note_counts(self, seeded_app):
        client, _, _ = seeded_app
        res = await client.get("/api/knowledge/sections")
        assert res.status_code == 200
        body = res.json()
        assert len(body) == 1
        assert body[0]["slug"] == "nlp"
        assert body[0]["note_count"] == 1

    @pytest.mark.asyncio
    async def test_section_detail_returns_notes(self, seeded_app):
        client, _, _ = seeded_app
        res = await client.get("/api/knowledge/sections/nlp")
        assert res.status_code == 200
        body = res.json()
        assert body["section"]["title"] == "NLP"
        assert len(body["notes"]) == 1
        assert body["notes"][0]["slug"] == "attention"

    @pytest.mark.asyncio
    async def test_unknown_section_404s(self, seeded_app):
        client, _, _ = seeded_app
        res = await client.get("/api/knowledge/sections/nonesuch")
        assert res.status_code == 404


class TestNoteDetailEndpoint:
    @pytest.mark.asyncio
    async def test_returns_raw_markdown(self, seeded_app):
        client, _, _ = seeded_app
        res = await client.get("/api/knowledge/notes/nlp/attention")
        assert res.status_code == 200
        body = res.json()
        assert body["title"] == "Attention Mechanism"
        # Body content survives the frontmatter strip.
        assert "weighted sums" in body["content"]
        assert body["tags"] == ["transformer", "attention"]

    @pytest.mark.asyncio
    async def test_unknown_note_404s(self, seeded_app):
        client, _, _ = seeded_app
        assert (
            await client.get(
                "/api/knowledge/notes/nlp/does-not-exist"
            )
        ).status_code == 404

    @pytest.mark.asyncio
    async def test_unknown_section_404s(self, seeded_app):
        client, _, _ = seeded_app
        assert (
            await client.get(
                "/api/knowledge/notes/nope/attention"
            )
        ).status_code == 404


class TestKnowledgeHealth:
    @pytest.mark.asyncio
    async def test_reports_counts(self, seeded_app):
        client, _, _ = seeded_app
        res = await client.get("/api/knowledge/health")
        assert res.status_code == 200
        body = res.json()
        assert body["status"] == "ok"
        assert body["note_count"] == 1
        assert body["section_count"] == 1


class TestPortfolioRoutesUnchanged:
    """Regression guard: the migration must not break existing portfolio surfaces."""

    @pytest.mark.asyncio
    async def test_root_endpoint(self, app_with_db):
        client, _, _ = app_with_db
        res = await client.get("/")
        assert res.status_code == 200
        assert "Portfolio API" in res.json()["message"]

    @pytest.mark.asyncio
    async def test_health_endpoint(self, app_with_db):
        client, _, _ = app_with_db
        assert (await client.get("/api/health")).status_code == 200

    @pytest.mark.asyncio
    async def test_blog_list_endpoint(self, app_with_db):
        client, _, _ = app_with_db
        res = await client.get("/api/blog")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    @pytest.mark.asyncio
    async def test_profile_endpoint(self, app_with_db):
        client, _, _ = app_with_db
        res = await client.get("/api/profile")
        assert res.status_code == 200


class TestCorsHeaders:
    @pytest.mark.asyncio
    async def test_preflight_allows_known_origin(self, app_with_db):
        client, _, _ = app_with_db
        res = await client.options(
            "/api/knowledge/sections",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert res.status_code == 200
        assert (
            res.headers.get("access-control-allow-origin")
            == "http://localhost:3000"
        )
