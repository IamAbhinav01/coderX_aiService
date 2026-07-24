import subprocess
from validations.pydanticValidation import GeneratedProblemRaw
import json
import sys

def test_cases_output(rawProblem: GeneratedProblemRaw) -> list:

    validated_testCases = []

    for case in rawProblem.testCaseInputs:
        input_str = case.input if isinstance(case.input,str) else json.dumps(case.input)
        try:
            process = subprocess.Popen(
                 [sys.executable, "-c", rawProblem.reference_solution],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout,stderr = process.communicate(input_str,timeout=2.0)
            validated_testCases.append({
                "input":input_str,
                "output":stdout.strip()
            })

        except subprocess.TimeoutExpired:
            process.kill()
            raise TimeoutError("Reference solution timed out during evaluation.")
        
    return validated_testCases