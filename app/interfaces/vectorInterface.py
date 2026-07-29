from abc import ABC,abstractmethod
from typing import Dict,Optional,Any

class InterfaceVectorStore(ABC):

    @abstractmethod
    def search_cache(self,prompt:str,threshold:float = 0.88)->Optional[Dict[str,Any]]:
        pass

    @abstractmethod
    def save_cache(self,prompt:str,payload:Dict[str,Any])->bool:
        pass