from app.config.server import ASTRA_DB_APPLICATION_TOKEN, ASTRA_DB_APPLICATION_URL
from app.utils.logger import get_logger
from astrapy import DataAPIClient

logger = get_logger(__name__)

# Initialise the AstraDB client and database handle once at module load time.
# All vector store operations import `db` from this module.
client = DataAPIClient()
db = client.get_database(
    ASTRA_DB_APPLICATION_URL,
    token=ASTRA_DB_APPLICATION_TOKEN,
)

logger.info(f"Connected to Astra DB | collections: {db.list_collection_names()}")