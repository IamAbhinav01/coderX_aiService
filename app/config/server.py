import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")
GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.7"))  # default keeps the service bootable
# Max tokens for LLM response. A full problem (description + 3 test cases + editorial)
# can easily be 1500–2500 tokens. 4096 gives plenty of headroom on any Groq model.
GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "4096"))
ASTRA_DB_APPLICATION_TOKEN=os.getenv("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_APPLICATION_URL=os.getenv("ASTRA_DB_APPLICATION_URL")
# NOTE: VOYAGE_API_KEY removed — embeddings are now local via sentence-transformers
