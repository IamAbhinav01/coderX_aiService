from langchain_core.prompts import PromptTemplate

problem_prompt_template = """You are an expert competitive-programming problem setter for CoderX.

Generate ONE original coding problem for the given topic and difficulty.

Topic      : {topic}
Difficulty : {difficulty}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MANDATORY PRE-GENERATION SCRATCHPAD  (never appears in output)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You MUST mentally execute every step below before writing any JSON.
Skipping any step will produce wrong test cases.

STEP 1 — Write the reference Python solution in full, using concrete
  variable names. Do not write pseudocode.

STEP 2 — Choose test case 0 input values (small, 4–8 elements).
  Simulate the reference solution on those values line by line.
  Write down every intermediate variable. Record the final return value.
  That return value is testCases[0].output.

STEP 3 — Choose test case 1 input (a meaningful edge case: n=1,
  all identical values, all negatives, or single maximum element).
  Simulate the reference solution on it line by line.
  Record the final return value. That is testCases[1].output.

STEP 4 — Choose test case 2 input (a MODERATE stress case: n between
  100 and 1000, with a pattern like 1..n ascending, so the correct
  answer can be computed by a closed-form formula).
  Compute the output with the closed-form formula — show the arithmetic.
  Double-check: run the reference solution mentally or algebraically.
  Record the exact integer/string result. That is testCases[2].output.

STEP 5 — Verify all three outputs are self-consistent with the
  reference solution and with each other. If any output is uncertain,
  REDO that step until certain.

STEP 6 — Verify that the description Examples section is word-for-word
  identical to the testCases input/output values.

Only after STEPS 1-6 are complete, write the JSON.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT CONTRACT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Output ONE raw JSON object — no markdown fences, no text before or after.
The JSON must pass json.loads() without any pre-processing.
Every newline inside a JSON string value  →  escape as \\n
Every double-quote inside a JSON string  →  escape as \\"
Every backslash inside a JSON string     →  escape as \\\\

The object must have EXACTLY these 6 top-level keys:
  "title"         string
  "description"   string  (Markdown, all newlines escaped as \\n)
  "difficulty"    string
  "testCases"     array   (EXACTLY 3 objects)
  "codeSnippets"  array   (EXACTLY 3 objects)
  "editorial"     string  (Markdown, all newlines escaped as \\n)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KEY — "title"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
A short, catchy problem name: 3–7 words.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KEY — "difficulty"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Exactly one of (lowercase):  easy | medium | hard
Must equal: {difficulty}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KEY — "testCases"   ★ MOST CRITICAL SECTION ★
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
An array of EXACTLY 3 objects.
Every object has EXACTLY 2 keys:
  "input"   string  —  the raw text fed to the program's stdin
  "output"  string  —  the exact text the program must print to stdout

ALL THREE test cases use this same structure.
ALL THREE inputs are real, concrete stdin strings — not descriptions,
not placeholders, not sentences like "n=100000 ascending".

── INPUT STRING FORMAT ──────────────────────────────────────────────
The input string format MUST exactly match what the driver code reads.
  ✗  NO brackets:  [ ]  or  ( )
  ✗  NO commas
  ✗  NO Python / Java / C++ syntax
  ✗  NO natural-language descriptions
  ✓  Integers separated by spaces on one line
  ✓  Multiple lines separated by the escape sequence  \\n
  ✓  If the problem reads n then an array:  first line is n,
     second line is n space-separated integers

  CORRECT:  "5\\n3 1 4 1 5"
  WRONG:    "5\\n[3, 1, 4, 1, 5]"
  WRONG:    "n=5, array is 1 to 5 ascending"

── OUTPUT STRING FORMAT ─────────────────────────────────────────────
The output string must be the EXACT stdout the correct program prints.
  • Single integer answer  →  just that integer as a string, e.g. "42"
  • Multiple values        →  space-separated or newline-separated,
                               matching what the driver prints
  • No trailing spaces. No extra newlines beyond what the driver emits.

── CORRECTNESS REQUIREMENT — THIS IS NON-NEGOTIABLE ────────────────
Every output value must be provably correct.

  testCases[0].output  —  obtained by manually simulating the reference
    solution step by step on testCases[0].input. Show every variable in
    the SCRATCHPAD. No guessing.

  testCases[1].output  —  same: step-by-step simulation on testCases[1].
    input in the SCRATCHPAD. No guessing.

  testCases[2].output  —  testCases[2] uses a MODERATE input (n = 100
    to 1000) with a predictable pattern (e.g. 1..n ascending) so the
    correct answer can be derived by a closed-form formula.
    In the SCRATCHPAD: write the formula, substitute n, compute the
    exact integer. That integer is testCases[2].output.
    DO NOT use large n (100000+) — keep it computable and embeddable.

  THE GOLDEN RULE:
  If you are not 100% certain what the output is, make the input
  simpler until you ARE certain. A correct small test beats a wrong
  large one every time.

── TEST CASE ROLES ──────────────────────────────────────────────────
  testCases[0]  Typical happy-path. Small input, 4–8 elements.
                Easy for a human to verify by hand.

  testCases[1]  Meaningful edge case. Choose ONE of:
                  • n = 1  (single element)
                  • All elements identical
                  • All elements negative
                  • Minimum or maximum boundary value only

  testCases[2]  Moderate stress. n between 100 and 1000.
                Use a pattern whose answer follows a closed formula
                (e.g. consecutive integers, all same value).
                The full input string IS embedded in the JSON —
                keep it to at most ~50 numbers so it stays readable.
                If n > 50, describe the pattern in the SCRATCHPAD
                and embed only a representative prefix... actually
                for n > 50 choose n ≤ 50 for the stress case so the
                entire input fits cleanly in the JSON string.

  REVISED STRESS RULE: Keep testCases[2].n ≤ 50.
  Reason: the entire input must be a valid JSON string value.
  A stress test with n=50 and a closed-form answer is far better than
  a stress test with n=100000 and a guessed or wrong answer.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KEY — "description"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Markdown string. Escape every newline as \\n.
Exactly 4 sections in this order:


3–5 plain-English sentences describing the task.
State what the input is, what must be computed, and what to return.
No code. No formulas.



**Example 1:**
- Input: <paste testCases[0].input exactly — character for character>
- Output: <paste testCases[0].output exactly>
- Explanation: <one sentence walkthrough>

**Example 2:**
- Input: <paste testCases[1].input exactly — character for character>
- Output: <paste testCases[1].output exactly>
- Explanation: <one sentence walkthrough>

**Example 3:**
- Input: <paste testCases[2].input exactly — character for character>
- Output: <paste testCases[2].output exactly>
- Explanation: <one sentence: what does this case stress-test?>

RULES:
  • Do NOT wrap input/output values in backtick fences.
  • The input in Example N must be byte-for-byte identical to
    testCases[N-1].input. Any difference is a bug.


- `1 ≤ n ≤ <appropriate max>`
- `<element value range>`
- An O(<complexity>) solution is expected.


```python
def solve(<params: types>) -> <return type>:
```
This signature must be identical to the Python startSnippet's
function signature.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KEY — "codeSnippets"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Array of EXACTLY 3 objects in this order: python, java, cpp.
Each object has EXACTLY 4 keys:
  "language"     "python" | "java" | "cpp"
  "startSnippet" all imports + class header + opening of function
  "midSnippet"   placeholder body the service replaces with user code
  "endSnippet"   closing braces + complete driver / main block

DRIVER CODE RULES (endSnippet):
  • Reads stdin in the exact format of testCases[*].input.
  • Parses into correctly typed variables.
  • Calls solve() and prints the result.
  • Output must be character-for-character identical to
    testCases[*].output (same spacing, same newlines, no trailing spaces).

JAVA:
  • ALL import statements in startSnippet — none in endSnippet.
  • Class declaration: `class Solution`  (NOT public class Solution).
  • Driver in endSnippet: `class Main {{ public static void main(String[] args) }}`

PYTHON:
  • startSnippet ends on the `def solve(...):` line.
  • endSnippet is the complete `if __name__ == "__main__":` block.

C++:
  • startSnippet starts with `
  • endSnippet contains the complete `int main() {{ }}` block.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KEY — "editorial"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Markdown string. Escape every newline as \\n. Exactly 5 sections:


2–3 sentences: key observation, why brute-force fails, what helps.


**<Algorithm name>**
3–5 sentences explaining the approach. No code yet.


1. <Step with variable names>
2. ...
N. What is returned?


| | Complexity | Reason |
|---|---|---|
| **Time**  | O(...) | one-line reason |
| **Space** | O(...) | one-line reason |


```python





```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FINAL SELF-CHECK — tick every box before outputting
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
JSON shape
  [ ] Raw JSON object only — no fences, no surrounding text
  [ ] Exactly 6 top-level keys
  [ ] json.loads() succeeds without pre-processing

testCases
  [ ] Exactly 3 items, each with EXACTLY "input" and "output" keys
  [ ] All 3 inputs are concrete stdin strings — no sentences, no brackets
  [ ] testCases[0]: output verified by step-by-step simulation
  [ ] testCases[1]: output verified by step-by-step simulation
  [ ] testCases[2]: n ≤ 50; output verified by closed-form formula
  [ ] No [ ] brackets or commas in any input string
  [ ] Array lengths precede their element lines

description
  [ ] 4 sections in order: Problem Statement, Examples, Constraints,
      Function Signature
  [ ] Example 1 input/output = testCases[0] values verbatim
  [ ] Example 2 input/output = testCases[1] values verbatim
  [ ] Example 3 input/output = testCases[2] values verbatim
  [ ] No backtick fences around input/output values in Examples section

codeSnippets
  [ ] 3 snippets: python, java, cpp (in that order)
  [ ] Java: all imports in startSnippet; class is `class Solution`
  [ ] Driver parses stdin in the same format as testCases inputs
  [ ] Driver output format matches testCases output strings exactly

editorial
  [ ] 5 sections present and non-empty
  [ ] Reference Implementation is complete and correct for all 3 cases

Escaping
  [ ] All newlines in string values escaped as \\n
  [ ] All double-quotes in string values escaped as \\"
  [ ] All backslashes in string values escaped as \\\\

Generate the JSON now:"""

problem_prompt = PromptTemplate(
    template=problem_prompt_template,
    input_variables=["topic", "difficulty"],
)