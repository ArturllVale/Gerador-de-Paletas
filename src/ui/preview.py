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
        
        # Palette cache for optimization
        self._cached_flat_pal = None
        self._last_bg_hex = None
        
        self.scale = 2.0 # Default zoom
        
        # Callback for pixel click: receives palette index
        self.on_pixel_click = None
        
        # Highlight state
        self._highlight_indices = None  # Set of indices to highlight
        self._highlight_blink_on = False
        self._highlight_after_id = None
        
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
            
            # Only update fg_color if changed (avoids redundant widget updates)
            if bg_hex != self._last_bg_hex:
                self._last_bg_hex = bg_hex
                self.configure(fg_color=bg_hex)
                self.container.configure(fg_color=bg_hex)
                self.image_label.configure(fg_color=bg_hex)
            
            # Flatten palette for PIL using list comprehension (faster)
            flat_pal = [c for color in palette for c in color[:3]]
            
            # Pad to 768 if needed
            if len(flat_pal) < 768:
                flat_pal.extend([0] * (768 - len(flat_pal)))
             
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
    
    def highlight_pixels(self, palette_indices):
        """Highlight pixels matching the given palette indices with blink effect.
        
        Args:
            palette_indices: A single index, set of indices, or None to clear.
        """
        # Cancel existing blink
        if self._highlight_after_id is not None:
            self.after_cancel(self._highlight_after_id)
            self._highlight_after_id = None
        
        # Normalize to set
        if palette_indices is None:
            self._highlight_indices = None
        elif isinstance(palette_indices, int):
            self._highlight_indices = {palette_indices}
        else:
            self._highlight_indices = set(palette_indices)
        
        self._highlight_blink_on = False
        
        if not self._highlight_indices or self.original_indexed is None or self.last_palette is None:
            # Restore original view
            if self.last_pil_image and self.last_palette:
                self.set_sprite(self.last_pil_image, self.last_palette)
            return
        
        # Start blink loop
        self._do_blink()
    
    def _do_blink(self):
        """Toggle highlight state and schedule next blink."""
        if self._highlight_indices is None:
            return
            
        self._highlight_blink_on = not self._highlight_blink_on
        self._render_with_highlight()
        
        # Schedule next blink (300ms interval)
        self._highlight_after_id = self.after(300, self._do_blink)
    
    def _render_with_highlight(self):
        """Render sprite with highlighted pixels inverted."""
        if self.original_indexed is None or self.last_palette is None:
            return
            
        img = self.last_pil_image.copy()
        
        if img.mode != 'P':
            return
            
        # Create modified palette
        modified_pal = list(self.last_palette)
        
        if self._highlight_blink_on and self._highlight_indices:
            for idx in self._highlight_indices:
                if 0 <= idx < 256:
                    # Invert/highlight the target color
                    orig = modified_pal[idx][:3]
                    # Use bright contrasting color (cyan for dark colors, magenta for bright)
                    brightness = (orig[0] + orig[1] + orig[2]) / 3
                    if brightness > 127:
                        highlight = (255, 0, 255)  # Magenta
                    else:
                        highlight = (0, 255, 255)  # Cyan
                    modified_pal[idx] = (*highlight, 255)
        
        # Flatten palette
        flat_pal = [c for color in modified_pal for c in color[:3]]
        if len(flat_pal) < 768:
            flat_pal.extend([0] * (768 - len(flat_pal)))
        
        img.putpalette(flat_pal)
        img = img.convert("RGBA")
        
        # Apply scaling
        if self.scale != 1.0:
            new_size = (int(img.width * self.scale), int(img.height * self.scale))
            img = img.resize(new_size, Image.NEAREST)
        
        self.current_image = img
        self.ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
        self.image_label.configure(image=self.ctk_image)
