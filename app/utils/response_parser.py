

import json
import re

from app.errors.base_error import BaseError
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _sanitize_cpp_snippet(code: str) -> str:
    """
    Fix common LLM mistakes in C++ code snippets that survive JSON parsing
    but break the compiler.

    Problem: The LLM writes ``'\\n'`` in its JSON output.  After
    ``json.loads`` that becomes the Python string ``'\n'`` — i.e. a
    single-quote, a real newline byte (0x0A), and a closing single-quote.
    When written to a .cpp file, g++ sees an unterminated char literal:

        cout << result << '<newline>

    Fix: replace every occurrence of <'><0x0A><'> with the string
    literal ``"\\n"`` which is valid, idiomatic C++.
    """
    # Replace '\n' (real newline inside single quotes) → "\n"
    code = code.replace("'\n'", '"\\n"')
    return code

REQUIRED_FIELDS: frozenset[str] = frozenset(
    {"title", "description", "difficulty", "testCases", "editorial", "codeSnippets"}
)

VALID_LANGUAGES: frozenset[str] = frozenset({"python", "java", "cpp"})
REQUIRED_SNIPPET_KEYS: frozenset[str] = frozenset(
    {"language", "startSnippet", "midSnippet", "endSnippet"}
)
VALID_DIFFICULTIES: frozenset[str] = frozenset({"easy", "medium", "hard"})


def _extract_json(raw: str) -> str:
    
    cleaned = raw.strip()

    
    try:
        json.loads(cleaned)
        return cleaned
    except json.JSONDecodeError:
        pass

    
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = cleaned[start : end + 1]
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            pass

    
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        
        inner = "\n".join(lines[1:-1]).strip()
        start = inner.find("{")
        end = inner.rfind("}")
        if start != -1 and end != -1:
            return inner[start : end + 1]
        return inner

    return cleaned


def parse_llm_response(raw: str) -> dict:

    
    cleaned = _extract_json(raw)

    
    try:
        data: dict = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.error(
            f"[ResponseParser] JSON decode failed after extraction: {exc}\n"
            f"Raw length: {len(raw)} chars | "
            f"First 500 chars of raw: {raw[:500]!r}\n"
            f"Extracted candidate ({len(cleaned)} chars): {cleaned[:300]!r}"
        )
        raise BaseError(
            502,
            "The AI model returned malformed JSON. Please retry.",
            str(exc),
        )

    
    missing = REQUIRED_FIELDS - set(data.keys())
    if missing:
        logger.error(f"[ResponseParser] Missing fields: {sorted(missing)}")
        raise BaseError(
            502,
            f"AI response is missing required fields: {sorted(missing)}.",
        )

    
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


    # ── codeSnippets validation ──────────────────────────────────────────────
    snippets = data.get("codeSnippets")
    if not isinstance(snippets, list) or len(snippets) != 3:
        raise BaseError(
            502,
            f"AI response must include exactly 3 codeSnippets (python, java, cpp). "
            f"Got: {len(snippets) if isinstance(snippets, list) else 'non-list'}.",
        )

    for i, snippet in enumerate(snippets):
        if not isinstance(snippet, dict):
            raise BaseError(502, f"codeSnippets[{i}] must be an object.")

        missing_keys = REQUIRED_SNIPPET_KEYS - set(snippet.keys())
        if missing_keys:
            raise BaseError(
                502,
                f"codeSnippets[{i}] is missing keys: {sorted(missing_keys)}.",
            )

        lang = snippet.get("language", "").strip().lower()
        if lang not in VALID_LANGUAGES:
            raise BaseError(
                502,
                f"codeSnippets[{i}] has invalid language '{snippet.get('language')}'. "
                f"Expected one of: {sorted(VALID_LANGUAGES)}.",
            )

        for key in ("startSnippet", "midSnippet", "endSnippet"):
            if not isinstance(snippet.get(key), str) or not snippet[key].strip():
                raise BaseError(
                    502,
                    f"codeSnippets[{i}].{key} must be a non-empty string.",
                )

        # Sanitize C++ snippets: fix literal newlines inside char literals
        if lang == "cpp":
            for key in ("startSnippet", "midSnippet", "endSnippet"):
                snippet[key] = _sanitize_cpp_snippet(snippet[key])

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