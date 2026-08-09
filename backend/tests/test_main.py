"""Tests for health / root endpoints defined in app/main.py."""
import pytest


class TestRootEndpoint:
    def test_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_response_is_json(self, client):
        response = client.get("/")
        assert response.headers["content-type"].startswith("application/json")

    def test_response_contains_message(self, client):
        body = client.get("/").json()
        assert "message" in body

    def test_response_contains_version(self, client):
        body = client.get("/").json()
        assert "version" in body

    def test_version_is_string(self, client):
        body = client.get("/").json()
        assert isinstance(body["version"], str)


class TestHealthEndpoint:
    def test_returns_200(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_response_is_json(self, client):
        response = client.get("/api/health")
        assert response.headers["content-type"].startswith("application/json")

    def test_status_is_healthy(self, client):
        body = client.get("/api/health").json()
        assert body.get("status") == "healthy"


class TestCORSHeaders:
    def test_options_request_allowed(self, client):
        """Preflight OPTIONS request should not return 405."""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        # FastAPI/Starlette returns 200 for preflight when CORS is configured
        assert response.status_code in (200, 204)
