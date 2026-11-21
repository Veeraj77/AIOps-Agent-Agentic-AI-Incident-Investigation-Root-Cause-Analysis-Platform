"""
AIOps Agent – Document Retriever
==================================
High-level interface for retrieving relevant knowledge base documents
given an incident description or question.

This is the RAG (Retrieval-Augmented Generation) retriever layer.

RAG Flow:
  User question
      ↓
  embed_query()          ← Sentence Transformers (local)
      ↓
  search_similar()       ← ChromaDB cosine similarity search
      ↓
  Filter by threshold    ← Only return relevant results
      ↓
  Format as context      ← Passed to LLM for grounded answers
"""

from typing import List, Dict, Any, Optional
from app.rag.vector_store import search_similar
from app.core.logging import get_logger

logger = get_logger(__name__)

# Minimum relevance score to include a result (0.0 = random, 1.0 = identical)
DEFAULT_RELEVANCE_THRESHOLD = 0.30


def retrieve_relevant_docs(
    query: str,
    top_k: int = 5,
    collection_name: Optional[str] = None,
    relevance_threshold: float = DEFAULT_RELEVANCE_THRESHOLD,
) -> List[Dict[str, Any]]:
    """
    Retrieve the most relevant document chunks for a query.

    Args:
        query:               The user's question or incident description.
        top_k:               Maximum number of results.
        collection_name:     ChromaDB collection to search.
        relevance_threshold: Minimum relevance score (0–1) to include.

    Returns:
        List of dicts: {'content', 'metadata', 'relevance_score', 'distance'}
        Only returns chunks above the relevance threshold.
    """
    if not query or not query.strip():
        logger.warning("Empty query passed to retriever")
        return []

    results = search_similar(
        query=query,
        top_k=top_k,
        collection_name=collection_name,
    )

    # Filter by minimum relevance
    filtered = [r for r in results if r["relevance_score"] >= relevance_threshold]

    logger.info(
        "Document retrieval complete",
        query_len=len(query),
        raw_results=len(results),
        filtered_results=len(filtered),
        threshold=relevance_threshold,
    )

    return filtered


def format_retrieved_docs_as_context(docs: List[Dict[str, Any]]) -> str:
    """
    Format retrieved documents into a readable context string
    that can be injected into an LLM prompt.

    Args:
        docs: Output of retrieve_relevant_docs().

    Returns:
        Formatted string with source citations.
    """
    if not docs:
        return "No relevant documentation found in the knowledge base."

    sections = []
    for idx, doc in enumerate(docs, start=1):
        source = doc.get("metadata", {}).get("source", "Unknown source")
        page = doc.get("metadata", {}).get("page", "")
        score = doc.get("relevance_score", 0)
        content = doc.get("content", "").strip()

        page_info = f" (page {page})" if page else ""
        sections.append(
            f"[Document {idx}] Source: {source}{page_info} | Relevance: {score:.2f}\n"
            f"{content}"
        )

    return "\n\n---\n\n".join(sections)
