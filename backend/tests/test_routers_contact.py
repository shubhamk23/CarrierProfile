"""Tests for the /api/contact router (app/routers/contact.py).

Delivery has two independent channels (DB insert, email notification).
The request succeeds if either lands, and only 500s if both fail or
neither is configured.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

VALID_PAYLOAD = {
    "name": "Alice",
    "email": "alice@example.com",
    "subject": "Hello there",
    "message": "This is a test message.",
}


def _make_async_db(*, raise_on_commit: bool = False):
    session = AsyncMock()
    session.add = MagicMock()
    session.rollback = AsyncMock()
    if raise_on_commit:
        session.commit = AsyncMock(side_effect=Exception("DB unavailable"))
    else:
        session.commit = AsyncMock(return_value=None)
    return session


@pytest.fixture
def app_with_db_override():
    """Yield (app, db_session) with get_db overridden; cleans up after."""

    def _make(db_session):
        from app.main import app
        from app.database.connection import get_db

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db
        return app

    yield _make

    from app.main import app

    app.dependency_overrides.clear()


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
    def test_db_success_returns_200(self, app_with_db_override):
        app = app_with_db_override(_make_async_db())
        with TestClient(app, raise_server_exceptions=True) as c:
            response = c.post("/api/contact", json=VALID_PAYLOAD)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert len(body["message"]) > 0

    def test_db_failure_with_no_email_configured_returns_500(
        self, app_with_db_override
    ):
        """DB is the only channel; if it fails and email isn't configured, the
        message would silently vanish, so this must surface as a failure."""
        app = app_with_db_override(_make_async_db(raise_on_commit=True))
        with TestClient(app, raise_server_exceptions=True) as c:
            response = c.post("/api/contact", json=VALID_PAYLOAD)

        assert response.status_code == 500

    def test_db_failure_rolls_back_session(self, app_with_db_override):
        db_session = _make_async_db(raise_on_commit=True)
        app = app_with_db_override(db_session)
        with TestClient(app, raise_server_exceptions=True) as c:
            c.post("/api/contact", json=VALID_PAYLOAD)

        db_session.rollback.assert_awaited_once()

    def test_db_unconfigured_with_no_email_configured_returns_500(
        self, app_with_db_override
    ):
        app = app_with_db_override(None)
        with TestClient(app, raise_server_exceptions=True) as c:
            response = c.post("/api/contact", json=VALID_PAYLOAD)

        assert response.status_code == 500


class TestSubmitContactFormEmailPath:
    def test_email_success_covers_db_failure(self, app_with_db_override, monkeypatch):
        from app.config import settings

        monkeypatch.setattr(settings, "resend_api_key", "test-key")
        monkeypatch.setattr(settings, "resend_to_email", "owner@example.com")

        app = app_with_db_override(_make_async_db(raise_on_commit=True))
        with patch("app.routers.contact.send_email_notification", new=AsyncMock()):
            with TestClient(app, raise_server_exceptions=True) as c:
                response = c.post("/api/contact", json=VALID_PAYLOAD)

        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_email_success_covers_db_unconfigured(
        self, app_with_db_override, monkeypatch
    ):
        from app.config import settings

        monkeypatch.setattr(settings, "resend_api_key", "test-key")
        monkeypatch.setattr(settings, "resend_to_email", "owner@example.com")

        app = app_with_db_override(None)
        with patch("app.routers.contact.send_email_notification", new=AsyncMock()):
            with TestClient(app, raise_server_exceptions=True) as c:
                response = c.post("/api/contact", json=VALID_PAYLOAD)

        assert response.status_code == 200

    def test_email_failure_does_not_mask_successful_db_write(
        self, app_with_db_override, monkeypatch
    ):
        from app.config import settings

        monkeypatch.setattr(settings, "resend_api_key", "test-key")
        monkeypatch.setattr(settings, "resend_to_email", "owner@example.com")

        app = app_with_db_override(_make_async_db())

        async def failing_email(_):
            raise Exception("SMTP timeout")

        with patch("app.routers.contact.send_email_notification", new=failing_email):
            with TestClient(app, raise_server_exceptions=True) as c:
                response = c.post("/api/contact", json=VALID_PAYLOAD)

        assert response.status_code == 200

    def test_both_channels_failing_returns_500(self, app_with_db_override, monkeypatch):
        from app.config import settings

        monkeypatch.setattr(settings, "resend_api_key", "test-key")
        monkeypatch.setattr(settings, "resend_to_email", "owner@example.com")

        app = app_with_db_override(_make_async_db(raise_on_commit=True))

        async def failing_email(_):
            raise Exception("SMTP timeout")

        with patch("app.routers.contact.send_email_notification", new=failing_email):
            with TestClient(app, raise_server_exceptions=True) as c:
                response = c.post("/api/contact", json=VALID_PAYLOAD)

        assert response.status_code == 500

    def test_email_html_escapes_message_content(self, monkeypatch):
        """A visitor-supplied <script> tag must not reach the notification
        email unescaped."""
        import asyncio
        from app.models import ContactMessage
        from app.routers.contact import send_email_notification
        from app.config import settings

        monkeypatch.setattr(settings, "resend_api_key", "test-key")
        monkeypatch.setattr(settings, "resend_to_email", "owner@example.com")

        malicious = ContactMessage(
            name="<script>alert(1)</script>",
            email="attacker@example.com",
            subject="hi",
            message="line1\nline2",
        )

        captured = {}

        def fake_send(params):
            captured.update(params)
            return {"id": "test"}

        with patch("resend.Emails.send", side_effect=fake_send):
            asyncio.run(send_email_notification(malicious))

        assert "<script>alert(1)</script>" not in captured["html"]
        assert "&lt;script&gt;" in captured["html"]

    def test_email_strips_crlf_from_subject_header(self, monkeypatch):
        """The subject reaches an email header, so CR/LF must not survive --
        otherwise it is a header-injection primitive."""
        import asyncio
        from app.models import ContactMessage
        from app.routers.contact import send_email_notification
        from app.config import settings

        monkeypatch.setattr(settings, "resend_api_key", "test-key")
        monkeypatch.setattr(settings, "resend_to_email", "owner@example.com")

        injected = ContactMessage(
            name="Attacker",
            email="attacker@example.com",
            subject="Hello\r\nBcc: victim@example.com",
            message="body text here",
        )

        captured = {}

        def fake_send(params):
            captured.update(params)
            return {"id": "test"}

        with patch("resend.Emails.send", side_effect=fake_send):
            asyncio.run(send_email_notification(injected))

        assert "\r" not in captured["subject"]
        assert "\n" not in captured["subject"]
        assert captured["subject"] == "Portfolio Contact: Hello Bcc: victim@example.com"

    def test_email_address_is_html_escaped(self, monkeypatch):
        """Every visitor-supplied field in the notification HTML is escaped,
        including the email address."""
        import asyncio
        from app.routers.contact import send_email_notification
        from app.config import settings

        monkeypatch.setattr(settings, "resend_api_key", "test-key")
        monkeypatch.setattr(settings, "resend_to_email", "owner@example.com")

        class _RawEmail:
            """Bypass EmailStr so the escaping itself is what's under test."""

            name = "Attacker"
            email = '"<img src=x onerror=alert(1)>"@example.com'
            subject = "hi"
            message = "body"

        captured = {}

        def fake_send(params):
            captured.update(params)
            return {"id": "test"}

        with patch("resend.Emails.send", side_effect=fake_send):
            asyncio.run(send_email_notification(_RawEmail()))

        assert "<img src=x" not in captured["html"]
        assert "&lt;img" in captured["html"]


class TestRateLimit:
    def test_sixth_submission_within_window_returns_429(self, app_with_db_override):
        app = app_with_db_override(_make_async_db())
        with TestClient(app, raise_server_exceptions=True) as c:
            for _ in range(5):
                response = c.post("/api/contact", json=VALID_PAYLOAD)
                assert response.status_code == 200
            response = c.post("/api/contact", json=VALID_PAYLOAD)

        assert response.status_code == 429


class TestAdminEndpointRemoved:
    def test_get_messages_endpoint_no_longer_exists(self, client):
        """The unauthenticated admin endpoint was deleted; it must not be
        routable under any method."""
        response = client.get("/api/contact/messages")
        assert response.status_code == 404
