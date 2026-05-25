from app.config.server import ASTRA_DB_APPLICATION_TOKEN, ASTRA_DB_APPLICATION_URL
from app.utils.logger import get_logger
from astrapy import DataAPIClient



logger = get_logger(__name__)



try:
    client = DataAPIClient()
    db = client.get_database(
        ASTRA_DB_APPLICATION_URL,
        token=ASTRA_DB_APPLICATION_TOKEN,

    )
    logger.info(f"Connected to Astra DB | collections: {db.list_collection_names()}")
except Exception as e:
    logger.error(f"Astra DB connection failed: {e}")
