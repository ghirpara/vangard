"""
    An experimental Tkinter-based image viewer application.
    Always shows a thumbnail pane on the left and a full-size image pane on the right.
    Both panes are individually scrollable, and the main image pane supports arrow key scrolling.

    
    AI Warning: This code has been generated in part or in whole by Google Gemini using the gemini-2.5-flash-preview-05-20 model. 

"""

import tkinter as tk
from tkinter import messagebox, PanedWindow, VERTICAL, HORIZONTAL, SUNKEN
import os
from PIL import Image, ImageTk, UnidentifiedImageError
import glob
import argparse

class ImageViewerApp:
    def __init__(self, root, initial_glob_pattern=None):
        self.root = root
        self.root.title("Image Viewer")

        self.image_paths = []
        self.images = []
        self.full_size_photo_cache = {}
        self.thumbnail_photo_images = []

        self.current_image_index = 0
        self.thumbnail_size = (128, 128)
        # Changed to represent "how many units" to scroll
        self.scroll_amount_units = 1 
        
        # --- UI Elements ---

        # 1. Control Frame (Glob Pattern Input & Load Button)
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(pady=10, fill=tk.X)

        tk.Label(self.control_frame, text="Glob Pattern:").pack(side=tk.LEFT, padx=5)
        self.glob_entry = tk.Entry(self.control_frame, width=50)
        self.glob_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        default_pattern = "**/*.{jpg,jpeg,png,gif,bmp,tiff}"
        self.glob_entry.insert(0, initial_glob_pattern if initial_glob_pattern else default_pattern) 

        self.load_button = tk.Button(self.control_frame, text="Load Images", command=self.load_images)
        self.load_button.pack(side=tk.LEFT, padx=5)

        # 2. Main Paned Window (holds thumbnail pane and image display pane)
        self.main_paned_window = PanedWindow(root, orient=HORIZONTAL, sashwidth=5, sashrelief=SUNKEN)
        self.main_paned_window.pack(fill=tk.BOTH, expand=True)

        # 2a. Thumbnail Pane (left) - ALWAYS PRESENT
        self.thumbnail_pane = tk.Frame(self.main_paned_window, bd=2, relief=SUNKEN, bg="#2c2c2c")
        self.main_paned_window.add(self.thumbnail_pane)
        
        self.thumbnail_canvas = tk.Canvas(self.thumbnail_pane, bg="#2c2c2c", bd=0, highlightthickness=0)
        self.thumbnail_v_scrollbar = tk.Scrollbar(self.thumbnail_pane, orient=VERTICAL, command=self.thumbnail_canvas.yview)
        self.thumbnail_h_scrollbar = tk.Scrollbar(self.thumbnail_pane, orient=HORIZONTAL, command=self.thumbnail_canvas.xview)
        
        self.thumbnail_v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.thumbnail_h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.thumbnail_canvas.pack(fill=tk.BOTH, expand=True)
        self.thumbnail_canvas.config(yscrollcommand=self.thumbnail_v_scrollbar.set, xscrollcommand=self.thumbnail_h_scrollbar.set)
        
        # 2b. Image Display Pane (right) - ALWAYS PRESENT
        self.image_display_pane = tk.Frame(self.main_paned_window, bd=2, relief=SUNKEN, bg="black")
        self.main_paned_window.add(self.image_display_pane)
        
        self.image_canvas = tk.Canvas(self.image_display_pane, bg="black", bd=0, highlightthickness=0)
        
        self.image_v_scrollbar = tk.Scrollbar(self.image_display_pane, orient=VERTICAL, command=self.image_canvas.yview)
        self.image_h_scrollbar = tk.Scrollbar(self.image_display_pane, orient=HORIZONTAL, command=self.image_canvas.xview)
        
        self.image_v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.image_h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.image_canvas.pack(fill=tk.BOTH, expand=True)
        self.image_canvas.config(yscrollcommand=self.image_v_scrollbar.set, xscrollcommand=self.image_h_scrollbar.set)

        # 3. Navigation Buttons
        self.nav_frame = tk.Frame(root)
        self.nav_frame.pack(pady=10, fill=tk.X)

        self.prev_button = tk.Button(self.nav_frame, text="Previous", command=self.show_prev_image)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.next_button = tk.Button(self.nav_frame, text="Next", command=self.show_next_image)
        self.next_button.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(self.nav_frame, text="", fg="gray")
        self.status_label.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)

        self.update_status()

        self.image_canvas.bind("<Configure>", self.on_image_canvas_resize)
        self.thumbnail_canvas.bind("<Configure>", self.on_thumbnail_canvas_resize)

        # Bind arrow key events to the main image canvas for scrolling
        # Unit changed from 'pixels' to 'units'
        self.image_canvas.bind("<Left>", self._scroll_image_left)
        self.image_canvas.bind("<Right>", self._scroll_image_right)
        self.image_canvas.bind("<Up>", self._scroll_image_up)
        self.image_canvas.bind("<Down>", self._scroll_image_down)
        self.image_canvas.bind("<MouseWheel>", self._scroll_image_mousewheel) # Windows/macOS
        self.image_canvas.bind("<Button-4>", self._scroll_image_mousewheel)  # Linux (scroll up)
        self.image_canvas.bind("<Button-5>", self._scroll_image_mousewheel)  # Linux (scroll down)

        try:
            self.main_paned_window.paneconfigure(self.thumbnail_pane, weight=1, minsize=150)
            self.main_paned_window.paneconfigure(self.image_display_pane, weight=4)
        except tk.TclError:
            print("Warning: 'weight' and 'minsize' options for PanedWindow not supported by your Tk version. Panes will resize equally.")


    def on_image_canvas_resize(self, event=None):
        if self.images:
            self.display_current_image()

    def on_thumbnail_canvas_resize(self, event=None):
        if self.images:
            self.display_thumbnails()

    def load_images(self):
        glob_pattern = self.glob_entry.get()
        self.image_paths = []
        self.images = []
        self.full_size_photo_cache = {}
        self.thumbnail_photo_images = []

        found_files = glob.glob(glob_pattern, recursive=True) 
        found_files.sort()

        if not found_files:
            messagebox.showinfo("No Images", f"No files found matching pattern: {glob_pattern}")
            self.update_status()
            self.clear_canvas(self.image_canvas)
            self.clear_canvas(self.thumbnail_canvas)
            return

        valid_images_found = False
        for f_path in found_files:
            try:
                img = Image.open(f_path)
                if img.mode not in ['RGB', 'RGBA']:
                    img = img.convert('RGB')
                self.images.append(img)
                self.image_paths.append(f_path)
                valid_images_found = True
            except UnidentifiedImageError:
                print(f"Skipping non-image or corrupted file: {f_path}")
            except Exception as e:
                print(f"An unexpected error occurred with file {f_path}: {e}")

        if not valid_images_found:
            messagebox.showinfo("No Valid Images", f"No valid image files could be loaded from pattern: {glob_pattern}")
            self.update_status()
            self.clear_canvas(self.image_canvas)
            self.clear_canvas(self.thumbnail_canvas)
            return

        self.current_image_index = 0
        self.display_current_image()
        self.display_thumbnails()

        self.update_status()

    def clear_canvas(self, canvas):
        canvas.delete("all")
        canvas.config(scrollregion=(0,0,0,0))

    def display_current_image(self):
        if not self.images:
            self.clear_canvas(self.image_canvas)
            return

        img = self.images[self.current_image_index]
        self.clear_canvas(self.image_canvas)

        img_width, img_height = img.size
        
        max_display_size = (3000, 3000)

        if img_width > max_display_size[0] or img_height > max_display_size[1]:
            ratio = min(max_display_size[0] / img_width, max_display_size[1] / img_height)
            display_img = img.resize((int(img_width * ratio), int(img_height * ratio)), Image.LANCZOS)
            display_width, display_height = display_img.size
            print(f"Image {os.path.basename(self.image_paths[self.current_image_index])} scaled down for display: {img_width}x{img_height} -> {display_width}x{display_height}")
        else:
            display_img = img
            display_width, display_height = img_width, img_height

        cache_key = (self.current_image_index, display_img.size)
        if cache_key not in self.full_size_photo_cache:
            self.full_size_photo_cache[cache_key] = ImageTk.PhotoImage(display_img)
        
        current_photo = self.full_size_photo_cache[cache_key]
        
        self.image_canvas.create_image(0, 0, anchor=tk.NW, image=current_photo)
        self.image_canvas.image_on_canvas = current_photo

        self.image_canvas.config(scrollregion=(0, 0, display_width, display_height))

        self.image_canvas.focus_set()
        
        self.image_canvas.xview_moveto(0)
        self.image_canvas.yview_moveto(0)
        
        self.update_status()

    def show_next_image(self):
        if self.images:
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
            self.display_current_image()

    def show_prev_image(self):
        if self.images:
            self.current_image_index = (self.current_image_index - 1 + len(self.images)) % len(self.images)
            self.display_current_image()

    def update_status(self):
        if self.images:
            current_file = os.path.basename(self.image_paths[self.current_image_index])
            status_text = f"{current_file} ({self.current_image_index + 1}/{len(self.images)}) | Total: {len(self.images)} images."
            self.status_label.config(text=status_text)
            
            self.prev_button.config(state=tk.NORMAL)
            self.next_button.config(state=tk.NORMAL)
        else:
            self.status_label.config(text="No images loaded.")
            self.prev_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)

    def display_thumbnails(self):
        self.clear_canvas(self.thumbnail_canvas)
        self.thumbnail_photo_images = []

        if not self.images:
            return

        canvas_width = self.thumbnail_canvas.winfo_width()
        if canvas_width <= 1: 
            canvas_width = self.thumbnail_pane.winfo_width()
            if canvas_width <=1: canvas_width = 250

        thumb_total_width = self.thumbnail_size[0] + 20 
        thumbnail_cols = max(1, (canvas_width - 20) // thumb_total_width) 
        thumbnail_cols = max(1, min(thumbnail_cols, 10))

        x_offset = 10
        y_offset = 10
        col_count = 0
        row_count = 0
        
        filename_font = ("Arial", 8)

        for i, img in enumerate(self.images):
            thumb = img.copy() 
            thumb.thumbnail(self.thumbnail_size, Image.LANCZOS)
            photo = ImageTk.PhotoImage(thumb)
            self.thumbnail_photo_images.append(photo)

            x_pos = x_offset + (col_count * thumb_total_width)
            y_pos = y_offset + (row_count * (self.thumbnail_size[1] + 25))

            self.thumbnail_canvas.create_image(x_pos, y_pos, anchor=tk.NW, image=photo, tags=f"thumb_{i}")
            
            filename = os.path.basename(self.image_paths[i])
            if len(filename) > 20: 
                 filename = filename[:17] + "..."

            self.thumbnail_canvas.create_text(x_pos + self.thumbnail_size[0] / 2, y_pos + self.thumbnail_size[1] + 5,
                                           text=filename, anchor=tk.N, font=filename_font, fill="white",
                                           tags=f"thumb_{i}_text", width=self.thumbnail_size[0])

            self.thumbnail_canvas.tag_bind(f"thumb_{i}", "<Button-1>", lambda event, idx=i: self.select_thumbnail(idx))
            self.thumbnail_canvas.tag_bind(f"thumb_{i}_text", "<Button-1>", lambda event, idx=i: self.select_thumbnail(idx))

            col_count += 1
            if col_count >= thumbnail_cols:
                col_count = 0
                row_count += 1

        total_grid_width = thumbnail_cols * thumb_total_width + x_offset
        total_grid_height = (row_count + (1 if col_count > 0 else 0)) * (self.thumbnail_size[1] + 25) + y_offset

        self.thumbnail_canvas.config(scrollregion=(0, 0, max(canvas_width, total_grid_width), max(self.thumbnail_canvas.winfo_height(), total_grid_height)))


    def select_thumbnail(self, index):
        self.current_image_index = index
        self.display_current_image()

    # --- Keyboard Scrolling Methods ---
    def _scroll_image_left(self, event):
        self.image_canvas.xview_scroll(-1 * self.scroll_amount_units, 'units') # Changed to 'units'
        return "break"

    def _scroll_image_right(self, event):
        self.image_canvas.xview_scroll(self.scroll_amount_units, 'units') # Changed to 'units'
        return "break"

    def _scroll_image_up(self, event):
        self.image_canvas.yview_scroll(-1 * self.scroll_amount_units, 'units') # Changed to 'units'
        return "break"

    def _scroll_image_down(self, event):
        self.image_canvas.yview_scroll(self.scroll_amount_units, 'units') # Changed to 'units'
        return "break"
    
    def _scroll_image_mousewheel(self, event):
        # Mousewheel already uses 'units' so no change needed here
        if event.num == 5 or event.delta == -120:  # Wheel down (Windows/macOS delta, Linux Button-5)
            self.image_canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta == 120:  # Wheel up (Windows/macOS delta, Linux Button-4)
            self.image_canvas.yview_scroll(-1, "units")
        return "break"


# Main execution block
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Image Viewer Application")
    
    parser.add_argument(
        '--pattern',
        type=str,
        default=None,
        help="Glob pattern for image files (e.g., 'images/*.jpg', '**/*.png')"
    )
    
    args = parser.parse_args()

    root = tk.Tk()
    root.geometry("1024x768")
    root.tk_setPalette(background='#333333', foreground='white', 
                       activeBackground='#555555', activeForeground='white')
    
    app = ImageViewerApp(root, initial_glob_pattern=args.pattern)
    
    if args.pattern:
        root.update_idletasks()
        app.load_images()
    
    root.mainloop()