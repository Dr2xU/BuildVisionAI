import tkinter as tk
import logging
from ui.welcome import WelcomeScreen
from ui.legend_selector import LegendSelector
from ui.symbol_linker import SymbolLinker
from utils.state_manager import state

logger = logging.getLogger(__name__)

class WorkflowManager:
    def __init__(self):
        logger.info("Initializing WorkflowManager")

        self.root = tk.Tk()
        self.root.title("Blueprint Symbol Manager")
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda e: self.quit_app())

        self.container = tk.Frame(self.root)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.current_frame = None
        self.start_welcome()

    def clear_frame(self):
        if self.current_frame:
            logger.debug("Clearing current frame")
            self.current_frame.destroy()

    def start_welcome(self):
        logger.info("Starting Welcome Screen")
        self.clear_frame()
        self.current_frame = WelcomeScreen(self.container, on_file_selected=self.start_legend_selector)

    def start_legend_selector(self, _=None):
        logger.info(f"Starting Legend Selector for image: {state.image_path}")
        self.clear_frame()

        # Create a frame container
        frame = tk.Frame(self.container)
        frame.pack(fill=tk.BOTH, expand=True)

        # Inject LegendSelector tool into the frame
        LegendSelector(frame, image_path=state.image_path, on_done=self.start_symbol_linker)

        self.current_frame = frame  # This can now be safely destroyed later


    def start_symbol_linker(self):
        self.clear_frame()
        self.current_frame = SymbolLinker(
            self.container,
            image_path=state.legend_path,
            on_done=self.end_workflow
        )

    def end_workflow(self):
        logger.info("✅ Symbol linking complete. Ready for next stage.")

    def quit_app(self):
        logging.info("ESC pressed — exiting application")
        self.root.quit()

    def run(self):
        logger.info("Running Tkinter main loop")
        self.root.mainloop()
