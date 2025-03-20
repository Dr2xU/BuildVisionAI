# utils/logging_setup.py
import os
import logging
import datetime
from pathlib import Path

def setup_logging(level=logging.INFO, log_dir="logs"):
    """
    Configure application logging with appropriate formatting and output locations.
    
    Args:
        level (int): Logging level (e.g., logging.INFO, logging.DEBUG)
        log_dir (str): Directory to store log files
    """
    # Create logs directory if it doesn't exist
    Path(log_dir).mkdir(exist_ok=True, parents=True)
    
    # Generate log filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"blueprint_analyzer_{timestamp}.log")
    
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # File handler for logging to file
    file_handler = logging.FileHandler(log_file)
    file_formatter = logging.Formatter(log_format, date_format)
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(level)
    root_logger.addHandler(file_handler)
    
    # Console handler for logging to console
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # Log startup message
    root_logger.info(f"Logging initialized at level {logging.getLevelName(level)}")
    root_logger.info(f"Log file: {log_file}")