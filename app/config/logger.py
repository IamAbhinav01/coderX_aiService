import logging,json,sys
from datetime import datetime
import pytz
from config import Settings

settings = Settings()

class JSON_formatter(logging.Formatter):
    def format(self,record:logging.LogRecord)->str:
        ist = pytz.timezone("Asia/Kolkata")
        log_data = {
            "timestamp":datetime.now(ist).isoformat(),
            "level":record.levelname,
            "message":record.getMessage(),
            "logger":record.name,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

def setup_logger(name:str = settings.APP_NAME)->logging.Logger:
    logger = logging.getLogger(name=name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSON_formatter())
        logger.addHandler(handler)
    return logger

# logger = setup_logger(name="logger")

# logger.info("Application started")