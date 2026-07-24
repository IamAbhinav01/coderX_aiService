from config.groqClient import client
from config.serverConfig import ServerConfig
from validations.pydanticValidation import GeneratedProblemRaw
import json
import subprocess
import sys
import re

groq_client = client

def clean_code(code: str) -> str:
    code = code.strip()
    
    # Strip markdown code blocks
    code = re.sub(r"^```(?:python|py)?\s*", "", code)
    code = re.sub(r"\s*```$", "", code)
    
    # Strip triple quotes if code is wrapped as a docstring
    if (code.startswith("'''") and code.endswith("'''")) or (code.startswith('"""') and code.endswith('"""')):
        code = code[3:-3].strip()
        
    return code.strip()

def verify_solution(raw_problem: GeneratedProblemRaw) -> str:
    """Runs the reference solution against the testcase inputs.
    Returns None if successful, or the error message string if it fails.
    """
    outputs = set()
    for index, case in enumerate(raw_problem.testCaseInputs):
        input_str = case.input if isinstance(case.input, str) else json.dumps(case.input)
        try:
            process = subprocess.Popen(
                [sys.executable, "-c", raw_problem.reference_solution],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(input_str, timeout=3.0)
            if process.returncode != 0:
                return f"Test Case {index + 1} failed execution. Exit code: {process.returncode}. Error:\n{stderr.strip()}"
            
            # Verify the output is valid JSON
            try:
                json.loads(stdout.strip())
            except Exception as json_err:
                return f"Test Case {index + 1} output is not valid JSON. Output:\n{stdout.strip()}\nParsing error: {json_err}"
            
            outputs.add(stdout.strip())
                
        except subprocess.TimeoutExpired:
            process.kill()
            return f"Test Case {index + 1} execution timed out (limit: 3.0s)."
        except Exception as e:
            return f"Test Case {index + 1} execution raised an exception: {e}"
            
    # Check if all test cases return the exact same output (e.g. all 0, all False)
    # Only enforce this if there is more than 1 test case generated
    if len(raw_problem.testCaseInputs) > 1 and len(outputs) == 1:
        return f"All generated test cases returned the exact same output: {list(outputs)[0]}. This represents extremely weak test coverage. Please generate more diverse and non-trivial test cases."
        
    return None

def generate_problem(prompt : str)->GeneratedProblemRaw:
    system_instruction = """You are a competitive programming designer.
    Generate a coding challenge based on the user request.
    Always output JSON matching the provided schema.
    
    The reference_solution MUST be a complete, self-contained Python 3 script.
    The script MUST:
    1. Define any necessary helper classes (such as ListNode, TreeNode, etc.) if the problem uses them.
    2. Implement the solution logic function.
    3. Implement a `build_input(raw)` function that converts the raw JSON/dict/array input (received from stdin) into whatever native structure the solution logic function expects.
    4. Implement a `serialize_output(result)` function that converts the solution function's return value back into plain, standard JSON-serializable types (such as str, int, bool, list, dict — no custom objects).
    5. Include an `if __name__ == "__main__":` block at the bottom that reads the JSON test case input from standard input (stdin) using `sys.stdin.read()`, deserializes it using `json.loads()`, calls `build_input()`, calls the solution function, calls `serialize_output()`, and prints the serialized result using `print(json.dumps(output))`. Nothing else must be printed.
    Ensure that the reference_solution is valid, runnable Python code. DO NOT wrap it in extra comments or block quotes (like single quotes or double quotes).
    
    Provide 3 to 5 realistic, diverse, and robust input cases in testCaseInputs.
    Requirements for testCaseInputs:
    - They must cover diverse scenarios (e.g. standard inputs, edge cases, boundary conditions).
    - They MUST NOT all produce the same trivial output (such as all returning 0, empty list, None, or False).
    - At least some cases must require executing the non-trivial/main logic paths of the solution (e.g., in knapsack, items must fit and be selected to maximize value, resulting in positive non-zero outputs).
    - Ensure all lists, arrays, or objects in the inputs contain actual comma-separated values (e.g., `[1, 3, 4, 5]` instead of a single contiguous number like `[1345]`).
    - Each item in testCaseInputs must contain an 'input' field representing the raw JSON input to be passed to the harness. E.g. for a linked list, pass a clean structure like: {"values": [3, 2, 0, -4], "pos": 1}.
    
    Generate starter code templates in codeSnippets for all supported languages: python, java, and cpp.
    
    Starter code template guidelines:
    - For C++ (cpp): Include standard competitive programming headers (e.g., `#include <bits/stdc++.h>`) and standard namespaces/libraries.
    - For Java (java): Include common standard library imports (e.g., `import java.util.*;` and `import java.io.*;`).
    
    Make sure each item in the codeSnippets array is a valid CodeSnippet object containing all required fields: 'language', 'startSnippet', 'midSnippet', and 'endSnippet'. Do not include raw strings or empty items in the codeSnippets array.
    """

    config = ServerConfig()
    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": prompt}
    ]
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=config["GROQ_MODEL"],
                temperature=config["TEMPERATURE"],
                max_tokens=config["GROQ_MAX_TOKENS"],
                messages=messages,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "GenerateCodingQuestionRAW",
                        "schema": GeneratedProblemRaw.model_json_schema()
                    }
                }
            )
        except Exception as e:
            error_msg = str(e)
            if "response_format" in error_msg or "json_schema" in error_msg:
                # Fallback to json_object mode
                schema_json = json.dumps(GeneratedProblemRaw.model_json_schema(), indent=2)
                fallback_system_instruction = system_instruction + f"\n\nYou MUST respond with valid JSON matching the following JSON Schema:\n{schema_json}"
                
                fallback_messages = [
                    {"role": "system", "content": fallback_system_instruction}
                ] + messages[1:]
                
                response = client.chat.completions.create(
                    model=config["GROQ_MODEL"],
                    temperature=config["TEMPERATURE"],
                    max_tokens=config["GROQ_MAX_TOKENS"],
                    messages=fallback_messages,
                    response_format={"type": "json_object"}
                )
            else:
                raise e
                
        raw_content = response.choices[0].message.content or "{}"
        try:
            raw_json = json.loads(raw_content)
            raw_problem = GeneratedProblemRaw.model_validate(raw_json)
            raw_problem.reference_solution = clean_code(raw_problem.reference_solution)
        except Exception as parse_error:
            if attempt == max_retries - 1:
                raise parse_error
            messages.append({"role": "assistant", "content": raw_content})
            messages.append({"role": "user", "content": f"The response was invalid JSON or did not match the Pydantic schema. Error:\n{parse_error}\nPlease output a valid JSON matching the schema."})
            continue
            
        validation_error = verify_solution(raw_problem)
        if validation_error is None:
            return raw_problem
            
        if attempt == max_retries - 1:
            raise RuntimeError(f"Failed to generate a working reference solution after {max_retries} attempts. Last error:\n{validation_error}")
            
        print(f"[Attempt {attempt + 1}] Reference solution failed verification: {validation_error}. Retrying...")
        messages.append({"role": "assistant", "content": raw_content})
        feedback = f"""Verification failed for the generated reference_solution.
Error Details:
{validation_error}

Please fix the reference_solution code. Make sure that:
1. Any block quotes (like triple single quotes or triple double quotes) wrapping the script are removed.
2. Stdin reading and JSON loading match the exact shape of inputs.
3. The script is fully working and standalone.
"""
        messages.append({"role": "user", "content": feedback})
