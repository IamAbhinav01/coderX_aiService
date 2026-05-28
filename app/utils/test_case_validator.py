"""
Test Case Validator
-------------------
Extracts the Python reference implementation from the editorial markdown block,
executes each generated test case against it in a subprocess, and removes any
test case whose expected output does not match the reference output.

This prevents wrong AI-generated expected outputs from ever reaching the DB.
"""

import os
import re
import subprocess
import sys
import tempfile

from app.errors.base_error import BaseError
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Matches a fenced python code block inside the Reference Implementation section
_REFERENCE_CODE_RE = re.compile(
    r"###\s*Reference\s+Implementation\s*\n"   # section header
    r"```(?:python|py)?\s*\n"                  # opening fence (language tag optional)
    r"(.*?)"                                    # code  (captured)
    r"```",                                     # closing fence
    re.DOTALL | re.IGNORECASE,
)


def _extract_reference_code(editorial: str) -> str | None:
    """Return the Python reference solution embedded in the editorial, or None."""
    match = _REFERENCE_CODE_RE.search(editorial)
    if match:
        return match.group(1).strip()
    return None


def _run_code(code: str, input_data: str, timeout: int = 5) -> str | None:
    """
    Execute *code* with *input_data* piped to stdin.
    Returns stripped stdout on success, None on runtime error or timeout.
    """
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as fh:
            fh.write(code)
            tmp_path = fh.name

        result = subprocess.run(
            [sys.executable, tmp_path],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            logger.warning(
                f"[Validator] Reference script exited with code {result.returncode}: "
                f"{result.stderr[:300]}"
            )
            return None
        output = result.stdout.strip()
        if not output and result.stderr:
            logger.debug(
                f"[Validator] Script produced no stdout. stderr: {result.stderr[:200]}"
            )
        return output

    except subprocess.TimeoutExpired:
        logger.warning("[Validator] Reference script timed out")
        return None
    except Exception as exc:
        logger.warning(f"[Validator] Unexpected error running reference: {exc}")
        return None
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def _ensure_entrypoint(code: str, python_end_snippet: str | None = None) -> str:
    """
    If the reference code defines a ``solve`` function but has no entrypoint
    (``if __name__`` block or a top-level ``solve(...)`` call), append one so
    the script actually executes and produces stdout.

    Two cases:
      • solve() takes NO parameters  → append ``if __name__ == "__main__": solve()``
      • solve() takes parameters     → append *python_end_snippet* (the codeSnippet
        endSnippet, which already contains proper stdin-parsing + solve call).
        If no snippet is available the code is returned as-is.
    """
    import ast

    # Fast-path 1: already has an __name__ guard
    if '__name__' in code:
        return code

    try:
        tree = ast.parse(code)
    except SyntaxError:
        # Unparseable — let the subprocess surface the SyntaxError
        return code

    # Fast-path 2: a top-level call to solve(...) already exists
    for node in tree.body:
        if (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == 'solve'
        ):
            return code

    # Find the top-level solve() function definition
    solve_func: ast.FunctionDef | None = None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == 'solve':
            solve_func = node
            break

    if solve_func is None:
        return code  # no solve() — nothing to patch

    n_params = len(solve_func.args.args)

    if n_params == 0:
        # Zero-arg solve: safe to call directly
        return code + '\n\nif __name__ == "__main__":\n    solve()\n'

    # Parameterised solve: delegate to endSnippet for proper stdin parsing
    if python_end_snippet and python_end_snippet.strip():
        logger.debug(
            f"[Validator] solve() has {n_params} param(s) — "
            "appending Python endSnippet as entrypoint"
        )
        return code + '\n\n' + python_end_snippet.strip() + '\n'

    logger.warning(
        f"[Validator] solve() has {n_params} param(s) but no endSnippet — "
        "cannot auto-generate entrypoint; subprocess will likely raise TypeError"
    )
    return code


def _normalize(s: str) -> str:
    """Case-insensitive, whitespace-stripped comparison string."""
    return s.strip().lower()


def validate_and_filter_test_cases(problem_data: dict) -> dict:
    """
    Run every test case through the embedded Python reference solution and
    remove any whose expected output does not match the reference output.

    - If the reference code cannot be extracted, validation is skipped (soft-fail)
      so that problems still go through — just without filtering.
    - If ALL test cases fail validation a BaseError(502) is raised so the caller
      can retry generation instead of saving a broken problem.

    Args:
        problem_data: The parsed problem dict (already validated by response_parser).

    Returns:
        The same dict with ``testCases`` filtered to only verified entries.
    """
    editorial: str = problem_data.get("editorial", "")
    test_cases: list = problem_data.get("testCases", [])

    # ── 1. Extract reference implementation ───────────────────────────────────
    reference_code = _extract_reference_code(editorial)
    if not reference_code:
        logger.warning(
            "[Validator] Could not locate '### Reference Implementation' code block "
            "in editorial — skipping test-case validation."
        )
        return problem_data

    logger.info(
        f"[Validator] Reference code extracted ({len(reference_code)} chars) — "
        f"validating {len(test_cases)} test case(s)"
    )

    # ── 1b. Grab the Python endSnippet for parameterised-solve entrypoint ─────
    python_end_snippet: str | None = None
    for snippet in problem_data.get("codeSnippets", []):
        if isinstance(snippet, dict) and snippet.get("language", "").lower() == "python":
            python_end_snippet = snippet.get("endSnippet")
            break

    # ── 2. Run each test case ─────────────────────────────────────────────────
    valid: list[dict] = []

    for idx, tc in enumerate(test_cases):
        raw_input: str = tc.get("input", "")
        expected: str = tc.get("output", "").strip()

        # After json.loads the \n sequences are already real newlines, but guard
        # against the rare case where the AI double-escaped them.
        if "\\n" in raw_input and "\n" not in raw_input:
            raw_input = raw_input.replace("\\n", "\n")

        actual = _run_code(_ensure_entrypoint(reference_code, python_end_snippet), raw_input)

        if actual is None:
            logger.warning(
                f"[Validator] Test case {idx}: reference script failed to run — dropping."
            )
            continue

        if _normalize(actual) == _normalize(expected):
            logger.info(
                f"[Validator] Test case {idx} ✓  "
                f"expected={expected!r}  actual={actual!r}"
            )
            valid.append(tc)
        else:
            logger.warning(
                f"[Validator] Test case {idx} ✗  "
                f"expected={expected!r}  actual={actual!r} — dropping."
            )

    # ── 3. Guard: don't save a problem with zero verified test cases ──────────
    if len(valid) == 0:
        raise BaseError(
            502,
            "All generated test cases have incorrect expected outputs. Please retry.",
            f"Reference solution disagreed with all {len(test_cases)} expected outputs.",
        )

    if len(valid) < len(test_cases):
        logger.warning(
            f"[Validator] {len(test_cases) - len(valid)} test case(s) dropped. "
            f"{len(valid)} valid case(s) will be saved."
        )
    else:
        logger.info(f"[Validator] All {len(valid)} test case(s) passed validation ✓")

    problem_data["testCases"] = valid
    return problem_data
