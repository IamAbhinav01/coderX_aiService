from typing import Optional

class DiagramService:
    @staticmethod
    def generate_url(is_visual:bool,diagram_type:str,diagram_code:Optional[str]=None)->Optional[str]: