from interfaces.vectorInterface import InterfaceVectorStore
from pinecone import Pinecone
from config.exception import PineConeVectorException
from config.config import Settings
from typing import Dict,Optional,Any
from config.logger import setup_logger
import json,uuid

settings = Settings()
logger = setup_logger()

class PineConeStore(InterfaceVectorStore):

    def __init__(self,api_key:str = settings.PINECONE_API_KEY,index_name:str = settings.PINECONE_INDEX_NAME,namespace:str=settings.PINECONE_NAMESPACE):
        self.api_key = api_key
        self.index_name = index_name.lower()
        self.namespace = namespace
        self.pc : Optional[Pinecone] = None
        self.index  = None

    def initialize_index(self):
        try:
            self.pc = Pinecone(api_key=self.api_key)
            if not self.pc.has_index(self.index_name):
                self.pc.create_index_for_model(
                    name=self.index_name,
                            cloud="aws",
                            region="us-east-1",
                            embed={
                                "model":"multilingual-e5-large",
                                "field_map": {"text": "prompt_text"}
                            },
                )
            self.index  = self.pc.Index(name=self.index_name)
            logger.info(f"connected to index : {self.index_name}")
        except Exception as e:
            logger.error(f"Error occured while intialising the pinecone vector store : {e}")
            raise PineConeVectorException("Error occured while Initialising the vector store")

    def search_cache(self,prompt:str,threshold:float = 0.88)->Optional[Dict[str,Any]]:

        if not self.index:
            return None

        try:
            response = self.index.search(
                namespace=self.namespace,
                query={
                    "inputs":{
                        "text":prompt
                    },
                    "top_k":1
                },
                fields=["prompt_text","payload_json"]
            )

            if response and response.result and response.result.hits:

                '''I got the response in this form
                
                    response (SearchResponse)
                        └── .result (SearchResult object)
                            └── .hits (List of Hit objects)
                                ├── top_hit.id (e.g. "record_123")
                                ├── top_hit.score (e.g. 0.92)
                                └── top_hit.fields (e.g. {"prompt_text": "...", "payload_json": "..."})
                '''


                top_hit = response.result.hits[0]

                if top_hit.score >= threshold: 
                    payload_str = top_hit.fields.get("payload_json")
                    if payload_str:
                        payload = json.loads(payload_str)
                        payload["_similarity"] = round(top_hit.score,4)
                        payload["_cache_hit"] = True

                        logger.info(f"[VECTOR CACHE] hit Score : {top_hit.score:.4f} for {prompt}")
                        return payload
        except Exception as e:
            logger.error(f"PineCone search error : {e}")
            return None


    def save_cache(self,prompt:str,payload:Dict[str,Any])->bool:

        if not self.index:
            return False

        try:
            prompt_id = f"prompt_{uuid.uuid4().hex[:12]}"
            payload_json = json.dumps(payload)

            self.index.upsert_records(
                namespace=self.namespace,
                records=[{
                    "_id":prompt_id,
                    "prompt_text":prompt,
                    "payload_json":payload_json
                }]
            )

            logger.info(f"[VECTOR CACHE SAVED] prompt_id: {prompt_id}")
            return True
        except Exception as e:
            logger.error(f"PineCone cache error : {e}")
            return False
       

        