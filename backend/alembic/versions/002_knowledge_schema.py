"""Knowledge hub schema (sections, notes, admin_users) with Postgres FTS

Revision ID: 002_knowledge
Revises: 001_initial
Create Date: 2026-05-17 09:00:00.000000

Chains off the existing contact_messages migration (001_initial) and adds
the three knowledge-hub tables without touching anything in the portfolio
schema.

Indexing strategy:
  * `notes.search_vector` is a STORED generated tsvector column that weighs
    title > summary > tags. We build a GIN index on it for ranked full-text
    search via `plainto_tsquery` + `ts_rank`.
  * A `pg_trgm` GIN index on `notes.tags` supports tolerant tag substring
    matching for the search router's tag-filter fallback.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision: str = "002_knowledge"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create sections, notes, admin_users + FTS indexes."""

    # ── Extensions ────────────────────────────────────────────
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # ── sections ──────────────────────────────────────────────
    op.create_table(
        "sections",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon", sa.String(), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_sections_slug"),
    )
    op.create_index("idx_sections_sort_order", "sections", ["sort_order"])

    # ── notes ─────────────────────────────────────────────────
    op.create_table(
        "notes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("section_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("tags", sa.Text(), server_default="[]", nullable=False),
        sa.Column(
            "visibility",
            sa.String(),
            server_default="public",
            nullable=False,
        ),
        sa.Column(
            "level",
            sa.String(),
            server_default="beginner",
            nullable=False,
        ),
        sa.Column("file_path", sa.String(), nullable=False),
        sa.Column("word_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("read_time", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["section_id"],
            ["sections.id"],
            ondelete="CASCADE",
            name="fk_notes_section",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("file_path", name="uq_notes_file_path"),
        sa.UniqueConstraint("section_id", "slug", name="uq_notes_section_slug"),
    )
    op.create_index("idx_notes_section_id", "notes", ["section_id"])
    op.create_index("idx_notes_visibility", "notes", ["visibility"])
    op.create_index(
        "idx_notes_section_visibility", "notes", ["section_id", "visibility"]
    )

    # Generated tsvector column (Postgres 12+). Weights: title A, summary B, tags C.
    op.execute(
        """
        ALTER TABLE notes
        ADD COLUMN search_vector tsvector
        GENERATED ALWAYS AS (
            setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
            setweight(to_tsvector('english', coalesce(summary, '')), 'B') ||
            setweight(to_tsvector('english', coalesce(tags, '')),    'C')
        ) STORED
        """
    )
    op.execute("CREATE INDEX notes_search_idx ON notes USING GIN (search_vector)")
    op.execute(
        "CREATE INDEX notes_tags_trgm ON notes USING GIN (tags gin_trgm_ops)"
    )

    # ── admin_users ───────────────────────────────────────────
    op.create_table(
        "admin_users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username", name="uq_admin_users_username"),
    )


def downgrade() -> None:
    """Reverse the knowledge schema. Leaves contact_messages and pg_trgm extension alone."""
    op.drop_table("admin_users")

    op.execute("DROP INDEX IF EXISTS notes_tags_trgm")
    op.execute("DROP INDEX IF EXISTS notes_search_idx")
    # search_vector column drops with the table.
    op.drop_index("idx_notes_section_visibility", table_name="notes")
    op.drop_index("idx_notes_visibility", table_name="notes")
    op.drop_index("idx_notes_section_id", table_name="notes")
    op.drop_table("notes")

    op.drop_index("idx_sections_sort_order", table_name="sections")
    op.drop_table("sections")
    # pg_trgm extension intentionally not dropped — other tables may use it.
