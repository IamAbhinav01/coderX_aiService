from app.config.db import db
from app.utils.logger import get_logger
import json

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

# def insert_into_mongodb(problem_data: dict):
#     return 

def insert_problem(problem_data: dict, vector: list[float]) -> dict:
    

    with open("problem_debug.json", "w") as f:
        json.dump(problem_data, f, indent=4)
    logger.info(f"Problem data written to problem_debug.json")
    # logger.info("Storing new problem to MongoDB")
    # insert_into_mongodb(problem_data=problem_data)

    collection = _get_collection()

    # Merge the problem fields with the vector column
    doc = {**problem_data, "$vector": vector}
    result = collection.insert_one(doc)

    inserted_id = str(result.inserted_id)
    logger.info(
        f"[AstraStore] Inserted ✓ | _id='{inserted_id}' | "
        f"title='{problem_data.get('title')}'"
    )

    return {**problem_data, "_id": inserted_id}
