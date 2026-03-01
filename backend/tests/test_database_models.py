"""Tests for the SQLAlchemy ORM model (app/database/models.py).

These tests verify the model's helper methods without requiring a live
database connection.
"""
import pytest
from datetime import datetime, timezone


class TestContactMessageModel:
    def _make_message(self, **overrides):
        """Construct a ContactMessage ORM instance with sensible defaults."""
        from app.database.models import ContactMessage

        now = datetime(2024, 6, 15, 10, 30, 0, tzinfo=timezone.utc)

        msg = ContactMessage(
            id=1,
            name="Alice",
            email="alice@example.com",
            subject="Hello",
            message="Hi there!",
            read=False,
            ip_address="1.2.3.4",
            user_agent="pytest/1.0",
        )
        # Manually set server-default fields (they'd normally be set by the DB)
        msg.timestamp = overrides.get("timestamp", now)
        msg.created_at = overrides.get("created_at", now)
        msg.updated_at = overrides.get("updated_at", now)

        for key, value in overrides.items():
            if key not in ("timestamp", "created_at", "updated_at"):
                setattr(msg, key, value)

        return msg

    # ------------------------------------------------------------------
    # to_dict()
    # ------------------------------------------------------------------

    def test_to_dict_returns_dict(self):
        msg = self._make_message()
        result = msg.to_dict()
        assert isinstance(result, dict)

    def test_to_dict_contains_id(self):
        msg = self._make_message()
        assert "id" in msg.to_dict()

    def test_to_dict_contains_name(self):
        msg = self._make_message()
        assert msg.to_dict()["name"] == "Alice"

    def test_to_dict_contains_email(self):
        msg = self._make_message()
        assert msg.to_dict()["email"] == "alice@example.com"

    def test_to_dict_contains_subject(self):
        msg = self._make_message()
        assert msg.to_dict()["subject"] == "Hello"

    def test_to_dict_contains_message(self):
        msg = self._make_message()
        assert msg.to_dict()["message"] == "Hi there!"

    def test_to_dict_timestamp_is_iso_string(self):
        """Datetime fields must be serialised to ISO-format strings."""
        msg = self._make_message()
        result = msg.to_dict()
        assert isinstance(result["timestamp"], str)
        # Should be parseable back to datetime
        dt = datetime.fromisoformat(result["timestamp"])
        assert isinstance(dt, datetime)

    def test_to_dict_created_at_is_iso_string(self):
        msg = self._make_message()
        result = msg.to_dict()
        assert isinstance(result["created_at"], str)

    def test_to_dict_updated_at_is_iso_string(self):
        msg = self._make_message()
        result = msg.to_dict()
        assert isinstance(result["updated_at"], str)

    def test_to_dict_timestamp_none_when_not_set(self):
        """If timestamp is None (e.g., not yet persisted), to_dict should return None."""
        msg = self._make_message(timestamp=None, created_at=None, updated_at=None)
        result = msg.to_dict()
        assert result["timestamp"] is None
        assert result["created_at"] is None
        assert result["updated_at"] is None

    def test_to_dict_contains_read_flag(self):
        msg = self._make_message()
        assert "read" in msg.to_dict()
        assert msg.to_dict()["read"] is False

    def test_to_dict_contains_ip_address(self):
        msg = self._make_message()
        assert msg.to_dict()["ip_address"] == "1.2.3.4"

    def test_to_dict_contains_user_agent(self):
        msg = self._make_message()
        assert msg.to_dict()["user_agent"] == "pytest/1.0"

    # ------------------------------------------------------------------
    # __repr__()
    # ------------------------------------------------------------------

    def test_repr_contains_name(self):
        msg = self._make_message()
        assert "Alice" in repr(msg)

    def test_repr_contains_email(self):
        msg = self._make_message()
        assert "alice@example.com" in repr(msg)

    def test_repr_contains_id(self):
        msg = self._make_message()
        assert "1" in repr(msg)
