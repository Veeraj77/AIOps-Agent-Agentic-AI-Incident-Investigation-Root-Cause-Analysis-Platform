"""
AIOps Agent – FastAPI Application Entry Point
==============================================
This is where the FastAPI application is created and configured.

What happens here:
1. Create the FastAPI app with metadata (title, description, version).
2. Configure CORS (Cross-Origin Resource Sharing) so the React frontend can call the API.
3. Register exception handlers for custom errors.
4. Include all API routers (health, incidents, documents, investigations).
5. Initialise the database on startup.
6. Configure structured logging.

Why CORS is needed:
- The React frontend runs on http://localhost:5173 (Vite dev server).
- The FastAPI backend runs on http://localhost:8000.
- Browsers block cross-origin requests by default.
- CORS middleware tells the browser: "these origins are trusted".
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.core.exceptions import AIOpsBaseException
from app.database.connection import init_db
from app.api.routes import health, incidents, documents, investigations

# ── Initialise Logging First ──────────────────────────────────────────────────
configure_logging()
logger = get_logger(__name__)
settings = get_settings()


# ── Application Lifespan ──────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Code here runs BEFORE the server accepts requests (startup).
    Code after 'yield' runs AFTER the server shuts down.

    Why use lifespan instead of @app.on_event('startup')?
    - FastAPI recommends lifespan as the modern approach.
    - Cleaner resource management with async context managers.
    """
    # ── Startup ───────────────────────────────────────────────────────────────
    logger.info(
        "AIOps Agent starting",
        version=settings.app_version,
        host=settings.host,
        port=settings.port,
        llm_provider=settings.llm_provider,
    )

    # Ensure required directories exist
    for dir_path in [settings.storage_dir, settings.upload_dir, settings.chroma_persist_dir]:
        os.makedirs(dir_path, exist_ok=True)

    # Initialise SQLite database tables
    init_db()

    # Validate LLM configuration (warn but don't crash – some routes work without LLM)
    if not settings.groq_api_key:
        logger.warning(
            "GROQ_API_KEY is not set. Investigation routes will fail until configured. "
            "Get your free key at https://console.groq.com"
        )
    else:
        logger.info("LLM configuration detected", provider=settings.llm_provider)

    logger.info("AIOps Agent is ready to serve requests")
    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    logger.info("AIOps Agent shutting down")


# ── Create FastAPI Application ────────────────────────────────────────────────
app = FastAPI(
    title="AIOps Agent API",
    description=(
        "Agentic AI-Powered Incident Investigation and Root Cause Analysis System. "
        "Upload logs, ask questions, get AI-powered insights."
    ),
    version=settings.app_version,
    docs_url="/docs",        # Swagger UI at http://localhost:8000/docs
    redoc_url="/redoc",      # ReDoc UI at http://localhost:8000/redoc
    lifespan=lifespan,
)


# ── CORS Middleware ───────────────────────────────────────────────────────────
# Allows the React frontend (localhost:5173) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],    # Allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],    # Allow all headers
)


# ── Custom Exception Handlers ─────────────────────────────────────────────────
@app.exception_handler(AIOpsBaseException)
async def aiops_exception_handler(request: Request, exc: AIOpsBaseException):
    """
    Catch any AIOpsBaseException (and subclasses) and return a proper JSON error.
    Without this, FastAPI would return a generic 500 Internal Server Error.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.message, "status_code": exc.status_code},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch any unexpected exceptions and return a safe error message."""
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "An unexpected error occurred", "status_code": 500},
    )


# ── Register API Routers ──────────────────────────────────────────────────────
# Each router handles a group of related endpoints.
app.include_router(health.router)                               # GET /health
app.include_router(incidents.router, prefix="/api/incidents")   # POST /api/incidents/analyze
app.include_router(documents.router, prefix="/api/documents")   # POST /api/documents/upload
app.include_router(investigations.router, prefix="/api/investigations")  # POST /api/investigations/run


# ── Root Endpoint ─────────────────────────────────────────────────────────────
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint – confirms the API is running.
    Visit http://localhost:8000/docs for the full API documentation.
    """
    return {
        "message": "AIOps Agent API is running",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }
