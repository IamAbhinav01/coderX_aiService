import subprocess
from validations.pydanticValidation import GeneratedProblemRaw
from services.groq_service import generate_problem, clean_code
import json
import sys

def test_cases_output(rawProblem: GeneratedProblemRaw) -> list:

    validated_testCases = []

    for case in rawProblem.testCaseInputs:
        # Standardize input formatting to clean JSON
        if isinstance(case.input, str):
            try:
                parsed = json.loads(case.input)
                input_str = json.dumps(parsed)
            except Exception:
                input_str = case.input
        else:
            input_str = json.dumps(case.input)
        try:
            process = subprocess.Popen(
                [sys.executable, "-c", clean_code(rawProblem.reference_solution)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate(input_str, timeout=2.0)
            output = stdout.strip() if stdout else ""

            # Only append if execution succeeded and output is non-empty
            if process.returncode == 0 and output:
                validated_testCases.append({
                    "input": input_str,
                    "output": output
                })

        except Exception:
            if 'process' in locals() and process.poll() is None:
                process.kill()
            continue
        
    return validated_testCases

def create_aligned_problem(user_prompt: str, raw_problem: GeneratedProblemRaw = None):

    if raw_problem is None:
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
