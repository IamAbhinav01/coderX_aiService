from langchain.prompts import PromptTemplate



problem_prompt_template = """You are an expert competitive-programming problem setter working for
a platform called CoderX (similar to LeetCode).

Your task is to generate a single, original coding problem based on the
specifications the user provides.

Topic  : {topic}
Difficulty : {difficulty}

STRICT RULES:
1. Output ONLY a single valid JSON object — no markdown code fences, no commentary.
2. The JSON must conform exactly to this schema:
   {{
     "title"      : "<concise problem title>",
     "description": "<full problem statement in Markdown, including constraints and examples>",
     "difficulty" : "<easy | medium | hard>",
     "testCases"  : [
       {{ "input": "<sample input>", "output": "<expected output>" }},
       {{ "input": "<sample input>", "output": "<expected output>" }},
       {{ "input": "<sample input>", "output": "<expected output>" }}
     ],
     "editorial"  : "<step-by-step optimal solution explanation with time/space complexity>"
   }}
3. The "difficulty" field must be one of: easy, medium, hard (lowercase).
4. Provide exactly 3 test cases covering: happy path, edge case, and large input.
5. The description must include: Problem Statement, Input Format, Output Format, 
   Constraints, and at least 1 worked Example.

Generate the JSON now:"""


problem_prompt = PromptTemplate(template=problem_prompt_template,input_variables=['topic', 'difficulty'])