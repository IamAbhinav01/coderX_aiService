"""
LLM Response Parser

Mirrors the JS utils/responseParser.js.

Responsible for:
  1. Stripping any accidental markdown fences the LLM adds despite instructions
  2. Parsing the raw string as JSON
  3. Validating that all required fields are present
  4. Validating field-level constraints (difficulty enum, testCases list length)
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

    Even though response_format=json_object is set at the API level the LLM
    occasionally wraps the output in markdown fences (```json ... ```). This
    function strips those before attempting JSON parsing.

    Args:
        raw: the raw string returned by ChatGroq.invoke().content

    Returns:
        A validated dict with keys: title, description, difficulty,
        testCases (list of 3 dicts), editorial.

    Raises:
        BaseError(502): malformed JSON, missing required fields, or invalid values.
    """
    # ── Strip markdown code fences if present ────────────────────────────────
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        # Remove the opening  ``` / ```json  line and the closing  ```  line
        cleaned = "\n".join(lines[1:-1]).strip()

    # ── JSON decode ───────────────────────────────────────────────────────────
    try:
        data: dict = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.error(
            f"[ResponseParser] JSON decode failed: {exc}\n"
            f"Raw length: {len(raw)} chars | "
            f"First 500 chars: {raw[:500]!r}"
            # If 'raw length' is suspiciously short (e.g. < 200 chars for a full problem),
            # the LLM hit its max_tokens limit and truncated the output mid-string.
        )
        raise BaseError(
            502,
            "The AI model returned malformed JSON. Please retry.",
            str(exc),
        )

    # ── Required field check ──────────────────────────────────────────────────
    missing = REQUIRED_FIELDS - set(data.keys())
    if missing:
        logger.error(f"[ResponseParser] Missing fields: {sorted(missing)}")
        raise BaseError(
            502,
            f"AI response is missing required fields: {sorted(missing)}.",
        )

    # ── testCases integrity ───────────────────────────────────────────────────
    if not isinstance(data["testCases"], list) or len(data["testCases"]) < 1:
        raise BaseError(502, "AI response must include at least one test case.")

    # ── difficulty enum ───────────────────────────────────────────────────────
    if data.get("difficulty") not in VALID_DIFFICULTIES:
        raise BaseError(
            502,
            f"AI returned an invalid difficulty: '{data.get('difficulty')}'. "
            f"Expected one of: {sorted(VALID_DIFFICULTIES)}.",
        )

    logger.info(
        f"[ResponseParser] Valid response | "
        f"title='{data['title']}' | difficulty='{data['difficulty']}' | "
        f"testCases={len(data['testCases'])}"
    )
    return data
