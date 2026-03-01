"""Tests for the /api/contact router (app/routers/contact.py).

The contact router has three distinct concerns tested here:
1. Input validation (Pydantic / FastAPI 422 responses)
2. DB-primary storage path (happy path)
3. JSON-file fallback when the DB raises an exception
4. Email failures must not cause the request to fail
5. Admin GET /api/contact/messages endpoint
"""
import io
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open

from fastapi.testclient import TestClient

VALID_PAYLOAD = {
    "name": "Alice",
    "email": "alice@example.com",
    "subject": "Hello there",
    "message": "This is a test message.",
}


def _make_async_db(*, raise_on_commit: bool = False):
    """Return a mock AsyncSession."""
    session = AsyncMock()
    session.add = MagicMock()
    if raise_on_commit:
        session.commit = AsyncMock(side_effect=Exception("DB unavailable"))
    else:
        session.commit = AsyncMock(return_value=None)
    return session


class TestSubmitContactFormValidation:
    def test_missing_name_returns_422(self, client):
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "name"}
        response = client.post("/api/contact", json=payload)
        assert response.status_code == 422

    def test_missing_email_returns_422(self, client):
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "email"}
        response = client.post("/api/contact", json=payload)
        assert response.status_code == 422

    def test_invalid_email_format_returns_422(self, client):
        payload = {**VALID_PAYLOAD, "email": "not-an-email"}
        response = client.post("/api/contact", json=payload)
        assert response.status_code == 422

    def test_missing_subject_returns_422(self, client):
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "subject"}
        response = client.post("/api/contact", json=payload)
        assert response.status_code == 422

    def test_missing_message_returns_422(self, client):
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "message"}
        response = client.post("/api/contact", json=payload)
        assert response.status_code == 422


class TestSubmitContactFormDBPath:
    def test_success_with_database_returns_200(self):
        from app.main import app

        db_session = _make_async_db(raise_on_commit=False)

        async def override_get_db():
            yield db_session

        import io as _io
        from app.database.connection import get_db
        from app.routers import profile as _profile_router

        profile_json = json.dumps(_profile_data())

        app.dependency_overrides[get_db] = override_get_db

        with patch("builtins.open", return_value=_io.StringIO(profile_json)):
            with patch("app.routers.contact.send_email_notification", new=AsyncMock()):
                with TestClient(app, raise_server_exceptions=True) as c:
                    response = c.post("/api/contact", json=VALID_PAYLOAD)

        app.dependency_overrides.clear()

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True

    def test_response_message_is_non_empty(self):
        from app.main import app
        from app.database.connection import get_db
        import io as _io

        db_session = _make_async_db()

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db

        profile_json = json.dumps(_profile_data())
        with patch("builtins.open", return_value=_io.StringIO(profile_json)):
            with patch("app.routers.contact.send_email_notification", new=AsyncMock()):
                with TestClient(app, raise_server_exceptions=True) as c:
                    body = c.post("/api/contact", json=VALID_PAYLOAD).json()

        app.dependency_overrides.clear()
        assert len(body.get("message", "")) > 0


class TestSubmitContactFormFallback:
    def test_falls_back_to_file_when_db_fails(self):
        """When the DB commit raises, the router should silently fall back to file storage."""
        from app.main import app
        from app.database.connection import get_db
        import io as _io

        db_session = _make_async_db(raise_on_commit=True)

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db

        profile_json = json.dumps(_profile_data())
        # Mock the file-write path so we don't touch the real filesystem
        with patch("builtins.open", side_effect=_open_side_effect(profile_json)):
            with patch("app.routers.contact.send_email_notification", new=AsyncMock()):
                with patch("app.routers.contact.MESSAGES_PATH") as mock_path:
                    mock_path.exists.return_value = False
                    mock_path.parent.mkdir = MagicMock()
                    with patch("builtins.open", mock_open(read_data="[]")):
                        with TestClient(app, raise_server_exceptions=True) as c:
                            response = c.post("/api/contact", json=VALID_PAYLOAD)

        app.dependency_overrides.clear()
        assert response.status_code == 200


class TestEmailFailureNonBlocking:
    def test_email_error_does_not_cause_500(self):
        from app.main import app
        from app.database.connection import get_db
        import io as _io

        db_session = _make_async_db()

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db

        profile_json = json.dumps(_profile_data())

        async def failing_email(_):
            raise Exception("SMTP timeout")

        with patch("builtins.open", return_value=_io.StringIO(profile_json)):
            with patch("app.routers.contact.send_email_notification", new=failing_email):
                with TestClient(app, raise_server_exceptions=True) as c:
                    response = c.post("/api/contact", json=VALID_PAYLOAD)

        app.dependency_overrides.clear()
        assert response.status_code == 200


class TestGetMessages:
    def test_returns_200_with_db(self):
        from app.main import app
        from app.database.connection import get_db
        import io as _io
        from sqlalchemy import select

        db_session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        db_session.execute = AsyncMock(return_value=result_mock)

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db

        profile_json = json.dumps(_profile_data())
        with patch("builtins.open", return_value=_io.StringIO(profile_json)):
            with TestClient(app, raise_server_exceptions=True) as c:
                response = c.get("/api/contact/messages")

        app.dependency_overrides.clear()
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_returns_empty_list_when_no_messages(self):
        from app.main import app
        from app.database.connection import get_db
        import io as _io

        db_session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        db_session.execute = AsyncMock(return_value=result_mock)

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db

        profile_json = json.dumps(_profile_data())
        with patch("builtins.open", return_value=_io.StringIO(profile_json)):
            with TestClient(app, raise_server_exceptions=True) as c:
                body = c.get("/api/contact/messages").json()

        app.dependency_overrides.clear()
        assert body == []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _profile_data():
    """Minimal profile dict to satisfy the profile router's open() call."""
    return {
        "name": "Test",
        "title": "Engineer",
        "subtitle": "Sub",
        "location": "Pune",
        "phone": "000",
        "email": "t@t.com",
        "linkedin": "https://linkedin.com/in/t",
        "github": "https://github.com/t",
        "summary": "Summary",
        "skills": {
            "languages": ["Python"],
            "ml_dl_frameworks": ["PyTorch"],
            "computer_vision": ["OpenCV"],
            "generative_ai_nlp": ["LangChain"],
            "mlops_devops": ["Docker"],
            "cloud_data": ["Azure"],
            "software_engineering": ["FastAPI"],
        },
        "experience": [],
        "projects": [],
        "education": {
            "degree": "B.E.",
            "institution": "Uni",
            "location": "City",
            "period": "2015-2019",
        },
        "certifications": [],
        "awards": [],
    }


def _open_side_effect(profile_json: str):
    """Return a side_effect callable that yields a StringIO for the profile
    JSON and a mock for any other path (e.g. messages.json writes)."""
    import io as _io

    call_count = {"n": 0}

    def _side_effect(*args, **kwargs):
        if call_count["n"] == 0:
            call_count["n"] += 1
            return _io.StringIO(profile_json)
        # subsequent open() calls (messages.json) get a writable mock
        m = MagicMock()
        m.__enter__ = lambda s: s
        m.__exit__ = MagicMock(return_value=False)
        m.read = MagicMock(return_value="[]")
        return m

    return _side_effect
