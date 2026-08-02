
class ApplicationService(Exception):
    def __init__(self,message,statuscode):

        super().__init__(message)
        self.message = message
        self.statuscode = statuscode


class DiagramException(ApplicationService):
    def __init__(self,message:str):
        
        super().__init__(f"[Diagram Service Error] {message}",statuscode=500)

class PineConeVectorException(ApplicationService):
    def __init__(self,message:str):

        super().__init__(f"[PineCone Vector Service Error] {message}",statuscode=500)

class GroqGenerationException(ApplicationService):
    def __init__(self, message:str):
        super().__init__(f"[GROQ Generation Service Error] {message}",statuscode=500)