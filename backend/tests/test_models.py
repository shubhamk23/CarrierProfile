"""Unit tests for Pydantic models defined in app/models.py."""

import pytest
from pydantic import ValidationError

from app.models import ContactMessage, ContactResponse

# ---------------------------------------------------------------------------
# ContactMessage
# ---------------------------------------------------------------------------


class TestContactMessage:
    def test_valid_contact_message(self):
        msg = ContactMessage(
            name="Alice",
            email="alice@example.com",
            subject="Hello",
            message="Hi there!",
        )
        assert msg.name == "Alice"
        assert str(msg.email) == "alice@example.com"

    def test_invalid_email_raises_validation_error(self):
        with pytest.raises(ValidationError) as exc_info:
            ContactMessage(
                name="Alice",
                email="not-an-email",
                subject="Hello",
                message="Hi!",
            )
        assert "email" in str(exc_info.value).lower()

    def test_missing_name_raises_validation_error(self):
        with pytest.raises(ValidationError):
            ContactMessage(
                email="alice@example.com",
                subject="Hello",
                message="Hi!",
            )

    def test_missing_subject_raises_validation_error(self):
        with pytest.raises(ValidationError):
            ContactMessage(
                name="Alice",
                email="alice@example.com",
                message="Hi!",
            )

    def test_missing_message_raises_validation_error(self):
        with pytest.raises(ValidationError):
            ContactMessage(
                name="Alice",
                email="alice@example.com",
                subject="Hello",
            )

    def test_oversized_name_raises_validation_error(self):
        """Lengths are capped at the DB column widths, so oversized input is
        rejected with a 422 instead of failing later on INSERT."""
        with pytest.raises(ValidationError):
            ContactMessage(
                name="A" * 256,
                email="alice@example.com",
                subject="Hello",
                message="Hi there!",
            )

    def test_oversized_subject_raises_validation_error(self):
        with pytest.raises(ValidationError):
            ContactMessage(
                name="Alice",
                email="alice@example.com",
                subject="S" * 501,
                message="Hi there!",
            )

    def test_oversized_message_raises_validation_error(self):
        with pytest.raises(ValidationError):
            ContactMessage(
                name="Alice",
                email="alice@example.com",
                subject="Hello",
                message="M" * 5001,
            )

    def test_empty_name_raises_validation_error(self):
        with pytest.raises(ValidationError):
            ContactMessage(
                name="",
                email="alice@example.com",
                subject="Hello",
                message="Hi there!",
            )

    def test_max_length_values_are_accepted(self):
        """The cap itself must be inclusive -- a message exactly at the limit
        is valid."""
        msg = ContactMessage(
            name="A" * 255,
            email="alice@example.com",
            subject="S" * 500,
            message="M" * 5000,
        )
        assert len(msg.name) == 255
        assert len(msg.subject) == 500
        assert len(msg.message) == 5000


# ---------------------------------------------------------------------------
# ContactResponse
# ---------------------------------------------------------------------------


class TestContactResponse:
    def test_valid_contact_response(self):
        resp = ContactResponse(success=True, message="Sent!")
        assert resp.success is True
        assert resp.message == "Sent!"

    def test_success_false(self):
        resp = ContactResponse(success=False, message="Failed")
        assert resp.success is False
