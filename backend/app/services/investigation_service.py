"""
AIOps Agent – Investigation Service
======================================
Orchestrates the 12-node LangGraph autonomous agent lifecycle:
1. Run the 12-node LangGraph StateGraph agent.
2. Extract the validated InvestigationReport from agent state.
3. Ensure persistence to SQLite.
4. Return the report conforming to API schemas.
"""

import uuid
import json
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from app.agents.graph import get_investigation_graph
from app.schemas.report import (
    InvestigationReport,
    InvestigationSummary,
    SeverityLevel,
    ConfidenceLevel,
    EvidenceItem,
    DocumentReference,
    RemediationStep,
)
from app.database.connection import InvestigationRecord
from app.core.logging import get_logger
from app.core.exceptions import InvestigationNotFoundError

logger = get_logger(__name__)


def run_investigation(
    logs: str,
    question: str,
    db: Session,
    document_collection: Optional[str] = None,
) -> InvestigationReport:
    """
    Run the full 12-node autonomous investigation workflow and persist results.
    """
    investigation_id = str(uuid.uuid4())
    logger.info("Starting 12-node autonomous investigation", id=investigation_id, log_len=len(logs))

    # ── Step 1: Run Upgraded 12-Node LangGraph Agent ─────────────────────────
    graph = get_investigation_graph()

    initial_state = {
        "investigation_id": investigation_id,
        "raw_logs": logs,
        "logs": logs,
        "user_question": question,
        "question": question,
        "document_collection": document_collection,
        "tool_calls_made": [],
        "errors": [],
        "node_execution_trace": [],
        "retry_count": 0,
        "iteration_count": 0,
    }

    try:
        final_state = graph.invoke(initial_state)
    except Exception as e:
        logger.error("LangGraph 12-node execution failed", error=str(e), id=investigation_id)
        raise

    # ── Step 2: Extract & Validate Final Response ────────────────────────────
    final_dict = final_state.get("final_response") or final_state.get("investigation_report")

    if final_dict and isinstance(final_dict, dict) and "incident_title" in final_dict:
        try:
            # Directly parse from final agent output
            report = InvestigationReport(**final_dict)
        except Exception as pydantic_err:
            logger.warning("Pydantic direct parse warning, falling back to field extraction", error=str(pydantic_err))
            report = _build_report_from_state(final_state, logs, question, investigation_id)
    else:
        report = _build_report_from_state(final_state, logs, question, investigation_id)

    # ── Step 3: Ensure Persistence in SQLite ─────────────────────────────────
    try:
        existing = db.query(InvestigationRecord).filter(InvestigationRecord.id == report.investigation_id).first()
        if not existing:
            record = InvestigationRecord(
                id=report.investigation_id,
                incident_title=report.incident_title,
                severity=report.severity.value,
                confidence=report.confidence.value,
                original_logs=logs,
                question=question,
                report_json=report.model_dump_json(),
                error_count=report.error_count,
                warning_count=report.warning_count,
                total_log_entries=report.total_log_entries,
                affected_services_json=json.dumps(report.affected_services),
                created_at=report.created_at,
            )
            db.add(record)
            db.commit()
            logger.info("Investigation persisted to SQLite", id=report.investigation_id)
    except Exception as e:
        logger.warning("Secondary persistence notice", error=str(e))
        db.rollback()

    return report


def _build_report_from_state(
    final_state: dict,
    logs: str,
    question: str,
    investigation_id: str,
) -> InvestigationReport:
    """Helper to convert raw AgentState fields to a strictly typed InvestigationReport."""
    freq = final_state.get("frequency_report") or final_state.get("freq_report") or {}
    severity_data = final_state.get("severity_result") or {}
    pattern_data = final_state.get("pattern_report") or {}
    retrieved_docs = final_state.get("retrieved_documents") or final_state.get("retrieved_docs") or []

    # Map string severity to enum
    severity_str = str(final_state.get("severity") or severity_data.get("severity") or "MEDIUM").upper()
    try:
        severity = SeverityLevel(severity_str)
    except ValueError:
        severity = SeverityLevel.MEDIUM

    # Map string confidence to enum
    confidence_str = str(final_state.get("confidence_level") or final_state.get("confidence") or "MEDIUM").upper()
    try:
        confidence = ConfidenceLevel(confidence_str)
    except ValueError:
        confidence = ConfidenceLevel.MEDIUM

    # Evidence items
    evidence_items = []
    for ev in (final_state.get("supporting_evidence") or [])[:10]:
        evidence_items.append(
            EvidenceItem(
                source=ev.get("source", "log"),
                content=ev.get("content", ""),
                relevance=ev.get("relevance", ""),
            )
        )

    # Document references
    doc_refs = []
    for doc in retrieved_docs[:5]:
        meta = doc.get("metadata", {})
        doc_refs.append(
            DocumentReference(
                document_name=meta.get("source", "Knowledge Base Runbook"),
                source_file=meta.get("file_path", meta.get("source", "")),
                excerpt=doc.get("content", "")[:300],
                relevance_score=doc.get("relevance_score", 0.0),
                page_number=meta.get("page"),
            )
        )

    # Remediation steps
    remediation = []
    for step in (final_state.get("remediation_steps") or [])[:8]:
        try:
            remediation.append(
                RemediationStep(
                    priority=int(step.get("priority", 5)),
                    action=step.get("action", ""),
                    rationale=step.get("rationale", ""),
                    estimated_impact=step.get("estimated_impact", ""),
                )
            )
        except Exception:
            pass

    pattern_names = final_state.get("detected_pattern_names") or [
        p.get("name", "") for p in pattern_data.get("detected_patterns", [])
    ]

    return InvestigationReport(
        investigation_id=investigation_id,
        incident_title=final_state.get("incident_title", "Application Incident Investigation"),
        severity=severity,
        created_at=datetime.utcnow(),
        executive_summary=final_state.get("executive_summary", ""),
        technical_summary=final_state.get("technical_summary", ""),
        symptoms=final_state.get("symptoms", []),
        affected_services=final_state.get("affected_services") or severity_data.get("affected_services", []),
        affected_endpoints=final_state.get("affected_endpoints") or severity_data.get("affected_endpoints", []),
        error_count=final_state.get("error_count", 0) or freq.get("level_counts", {}).get("ERROR", 0),
        warning_count=final_state.get("warning_count", 0) or freq.get("level_counts", {}).get("WARNING", 0),
        total_log_entries=final_state.get("total_entries", 0) or freq.get("total_entries", 0),
        detected_patterns=pattern_names,
        probable_root_cause=final_state.get("probable_root_cause", ""),
        alternative_causes=final_state.get("alternative_causes", []),
        supporting_evidence=evidence_items,
        document_references=doc_refs,
        recommended_remediation=remediation,
        immediate_actions=final_state.get("immediate_actions", []),
        confidence=confidence,
        confidence_reasoning=final_state.get("confidence_reasoning", ""),
        additional_info_required=final_state.get("additional_info", []),
        limitations=final_state.get("limitations", []),
    )


def get_investigation_by_id(investigation_id: str, db: Session) -> InvestigationReport:
    """Retrieve a previously run investigation by its UUID."""
    record = db.query(InvestigationRecord).filter(InvestigationRecord.id == investigation_id).first()
    if not record:
        raise InvestigationNotFoundError(f"Investigation with ID '{investigation_id}' not found")
    data = json.loads(record.report_json)
    return InvestigationReport(**data)


def list_investigations(limit: int, db: Session) -> List[InvestigationSummary]:
    """Retrieve summaries of previous investigations for history view."""
    records = db.query(InvestigationRecord).order_by(InvestigationRecord.created_at.desc()).limit(limit).all()
    summaries = []
    for r in records:
        try:
            summaries.append(
                InvestigationSummary(
                    investigation_id=r.id,
                    incident_title=r.incident_title,
                    severity=SeverityLevel(r.severity),
                    confidence=ConfidenceLevel(r.confidence),
                    created_at=r.created_at,
                    error_count=r.error_count,
                    affected_services=r.affected_services,
                )
            )
        except Exception as e:
            logger.warning("Failed to parse investigation record summary", id=r.id, error=str(e))
    return summaries
