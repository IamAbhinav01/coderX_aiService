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
    """

    response = client.chat.completions.create(
        model=ServerConfig()["openai/gpt-oss-20b"],
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
    raw_json = json.loads(response.choices[0].message.content or "{}")
    return GeneratedProblemRaw.model_validate(raw_json)

