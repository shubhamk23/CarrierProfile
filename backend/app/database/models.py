from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Index
from sqlalchemy.sql import func
from app.database.connection import Base


class ContactMessage(Base):
    """SQLAlchemy model for contact form messages"""

    __tablename__ = "contact_messages"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Contact information
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    subject = Column(String(500), nullable=False)
    message = Column(Text, nullable=False)

    # Metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    read = Column(Boolean, default=False, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)  # Supports IPv4 and IPv6
    user_agent = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Indexes for common queries
    __table_args__ = (
        Index('idx_messages_timestamp_desc', timestamp.desc()),
        Index('idx_messages_read_timestamp', read, timestamp.desc()),
    )

    def __repr__(self):
        return f"<ContactMessage(id={self.id}, name='{self.name}', email='{self.email}', timestamp={self.timestamp})>"

    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "subject": self.subject,
            "message": self.message,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "read": self.read,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
