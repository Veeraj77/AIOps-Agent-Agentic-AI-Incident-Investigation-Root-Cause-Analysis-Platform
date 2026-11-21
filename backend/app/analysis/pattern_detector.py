"""
AIOps Agent – Error Pattern Detector
=======================================
Identifies recurring error patterns in log entries.
Groups similar errors and detects known anti-patterns
(e.g., connection exhaustion, cascading failures, auth loops).

Why pattern detection?
- Raw error counts show *what* is failing, patterns show *how* it's failing.
- Cascading failures (A causes B causes C) need to be recognised as one incident.
- Known patterns map directly to known root causes.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Any
from app.ingestion.log_parser import LogEntry
from app.core.logging import get_logger

logger = get_logger(__name__)

# ── Known Incident Patterns ───────────────────────────────────────────────────
# Each pattern has a name, description, regex keywords, and suggested cause.
KNOWN_PATTERNS = [
    {
        "id": "DB_CONNECTION_EXHAUSTION",
        "name": "Database Connection Pool Exhausted",
        "keywords": [
            r"connection\s*pool\s*exhausted",
            r"connection\s*timeout",
            r"too\s*many\s*connections",
            r"max\s*connections\s*reached",
            r"unable\s*to\s*acquire\s*connection",
            r"database.*timeout",
            r"db.*timeout",
        ],
        "description": "Database connection pool has been exhausted. Requests cannot acquire a database connection.",
        "probable_cause": "Connection pool size too small, connections not released, or database overloaded.",
        "severity": "HIGH",
    },
    {
        "id": "API_SLOW_RESPONSE",
        "name": "API Slow Response / Timeout",
        "keywords": [
            r"response\s*time\s*exceeded",
            r"request\s*timeout",
            r"api.*timeout",
            r"gateway\s*timeout",
            r"504",
            r"response.*\d{4,}ms",
        ],
        "description": "API endpoints are responding slower than acceptable thresholds.",
        "probable_cause": "Downstream service slow, database bottleneck, or insufficient compute resources.",
        "severity": "MEDIUM",
    },
    {
        "id": "HTTP_5XX_ERRORS",
        "name": "HTTP 5xx Server Errors",
        "keywords": [
            r"http\s*5\d{2}",
            r"500\s*internal\s*server",
            r"502\s*bad\s*gateway",
            r"503\s*service\s*unavailable",
            r"status\s*code\s*5\d{2}",
        ],
        "description": "Server-side HTTP errors indicate the application is failing to handle requests.",
        "probable_cause": "Application crash, unhandled exception, or upstream dependency failure.",
        "severity": "HIGH",
    },
    {
        "id": "MEMORY_PRESSURE",
        "name": "Memory Pressure / Out of Memory",
        "keywords": [
            r"out\s*of\s*memory",
            r"memory\s*exhausted",
            r"java\.lang\.outofmemoryerror",
            r"memory\s*leak",
            r"heap\s*space",
            r"gc\s*overhead\s*limit",
        ],
        "description": "Application or JVM is running out of heap memory.",
        "probable_cause": "Memory leak, insufficient heap allocation, or unexpected traffic spike.",
        "severity": "CRITICAL",
    },
    {
        "id": "AUTH_FAILURE",
        "name": "Authentication / Authorisation Failures",
        "keywords": [
            r"authentication\s*failed",
            r"unauthori[sz]ed",
            r"401",
            r"403\s*forbidden",
            r"invalid\s*token",
            r"jwt.*invalid",
            r"access\s*denied",
        ],
        "description": "Authentication or authorisation failures are occurring.",
        "probable_cause": "Expired credentials, misconfigured auth service, or token rotation issue.",
        "severity": "MEDIUM",
    },
    {
        "id": "DISK_IO_ERROR",
        "name": "Disk / File System Errors",
        "keywords": [
            r"disk\s*full",
            r"no\s*space\s*left",
            r"i/o\s*error",
            r"file\s*not\s*found",
            r"permission\s*denied.*file",
            r"read\s*only\s*file\s*system",
        ],
        "description": "Disk or file system errors are preventing normal operation.",
        "probable_cause": "Disk full, file permission misconfiguration, or storage device failure.",
        "severity": "HIGH",
    },
    {
        "id": "NETWORK_CONNECTIVITY",
        "name": "Network Connectivity Issues",
        "keywords": [
            r"connection\s*refused",
            r"network\s*unreachable",
            r"host\s*not\s*found",
            r"name\s*resolution\s*failed",
            r"dns.*fail",
            r"socket.*timeout",
        ],
        "description": "Network connectivity failures between services.",
        "probable_cause": "Service down, network partition, DNS issue, or firewall change.",
        "severity": "HIGH",
    },
    {
        "id": "CASCADING_FAILURE",
        "name": "Cascading Service Failure",
        "keywords": [
            r"service\s*unavailable",
            r"upstream\s*fail",
            r"dependency.*fail",
            r"circuit\s*breaker\s*open",
            r"fallback\s*triggered",
        ],
        "description": "A failure in one service is propagating to dependent services.",
        "probable_cause": "Missing circuit breaker, insufficient timeout or retry configuration.",
        "severity": "CRITICAL",
    },
]


@dataclass
class DetectedPattern:
    """A known pattern that was detected in the log entries."""

    pattern_id: str
    name: str
    description: str
    probable_cause: str
    severity: str
    matched_lines: List[str] = field(default_factory=list)
    match_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "name": self.name,
            "description": self.description,
            "probable_cause": self.probable_cause,
            "severity": self.severity,
            "match_count": self.match_count,
            "matched_lines": self.matched_lines[:5],  # Include up to 5 examples
        }


@dataclass
class PatternReport:
    """Result of pattern detection analysis."""

    detected_patterns: List[DetectedPattern]
    total_patterns_found: int
    has_cascading_risk: bool
    highest_severity: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_patterns_found": self.total_patterns_found,
            "has_cascading_risk": self.has_cascading_risk,
            "highest_severity": self.highest_severity,
            "detected_patterns": [p.to_dict() for p in self.detected_patterns],
        }


def _severity_rank(severity: str) -> int:
    """Convert severity string to sortable integer."""
    return {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(severity.upper(), 0)


def detect_patterns(entries: List[LogEntry]) -> PatternReport:
    """
    Scan log entries for known incident patterns.

    Args:
        entries: Parsed log entries.

    Returns:
        PatternReport listing every matched known pattern with evidence.
    """
    if not entries:
        return PatternReport(
            detected_patterns=[],
            total_patterns_found=0,
            has_cascading_risk=False,
            highest_severity="NONE",
        )

    # Compile all keyword regexes once
    compiled_patterns = []
    for pattern in KNOWN_PATTERNS:
        regexes = [re.compile(kw, re.IGNORECASE) for kw in pattern["keywords"]]
        compiled_patterns.append((pattern, regexes))

    detected: List[DetectedPattern] = []

    for pattern_def, regexes in compiled_patterns:
        matched_lines = []
        for entry in entries:
            # Only check ERROR/WARNING/CRITICAL lines for efficiency
            if entry.level not in ("ERROR", "WARNING", "CRITICAL", "INFO"):
                continue
            text_to_check = f"{entry.service} {entry.message}".lower() if entry.service else entry.message.lower()
            if any(rx.search(text_to_check) for rx in regexes):
                matched_lines.append(entry.raw_line)

        if matched_lines:
            detected.append(
                DetectedPattern(
                    pattern_id=pattern_def["id"],
                    name=pattern_def["name"],
                    description=pattern_def["description"],
                    probable_cause=pattern_def["probable_cause"],
                    severity=pattern_def["severity"],
                    matched_lines=matched_lines,
                    match_count=len(matched_lines),
                )
            )

    # Sort by severity (most critical first)
    detected.sort(key=lambda p: _severity_rank(p.severity), reverse=True)

    highest = detected[0].severity if detected else "NONE"
    has_cascading = any(p.pattern_id == "CASCADING_FAILURE" for p in detected)

    logger.info(
        "Pattern detection complete",
        patterns_found=len(detected),
        highest_severity=highest,
        cascading_risk=has_cascading,
    )

    return PatternReport(
        detected_patterns=detected,
        total_patterns_found=len(detected),
        has_cascading_risk=has_cascading,
        highest_severity=highest,
    )
