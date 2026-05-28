from langchain_core.prompts import PromptTemplate

problem_prompt_template = """You are an expert competitive-programming problem setter for CoderX. Your task is to generate exactly ONE highly structured, original coding problem based on the given topic and difficulty, formatted as a single, production-ready JSON object.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INPUT VARIABLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Topic:      {topic}
  Difficulty: {difficulty}   (must be one of: easy | medium | hard)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PART 1 — MANDATORY PRE-GENERATION SCRATCHPAD  (DO THIS BEFORE WRITING JSON)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You MUST complete all 8 steps below mentally before emitting any JSON. Skipping even one step will produce broken test cases or runner code.

STEP 1 — Design the problem & define the EXACT stdin format
  • Write out the complete specification of what each line of stdin contains.
  • Example A (single array):
        Line 1: integer n
        Line 2: n space-separated integers
  • Example B (two arrays):
        Line 1: integer n (length of array A)
        Line 2: n space-separated integers (array A)
        Line 3: integer m (length of array B)
        Line 4: m space-separated integers (array B)
  • If the problem needs multiple arrays, EVERY array MUST be preceded by its own length on a separate line — even if you could infer the length from context.
  • Write this stdin spec down. You will reuse it verbatim in the description and in all code snippets.

STEP 2 — Write the complete, correct reference Python solution
  • Use concrete variable names. No pseudocode.
  • The stdin-parsing section must follow the EXACT format you defined in Step 1.

STEP 3 — Construct Test Case 0 (Happy Path)
  a) Choose a small, interesting input (4–8 elements per array).
  b) Write out every line of the input string, one token per line, following Step 1's format.
  c) TOKEN-COUNT CHECK: count the number of integers you declared in any length-lines and verify that exactly that many integers appear on the corresponding data-line. Fix any mismatch before continuing.
  d) Trace the reference solution line-by-line with this input and record the exact output string.

STEP 4 — Construct Test Case 1 (Edge Case)
  a) Choose a meaningful edge case (n=1, all-negative, identical elements, or empty sub-array).
  b) Repeat steps 3b, 3c, 3d for this input.

STEP 5 — Construct Test Case 2 (Moderate Stress)
  a) Choose a moderate input (30 ≤ n ≤ 50) with a predictable pattern (e.g., 1…n ascending) whose answer can be verified with a closed-form formula.
  b) Repeat steps 3b, 3c, 3d for this input. Compute the expected output mathematically and verify it matches the solution.

STEP 6 — Cross-Consistency Check
  • All three outputs must be produced by the SAME reference solution.
  • Re-read each input string character-by-character and confirm it parses cleanly in your Python snippet's main block with zero IndexError / ValueError risk.

STEP 7 — Code Snippet Verification
  For every language (Python, Java, C++):
    • The stdin-parsing logic must follow the EXACT same line-by-line format defined in Step 1.
    • If Step 1 says "Line 3 is an integer m", then your parser must call a separate read for m before reading array B.
    • The solve() function signature, parameter types, and return type must be identical across all three languages.

STEP 8 — Example Section Match Check
  • The input/output values shown in the description's "### Examples" section must be byte-for-byte identical to the raw values in testCases[0], testCases[1], and testCases[2].

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PART 2 — JSON OUTPUT CONTRACT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Output EXACTLY one raw JSON object. Rules:

  ✗ Do NOT wrap in markdown fences (```json … ```).
  ✗ Do NOT include any text before {{ or after }}.
  ✓ The first character must be {{ and the last must be }}.

NEWLINE ESCAPING (CRITICAL — failure here causes JSON decode errors):
  • Every newline inside a JSON string value MUST be the two-character escape sequence \\n.
  • WRONG  →  "input": "2\\n1 3\\n2 4"   (if there are actually raw newlines)
  • CORRECT → "input": "2\\n1 3\\n2\\n2 4"   (each logical line separated by \\n)
  • Every " inside a string must be escaped as \\".
  • Every \\ inside a string must be escaped as \\\\.

REQUIRED TOP-LEVEL KEYS (exactly 6, in this order):
  "title", "difficulty", "testCases", "description", "codeSnippets", "editorial"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PART 3 — DEEP DIVE INTO EACH JSON KEY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. "title"
   A catchy competitive-programming title of 3–7 words. Must NOT be a generic name like "Array Problem".

2. "difficulty"
   Lowercase string exactly matching the input variable: easy | medium | hard.

3. "testCases"
   An array of EXACTLY 3 objects. Each object has exactly two keys:

   "input"
     • Raw stdin text with lines separated by \\n (the two-character escape).
     • ABSOLUTELY NO square brackets [], curly braces, or commas unless the problem explicitly uses CSV format.
     • ABSOLUTELY NO natural-language labels like "array1 = ".
     • If a data line contains n integers, the line immediately before it must be a line containing just n.
     • MULTI-ARRAY RULE: for EVERY array that the problem reads, its length n MUST appear on its own \\n-separated line immediately before the array's data line — even if the problem gives both arrays the same length.
       ✗ WRONG  (two arrays, only one length line): "2\\n1 3\\n2 4"
       ✓ CORRECT (two arrays, two length lines):    "2\\n1 3\\n2\\n2 4"

   "output"
     • The exact stdout the reference solution produces for this input.
     • No trailing spaces. No extra newlines beyond what print() naturally emits.
     • BOOLEAN OUTPUTS: If the answer is a boolean, ALWAYS write it as lowercase "true" or "false" — NEVER Python-style "True" or "False". This applies regardless of which language the reference solution uses, because the judge normalises across Python (True/False), C++ (true/false), and Java (true/false).

4. "description"
   A Markdown string (all newlines as \\n) with EXACTLY these four sections in order:

   ### Problem Statement
   3–5 plain-English sentences. State what the input format is (reference Step 1's spec word-for-word), what must be computed, and what should be printed.

   ### Examples
   For each of the 3 test cases:

     Example N:
     Input:
     <paste testCases[N-1].input exactly, but with \\n rendered as actual newlines for readability>
     Output: <paste testCases[N-1].output exactly>
     Explanation: <one-sentence walkthrough>

   Rule: Do NOT wrap input/output in backtick fences.

   ### Constraints
   • Bullet points for the bounds of n and element values.
   • Explicitly state expected Big-O complexity (e.g., "An O(N log N) solution is expected.").

   ### Function Signature
   def solve(<params: types>) -> <return type>:

   This signature must exactly match the Python startSnippet.

5. "codeSnippets"
   An array of EXACTLY 3 objects, in this order: python, java, cpp.
   Each object has exactly 4 keys: "language", "startSnippet", "midSnippet", "endSnippet".

   ── Python ──
   startSnippet : Import statements, type hints, and the `def solve(…) -> …:` line.
   midSnippet   : Exactly this two-line placeholder:
                    # User code goes here
                    pass
   endSnippet   : A complete `if __name__ == "__main__":` block that:
                    • Reads stdin following Step 1's line-by-line format EXACTLY.
                      - Each array length is read with int(input()) on its own line.
                      - Each array's data is read with list(map(int, input().split())) on the next line.
                    • Calls solve() with the parsed arguments.
                    • Prints the result with print().

   ── Java ──
   startSnippet : All imports (java.util.*; java.io.*;), then:
                    class Solution {{ public <ReturnType> solve(<params>) {{
   midSnippet   : Placeholder comment + default return statement.
   endSnippet   : Closing `}}` of solve(), closing `}}` of Solution class, then a separate
                    class Main {{ public static void main(String[] args) throws IOException {{ … }} }}
                  that parses stdin using BufferedReader following Step 1's format, calls
                  new Solution().solve(…), and prints the result.

   ── C++ ──
   startSnippet : #include <bits/stdc++.h> and using namespace std;, then:
                    <ReturnType> solve(<params>) {{
   midSnippet   : Placeholder comment + default return statement.
   endSnippet   : Closing `}}` of solve(), then a complete int main() {{ … }} with:
                    • ios::sync_with_stdio(false); cin.tie(nullptr);
                    • Parsing following Step 1's format — each array length read separately with `cin >> n;`
                      before reading n elements.
                    • Calling solve() and printing the result.
                    • CRITICAL — newlines in output: ALWAYS write `"\n"` (double-quoted string).
                      NEVER write `'\n'` (single-quoted char literal). Single-quoted newlines
                      are corrupted during JSON serialization and cause a compile error.
                      ✗ WRONG:   cout << solve(…) << '\n';
                      ✓ CORRECT: cout << solve(…) << "\n";

6. "editorial"
   A Markdown string (all newlines as \\n) with EXACTLY these 5 sections in order:

   ### Intuition
   2–3 sentences: the core observation and why brute force fails.

   ### Approach
   Algorithm name as a sub-header, then 3–5 sentences on the optimal strategy. No code.

   ### Algorithm Steps
   Numbered list referencing exact variable names from the reference solution.

   ### Complexity Analysis
   A Markdown table:
   | Complexity | Value | Justification |
   |------------|-------|---------------|
   | Time       | O(…)  | one sentence  |
   | Space      | O(…)  | one sentence  |

   ### Reference Implementation
   A markdown fenced code block (```python … ```) with the verified reference solution from Step 2.
"""

problem_prompt = PromptTemplate(
    template=problem_prompt_template,
    input_variables=["topic", "difficulty"],
)