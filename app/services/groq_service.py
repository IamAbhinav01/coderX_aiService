from config.groqClient import client
from config.serverConfig import ServerConfig
from validations.pydanticValidation import GeneratedProblemRaw
from prompts.generationPrompt import prompt as SYSTEM_PROMPT
import json
import subprocess
import sys
import re
import groq

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
                return f"Test Case {index + 1} output is not valid JSON. Output:\n{stdout.strip()}\nParsing error: {json_err}. Note: The reference_solution MUST print ONLY raw JSON via `print(json.dumps(output))`."

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

def generate_problem(user_prompt: str) -> GeneratedProblemRaw:
    system_instruction = SYSTEM_PROMPT
    config = ServerConfig()
    
    # Model fallback hierarchy if primary model hits rate limit (429)
    models_to_try = [config["GROQ_MODEL"]]
    for fallback_model in ["llama-3.1-8b-instant", "mixtral-8x7b-32768"]:
        if fallback_model not in models_to_try:
            models_to_try.append(fallback_model)

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_prompt}
    ]
    
    max_retries = 5
    for attempt in range(max_retries):
        response = None
        for current_model in models_to_try:
            try:
                response = client.chat.completions.create(
                    model=current_model,
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
                break
            except groq.RateLimitError as rle:
                print(f"[RateLimitError] Model '{current_model}' hit rate limit. Trying fallback model...")
                continue
            except Exception as e:
                error_msg = str(e)
                if "response_format" in error_msg or "json_schema" in error_msg:
                    # Fallback to json_object mode
                    schema_json = json.dumps(GeneratedProblemRaw.model_json_schema(), indent=2)
                    fallback_system_instruction = system_instruction + f"\n\nYou MUST respond with valid JSON matching the following JSON Schema:\n{schema_json}"
                    
                    fallback_messages = [
                        {"role": "system", "content": fallback_system_instruction}
                    ] + messages[1:]
                    
                    try:
                        response = client.chat.completions.create(
                            model=current_model,
                            temperature=config["TEMPERATURE"],
                            max_tokens=config["GROQ_MAX_TOKENS"],
                            messages=fallback_messages,
                            response_format={"type": "json_object"}
                        )
                        break
                    except groq.RateLimitError:
                        print(f"[RateLimitError] Fallback model '{current_model}' hit rate limit.")
                        continue
                    except groq.BadRequestError as bre:
                        print(f"[BadRequestError] {bre}. Adjusting retry prompt...")
                        if attempt < max_retries - 1:
                            messages.append({"role": "user", "content": "Your last response failed JSON validation. Please output strictly valid, escaped JSON without any unescaped triple-quotes or formatting errors."})
                            break
                        else:
                            raise bre
                else:
                    if attempt < max_retries - 1 and ("400" in error_msg or "json_validate_failed" in error_msg):
                        print(f"[API Error] {error_msg}. Retrying with sanitized prompt...")
                        messages.append({"role": "user", "content": "JSON validation failed. Ensure all strings are standard escaped JSON strings with no unescaped triple-quotes or python docstrings."})
                        break
                    raise e
                    
        if response is None:
            raise RuntimeError("All configured Groq models failed or exceeded rate limits. Please try again later.")

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
1. The script MUST end with:
   if __name__ == "__main__":
       import sys, json
       raw = json.loads(sys.stdin.read())
       parsed_args = build_input(raw)
       solution = Solution()
       ...
       print(json.dumps(output))
2. DO NOT write a main loop iterating over test cases or print formatted strings like `print(f"Input: ..., Output: ...")`. Print ONLY raw JSON via `print(json.dumps(output))`.
3. DO NOT use Python triple-quotes (`\"\"\"`) inside JSON fields.
4. DO NOT HARDCODE ANY PARAMETER VALUES inside the solution script or build_input!
5. `testCaseInputs` must be structured JSON objects containing all parameter keys with comma-separated list elements.
"""
        messages.append({"role": "user", "content": feedback})

