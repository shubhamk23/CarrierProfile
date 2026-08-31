"""Tests for the SQLAlchemy ORM model (app/database/models.py).

These tests verify the model's helper methods without requiring a live
database connection.
"""

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
            ip_address="1.2.3.4",
            user_agent="pytest/1.0",
        )
        msg.created_at = overrides.get("created_at", now)

        for key, value in overrides.items():
            if key != "created_at":
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

    def test_to_dict_created_at_is_iso_string(self):
        msg = self._make_message()
        result = msg.to_dict()
        assert isinstance(result["created_at"], str)
        dt = datetime.fromisoformat(result["created_at"])
        assert isinstance(dt, datetime)

    def test_to_dict_created_at_none_when_not_set(self):
        """If created_at is None (e.g., not yet persisted), to_dict should return None."""
        msg = self._make_message(created_at=None)
        result = msg.to_dict()
        assert result["created_at"] is None

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
