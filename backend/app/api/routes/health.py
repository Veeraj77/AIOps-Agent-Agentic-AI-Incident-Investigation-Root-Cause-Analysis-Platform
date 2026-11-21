"""
AIOps Agent – API Route: Health Check
=======================================
Simple health check endpoint used by:
- Docker health checks
- Load balancers
- Monitoring tools (Prometheus, Grafana, etc.)

Returns application status and version.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from app.config import get_settings

router = APIRouter()
settings = get_settings()


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    llm_provider: str
    llm_model: str


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """
    Returns the application health status.

    Use this endpoint to verify the backend is running.
    """
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version=settings.app_version,
        llm_provider=settings.llm_provider,
        llm_model=settings.llm_model,
    )
