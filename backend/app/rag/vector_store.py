"""
AIOps Agent – ChromaDB Vector Store
=======================================
Manages storage and retrieval of document embeddings in ChromaDB.

Why ChromaDB?
- Lightweight, open-source vector database.
- Runs in-process (no separate server needed for development).
- Persists data to disk so embeddings survive restarts.
- Supports metadata filtering for fine-grained retrieval.

Architecture:
  Document → Chunks → Embeddings → ChromaDB (persisted on disk)
  Query → Query Embedding → ChromaDB similarity search → Top-K chunks
"""

import os
from typing import List, Dict, Any, Optional
from app.config import get_settings
from app.core.logging import get_logger
from app.core.exceptions import VectorStoreError
from app.rag.chunking import TextChunk
from app.rag.embeddings import embed_texts, embed_query

logger = get_logger(__name__)
settings = get_settings()


def _get_client():
    """
    Get or create the ChromaDB persistent client.
    Uses a module-level singleton to avoid creating multiple clients.
    """
    try:
        import chromadb
        from chromadb.config import Settings as ChromaSettings

        persist_dir = os.path.abspath(settings.chroma_persist_dir)
        os.makedirs(persist_dir, exist_ok=True)

        client = chromadb.PersistentClient(
            path=persist_dir,
        )
        return client
    except ImportError:
        raise VectorStoreError(
            "chromadb is not installed. Run: pip install chromadb"
        )
    except Exception as e:
        raise VectorStoreError(f"Failed to initialise ChromaDB: {str(e)}")


def get_collection(collection_name: Optional[str] = None):
    """
    Get or create a ChromaDB collection.

    A collection is like a table in a relational database –
    it groups related documents together.

    Args:
        collection_name: Name of the collection. Defaults to settings value.

    Returns:
        A ChromaDB Collection object.
    """
    name = collection_name or settings.chroma_collection_name
    client = _get_client()
    try:
        # get_or_create_collection: creates if missing, returns existing otherwise.
        collection = client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},  # Use cosine similarity
        )
        logger.info("ChromaDB collection ready", collection=name)
        return collection
    except Exception as e:
        raise VectorStoreError(f"Failed to get collection '{name}': {str(e)}")


def add_chunks_to_store(
    chunks: List[TextChunk],
    collection_name: Optional[str] = None,
) -> int:
    """
    Embed and store a list of TextChunks in ChromaDB.

    Args:
        chunks:          Chunked documents from chunking.chunk_documents().
        collection_name: ChromaDB collection to add chunks to.

    Returns:
        Number of chunks successfully stored.
    """
    if not chunks:
        logger.warning("No chunks provided to add_chunks_to_store")
        return 0

    collection = get_collection(collection_name)

    # Generate embeddings for all chunk texts
    texts = [c.content for c in chunks]
    try:
        embeddings = embed_texts(texts)
    except Exception as e:
        raise VectorStoreError(f"Embedding generation failed: {str(e)}")

    # Prepare IDs, documents, embeddings, and metadata for ChromaDB
    ids = [c.chunk_id for c in chunks]
    metadatas = [c.metadata for c in chunks]

    # ChromaDB requires all metadata values to be str/int/float/bool
    # Convert any list/dict values to strings
    safe_metadatas = []
    for meta in metadatas:
        safe_meta = {}
        for k, v in meta.items():
            if isinstance(v, (str, int, float, bool)):
                safe_meta[k] = v
            else:
                safe_meta[k] = str(v)
        safe_metadatas.append(safe_meta)

    try:
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=safe_metadatas,
        )
        logger.info(
            "Chunks stored in ChromaDB",
            count=len(chunks),
            collection=collection_name or settings.chroma_collection_name,
        )
        return len(chunks)

    except Exception as e:
        raise VectorStoreError(f"Failed to store chunks in ChromaDB: {str(e)}")


def search_similar(
    query: str,
    top_k: int = 5,
    collection_name: Optional[str] = None,
    where: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Perform semantic similarity search in ChromaDB.

    Args:
        query:           The user's question or incident description.
        top_k:           Number of results to return.
        collection_name: Which collection to search.
        where:           Optional metadata filter dict.

    Returns:
        List of dicts with 'content', 'metadata', and 'distance' keys.
        Lower distance = more similar.
    """
    collection = get_collection(collection_name)

    try:
        # Check if collection has any documents
        count = collection.count()
        if count == 0:
            logger.warning("Collection is empty – no documents have been uploaded yet")
            return []

        # Embed the query
        query_embedding = embed_query(query)

        # Query ChromaDB
        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": min(top_k, count),  # Can't return more than what's stored
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            query_params["where"] = where

        results = collection.query(**query_params)

        # Flatten the nested result structure into a clean list
        output = []
        if results and results.get("documents"):
            for idx in range(len(results["documents"][0])):
                output.append(
                    {
                        "content": results["documents"][0][idx],
                        "metadata": results["metadatas"][0][idx],
                        "distance": results["distances"][0][idx],
                        "relevance_score": round(1.0 - results["distances"][0][idx], 4),
                    }
                )

        logger.info(
            "Semantic search complete",
            query_len=len(query),
            results_found=len(output),
        )
        return output

    except Exception as e:
        raise VectorStoreError(f"Semantic search failed: {str(e)}")


def get_collection_stats(collection_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Return basic statistics about a ChromaDB collection.

    Args:
        collection_name: Which collection to inspect.

    Returns:
        Dict with 'name', 'document_count', and 'status'.
    """
    name = collection_name or settings.chroma_collection_name
    try:
        collection = get_collection(name)
        return {
            "name": name,
            "document_count": collection.count(),
            "status": "ready",
        }
    except Exception as e:
        return {"name": name, "document_count": 0, "status": f"error: {str(e)}"}


def delete_collection(collection_name: Optional[str] = None) -> bool:
    """
    Delete a ChromaDB collection and all its contents.
    Use with caution!
    """
    name = collection_name or settings.chroma_collection_name
    try:
        client = _get_client()
        client.delete_collection(name)
        logger.info("ChromaDB collection deleted", collection=name)
        return True
    except Exception as e:
        logger.error("Failed to delete collection", collection=name, error=str(e))
        return False
