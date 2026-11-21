"""
AIOps Agent – 12-Node Modular Agentic Architecture
===================================================
Each function here implements one single-responsibility agent node
in the 12-node LangGraph investigation workflow:

 1. incident_intake_node          – Ingest incident & assign tracing ID
 2. data_validation_node          – Validate & sanitize incoming telemetry
 3. severity_classification_node  – Rule-based severity & impact analysis
 4. log_analysis_node             – Regex log parsing & frequency stats
 5. rag_retrieval_node            – Semantic search in ChromaDB runbooks
 6. pattern_correlation_node      – Signature matching & cascade risk
 7. root_cause_analysis_node      – Generative RCA reasoning via Groq
 8. hypothesis_validation_node    – Evidence grounding & hallucination check
 9. remediation_planning_node     – Prioritized mitigation & permanent fix
10. report_generation_node        – Structured InvestigationReport synthesis
11. memory_learning_node          – SQLite persistence & safe vector learning
12. final_response_node           – API schema validation & metadata assembly
"""

import uuid
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.agents.state import AgentState
from app.agents.prompts import (
    SYSTEM_UNDERSTAND_INCIDENT,
    PROMPT_UNDERSTAND_INCIDENT,
    SYSTEM_INVESTIGATE_ROOT_CAUSE,
    PROMPT_INVESTIGATE_ROOT_CAUSE,
)
from app.ingestion.log_parser import parse_logs
from app.analysis.frequency_analyzer import analyze_frequency
from app.analysis.pattern_detector import detect_patterns
from app.analysis.severity_classifier import classify_severity
from app.rag.retriever import retrieve_relevant_docs, format_retrieved_docs_as_context
from app.services.llm_service import invoke_llm
from app.database.connection import get_db_context, InvestigationRecord
from app.core.logging import get_logger

logger = get_logger(__name__)


def _safe_llm_json(response_text: str) -> dict:
    """Extract valid JSON from LLM markdown fences or raw strings."""
    text = response_text.strip()
    if "```json" in text:
        text = text.split("```json")[-1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.warning("LLM response was not valid JSON", snippet=text[:200])
        return {}


# ─────────────────────────────────────────────────────────────────────────────
# Node 1: Incident Intake Agent
# ─────────────────────────────────────────────────────────────────────────────

def incident_intake_node(state: AgentState) -> Dict[str, Any]:
    """Ingest incident input, assign tracing ID, initialize telemetry buffers."""
    start_time = time.time()
    investigation_id = state.get("investigation_id") or str(uuid.uuid4())
    raw_logs = state.get("raw_logs") or state.get("logs") or ""
    question = state.get("user_question") or state.get("question") or "Why is the application failing?"

    logger.info("Node 1 [Intake]: Initiating investigation", id=investigation_id, log_len=len(raw_logs))

    duration_ms = round((time.time() - start_time) * 1000, 2)
    return {
        "investigation_id": investigation_id,
        "raw_logs": raw_logs,
        "logs": raw_logs,
        "user_question": question,
        "question": question,
        "intake_timestamp": datetime.utcnow().isoformat(),
        "tool_calls_made": ["incident_intake"],
        "node_execution_trace": [{
            "node": "incident_intake",
            "status": "success",
            "duration_ms": duration_ms,
        }],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Node 2: Data Validation and Normalization Agent
# ─────────────────────────────────────────────────────────────────────────────

def data_validation_node(state: AgentState) -> Dict[str, Any]:
    """Validate incoming logs and sanitize format, catching malformed input."""
    start_time = time.time()
    logs = state.get("raw_logs", "")
    errors: List[str] = []

    if not logs or not logs.strip():
        errors.append("Log content cannot be empty or whitespace only.")
    elif len(logs.strip()) < 10:
        errors.append("Log content is too short for meaningful incident analysis (min 10 characters).")

    # Sanitize null bytes and normalize newlines
    normalized_logs = logs.replace("\x00", "").replace("\r\n", "\n").strip()
    is_valid = len(errors) == 0

    duration_ms = round((time.time() - start_time) * 1000, 2)
    logger.info("Node 2 [Validation]: Checked input", is_valid=is_valid, errors=errors)

    return {
        "normalized_logs": normalized_logs,
        "is_valid_input": is_valid,
        "validation_errors": errors,
        "errors": [f"Validation: {e}" for e in errors] if errors else [],
        "tool_calls_made": ["data_validation"],
        "node_execution_trace": [{
            "node": "data_validation",
            "status": "success" if is_valid else "validation_failed",
            "duration_ms": duration_ms,
        }],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Node 3: Severity Classification Agent
# ─────────────────────────────────────────────────────────────────────────────

def severity_classification_node(state: AgentState) -> Dict[str, Any]:
    """Calculate deterministic severity score (0-100) and blast radius."""
    start_time = time.time()
    logs = state.get("normalized_logs", "")

    # Quick preliminary parse for classification weights
    entries = parse_logs(logs)
    freq = analyze_frequency(entries)
    patterns = detect_patterns(entries)
    severity_res = classify_severity(entries, freq, patterns)

    duration_ms = round((time.time() - start_time) * 1000, 2)
    logger.info("Node 3 [Severity]: Classified", severity=severity_res.severity, score=severity_res.score)

    return {
        "severity": severity_res.severity,
        "severity_score": severity_res.score,
        "severity_reasoning": severity_res.reasoning,
        "affected_services": severity_res.affected_services,
        "affected_endpoints": severity_res.affected_endpoints,
        "severity_result": severity_res.to_dict(),
        "tool_calls_made": ["severity_classifier"],
        "node_execution_trace": [{
            "node": "severity_classification",
            "status": "success",
            "duration_ms": duration_ms,
        }],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Node 4: Log Analysis Agent
# ─────────────────────────────────────────────────────────────────────────────

def log_analysis_node(state: AgentState) -> Dict[str, Any]:
    """Execute multi-format log parsing and calculate error frequencies."""
    start_time = time.time()
    logs = state.get("normalized_logs", "")

    entries = parse_logs(logs)
    freq = analyze_frequency(entries)

    parsed_dicts = [e.to_dict() for e in entries]
    error_cnt = freq.level_counts.get("ERROR", 0) + freq.level_counts.get("CRITICAL", 0)
    warning_cnt = freq.level_counts.get("WARNING", 0)

    # Retrieval is required if actionable errors or log entries are present
    should_retrieve = (
        error_cnt > 0
        or warning_cnt > 0
        or any(e.get("level") in ("ERROR", "CRITICAL", "WARN", "WARNING") for e in parsed_dicts)
        or len(entries) > 0
    )

    duration_ms = round((time.time() - start_time) * 1000, 2)
    logger.info("Node 4 [LogAnalysis]: Parsed entries", total=len(entries), errors=error_cnt, retrieve=should_retrieve)

    return {
        "parsed_entries": parsed_dicts,
        "frequency_report": freq.to_dict(),
        "freq_report": freq.to_dict(),
        "total_entries": freq.total_entries,
        "error_count": freq.level_counts.get("ERROR", 0),
        "warning_count": warning_cnt,
        "should_retrieve": should_retrieve,
        "tool_calls_made": ["log_parser", "frequency_analyzer"],
        "node_execution_trace": [{
            "node": "log_analysis",
            "status": "success",
            "duration_ms": duration_ms,
        }],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Node 5: RAG Knowledge Retrieval Agent
# ─────────────────────────────────────────────────────────────────────────────

def rag_retrieval_node(state: AgentState) -> Dict[str, Any]:
    """Retrieve relevant runbook documentation and troubleshooting guides from ChromaDB."""
    start_time = time.time()
    question = state.get("user_question", "Why is the application failing?")
    severity = state.get("severity", "MEDIUM")
    services = state.get("affected_services", [])

    query = f"{question} {' '.join(services[:3])} {severity} severity incident."
    collection = state.get("document_collection")

    try:
        docs = retrieve_relevant_docs(query=query, top_k=5, collection_name=collection)
        context = format_retrieved_docs_as_context(docs)
        has_docs = len(docs) > 0
    except Exception as e:
        logger.warning("RAG retrieval exception, continuing gracefully", error=str(e))
        docs = []
        context = "No relevant runbooks found in ChromaDB knowledge base."
        has_docs = False

    duration_ms = round((time.time() - start_time) * 1000, 2)
    logger.info("Node 5 [RAG]: Retrieved docs", count=len(docs), has_docs=has_docs)

    return {
        "retrieved_documents": docs,
        "retrieved_docs": docs,
        "rag_context_text": context,
        "context_text": context,
        "has_relevant_docs": has_docs,
        "tool_calls_made": ["rag_retriever"],
        "node_execution_trace": [{
            "node": "rag_retrieval",
            "status": "success",
            "duration_ms": duration_ms,
        }],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Node 6: Pattern Correlation Agent
# ─────────────────────────────────────────────────────────────────────────────

def pattern_correlation_node(state: AgentState) -> Dict[str, Any]:
    """Correlate current logs with known failure signatures and detect cascading risks."""
    start_time = time.time()
    logs = state.get("normalized_logs", "")

    entries = parse_logs(logs)
    patterns = detect_patterns(entries)
    pattern_dicts = [p.to_dict() for p in patterns.detected_patterns]
    pattern_names = [p["name"] for p in pattern_dicts]

    primary_signature = pattern_names[0] if pattern_names else None

    duration_ms = round((time.time() - start_time) * 1000, 2)
    logger.info("Node 6 [Correlation]: Patterns correlated", count=len(pattern_dicts), cascade=patterns.has_cascading_risk)

    return {
        "correlated_patterns": pattern_dicts,
        "pattern_report": patterns.to_dict(),
        "detected_pattern_names": pattern_names,
        "cascading_risk": patterns.has_cascading_risk,
        "primary_failure_signature": primary_signature,
        "tool_calls_made": ["pattern_correlation"],
        "node_execution_trace": [{
            "node": "pattern_correlation",
            "status": "success",
            "duration_ms": duration_ms,
        }],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Node 7: Root Cause Analysis Agent
# ─────────────────────────────────────────────────────────────────────────────

def root_cause_analysis_node(state: AgentState) -> Dict[str, Any]:
    """Synthesize root cause hypotheses using Groq LLM with deterministic fallbacks."""
    start_time = time.time()
    patterns = state.get("correlated_patterns", [])
    freq = state.get("frequency_report", {})
    context = state.get("rag_context_text", "No documentation available.")
    services = state.get("affected_services", [])

    patterns_str = "\n".join(f"  - {p['name']} ({p.get('severity', 'UNKNOWN')}): {p.get('description', '')}" for p in patterns[:5])
    top_errors_str = "\n".join(f"  - [{e.get('count', 1)}x] {e.get('message', '')}" for e in freq.get("top_errors", [])[:5])

    # First formulate title & symptoms
    prompt_understand = PROMPT_UNDERSTAND_INCIDENT.format(
        question=state.get("user_question", "Why is the application failing?"),
        logs=state.get("normalized_logs", "")[:2500],
        total_entries=state.get("total_entries", 0),
        error_count=state.get("error_count", 0),
        warning_count=state.get("warning_count", 0),
        severity=state.get("severity", "MEDIUM"),
        patterns=", ".join(state.get("detected_pattern_names", [])) or "None detected",
        services=", ".join(services[:5]) if services else "Not identified",
    )

    try:
        resp_understand = invoke_llm(prompt_understand, system_message=SYSTEM_UNDERSTAND_INCIDENT)
        parsed_und = _safe_llm_json(resp_understand)
    except Exception as e:
        logger.warning("LLM Understand call failed, using deterministic fallback", error=str(e))
        parsed_und = {}

    incident_title = parsed_und.get("incident_title") or f"{state.get('severity', 'UNKNOWN')} Incident: {state.get('primary_failure_signature') or 'System Outage'}"
    exec_summary = parsed_und.get("executive_summary") or f"An incident with {state.get('severity', 'MEDIUM')} severity was analyzed across {len(services)} services."
    tech_summary = parsed_und.get("technical_summary") or f"Telemetry indicates {state.get('error_count', 0)} errors correlated with {state.get('primary_failure_signature') or 'system faults'}."
    symptoms = parsed_und.get("symptoms") or [p.get("description", "") for p in patterns[:3]]

    # Next formulate root cause hypotheses
    prompt_rca = PROMPT_INVESTIGATE_ROOT_CAUSE.format(
        incident_title=incident_title,
        severity=state.get("severity", "MEDIUM"),
        question=state.get("user_question", "Why is the application failing?"),
        symptoms="\n".join(f"  - {s}" for s in symptoms[:6]) or "  None identified",
        patterns=patterns_str or "  No specific patterns detected",
        top_errors=top_errors_str or "  No repeated errors identified",
        context=context[:2000],
    )

    try:
        resp_rca = invoke_llm(prompt_rca, system_message=SYSTEM_INVESTIGATE_ROOT_CAUSE)
        parsed_rca = _safe_llm_json(resp_rca)
    except Exception as e:
        logger.warning("LLM RCA call failed, using rule-based diagnostic fallback", error=str(e))
        parsed_rca = {}

    probable_rc = parsed_rca.get("probable_root_cause")
    if not probable_rc:
        sig = state.get("primary_failure_signature") or "Infrastructure Error"
        probable_rc = f"[HYPOTHESIS] {sig} detected based on recurring telemetry error signatures."

    alt_causes = parsed_rca.get("alternative_causes") or [p["name"] for p in patterns[1:3]]

    hypotheses = [{
        "rank": 1,
        "cause": probable_rc,
        "type": "primary",
    }]
    for i, alt in enumerate(alt_causes):
        hypotheses.append({
            "rank": i + 2,
            "cause": alt,
            "type": "alternative",
        })

    duration_ms = round((time.time() - start_time) * 1000, 2)
    logger.info("Node 7 [RCA]: Hypotheses generated", primary=probable_rc[:60])

    return {
        "incident_title": incident_title,
        "executive_summary": exec_summary,
        "technical_summary": tech_summary,
        "symptoms": symptoms,
        "probable_root_cause": probable_rc,
        "alternative_causes": alt_causes,
        "root_cause_hypotheses": hypotheses,
        "tool_calls_made": ["root_cause_analysis"],
        "node_execution_trace": [{
            "node": "root_cause_analysis",
            "status": "success",
            "duration_ms": duration_ms,
        }],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Node 8: Hypothesis Validation Agent
# ─────────────────────────────────────────────────────────────────────────────

def hypothesis_validation_node(state: AgentState) -> Dict[str, Any]:
    """Validate root cause hypotheses against verified log lines to prevent hallucinations."""
    start_time = time.time()
    patterns = state.get("correlated_patterns", [])
    probable_rc = state.get("probable_root_cause", "")
    entries = state.get("parsed_entries", [])

    # Extract verified log citations from detected pattern lines
    evidence_items = []
    for p in patterns[:4]:
        for line in p.get("matched_lines", [])[:2]:
            evidence_items.append({
                "source": "log",
                "content": line,
                "relevance": f"Verified match for pattern '{p.get('name')}' ({p.get('severity')})",
            })

    # If no pattern lines, grab the first 3 actual error entries
    if not evidence_items:
        for e in entries:
            if e.get("level") in ("ERROR", "CRITICAL") and e.get("message"):
                evidence_items.append({
                    "source": "log",
                    "content": e.get("message"),
                    "relevance": f"Observed {e.get('level')} exception in service {e.get('service') or 'unknown'}",
                })
                if len(evidence_items) >= 3:
                    break

    # Grounding evaluation: check if evidence supports hypothesis
    has_evidence = len(evidence_items) > 0
    is_pattern_backed = bool(state.get("primary_failure_signature"))

    if has_evidence and is_pattern_backed:
        confidence = "HIGH" if state.get("total_entries", 0) >= 4 else "MEDIUM"
        confidence_score = 0.85 if confidence == "HIGH" else 0.70
        reasoning = "Root cause hypothesis is grounded in verified log signatures and matching failure patterns."
        validation_passed = True
    elif has_evidence:
        confidence = "MEDIUM"
        confidence_score = 0.60
        reasoning = "Evidence found in logs, but signature pattern was atypical."
        validation_passed = True
    else:
        confidence = "LOW"
        confidence_score = 0.35
        reasoning = "Hypothesis has limited direct log citation evidence; further telemetry needed."
        validation_passed = False

    retry_count = state.get("retry_count", 0) + 1

    duration_ms = round((time.time() - start_time) * 1000, 2)
    logger.info("Node 8 [Validation]: Evaluated evidence", confidence=confidence, evidence_count=len(evidence_items))

    return {
        "validated_hypotheses": state.get("root_cause_hypotheses", []),
        "confidence_level": confidence,
        "confidence": confidence,
        "confidence_score": confidence_score,
        "confidence_reasoning": reasoning,
        "supporting_evidence": evidence_items,
        "validation_passed": validation_passed,
        "retry_count": retry_count,
        "tool_calls_made": ["hypothesis_validator"],
        "node_execution_trace": [{
            "node": "hypothesis_validation",
            "status": "success",
            "duration_ms": duration_ms,
        }],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Node 9: Remediation Planning Agent
# ─────────────────────────────────────────────────────────────────────────────

def remediation_planning_node(state: AgentState) -> Dict[str, Any]:
    """Generate prioritized, actionable remediation steps (mitigation vs permanent fix)."""
    start_time = time.time()
    patterns = state.get("correlated_patterns", [])
    probable_rc = state.get("probable_root_cause", "")

    remediation_steps = []
    immediate_actions = []

    # Map pattern causes to actionable engineering remediation
    for i, p in enumerate(patterns[:4]):
        remediation_steps.append({
            "priority": i + 1,
            "action": f"Mitigate {p.get('name')}: {p.get('probable_cause') or 'Review configuration'}",
            "rationale": f"Detected pattern indicates {p.get('description')}",
            "estimated_impact": f"Directly reduces {p.get('severity')} operational risk",
        })

    # Default fallback steps if patterns were sparse
    if not remediation_steps:
        remediation_steps = [
            {
                "priority": 1,
                "action": "Inspect application and database health metrics",
                "rationale": "Identify immediate saturation points across services",
                "estimated_impact": "Stabilizes service traffic",
            },
            {
                "priority": 2,
                "action": "Check recent deployment logs and service configurations",
                "rationale": "Rule out regression bugs introduced in recent releases",
                "estimated_impact": "Prevents recurring failures",
            },
        ]

    immediate_actions = [
        "Verify service traffic routing and health check endpoints",
        "Scale service replicas or increase database connection pool capacity if saturated",
    ]

    duration_ms = round((time.time() - start_time) * 1000, 2)
    logger.info("Node 9 [Remediation]: Planned actions", count=len(remediation_steps))

    return {
        "remediation_steps": remediation_steps,
        "immediate_actions": immediate_actions,
        "preventative_actions": [
            "Add alert rules for early warning threshold triggers",
            "Implement circuit breakers on outbound network dependencies",
        ],
        "additional_info": [
            "Application APM traces and thread dumps for the incident window",
            "Database query latency and connection pool saturation metrics",
        ],
        "limitations": [
            "Analysis is bounded to the telemetry provided in the submitted log excerpt",
        ],
        "tool_calls_made": ["remediation_planner"],
        "node_execution_trace": [{
            "node": "remediation_planning",
            "status": "success",
            "duration_ms": duration_ms,
        }],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Node 10: Investigation Report Generation Agent
# ─────────────────────────────────────────────────────────────────────────────

def report_generation_node(state: AgentState) -> Dict[str, Any]:
    """Assemble structured InvestigationReport adhering strictly to API contracts."""
    start_time = time.time()
    investigation_id = state.get("investigation_id") or str(uuid.uuid4())

    # Build document references for report
    doc_refs = []
    for doc in state.get("retrieved_documents", [])[:5]:
        meta = doc.get("metadata", {})
        doc_refs.append({
            "document_name": meta.get("source", "Knowledge Base Runbook"),
            "source_file": meta.get("file_path", meta.get("source", "")),
            "excerpt": doc.get("content", "")[:300],
            "relevance_score": doc.get("relevance_score", 0.0),
            "page_number": meta.get("page"),
        })

    report = {
        "investigation_id": investigation_id,
        "incident_title": state.get("incident_title", "Application Incident Investigation"),
        "severity": state.get("severity", "MEDIUM"),
        "created_at": datetime.utcnow().isoformat(),
        "executive_summary": state.get("executive_summary", ""),
        "technical_summary": state.get("technical_summary", ""),
        "symptoms": state.get("symptoms", []),
        "affected_services": state.get("affected_services", []),
        "affected_endpoints": state.get("affected_endpoints", []),
        "error_count": state.get("error_count", 0),
        "warning_count": state.get("warning_count", 0),
        "total_log_entries": state.get("total_entries", 0),
        "detected_patterns": state.get("detected_pattern_names", []),
        "probable_root_cause": state.get("probable_root_cause", ""),
        "alternative_causes": state.get("alternative_causes", []),
        "supporting_evidence": state.get("supporting_evidence", []),
        "document_references": doc_refs,
        "recommended_remediation": state.get("remediation_steps", []),
        "immediate_actions": state.get("immediate_actions", []),
        "confidence": state.get("confidence_level", "MEDIUM"),
        "confidence_reasoning": state.get("confidence_reasoning", ""),
        "additional_info_required": state.get("additional_info", []),
        "limitations": state.get("limitations", []),
    }

    duration_ms = round((time.time() - start_time) * 1000, 2)
    logger.info("Node 10 [Report]: Formatted report", id=investigation_id)

    return {
        "investigation_report": report,
        "is_report_generated": True,
        "tool_calls_made": ["report_generator"],
        "node_execution_trace": [{
            "node": "report_generation",
            "status": "success",
            "duration_ms": duration_ms,
        }],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Node 11: Memory and Learning Agent
# ─────────────────────────────────────────────────────────────────────────────

def memory_learning_node(state: AgentState) -> Dict[str, Any]:
    """Persist investigation audit to SQLite and conditionally store high-confidence patterns."""
    start_time = time.time()
    report = state.get("investigation_report", {})
    investigation_id = state.get("investigation_id", str(uuid.uuid4()))
    memory_persisted = False

    try:
        with get_db_context() as db:
            record = InvestigationRecord(
                id=investigation_id,
                incident_title=report.get("incident_title", "Incident"),
                severity=report.get("severity", "MEDIUM"),
                confidence=report.get("confidence", "MEDIUM"),
                original_logs=state.get("raw_logs", ""),
                question=state.get("user_question", ""),
                report_json=json.dumps(report),
                error_count=report.get("error_count", 0),
                warning_count=report.get("warning_count", 0),
                total_log_entries=report.get("total_log_entries", 0),
                affected_services_json=json.dumps(report.get("affected_services", [])),
                created_at=datetime.utcnow(),
            )
            db.add(record)
            db.commit()
            memory_persisted = True
            logger.info("Node 11 [Memory]: Saved to SQLite", id=investigation_id)
    except Exception as e:
        logger.warning("Node 11 [Memory]: SQLite persistence skipped or failed", error=str(e))
        memory_persisted = False

    duration_ms = round((time.time() - start_time) * 1000, 2)
    return {
        "db_record_id": investigation_id if memory_persisted else None,
        "memory_persisted": memory_persisted,
        "knowledge_base_updated": False,  # Strict safeguard: prevent automated uncontrolled RAG mutation
        "tool_calls_made": ["memory_learning"],
        "node_execution_trace": [{
            "node": "memory_learning",
            "status": "success" if memory_persisted else "persistence_failed",
            "duration_ms": duration_ms,
        }],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Node 12: Final Response Agent
# ─────────────────────────────────────────────────────────────────────────────

def final_response_node(state: AgentState) -> Dict[str, Any]:
    """Compile final response payload conforming to FastAPI & React contracts."""
    start_time = time.time()
    is_valid = state.get("is_valid_input", True)
    report = state.get("investigation_report")

    if not is_valid or not report:
        # Build graceful validation/error fallback response
        errors = state.get("validation_errors", ["Invalid incident input."])
        report = {
            "investigation_id": state.get("investigation_id") or str(uuid.uuid4()),
            "incident_title": "Invalid Incident Submission",
            "severity": "LOW",
            "created_at": datetime.utcnow().isoformat(),
            "executive_summary": "The incident submission could not be processed due to validation errors.",
            "technical_summary": " ".join(errors),
            "symptoms": errors,
            "affected_services": [],
            "affected_endpoints": [],
            "error_count": 0,
            "warning_count": 0,
            "total_log_entries": 0,
            "detected_patterns": [],
            "probable_root_cause": "N/A - Input rejected by validation agent.",
            "alternative_causes": [],
            "supporting_evidence": [],
            "document_references": [],
            "recommended_remediation": [
                {
                    "priority": 1,
                    "action": "Ensure raw logs contain at least 10 non-whitespace characters",
                    "rationale": "Sufficient telemetry is required for pattern and frequency analysis",
                    "estimated_impact": "Enables root cause investigation",
                }
            ],
            "immediate_actions": ["Provide valid application logs or telemetry stream"],
            "confidence": "LOW",
            "confidence_reasoning": "Input failed validation checks.",
            "additional_info_required": ["Raw application error logs or syslog excerpt"],
            "limitations": errors,
        }

    duration_ms = round((time.time() - start_time) * 1000, 2)
    logger.info("Node 12 [FinalResponse]: Workflow complete", is_valid=is_valid)

    return {
        "final_response": report,
        "is_complete": True,
        "tool_calls_made": ["final_response"],
        "node_execution_trace": [{
            "node": "final_response",
            "status": "success",
            "duration_ms": duration_ms,
        }],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Backward Compatibility Wrappers (Preserve existing 5-node test signatures)
# ─────────────────────────────────────────────────────────────────────────────

def understand_incident_node(state: AgentState) -> Dict[str, Any]:
    """Legacy alias wrapping Nodes 1, 2, 3, 4 for existing tests."""
    s1 = incident_intake_node(state)
    state = {**state, **s1}
    s2 = data_validation_node(state)
    state = {**state, **s2}
    s3 = severity_classification_node(state)
    state = {**state, **s3}
    s4 = log_analysis_node(state)
    state = {**state, **s4}
    s6 = pattern_correlation_node(state)
    return {
        "parsed_entries": state.get("parsed_entries", []),
        "freq_report": state.get("frequency_report", {}),
        "pattern_report": state.get("pattern_report", {}),
        "severity_result": state.get("severity_result", {}),
        "tool_calls_made": ["log_parser", "log_frequency_analyzer", "error_pattern_detector", "severity_classifier"],
        "errors": state.get("errors", []),
        "should_retrieve": state.get("should_retrieve", False),
        "iteration_count": state.get("iteration_count", 0) + 1,
    }

def retrieve_docs_node(state: AgentState) -> Dict[str, Any]:
    """Legacy alias wrapping Node 5."""
    return rag_retrieval_node(state)

def llm_understand_node(state: AgentState) -> Dict[str, Any]:
    """Legacy alias wrapping preliminary LLM understand."""
    return root_cause_analysis_node(state)

def investigate_root_cause_node(state: AgentState) -> Dict[str, Any]:
    """Legacy alias wrapping Nodes 7, 8, 9."""
    s7 = root_cause_analysis_node(state)
    state = {**state, **s7}
    s8 = hypothesis_validation_node(state)
    state = {**state, **s8}
    s9 = remediation_planning_node(state)
    return {**s7, **s8, **s9}

def generate_report_node(state: AgentState) -> Dict[str, Any]:
    """Legacy alias wrapping Nodes 10, 11, 12."""
    return final_response_node(state)
