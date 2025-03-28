import tkinter as tk
from tkinter import Toplevel
from PIL import Image, ImageTk
import cv2
import numpy as np
import pytesseract
import json
import os
import logging
from utils.image_tools import detect_symbols, detect_text
from utils.state_manager import state


class SymbolLinker:
    def __init__(self, root, image_path=None, on_done=None):
        self.root = root
        toplevel = self.root.winfo_toplevel()
        toplevel.title("Link Symbols to Labels")
        toplevel.attributes("-fullscreen", True)

        self.on_done = on_done

        legend_path = state.legend_path or image_path
        if not legend_path or not os.path.exists(legend_path):
            raise FileNotFoundError(f"Legend image not found at {legend_path}")

        self.legend_crop = cv2.imread(legend_path)
        self.legend_crop = cv2.cvtColor(self.legend_crop, cv2.COLOR_BGR2RGB)
        self.zoom_factor = 1.0

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.main_frame, bg="white", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.side_panel = tk.Frame(self.main_frame, width=500, bg="black")
        self.side_panel.pack(side=tk.RIGHT, fill=tk.Y)

        self.tk_image = None
        self.image_on_canvas = None

        self.image_x_offset = 0
        self.image_y_offset = 0
        self.image_scale = 1.0

        self.links = []
        self.visual_elements = []  # List of drawn canvas items per link
        self.current_symbol = None
        self.selection_box = None
        self.start_x = self.start_y = 0
        self.selecting = False
        self.detection_mode = "symbol"

        self.setup_controls()
        self.bind_keys()
        self.root.after(50, self.render_image)
        self.root.bind("<Escape>", self.exit_application)

        logging.info(f"Legend loaded from: {legend_path}")

    def setup_controls(self):
        ctrl = tk.Frame(self.side_panel, bg="gray20")
        ctrl.pack(fill=tk.X, pady=10)

        tk.Button(ctrl, text="🧽 Clear Last", command=self.clear_last).pack(pady=2, fill=tk.X)
        tk.Button(ctrl, text="❌ Clear All", command=self.clear_all).pack(pady=2, fill=tk.X)
        tk.Button(ctrl, text="↩ Save & Exit", command=self.save_and_continue).pack(pady=2, fill=tk.X)
        self.link_table = tk.Listbox(self.side_panel, bg="white", fg="black")
        self.link_table.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def bind_keys(self):
        self.canvas.bind("i", self.zoom_in)
        self.canvas.bind("o", self.zoom_out)
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

    def exit_application(self, event=None):
        logging.info("Exiting application")
        self.root.quit()

    def render_image(self):
        canvas_width = self.root.winfo_width() - 500
        canvas_height = self.root.winfo_height()
        h, w = self.legend_crop.shape[:2]
        aspect = w / h

        if canvas_width / aspect > canvas_height:
            fit_w = int(canvas_height * aspect)
            fit_h = canvas_height
        else:
            fit_w = canvas_width
            fit_h = int(canvas_width / aspect)

        resized = cv2.resize(self.legend_crop, (fit_w, fit_h), interpolation=cv2.INTER_AREA)
        self.display_crop = resized.copy()
        self.image_scale = self.legend_crop.shape[1] / fit_w
        self.image_x_offset = (canvas_width - fit_w) // 2 + 250
        self.image_y_offset = (canvas_height - fit_h) // 2

        self.canvas.delete("all")
        self.tk_image = ImageTk.PhotoImage(Image.fromarray(self.display_crop))
        self.image_on_canvas = self.canvas.create_image(
            self.image_x_offset, self.image_y_offset, anchor=tk.NW, image=self.tk_image
        )
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.redraw_links()

    def redraw_links(self):
        for idx, link in enumerate(self.links):
            self.draw_link(link)

    def draw_link(self, link):
        sx, sy, sw, sh = link["symbol"]['rel_x'], link["symbol"]['rel_y'], link["symbol"]['w'], link["symbol"]['h']
        tx, ty, tw, th = link["text"]['rel_x'], link["text"]['rel_y'], link["text"]['w'], link["text"]['h']

        sx1 = sx / self.image_scale + self.image_x_offset
        sy1 = sy / self.image_scale + self.image_y_offset
        sx2 = (sx + sw) / self.image_scale + self.image_x_offset
        sy2 = (sy + sh) / self.image_scale + self.image_y_offset

        tx1 = tx / self.image_scale + self.image_x_offset
        ty1 = ty / self.image_scale + self.image_y_offset
        tx2 = (tx + tw) / self.image_scale + self.image_x_offset
        ty2 = (ty + th) / self.image_scale + self.image_y_offset

        rect1 = self.canvas.create_rectangle(sx1, sy1, sx2, sy2, outline="lime", width=2)
        rect2 = self.canvas.create_rectangle(tx1, ty1, tx2, ty2, outline="lime", width=2)

        line = self.canvas.create_line((sx + sw) / self.image_scale + self.image_x_offset,
                                (sy + sh // 2) / self.image_scale + self.image_y_offset,
                                (tx) / self.image_scale + self.image_x_offset,
                                (ty + th // 2) / self.image_scale + self.image_y_offset,
                                fill="red", width=2)
        
        self.visual_elements.append([rect1, rect2, line])

    def on_mouse_down(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.selecting = True
        if self.selection_box:
            self.canvas.delete(self.selection_box)
        self.selection_box = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="yellow", width=2)

    def on_mouse_drag(self, event):
        if self.selecting and self.selection_box:
            self.canvas.coords(self.selection_box, self.start_x, self.start_y, event.x, event.y)

    def on_mouse_up(self, event):
        self.selecting = False
        if self.selection_box:
            self.canvas.delete(self.selection_box)
            self.selection_box = None

        x1 = int((min(self.start_x, event.x) - self.image_x_offset) * self.image_scale)
        y1 = int((min(self.start_y, event.y) - self.image_y_offset) * self.image_scale)
        x2 = int((max(self.start_x, event.x) - self.image_x_offset) * self.image_scale)
        y2 = int((max(self.start_y, event.y) - self.image_y_offset) * self.image_scale)

        region = self.legend_crop[y1:y2, x1:x2]
        if region.size == 0:
            return

        if self.detection_mode == "symbol":
            _, symbols = detect_symbols(region)
            if not symbols:
                return
            min_x = min([s["X"] for s in symbols])
            min_y = min([s["Y"] for s in symbols])
            max_x = max([s["X"] + s["Width"] for s in symbols])
            max_y = max([s["Y"] + s["Height"] for s in symbols])

            symbol = {
                "rel_x": x1 + min_x,
                "rel_y": y1 + min_y,
                "w": max_x - min_x,
                "h": max_y - min_y
            }
            self.current_symbol = symbol

            sx1 = symbol["rel_x"] / self.image_scale + self.image_x_offset
            sy1 = symbol["rel_y"] / self.image_scale + self.image_y_offset
            sx2 = (symbol["rel_x"] + symbol["w"]) / self.image_scale + self.image_x_offset
            sy2 = (symbol["rel_y"] + symbol["h"]) / self.image_scale + self.image_y_offset
            rect = self.canvas.create_rectangle(sx1, sy1, sx2, sy2, outline="lime", width=2)
            self.visual_elements.append([rect])
            self.detection_mode = "text"

        elif self.detection_mode == "text" and self.current_symbol:
            texts = detect_text(region)
            if not texts:
                logging.warning("No text detected in the selected region")
                self.current_symbol = None
                return

            min_x = min([t["bounding_box"][0] for t in texts])
            min_y = min([t["bounding_box"][1] for t in texts])
            max_x = max([t["bounding_box"][2] for t in texts])
            max_y = max([t["bounding_box"][3] for t in texts])

            combined_text = " ".join(t["text"] for t in texts)

            text = {
                "text": combined_text,
                "rel_x": x1 + min_x,
                "rel_y": y1 + min_y,
                "w": max_x - min_x,
                "h": max_y - min_y
            }

            self.links.append({"symbol": self.current_symbol, "text": text})
            self.link_table.insert(tk.END, f"🔗 {text['text']}")
            self.draw_link({"symbol": self.current_symbol, "text": text})

            icon_crop = self.legend_crop[
                self.current_symbol["rel_y"]:self.current_symbol["rel_y"]+self.current_symbol["h"],
                self.current_symbol["rel_x"]:self.current_symbol["rel_x"]+self.current_symbol["w"]
            ]
            icon_dir = state.config.get("paths", {}).get("icon_dir", "symbol_icons")
            os.makedirs(icon_dir, exist_ok=True)
            safe_name = text["text"].strip().replace(" ", "_").replace("/", "-")
            icon_path = os.path.join(icon_dir, f"{safe_name}.png")
            cv2.imwrite(icon_path, icon_crop)

            self.detection_mode = "symbol"
            self.current_symbol = None

    def clear_last(self):
        if self.links and self.visual_elements:
            self.links.pop()
            elements = self.visual_elements.pop()
            for item in elements:
                self.canvas.delete(item)
            self.link_table.delete(tk.END)
            self.detection_mode = "symbol"

    def clear_all(self):
        self.links.clear()
        self.visual_elements.clear()
        self.link_table.delete(0, tk.END)
        self.render_image()
        self.detection_mode = "symbol"

    def save_and_continue(self):
        output_dir = state.config.get("paths", {}).get("output_dir", "symbol_links")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "links.json")
        try:
            with open(output_path, "w") as f:
                json.dump(self.links, f, indent=2)
            state.linked_items = self.links
            logging.info(f"Saved symbol-text links to {output_path}")
            if self.on_done:
                self.on_done()
            self.root.quit()
        except Exception as e:
            logging.error(f"Failed to save symbol links: {e}")

    def zoom_in(self, event=None):
        self.zoom_factor *= 1.1
        self.render_image()

    def zoom_out(self, event=None):
        self.zoom_factor /= 1.1
        self.render_image()

    def set_mode(self, mode):
        self.detection_mode = mode
        logging.info(f"Detection mode set to: {mode}")