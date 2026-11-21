"""
AIOps Agent – Custom Exception Classes
========================================
Defines application-specific exceptions with HTTP status codes.

Why custom exceptions?
- Makes error handling consistent across all API routes.
- Allows FastAPI's exception handlers to return proper HTTP responses.
- Separates business logic errors from unexpected system errors.
"""

from typing import Optional


class AIOpsBaseException(Exception):
    """Base class for all AIOps application exceptions."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class LogParsingError(AIOpsBaseException):
    """Raised when log parsing fails (e.g., completely empty or corrupt input)."""

    def __init__(self, message: str = "Failed to parse the provided logs"):
        super().__init__(message, status_code=422)


class DocumentProcessingError(AIOpsBaseException):
    """Raised when a document cannot be loaded or processed."""

    def __init__(self, message: str = "Failed to process the uploaded document"):
        super().__init__(message, status_code=422)


class VectorStoreError(AIOpsBaseException):
    """Raised when ChromaDB operations fail."""

    def __init__(self, message: str = "Vector store operation failed"):
        super().__init__(message, status_code=500)


class LLMServiceError(AIOpsBaseException):
    """Raised when the LLM API call fails (network, quota, auth)."""

    def __init__(self, message: str = "LLM service is unavailable"):
        super().__init__(message, status_code=503)


class LLMConfigurationError(AIOpsBaseException):
    """Raised when LLM credentials are missing or invalid."""

    def __init__(self, message: str = "LLM is not properly configured"):
        super().__init__(message, status_code=500)


class InvestigationNotFoundError(AIOpsBaseException):
    """Raised when a requested investigation ID does not exist in the database."""

    def __init__(self, investigation_id: str):
        super().__init__(
            f"Investigation '{investigation_id}' not found",
            status_code=404,
        )


class FileTooLargeError(AIOpsBaseException):
    """Raised when an uploaded file exceeds the size limit."""

    def __init__(self, max_size_mb: int = 50):
        super().__init__(
            f"File exceeds the maximum allowed size of {max_size_mb} MB",
            status_code=413,
        )


class UnsupportedFileTypeError(AIOpsBaseException):
    """Raised when an uploaded file has a disallowed extension."""

    def __init__(self, extension: str, allowed: Optional[list] = None):
        allowed_str = ", ".join(allowed) if allowed else "unknown"
        super().__init__(
            f"File type '{extension}' is not supported. Allowed: {allowed_str}",
            status_code=415,
        )
