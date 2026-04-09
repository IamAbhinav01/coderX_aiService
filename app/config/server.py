import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")
GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE"))
ASTRA_DB_APPLICATION_TOKEN=os.getenv("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_APPLICATION_URL=os.getenv("ASTRA_DB_APPLICATION_URL")
VOYAGE_API_KEY=os.getenv("VOYAGE_API_KEY")
