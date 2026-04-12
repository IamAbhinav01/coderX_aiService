import requests

from app.config.db import db
from app.utils.logger import get_logger
import json

logger = get_logger(__name__)

mongoDBRL = "http://localhost:3000/api/v1/problems"

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


def transform_for_mongodb(problem_data: dict) -> dict:
    return {
        "title": problem_data["title"],
        "description": problem_data["description"],
        "difficulty": problem_data["difficulty"],
        "testCases": problem_data["testCases"],
        "editorial": problem_data["editorial"],
        "codeStubs": [
            {
                "language": c["language"],
                "startSnippet": c["startSnippet"],
                "endSnippet": c["endSnippet"]
            }
            for c in problem_data["codeSnippets"]
        ]
    }
def insert_into_mongodb(problem_data: dict):

    new_problem_data = transform_for_mongodb(problem_data)

    response = requests.post(mongoDBRL, json=new_problem_data)

    if response.status_code != 201:
        logger.error(
            f"[MongoService] Failed to insert problem | "
            f"status={response.status_code} | response={response.text}"
        )
        raise Exception("Mongo insertion failed")

    data = response.json()

    mongo_id = data["data"]["_id"]   # depends on your API response

    logger.info(
        f"[MongoService] Inserted ✓ | mongo_id='{mongo_id}'"
    )

    return mongo_id

def insert_problem(problem_data: dict, vector: list[float]) -> dict:

    logger.info("Storing new problem to MongoDB")

    mongo_id = insert_into_mongodb(problem_data)

    collection = _get_collection()

    doc = {
        "mongo_id": mongo_id,
        "title": problem_data["title"],
        "difficulty": problem_data["difficulty"],
        "topic": problem_data.get("topic"),
        "$vector": vector
    }

    result = collection.insert_one(doc)

    vector_id = str(result.inserted_id)

    logger.info(
        f"[AstraStore] Inserted ✓ | vector_id='{vector_id}' | mongo_id='{mongo_id}'"
    )

    return {
        **problem_data,
        "_id": mongo_id
    }