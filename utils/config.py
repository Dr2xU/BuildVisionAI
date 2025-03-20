# utils/config.py
import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def load_configuration(config_path):
    """
    Load application configuration from a YAML file.
    
    Args:
        config_path (Path): Path to the configuration file
    
    Returns:
        dict: Dictionary containing configuration settings
    """
    try:
        with open(config_path, 'r') as config_file:
            config = yaml.safe_load(config_file)
            logger.info(f"Configuration loaded from {config_path}")
            return config
    except yaml.YAMLError as e:
        logger.error(f"Error parsing configuration file: {e}")
        return {}
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return {}

def get_default_config():
    """
    Get default configuration values when no config file is available.
    
    Returns:
        dict: Dictionary containing default configuration settings
    """
    return {
        "ui": {
            "window_width": 1200,
            "window_height": 800,
            "theme": "default"
        },
        "processing": {
            "detection_threshold": 0.75,
            "max_symbols": 200
        },
        "paths": {
            "temp_dir": "temp",
            "output_dir": "output"
        }
    }