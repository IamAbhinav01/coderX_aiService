import os
from dotenv import load_dotenv

load_dotenv()

def ServerConfig()->dict:
    return {
        "PORT": int(os.getenv("PORT", 8000)),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        "GROQ_MODEL": os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        "TEMPERATURE": float(os.getenv("TEMPERATURE", 0.7)),
        "GROQ_MAX_TOKENS": int(os.getenv("GROQ_MAX_TOKENS", 4096)),
        "PINECONE_API_KEY":os.getenv("PINECONE_API_KEY"),
        "HF_TOKEN":os.getenv("HF_TOKEN")
    }
