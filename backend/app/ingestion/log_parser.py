"""
AIOps Agent – Log Parser
=========================
Parses raw log text into structured LogEntry objects.

Supports formats:
  - Standard syslog-style: 2024-01-15 10:30:45 ERROR DatabaseService - Connection timeout
  - Bracket-style:        [2024-01-15 10:30:45] [ERROR] Connection timeout
  - Level-first:          ERROR: Database connection timeout
  - Plain text:           Any text treated as INFO

Why regex-based parsing?
- Logs have no universal format; regex handles multiple styles.
- Much faster than LLM-based parsing for structured extraction.
- Provides deterministic, testable results.
"""

import re
from datetime import datetime
from typing import List, Optional
from app.core.logging import get_logger
from app.core.exceptions import LogParsingError

logger = get_logger(__name__)

# ── Log Level Constants ──────────────────────────────────────────────────────
LOG_LEVELS = {
    "CRITICAL": 50,
    "FATAL": 50,
    "ERROR": 40,
    "WARNING": 30,
    "WARN": 30,
    "INFO": 20,
    "DEBUG": 10,
    "TRACE": 5,
}

# ── Regex Patterns (ordered from most specific to least specific) ────────────
# Pattern 1: 2024-01-15 10:30:45,123 ERROR ServiceName - Message
_P1 = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}[,\.\d]*)"
    r"\s+(?P<level>CRITICAL|FATAL|ERROR|WARNING|WARN|INFO|DEBUG|TRACE)"
    r"(?:\s+(?P<service>\w[\w\.\-]*))?[\s\-:]+(?P<message>.+)",
    re.IGNORECASE,
)

# Pattern 2: [2024-01-15 10:30:45] [ERROR] [ServiceName] Message
_P2 = re.compile(
    r"\[(?P<timestamp>[^\]]+)\]\s*\[(?P<level>CRITICAL|FATAL|ERROR|WARNING|WARN|INFO|DEBUG|TRACE)\]"
    r"(?:\s*\[(?P<service>[^\]]+)\])?\s*(?P<message>.+)",
    re.IGNORECASE,
)

# Pattern 3: ERROR: Message  or  ERROR - Message  or  [ERROR] Message
_P3 = re.compile(
    r"(?:\[)?(?P<level>CRITICAL|FATAL|ERROR|WARNING|WARN|INFO|DEBUG|TRACE)(?:\])?"
    r"[\s:\-]+(?P<message>.+)",
    re.IGNORECASE,
)

# ── Service / Endpoint Extraction ────────────────────────────────────────────
_HTTP_ENDPOINT = re.compile(
    r"(?:GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+(/[\w/\-\.\{\}]+)"
    r"|(/api/[\w/\-\.\{\}]+)"
    r"|(HTTP\s+\d{3}.*?(/[\w/\-\.\{\}]+))",
    re.IGNORECASE,
)
_SERVICE_KEYWORDS = re.compile(
    r"\b(database|db|redis|kafka|rabbitmq|elasticsearch|postgres|mysql|mongodb"
    r"|api|service|server|client|worker|scheduler|gateway|proxy|cache|queue"
    r"|auth|payment|order|user|product|notification|email|storage|s3)\b",
    re.IGNORECASE,
)
_EXCEPTION_PATTERN = re.compile(
    r"([\w\.]+(?:Exception|Error|Timeout|Refused|Failed|Exhausted))",
    re.IGNORECASE,
)


class LogEntry:
    """
    Represents a single parsed log line.

    Attributes:
        raw_line:   Original log line exactly as provided.
        level:      Normalised log level (ERROR, WARNING, INFO, DEBUG).
        message:    The human-readable log message.
        timestamp:  Parsed datetime if found in the line.
        service:    Extracted service/component name if detectable.
        endpoints:  HTTP endpoints mentioned in the message.
        exceptions: Exception class names mentioned in the message.
        line_number: Position in the original log block.
    """

    def __init__(
        self,
        raw_line: str,
        level: str,
        message: str,
        timestamp: Optional[datetime] = None,
        service: Optional[str] = None,
        line_number: int = 0,
    ):
        self.raw_line = raw_line
        self.level = level.upper()
        self.message = message.strip()
        self.timestamp = timestamp
        self.service = service
        self.line_number = line_number

        # Extract additional context from the message text
        self.endpoints: List[str] = self._extract_endpoints()
        self.exceptions: List[str] = self._extract_exceptions()
        self.mentioned_services: List[str] = self._extract_service_mentions()

    def _extract_endpoints(self) -> List[str]:
        """Find HTTP endpoint paths mentioned in the log message."""
        endpoints = []
        for match in _HTTP_ENDPOINT.finditer(self.message):
            path = next((g for g in match.groups() if g), None)
            if path and path.startswith("/"):
                endpoints.append(path)
        return list(set(endpoints))

    def _extract_exceptions(self) -> List[str]:
        """Find exception/error class names like NullPointerException."""
        return list(set(_EXCEPTION_PATTERN.findall(self.message)))

    def _extract_service_mentions(self) -> List[str]:
        """Find common service/component keywords in the message."""
        return list(set(m.lower() for m in _SERVICE_KEYWORDS.findall(self.message)))

    @property
    def severity_weight(self) -> int:
        """Numeric weight for sorting/comparison. Higher = more severe."""
        return LOG_LEVELS.get(self.level, 0)

    def to_dict(self) -> dict:
        """Serialise to a plain dictionary (JSON-safe)."""
        return {
            "line_number": self.line_number,
            "level": self.level,
            "message": self.message,
            "service": self.service,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "endpoints": self.endpoints,
            "exceptions": self.exceptions,
            "mentioned_services": self.mentioned_services,
            "raw_line": self.raw_line,
        }


def _parse_timestamp(ts_str: str) -> Optional[datetime]:
    """Try multiple timestamp formats; return None if none match."""
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S,%f",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%SZ",
    ]
    ts_clean = ts_str.strip().rstrip("Z")
    for fmt in formats:
        try:
            return datetime.strptime(ts_clean, fmt)
        except ValueError:
            continue
    return None


def parse_log_line(line: str, line_number: int = 0) -> Optional[LogEntry]:
    """
    Parse a single log line into a LogEntry.

    Returns None if the line is empty or a pure separator/comment.
    """
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or set(stripped) <= set("-=*_ "):
        return None

    # Try each pattern in order of specificity
    for pattern in (_P1, _P2, _P3):
        m = pattern.match(stripped)
        if m:
            groups = m.groupdict()
            level = groups.get("level", "INFO").upper()
            # Normalise WARN → WARNING, FATAL → CRITICAL
            level = "WARNING" if level == "WARN" else level
            level = "CRITICAL" if level == "FATAL" else level

            timestamp = None
            if groups.get("timestamp"):
                timestamp = _parse_timestamp(groups["timestamp"])

            return LogEntry(
                raw_line=stripped,
                level=level,
                message=groups.get("message", stripped),
                timestamp=timestamp,
                service=groups.get("service"),
                line_number=line_number,
            )

    # Fallback: treat the whole line as an INFO message
    return LogEntry(
        raw_line=stripped,
        level="INFO",
        message=stripped,
        line_number=line_number,
    )


def parse_logs(raw_text: str) -> List[LogEntry]:
    """
    Parse a multi-line log block into a list of LogEntry objects.

    Args:
        raw_text: Raw log content as a string (from file upload or manual input).

    Returns:
        List of LogEntry objects, one per meaningful log line.

    Raises:
        LogParsingError: If the input is empty or contains no parseable content.
    """
    if not raw_text or not raw_text.strip():
        raise LogParsingError("Log input is empty. Please provide log content.")

    lines = raw_text.splitlines()
    entries: List[LogEntry] = []

    for idx, line in enumerate(lines, start=1):
        entry = parse_log_line(line, line_number=idx)
        if entry:
            entries.append(entry)

    if not entries:
        raise LogParsingError(
            "No parseable log entries found. "
            "Ensure the input contains at least one log line."
        )

    logger.info(
        "Log parsing complete",
        total_lines=len(lines),
        parsed_entries=len(entries),
        error_count=sum(1 for e in entries if e.level == "ERROR"),
        warning_count=sum(1 for e in entries if e.level == "WARNING"),
    )

    return entries
