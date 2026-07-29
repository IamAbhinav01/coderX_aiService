
class ApplicationService(Exception):
    def __init__(self,message,statuscode):

        super().__init__(message)
        self.message = message
        self.statuscode = statuscode


class DiagramException(ApplicationService):
    def __init__(self,message:str):
        
        super().__init__(f"[Diagram Service Error] {message}",statuscode=500)