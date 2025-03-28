import yaml
import logging
from pathlib import Path
from copy import deepcopy

logger = logging.getLogger(__name__)

def get_default_config():
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

def merge_config(user_cfg, default_cfg=None):
    """
    Merge a user-provided config dictionary with defaults.
    Nested dicts are merged recursively.

    Returns:
        dict: Complete config dictionary
    """
    if default_cfg is None:
        default_cfg = get_default_config()

    result = deepcopy(default_cfg)
    for key, val in user_cfg.items():
        if isinstance(val, dict) and key in result:
            result[key] = merge_config(val, result[key])
        else:
            result[key] = val
    return result

def load_configuration(config_path: Path):
    """
    Load application configuration from a YAML file, merged with defaults.

    Args:
        config_path (Path): Path to the configuration file

    Returns:
        dict: Merged configuration dictionary
    """
    try:
        with open(config_path, 'r') as config_file:
            user_config = yaml.safe_load(config_file) or {}
            full_config = merge_config(user_config)
            logger.info(f"Configuration loaded from {config_path}")
            return full_config
    except yaml.YAMLError as e:
        logger.error(f"Error parsing configuration file: {e}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
    
    return get_default_config()

def save_configuration(config: dict, path: Path):
    """
    Save configuration to a YAML file.

    Args:
        config (dict): Configuration dictionary
        path (Path): Output path
    """
    try:
        with open(path, 'w') as f:
            yaml.safe_dump(config, f)
        logger.info(f"Configuration saved to {path}")
    except Exception as e:
        logger.error(f"Failed to save configuration: {e}")
