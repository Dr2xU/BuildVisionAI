import cv2
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
import os
import json
from ui.symbol_linker import SymbolLinker

class LegendSelector:
    def __init__(self, root, image_path, on_done=None):
        # Setup window and inputs
        self.root = root
        self.on_done = on_done
        self.image_path = image_path

        # Load image and convert to RGB
        self.cv_image_full = cv2.imread(image_path)
        self.cv_image_full = cv2.cvtColor(self.cv_image_full, cv2.COLOR_BGR2RGB)
        self.original_size = self.cv_image_full.shape[1], self.cv_image_full.shape[0]

        # Initial offset and scale (for centering and zoom) 
        self.offset = (0, 0)
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.scale = min(screen_w / self.original_size[0], screen_h / self.original_size[1])
        self.display_size = (int(self.original_size[0] * self.scale), int(self.original_size[1] * self.scale))

        # State variables
        self.start_x = self.start_y = 0  # Mouse start point
        self.selection_box = None        # Rectangle visual
        self.selecting = False           # Mouse drag in progress
        self.legend_bbox_original = None # (x1, y1, x2, y2) in original coords
        self.zoomed = False              # Zoomed into selected area

         # Create canvas to display image
        self.canvas = tk.Canvas(root, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.tk_image_ref = None         # To avoid garbage collection
        self.image_on_canvas = None      # Tkinter image item

        # Mouse bindings for selection
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        # Keyboard shortcuts
        self.canvas.bind("<Escape>", lambda e: root.destroy())       # Exit app
        self.canvas.bind("c", self.reset_selection)                  # Cancel selection
        self.canvas.bind("<Return>", self.confirm_selection)         # Confirm selection
        self.canvas.bind("i", self.zoom_in)                          # Zoom in
        self.canvas.bind("o", self.zoom_out)                         # Zoom out

        # Arrow keys for scrolling
        self.canvas.bind("<Up>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Down>", lambda e: self.canvas.yview_scroll(1, "units"))
        self.canvas.bind("<Left>", lambda e: self.canvas.xview_scroll(-1, "units"))
        self.canvas.bind("<Right>", lambda e: self.canvas.yview_scroll(1, "units"))
        
        # Redraw image if window resizes
        self.canvas.bind("<Configure>", self.render_image)
        self.canvas.focus_set()

        # Info label at the bottom
        self.info_text = tk.Label(root, text="Select legend area → Press ENTER to zoom | ESC to quit",
                                  bg="black", fg="white", font=("Arial", 14))
        self.info_text.place(relx=0.5, rely=0.96, anchor=tk.S)

        # Initial render
        self.render_image()

    def on_mouse_down(self, event):
        # Prevent multiple selections
        if self.legend_bbox_original or self.zoomed:
            return
        
        # Start drawing a rectangle
        self.start_x, self.start_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.selecting = True
        if self.selection_box:
            self.canvas.delete(self.selection_box)
        self.selection_box = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, outline="yellow", width=2
        )

    def on_mouse_drag(self, event):
        # Update selection box while dragging
        if self.selecting and self.selection_box:
            cur_x = self.canvas.canvasx(event.x)
            cur_y = self.canvas.canvasy(event.y)
            self.canvas.coords(self.selection_box, self.start_x, self.start_y, cur_x, cur_y)

    def on_mouse_up(self, event):
         # Finalize selection box and convert to original image coords
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

        self.render_image()

    def confirm_selection(self, event=None):
        # Confirm the selected legend, crop it, center it, and trigger the next step
        if self.zoomed or not self.legend_bbox_original:
            return
        
        self.zoomed = True
        x1, y1, x2, y2 = self.legend_bbox_original

        # Crop and zoom in
        crop = self.cv_image_full[y1:y2, x1:x2]
        h, w = crop.shape[:2]
        self.cv_image_full = crop
        self.original_size = (w, h)
        self.scale = min(self.root.winfo_width() / w, self.root.winfo_height() / h)

        # Clear selection and re-render
        self.legend_bbox_original = None
        self.selection_box = None
        self.render_image()

        # Save cropped area and coordinates
        os.makedirs("legend_symbols", exist_ok=True)
        cv2.imwrite("legend_symbols/legend_area.png", cv2.cvtColor(crop, cv2.COLOR_RGB2BGR))
        with open("legend_symbols/legend_bbox.json", "w") as f:
            json.dump({"x1": x1, "y1": y1, "x2": x2, "y2": y2}, f)

        # Proceed to next class (e.g., SymbolLinker)
        if self.on_done:
            self.on_done()

    def reset_selection(self, event=None):
        # Cancel selection and restore original image and scale
        self.legend_bbox_original = None
        self.zoomed = False
        self.selection_box = None
        self.cv_image_full = cv2.imread(self.image_path)
        self.cv_image_full = cv2.cvtColor(self.cv_image_full, cv2.COLOR_BGR2RGB)
        self.original_size = self.cv_image_full.shape[1], self.cv_image_full.shape[0]
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.scale = min(screen_w / self.original_size[0], screen_h / self.original_size[1])
        self.render_image()

    def render_image(self, event=None):
        # Resize and render the image, apply blur to non-selected regions
        w = max(1, int(self.original_size[0] * self.scale))
        h = max(1, int(self.original_size[1] * self.scale))
        resized = cv2.resize(self.cv_image_full, (w, h), interpolation=cv2.INTER_AREA)

        # Apply blur outside the selected area
        if self.legend_bbox_original and not self.zoomed:
            x1, y1, x2, y2 = self.legend_bbox_original
            sx1 = int(x1 * self.scale)
            sy1 = int(y1 * self.scale)
            sx2 = int(x2 * self.scale)
            sy2 = int(y2 * self.scale)

            mask = np.zeros((h, w), dtype=np.uint8)
            cv2.rectangle(mask, (sx1, sy1), (sx2, sy2), 255, -1)
            blurred = cv2.GaussianBlur(resized, (31, 31), 0)
            region = cv2.bitwise_and(resized, resized, mask=mask)
            bg = cv2.bitwise_and(blurred, blurred, mask=cv2.bitwise_not(mask))
            resized = cv2.add(region, bg)

        # Convert to Tkinter image
        pil_image = Image.fromarray(resized)
        self.tk_image_ref = ImageTk.PhotoImage(pil_image)

        # Center image on canvas
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
        # Zoom in
        self.scale *= 1.1
        self.render_image()

    def zoom_out(self, event=None):
        # Zoom out
        self.scale *= 0.9
        self.render_image()
