"""
AIOps Agent – Pydantic Schemas: Incident
==========================================
Defines the request/response models for incident-related API endpoints.

Why Pydantic?
- Automatic request validation (FastAPI uses these at the API layer).
- Clear data contracts between frontend, API, and backend services.
- Automatic JSON serialisation with .model_dump().
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class IncidentAnalysisRequest(BaseModel):
    """
    Request body for POST /api/incidents/analyze.

    The user provides raw log text and we return structured analysis.
    """

    logs: str = Field(
        ...,
        description="Raw log content to analyse",
        min_length=10,
        max_length=500_000,
        examples=["ERROR: Database connection timeout\nERROR: Connection pool exhausted"],
    )

    @field_validator("logs")
    @classmethod
    def logs_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Log content cannot be empty or whitespace only")
        return v


class LogLevelCount(BaseModel):
    """Count of log entries per level."""

    level: str
    count: int
    percentage: float


class TopError(BaseModel):
    """A frequently occurring error message with its count."""

    message: str
    count: int
    percentage: float


class DetectedPatternSchema(BaseModel):
    """A known incident pattern detected in the logs."""

    pattern_id: str
    name: str
    description: str
    probable_cause: str
    severity: str
    match_count: int
    matched_lines: List[str]


class IncidentAnalysisResponse(BaseModel):
    """
    Response body for POST /api/incidents/analyze.
    Contains structured analysis without LLM involvement.
    """

    success: bool = True
    total_log_entries: int
    level_counts: Dict[str, int]
    error_rate_percent: float
    unique_error_count: int
    top_errors: List[TopError]
    top_warnings: List[TopError]
    detected_patterns: List[DetectedPatternSchema]
    overall_severity: str
    severity_score: int
    severity_confidence: str
    severity_reasoning: List[str]
    affected_services: List[str]
    affected_endpoints: List[str]
    summary: str  # One-line human-readable summary

    model_config = {"from_attributes": True}
