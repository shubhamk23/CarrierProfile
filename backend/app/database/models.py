from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.sql import func
from app.database.connection import Base


class ContactMessage(Base):
    """SQLAlchemy model for contact form messages"""

    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    message = Column(Text, nullable=False)

    ip_address = Column(String(45), nullable=True)  # Supports IPv4 and IPv6
    user_agent = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (Index("idx_messages_created_at_desc", created_at.desc()),)

    def __repr__(self):
        return f"<ContactMessage(id={self.id}, name='{self.name}', email='{self.email}', created_at={self.created_at})>"

    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "subject": self.subject,
            "message": self.message,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
