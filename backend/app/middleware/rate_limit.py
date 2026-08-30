from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request
from app.config import settings


def get_client_identifier(request: Request) -> str:
    """
    Get client identifier for rate limiting.
    Uses X-Forwarded-For header if available (Vercel provides this),
    otherwise falls back to direct IP address.
    """
    # Vercel sets X-Forwarded-For header with the real client IP
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, use the first one (client IP)
        return forwarded_for.split(",")[0].strip()

    # Fallback to direct connection IP
    return get_remote_address(request)


# Create limiter instance
limiter = Limiter(
    key_func=get_client_identifier,
    default_limits=[],  # No default limits, we'll apply per-route
    enabled=settings.rate_limit_enabled,
    # ponytail: per-instance limit, resets on cold start. Upgrade to Upstash
    # Redis storage_uri if abuse becomes real.
    storage_uri="memory://",
)

# Middleware class for adding to FastAPI app
RateLimitMiddleware = SlowAPIMiddleware
