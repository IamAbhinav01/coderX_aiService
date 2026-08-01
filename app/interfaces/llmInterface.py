from abc import ABC,abstractmethod
from models.model import GeneratedProblemRaw

class InterfaceLLMGroq(ABC):

    @abstractmethod
    def GenerateProbelm(self,prompt:str)->GeneratedProblemRaw:
        pass
    