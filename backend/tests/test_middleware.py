"""Tests for the rate-limit middleware helpers (app/middleware/rate_limit.py).

get_client_identifier() is a pure function that reads request headers, so
we can test it without starting the full FastAPI app.
"""

from typing import Optional
from unittest.mock import MagicMock

from app.middleware.rate_limit import get_client_identifier


def _make_request(
    x_forwarded_for: Optional[str] = None,
    client_host: str = "1.1.1.1",
    extra_headers: Optional[dict] = None,
):
    """Build a minimal mock Request object."""
    request = MagicMock()
    headers = dict(extra_headers or {})
    if x_forwarded_for is not None:
        headers["X-Forwarded-For"] = x_forwarded_for
    request.headers = headers
    request.client = MagicMock()
    request.client.host = client_host
    return request


class TestGetClientIdentifier:
    def test_returns_ip_from_x_forwarded_for(self):
        request = _make_request(x_forwarded_for="2.3.4.5")
        assert get_client_identifier(request) == "2.3.4.5"

    def test_takes_first_ip_when_multiple_forwarded(self):
        """X-Forwarded-For can contain a comma-separated chain of proxies."""
        request = _make_request(x_forwarded_for="2.3.4.5, 10.0.0.1, 192.168.1.1")
        assert get_client_identifier(request) == "2.3.4.5"

    def test_strips_whitespace_from_forwarded_ip(self):
        request = _make_request(x_forwarded_for="  2.3.4.5  ")
        assert get_client_identifier(request) == "2.3.4.5"

    def test_falls_back_to_client_host_when_no_header(self):
        request = _make_request(x_forwarded_for=None, client_host="9.9.9.9")
        result = get_client_identifier(request)
        # get_remote_address returns request.client.host when no forwarded header
        assert result == "9.9.9.9"

    def test_handles_single_ip_in_forwarded_header(self):
        request = _make_request(x_forwarded_for="203.0.113.42")
        assert get_client_identifier(request) == "203.0.113.42"

    def test_handles_ipv6_in_forwarded_header(self):
        ipv6 = "2001:db8::1"
        request = _make_request(x_forwarded_for=ipv6)
        assert get_client_identifier(request) == ipv6


class TestSpoofResistance:
    """The client controls X-Forwarded-For, so Vercel's own headers win."""

    def test_vercel_header_beats_spoofed_x_forwarded_for(self):
        request = _make_request(
            x_forwarded_for="6.6.6.6",
            extra_headers={"x-vercel-forwarded-for": "9.9.9.9"},
        )
        assert get_client_identifier(request) == "9.9.9.9"

    def test_real_ip_beats_spoofed_x_forwarded_for(self):
        request = _make_request(
            x_forwarded_for="6.6.6.6", extra_headers={"x-real-ip": "8.8.8.8"}
        )
        assert get_client_identifier(request) == "8.8.8.8"

    def test_vercel_header_beats_real_ip(self):
        request = _make_request(
            extra_headers={"x-vercel-forwarded-for": "9.9.9.9", "x-real-ip": "8.8.8.8"}
        )
        assert get_client_identifier(request) == "9.9.9.9"
