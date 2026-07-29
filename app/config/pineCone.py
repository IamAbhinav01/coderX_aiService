from pinecone import Pinecone,ServerlessSpec
from config import Settings

settings = Settings()

api_key = settings.PINECONE_API_KEY

pc = Pinecone(api_key=api_key)

if not pc.has_index(settings.PINECONE_INDEX_NAME):
    pc.create_index_for_model(
        name=settings.PINECONE_INDEX_NAME,
        cloud="aws",
        region="us-east-1",
        embed={
            "model":"multilingual-e5-large",
            "field_map": {"text": "prompt_text"}
        },
    )

index_name = pc.Index(settings.PINECONE_INDEX_NAME)

def PineCone_Config():
    return pc