"""
Question Generator Service

Python port of the JS generateAndSaveProblem service, extended with a
semantic deduplication layer that uses AstraDB vector search to avoid
calling the LLM when a similar problem already exists.

Execution path:
  1.  Validate & normalise inputs
  2.  Build a query embedding from topic + difficulty
  3.  ANN search AstraDB  →  cache HIT?  →  return existing problem
  4.  Format prompt using problemPrompt.py template
  5.  Invoke Groq LLM via LangChain
  6.  Parse & validate the raw JSON response
  7.  Embed the problem text (document-optimised) for storage
  8.  Insert the document + vector into AstraDB
  9.  Return the saved problem

Response envelope:
  {
      "source": "cache" | "generated",
      "problem": { title, description, difficulty, testCases, editorial,
                   topic, _id }
  }
"""

from app.config.langchainConfig import get_groq_client
from app.prompts.problemPrompt import problem_prompt
from app.utils.response_parser import parse_llm_response
from app.utils.embedder import embed_document, embed_query
from app.vector_store.astra_store import find_similar_problem, insert_problem
from app.utils.logger import get_logger
from app.errors.base_error import BaseError

logger = get_logger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────

VALID_TOPICS: list[str] = [
    "arrays", "strings", "linked lists", "stacks", "queues",
    "trees", "graphs", "dynamic programming", "backtracking",
    "binary search", "sorting", "hashing", "heaps", "tries",
    "recursion", "greedy", "bit manipulation", "math",
]

VALID_DIFFICULTIES: list[str] = ["easy", "medium", "hard"]


# ── Service function ──────────────────────────────────────────────────────────

def generate_and_save_problem(topic: str, difficulty: str) -> dict:
    """
    Generate (or retrieve) a coding problem for the given topic and difficulty.

    This is the single entry point for the /generate/problem endpoint.
    It mirrors the shape and responsibilities of the JS generateAndSaveProblem
    function while adding the semantic deduplication step (step 2–3 above).

    Args:
        topic:      programming topic string (e.g. "binary search").
        difficulty: one of "easy", "medium", "hard".

    Returns:
        A dict with keys:
            source  — "cache" if an existing problem was returned,
                       "generated" if the LLM produced a new one.
            problem — the full problem object including _id.

    Raises:
        BaseError(400): invalid / missing input.
        BaseError(502): LLM failure.
        BaseError(500): database failure.
    """

    # ── 1. Validate & normalise ───────────────────────────────────────────────
    if not topic or not isinstance(topic, str) or not topic.strip():
        raise BaseError(
            400,
            'Request body must include a non-empty "topic" field.',
            f"Received: {topic!r}",
        )

    if not difficulty or not isinstance(difficulty, str) or not difficulty.strip():
        raise BaseError(
            400,
            'Request body must include a non-empty "difficulty" field.',
            f"Received: {difficulty!r}",
        )

    normalised_topic = topic.strip().lower()
    normalised_difficulty = difficulty.strip().lower()

    if normalised_difficulty not in VALID_DIFFICULTIES:
        raise BaseError(
            400,
            f"Invalid difficulty. Must be one of: {', '.join(VALID_DIFFICULTIES)}.",
            f"Received: {difficulty!r}",
        )

    logger.info(
        f'[QuestionGenerator] Request | '
        f'topic="{normalised_topic}" | difficulty="{normalised_difficulty}"'
    )

    # ── 2. Build query embedding ──────────────────────────────────────────────
    # We use a short, focused query string that captures the user's intent.
    # The "competitive programming problem:" prefix steers the embedding model
    # toward the domain-specific semantic space so similarity scores are more
    # meaningful than with a bare "binary search medium" query.
    #
    # input_type="query" tells Voyage AI to produce a retrieval-optimised
    # embedding — designed to find semantically matching *documents* even when
    # the phrasing differs.
    query_text = (
        f"competitive programming problem: {normalised_topic}, "
        f"difficulty: {normalised_difficulty}"
    )
    query_vector = embed_query(query_text)

    # ── 3. Semantic similarity check (cache lookup) ───────────────────────────
    # AstraDB's ANN index finds the closest stored vector in O(log n).
    # If the cosine similarity meets the threshold we return the cached problem
    # immediately — NO LLM call, NO embedding call, instant response.
    existing = find_similar_problem(query_vector)
    if existing:
        # Scrub internal AstraDB fields before returning to the caller
        existing.pop("$vector", None)
        existing.pop("$similarity", None)
        if "_id" in existing:
            existing["_id"] = str(existing["_id"])

        logger.info(
            f'[QuestionGenerator] Cache HIT → returning cached '
            f'"{existing.get("title")}"'
        )
        return {"source": "cache", "problem": existing}

    # ── 4. Format prompt ──────────────────────────────────────────────────────
    # Uses the LangChain PromptTemplate from app/prompts/problemPrompt.py.
    # The template injects topic and difficulty and enforces a strict JSON
    # output contract (title, description, difficulty, testCases, editorial).
    formatted_prompt = problem_prompt.format(
        topic=normalised_topic,
        difficulty=normalised_difficulty,
    )

    # ── 5. Call LLM ───────────────────────────────────────────────────────────
    try:
        llm = get_groq_client()
        response = llm.invoke(formatted_prompt)
        # LangChain wraps the Groq response in an AIMessage object.
        # We extract the text content — the field is always `.content` in
        # LangChain v0.2+.
        raw: str = response.content if hasattr(response, "content") else str(response)

    except BaseError:
        raise  # our own errors pass through unchanged

    except Exception as llm_err:
        logger.error(f"[QuestionGenerator] LLM invocation failed: {llm_err}")
        raise BaseError(
            502,
            "Failed to get a response from the AI model. Please try again.",
            str(llm_err),
        )

    logger.info("[QuestionGenerator] LLM responded — parsing output...")

    # ── 6. Parse & validate LLM response ─────────────────────────────────────
    # parse_llm_response() strips markdown fences, JSON-decodes, and checks
    # field presence + value constraints. Raises BaseError(502) on failure.
    problem_data: dict = parse_llm_response(raw)

    # Attach the original topic so the stored document is self-describing
    # (the LLM output only includes the difficulty, not the topic explicitly).
    problem_data["topic"] = normalised_topic

    # ── 7. Build storage embedding ────────────────────────────────────────────
    # We embed a richer string for storage than we used for the query.
    # Including the generated title anchors the vector to the specific problem,
    # so future queries for the same topic+difficulty will find this document
    # via its semantic similarity to the query vector.
    #
    # input_type="document" tells Voyage AI to produce a storage-optimised
    # embedding — designed to be retrieved by query embeddings.
    doc_text = (
        f"competitive programming problem: {normalised_topic}, "
        f"difficulty: {normalised_difficulty}: {problem_data['title']}"
    )
    doc_vector = embed_document(doc_text)

    # ── 8. Persist to AstraDB ─────────────────────────────────────────────────
    try:
        saved_problem = insert_problem(problem_data, doc_vector)

    except BaseError:
        raise

    except Exception as db_err:
        logger.error(f"[QuestionGenerator] AstraDB insert failed: {db_err}")
        raise BaseError(
            500,
            "Failed to save the generated problem to the database.",
            str(db_err),
        )

    logger.info(
        f'[QuestionGenerator] Saved ✓ | '
        f'_id="{saved_problem.get("_id")}" | '
        f'title="{saved_problem.get("title")}"'
    )

    # ── 9. Return ─────────────────────────────────────────────────────────────
    return {"source": "generated", "problem": saved_problem}
