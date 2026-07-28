from groq import Groq
from config.config import Settings

settings = Settings()

api_key = settings.GROQ_API_KEY
client = Groq(api_key=api_key)

def Client():
    return client