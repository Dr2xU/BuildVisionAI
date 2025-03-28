import tkinter as tk
from tkinter import filedialog, messagebox
import os
import logging

from utils.state_manager import state, WorkflowState
from utils.pdf_tools import convert_pdf_to_image

logger = logging.getLogger(__name__)

class WelcomeScreen(tk.Frame):
    def __init__(self, parent, on_file_selected):
        super().__init__(parent, bg="white")
        self.pack(fill=tk.BOTH, expand=True)
        self.on_file_selected = on_file_selected

        self.label = tk.Label(self, text="Welcome to Blueprint Analyzer",
                              fg="black", bg="white", font=("Arial", 20))
        self.label.pack(pady=30)

        self.test_btn = tk.Button(
            self,
            text="Upload Test Blueprint",
            font=("Arial", 12),
            command=lambda: self.upload_file("blueprints_images\Blueprint_page_1.png"),  # ✅ Replace path as needed
            bg="black", fg="white", width=25
        )
        self.test_btn.pack(pady=10)

        self.symbol_link_btn = tk.Button(
            self,
            text="Open Test Legend",
            font=("Arial", 12),
            command=self.open_symbol_linker_test,
            bg="green", fg="white", width=25
        )
        self.symbol_link_btn.pack(pady=10)


        self.upload_btn = tk.Button(self, text="Upload New Blueprint",
                                    font=("Arial", 12), command=self.upload_file,
                                    bg="black", fg="white", width=25)
        self.upload_btn.pack(pady=10)

        self.load_btn = tk.Button(self, text="Load Previous Session",
                                  font=("Arial", 12), command=self.load_session,
                                  bg="#444", fg="white", width=25)
        self.load_btn.pack(pady=10)

        self.status_label = tk.Label(self, text="", bg="white", fg="gray", font=("Arial", 12))
        self.status_label.pack(pady=20)


    def upload_file(self, file_path=None):
        if not file_path:
            file_path = filedialog.askopenfilename(filetypes=[
                ("Supported Files", "*.png *.jpg *.jpeg *.pdf"),
                ("Image Files", "*.png *.jpg *.jpeg"),
                ("PDF Files", "*.pdf")
            ])
        if file_path:
            self.update_status("Loading file...")

            if file_path.lower().endswith(".pdf"):
                logger.info(f"PDF uploaded: {file_path}")
                self.update_status("Converting PDF to image...")

                try:
                    converted = convert_pdf_to_image(file_path)
                    if not converted:
                        messagebox.showerror("Conversion Error", "Could not convert PDF to image.")
                        self.update_status("")
                        return
                    file_path = converted
                    logger.info(f"Converted to image: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to convert PDF: {e}")
                    messagebox.showerror("Error", f"Failed to convert PDF:\n{e}")
                    self.update_status("")
                    return

            state.image_path = file_path
            state.legend_path = None
            logger.info(f"Image selected: {file_path}")
            self.update_status("Opening blueprint...")
            self.destroy()
            self.on_file_selected(file_path)

    def open_symbol_linker_test(self):
        from ui.symbol_linker import SymbolLinker  # ensure this is correct
        legend_path = "legend_symbols/legend_area.png"  # ✅ your specific test path
        state.legend_path = legend_path
        state.image_path = None  # Clear blueprint if only legend is to be used
        self.destroy()
        SymbolLinker(self.master, image_path=legend_path).root.mainloop()



    def load_session(self):
        session_path = filedialog.askopenfilename(filetypes=[("Session Files", "*.json")])
        if session_path and os.path.exists(session_path):
            self.update_status("Loading session...")
            try:
                loaded_state = WorkflowState.from_json(session_path)
                state.__dict__.update(loaded_state.__dict__)
                logger.info(f"Session loaded from: {session_path}")
                self.update_status("Opening blueprint...")
                self.destroy()
                self.on_file_selected(state.image_path)
            except Exception as e:
                logger.error(f"Failed to load session: {e}")
                messagebox.showerror("Error", f"Failed to load session:\n{e}")
                self.update_status("")


    def update_status(self, message):
        self.status_label.config(text=message)
        self.status_label.update_idletasks()
