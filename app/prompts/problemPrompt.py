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

RULE 2 — JSON must contain exactly these five keys:
  title  ·  description  ·  difficulty  ·  testCases  ·  editorial

RULE 3 — "title"
  A short, catchy problem title (3–7 words). Example: "Find the Missing Number"

RULE 4 — "description"   ← Markdown string; escape newlines as \n inside the JSON value
  Format the description EXACTLY with these sections in this order:

  ## 📋 Problem Statement\n[2–4 sentences that clearly define the task]\n\n## 📥 Input Format\n[bullet list of every input line / parameter]\n\n## 📤 Output Format\n[what must be printed or returned]\n\n## ⚙️ Constraints\n- `constraint 1`\n- `constraint 2`\n- (include time limit hint if relevant)\n\n## 💡 Example\n**Input:**\n```\n[sample input]\n```\n**Output:**\n```\n[expected output]\n```\n**Explanation:** [one sentence walking through the example]

RULE 5 — "difficulty"
  Must be exactly one of (lowercase, no surrounding quotes in value):  easy  |  medium  |  hard

RULE 6 — "testCases"   ← array of EXACTLY 3 objects: {{"input":"...","output":"..."}}
  - Index 0: typical happy-path case
  - Index 1: edge case  (e.g. empty input, single element, all-equal values, boundary value)
  - Index 2: large-input case — describe it in PLAIN TEXT, do NOT generate thousands of numbers.
             Example: "n=100000, array sorted ascending 1 to 100000, target=99999"

RULE 7 — "editorial"   ← Markdown string; escape newlines as \n inside the JSON value
  Format the editorial EXACTLY with these sections in this order:

  ## 🧠 Intuition\n[1–2 sentences on the key insight that makes this problem tractable]\n\n## 📐 Approach\n**[Algorithm / technique name]** — [2–3 sentences explaining the method]\n\n## 🔢 Algorithm\n1. [Step one]\n2. [Step two]\n3. [Continue until complete]\n\n## 💻 Reference Implementation\n```python\n[complete, clean, working Python solution with meaningful variable names]\n```\n\n## ⏱️ Complexity Analysis\n| | Complexity | Reason |\n|---|---|---|\n| **Time** | O(...) | [one-line justification] |\n| **Space** | O(...) | [one-line justification] |

══════════════════════════════════════════════════════════════
Generate the JSON now:"""


problem_prompt = PromptTemplate(
    template=problem_prompt_template,
    input_variables=["topic", "difficulty"],
)