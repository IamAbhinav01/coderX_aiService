from langchain_core.prompts import PromptTemplate

problem_prompt_template = """You are an expert competitive-programming problem setter for CoderX, a platform similar to LeetCode.

Generate ONE completely original coding problem matching the specification below.

Topic      : {topic}
Difficulty : {difficulty}

══════════════════════════════════════════════════════════════
MANDATORY OUTPUT RULES  —  read every rule before generating
══════════════════════════════════════════════════════════════

RULE 1 — Output format
  Output a SINGLE valid JSON object.
  No markdown fences around the JSON. No text before or after it.

RULE 2 — JSON must contain EXACTLY these six keys:

  title
  description
  difficulty
  testCases
  codeSnippets
  editorial

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE 3 — "title"
  A short, catchy problem title (3–7 words).
  Example: "Find the Missing Number"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE 4 — "description"
  Value is a Markdown string. Escape every newline as \n inside the JSON string.
  Use EXACTLY these four sections in this order:

  SECTION 1 — Problem Statement
    ## Problem Statement
    [3–5 sentences in plain English. Define the task clearly.
     State what the input is, what must be computed, and what to return.]

  SECTION 2 — Examples
    ## Examples
    [Copy the input/output values DIRECTLY from your testCases array — keep them identical.]
    [Do NOT wrap input/output values in triple backtick fences here.]
    [Format each example exactly like this:]

    **Example 1:**
    - Input: [plain text — same string as testCases[0].input]
    - Output: [plain text — same string as testCases[0].output]
    - Explanation: [one sentence walkthrough]

    **Example 2:**
    - Input: [plain text — same string as testCases[1].input]
    - Output: [plain text — same string as testCases[1].output]
    - Explanation: [one sentence walkthrough]

    **Example 3:**
    - Input: [plain text description of testCases[2] — do NOT paste thousands of numbers]
    - Output: [expected output]
    - Explanation: [one sentence about what this stress case tests]

  SECTION 3 — Constraints
    ## Constraints
    - `1 ≤ n ≤ ...`
    - `-10^9 ≤ A[i] ≤ 10^9`
    - [One line stating the expected time complexity, e.g. "An O(n) solution is expected."]

  SECTION 4 — Function Signature
    ## Function Signature
```python
    def solve(...) -> ...:
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE 5 — "difficulty"
  Must be exactly one of (lowercase):  easy  |  medium  |  hard

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE 6 — "testCases"
  A JSON array of EXACTLY 3 objects. Each object: {{"input": "...", "output": "..."}}

  IMPORTANT — input and output values must be PLAIN STRINGS:
    WRONG : "input": "```\\n8\\n5 1 4 3\\n```"   ← NO backtick fences inside values
    CORRECT: "input": "8\\n5 1 4 3"               ← plain text only

  - Index 0: Typical happy-path. Small, human-readable numbers.
  - Index 1: Edge case (n=1, all equal values, all negative, boundary).
  - Index 2: Large/stress case described in plain text.
             Example: "n=100000, array is 1 to 100000 in ascending order"

             
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE 7 — "codeSnippets" (Evaluator Service Format)
Return 3 objects (python, java, cpp). 

For each language, provide:
1. "startSnippet": Includes imports, class header, and the function signature. The function MUST take strongly typed arguments (e.g., arrays, integers, strings), NOT a single raw combined string.
2. "midSnippet": This is a placeholder or a default "return 0" that my service replaces with the user's logic.
3. "endSnippet": Includes the closing braces for the function/class AND the driver code. The driver code MUST read the plain text input from standard input (stdin / sys.stdin / Scanner), parse it into the strongly typed variables required by the function signature, call the function, and print the formatted output.

Example for C++:
"codeSnippets": [
  {{
    "language": "cpp",
    "startSnippet": "#include <bits/stdc++.h>\\nusing namespace std;\\n\\nclass Solution {{\\npublic:\\n    vector<int> solve(int n, vector<int>& arr) {{",
    "midSnippet": "        // Write your logic here\\n        return {{}};",
    "endSnippet": "    }}\\n}};\\n\\nint main() {{\\n    ios::sync_with_stdio(false);\\n    cin.tie(nullptr);\\n    int n;\\n    if (!(cin >> n)) return 0;\\n    vector<int> arr(n);\\n    for(int i=0; i<n; i++) cin >> arr[i];\\n    vector<int> res = Solution().solve(n, arr);\\n    for(int x : res) cout << x << \\" \\";\\n    cout << \\"\\\\n\\";\\n    return 0;\\n}}"
  }}
]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE 8 — "editorial"
  Value is a Markdown string. Escape every newline as \n inside the JSON string.
  Use EXACTLY these five sections in this order:

  SECTION 1 — Intuition
    ## Intuition
    [2–3 sentences. What key observation makes this solvable efficiently?
     Why does the brute force fail? What pattern or data structure helps?]

  SECTION 2 — Approach
    ## Approach
    **[Algorithm name, e.g. Monotonic Stack / Two Pointers / Binary Search]**
    [3–5 sentences explaining the method conceptually. No code yet.]

  SECTION 3 — Algorithm
    ## Algorithm
    1. [Step 1 — specific, mention variable names]
    2. [Step 2]
    3. [Step 3]
    4. [Final step — what is returned?]

  SECTION 4 — Complexity Analysis
    ## Complexity Analysis
    | | Complexity | Reason |
    |---|---|---|
    | **Time**  | O(...) | [one-line justification] |
    | **Space** | O(...) | [one-line justification] |

  SECTION 5 — Reference Implementation
    ## Reference Implementation
```python
    [Complete, correct, clean Python solution.
     Meaningful variable names. Comment every non-obvious line.]
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SELF-CHECK — before outputting, verify every point:

  [ ] Output is a raw JSON object — no fences, no extra text outside it
  [ ] All 6 keys present: title, description, difficulty, testCases, codeSnippets, editorial
  [ ] testCases has EXACTLY 3 items
  [ ] testCases input/output values are plain strings — NO triple backtick fences inside them
  [ ] description examples match testCases values exactly
  [ ] code snippets are included for Python, Java, and Cpp, with start and end snippets
  [ ] editorial has all 5 sections and is NOT empty
  [ ] difficulty is one of: easy | medium | hard
  [ ] Every newline inside JSON string values is escaped as \\n

══════════════════════════════════════════════════════════════
Generate the JSON now:"""

problem_prompt = PromptTemplate(
    template=problem_prompt_template,
    input_variables=["topic", "difficulty"],
)