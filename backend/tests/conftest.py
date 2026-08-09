"""Shared fixtures for the CarrierProfile backend test suite."""
import json
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.middleware.rate_limit import limiter

# Minimal valid profile data mirroring the real profile.json structure
MOCK_PROFILE_DATA = {
    "name": "Test User",
    "title": "ML Engineer",
    "subtitle": "AI Specialist",
    "location": "Pune, India",
    "phone": "+91-0000000000",
    "email": "test@example.com",
    "linkedin": "https://linkedin.com/in/test",
    "github": "https://github.com/test",
    "summary": "A test profile summary.",
    "skills": {
        "languages": ["Python", "SQL"],
        "ml_dl_frameworks": ["PyTorch"],
        "computer_vision": ["OpenCV"],
        "generative_ai_nlp": ["LangChain"],
        "mlops_devops": ["Docker"],
        "cloud_data": ["Azure"],
        "software_engineering": ["FastAPI"],
    },
    "experience": [
        {
            "company": "ACME Corp",
            "role": "ML Engineer",
            "location": "Pune, India",
            "period": "2022 - Present",
            "description": ["Built ML models"],
            "technologies": ["Python"],
        }
    ],
    "projects": [
        {
            "title": "Test Project",
            "period": "2023",
            "technologies": ["Python"],
            "description": "A test project",
            "highlights": ["Did something cool"],
        }
    ],
    "education": {
        "degree": "B.E. Computer Engineering",
        "institution": "Test University",
        "location": "Pune, India",
        "period": "2015 - 2019",
    },
    "certifications": [{"title": "AWS Certified", "issuer": "Amazon"}],
    "awards": [
        {
            "title": "Best Paper",
            "year": "2023",
            "description": "Won best paper award",
        }
    ],
}


@pytest.fixture
def mock_profile_data():
    """Return minimal valid profile data as a dict."""
    return MOCK_PROFILE_DATA


@pytest.fixture
def mock_profile_json(mock_profile_data):
    """Return profile data serialised as JSON bytes (for file-open mocking)."""
    return json.dumps(mock_profile_data).encode()


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """
    Reset the in-memory rate-limit storage before each test.

    TestClient requests always resolve to the same client identifier
    (Starlette sets scope["client"] = None), so without a reset every test
    in a module shares one rate-limit bucket and can spuriously start
    returning 429 once enough non-422 requests accumulate.
    """
    limiter.reset()
    yield


@pytest.fixture
def client(mock_profile_data):
    """
    FastAPI TestClient with the profile file-open mocked so tests never
    depend on the filesystem, and a default DB dependency override so
    routes with a `db` dependency don't hit the real (unconfigured)
    database — FastAPI resolves dependencies before evaluating body
    validation errors, so even a request expected to fail validation
    would otherwise blow up on the missing DATABASE_URL.
    """
    import io
    from app.database.connection import get_db

    profile_json = json.dumps(mock_profile_data)

    async def _override_get_db():
        yield AsyncMock()

    with patch(
        "builtins.open",
        side_effect=lambda *args, **kwargs: io.StringIO(profile_json),
    ):
        from app.main import app

        app.dependency_overrides[get_db] = _override_get_db
        try:
            with TestClient(app, raise_server_exceptions=True) as c:
                yield c
        finally:
            app.dependency_overrides.pop(get_db, None)
