#!/usr/bin/env python3
import logging
from ui.workflow_manager import WorkflowManager
from utils.state_manager import state
from utils.logging_setup import setup_logging

def main():
    # Setup logging
    setup_logging(logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.info("Starting Blueprint Analysis Application")


    # Optional: initialize any state here
    state.linked_items = []
    state.legend_box = None

    # Launch the workflow
    app = WorkflowManager()
    app.run()

if __name__ == "__main__":
    main()
