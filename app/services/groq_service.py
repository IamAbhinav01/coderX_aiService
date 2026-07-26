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
    multi_element_cases = 0

    for index, case in enumerate(raw_problem.testCaseInputs):
        # Programmatically check input quality for arrays
        inp = case.input
        if isinstance(inp, dict):
            for k, v in inp.items():
                if isinstance(v, list):
                    if len(v) >= 2:
                        multi_element_cases += 1
                    elif len(v) == 1 and isinstance(v[0], int) and v[0] > 9:
                        return f"Test Case {index + 1} parameter '{k}' contains a concatenated single number [{v[0]}] instead of a multi-element array like [1, 4, 3, 2, 5, 2]. You MUST separate numbers into individual list elements."
        elif isinstance(inp, list):
            if len(inp) >= 2:
                multi_element_cases += 1
            elif len(inp) == 1 and isinstance(inp[0], int) and inp[0] > 9:
                return f"Test Case {index + 1} contains a concatenated single number [{inp[0]}] instead of a multi-element array like [1, 4, 3, 2, 5, 2]. You MUST separate numbers into individual list elements."

        input_str = json.dumps(case.input) if not isinstance(case.input, str) else case.input
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
            
            try:
                actual_res = json.loads(stdout.strip())
            except Exception as json_err:
                return f"Test Case {index + 1} output is not valid JSON. Output:\n{stdout.strip()}\nParsing error: {json_err}"

            if case.expected_output is not None:
                exp_res = case.expected_output
                if json.dumps(actual_res, sort_keys=True) != json.dumps(exp_res, sort_keys=True):
                    return f"Test Case {index + 1} expected output ({exp_res}) does NOT match actual reference solution execution output ({actual_res}). Reference solution logic and test case expected outputs must be aligned."

            outputs.add(stdout.strip())
                
        except subprocess.TimeoutExpired:
            process.kill()
            return f"Test Case {index + 1} execution timed out (limit: 3.0s)."
        except Exception as e:
            return f"Test Case {index + 1} execution raised an exception: {e}"
            
    if len(raw_problem.testCaseInputs) >= 3 and multi_element_cases < 2:
        return "Test cases lack multi-element inputs. At least 2 or 3 test cases must provide lists/arrays with 3 to 6 separate elements (e.g. [1, 4, 3, 2, 5, 2])."

    if len(raw_problem.testCaseInputs) >= 3 and len(outputs) < 2:
        return f"All generated test cases returned weak outputs with insufficient diversity ({list(outputs)}). Please generate more diverse test cases where at least 2 cases return distinct non-zero results."
        
    return None

def generate_problem(prompt : str)->GeneratedProblemRaw:
    system_instruction = """You are an expert competitive programming problem designer.
    Generate a complete, high-quality coding challenge based on the user request.
    Always output JSON matching the provided schema.
    
    CRITICAL RULES FOR DYNAMIC INPUTS & NO HARDCODING:
    1. NEVER HARDCODE ANY PARAMETERS or variables (such as target values, partition pivots x, k, target, etc.) inside the reference_solution script!
    2. All problem parameters MUST be passed dynamically through each test case in `testCaseInputs`.
    3. If the problem takes MULTIPLE arguments (e.g. `head` and `x`, or `nums` and `target`, or `grid` and `k`), each item in `testCaseInputs` MUST have its 'input' field formatted as a JSON Object with explicit key names matching all parameters.
       Examples:
       - Multi-parameter LinkedList: `{"list": [1, 4, 3, 2, 5, 2], "x": 3}`
       - Multi-parameter Array: `{"nums": [2, 7, 11, 15], "target": 9}`
       - Single-parameter Array: `{"height": [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]}`
    4. ARRAY FORMATTING (STRICT): Arrays MUST contain multiple separate elements (e.g., `[1, 4, 3, 2, 5, 2]`). NEVER concatenate digits into a single number like `[143252]` or `[21]`. Each number in the array MUST be a separate integer in JSON!

    THE `reference_solution` SCRIPT RULES:
    The reference_solution MUST be a complete, self-contained, executable Python 3 script.
    The script MUST:
    1. Define any helper classes required by the problem (e.g., `class ListNode: def __init__(self, val=0, next=None): self.val = val; self.next = next`, `class TreeNode: ...`).
    2. Implement the solution logic function/class method.
    3. Implement a `build_input(raw)` function that dynamically converts the JSON raw input (read from stdin) into whatever arguments the solution function expects.
       - If `raw` is a dictionary containing named parameter keys (e.g., `{"list": [1, 4, 3, 2, 5, 2], "x": 3}`), `build_input(raw)` MUST extract all parameters dynamically from `raw` (e.g., `head_list = raw.get("list", raw.get("head"))`, `x = raw["x"]`), construct any helper data structures (like building a `ListNode` chain), and return a tuple of arguments `(head_node, x)`.
       - NEVER hardcode values like `x = 3` or `target = 9` inside `build_input` or solution methods!
    4. Implement a `serialize_output(result)` function that converts the solution function's return value back into standard JSON-serializable types (e.g., converting a `ListNode` head back to a Python list `[1, 2, 2, 4, 3, 5]`, or converting custom objects to plain lists/ints/dicts).
    5. Include an `if __name__ == "__main__":` block at the bottom:
       ```python
       if __name__ == "__main__":
           raw = json.loads(sys.stdin.read())
           parsed_args = build_input(raw)
           solution = Solution()
           if isinstance(parsed_args, tuple):
               result = solution.solve(*parsed_args)
           elif isinstance(parsed_args, dict):
               result = solution.solve(**parsed_args)
           else:
               result = solution.solve(parsed_args)
           output = serialize_output(result)
           print(json.dumps(output))
       ```

    FEW-SHOT EXAMPLES OF GOOD MULTI-ELEMENT TEST CASES:
    For a Partition List around x problem:
    - Case 1: `{"input": {"list": [1, 4, 3, 2, 5, 2], "x": 3}}` -> Expected Output: `[1, 2, 2, 4, 3, 5]` (Standard case)
    - Case 2: `{"input": {"list": [2, 1], "x": 2}}` -> Expected Output: `[1, 2]` (Node movement case)
    - Case 3: `{"input": {"list": [4, 1, 5, 2, 3], "x": 3}}` -> Expected Output: `[1, 2, 4, 5, 3]` (Stability case)
    - Case 4: `{"input": {"list": [3, 3, 3, 1, 2], "x": 3}}` -> Expected Output: `[1, 2, 3, 3, 3]` (Duplicates case)
    - Case 5: `{"input": {"list": [], "x": 3}}` -> Expected Output: `[]` (Empty boundary case)

    STARTER CODE SNIPPETS (codeSnippets):
    Generate starter templates for python, java, and cpp.
    Make sure method signatures match the exact parameter names used in `testCaseInputs`.
    """

    config = ServerConfig()
    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": prompt}
    ]
    
    max_retries = 5
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
1. Any block quotes or indentation issues on imports are removed.
2. DO NOT HARDCODE ANY PARAMETER VALUES (such as x=3, target=9, k=2) inside the solution script or build_input!
3. All parameters MUST be extracted dynamically from `raw` inside `build_input(raw)` (e.g. `head_list = raw.get("list", raw.get("head"))`, `x = raw["x"]`).
4. `testCaseInputs` must be structured JSON objects containing all parameter keys (e.g. `{{"list": [1, 4, 3, 2, 5, 2], "x": 3}}`) with comma-separated elements in arrays.
5. The script is fully runnable standalone.
"""
        messages.append({"role": "user", "content": feedback})
