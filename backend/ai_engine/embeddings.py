import logging
logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
except ImportError:
    model = None
    logger.warning("sentence-transformers not installed. Embedding generation mocked.")

def generate_embedding(text: str) -> list[float]:
    """Generate embedding for a single text string."""
    if not model:
        return [0.0] * 384
    return model.encode(text).tolist()

def generate_batch_embeddings(texts: list[str]) -> list[list[float]]:
    """Batch embedding generation for efficiency."""
    if not model:
        return [[0.0] * 384 for _ in texts]
    return model.encode(texts, batch_size=32, show_progress_bar=False).tolist()
