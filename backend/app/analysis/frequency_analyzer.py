"""
AIOps Agent – Error Frequency Analyzer
========================================
Counts how many times each unique error/warning appears.
Identifies the most critical recurring issues.

Why frequency analysis?
- Repeated errors signal systemic problems, not one-off glitches.
- High-frequency errors should be investigated first.
- Gives the LLM agent concrete numbers to reason about.
"""

from collections import Counter
from typing import Dict, List, Any
from app.ingestion.log_parser import LogEntry
from app.core.logging import get_logger

logger = get_logger(__name__)


class FrequencyReport:
    """
    Result of frequency analysis on a set of log entries.

    Attributes:
        level_counts:       {level: count} for all log levels.
        top_errors:         The N most frequent ERROR messages.
        top_warnings:       The N most frequent WARNING messages.
        error_rate:         Percentage of entries that are errors.
        total_entries:      Total number of parsed log lines.
        unique_error_count: Number of distinct error messages.
    """

    def __init__(
        self,
        level_counts: Dict[str, int],
        top_errors: List[Dict[str, Any]],
        top_warnings: List[Dict[str, Any]],
        total_entries: int,
        unique_error_count: int,
    ):
        self.level_counts = level_counts
        self.top_errors = top_errors
        self.top_warnings = top_warnings
        self.total_entries = total_entries
        self.unique_error_count = unique_error_count

    @property
    def error_rate(self) -> float:
        """Fraction of all entries that are ERROR or CRITICAL."""
        error_total = self.level_counts.get("ERROR", 0) + self.level_counts.get("CRITICAL", 0)
        if self.total_entries == 0:
            return 0.0
        return round(error_total / self.total_entries * 100, 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_entries": self.total_entries,
            "level_counts": self.level_counts,
            "error_rate_percent": self.error_rate,
            "unique_error_count": self.unique_error_count,
            "top_errors": self.top_errors,
            "top_warnings": self.top_warnings,
        }


def analyze_frequency(entries: List[LogEntry], top_n: int = 10) -> FrequencyReport:
    """
    Count log entry frequencies by level and message.

    Args:
        entries: Parsed log entries from log_parser.parse_logs().
        top_n:   How many of the top errors/warnings to return.

    Returns:
        FrequencyReport with counts, rates, and ranked error lists.
    """
    if not entries:
        return FrequencyReport(
            level_counts={},
            top_errors=[],
            top_warnings=[],
            total_entries=0,
            unique_error_count=0,
        )

    # Count entries by level
    level_counts: Counter = Counter(e.level for e in entries)

    # Count ERROR and CRITICAL messages by exact text
    error_messages: Counter = Counter(
        e.message for e in entries if e.level in ("ERROR", "CRITICAL")
    )

    # Count WARNING messages
    warning_messages: Counter = Counter(
        e.message for e in entries if e.level == "WARNING"
    )

    # Build ranked lists with count and percentage
    def build_ranked(counter: Counter, total: int) -> List[Dict[str, Any]]:
        ranked = []
        for msg, count in counter.most_common(top_n):
            ranked.append(
                {
                    "message": msg,
                    "count": count,
                    "percentage": round(count / total * 100, 2) if total > 0 else 0,
                }
            )
        return ranked

    total = len(entries)
    report = FrequencyReport(
        level_counts=dict(level_counts),
        top_errors=build_ranked(error_messages, total),
        top_warnings=build_ranked(warning_messages, total),
        total_entries=total,
        unique_error_count=len(error_messages),
    )

    logger.info(
        "Frequency analysis complete",
        total=total,
        error_rate=report.error_rate,
        unique_errors=report.unique_error_count,
    )

    return report
