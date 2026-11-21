"""
AIOps Agent – Text Chunking
=============================
Splits large documents into smaller overlapping chunks
suitable for embedding and semantic search.

Why chunk documents?
- LLMs have context length limits (can't process 100-page PDFs at once).
- Embedding models work best on short, focused passages (~200-500 words).
- Smaller chunks give more precise retrieval results.

Why overlapping chunks?
- Prevents important context from being split at chunk boundaries.
- A sentence at the end of chunk N also appears at the start of chunk N+1.
"""

from typing import List
from dataclasses import dataclass, field
from app.ingestion.document_loader import Document
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class TextChunk:
    """
    A single chunk of text ready for embedding.

    Attributes:
        content:    The chunk text.
        metadata:   Source document metadata + chunk position info.
        chunk_id:   Unique identifier (source_filename_chunkN).
    """

    content: str
    metadata: dict = field(default_factory=dict)
    chunk_id: str = ""

    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "metadata": self.metadata,
        }


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    separator: str = "\n",
) -> List[str]:
    """
    Split text into overlapping chunks by character count.

    Strategy:
    1. Split by separator (newline by default) to respect natural boundaries.
    2. Accumulate lines until chunk_size is reached.
    3. When a chunk is full, emit it and start a new chunk from the overlap point.

    Args:
        text:         Input text to split.
        chunk_size:   Target character count per chunk (not a hard limit).
        chunk_overlap: Number of characters of overlap between chunks.
        separator:    Line separator character.

    Returns:
        List of chunk strings.
    """
    if not text or not text.strip():
        return []

    lines = text.split(separator)
    chunks: List[str] = []
    current_chunk: List[str] = []
    current_len = 0

    for line in lines:
        line_len = len(line)

        # If adding this line would exceed chunk_size, emit the current chunk
        if current_len + line_len > chunk_size and current_chunk:
            chunk_text_str = separator.join(current_chunk)
            if chunk_text_str.strip():
                chunks.append(chunk_text_str)

            # Overlap: keep the last N characters worth of lines
            overlap_lines: List[str] = []
            overlap_len = 0
            for prev_line in reversed(current_chunk):
                if overlap_len + len(prev_line) > chunk_overlap:
                    break
                overlap_lines.insert(0, prev_line)
                overlap_len += len(prev_line)

            current_chunk = overlap_lines
            current_len = overlap_len

        current_chunk.append(line)
        current_len += line_len

    # Emit the final chunk
    if current_chunk:
        final_chunk = separator.join(current_chunk)
        if final_chunk.strip():
            chunks.append(final_chunk)

    return chunks


def chunk_documents(
    documents: List[Document],
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[TextChunk]:
    """
    Chunk a list of Document objects into TextChunks ready for embedding.

    Args:
        documents:     Documents loaded by document_loader.
        chunk_size:    Characters per chunk.
        chunk_overlap: Overlap between consecutive chunks.

    Returns:
        List of TextChunk objects with IDs and metadata.
    """
    all_chunks: List[TextChunk] = []

    for doc in documents:
        raw_chunks = chunk_text(
            doc.content,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", 1)

        for idx, chunk_content in enumerate(raw_chunks):
            chunk_id = f"{source}_p{page}_c{idx}"
            all_chunks.append(
                TextChunk(
                    content=chunk_content,
                    metadata={
                        **doc.metadata,
                        "chunk_index": idx,
                        "chunk_id": chunk_id,
                        "char_count": len(chunk_content),
                    },
                    chunk_id=chunk_id,
                )
            )

    logger.info(
        "Document chunking complete",
        input_documents=len(documents),
        output_chunks=len(all_chunks),
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    return all_chunks
