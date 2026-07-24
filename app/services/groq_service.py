from config.groqClient import client
from config.serverConfig import ServerConfig
from validations.pydanticValidation import GeneratedProblemRaw
import json

groq_client = client

def generate_problem(prompt : str)->GeneratedProblemRaw:
    system_instruction = """You are a competitive programming designer.
    Generate a coding challenge based on the user request.
    Always output JSON matching the provided schema.
    
    Provide a robust reference_solution written in Python 3. The reference_solution must be a fully working standalone script that reads test case inputs from standard input (stdin), parses them (e.g., from JSON format or string representation) into any needed data structures (such as ListNodes, TreeNodes, arrays, etc.), calls the solution logic, and prints the results to standard output (stdout). Ensure all necessary helper classes (like ListNode or TreeNode) are defined inside the script.
    
    Provide 3 to 5 realistic input cases in testCaseInputs.
    Generate starter code templates in codeSnippets for all supported languages: python, java, and cpp.
    
    Starter code template guidelines:
    - For C++ (cpp): Include standard competitive programming headers (e.g., `#include <bits/stdc++.h>`) and standard namespaces/libraries.
    - For Java (java): Include common standard library imports (e.g., `import java.util.*;` and `import java.io.*;`).
    
    Make sure each item in the codeSnippets array is a valid CodeSnippet object containing all required fields: 'language', 'startSnippet', 'midSnippet', and 'endSnippet'. Do not include raw strings or empty items in the codeSnippets array.
    """

    config = ServerConfig()
    try:
        response = client.chat.completions.create(
            model=config["GROQ_MODEL"],
            temperature=config["TEMPERATURE"],
            max_tokens=config["GROQ_MAX_TOKENS"],
            messages=[
                {"role":"system","content":system_instruction},
                {"role":"user","content":prompt}
            ],
            response_format={
                "type":"json_schema",
                "json_schema":{
                    "name":"GenerateCodingQuestionRAW",
                    "schema":GeneratedProblemRaw.model_json_schema()
                }
            }
        )
    except Exception as e:
        error_msg = str(e)
        if "response_format" in error_msg or "json_schema" in error_msg:
            schema_json = json.dumps(GeneratedProblemRaw.model_json_schema(), indent=2)
            fallback_system_instruction = system_instruction + f"\n\nYou MUST respond with valid JSON matching the following JSON Schema:\n{schema_json}"
            
            response = client.chat.completions.create(
                model=config["GROQ_MODEL"],
                temperature=config["TEMPERATURE"],
                max_tokens=config["GROQ_MAX_TOKENS"],
                messages=[
                    {"role":"system","content":fallback_system_instruction},
                    {"role":"user","content":prompt}
                ],
                response_format={"type": "json_object"}
            )
        else:
            raise e
    raw_content = response.choices[0].message.content or "{}"
    try:
        raw_json = json.loads(raw_content)
        return GeneratedProblemRaw.model_validate(raw_json)
    except Exception as e:
        print("\n--- RAW LLM RESPONSE START ---")
        try:
            print(raw_content.encode('utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8', errors='replace'))
        except Exception:
            print(repr(raw_content))
        print("--- RAW LLM RESPONSE END ---\n")
        raise e

