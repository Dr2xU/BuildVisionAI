import cv2
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
import os
import json
import logging
from utils.state_manager import state

logger = logging.getLogger(__name__)

class LegendSelector:
    def __init__(self, root, image_path, on_done=None):
        self.root = root
        self.on_done = on_done
        self.image_path = image_path

        # Load image
        self.cv_image_full = cv2.imread(image_path)
        self.cv_image_full = cv2.cvtColor(self.cv_image_full, cv2.COLOR_BGR2RGB)
        self.original_size = self.cv_image_full.shape[1], self.cv_image_full.shape[0]

        # Scaling and centering
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.scale = min(screen_w / self.original_size[0], screen_h / self.original_size[1])
        self.offset = (0, 0)

        # State
        self.selection_box = None
        self.selecting = False
        self.legend_bbox_original = None
        self.zoomed = False

        # Canvas setup
        self.canvas = tk.Canvas(root, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.tk_image_ref = None
        self.image_on_canvas = None

        # Event bindings
        self.bind_events()
        self.canvas.focus_set()

        # Info label
        self.info_text = tk.Label(root, text="Select legend area → Press ENTER to zoom | ESC to quit",
                                  bg="black", fg="white", font=("Arial", 14))
        self.info_text.place(relx=0.5, rely=0.96, anchor=tk.S)

        self.render_image()

    def bind_events(self):
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        self.canvas.bind("<Escape>", lambda e: self.root.destroy())
        self.canvas.bind("c", self.reset_selection)
        self.canvas.bind("<Return>", self.confirm_selection)
        self.canvas.bind("i", self.zoom_in)
        self.canvas.bind("o", self.zoom_out)

        self.canvas.bind("<Configure>", self.render_image)

        # Global bindings to ensure arrow keys work
        self.root.bind_all("<Left>", lambda e: self.canvas.xview_scroll(-1, "units"))
        self.root.bind_all("<Right>", lambda e: self.canvas.xview_scroll(1, "units"))
        self.root.bind_all("<Up>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.root.bind_all("<Down>", lambda e: self.canvas.yview_scroll(1, "units"))

    def on_mouse_down(self, event):
        if self.legend_bbox_original or self.zoomed:
            return
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.selecting = True
        if self.selection_box:
            self.canvas.delete(self.selection_box)
        self.selection_box = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, outline="yellow", width=2
        )

    def on_mouse_drag(self, event):
        if self.selecting and self.selection_box:
            cur_x = self.canvas.canvasx(event.x)
            cur_y = self.canvas.canvasy(event.y)
            self.canvas.coords(self.selection_box, self.start_x, self.start_y, cur_x, cur_y)

    def on_mouse_up(self, event):
        self.selecting = False
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)

        ox, oy = self.offset
        scale = self.scale
        x1 = int((min(self.start_x, end_x) - ox) / scale)
        y1 = int((min(self.start_y, end_y) - oy) / scale)
        x2 = int((max(self.start_x, end_x) - ox) / scale)
        y2 = int((max(self.start_y, end_y) - oy) / scale)

        self.legend_bbox_original = (x1, y1, x2, y2)

        if self.selection_box:
            self.canvas.delete(self.selection_box)

        canvas_x1 = min(self.start_x, end_x)
        canvas_y1 = min(self.start_y, end_y)
        canvas_x2 = max(self.start_x, end_x)
        canvas_y2 = max(self.start_y, end_y)
        self.canvas.create_rectangle(canvas_x1, canvas_y1, canvas_x2, canvas_y2, outline="lime", width=2)

     

    def confirm_selection(self, event=None):
        if self.zoomed or not self.legend_bbox_original:
            return

        self.zoomed = True
        x1, y1, x2, y2 = self.legend_bbox_original
        crop = self.cv_image_full[y1:y2, x1:x2]
        h, w = crop.shape[:2]
        self.cv_image_full = crop
        self.original_size = (w, h)
        self.scale = min(self.root.winfo_width() / w, self.root.winfo_height() / h)

        self.legend_bbox_original = None
        self.selection_box = None
        self.render_image()

        # Save cropped image and bbox
        out_dir = state.config.get("paths", {}).get("legend_dir", "legend_symbols")
        os.makedirs(out_dir, exist_ok=True)

        image_path = os.path.join(out_dir, "legend_area.png")
        bbox_path = os.path.join(out_dir, "legend_bbox.json")

        try:
            cv2.imwrite(image_path, cv2.cvtColor(crop, cv2.COLOR_RGB2BGR))
            with open(bbox_path, "w") as f:
                json.dump({"x1": x1, "y1": y1, "x2": x2, "y2": y2}, f)

            logger.info(f"Legend saved to: {image_path} and {bbox_path}")
            state.legend_box = (x1, y1, x2, y2)
            state.config["legend_bbox_path"] = bbox_path
            state.image_path = self.image_path
            state.legend_path = image_path

            if self.on_done:
                self.on_done()

        except Exception as e:
            logger.error(f"Error saving legend data: {e}")

    def reset_selection(self, event=None):
        # Immediately reset all selection-related states
        self.legend_bbox_original = None
        self.zoomed = False
        self.selection_box = None
        # Render immediately with full image
        self.render_image()

    def render_image(self, event=None):
        w = max(1, int(self.original_size[0] * self.scale))
        h = max(1, int(self.original_size[1] * self.scale))
        resized = cv2.resize(self.cv_image_full, (w, h), interpolation=cv2.INTER_AREA)

        pil_image = Image.fromarray(resized)
        self.tk_image_ref = ImageTk.PhotoImage(pil_image)

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        offset_x = max((canvas_w - w) // 2, 0)
        offset_y = max((canvas_h - h) // 2, 0)
        self.offset = (offset_x, offset_y)

        if self.image_on_canvas:
            self.canvas.itemconfig(self.image_on_canvas, image=self.tk_image_ref)
            self.canvas.coords(self.image_on_canvas, offset_x, offset_y)
        else:
            self.image_on_canvas = self.canvas.create_image(offset_x, offset_y, anchor=tk.NW, image=self.tk_image_ref)

        self.canvas.image = self.tk_image_ref
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def zoom_in(self, event=None):
        self.scale *= 1.1
        self.render_image()

    def zoom_out(self, event=None):
        self.scale *= 0.9
        self.render_image()
