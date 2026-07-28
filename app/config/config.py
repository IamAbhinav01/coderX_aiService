from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):

    APP_NAME:str = "CoderX_AI_SERVICE"
    ENV:str = "development"
    PORT:int = 8000
    GROQ_API_KEY:str
    GROQ_MODEL:str = "llama-3.3-70b-versatile"
    GROQ_MAX_TOKENS:int = 4096
    TEMPERATURE:float = 0.7
    PINECONE_API_KEY:str
    PINECONE_INDEX_NAME:str = "coderx"
    PINECONE_NAMESPACE:str = "coding_Prompts"
    HF_TOKEN:str


    model_config = SettingsConfigDict(env_file='.env',env_file_encoding='utf-8',extra='ignore')


