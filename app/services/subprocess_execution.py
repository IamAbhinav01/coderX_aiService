import subprocess
from validations.pydanticValidation import GeneratedProblemRaw
from groq_service import generate_problem
import json
import sys

def test_cases_output(rawProblem: GeneratedProblemRaw) -> list:

    validated_testCases = []

    for case in rawProblem.testCaseInputs:
        input_str = case.input if isinstance(case.input, str) else json.dumps(case.input)
        try:
            process = subprocess.Popen(
                [sys.executable, "-c", rawProblem.reference_solution],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate(input_str, timeout=2.0)
            validated_testCases.append({
                "input": input_str,
                "output": stdout.strip()
            })

        except subprocess.TimeoutExpired:
            process.kill()
            raise TimeoutError("Reference solution timed out during evaluation.")
        
    return validated_testCases

def create_aligned_problem(user_prompt: str):

    raw_problem = generate_problem(user_prompt)
    
    
    test_cases = test_cases_output(raw_problem)
    
   
    final_payload = {
        "title": raw_problem.title,
        "description": raw_problem.description,
        "difficulty": raw_problem.difficulty.value,
        "testCases": test_cases,
        "codeSnippets": [
            {
                "language": snippet.language.value,
                "startSnippet": snippet.startSnippet,
                "midSnippet": snippet.midSnippet,
                "endSnippet": snippet.endSnippet
            } for snippet in raw_problem.codeSnippets
        ],
        "editorial": f"### Optimal Solution Walkthrough\n\n```python\n{raw_problem.reference_solution}\n```",
        "topic": raw_problem.topic
    }
    
    return final_payload
