"""Shared fixtures for the CarrierProfile backend test suite."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """Rate limiter storage is process-wide (module-level singleton); reset
    it before every test so tests don't trip each other's limits."""
    from app.middleware import limiter

    limiter.reset()
    yield


@pytest.fixture
def client():
    """FastAPI TestClient against the real app."""
    from app.main import app

    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


@pytest.fixture
def mock_db_session():
    """Async mock of an SQLAlchemy AsyncSession."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.execute = AsyncMock()
    session.rollback = AsyncMock()
    return session
