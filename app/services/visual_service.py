from huggingface_hub import InferenceClient
from interfaces.visualInterface import InterfaceVisualService
from config.logger import setup_logger
from models.model import DiagramType,VisualPayload
from config.config import Settings
from typing import Optional
import base64,urllib.parse,os,uuid
from PIL import Image

logger = setup_logger()

class HybridVisualConnector(InterfaceVisualService):
    def __init__(self,settings:Settings, storage_dir:str = "app/static/generated_images"):
        self.settings = settings
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir,exist_ok=True)

        self.hf_client = Optional[InferenceClient] = None
        if settings.HF_TOKEN:
            try:
                self.hf_client = InferenceClient(provider="fal-ai",api_key=settings.HF_TOKEN)
            except Exception as e:
                logger.warning(f"HuggingFace client init warninga: {e}")

    def _generate_image_from_HF(self,prompt:str,model:str = "ideogram-ai/ideogram-4-fp8")->Optional[str]:
        if not self.hf_client:
            logger.warning("HF_TOKEN is missing")
            return None
        try:
            logger.info(f"Generating image from huggingFace")
            image:Image.Image = self.hf_client.text_to_image(
                prompt=prompt,
                model=model
            )
            filename = f"image_{uuid.uuid4().hex[:10]}.png"
            filepath = os.path.join(self.storage_dir,filename)
            image.save(filepath,format="PNG")

            logger.info(f"Succesfully generated and saved AI image to : {filepath}")
            return f"/static/generated_images/{filename}"
        except Exception as e:
            logger.error(f"HuggingFace Image generation failed: {e}")
            return None
    def generate_visual_url(self, has_visual:bool, diagram_type:DiagramType, diagram_code:Optional[str] = None, image_prompt:Optional[str] = None) -> VisualPayload:

        if not has_visual or diagram_type == DiagramType.NONE:
            return VisualPayload(hasVisual=False,type="none",url=None,diagramCode=None)

        if diagram_code and diagram_code.strip() and diagram_type in [DiagramType.TREE,DiagramType.GRAPH,DiagramType.GRID,DiagramType.LINKED_LIST]:
            try:
                cleaned_mermaid = diagram_code.replace("```mermaid", "").replace("```", "").strip()
                encoded_b64 = base64.b64encode(cleaned_mermaid.encode("utf-8")).decode("utf-8")
                svg_url = f"https://mermaid.ink/svg/{encoded_b64}"
                logger.info(f"[VISUAL] generated mermaid svg url : {svg_url[:60]}..")
                return VisualPayload(
                    hasVisual=True,
                    type=diagram_type.value,
                    url=svg_url,
                    diagramCode=cleaned_mermaid
                )
            except Exception as e:
                logger.error(f"[VISUAL Error] Mermaid encoding failed:{e}")

        if image_prompt and image_prompt.strip() and diagram_type == DiagramType.ILLUSTRATION:
            if self.hf_client:
                try:
                    saved_image_path = self._generate_image_from_HF(image_prompt)
                    if saved_image_path:
                        return saved_image_path
                    encoded_prompt = urllib.parse.quote(image_prompt.strip())
                    pollinations_url = "https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=450&nologo=true"
                    return VisualPayload(hasVisual=True,type=diagram_type.value,url=pollinations_url,diagramCode=None)
                except Exception as hf_err:
                    logger.info(f"Error occured while generating image from HF , error : {hf_err}")
                    
        return VisualPayload(hasVisual=False,type="none",url=None,diagramCode=None)         