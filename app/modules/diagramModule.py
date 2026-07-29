import base64
from typing import Optional
from config.logger import setup_logger

logger = setup_logger(name="DiagramModule")

class DiagramService:
    @staticmethod
    def generate_url(is_visual:bool,diagram_type:str,diagram_code:Optional[str]=None)->Optional[str]:

        if not is_visual or not diagram_code or  diagram_type == "none":
            return None

        try:
            clean_code = diagram_code.replace("```mermaid", "").replace("```", "").strip()
            encoded_b64 = base64.b64encode(clean_code.encode(encoding="utf-8")).decode(encoding="utf-8")
            logger.info("encoded_b64 successfully generated")
            return f"https://mermaid.ink/svg/{encoded_b64}"
        except Exception as e:
            
            logger.exception("Error while generating diagram URL")
            return None

