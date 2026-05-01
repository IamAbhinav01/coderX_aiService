from astrapy import DataAPIClient
from astrapy.constants import VectorMetric
from astrapy.info import CollectionDefinition, CollectionVectorOptions
from app.config.server import ASTRA_DB_APPLICATION_TOKEN, ASTRA_DB_APPLICATION_URL  
client = DataAPIClient(ASTRA_DB_APPLICATION_TOKEN)

database = client.get_database(ASTRA_DB_APPLICATION_URL)

collection_definition = CollectionDefinition(
    vector=CollectionVectorOptions(
        dimension=768,
        metric=VectorMetric.COSINE
    ),
)

collection = database.create_collection(
    "coderx_problems",
    definition=collection_definition,
)
print("Collection created:", collection.name)