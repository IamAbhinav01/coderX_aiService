from abc import ABC,abstractmethod
from typing import List,Dict,Any
from models.model import GeneratedProblemRaw

class InterfaceRunner(ABC):
    @abstractmethod
    def verify_and_execute(self,raw_problem:GeneratedProblemRaw)->List[Dict[str,Any]]:
        pass