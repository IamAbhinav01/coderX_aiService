from pinecone import Pinecone,ServerlessSpec
from serverConfig import ServerConfig

api_key = ServerConfig()["PINECONE_API_KEY"]

pc = Pinecone(api_key=api_key)
index_name = pc.Index("coderX")

if not pc.has_index(index_name):
    pc.create_index_for_model(
        name=index_name,
        cloud="aws",
        region="us-east-1",
        embed={
            "model":"multilingual-e5-large",
            "field_map": {"text": "prompt_text"}

        },

    )

def PineCone_Config():
    return pc