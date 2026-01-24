from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from slowapi.errors import RateLimitExceeded

from app.routers import profile, blog, contact
from app.config import settings
from app.database.connection import init_db, close_db
from app.middleware import limiter, RateLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Initializes database on startup and closes connections on shutdown.
    """
    # Startup
    print("🚀 Starting CarrierProfile API...")
    try:
        if settings.database_url:
            print("📊 Initializing database connection...")
            await init_db()
            print("✅ Database initialized successfully")
        else:
            print("⚠️  No database URL configured, using JSON storage")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("⚠️  Falling back to JSON storage")

    yield

    # Shutdown
    print("🛑 Shutting down CarrierProfile API...")
    try:
        await close_db()
        print("✅ Database connections closed")
    except Exception as e:
        print(f"⚠️  Error closing database: {e}")


app = FastAPI(
    title="Shubham Khanapure Portfolio API",
    description="Backend API for career portfolio website",
    version="1.0.0",
    lifespan=lifespan,
)

# Add rate limiter state
app.state.limiter = limiter

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Include routers
app.include_router(profile.router, prefix="/api", tags=["Profile"])
app.include_router(blog.router, prefix="/api", tags=["Blog"])
app.include_router(contact.router, prefix="/api", tags=["Contact"])


@app.get("/")
async def root():
    return {"message": "Shubham Khanapure Portfolio API", "version": "1.0.0"}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
