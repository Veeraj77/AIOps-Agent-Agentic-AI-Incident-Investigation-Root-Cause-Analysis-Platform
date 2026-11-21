"""
AIOps Agent – Pydantic Schemas: Investigation Report
======================================================
Defines the full investigation report structure.

The report separates:
- OBSERVED FACTS: What is in the logs (deterministic analysis).
- AI HYPOTHESES: LLM-generated root cause and recommendations.

This distinction is critical for engineering trust and credibility.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class SeverityLevel(str, Enum):
    """Allowed severity levels for an incident."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class ConfidenceLevel(str, Enum):
    """AI confidence levels for the root cause hypothesis."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class EvidenceItem(BaseModel):
    """
    A single piece of evidence supporting the root cause hypothesis.
    Evidence must come directly from logs – not AI imagination.
    """
    source: str = Field(..., description="'log' or 'document'")
    content: str = Field(..., description="The actual log line or document excerpt")
    relevance: str = Field(..., description="Why this evidence is relevant")
    line_number: Optional[int] = Field(None, description="Log line number if applicable")


class DocumentReference(BaseModel):
    """A retrieved knowledge base document used in the investigation."""
    document_name: str
    source_file: str
    excerpt: str
    relevance_score: float
    page_number: Optional[int] = None


class RemediationStep(BaseModel):
    """A specific, actionable remediation step."""
    priority: int = Field(..., description="1 = highest priority", ge=1, le=10)
    action: str = Field(..., description="What to do")
    rationale: str = Field(..., description="Why this action will help")
    estimated_impact: str = Field(..., description="Expected effect if applied")


class InvestigationReport(BaseModel):
    """
    Full AI-generated investigation report.

    Sections:
    1. Identification  – What is the incident?
    2. Evidence        – What do the logs show? (FACTS)
    3. Root Cause      – Why did it happen? (AI HYPOTHESIS)
    4. Remediation     – How to fix it?
    5. Meta            – Confidence, limitations, next steps.
    """

    # ── Identification ────────────────────────────────────────────────────────
    investigation_id: str = Field(..., description="Unique investigation UUID")
    incident_title: str = Field(..., description="Short descriptive title")
    severity: SeverityLevel
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # ── Summary ───────────────────────────────────────────────────────────────
    executive_summary: str = Field(
        ..., description="2-3 sentence overview for a non-technical audience"
    )
    technical_summary: str = Field(
        ..., description="Detailed summary for engineers"
    )

    # ── Observed Facts (from log analysis – deterministic) ───────────────────
    symptoms: List[str] = Field(
        default_factory=list, description="Observable symptoms from logs"
    )
    affected_services: List[str] = Field(default_factory=list)
    affected_endpoints: List[str] = Field(default_factory=list)
    error_count: int = Field(default=0)
    warning_count: int = Field(default=0)
    total_log_entries: int = Field(default=0)
    detected_patterns: List[str] = Field(
        default_factory=list,
        description="Names of matching known incident patterns",
    )

    # ── AI Hypothesis (LLM-generated – clearly labelled) ─────────────────────
    probable_root_cause: str = Field(
        ...,
        description="[AI HYPOTHESIS] Most likely root cause. NOT a confirmed fact.",
    )
    alternative_causes: List[str] = Field(
        default_factory=list,
        description="[AI HYPOTHESIS] Other possible causes to investigate",
    )

    # ── Evidence ──────────────────────────────────────────────────────────────
    supporting_evidence: List[EvidenceItem] = Field(
        default_factory=list,
        description="Log lines and documents supporting the root cause",
    )
    document_references: List[DocumentReference] = Field(
        default_factory=list,
        description="Retrieved knowledge base documents",
    )

    # ── Remediation ───────────────────────────────────────────────────────────
    recommended_remediation: List[RemediationStep] = Field(
        default_factory=list,
        description="Prioritised, actionable remediation steps",
    )
    immediate_actions: List[str] = Field(
        default_factory=list,
        description="Things to do RIGHT NOW to restore service",
    )

    # ── Meta ──────────────────────────────────────────────────────────────────
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    confidence_reasoning: str = Field(
        default="",
        description="Why the AI assigned this confidence level",
    )
    additional_info_required: List[str] = Field(
        default_factory=list,
        description="What additional information would improve the diagnosis",
    )
    limitations: List[str] = Field(
        default_factory=list,
        description="Known limitations or caveats of this analysis",
    )

    model_config = {"from_attributes": True}


class InvestigationRequest(BaseModel):
    """Request body for POST /api/investigations/run."""

    logs: str = Field(
        ...,
        min_length=10,
        max_length=500_000,
        description="Raw log content to investigate",
    )
    question: str = Field(
        default="Why is the application failing?",
        max_length=1000,
        description="Specific investigation question",
    )
    document_collection: Optional[str] = Field(
        default=None,
        description="ChromaDB collection to search for context",
    )


class InvestigationSummary(BaseModel):
    """Lightweight summary for the history list endpoint."""

    investigation_id: str
    incident_title: str
    severity: str
    confidence: str
    created_at: datetime
    error_count: int
    affected_services: List[str]

    model_config = {"from_attributes": True}
