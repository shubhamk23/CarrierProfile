"""Integration tests for the admin auth + write flows."""

import pytest

pytestmark = pytest.mark.integration


async def _login(client, username="admin", password="test-password") -> str:
    res = await client.post(
        "/api/knowledge/auth/token",
        json={"username": username, "password": password},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


class TestAdminAuth:
    @pytest.mark.asyncio
    async def test_login_with_valid_creds(self, seeded_app):
        client, _, _ = seeded_app
        token = await _login(client)
        assert isinstance(token, str) and len(token) > 20

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, seeded_app):
        client, _, _ = seeded_app
        res = await client.post(
            "/api/knowledge/auth/token",
            json={"username": "admin", "password": "wrong"},
        )
        assert res.status_code == 401

    @pytest.mark.asyncio
    async def test_login_unknown_user(self, seeded_app):
        client, _, _ = seeded_app
        res = await client.post(
            "/api/knowledge/auth/token",
            json={"username": "nope", "password": "x"},
        )
        assert res.status_code == 401

    @pytest.mark.asyncio
    async def test_protected_endpoint_rejects_anonymous(self, seeded_app):
        client, _, _ = seeded_app
        assert (
            await client.get("/api/knowledge/admin/notes")
        ).status_code == 401

    @pytest.mark.asyncio
    async def test_protected_endpoint_rejects_garbage_token(self, seeded_app):
        client, _, _ = seeded_app
        res = await client.get(
            "/api/knowledge/admin/notes",
            headers={"Authorization": "Bearer not-a-real-token"},
        )
        assert res.status_code == 401


class TestAdminListNotes:
    @pytest.mark.asyncio
    async def test_lists_all_notes(self, seeded_app):
        client, _, _ = seeded_app
        token = await _login(client)
        res = await client.get(
            "/api/knowledge/admin/notes",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        notes = res.json()
        assert len(notes) == 1
        assert notes[0]["slug"] == "attention"
        assert "content" in notes[0]


class TestAdminUpdateNote:
    @pytest.mark.asyncio
    async def test_update_round_trip(self, seeded_app):
        client, _, _ = seeded_app
        token = await _login(client)
        notes = (
            await client.get(
                "/api/knowledge/admin/notes",
                headers={"Authorization": f"Bearer {token}"},
            )
        ).json()
        note_id = notes[0]["id"]

        new_body = "Updated content with very specific words: cosmic ray."
        res = await client.put(
            f"/api/knowledge/admin/notes/{note_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"content": new_body, "tags": ["updated"]},
        )
        assert res.status_code == 200
        updated = res.json()
        assert "cosmic ray" in updated["content"]
        assert updated["tags"] == ["updated"]

        # Public endpoint reflects the change.
        public = await client.get("/api/knowledge/notes/nlp/attention")
        assert "cosmic ray" in public.json()["content"]

    @pytest.mark.asyncio
    async def test_update_unknown_note_404s(self, seeded_app):
        client, _, _ = seeded_app
        token = await _login(client)
        res = await client.put(
            "/api/knowledge/admin/notes/99999",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "X"},
        )
        assert res.status_code == 404


class TestAdminReindex:
    @pytest.mark.asyncio
    async def test_reindex_returns_count(self, seeded_app):
        client, _, _ = seeded_app
        token = await _login(client)
        res = await client.post(
            "/api/knowledge/admin/reindex",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["indexed"] >= 1
        assert body["errors"] == []
