"""
AstraDB Vector Store Interface

Two public functions:
  find_similar_problem(query_vector)         → dict | None
  insert_problem(problem_data, vector)       → dict

This is the Python equivalent of the MongoDB Problem model operations in the
JS codebase, extended with vector similarity search via AstraDB's ANN index.

How AstraDB vector search works:
  - Each document stored in the collection has a "$vector" field (1024 floats).
  - On find(), sorting by {"$vector": query_vector} triggers an ANN (Approximate
    Nearest Neighbour) search using the cosine distance index.
  - With include_similarity=True, each returned document gains a "$similarity"
    key containing the cosine similarity score in [0, 1].
  - We return only the top-1 result and check it against SIMILARITY_THRESHOLD.
"""

from app.config.db import db
from app.utils.logger import get_logger

logger = get_logger(__name__)

COLLECTION_NAME = "coderx_problems"

# Cosine similarity threshold for cache hits.
# A score of 1.0 means identical vectors; 0.0 means orthogonal (completely dissimilar).
# 0.88 was chosen because:
#   - Same topic + difficulty  →  ~0.95–0.99 (always hits cache)
#   - Related topic, same diff →  ~0.80–0.88 (borderline, may hit cache — that's fine)
#   - Different topic          →  ~0.50–0.75 (always misses — generates new problem)
SIMILARITY_THRESHOLD = 0.88


def _get_collection():
    """Return the live AstraDB collection handle."""
    return db.get_collection(COLLECTION_NAME)


def find_similar_problem(
    query_vector: list[float],
    threshold: float = SIMILARITY_THRESHOLD,
) -> dict | None:
    """
    Search the vector collection for a problem semantically similar to
    the given query vector.

    The search uses AstraDB's built-in ANN (cosine) index — no full table
    scan, O(log n) performance even at millions of documents.

    Args:
        query_vector: 1024-dim float list produced by embed_query().
                      Must match the dimensionality of the stored vectors.
        threshold:    minimum cosine similarity to consider a cache hit.
                      Defaults to SIMILARITY_THRESHOLD (0.88).

    Returns:
        The matching document dict (without the $vector field) if a hit is
        found, or None if the collection is empty or the best match is below
        the threshold.
    """
    collection = _get_collection()

    # sort={"$vector": ...} triggers ANN search.
    # projection={"$vector": False} excludes the raw 1024-float array from
    # the network response — we don't need it back and it's ~8 KB per doc.
    cursor = collection.find(
        filter={},
        sort={"$vector": query_vector},
        limit=1,
        include_similarity=True,
        projection={"$vector": False},
    )

    results = list(cursor)
    if not results:
        logger.info("[AstraStore] Collection is empty — no candidates.")
        return None

    top_doc = results[0]
    similarity: float = top_doc.get("$similarity", 0.0)

    logger.info(
        f"[AstraStore] Best candidate: '{top_doc.get('title')}' | "
        f"similarity={similarity:.4f} | threshold={threshold}"
    )

    if similarity >= threshold:
        logger.info(
            f"[AstraStore] Cache HIT ✓ — '{top_doc.get('title')}' "
            f"(sim={similarity:.4f})"
        )
        return top_doc

    logger.info(
        f"[AstraStore] Cache MISS ✗ — similarity {similarity:.4f} < {threshold}. "
        "Will generate a new problem."
    )
    return None


def insert_problem(problem_data: dict, vector: list[float]) -> dict:
    """
    Insert a new problem document into AstraDB, attaching the embedding vector.

    The "$vector" field is the AstraDB convention for the vector column —
    it is used exclusively for ANN indexing and is not returned to API callers.

    Args:
        problem_data: cleaned problem dict (title, description, difficulty,
                      testCases, editorial, topic).
        vector:       1024-dim float list produced by embed_document().

    Returns:
        The problem dict with an "_id" string field added (the AstraDB-assigned UUID).
    """
    collection = _get_collection()

    # Merge the problem fields with the vector column
    doc = {**problem_data, "$vector": vector}
    result = collection.insert_one(doc)

    inserted_id = str(result.inserted_id)
    logger.info(
        f"[AstraStore] Inserted ✓ | _id='{inserted_id}' | "
        f"title='{problem_data.get('title')}'"
    )

    # Return the problem data without the raw $vector (caller doesn't need it)
    return {**problem_data, "_id": inserted_id}
