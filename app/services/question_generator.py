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
from app.prompts.promptParser import problem_prompt as parser_prompt

logger = get_logger(__name__)



VALID_TOPICS: list[str] = [
    "arrays", "strings", "linked lists", "stacks", "queues",
    "trees", "graphs", "dynamic programming", "backtracking",
    "binary search", "sorting", "hashing", "heaps", "tries",
    "recursion", "greedy", "bit manipulation", "math",
]

VALID_DIFFICULTIES: list[str] = ["easy", "medium", "hard"]



def prompt_to_inputs(input_prompt: str) -> dict:
    try:
        result = parser_prompt.invoke({"user_prompt": input_prompt})
        model = get_groq_client()
        response = model.invoke(result)
        raw_output = response.content if hasattr(response, "content") else str(response)
        
        logger.info(f'user prompt is : {input_prompt} \n and the output generated from llm is {raw_output}\n')
        
        topic = ""
        difficulty = ""
        for line in raw_output.splitlines():
            line = line.strip()
            if line.lower().startswith("string:"):
                topic = line.split(":", 1)[1].strip()
            elif line.lower().startswith("difficulty:"):
                difficulty = line.split(":", 1)[1].strip()
                
        return {"topic": topic, "difficulty": difficulty}
    except BaseError:
        raise
    except Exception as e:
        logger.error(f"[prompt_to_inputs] Failed to parse user prompt: {e}")
        raise BaseError(500, "Failed to parse user prompt", str(e))


def generate_and_save_problem(topic: str, difficulty: str) -> dict:
    
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

    query_text = (
        f"competitive programming problem: {normalised_topic}, "
        f"difficulty: {normalised_difficulty}"
    )
    query_vector = embed_query(query_text)

  
    existing = find_similar_problem(query_vector, difficulty=normalised_difficulty)
    if existing:
        
        existing.pop("$vector", None)
        existing.pop("$similarity", None)
        if "_id" in existing:
            existing["_id"] = str(existing["_id"])

        logger.info(
            f'[QuestionGenerator] Cache HIT → returning cached '
            f'"{existing.get("title")}"'
        )
        return {"source": "cache", "problem": existing}

    formatted_prompt = problem_prompt.format(
        topic=normalised_topic,
        difficulty=normalised_difficulty,
    )

    try:
        llm = get_groq_client()
        response = llm.invoke(formatted_prompt)
        raw: str = response.content if hasattr(response, "content") else str(response)

    except BaseError:
        raise  

    except Exception as llm_err:
        logger.error(f"[QuestionGenerator] LLM invocation failed: {llm_err}")
        raise BaseError(
            502,
            "Failed to get a response from the AI model. Please try again.",
            str(llm_err),
        )

    logger.info("[QuestionGenerator] LLM responded — parsing output...")

   
    problem_data: dict = parse_llm_response(raw)

   
    problem_data["topic"] = normalised_topic

   
    doc_text = (
        f"competitive programming problem: {normalised_topic}, "
        f"difficulty: {normalised_difficulty}: {problem_data['title']}"
    )
    doc_vector = embed_document(doc_text)

    
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

    
    return {"source": "generated", "problem": saved_problem}
