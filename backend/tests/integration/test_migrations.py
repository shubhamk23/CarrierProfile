"""Alembic migrations against a real PostgreSQL."""

import pytest
from sqlalchemy import create_engine, inspect

from tests.integration.conftest import DATABASE_URL, run_alembic

pytestmark = pytest.mark.integration


def _inspect():
    return inspect(create_engine(DATABASE_URL))


def test_upgrade_head_creates_expected_schema(migrated_db):
    inspector = _inspect()
    assert "contact_messages" in inspector.get_table_names()
    columns = {c["name"] for c in inspector.get_columns("contact_messages")}
    assert columns == {
        "id",
        "name",
        "email",
        "subject",
        "message",
        "ip_address",
        "user_agent",
        "created_at",
    }


def test_orm_model_matches_migrated_schema(migrated_db):
    """Model/migration drift is what create_all used to hide; check it directly."""
    from app.database.models import ContactMessage

    model_cols = {c.name for c in ContactMessage.__table__.columns}
    db_cols = {c["name"] for c in _inspect().get_columns("contact_messages")}
    assert model_cols == db_cols


def test_downgrade_to_base_then_upgrade_round_trips(migrated_db):
    run_alembic("downgrade", "base")
    assert "contact_messages" not in _inspect().get_table_names()
    run_alembic("upgrade", "head")
    assert "contact_messages" in _inspect().get_table_names()


def test_current_revision_is_single_head(migrated_db):
    out = run_alembic("heads").stdout.strip().splitlines()
    assert len(out) == 1, f"expected one migration head, got: {out}"
