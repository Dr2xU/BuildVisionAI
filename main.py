#!/usr/bin/env python3
import sys
import argparse
import logging
from pathlib import Path

# Import your application components
from ui.workflow_manager import WorkflowManager
from utils.config import load_configuration, get_default_config
from utils.logging_setup import setup_logging

def parse_arguments():
    """Parse command line arguments for the application."""
    parser = argparse.ArgumentParser(description="Blueprint Analysis Application")
    
    parser.add_argument("--config", type=str, default="config.yaml",
                        help="Path to configuration file")
    parser.add_argument("--debug", action="store_true", 
                        help="Enable debug mode with verbose logging")
    parser.add_argument("--skip-welcome", action="store_true",
                        help="Skip welcome screen and go directly to file processing")
    parser.add_argument("--input-file", type=str,
                        help="Path to blueprint file to open on startup")
    
    return parser.parse_args()

def main():
    """Main entry point for the Blueprint Analysis Application."""
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Setup logging based on debug flag
        log_level = logging.DEBUG if args.debug else logging.INFO
        # setup_logging(log_level)
        logger = logging.getLogger(__name__)
        
        logger.info("Starting Blueprint Analysis Application")
        
        # Load application configuration
        config_path = Path(args.config)
        if not config_path.exists():
            logger.warning(f"Configuration file {args.config} not found, using defaults")
            config = get_default_config()
        else:
            config = load_configuration(config_path)
        
        # Initialize the workflow manager with configuration
        workflow_options = {
            "skip_welcome": args.skip_welcome,
            "input_file": args.input_file,
            "config": config
        }
        
        app = WorkflowManager(**workflow_options)
        
        # Run the application
        logger.info("Initializing user interface")
        exit_code = app.run()
        
        logger.info(f"Application exited with code {exit_code}")
        return exit_code
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.critical(f"Unhandled exception: {str(e)}", exc_info=True)
        print(f"Critical error: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())