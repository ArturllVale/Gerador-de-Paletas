import customtkinter as ctk
from PIL import Image

class SpritePreview(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs, fg_color="#FFFFFF")
        
        # Container frame for centering
        self.container = ctk.CTkFrame(self, fg_color="#FFFFFF")
        self.container.pack(expand=True, fill="both")
        
        # Use Label for image display
        self.image_label = ctk.CTkLabel(self.container, text="", fg_color="#FFFFFF")
        self.image_label.place(relx=0.5, rely=0.5, anchor="center")
        
        self.original_image = None  # Store unscaled source (RGBA)
        self.original_indexed = None  # Store P-mode for index lookup
        self.current_image = None
        self.ctk_image = None
        
        # Store initial data for re-rendering
        self.last_pil_image = None
        self.last_palette = None
        
        self.scale = 2.0 # Default zoom
        
        # Callback for pixel click: receives palette index
        self.on_pixel_click = None
        
        # Bind click event
        self.image_label.bind("<Button-1>", self._on_click)
        
    def set_sprite(self, pil_image, palette=None):
        """
        pil_image: PIL Image (P mode or RGBA)
        palette: List of (r,g,b). If None, uses image's current palette.
        """
        # Store for re-scaling
        self.last_pil_image = pil_image
        self.last_palette = palette
        
        # Clear previous image references
        self.ctk_image = None
        self.current_image = None
        self.original_image = None
        self.original_indexed = None
        # Don't set image=None as it causes TclError, just clear text
        self.image_label.configure(text="")
        
        if pil_image is None:
            return
            
        # Copy to avoid modifying original
        img = pil_image.copy()
        
        # Store indexed image for click lookup BEFORE palette modification
        if img.mode == 'P':
            self.original_indexed = img.copy()
        
        # Apply NEW palette if provided
        if palette:
            # Get background color from index 0
            bg_color = palette[0][:3] if palette else (255, 255, 255)
            bg_hex = f"#{bg_color[0]:02x}{bg_color[1]:02x}{bg_color[2]:02x}"
            self.configure(fg_color=bg_hex)
            self.container.configure(fg_color=bg_hex)
            self.image_label.configure(fg_color=bg_hex)
            
            # Flatten palette for PIL: [r,g,b, r,g,b...]
            flat_pal = []
            for color in palette:
                flat_pal.extend(color[:3]) # Take first 3 RGB
            
            # Ensure 256 colors (768 ints)
            while len(flat_pal) < 768:
                flat_pal.extend([0, 0, 0])
             
            # If image is P mode
            if img.mode == 'P':
                img.putpalette(flat_pal)
        
        # Convert to RGBA for transparency handling in display
        img = img.convert("RGBA")
        
        # Store original before scaling
        self.original_image = img.copy()
        
        # Handle scaling
        if self.scale != 1.0:
            new_size = (int(img.width * self.scale), int(img.height * self.scale))
            img = img.resize(new_size, Image.NEAREST)
            
        self.current_image = img
        
        # Use CTkImage for proper CustomTkinter integration
        self.ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
        
        # Set image to label
        self.image_label.configure(image=self.ctk_image)
        
    def set_scale(self, scale):
        self.scale = scale
        # Redraw if image exists
        if self.last_pil_image:
            self.set_sprite(self.last_pil_image, self.last_palette)

    def _on_click(self, event):
        """Handle click on sprite preview to select palette index"""
        if self.original_indexed is None:
            return
            
        # Get click position relative to image center
        # image_label uses place with relx=0.5, rely=0.5, anchor="center"
        label_width = self.image_label.winfo_width()
        label_height = self.image_label.winfo_height()
        
        if self.current_image is None:
            return
            
        img_width = self.current_image.width
        img_height = self.current_image.height
        
        # Calculate image top-left position within label
        img_x_offset = (label_width - img_width) // 2
        img_y_offset = (label_height - img_height) // 2
        
        # Convert click coords to image coords
        click_x = event.x - img_x_offset
        click_y = event.y - img_y_offset
        
        # Scale back to original image coords
        orig_x = int(click_x / self.scale)
        orig_y = int(click_y / self.scale)
        
        # Check bounds
        if 0 <= orig_x < self.original_indexed.width and 0 <= orig_y < self.original_indexed.height:
            # Get palette index at this pixel
            palette_index = self.original_indexed.getpixel((orig_x, orig_y))
            
            # Call callback if set
            if self.on_pixel_click:
                self.on_pixel_click(palette_index)

