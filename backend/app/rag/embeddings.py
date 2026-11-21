"""
AIOps Agent – Embedding Generation
=====================================
Generates dense vector embeddings for text using Sentence Transformers.

Why Sentence Transformers?
- Free, open-source, runs locally (no API key needed).
- 'all-MiniLM-L6-v2' is fast (384-dim) and accurate for semantic search.
- No per-request costs – ideal for a demo/portfolio project.

How embeddings work:
- Each piece of text is converted to a list of ~384 floating-point numbers.
- Texts with similar meaning have vectors that are "close" in this space.
- Semantic search = find the document vectors closest to your query vector.
"""

from typing import List
from functools import lru_cache
from app.config import get_settings
from app.core.logging import get_logger
from app.core.exceptions import VectorStoreError

logger = get_logger(__name__)
settings = get_settings()


@lru_cache(maxsize=1)
def _get_model():
    """
    Load the Sentence Transformer model (cached so it loads only once).

    Why lru_cache?
    - Loading a model takes ~2-5 seconds.
    - We only want to pay that cost once at startup, not per request.
    """
    try:
        from sentence_transformers import SentenceTransformer

        model_name = settings.embedding_model
        logger.info("Loading embedding model", model=model_name)
        model = SentenceTransformer(model_name)
        logger.info("Embedding model loaded successfully", model=model_name)
        return model
    except ImportError:
        raise VectorStoreError(
            "sentence-transformers is not installed. Run: pip install sentence-transformers"
        )
    except Exception as e:
        raise VectorStoreError(f"Failed to load embedding model: {str(e)}")


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of text strings.

    Args:
        texts: List of text strings to embed.

    Returns:
        List of embedding vectors (each is a list of floats).

    Example:
        embeddings = embed_texts(["Database connection timeout", "Network error"])
        # Returns: [[0.12, -0.34, ...], [0.56, 0.78, ...]]
    """
    if not texts:
        return []

    try:
        model = _get_model()
        embeddings = model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,  # L2-normalise for cosine similarity
        )
        return embeddings.tolist()

    except VectorStoreError:
        raise
    except Exception as e:
        raise VectorStoreError(f"Embedding generation failed: {str(e)}")


def embed_query(query: str) -> List[float]:
    """
    Embed a single query string for retrieval.

    Args:
        query: The user's question or search text.

    Returns:
        A single embedding vector.
    """
    results = embed_texts([query])
    if not results:
        raise VectorStoreError("Failed to embed query")
    return results[0]
