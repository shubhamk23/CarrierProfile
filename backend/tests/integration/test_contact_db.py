"""POST /api/contact against a real PostgreSQL with the real migrations."""

from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import func, select, text

from app.database.models import ContactMessage

pytestmark = pytest.mark.integration

PAYLOAD = {
    "name": "Alice",
    "email": "alice@example.com",
    "subject": "Hello there",
    "message": "This is an integration test message.",
}


async def _all_rows(factory):
    async with factory() as session:
        return (await session.execute(select(ContactMessage))).scalars().all()


async def test_submission_writes_exactly_one_row(
    integration_client, db_session_factory
):
    response = integration_client.post(
        "/api/contact", json=PAYLOAD, headers={"User-Agent": "pytest-integration"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

    rows = await _all_rows(db_session_factory)
    assert len(rows) == 1
    row = rows[0]
    assert (row.name, row.email, row.subject) == (
        PAYLOAD["name"],
        PAYLOAD["email"],
        PAYLOAD["subject"],
    )
    assert row.message == PAYLOAD["message"]
    assert row.user_agent == "pytest-integration"
    assert row.created_at is not None  # server default applied by the real schema


async def test_oversized_name_is_rejected_and_nothing_is_written(
    integration_client, db_session_factory
):
    response = integration_client.post(
        "/api/contact", json={**PAYLOAD, "name": "x" * 300}
    )
    assert response.status_code == 422
    assert await _all_rows(db_session_factory) == []


async def test_name_at_column_limit_is_accepted(integration_client, db_session_factory):
    """255 chars is the column width; the boundary must round-trip, not fail on INSERT."""
    response = integration_client.post(
        "/api/contact", json={**PAYLOAD, "name": "x" * 255}
    )
    assert response.status_code == 200
    assert len(await _all_rows(db_session_factory)) == 1


async def test_unicode_and_markup_are_stored_verbatim(
    integration_client, db_session_factory
):
    body = "नमस्ते 👋 <script>alert(1)</script> 'quotes' \"double\""
    response = integration_client.post(
        "/api/contact", json={**PAYLOAD, "message": body}
    )
    assert response.status_code == 200
    (row,) = await _all_rows(db_session_factory)
    assert row.message == body  # escaping happens in the email, never in storage


async def test_database_failure_falls_back_to_email(
    integration_client, db_session_factory
):
    """With the table gone the insert fails; a working email still saves the day."""
    async with db_session_factory() as session:
        await session.execute(text("DROP TABLE contact_messages"))
        await session.commit()

    sender = AsyncMock()
    with patch("app.routers.contact.settings") as s, patch(
        "app.routers.contact.send_email_notification", sender
    ):
        s.resend_api_key = "key"
        s.resend_to_email = "me@example.com"
        s.rate_limit_times, s.rate_limit_seconds = 5, 3600
        response = integration_client.post("/api/contact", json=PAYLOAD)

    assert response.status_code == 200
    sender.assert_awaited_once()


async def test_database_failure_without_email_returns_500(
    integration_client, db_session_factory
):
    async with db_session_factory() as session:
        await session.execute(text("DROP TABLE contact_messages"))
        await session.commit()

    response = integration_client.post("/api/contact", json=PAYLOAD)
    assert response.status_code == 500


async def test_rate_limit_counts_per_client_and_returns_json_429(
    integration_client, db_session_factory
):
    headers = {"x-real-ip": "203.0.113.7"}
    for _ in range(5):
        assert (
            integration_client.post("/api/contact", json=PAYLOAD, headers=headers)
        ).status_code == 200

    blocked = integration_client.post("/api/contact", json=PAYLOAD, headers=headers)
    assert blocked.status_code == 429
    assert blocked.headers["content-type"].startswith("application/json")

    other = integration_client.post(
        "/api/contact", json=PAYLOAD, headers={"x-real-ip": "203.0.113.8"}
    )
    assert other.status_code == 200

    async with db_session_factory() as session:
        count = (
            await session.execute(select(func.count()).select_from(ContactMessage))
        ).scalar_one()
    assert (
        count == 6
    )  # 5 from the first client + 1 from the second; the 429 wrote nothing
