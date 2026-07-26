from groq import Groq
from config.serverConfig import ServerConfig


api_key = ServerConfig()["GROQ_API_KEY"]
client = Groq(api_key=api_key)

def Client():
    return client