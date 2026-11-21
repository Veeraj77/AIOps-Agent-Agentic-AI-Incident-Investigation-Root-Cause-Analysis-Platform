"""
AIOps Agent – API Route: Investigations
=========================================
Runs the full AI-powered investigation using the LangGraph agent.

POST /api/investigations/run
  - Triggers the full LangGraph agent workflow.
  - Returns a structured InvestigationReport.

GET /api/investigations
  - Lists all past investigations from SQLite.

GET /api/investigations/{investigation_id}
  - Returns the full report for a specific investigation.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.schemas.report import InvestigationRequest, InvestigationReport, InvestigationSummary
from app.services.investigation_service import (
    run_investigation,
    get_investigation_by_id,
    list_investigations,
)
from app.database.connection import get_db
from app.core.exceptions import InvestigationNotFoundError, LLMConfigurationError, LLMServiceError
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/run", response_model=InvestigationReport, tags=["Investigations"])
async def run_investigation_endpoint(
    request: InvestigationRequest,
    db: Session = Depends(get_db),
) -> InvestigationReport:
    """
    Run a full AI-powered incident investigation.

    This endpoint invokes the LangGraph agent which:
    1. Parses and analyses the logs.
    2. Detects error patterns.
    3. Retrieves relevant documentation (RAG).
    4. Uses the LLM to identify the root cause.
    5. Generates a structured investigation report.

    **Requires:** A valid GROQ_API_KEY in .env

    **Note:** First run may take 10-30 seconds (embedding model loads on first use).
    """
    try:
        logger.info(
            "Investigation request received",
            log_len=len(request.logs),
            question=request.question,
        )

        report = run_investigation(
            logs=request.logs,
            question=request.question,
            db=db,
            document_collection=request.document_collection,
        )
        return report

    except LLMConfigurationError as e:
        raise HTTPException(
            status_code=500,
            detail=f"LLM Configuration Error: {e.message}. "
                   "Please set GROQ_API_KEY in your .env file.",
        )
    except LLMServiceError as e:
        raise HTTPException(status_code=503, detail=f"LLM Service Error: {e.message}")
    except Exception as e:
        logger.error("Investigation failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Investigation failed: {str(e)}")


@router.get("", response_model=list[InvestigationSummary], tags=["Investigations"])
async def list_investigations_endpoint(
    limit: int = 50,
    db: Session = Depends(get_db),
) -> list[InvestigationSummary]:
    """
    List all past investigations (most recent first).

    Returns lightweight summaries – use GET /investigations/{id} for full details.
    """
    return list_investigations(db=db, limit=limit)


@router.get("/{investigation_id}", response_model=InvestigationReport, tags=["Investigations"])
async def get_investigation_endpoint(
    investigation_id: str,
    db: Session = Depends(get_db),
) -> InvestigationReport:
    """
    Retrieve the full report for a specific investigation.

    Args:
        investigation_id: UUID returned when the investigation was created.
    """
    try:
        return get_investigation_by_id(investigation_id=investigation_id, db=db)
    except InvestigationNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
