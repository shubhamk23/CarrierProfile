"""SQLAlchemy ORM models for the knowledge hub.

These tables live alongside the portfolio's `contact_messages` in the same
Postgres database. They share the portfolio's declarative ``Base`` so
Alembic autogenerate sees them and so a single ``Base.metadata`` reflects
the whole application schema.
"""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.connection import Base


class Section(Base):
    """A top-level grouping of notes (e.g. NLP, Vision)."""

    __tablename__ = "sections"
    __table_args__ = (UniqueConstraint("slug", name="uq_sections_slug"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)
    sort_order = Column(Integer, server_default="0", nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    notes = relationship(
        "Note", back_populates="section", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Section slug={self.slug!r}>"


class Note(Base):
    """A single markdown note inside a section."""

    __tablename__ = "notes"
    __table_args__ = (
        UniqueConstraint("section_id", "slug", name="uq_notes_section_slug"),
        UniqueConstraint("file_path", name="uq_notes_file_path"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String, nullable=False)
    section_id = Column(
        Integer,
        ForeignKey("sections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    tags = Column(Text, server_default="[]", nullable=False)  # JSON-encoded list
    visibility = Column(String, server_default="public", nullable=False)
    level = Column(String, server_default="beginner", nullable=False)
    file_path = Column(String, nullable=False)
    word_count = Column(Integer, server_default="0", nullable=False)
    read_time = Column(Integer, server_default="0", nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    section = relationship("Section", back_populates="notes")

    def __repr__(self) -> str:
        return f"<Note section_id={self.section_id} slug={self.slug!r}>"


class AdminUser(Base):
    """Knowledge-hub admin account (separate from any future portfolio auth)."""

    __tablename__ = "admin_users"

    __table_args__ = (
        UniqueConstraint("username", name="uq_admin_users_username"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<AdminUser username={self.username!r}>"
