import logging
from logging.handlers import TimedRotatingFileHandler
import sys
from pathlib import Path

# Ensure Logs directory exists:
LOG_DIR = Path(__file__).resolve().parents[3] / "logs"
LOG_DIR.mkdir(exist_ok=True)


def setup_logging():

    log_format = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"

    handlers = [
        logging.StreamHandler(sys.stdout),
        TimedRotatingFileHandler(
            LOG_DIR / "app.log",
            when="midnight",
            interval=1,             # rotate every midnight
            backupCount=7,          # every 1 day
            encoding="utf-8"        # keep 7 days of logs
        )
    ]

    logging.basicConfig(
        level=logging.INFO,         # Only show logs that are INFO or more important
        format=log_format,
        handlers=handlers
    )