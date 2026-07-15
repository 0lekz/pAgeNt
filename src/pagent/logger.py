# logger.py
# Structured logging so we can see requests, tool calls, and errors in a single place.

from datetime import datetime
import json
import logging

from pagent.config import Settings


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }
        # merge in any extra fields that were passed to the logger
        payload.update(getattr(record, "data", {}))
        return json.dumps(payload)
    
def setup_logger(settings: Settings) -> None:
    """
    Configure the root pagent logger once. Call this exactly once at the start of
    your program.
    """
    logger = logging.getLogger("pagent")
    logger.setLevel(settings.log_level)

    handler = logging.FileHandler(settings.data_dir / "pagent.log")
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    