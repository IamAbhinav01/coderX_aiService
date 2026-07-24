import os
from dotenv import load_dotenv



load_dotenv()

def ServerConfig()->dict:
    return {
        "PORT":os.getenv("PORT",8000),
        "GROQ_API_KEY":os.getenv("GROQ_API_KEY"),
        "GROQ_MODEL":os.getenv("GROQ_MODEL","openai/gpt-oss-20b"),
        "TEMPERATURE":os.getenv("TEMPERATURE",0.7)
    }