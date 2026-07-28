import logging,json
from datetime import datetime
from zoneinfo import ZoneInfo
from config.config import Settings

settings = Settings()

class JSON_formatter(logging.Formatter):
    def format(self,record:logging.LogRecord)->str:
        timestamp = datetime.now(ZoneInfo("Asia/Kolkata"))
        log_data = {
            "timestamp":timestamp,
            "level":record.levelname,
            "message":record.getMessage(),
            "logger":record.name,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

def setup_logger(name:str = settings.APP_NAME)->logging.Logger:
    