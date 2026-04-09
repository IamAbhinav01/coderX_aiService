from langchain_groq import ChatGroq
from app.config.server import GROQ_API_KEY,GROQ_MODEL,GROQ_TEMPERATURE

isllmInstance  = None
def get_groq_client():
    global isllmInstance
    if not isllmInstance:
       if(not GROQ_API_KEY or not GROQ_MODEL):
          raise ValueError("GROQ_API_KEY and GROQ_MODEL must be set in environment variables.")

    isllmInstance = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name=GROQ_MODEL,
        temperature=GROQ_TEMPERATURE,
         response_format={"type": "json_object"}
    )
    return isllmInstance
