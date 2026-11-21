"""
AIOps Agent – API Route: Documents
=====================================
Handles knowledge base document upload and management.

POST /api/documents/upload
  - Accept PDF or TXT file.
  - Load, chunk, embed, and store in ChromaDB.
  - Record metadata in SQLite.

GET /api/documents
  - List all uploaded documents.
"""

import os
import uuid
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from app.ingestion.document_loader import load_document_from_bytes
from app.rag.chunking import chunk_documents
from app.rag.vector_store import add_chunks_to_store, get_collection_stats
from app.database.connection import get_db, DocumentRecord
from app.config import get_settings
from app.core.logging import get_logger
from app.core.exceptions import DocumentProcessingError

router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()


class DocumentUploadResponse(BaseModel):
    success: bool
    document_id: str
    filename: str
    file_type: str
    file_size_bytes: int
    chunk_count: int
    collection_name: str
    message: str


class DocumentSummary(BaseModel):
    document_id: str
    filename: str
    file_type: str
    file_size_bytes: int
    chunk_count: int
    collection_name: str
    is_embedded: bool
    created_at: str


class CollectionStatsResponse(BaseModel):
    collection_name: str
    document_count: int
    status: str


@router.post("/upload", response_model=DocumentUploadResponse, tags=["Documents"])
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DocumentUploadResponse:
    """
    Upload a PDF or TXT document to the knowledge base.

    The document is:
    1. Loaded and text extracted.
    2. Split into overlapping chunks (500 chars, 50 overlap).
    3. Embedded with Sentence Transformers (local, free).
    4. Stored in ChromaDB for semantic retrieval.
    5. Metadata recorded in SQLite.

    **Note:** First upload may take 30-60 seconds (embedding model download).
    """
    # Validate file type
    filename = file.filename or "unknown"
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in settings.allowed_doc_ext_list:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{ext}'. Allowed: {settings.allowed_doc_extensions}",
        )

    # Read content
    content = await file.read()

    # Validate file size
    if len(content) > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File size {len(content)} bytes exceeds limit of {settings.max_file_size_mb} MB",
        )

    if len(content) == 0:
        raise HTTPException(status_code=422, detail="Uploaded file is empty")

    document_id = str(uuid.uuid4())
    file_type = ext.lstrip(".")
    collection_name = settings.chroma_collection_name

    try:
        # Step 1: Load document
        logger.info("Loading document", filename=filename, size=len(content))
        documents = load_document_from_bytes(
            content=content,
            filename=filename,
            file_type=file_type,
        )

        # Step 2: Chunk
        chunks = chunk_documents(documents, chunk_size=500, chunk_overlap=50)

        # Add document_id to chunk metadata for filtering
        for chunk in chunks:
            chunk.metadata["document_id"] = document_id
            chunk.chunk_id = f"{document_id}_{chunk.chunk_id}"

        # Step 3 & 4: Embed and store in ChromaDB
        chunk_count = add_chunks_to_store(chunks, collection_name=collection_name)

        # Step 5: Persist metadata to SQLite
        record = DocumentRecord(
            id=document_id,
            filename=f"{document_id}_{filename}",
            original_name=filename,
            file_type=file_type,
            file_size_bytes=len(content),
            chunk_count=chunk_count,
            collection_name=collection_name,
            is_embedded=True,
        )
        db.add(record)
        db.commit()

        logger.info(
            "Document uploaded and embedded",
            id=document_id,
            filename=filename,
            chunks=chunk_count,
        )

        return DocumentUploadResponse(
            success=True,
            document_id=document_id,
            filename=filename,
            file_type=file_type,
            file_size_bytes=len(content),
            chunk_count=chunk_count,
            collection_name=collection_name,
            message=f"Successfully processed '{filename}' into {chunk_count} searchable chunks.",
        )

    except DocumentProcessingError as e:
        raise HTTPException(status_code=422, detail=e.message)
    except Exception as e:
        logger.error("Document upload failed", filename=filename, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


@router.get("", response_model=List[DocumentSummary], tags=["Documents"])
async def list_documents(db: Session = Depends(get_db)) -> List[DocumentSummary]:
    """List all uploaded knowledge base documents."""
    records = db.query(DocumentRecord).order_by(DocumentRecord.created_at.desc()).all()
    return [
        DocumentSummary(
            document_id=r.id,
            filename=r.original_name,
            file_type=r.file_type,
            file_size_bytes=r.file_size_bytes,
            chunk_count=r.chunk_count,
            collection_name=r.collection_name,
            is_embedded=r.is_embedded,
            created_at=r.created_at.isoformat(),
        )
        for r in records
    ]


@router.get("/stats", response_model=CollectionStatsResponse, tags=["Documents"])
async def get_stats() -> CollectionStatsResponse:
    """Return ChromaDB collection statistics."""
    stats = get_collection_stats()
    return CollectionStatsResponse(
        collection_name=stats.get("name", ""),
        document_count=stats.get("document_count", 0),
        status=stats.get("status", "unknown"),
    )
