"""Create contact_messages table

Revision ID: 001_initial
Revises:
Create Date: 2026-01-24 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create contact_messages table"""
    op.create_table(
        'contact_messages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('subject', sa.String(length=500), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('read', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('idx_contact_messages_name', 'contact_messages', ['name'])
    op.create_index('idx_contact_messages_email', 'contact_messages', ['email'])
    op.create_index('idx_contact_messages_read', 'contact_messages', ['read'])
    op.create_index('idx_messages_timestamp_desc', 'contact_messages', [sa.text('timestamp DESC')])
    op.create_index('idx_messages_read_timestamp', 'contact_messages', ['read', sa.text('timestamp DESC')])


def downgrade() -> None:
    """Drop contact_messages table"""
    op.drop_index('idx_messages_read_timestamp', table_name='contact_messages')
    op.drop_index('idx_messages_timestamp_desc', table_name='contact_messages')
    op.drop_index('idx_contact_messages_read', table_name='contact_messages')
    op.drop_index('idx_contact_messages_email', table_name='contact_messages')
    op.drop_index('idx_contact_messages_name', table_name='contact_messages')
    op.drop_table('contact_messages')
