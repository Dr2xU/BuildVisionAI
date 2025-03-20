import tkinter as tk
from ui.welcome import WelcomeScreen
from ui.legend_selector import LegendSelector
from ui.symbol_linker import SymbolLinker

class WorkflowManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Blueprint Symbol Manager")
        self.root.attributes("-fullscreen", True)
        self.container = tk.Frame(self.root)
        self.container.pack(fill=tk.BOTH, expand=True)
        self.current_frame = None
        self.start_welcome()

    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

    def start_welcome(self):
        self.clear_frame()
        self.current_frame = WelcomeScreen(self.container, on_file_selected=self.start_legend_selector)

    def start_legend_selector(self, image_path):
        self.image_path = image_path
        self.clear_frame()
        self.current_frame = LegendSelector(self.container, image_path=image_path, on_done=self.start_symbol_linker)

    def start_symbol_linker(self):
        self.clear_frame()
        self.current_frame = SymbolLinker(self.container, image_path=self.image_path,
                                          legend_bbox_path="legend_symbols/legend_bbox.json",
                                          on_done=self.end_workflow)

    def end_workflow(self):
        print("✅ Linked. Ready to return to full view.")

    def run(self):
        self.root.mainloop()
