"""
LLM Response Parser

Responsible for:
  1. Stripping any accidental markdown fences the LLM adds
  2. Parsing the raw string as JSON
  3. Validating all required fields are present
  4. Validating field-level constraints (difficulty enum, testCases length)
"""

import json

from app.errors.base_error import BaseError
from app.utils.logger import get_logger

logger = get_logger(__name__)

REQUIRED_FIELDS: frozenset[str] = frozenset(
    {"title", "description", "difficulty", "testCases", "editorial"}
)
VALID_DIFFICULTIES: frozenset[str] = frozenset({"easy", "medium", "hard"})


def parse_llm_response(raw: str) -> dict:
    """
    Parse and validate the raw LLM output string into a problem dictionary.

    Args:
        raw: the raw string returned by the LLM

    Returns:
        A validated dict with keys:
            title, description, difficulty, testCases, editorial

    Raises:
        BaseError(502): malformed JSON, missing fields, or invalid values.
    """

    # ── 1. Strip markdown fences if present ──────────────────────────────────
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        cleaned = "\n".join(lines[1:-1]).strip()

    # ── 2. JSON decode ────────────────────────────────────────────────────────
    try:
        data: dict = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.error(
            f"[ResponseParser] JSON decode failed: {exc}\n"
            f"Raw length: {len(raw)} chars | "
            f"First 500 chars: {raw[:500]!r}"
        )
        raise BaseError(
            502,
            "The AI model returned malformed JSON. Please retry.",
            str(exc),
        )

    # ── 3. Required fields check ──────────────────────────────────────────────
    missing = REQUIRED_FIELDS - set(data.keys())
    if missing:
        logger.error(f"[ResponseParser] Missing fields: {sorted(missing)}")
        raise BaseError(
            502,
            f"AI response is missing required fields: {sorted(missing)}.",
        )

    # ── 4. testCases integrity ────────────────────────────────────────────────
    if not isinstance(data["testCases"], list) or len(data["testCases"]) != 3:
        raise BaseError(
            502,
            f"AI response must include exactly 3 test cases. "
            f"Got: {len(data['testCases']) if isinstance(data['testCases'], list) else 'non-list'}.",
        )

    for i, tc in enumerate(data["testCases"]):
        if not isinstance(tc, dict) or "input" not in tc or "output" not in tc:
            raise BaseError(
                502,
                f"testCase at index {i} is missing 'input' or 'output' field.",
            )

    # ── 5. Difficulty enum ────────────────────────────────────────────────────
    if data.get("difficulty") not in VALID_DIFFICULTIES:
        raise BaseError(
            502,
            f"AI returned invalid difficulty: '{data.get('difficulty')}'. "
            f"Expected one of: {sorted(VALID_DIFFICULTIES)}.",
        )

    logger.info(
        f"[ResponseParser] Valid response | "
        f"title='{data['title']}' | "
        f"difficulty='{data['difficulty']}' | "
        f"testCases={len(data['testCases'])}"
    )

    return data