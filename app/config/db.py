from server import  ASTRA_DB_APPLICATION_TOKEN, ASTRA_DB_APPLICATION_URL
from astrapy import DataAPIClient

# Initialize the client
client = DataAPIClient()
db = client.get_database(
  ASTRA_DB_APPLICATION_URL,
  token=ASTRA_DB_APPLICATION_TOKEN
)

print(f"Connected to Astra DB: {db.list_collection_names()}")