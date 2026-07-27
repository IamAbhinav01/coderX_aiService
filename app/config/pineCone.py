from pinecone import Pinecone,ServerlessSpec
from config.serverConfig import ServerConfig

api_key = ServerConfig()["PINECONE_API_KEY"]

pc = Pinecone(api_key=api_key)
INDEX_NAME = "coderx"

if not pc.has_index(INDEX_NAME):
    pc.create_index_for_model(
        name=INDEX_NAME,
        cloud="aws",
        region="us-east-1",
        embed={
            "model":"multilingual-e5-large",
            "field_map": {"text": "prompt_text"}
        },
    )

index_name = pc.Index(INDEX_NAME)

def PineCone_Config():
    return pc