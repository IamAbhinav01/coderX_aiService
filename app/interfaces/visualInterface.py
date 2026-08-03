from abc import ABC,abstractmethod
from models.model import DiagramType,VisualPayload
from typing import Optional

class  InterfaceVisualService(ABC):
    @abstractmethod
    def generate_visual_url(self,has_visual:bool,diagram_type:DiagramType,diagram_code:Optional[str]=None,image_prompt:Optional[str] = None) -> VisualPayload:
        pass