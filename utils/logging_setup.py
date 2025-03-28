import os
import logging
import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler

LOG_FILE_PATH = None  # Accessible from elsewhere

def setup_logging(level=logging.INFO, log_dir="logs"):
    """
    Configure application logging with appropriate formatting and output locations.

    Args:
        level (int): Logging level (e.g., logging.INFO, logging.DEBUG)
        log_dir (str): Directory to store log files
    """
    global LOG_FILE_PATH

    # Allow override from environment variable
    env_level = os.getenv("BLUEPRINT_LOG_LEVEL")
    if env_level:
        level = getattr(logging, env_level.upper(), level)

    Path(log_dir).mkdir(exist_ok=True, parents=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    LOG_FILE_PATH = os.path.join(log_dir, f"blueprint_analyzer_{timestamp}.log")

    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Rotating file handler (5 MB max, 3 backups)
    file_handler = RotatingFileHandler(LOG_FILE_PATH, maxBytes=5*1024*1024, backupCount=3)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    file_handler.setLevel(level)
    root_logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    console_handler.setLevel(level)
    root_logger.addHandler(console_handler)

    root_logger.info(f"Logging initialized at level {logging.getLevelName(level)}")
    root_logger.info(f"Log file: {LOG_FILE_PATH}")
