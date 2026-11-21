"""
AIOps Agent – Agent Tools
===========================
LangChain-compatible tools that the agent can invoke during investigation.

What are tools?
- Functions the LLM agent can CALL to get structured information.
- Each tool does a real operation (not fake) and returns structured JSON.
- The agent decides which tools to use based on the incident context.

Tools defined here:
1. log_frequency_analyzer    – Counts error occurrences.
2. error_pattern_detector    – Identifies known failure patterns.
3. severity_classifier       – Rates overall incident severity.
4. api_error_analyzer        – Analyses HTTP error patterns.
5. documentation_retriever   – Searches the knowledge base (RAG).
6. configuration_analyzer    – Looks for configuration-related errors.
"""

import json
from typing import Optional
from langchain_core.tools import tool
from app.ingestion.log_parser import parse_logs
from app.analysis.frequency_analyzer import analyze_frequency
from app.analysis.pattern_detector import detect_patterns
from app.analysis.severity_classifier import classify_severity
from app.rag.retriever import retrieve_relevant_docs
from app.core.logging import get_logger

logger = get_logger(__name__)


@tool
def log_frequency_analyzer(logs: str) -> str:
    """
    Analyse log entry frequencies by severity level.

    Counts how many ERROR, WARNING, INFO, CRITICAL entries exist.
    Identifies the most frequently occurring error messages.
    Returns a JSON summary of error rates and top errors.

    Use this tool when you need to understand the volume and distribution
    of log events, especially to identify dominant error patterns.

    Args:
        logs: Raw log text to analyse.

    Returns:
        JSON string with frequency statistics.
    """
    try:
        entries = parse_logs(logs)
        freq = analyze_frequency(entries)
        result = freq.to_dict()
        logger.info("Tool: log_frequency_analyzer executed", entries=len(entries))
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "tool": "log_frequency_analyzer"})


@tool
def error_pattern_detector(logs: str) -> str:
    """
    Detect known incident patterns in log data.

    Identifies patterns such as:
    - Database connection pool exhaustion
    - API timeout / slow response
    - HTTP 5xx server errors
    - Memory pressure / OOM
    - Authentication failures
    - Cascading service failures

    Use this tool when you need to understand what TYPE of failure
    is occurring based on recognised anti-patterns.

    Args:
        logs: Raw log text to analyse.

    Returns:
        JSON string listing detected patterns with severity and evidence.
    """
    try:
        entries = parse_logs(logs)
        pattern_report = detect_patterns(entries)
        result = pattern_report.to_dict()
        logger.info(
            "Tool: error_pattern_detector executed",
            patterns_found=result["total_patterns_found"],
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "tool": "error_pattern_detector"})


@tool
def severity_classifier(logs: str) -> str:
    """
    Classify the overall severity of the incident (CRITICAL/HIGH/MEDIUM/LOW).

    Uses a weighted scoring model based on:
    - Number and type of errors
    - Error rate percentage
    - Known dangerous patterns (cascading failures, OOM, etc.)
    - Affected services

    Use this tool to establish the urgency of the incident before
    investigating the root cause.

    Args:
        logs: Raw log text to classify.

    Returns:
        JSON string with severity label, score, and reasoning.
    """
    try:
        entries = parse_logs(logs)
        freq = analyze_frequency(entries)
        patterns = detect_patterns(entries)
        sev = classify_severity(entries, freq, patterns)
        result = sev.to_dict()
        logger.info(
            "Tool: severity_classifier executed",
            severity=result["severity"],
            score=result["score"],
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "tool": "severity_classifier"})


@tool
def api_error_analyzer(logs: str) -> str:
    """
    Specifically analyse HTTP API errors in the logs.

    Extracts:
    - HTTP status codes (4xx, 5xx)
    - Affected API endpoints
    - Response time violations
    - Error distribution across endpoints

    Use this tool when you see HTTP errors or API-related failures
    in the logs and need to understand which endpoints are affected.

    Args:
        logs: Raw log text to analyse.

    Returns:
        JSON string with API error breakdown.
    """
    import re

    http_pattern = re.compile(
        r"(?:HTTP\s+)?(?P<status>[45]\d{2})\s*[-–]?\s*(?P<endpoint>/[\w/\-\.\{\}]*)?",
        re.IGNORECASE,
    )
    timeout_pattern = re.compile(r"response\s*time\s*(?:exceeded)?\s*(\d+)\s*ms", re.IGNORECASE)

    status_counts: dict = {}
    endpoint_errors: dict = {}
    timeouts = []

    for line in logs.splitlines():
        # HTTP status codes
        for m in http_pattern.finditer(line):
            status = m.group("status")
            endpoint = m.group("endpoint") or "unknown"
            status_counts[status] = status_counts.get(status, 0) + 1
            if endpoint != "unknown":
                endpoint_errors[endpoint] = endpoint_errors.get(endpoint, 0) + 1

        # Timeout values
        for m in timeout_pattern.finditer(line):
            try:
                timeouts.append(int(m.group(1)))
            except ValueError:
                pass

    result = {
        "http_status_distribution": status_counts,
        "affected_endpoints": endpoint_errors,
        "timeout_values_ms": timeouts,
        "max_response_time_ms": max(timeouts) if timeouts else None,
        "avg_response_time_ms": round(sum(timeouts) / len(timeouts)) if timeouts else None,
        "has_5xx_errors": any(s.startswith("5") for s in status_counts),
        "has_4xx_errors": any(s.startswith("4") for s in status_counts),
    }

    logger.info(
        "Tool: api_error_analyzer executed",
        status_codes=len(status_counts),
        endpoints=len(endpoint_errors),
    )
    return json.dumps(result, indent=2)


@tool
def documentation_retriever(query: str, top_k: int = 5) -> str:
    """
    Search the knowledge base for documentation relevant to the incident.

    Uses semantic similarity search (RAG) over uploaded technical documents.
    Returns the most relevant passages with source citations.

    Use this tool when you need to find:
    - Known solutions to similar errors
    - Configuration documentation
    - Runbooks and incident playbooks
    - Architecture documentation

    Args:
        query: A description of the incident or specific question.
        top_k: Maximum number of documents to retrieve (default: 5).

    Returns:
        JSON string with retrieved document passages and metadata.
    """
    try:
        docs = retrieve_relevant_docs(query=query, top_k=top_k)
        result = {
            "query": query,
            "results_found": len(docs),
            "documents": [
                {
                    "content": d["content"],
                    "source": d.get("metadata", {}).get("source", "unknown"),
                    "page": d.get("metadata", {}).get("page"),
                    "relevance_score": d.get("relevance_score", 0),
                }
                for d in docs
            ],
        }
        logger.info(
            "Tool: documentation_retriever executed",
            query_len=len(query),
            docs_found=len(docs),
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "tool": "documentation_retriever", "results_found": 0})


@tool
def configuration_analyzer(logs: str) -> str:
    """
    Identify configuration-related errors and misconfigurations in logs.

    Looks for signals such as:
    - Missing environment variables
    - Invalid configuration values
    - Port binding failures
    - File permission issues
    - Dependency version mismatches

    Use this tool when logs suggest the application may be misconfigured.

    Args:
        logs: Raw log text to analyse.

    Returns:
        JSON string with detected configuration issues.
    """
    import re

    config_patterns = {
        "missing_env_var": re.compile(
            r"(?:environment variable|env var)\s+['\"]?(\w+)['\"]?\s+(?:is\s+)?(?:not\s+set|missing|undefined)",
            re.IGNORECASE,
        ),
        "port_conflict": re.compile(r"(?:address already in use|port\s+\d+.*in use|bind.*failed)", re.IGNORECASE),
        "file_permission": re.compile(r"(?:permission denied|access denied|cannot read|cannot write)", re.IGNORECASE),
        "invalid_config": re.compile(
            r"(?:invalid\s+(?:configuration|config|value|parameter)|configuration\s+error|misconfigured)",
            re.IGNORECASE,
        ),
        "dependency_missing": re.compile(
            r"(?:module not found|cannot import|importerror|no module named|dependency.*missing)",
            re.IGNORECASE,
        ),
        "ssl_tls_error": re.compile(r"(?:ssl|tls|certificate).*(?:error|invalid|expired|failed)", re.IGNORECASE),
    }

    findings: dict = {}
    for issue_type, pattern in config_patterns.items():
        matched_lines = []
        for line in logs.splitlines():
            if pattern.search(line):
                matched_lines.append(line.strip())
        if matched_lines:
            findings[issue_type] = {
                "count": len(matched_lines),
                "examples": matched_lines[:3],
            }

    result = {
        "configuration_issues_found": len(findings),
        "has_config_problems": len(findings) > 0,
        "issues": findings,
    }

    logger.info(
        "Tool: configuration_analyzer executed",
        issues_found=len(findings),
    )
    return json.dumps(result, indent=2)


# ── Tool Registry ─────────────────────────────────────────────────────────────
# All tools available to the agent (import this list in graph.py)
ALL_TOOLS = [
    log_frequency_analyzer,
    error_pattern_detector,
    severity_classifier,
    api_error_analyzer,
    documentation_retriever,
    configuration_analyzer,
]
