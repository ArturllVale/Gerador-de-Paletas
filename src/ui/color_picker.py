"""
Modern Color Picker Dialog with HSV gradient
Style similar to modern design tools
"""
import tkinter as tk
import customtkinter as ctk
import colorsys
from PIL import Image, ImageTk, ImageDraw


class ColorPickerDialog(ctk.CTkToplevel):
    """Modern color picker dialog with 2D gradient and hue slider"""
    
    def __init__(self, master, initial_color=(255, 255, 255), title="Color Picker"):
        super().__init__(master)
        
        self.title(title)
        self.geometry("300x420")
        self.resizable(False, False)
        # fg_color is now inherited from theme.json CTkToplevel settings
        
        # Make modal
        self.transient(master)
        self.grab_set()
        
        # Result
        self.result = None
        
        # Current color in HSV
        r, g, b = initial_color
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        self.hue = h
        self.saturation = s
        self.value = v
        
        # Title
        self.lbl_title = ctk.CTkLabel(self, text="Color Picker", font=("Roboto", 14, "bold"))
        self.lbl_title.pack(pady=(10, 5))
        
        # Canvas Background based on mode (static for dialog lifetime)
        mode = ctk.get_appearance_mode()
        canvas_bg = "#1a1a1a" if mode == "Dark" else "#E0E0E0"
        
        # Saturation-Value gradient canvas (2D)
        self.sv_size = 200
        self.sv_canvas = tk.Canvas(self, width=self.sv_size, height=self.sv_size, 
                                    highlightthickness=0, bg=canvas_bg)
        self.sv_canvas.pack(pady=10)
        
        # Hue slider canvas
        self.hue_canvas = tk.Canvas(self, width=250, height=20, highlightthickness=0, bg=canvas_bg)
        self.hue_canvas.pack(pady=10)
        
        # Hex input and preview
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(fill="x", padx=20, pady=10)
        
        # Hex entry
        self.hex_frame = ctk.CTkFrame(self.bottom_frame)
        self.hex_frame.pack(side="left", fill="x", expand=True)
        
        self.hex_entry = ctk.CTkEntry(self.hex_frame, width=100, 
                                       placeholder_text="#FFFFFF",
                                       border_width=0)
        self.hex_entry.pack(side="left", padx=5, pady=5)
        self.hex_entry.bind("<Return>", self._on_hex_enter)
        
        self.lbl_hex = ctk.CTkLabel(self.hex_frame, text="HEX", text_color="gray")
        self.lbl_hex.pack(side="left", padx=5)
        
        # Preview
        self.preview_canvas = tk.Canvas(self.bottom_frame, width=50, height=30, 
                                         highlightthickness=1, highlightbackground="#555")
        self.preview_canvas.pack(side="right", padx=10)
        
        # OK Button
        self.btn_ok = ctk.CTkButton(self, text="OK", command=self._on_ok,
                                     fg_color="#4CAF50", hover_color="#388E3C")
        self.btn_ok.pack(pady=10)
        
        # Canvas bindings
        self.sv_canvas.bind("<Button-1>", self._on_sv_click)
        self.sv_canvas.bind("<B1-Motion>", self._on_sv_click)
        self.hue_canvas.bind("<Button-1>", self._on_hue_click)
        self.hue_canvas.bind("<B1-Motion>", self._on_hue_click)
        
        # Draw initial state
        self._draw_hue_bar()
        self._draw_sv_gradient()
        self._update_preview()
        self._update_hex_entry()
        
        # Center on parent
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() - self.winfo_width()) // 2
        y = master.winfo_rooty() + (master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        
        # Wait for dialog
        self.wait_window()
    
    def _draw_hue_bar(self):
        """Draw the horizontal hue gradient bar"""
        width = 250
        height = 20
        
        img = Image.new("RGB", (width, height))
        for x in range(width):
            h = x / width
            r, g, b = colorsys.hsv_to_rgb(h, 1.0, 1.0)
            for y in range(height):
                img.putpixel((x, y), (int(r*255), int(g*255), int(b*255)))
        
        self.hue_img = ImageTk.PhotoImage(img)
        self.hue_canvas.create_image(0, 0, anchor="nw", image=self.hue_img)
        
        # Draw position marker
        self._draw_hue_marker()
    
    def _draw_hue_marker(self):
        """Draw the hue position marker"""
        self.hue_canvas.delete("marker")
        x = int(self.hue * 250)
        self.hue_canvas.create_oval(x-6, 4, x+6, 16, fill="white", outline="#333", 
                                     width=2, tags="marker")
    
    def _draw_sv_gradient(self):
        """Draw the saturation-value gradient for current hue"""
        size = self.sv_size
        
        img = Image.new("RGB", (size, size))
        for x in range(size):
            for y in range(size):
                s = x / size  # Saturation: left to right
                v = 1 - (y / size)  # Value: top to bottom
                r, g, b = colorsys.hsv_to_rgb(self.hue, s, v)
                img.putpixel((x, y), (int(r*255), int(g*255), int(b*255)))
        
        self.sv_img = ImageTk.PhotoImage(img)
        self.sv_canvas.create_image(0, 0, anchor="nw", image=self.sv_img)
        
        # Draw position marker
        self._draw_sv_marker()
    
    def _draw_sv_marker(self):
        """Draw the SV position marker"""
        self.sv_canvas.delete("marker")
        x = int(self.saturation * self.sv_size)
        y = int((1 - self.value) * self.sv_size)
        
        # Draw circle with contrasting outline
        self.sv_canvas.create_oval(x-8, y-8, x+8, y+8, 
                                    outline="white", width=2, tags="marker")
        self.sv_canvas.create_oval(x-6, y-6, x+6, y+6, 
                                    outline="#333", width=1, tags="marker")
    
    def _update_preview(self):
        """Update the color preview"""
        r, g, b = self._get_rgb()
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        self.preview_canvas.configure(bg=hex_color)
    
    def _update_hex_entry(self):
        """Update hex entry with current color"""
        r, g, b = self._get_rgb()
        hex_color = f"#{r:02x}{g:02x}{b:02x}".upper()
        self.hex_entry.delete(0, "end")
        self.hex_entry.insert(0, hex_color)
    
    def _get_rgb(self):
        """Get current color as RGB tuple"""
        r, g, b = colorsys.hsv_to_rgb(self.hue, self.saturation, self.value)
        return (int(r*255), int(g*255), int(b*255))
    
    def _on_sv_click(self, event):
        """Handle click on SV gradient"""
        x = max(0, min(event.x, self.sv_size - 1))
        y = max(0, min(event.y, self.sv_size - 1))
        
        self.saturation = x / self.sv_size
        self.value = 1 - (y / self.sv_size)
        
        self._draw_sv_marker()
        self._update_preview()
        self._update_hex_entry()
    
    def _on_hue_click(self, event):
        """Handle click on hue bar"""
        x = max(0, min(event.x, 249))
        self.hue = x / 250
        
        self._draw_hue_marker()
        self._draw_sv_gradient()
        self._update_preview()
        self._update_hex_entry()
    
    def _on_hex_enter(self, event):
        """Handle hex input"""
        hex_val = self.hex_entry.get().strip()
        if hex_val.startswith("#"):
            hex_val = hex_val[1:]
        
        try:
            if len(hex_val) == 6:
                r = int(hex_val[0:2], 16)
                g = int(hex_val[2:4], 16)
                b = int(hex_val[4:6], 16)
                
                h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
                self.hue = h
                self.saturation = s
                self.value = v
                
                self._draw_hue_marker()
                self._draw_sv_gradient()
                self._update_preview()
        except ValueError:
            pass
    
    def _on_ok(self):
        """Confirm selection"""
        self.result = self._get_rgb()
        self.destroy()
    
    @staticmethod
    def ask_color(master, initial_color=(255, 255, 255), title="Color Picker"):
        """Static method to show dialog and return selected color"""
        dialog = ColorPickerDialog(master, initial_color, title)
        return dialog.result
