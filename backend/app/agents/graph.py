"""
AIOps Agent – 12-Node Modular LangGraph Investigation Workflow
==============================================================
Assembles the upgraded agent workflow using LangGraph's StateGraph.

Architecture:
  Node 1:  incident_intake          – Normalizes incident input and tracing ID
  Node 2:  data_validation          – Validates log length, encoding, and format
             ├── [invalid] ─────────────────────────────────────────────────────┐
             └── [valid]                                                        │
  Node 3:  severity_classification  – Computes blast radius & 0-100 severity   │
  Node 4:  log_analysis             – Regex log parser & frequency stats        │
             ├── [should_retrieve] ─> Node 5: rag_retrieval ─> Node 6          │
             └── [clean_logs] ───────────────────────────────> Node 6          │
  Node 6:  pattern_correlation      – Correlates failure signatures & cascades  │
  Node 7:  root_cause_analysis <──┐ – Synthesizes hypotheses via Groq LLM      │
  Node 8:  hypothesis_validation  │ – Verifies claims against log citations    │
             ├── [retry_hypothesis] ┘ (bounded to max 1 iteration)              │
             └── [validated]                                                    │
  Node 9:  remediation_planning     – Formulates prioritized P1/P2/P3 actions  │
  Node 10: report_generation        – Assembles Pydantic InvestigationReport   │
  Node 11: memory_learning          – Persists audit to SQLite                  │
  Node 12: final_response <─────────────────────────────────────────────────────┘
             ↓
            END
"""

from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
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
from app.core.logging import get_logger

logger = get_logger(__name__)


# ── Conditional Routing Functions ─────────────────────────────────────────────

def _route_validation(state: AgentState) -> str:
    """Decide whether to proceed to severity analysis or abort early if input is invalid."""
    if state.get("is_valid_input", True):
        return "severity_classification"
    return "final_response"


def _route_retrieval(state: AgentState) -> str:
    """Decide whether to execute RAG retrieval (if actionable errors/warnings exist)."""
    if state.get("should_retrieve", True):
        return "rag_retrieval"
    return "pattern_correlation"


def _route_validation_retry(state: AgentState) -> str:
    """Decide whether hypotheses need revision or can proceed to remediation planning."""
    # Bounded to at most 1 retry loop to respect latency and token budgets
    if state.get("validation_passed", True) or state.get("retry_count", 0) >= 2:
        return "remediation_planning"
    return "root_cause_analysis"


# ── StateGraph Construction ───────────────────────────────────────────────────

def build_investigation_graph() -> StateGraph:
    """
    Build and compile the 12-node LangGraph investigation workflow.
    """
    graph = StateGraph(AgentState)

    # 1. Register all 12 nodes
    graph.add_node("incident_intake", incident_intake_node)
    graph.add_node("data_validation", data_validation_node)
    graph.add_node("severity_classification", severity_classification_node)
    graph.add_node("log_analysis", log_analysis_node)
    graph.add_node("rag_retrieval", rag_retrieval_node)
    graph.add_node("pattern_correlation", pattern_correlation_node)
    graph.add_node("root_cause_analysis", root_cause_analysis_node)
    graph.add_node("hypothesis_validation", hypothesis_validation_node)
    graph.add_node("remediation_planning", remediation_planning_node)
    graph.add_node("report_generation", report_generation_node)
    graph.add_node("memory_learning", memory_learning_node)
    graph.add_node("final_response", final_response_node)

    # 2. Set entry point
    graph.set_entry_point("incident_intake")

    # 3. Connect nodes & conditional edges
    graph.add_edge("incident_intake", "data_validation")

    graph.add_conditional_edges(
        "data_validation",
        _route_validation,
        {
            "severity_classification": "severity_classification",
            "final_response": "final_response",
        },
    )

    graph.add_edge("severity_classification", "log_analysis")

    graph.add_conditional_edges(
        "log_analysis",
        _route_retrieval,
        {
            "rag_retrieval": "rag_retrieval",
            "pattern_correlation": "pattern_correlation",
        },
    )

    graph.add_edge("rag_retrieval", "pattern_correlation")
    graph.add_edge("pattern_correlation", "root_cause_analysis")
    graph.add_edge("root_cause_analysis", "hypothesis_validation")

    graph.add_conditional_edges(
        "hypothesis_validation",
        _route_validation_retry,
        {
            "remediation_planning": "remediation_planning",
            "root_cause_analysis": "root_cause_analysis",
        },
    )

    graph.add_edge("remediation_planning", "report_generation")
    graph.add_edge("report_generation", "memory_learning")
    graph.add_edge("memory_learning", "final_response")
    graph.add_edge("final_response", END)

    # 4. Compile workflow
    compiled = graph.compile()
    logger.info("Upgraded 12-node LangGraph investigation graph compiled successfully")
    return compiled


# Module-level compiled graph singleton
_compiled_graph = None


def get_investigation_graph():
    """Retrieve compiled investigation graph instance."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_investigation_graph()
    return _compiled_graph
