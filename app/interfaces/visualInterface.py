from abc import ABC,abstractmethod

class  InterfaceVisualService(ABC):
    @abstractmethod
    def generate_visual_url(self,has_visual:bool,diagram_type:Diagr)