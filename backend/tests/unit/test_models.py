"""Unit tests for ORM model definitions + metadata."""

import pytest

from app.database.connection import Base
from app.knowledge.models import AdminUser, Note, Section

pytestmark = pytest.mark.unit


class TestMetadataRegistration:
    """Both portfolio and knowledge tables must share one Base.metadata."""

    def test_all_expected_tables_registered(self):
        names = set(Base.metadata.tables.keys())
        assert {"contact_messages", "sections", "notes", "admin_users"} <= names

    def test_notes_has_foreign_key_to_sections(self):
        notes = Base.metadata.tables["notes"]
        fks = list(notes.c.section_id.foreign_keys)
        assert len(fks) == 1
        assert fks[0].column.table.name == "sections"
        # CASCADE on delete is required so removing a section nukes its notes.
        assert fks[0].ondelete == "CASCADE"

    def test_notes_unique_constraint_on_section_slug(self):
        notes = Base.metadata.tables["notes"]
        names = {c.name for c in notes.constraints}
        assert "uq_notes_section_slug" in names

    def test_admin_user_username_is_unique(self):
        admin = Base.metadata.tables["admin_users"]
        names = {c.name for c in admin.constraints}
        assert "uq_admin_users_username" in names

    def test_section_slug_is_unique(self):
        s = Base.metadata.tables["sections"]
        names = {c.name for c in s.constraints}
        assert "uq_sections_slug" in names


class TestModelDefaults:
    def test_note_visibility_default_public(self):
        # SQLAlchemy server_default is a literal; check the Column definition.
        col = Note.__table__.c.visibility
        assert col.server_default.arg == "public"   # type: ignore[attr-defined]

    def test_note_level_default_beginner(self):
        col = Note.__table__.c.level
        assert col.server_default.arg == "beginner"   # type: ignore[attr-defined]

    def test_section_sort_order_default_zero(self):
        col = Section.__table__.c.sort_order
        assert col.server_default.arg == "0"   # type: ignore[attr-defined]
