from config.groqClient import client
from config.serverConfig import ServerConfig
from validations.pydanticValidation import GeneratedProblemRaw
import json

groq_client = client

def generate_problem(prompt : str)->dict:
    system_instruction = """You are a competitive programming designer.
    Generate a coding challenge based on the user request.
    Always output JSON matching the provided schema.
    Provide a robust reference_solution written in Python 3.
    Provide 3 to 5 realistic input cases in testCaseInputs.
    Make sure each item in the codeSnippets array is a valid CodeSnippet object containing all required fields: 'language', 'startSnippet', 'midSnippet', and 'endSnippet'. Do not include raw strings or empty items in the codeSnippets array.
    """

    config = ServerConfig()
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

