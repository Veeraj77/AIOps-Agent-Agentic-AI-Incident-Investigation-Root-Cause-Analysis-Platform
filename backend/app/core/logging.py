"""
AIOps Agent – Structured Logging Configuration
================================================
Uses structlog for structured, JSON-formatted logs.
JSON logs are easier to parse by monitoring tools like Datadog, Grafana Loki, etc.

Why structlog instead of print()?
- Logs include timestamps, severity levels, and context fields automatically.
- JSON output integrates with log aggregation platforms.
- Consistent format across all modules.
"""

import logging
import sys
import structlog
from app.config import get_settings


def configure_logging() -> None:
    """
    Set up structlog with the application's log level.
    Call once at application startup (in main.py).
    """
    settings = get_settings()
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Configure the standard Python logging system
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Configure structlog processors (what happens to each log record)
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,          # Add request-scoped context
            structlog.stdlib.add_log_level,                   # Add level field
            structlog.stdlib.add_logger_name,                 # Add logger name
            structlog.processors.TimeStamper(fmt="iso"),      # ISO 8601 timestamps
            structlog.processors.StackInfoRenderer(),         # Include stack info
            structlog.dev.ConsoleRenderer()                   # Human-readable console output
            if settings.debug
            else structlog.processors.JSONRenderer(),         # JSON in production
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a named structlog logger.

    Usage:
        logger = get_logger(__name__)
        logger.info("Processing logs", count=42, severity="ERROR")

    Args:
        name: Usually __name__ from the calling module.

    Returns:
        A bound structlog logger instance.
    """
    return structlog.get_logger(name)
