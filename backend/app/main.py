import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.routers import contact
from app.config import settings
from app.database.connection import init_db, close_db
from app.middleware import limiter, RateLimitMiddleware

logging.basicConfig(level=logging.INFO if not settings.debug else logging.DEBUG)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Initializes database on startup and closes connections on shutdown.
    """
    if settings.database_url:
        try:
            await init_db()
            logger.info("Database initialized successfully")
        except Exception:
            logger.exception(
                "Database initialization failed; contact form will use email-only delivery"
            )
    else:
        logger.info(
            "No DATABASE_URL configured; contact form will use email-only delivery"
        )

    yield

    try:
        await close_db()
    except Exception:
        logger.exception("Error closing database connections")


app = FastAPI(
    title="Shubham Khanapure Portfolio API",
    description="Backend API for career portfolio website",
    version="1.0.0",
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(RateLimitMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_origin_regex=settings.cors_allow_origin_regex,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

app.include_router(contact.router, prefix="/api", tags=["Contact"])


@app.get("/")
async def root():
    return {"message": "Shubham Khanapure Portfolio API", "version": "1.0.0"}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
