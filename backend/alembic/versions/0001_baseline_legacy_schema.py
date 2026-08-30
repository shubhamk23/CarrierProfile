"""baseline: legacy create_all schema (pre-Alembic)

This migration documents the schema as it existed in production before
Alembic was adopted (created via SQLAlchemy's Base.metadata.create_all at
app startup). It is not meant to be run with `alembic upgrade` against the
live database -- that table already exists. Apply it with `alembic stamp
0001_baseline` once, so Alembic knows the live DB's history starts here,
then run `alembic upgrade head` to apply 0002 on top of it.

A fresh database (e.g. local dev, CI) can run the full chain with
`alembic upgrade head` normally, since 0001 creates the table `create_all`
would have and 0002 immediately cleans it up to the current model shape.

Revision ID: 0001_baseline
Revises:
Create Date: 2026-08-30
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "contact_messages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("subject", sa.String(length=500), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "read", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_contact_messages_name", "contact_messages", ["name"])
    op.create_index("ix_contact_messages_email", "contact_messages", ["email"])
    op.create_index("ix_contact_messages_read", "contact_messages", ["read"])
    op.create_index(
        "idx_messages_timestamp_desc", "contact_messages", [sa.text("timestamp DESC")]
    )
    op.create_index(
        "idx_messages_read_timestamp",
        "contact_messages",
        ["read", sa.text("timestamp DESC")],
    )


def downgrade() -> None:
    op.drop_table("contact_messages")
