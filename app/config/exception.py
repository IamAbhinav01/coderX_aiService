
class ApplicationService(Exception):
    def __init__(self,message,statuscode):

        super().__init__(message)
        self.message = message
        self.statuscode = statuscode