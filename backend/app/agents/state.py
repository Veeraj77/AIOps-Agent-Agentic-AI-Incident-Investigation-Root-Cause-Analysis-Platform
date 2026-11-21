"""
AIOps Agent – LangGraph Agent State
=====================================
Defines the shared state TypedDict that flows through all 12 agent nodes.

Why TypedDict for state?
- LangGraph requires state to be a TypedDict or similar mapping.
- Each node reads from and writes to this shared state.
- Annotated reducers allow list-based telemetry (tool calls, errors, trace)
  to accumulate across nodes without accidental overwrite.
"""

from typing import TypedDict, List, Optional, Dict, Any, Annotated
import operator


class AgentState(TypedDict, total=False):
    """
    Comprehensive state for the 12-node AIOps autonomous investigation agent.
    """

    # ── 1. Intake & Raw Input (Node 1) ────────────────────────────────────────
    investigation_id: str
    raw_logs: str
    logs: str                          # Backward-compatibility alias
    user_question: str
    question: str                      # Backward-compatibility alias
    document_collection: Optional[str]
    metadata: Dict[str, Any]
    intake_timestamp: str

    # ── 2. Validation & Normalization (Node 2) ───────────────────────────────
    normalized_logs: str
    is_valid_input: bool
    validation_errors: List[str]

    # ── 3. Severity Classification (Node 3) ──────────────────────────────────
    severity: str                      # CRITICAL, HIGH, MEDIUM, LOW, INFO
    severity_score: int                # 0 - 100
    severity_reasoning: str
    affected_services: List[str]
    affected_endpoints: List[str]
    severity_result: Dict[str, Any]    # Serialized dict for API compatibility

    # ── 4. Log Analysis & Telemetry (Node 4) ─────────────────────────────────
    parsed_entries: List[Dict[str, Any]]
    frequency_report: Dict[str, Any]
    freq_report: Dict[str, Any]        # Backward-compatibility alias
    total_entries: int
    error_count: int
    warning_count: int
    should_retrieve: bool

    # ── 5. RAG Retrieval (Node 5) ────────────────────────────────────────────
    retrieved_documents: List[Dict[str, Any]]
    retrieved_docs: List[Dict[str, Any]] # Backward-compatibility alias
    rag_context_text: str
    context_text: str                  # Backward-compatibility alias
    has_relevant_docs: bool

    # ── 6. Pattern Correlation (Node 6) ──────────────────────────────────────
    correlated_patterns: List[Dict[str, Any]]
    pattern_report: Dict[str, Any]     # Backward-compatibility alias
    detected_pattern_names: List[str]
    cascading_risk: bool
    primary_failure_signature: Optional[str]

    # ── 7. Root Cause Analysis (Node 7) ──────────────────────────────────────
    incident_title: str
    executive_summary: str
    technical_summary: str
    symptoms: List[str]
    probable_root_cause: str
    alternative_causes: List[str]
    root_cause_hypotheses: List[Dict[str, Any]]

    # ── 8. Hypothesis Validation (Node 8) ────────────────────────────────────
    validated_hypotheses: List[Dict[str, Any]]
    confidence_level: str              # HIGH, MEDIUM, LOW, UNKNOWN
    confidence: str                    # Backward-compatibility alias
    confidence_score: float            # 0.0 - 1.0
    confidence_reasoning: str
    supporting_evidence: List[Dict[str, Any]]
    validation_passed: bool
    retry_count: int

    # ── 9. Remediation Planning (Node 9) ─────────────────────────────────────
    remediation_steps: List[Dict[str, Any]]
    immediate_actions: List[str]
    preventative_actions: List[str]
    additional_info: List[str]
    limitations: List[str]

    # ── 10. Report Generation (Node 10) ──────────────────────────────────────
    investigation_report: Dict[str, Any]
    is_report_generated: bool

    # ── 11. Memory & Learning (Node 11) ──────────────────────────────────────
    db_record_id: Optional[str]
    memory_persisted: bool
    knowledge_base_updated: bool

    # ── 12. Final Response (Node 12) ─────────────────────────────────────────
    final_response: Dict[str, Any]
    is_complete: bool

    # ── Telemetry & Observability (Accumulators) ─────────────────────────────
    tool_calls_made: Annotated[List[str], operator.add]
    errors: Annotated[List[str], operator.add]
    node_execution_trace: Annotated[List[Dict[str, Any]], operator.add]
    total_duration_ms: float
