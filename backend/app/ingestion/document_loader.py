"""
AIOps Agent – Document Loader
================================
Loads PDF and TXT files, extracts their text content,
and prepares it for chunking and embedding.

Why support multiple formats?
- TXT: Simple runbooks, READMEs, error guides.
- PDF: Official documentation, architecture docs, incident post-mortems.

How it works:
1. Detect file type by extension.
2. Use pypdf for PDFs, plain read for TXT.
3. Return a list of Document objects (text + metadata).
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional
from app.core.logging import get_logger
from app.core.exceptions import DocumentProcessingError

logger = get_logger(__name__)


@dataclass
class Document:
    """
    Represents a loaded document page or section.

    Attributes:
        content:   Extracted text content.
        metadata:  Source file info (name, page number, type).
    """

    content: str
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"content": self.content, "metadata": self.metadata}


def load_txt_file(file_path: str) -> List[Document]:
    """
    Load a plain text file and return as a single Document.

    Args:
        file_path: Absolute path to the .txt or .md file.

    Returns:
        List with one Document containing the full file text.
    """
    filename = os.path.basename(file_path)
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        if not content.strip():
            raise DocumentProcessingError(f"File '{filename}' is empty")

        logger.info("Loaded TXT document", filename=filename, chars=len(content))
        return [
            Document(
                content=content,
                metadata={
                    "source": filename,
                    "file_type": "txt",
                    "file_path": file_path,
                    "page": 1,
                },
            )
        ]
    except DocumentProcessingError:
        raise
    except Exception as e:
        raise DocumentProcessingError(f"Failed to read '{filename}': {str(e)}")


def load_pdf_file(file_path: str) -> List[Document]:
    """
    Load a PDF file and return one Document per page.

    Uses pypdf for text extraction.

    Args:
        file_path: Absolute path to the .pdf file.

    Returns:
        List of Documents, one per page, with page number in metadata.
    """
    filename = os.path.basename(file_path)
    try:
        from pypdf import PdfReader

        reader = PdfReader(file_path)
        documents = []

        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                documents.append(
                    Document(
                        content=text,
                        metadata={
                            "source": filename,
                            "file_type": "pdf",
                            "file_path": file_path,
                            "page": page_num,
                            "total_pages": len(reader.pages),
                        },
                    )
                )

        if not documents:
            raise DocumentProcessingError(
                f"No readable text found in '{filename}'. "
                "The PDF may be scanned (image-based) or encrypted."
            )

        logger.info(
            "Loaded PDF document",
            filename=filename,
            pages_with_text=len(documents),
            total_pages=len(reader.pages),
        )
        return documents

    except DocumentProcessingError:
        raise
    except ImportError:
        raise DocumentProcessingError(
            "pypdf is not installed. Run: pip install pypdf"
        )
    except Exception as e:
        raise DocumentProcessingError(f"Failed to read PDF '{filename}': {str(e)}")


def load_document(file_path: str) -> List[Document]:
    """
    Auto-detect file type and load accordingly.

    Args:
        file_path: Path to a .pdf, .txt, or .md file.

    Returns:
        List of Document objects.

    Raises:
        DocumentProcessingError: If the file type is unsupported or loading fails.
    """
    if not os.path.exists(file_path):
        raise DocumentProcessingError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[-1].lower()

    if ext == ".pdf":
        return load_pdf_file(file_path)
    elif ext in (".txt", ".md", ".log"):
        return load_txt_file(file_path)
    else:
        raise DocumentProcessingError(
            f"Unsupported file type '{ext}'. Supported: .pdf, .txt, .md, .log"
        )


def load_document_from_bytes(
    content: bytes,
    filename: str,
    file_type: str,
) -> List[Document]:
    """
    Load a document from raw bytes (e.g., from a FastAPI UploadFile).

    Saves the bytes to a temp location, loads it, then cleans up.

    Args:
        content:   Raw file bytes.
        filename:  Original filename (used for metadata).
        file_type: 'pdf' or 'txt'.

    Returns:
        List of Document objects.
    """
    import tempfile

    suffix = f".{file_type}"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        docs = load_document(tmp_path)
        # Update metadata with the original filename
        for doc in docs:
            doc.metadata["source"] = filename
        return docs
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
