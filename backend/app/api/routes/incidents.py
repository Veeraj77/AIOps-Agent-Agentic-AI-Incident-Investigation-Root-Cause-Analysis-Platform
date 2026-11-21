"""
AIOps Agent – API Route: Incidents
=====================================
Handles log submission and structural analysis (without LLM).

POST /api/incidents/analyze
  - Parse logs
  - Run frequency analysis
  - Detect patterns
  - Classify severity
  - Return structured analysis

This endpoint is fast and deterministic (no LLM calls).
Use /api/investigations/run for full AI-powered root cause analysis.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from app.schemas.incident import IncidentAnalysisRequest, IncidentAnalysisResponse, TopError, DetectedPatternSchema
from app.ingestion.log_parser import parse_logs
from app.analysis.frequency_analyzer import analyze_frequency
from app.analysis.pattern_detector import detect_patterns
from app.analysis.severity_classifier import classify_severity
from app.core.exceptions import LogParsingError, FileTooLargeError, UnsupportedFileTypeError
from app.config import get_settings
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()


def _build_summary(severity: str, error_count: int, pattern_count: int) -> str:
    """Generate a one-line incident summary from analysis results."""
    if error_count == 0:
        return "No errors detected. System appears healthy."
    return (
        f"{severity} incident detected: {error_count} error(s) found "
        f"across {pattern_count} known incident pattern(s)."
    )


@router.post("/analyze", response_model=IncidentAnalysisResponse, tags=["Incidents"])
async def analyze_incident(request: IncidentAnalysisRequest) -> IncidentAnalysisResponse:
    """
    Analyse raw log text and return a structured incident report.

    This endpoint does NOT call the LLM – it uses deterministic rule-based analysis.
    For AI-powered root cause investigation, use POST /api/investigations/run.

    **Steps:**
    1. Parse log lines into structured entries.
    2. Count frequencies per log level.
    3. Detect known incident patterns.
    4. Classify overall severity.
    5. Return structured JSON response.
    """
    try:
        logger.info("Starting log analysis", log_length=len(request.logs))

        # Step 1: Parse
        entries = parse_logs(request.logs)

        # Step 2: Frequency analysis
        freq_report = analyze_frequency(entries)

        # Step 3: Pattern detection
        pattern_report = detect_patterns(entries)

        # Step 4: Severity classification
        severity_result = classify_severity(entries, freq_report, pattern_report)

        # Step 5: Build response
        return IncidentAnalysisResponse(
            success=True,
            total_log_entries=freq_report.total_entries,
            level_counts=freq_report.level_counts,
            error_rate_percent=freq_report.error_rate,
            unique_error_count=freq_report.unique_error_count,
            top_errors=[TopError(**e) for e in freq_report.top_errors],
            top_warnings=[TopError(**w) for w in freq_report.top_warnings],
            detected_patterns=[
                DetectedPatternSchema(**p.to_dict())
                for p in pattern_report.detected_patterns
            ],
            overall_severity=severity_result.severity,
            severity_score=severity_result.score,
            severity_confidence=severity_result.confidence,
            severity_reasoning=severity_result.reasoning,
            affected_services=severity_result.affected_services,
            affected_endpoints=severity_result.affected_endpoints,
            summary=_build_summary(
                severity_result.severity,
                freq_report.level_counts.get("ERROR", 0),
                pattern_report.total_patterns_found,
            ),
        )

    except LogParsingError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error("Unexpected error during log analysis", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal analysis error: {str(e)}")


@router.post("/analyze/upload", response_model=IncidentAnalysisResponse, tags=["Incidents"])
async def analyze_incident_file(
    file: UploadFile = File(...),
) -> IncidentAnalysisResponse:
    """
    Upload a .log or .txt file and analyse it.

    Accepts: text/plain, .log, .txt files up to 50 MB.
    """
    # Validate file type
    ext = "." + (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in settings.allowed_log_ext_list:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{ext}'. Allowed: {settings.allowed_log_extensions}",
        )

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {settings.max_file_size_mb} MB limit",
        )

    try:
        log_text = content.decode("utf-8", errors="replace")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not decode file: {str(e)}")

    # Delegate to the same analysis logic
    return await analyze_incident(IncidentAnalysisRequest(logs=log_text))
