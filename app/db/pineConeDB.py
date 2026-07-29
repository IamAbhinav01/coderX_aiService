from interfaces.vectorInterface import InterfaceVectorStore
from pinecone import Pinecone
from config.exception import PineConeVectorException
from config.config import Settings
from typing import Optional
from config.logger import setup_logger

settings = Settings()
logger = setup_logger()

class PineConeStore(InterfaceVectorStore):

    def __init__(self,api_key:str = settings.PINECONE_API_KEY,index_name:str = settings.PINECONE_INDEX_NAME,namespace:str=settings.PINECONE_NAMESPACE):
        self.api_key = api_key
        self.index_name = index_name
        self.namespace = namespace
        self.pc : Optional[Pinecone] = None
        self.index  = None

    def initialize_index(self):
        try:
            self.pc = "Hi"
        except Exception as e:
            logger.error(f"Error occured while intialising the pinecone vector store : {e}")
            raise PineConeVectorException("Error occured while Initialising the vector store")
