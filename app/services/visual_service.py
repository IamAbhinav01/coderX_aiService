from huggingface_hub import InferenceClient
from interfaces.visualInterface import InterfaceVisualService
from config.logger import setup_logger
from models.model import DiagramType
from config.config import Settings
from typing import Optional
import base64,urllib.parse

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

        if diagram_code and diagram_type in [DiagramType.TREE,DiagramType.GRAPH,DiagramType.GRID,DiagramType.LINKED_LIST]:
            try:
                cleaned_mermaid = diagram_code.replace("```mermaid", "").replace("```", "").strip()
                encoded_b64 = base64.b64encode(cleaned_mermaid.encode("utf-8")).decode("utf-8")
                svg_url = f"https://mermaid.ink/svg/{encoded_b64}"
                logger.info(f"[VISUAL] generated mermaid svg url : {svg_url[:60]}..")
                return svg_url
            except Exception as e:
                logger.error(f"[VISUAL Error] Mermaid encoding failed:{e}")

        if image_prompt and diagram_type == DiagramType.ILLUSTRATION:
            if self.hf_client:
                try:
                    logger.info(f"[VISUAL] Generating HuggingFace Image for prompt: '{image_prompt[:30]}...'")
                    encoded_prompt = urllib.parse.quote(image_prompt)
                    return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=450&nologo=true"
                except Exception as hf_err:
                    logger.error(f"[VISUAL ERROR] HuggingFace generation failed: {hf_err}")
            encoded_prompt = urllib.parse.quote(image_prompt)
            return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=450&nologo=true"
        return None         