from huggingface_hub import InferenceClient
from interfaces.visualInterface import InterfaceVisualService
from config.logger import setup_logger
from models.model import DiagramType
from config.config import Settings
from typing import Optional

logger = setup_logger()

class HybridVisualConnector(InterfaceVisualService):
    def __init__(self,settings:Settings):
        self.settings = settings
        self.hf_client = Optional[InferenceClient] = None
        if settings.HF_TOKEN:
            try:
                self.hf_client = InferenceClient(provider="fal-ai",api_key=settings.HF_TOKEN)
            except Exception as e:
                logger.warning(f"HuggingFace client init warninga: {e}")


    def generate_visual_url(self, has_visual:bool, diagram_type:DiagramType, diagram_code:Optional[str] = None, image_prompt:Optional[str] = None) -> Optional[str]:

        if not has_visual or diagram_type == DiagramType.NONE:
            return None
        