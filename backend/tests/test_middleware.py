"""Tests for the rate-limit middleware helpers (app/middleware/rate_limit.py).

get_client_identifier() is a pure function that reads request headers, so
we can test it without starting the full FastAPI app.
"""
import pytest
from unittest.mock import MagicMock

from app.middleware.rate_limit import get_client_identifier


def _make_request(x_forwarded_for: str | None = None, client_host: str = "1.1.1.1"):
    """Build a minimal mock Request object."""
    request = MagicMock()
    headers = {}
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
