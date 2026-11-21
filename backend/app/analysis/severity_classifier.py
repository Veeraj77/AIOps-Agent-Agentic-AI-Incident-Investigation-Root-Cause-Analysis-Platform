"""
AIOps Agent – Severity Classifier
====================================
Classifies the overall incident severity (CRITICAL/HIGH/MEDIUM/LOW)
based on a scoring model using log levels, patterns, error rates,
and service impact signals.

Why rule-based classification first?
- Fast and deterministic (runs before the LLM agent).
- Gives the agent a starting severity level to reason from.
- Avoids sending unnecessary LLM calls for low-severity events.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from app.ingestion.log_parser import LogEntry
from app.analysis.frequency_analyzer import FrequencyReport
from app.analysis.pattern_detector import PatternReport
from app.core.logging import get_logger

logger = get_logger(__name__)

# ── Severity Levels ───────────────────────────────────────────────────────────
SEVERITY_LEVELS = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]

# ── Scoring Weights ───────────────────────────────────────────────────────────
# Positive scores increase severity; each threshold maps to a label.
SCORING_THRESHOLDS = [
    (75, "CRITICAL"),
    (45, "HIGH"),
    (20, "MEDIUM"),
    (10, "LOW"),
    (0, "INFO"),
]


@dataclass
class SeverityResult:
    """
    Result of severity classification.

    Attributes:
        severity:       Overall incident severity label.
        score:          Raw numeric score (0–100+).
        confidence:     Classifier confidence (LOW/MEDIUM/HIGH).
        reasoning:      Human-readable explanation of the score.
        affected_services: Services extracted from logs.
        affected_endpoints: HTTP endpoints extracted from logs.
    """

    severity: str
    score: int
    confidence: str
    reasoning: List[str]
    affected_services: List[str]
    affected_endpoints: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity,
            "score": self.score,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "affected_services": self.affected_services,
            "affected_endpoints": self.affected_endpoints,
        }


def _score_level_counts(freq: FrequencyReport) -> tuple[int, List[str]]:
    """Score based on log level distribution."""
    score = 0
    reasons = []
    counts = freq.level_counts

    critical_count = counts.get("CRITICAL", 0)
    error_count = counts.get("ERROR", 0)
    warning_count = counts.get("WARNING", 0)

    if critical_count > 0:
        score += 35 + min((critical_count - 1) * 15, 30)
        reasons.append(f"{critical_count} CRITICAL log entries detected")

    if error_count > 0:
        score += min(error_count * 3, 25)
        reasons.append(f"{error_count} ERROR log entries detected")

    if warning_count > 0:
        score += min(warning_count * 1, 10)
        reasons.append(f"{warning_count} WARNING log entries detected")

    if freq.error_rate > 50:
        score += 20
        reasons.append(f"Error rate is very high: {freq.error_rate:.1f}%")
    elif freq.error_rate > 20:
        score += 10
        reasons.append(f"Error rate elevated: {freq.error_rate:.1f}%")

    return score, reasons


def _score_patterns(pattern_report: PatternReport) -> tuple[int, List[str]]:
    """Score based on detected patterns."""
    score = 0
    reasons = []

    severity_scores = {"CRITICAL": 25, "HIGH": 15, "MEDIUM": 8, "LOW": 3}

    for pattern in pattern_report.detected_patterns:
        pts = severity_scores.get(pattern.severity, 0)
        score += pts
        reasons.append(
            f"Pattern '{pattern.name}' detected ({pattern.match_count} occurrences)"
        )

    has_cascading_pattern = any(p.pattern_id == "CASCADING_FAILURE" for p in pattern_report.detected_patterns)
    if pattern_report.has_cascading_risk and not has_cascading_pattern:
        score += 10
        reasons.append("Cascading failure risk detected")

    return score, reasons


def _extract_affected_services(entries: List[LogEntry]) -> List[str]:
    """Collect all unique service names mentioned across log entries."""
    services = set()
    for entry in entries:
        if entry.service:
            services.add(entry.service)
        services.update(entry.mentioned_services)
    # Clean up: remove generic single-character entries
    return sorted(s for s in services if len(s) > 2)


def _extract_affected_endpoints(entries: List[LogEntry]) -> List[str]:
    """Collect all unique HTTP endpoints mentioned across log entries."""
    endpoints = set()
    for entry in entries:
        endpoints.update(entry.endpoints)
    return sorted(endpoints)


def classify_severity(
    entries: List[LogEntry],
    freq_report: FrequencyReport,
    pattern_report: PatternReport,
) -> SeverityResult:
    """
    Classify overall incident severity using a weighted scoring model.

    The score combines:
    - Log level counts (CRITICAL/ERROR/WARNING weights)
    - Error rate percentage
    - Known pattern severities
    - Cascading failure indicator

    Args:
        entries:        Parsed log entries.
        freq_report:    Output of frequency_analyzer.analyze_frequency().
        pattern_report: Output of pattern_detector.detect_patterns().

    Returns:
        SeverityResult with label, score, reasoning, and affected services.
    """
    total_score = 0
    all_reasons: List[str] = []

    # Component 1: Level counts
    level_score, level_reasons = _score_level_counts(freq_report)
    total_score += level_score
    all_reasons.extend(level_reasons)

    # Component 2: Pattern matches
    pattern_score, pattern_reasons = _score_patterns(pattern_report)
    total_score += pattern_score
    all_reasons.extend(pattern_reasons)

    # Determine severity label from score
    severity = "INFO"
    for threshold, label in SCORING_THRESHOLDS:
        if total_score >= threshold:
            severity = label
            break

    # Confidence based on number of signals
    signal_count = len(all_reasons)
    if signal_count >= 4:
        confidence = "HIGH"
    elif signal_count >= 2:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    affected_services = _extract_affected_services(entries)
    affected_endpoints = _extract_affected_endpoints(entries)

    if affected_services:
        all_reasons.append(f"Affected services: {', '.join(affected_services[:5])}")
    if affected_endpoints:
        all_reasons.append(f"Affected endpoints: {', '.join(affected_endpoints[:5])}")

    result = SeverityResult(
        severity=severity,
        score=total_score,
        confidence=confidence,
        reasoning=all_reasons,
        affected_services=affected_services,
        affected_endpoints=affected_endpoints,
    )

    logger.info(
        "Severity classification complete",
        severity=severity,
        score=total_score,
        confidence=confidence,
    )

    return result
