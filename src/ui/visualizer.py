import tkinter as tk
import customtkinter as ctk

class PaletteVisualizer(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Internal state
        self.palette = [(255, 255, 255)] * 256 # Default white
        self.selected_indices = set()
        self.rect_ids = [] # To store canvas object IDs
        self.cell_size = 20
        self.grid_size = 16 # 16x16 = 256
        
        # UI Elements
        self.canvas_width = self.cell_size * self.grid_size
        self.canvas_height = self.cell_size * self.grid_size
        
        self.canvas = ctk.CTkCanvas(
            self, 
            width=self.canvas_width, 
            height=self.canvas_height,
            bg="#2b2b2b", 
            highlightthickness=0
        )
        self.canvas.grid(row=0, column=0, padx=10, pady=10)
        
        # Info Label
        self.info_label = ctk.CTkLabel(self, text="Hover over a color", text_color="gray")
        self.info_label.grid(row=1, column=0, pady=(0, 10))
        
        # Events
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<Motion>", self._on_hover)
        
        # Initial draw
        self._init_grid()
        
    def _init_grid(self):
        self.rect_ids = []
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                x1 = x * self.cell_size
                y1 = y * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                rect_id = self.canvas.create_rectangle(
                    x1, y1, x2, y2, 
                    fill="#ffffff", 
                    outline="#404040"
                )
                self.rect_ids.append(rect_id)
                
    def set_palette(self, palette_data):
        if len(palette_data) != 256:
            print("Warning: Palette data must have 256 colors.")
            return
            
        self.palette = palette_data
        
        # Update canvas background to index 0 color
        bg_color = palette_data[0] if palette_data else (43, 43, 43)
        bg_hex = f"#{bg_color[0]:02x}{bg_color[1]:02x}{bg_color[2]:02x}"
        self.canvas.configure(bg=bg_hex)
        
        self._redraw_colors()
        
    def _redraw_colors(self):
        for i, color in enumerate(self.palette):
            r, g, b = color
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            
            # Check if selected
            outline = "#00ff00" if i in self.selected_indices else "#404040"
            width = 2 if i in self.selected_indices else 1
            
            self.canvas.itemconfig(
                self.rect_ids[i], 
                fill=hex_color, 
                outline=outline,
                width=width
            )

    def _get_index_at_pos(self, x, y):
        col = x // self.cell_size
        row = y // self.cell_size
        
        if 0 <= col < self.grid_size and 0 <= row < self.grid_size:
            return row * self.grid_size + col
        return None

    def _on_click(self, event):
        idx = self._get_index_at_pos(event.x, event.y)
        if idx is not None:
            # Toggle selection logic for single click
            # If Ctrl is held (not implemented here for simplicity yet), we could append
            # For now, let's implement toggle behavior
            if idx in self.selected_indices:
                self.selected_indices.remove(idx)
            else:
                self.selected_indices.add(idx)
            self._update_single_cell(idx)
            
    def _on_drag(self, event):
        idx = self._get_index_at_pos(event.x, event.y)
        if idx is not None:
             # Dragging adds to selection
            if idx not in self.selected_indices:
                self.selected_indices.add(idx)
                self._update_single_cell(idx)
                
    def _on_hover(self, event):
        idx = self._get_index_at_pos(event.x, event.y)
        if idx is not None:
            r, g, b = self.palette[idx]
            self.info_label.configure(text=f"Index: {idx} | RGB: ({r}, {g}, {b}) | Hex: #{r:02x}{g:02x}{b:02x}")
        else:
            self.info_label.configure(text="")

    def _update_single_cell(self, idx):
        outline = "#00ff00" if idx in self.selected_indices else "#404040"
        width = 2 if idx in self.selected_indices else 1
        self.canvas.itemconfig(self.rect_ids[idx], outline=outline, width=width)
        
    def get_selection_mask(self):
        return self.selected_indices

    def clear_selection(self):
        self.selected_indices.clear()
        self._redraw_colors()
        
    def select_all(self):
        self.selected_indices = set(range(256))
        self._redraw_colors()
