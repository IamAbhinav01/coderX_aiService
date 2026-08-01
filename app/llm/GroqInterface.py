from interfaces.llmInterface import InterfaceLLMGroq
from models.model import GeneratedProblemRaw
from config.config import Settings
from config.logger import setup_logger
import re
import groq

logger = setup_logger()

class GroqInterface(InterfaceLLMGroq):

    def __init__(self,settings:Settings):
        self.settings = settings
        self.client = groq.Groq(api_key=settings.GROQ_API_KEY)
        self.models_to_try = [
            settings.GROQ_MODEL,
            "llama-3.1-8b-instant",
            "openai/gpt-oss-20b",
            "llama-3.1-8b-instant",
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "mixtral-8x7b-32768"
        ]

    def _clean_code(self,code:str)->str:
        code = code.strip()
        code = re.sub(r"^```(?:python|py)?\s*", "", code)
        code = re.sub(r"\s*```$", "", code)
        
    # def GenerateProbelm(self, prompt:str)->GeneratedProblemRaw:
    #     messages = [
    #         {
    #             "role":"system","content":
    #         }
    #     ]
    