"""Tests for health / root endpoints defined in app/main.py."""


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
    def test_preflight_request_allowed(self, client):
        """A real CORS preflight (Origin + Access-Control-Request-Method) must
        be intercepted by CORSMiddleware, not 405 from the router."""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code in (200, 204)
        assert (
            response.headers["access-control-allow-origin"] == "http://localhost:3000"
        )

    def test_preflight_from_vercel_preview_subdomain_allowed(self, client):
        """allow_origin_regex must match *.vercel.app preview deployments."""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "https://carrier-profile-git-preview.vercel.app",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code in (200, 204)
        assert (
            response.headers["access-control-allow-origin"]
            == "https://carrier-profile-git-preview.vercel.app"
        )

    def test_disallowed_origin_gets_no_cors_header(self, client):
        response = client.options(
            "/api/health",
            headers={
                "Origin": "https://evil.example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert "access-control-allow-origin" not in response.headers
