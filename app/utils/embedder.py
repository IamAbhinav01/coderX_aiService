"""
Sentence Transformers embedding utilities.

Model: BAAI/bge-large-en-v1.5
  - Produces 1024-dimensional vectors — matches the AstraDB collection exactly,
    no collection recreation needed.
  - Ranked among the top open-source embedding models on the MTEB leaderboard.
  - Runs fully locally — no API key, no network call per embed, no rate limits.
  - First load downloads ~1.3 GB to the HuggingFace cache; subsequent starts
    are instant (model is cached on disk).

Asymmetric embedding (same concept as Voyage AI's input_type):
  - Documents (storage): encoded normally with L2-normalised vectors.
  - Queries  (search) : encoded with the BGE instruction prefix
      "Represent this sentence for searching relevant passages: "
    This steers the query embedding into the retrieval subspace so cosine
    similarity against document embeddings is maximised for relevant results.
"""

from app.utils.logger import get_logger
from sentence_transformers import SentenceTransformer

logger = get_logger(__name__)

# ── Model config ───────────────────────────────────────────────────────────────
MODEL_NAME = "BAAI/bge-base-en-v1.5"
EXPECTED_DIMS = 768  # must match the AstraDB collection vector dimension

# BGE models use a plain instruction prefix for query-side asymmetric retrieval.
# See: https://huggingface.co/BAAI/bge-large-en-v1.5#usage
_BGE_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    """
    Return the singleton SentenceTransformer model.

    The model is loaded lazily on first call. On subsequent calls the same
    in-memory object is returned immediately — no reloading.

    CPython's GIL makes this safe for multi-threaded FastAPI thread-pool
    workers: only one thread will enter the `if` block.
    """
    global _model
    if _model is None:
        logger.info(
            f"[Embedder] Loading '{MODEL_NAME}' — "
            "first load downloads ~1.3 GB to HuggingFace cache..."
        )
        _model = SentenceTransformer(MODEL_NAME)
        dims = _model.get_sentence_embedding_dimension()
        if dims != EXPECTED_DIMS:
            raise RuntimeError(
                f"[Embedder] Model produced {dims}-dim vectors but AstraDB "
                f"collection expects {EXPECTED_DIMS}. Recreate the collection "
                "or switch to a model with matching dimensions."
            )
        logger.info(f"[Embedder] Model ready | dims={dims}")
    return _model


def embed_document(text: str) -> list[float]:
    """
    Produce a 1024-dimensional embedding vector optimised for **storage**.

    Call this when you have the full problem text ready to insert into AstraDB.
    Vectors are L2-normalised so cosine similarity reduces to a dot product —
    this is what AstraDB's COSINE metric expects.

    Args:
        text: the document string (e.g. "topic: binary search, difficulty: medium: <title>").

    Returns:
        A list of 1024 floats in the range [-1, 1].
    """
    model = _get_model()
    # No prefix for documents — BGE encodes them as-is.
    # normalize_embeddings=True → L2 normalisation → cosine sim == dot product.
    vector = model.encode(text, normalize_embeddings=True)
    logger.info(f"[Embedder] Document embedded | dims={len(vector)}")
    return vector.tolist()


def embed_query(text: str) -> list[float]:
    """
    Produce a 768-dimensional embedding vector optimised for **retrieval**.

    Call this when searching AstraDB for a semantically similar problem.
    The BGE instruction prefix shifts the query embedding into the same
    retrieval subspace as the stored document vectors, improving recall.

    Args:
        text: the short query string (e.g. "competitive programming: binary search, medium").

    Returns:
        A list of 768 floats in the range [-1, 1].
    """
    model = _get_model()
    # Prepend the BGE query instruction — this is the sentence-transformers
    # equivalent of Voyage AI's input_type="query".
    vector = model.encode(_BGE_QUERY_PREFIX + text, normalize_embeddings=True)
    logger.info(f"[Embedder] Query embedded | dims={len(vector)}")
    return vector.tolist()
