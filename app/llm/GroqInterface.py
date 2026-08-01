from interfaces.llmInterface import InterfaceLLMGroq
from models.model import GeneratedProblemRaw
from config.config import Settings
from config.logger import setup_logger

settings = Settings()
logger = setup_logger()

class GroqInterface(InterfaceLLMGroq):

    def __init__(self):
        
    # def GenerateProbelm(self, prompt:str)->GeneratedProblemRaw:
    #     messages = [
    #         {
    #             "role":"system","content":
    #         }
    #     ]
    