"""
AIOps Agent – 12-Node Agentic Architecture Test Suite
=====================================================
Validates each of the 12 LangGraph nodes independently and tests the
complete integrated StateGraph execution pipeline.
"""

import pytest
from app.agents.nodes import (
    incident_intake_node,
    data_validation_node,
    severity_classification_node,
    log_analysis_node,
    rag_retrieval_node,
    pattern_correlation_node,
    root_cause_analysis_node,
    hypothesis_validation_node,
    remediation_planning_node,
    report_generation_node,
    memory_learning_node,
    final_response_node,
)
from app.agents.graph import get_investigation_graph


SAMPLE_LOGS = """
2026-11-20T10:00:00Z ERROR [orders-api] Database connection timeout: 100/100 connections active. Timeout after 30000ms.
2026-11-20T10:00:01Z CRITICAL [orders-api] Unhandled Exception: Failed to acquire connection from pool [HikariPool-1]
2026-11-20T10:00:02Z ERROR [gateway] HTTP 500 Internal Server Error returned for POST /api/v1/orders
"""


def test_node1_incident_intake():
    """Verify Node 1 normalizes input and creates investigation UUID."""
    state = {"logs": SAMPLE_LOGS, "question": "Why is the API down?"}
    out = incident_intake_node(state)
    assert "investigation_id" in out
    assert out["raw_logs"] == SAMPLE_LOGS
    assert out["user_question"] == "Why is the API down?"
    assert "incident_intake" in out["tool_calls_made"]
    assert len(out["node_execution_trace"]) == 1


def test_node2_data_validation_success():
    """Verify Node 2 validates clean telemetry input."""
    state = {"raw_logs": SAMPLE_LOGS}
    out = data_validation_node(state)
    assert out["is_valid_input"] is True
    assert len(out["validation_errors"]) == 0
    assert len(out["normalized_logs"]) > 0


def test_node2_data_validation_rejection():
    """Verify Node 2 rejects empty or whitespace-only input."""
    state = {"raw_logs": "   \n  \t "}
    out = data_validation_node(state)
    assert out["is_valid_input"] is False
    assert len(out["validation_errors"]) > 0


def test_node3_severity_classification():
    """Verify Node 3 computes deterministic severity and blast radius."""
    state = {"normalized_logs": SAMPLE_LOGS}
    out = severity_classification_node(state)
    assert out["severity"] in ("CRITICAL", "HIGH", "MEDIUM", "LOW")
    assert 0 <= out["severity_score"] <= 100
    assert "severity_reasoning" in out
    assert "severity_classifier" in out["tool_calls_made"]


def test_node4_log_analysis():
    """Verify Node 4 parses entries and calculates frequency stats."""
    state = {"normalized_logs": SAMPLE_LOGS}
    out = log_analysis_node(state)
    assert len(out["parsed_entries"]) >= 2
    assert out["total_entries"] >= 2
    assert out["should_retrieve"] is True


def test_node5_rag_retrieval_graceful():
    """Verify Node 5 queries ChromaDB gracefully even when empty."""
    state = {
        "user_question": "Database pool issues",
        "severity": "HIGH",
        "affected_services": ["orders-api"],
    }
    out = rag_retrieval_node(state)
    assert "retrieved_documents" in out
    assert "rag_context_text" in out
    assert isinstance(out["has_relevant_docs"], bool)


def test_node6_pattern_correlation():
    """Verify Node 6 identifies known failure signatures."""
    state = {"normalized_logs": SAMPLE_LOGS}
    out = pattern_correlation_node(state)
    assert len(out["correlated_patterns"]) > 0
    assert any("Database" in p["name"] for p in out["correlated_patterns"])
    assert "pattern_correlation" in out["tool_calls_made"]


def test_node7_root_cause_analysis():
    """Verify Node 7 formulates incident title, summaries, and hypotheses."""
    state = {
        "user_question": "Why did orders fail?",
        "normalized_logs": SAMPLE_LOGS,
        "severity": "HIGH",
        "primary_failure_signature": "Database Connection Pool Exhausted",
        "correlated_patterns": [{"name": "Database Connection Pool Exhausted", "description": "Pool full"}],
        "frequency_report": {"top_errors": [{"count": 2, "message": "timeout"}]},
    }
    out = root_cause_analysis_node(state)
    assert "incident_title" in out
    assert "probable_root_cause" in out
    assert len(out["root_cause_hypotheses"]) >= 1


def test_node8_hypothesis_validation():
    """Verify Node 8 validates hypotheses against observed log lines."""
    state = {
        "probable_root_cause": "[HYPOTHESIS] DB Pool Exhaustion",
        "primary_failure_signature": "Database Connection Pool Exhausted",
        "correlated_patterns": [{
            "name": "Database Connection Pool Exhausted",
            "severity": "HIGH",
            "matched_lines": ["Database connection timeout: 100/100 connections active."],
        }],
        "total_entries": 4,
    }
    out = hypothesis_validation_node(state)
    assert out["validation_passed"] is True
    assert out["confidence_level"] in ("HIGH", "MEDIUM")
    assert len(out["supporting_evidence"]) > 0


def test_node9_remediation_planning():
    """Verify Node 9 formulates prioritized remediation steps."""
    state = {
        "probable_root_cause": "DB Pool Exhaustion",
        "correlated_patterns": [{
            "name": "Database Connection Pool Exhausted",
            "probable_cause": "Pool size too small",
            "description": "Connections exhausted",
            "severity": "HIGH",
        }],
    }
    out = remediation_planning_node(state)
    assert len(out["remediation_steps"]) >= 1
    assert out["remediation_steps"][0]["priority"] == 1
    assert len(out["immediate_actions"]) >= 1


def test_node10_report_generation():
    """Verify Node 10 assembles structured report conforming to schema."""
    state = {
        "investigation_id": "test-uuid-1234",
        "incident_title": "Database Outage",
        "severity": "HIGH",
        "executive_summary": "Orders failed due to database timeout.",
        "technical_summary": "100/100 connections active.",
        "symptoms": ["Timeout"],
        "probable_root_cause": "Pool Exhaustion",
        "remediation_steps": [{"priority": 1, "action": "Increase pool", "rationale": "More capacity", "estimated_impact": "Stabilizes API"}],
        "immediate_actions": ["Restart pool"],
        "confidence_level": "HIGH",
    }
    out = report_generation_node(state)
    assert out["is_report_generated"] is True
    report = out["investigation_report"]
    assert report["investigation_id"] == "test-uuid-1234"
    assert report["severity"] == "HIGH"


def test_node11_memory_learning():
    """Verify Node 11 safely manages SQLite persistence."""
    state = {
        "investigation_id": "test-memory-uuid",
        "raw_logs": SAMPLE_LOGS,
        "investigation_report": {
            "incident_title": "Memory Test Incident",
            "severity": "MEDIUM",
            "confidence": "MEDIUM",
        },
    }
    out = memory_learning_node(state)
    assert "memory_persisted" in out
    assert out["knowledge_base_updated"] is False  # Safeguard check


def test_node12_final_response():
    """Verify Node 12 delivers the final schema payload with completion flag."""
    state = {
        "is_valid_input": True,
        "investigation_report": {
            "investigation_id": "final-uuid-999",
            "incident_title": "Resolved Incident",
            "severity": "LOW",
        },
    }
    out = final_response_node(state)
    assert out["is_complete"] is True
    assert out["final_response"]["investigation_id"] == "final-uuid-999"


def test_full_12_node_graph_execution():
    """Verify full end-to-end execution through the compiled 12-node StateGraph."""
    graph = get_investigation_graph()
    initial_state = {
        "raw_logs": SAMPLE_LOGS,
        "user_question": "What caused the database failure?",
    }
    result = graph.invoke(initial_state)
    assert result.get("is_complete") is True
    assert result.get("investigation_id") is not None
    assert result.get("severity") in ("CRITICAL", "HIGH", "MEDIUM", "LOW")
    trace_nodes = [t["node"] for t in result.get("node_execution_trace", [])]
    assert "incident_intake" in trace_nodes
    assert "data_validation" in trace_nodes
    assert "severity_classification" in trace_nodes
    assert "final_response" in trace_nodes
