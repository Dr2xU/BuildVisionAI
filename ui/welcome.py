import tkinter as tk
from tkinter import filedialog

class WelcomeScreen(tk.Frame):
    def __init__(self, parent, on_file_selected):
        super().__init__(parent, bg="white")
        self.pack(fill=tk.BOTH, expand=True)

        self.label = tk.Label(self, text="Welcome! Please upload your blueprint file.",
                              fg="black", bg="white", font=("Arial", 20))
        self.label.pack(pady=30)

        self.upload_btn = tk.Button(self, text="Upload Blueprint", font=("Arial", 12),
                                    command=self.upload_file, bg="black", fg="white")
        self.upload_btn.pack(pady=10)

        self.on_file_selected = on_file_selected

    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            self.destroy()
            self.on_file_selected(file_path)
