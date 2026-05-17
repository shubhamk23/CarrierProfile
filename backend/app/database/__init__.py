"""Database package for SQLAlchemy models and connection management.

Knowledge-hub models are not imported here to avoid a circular import
between ``app.database`` and ``app.knowledge.models``. They are imported
explicitly at the call sites that need them registered with Base.metadata:

  * ``app.main`` at startup (lifespan).
  * ``alembic/env.py`` at migration time.
"""

from app.database.connection import async_session_maker, engine, get_db
from app.database.models import ContactMessage

__all__ = ["get_db", "engine", "async_session_maker", "ContactMessage"]
