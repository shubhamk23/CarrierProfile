"""Integration tests for the admin CRUD endpoints (notes + sections)."""

import pytest

pytestmark = pytest.mark.integration


async def _login(client) -> str:
    res = await client.post(
        "/api/knowledge/auth/token",
        json={"username": "admin", "password": "test-password"},
    )
    return res.json()["access_token"]


class TestAdminCreateNote:
    @pytest.mark.asyncio
    async def test_creates_note_and_file(self, seeded_app):
        client, _, _ = seeded_app
        token = await _login(client)

        res = await client.post(
            "/api/knowledge/admin/notes",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Diffusion Models",
                "section_slug": "nlp",
                "content": "Diffusion models gradually denoise random noise.",
                "tags": ["diffusion", "generative"],
                "visibility": "public",
                "level": "intermediate",
            },
        )
        assert res.status_code == 201, res.text
        note = res.json()
        assert note["slug"] == "diffusion-models"
        assert note["tags"] == ["diffusion", "generative"]
        assert note["level"] == "intermediate"

    @pytest.mark.asyncio
    async def test_create_in_unknown_section_404s(self, seeded_app):
        client, _, _ = seeded_app
        token = await _login(client)
        res = await client.post(
            "/api/knowledge/admin/notes",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "X",
                "section_slug": "nope",
                "content": "body",
            },
        )
        assert res.status_code == 404

    @pytest.mark.asyncio
    async def test_duplicate_slug_in_section_409s(self, seeded_app):
        client, _, _ = seeded_app
        token = await _login(client)
        # Re-use the seeded "attention" slug.
        res = await client.post(
            "/api/knowledge/admin/notes",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Attention Mechanism",
                "section_slug": "nlp",
                "content": "Duplicate.",
                "slug": "attention",
            },
        )
        assert res.status_code == 409


class TestAdminGetNote:
    @pytest.mark.asyncio
    async def test_get_existing_note(self, seeded_app):
        client, _, _ = seeded_app
        token = await _login(client)
        list_res = await client.get(
            "/api/knowledge/admin/notes",
            headers={"Authorization": f"Bearer {token}"},
        )
        note_id = list_res.json()[0]["id"]

        res = await client.get(
            f"/api/knowledge/admin/notes/{note_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["id"] == note_id
        assert "content" in body

    @pytest.mark.asyncio
    async def test_get_unknown_404s(self, seeded_app):
        client, _, _ = seeded_app
        token = await _login(client)
        res = await client.get(
            "/api/knowledge/admin/notes/99999",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 404


class TestAdminDeleteNote:
    @pytest.mark.asyncio
    async def test_delete_existing_note(self, seeded_app):
        client, _, _ = seeded_app
        token = await _login(client)

        # Create then delete.
        created = (
            await client.post(
                "/api/knowledge/admin/notes",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "title": "Throwaway",
                    "section_slug": "nlp",
                    "content": "delete me",
                },
            )
        ).json()

        res = await client.delete(
            f"/api/knowledge/admin/notes/{created['id']}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        assert res.json()["deleted"] is True

        # Subsequent GET 404s.
        gone = await client.get(
            f"/api/knowledge/admin/notes/{created['id']}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert gone.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_unknown_404s(self, seeded_app):
        client, _, _ = seeded_app
        token = await _login(client)
        res = await client.delete(
            "/api/knowledge/admin/notes/99999",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 404


class TestAdminSections:
    @pytest.mark.asyncio
    async def test_list_sections(self, seeded_app):
        client, _, _ = seeded_app
        token = await _login(client)
        res = await client.get(
            "/api/knowledge/admin/sections",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        body = res.json()
        assert len(body) == 1
        assert body[0]["slug"] == "nlp"
        assert "created_at" in body[0]

    @pytest.mark.asyncio
    async def test_create_section(self, seeded_app):
        client, _, _ = seeded_app
        token = await _login(client)
        res = await client.post(
            "/api/knowledge/admin/sections",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "slug": "agents",
                "title": "Agentic Systems",
                "description": "Tool-using LLM workflows.",
                "icon": "🤖",
                "sort_order": 10,
            },
        )
        assert res.status_code == 201
        body = res.json()
        assert body["slug"] == "agents"
        assert body["icon"] == "🤖"

    @pytest.mark.asyncio
    async def test_create_duplicate_slug_409s(self, seeded_app):
        client, _, _ = seeded_app
        token = await _login(client)
        res = await client.post(
            "/api/knowledge/admin/sections",
            headers={"Authorization": f"Bearer {token}"},
            json={"slug": "nlp", "title": "NLP again"},
        )
        assert res.status_code == 409

    @pytest.mark.asyncio
    async def test_update_section(self, seeded_app):
        client, _, _ = seeded_app
        token = await _login(client)
        list_res = await client.get(
            "/api/knowledge/admin/sections",
            headers={"Authorization": f"Bearer {token}"},
        )
        section_id = list_res.json()[0]["id"]

        res = await client.put(
            f"/api/knowledge/admin/sections/{section_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Natural Language Processing",
                "sort_order": 99,
            },
        )
        assert res.status_code == 200
        body = res.json()
        assert body["title"] == "Natural Language Processing"
        assert body["sort_order"] == 99

    @pytest.mark.asyncio
    async def test_update_unknown_section_404s(self, seeded_app):
        client, _, _ = seeded_app
        token = await _login(client)
        res = await client.put(
            "/api/knowledge/admin/sections/99999",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "X"},
        )
        assert res.status_code == 404
