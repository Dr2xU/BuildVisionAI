import tkinter as tk
from PIL import Image, ImageTk
import cv2
import numpy as np
import pytesseract
import json
import os
from utils.image_tools import detect_symbols

class SymbolLinker:
    def __init__(self, root, image_path, legend_bbox_path, on_done=None):
        self.root = root
        self.root.title("Link Symbols to Labels")
        self.root.attributes("-fullscreen", True)
        self.on_done = on_done

        # Load original image and bbox
        self.original_image = cv2.imread(image_path)
        self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        with open(legend_bbox_path, "r") as f:
            bbox = json.load(f)
        self.bbox = bbox
        self.x1, self.y1, self.x2, self.y2 = bbox["x1"], bbox["y1"], bbox["x2"], bbox["y2"]

        # Crop and prepare display image
        self.legend_crop = self.original_image[self.y1:self.y2, self.x1:self.x2]
        self.zoom_factor = 1.0

        self.canvas = tk.Canvas(root, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.tk_image = None
        self.image_on_canvas = None

        self.symbols = []
        self.text_links = []
        self.current_symbol = None
        self.selection_box = None
        self.start_x = self.start_y = 0
        self.selecting_text = False

        self.setup_controls()
        self.bind_keys()
        self.render_image()

    def setup_controls(self):
        self.control_frame = tk.Frame(self.root, bg="black")
        self.control_frame.place(relx=0.01, rely=0.01)
        tk.Button(self.control_frame, text="🧽 Clear Last", command=self.clear_last).pack(pady=2)
        tk.Button(self.control_frame, text="❌ Clear All", command=self.clear_all).pack(pady=2)
        tk.Button(self.control_frame, text="↩ Save & Exit", command=self.save_and_continue).pack(pady=2)

    def bind_keys(self):
        self.canvas.bind("+", self.zoom_in)
        self.canvas.bind("-", self.zoom_out)
        self.canvas.bind("<Up>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Down>", lambda e: self.canvas.yview_scroll(1, "units"))
        self.canvas.bind("<Left>", lambda e: self.canvas.xview_scroll(-1, "units"))
        self.canvas.bind("<Right>", lambda e: self.canvas.xview_scroll(1, "units"))
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<ButtonPress-3>", self.start_text_area)
        self.canvas.bind("<B3-Motion>", self.drag_text_area)
        self.canvas.bind("<ButtonRelease-3>", self.ocr_text_area)

    def render_image(self):
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        aspect = self.legend_crop.shape[1] / self.legend_crop.shape[0]
        fit_w = screen_w
        fit_h = int(fit_w / aspect)
        if fit_h > screen_h:
            fit_h = screen_h
            fit_w = int(fit_h * aspect)

        resized = cv2.resize(self.legend_crop, (fit_w, fit_h), interpolation=cv2.INTER_AREA)
        self.display_crop = resized.copy()
        self.display_scale = fit_w / (self.x2 - self.x1)

        for sym in self.symbols:
            sx, sy, sw, sh = sym["rel_x"], sym["rel_y"], sym["w"], sym["h"]
            cv2.rectangle(self.display_crop, (sx, sy), (sx + sw, sy + sh), (0, 255, 255), 2)
        for link in self.text_links:
            lx, ly, lw, lh = link["rel_x"], link["rel_y"], link["w"], link["h"]
            cv2.rectangle(self.display_crop, (lx, ly), (lx + lw, ly + lh), (0, 255, 0), 2)
            cv2.putText(self.display_crop, link["text"], (lx, ly - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        pil_img = Image.fromarray(self.display_crop)
        self.tk_image = ImageTk.PhotoImage(pil_img)
        self.canvas.delete("all")
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        offset_x = (canvas_w - fit_w) // 2
        offset_y = (canvas_h - fit_h) // 2
        self.image_on_canvas = self.canvas.create_image(offset_x, offset_y, anchor=tk.NW, image=self.tk_image)

    def on_click(self, event):
        x = int(event.x / self.display_scale)
        y = int(event.y / self.display_scale)
        box_size = int(50 / self.display_scale)
        cropped = self.legend_crop[max(0, y - box_size): y + box_size, max(0, x - box_size): x + box_size]
        _, candidates = detect_symbols(cropped)
        if candidates:
            c = candidates[0]
            abs_x = max(0, x - box_size) + c["X"]
            abs_y = max(0, y - box_size) + c["Y"]
            sym = {
                "rel_x": int(abs_x * self.display_scale),
                "rel_y": int(abs_y * self.display_scale),
                "x": abs_x + self.x1,
                "y": abs_y + self.y1,
                "w": int(c["Width"] * self.display_scale),
                "h": int(c["Height"] * self.display_scale),
            }
            self.symbols.append(sym)
            self.current_symbol = sym
            self.render_image()

    def start_text_area(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.selecting_text = True
        if self.selection_box:
            self.canvas.delete(self.selection_box)
        self.selection_box = self.canvas.create_rectangle(event.x, event.y, event.x, event.y,
                                                          outline="green", width=2)

    def drag_text_area(self, event):
        if self.selecting_text and self.selection_box:
            self.canvas.coords(self.selection_box, self.start_x, self.start_y, event.x, event.y)

    def ocr_text_area(self, event):
        self.selecting_text = False
        x1, y1 = int(min(self.start_x, event.x)), int(min(self.start_y, event.y))
        x2, y2 = int(max(self.start_x, event.x)), int(max(self.start_y, event.y))
        crop = self.display_crop[y1:y2, x1:x2]
        gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
        text = pytesseract.image_to_string(gray, config="--psm 6").strip()

        if text and self.current_symbol:
            self.text_links.append({
                "text": text,
                "symbol": self.current_symbol,
                "rel_x": x1,
                "rel_y": y1,
                "w": x2 - x1,
                "h": y2 - y1
            })
            self.current_symbol = None
            self.render_image()

        if self.selection_box:
            self.canvas.delete(self.selection_box)
            self.selection_box = None

    def clear_last(self):
        if self.text_links:
            self.text_links.pop()
        elif self.symbols:
            self.symbols.pop()
        self.render_image()

    def clear_all(self):
        self.symbols.clear()
        self.text_links.clear()
        self.render_image()

    def save_and_continue(self):
        os.makedirs("symbol_links", exist_ok=True)
        with open("symbol_links/links.json", "w") as f:
            json.dump(self.text_links, f, indent=2)
        if self.on_done:
            self.on_done()