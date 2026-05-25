from langchain_groq import ChatGroq
from app.config.server import GROQ_API_KEY, GROQ_MODEL, GROQ_TEMPERATURE, GROQ_MAX_TOKENS

_llm_instance: ChatGroq | None = None


def get_groq_client() -> ChatGroq:
    global _llm_instance

    if _llm_instance is None:
        if not GROQ_API_KEY or not GROQ_MODEL:
            raise ValueError(
                "GROQ_API_KEY and GROQ_MODEL must be set in the environment."
            )

        _llm_instance = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name=GROQ_MODEL,
            temperature=GROQ_TEMPERATURE,
            max_tokens=GROQ_MAX_TOKENS,  
            
        )

    return _llm_instance
