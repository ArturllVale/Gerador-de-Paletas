import os
from src.core.pal_handler import PaletteHandler
from src.core.color_math import apply_adjustments, apply_colorize

class PaletteGenerator:
    def __init__(self, base_palette):
        self.base_palette = base_palette

    def generate_batch(self, 
                       output_dir, 
                       base_filename, 
                       count, 
                       groups, # List of ColorGroup
                       generate_preview=False):
        """
        Generates 'count' unique variations based on groups settings.
        Distributes hue evenly across 360° for guaranteed uniqueness.
        """
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        generated_files = []
        
        for i in range(count):
            new_palette = list(self.base_palette) # Copy original
            
            for group in groups:
                # Get hue range from group settings (in degrees)
                hue_start = getattr(group, 'hue_range_start', 0)
                hue_end = getattr(group, 'hue_range_end', 360)
                
                # Calculate hue range
                hue_range = hue_end - hue_start
                
                # If colors are the same (or very close), use full 360° spectrum
                if abs(hue_range) < 10:  # Less than 10 degrees difference = same color
                    hue_range = 360
                    hue_start = 0
                elif hue_range < 0:
                    # Wrap around (e.g., from 350° to 30° = 40° range through red)
                    hue_range = hue_range + 360
                
                # Distribute evenly within the specified range
                hue_degrees = hue_start + (hue_range * i) / count
                hue_degrees = hue_degrees % 360  # Normalize to 0-360
                hue_normalized = hue_degrees / 360.0  # 0.0 to 1.0
                
                for idx in group.indices:
                    if 0 <= idx < 256:
                        color = new_palette[idx]
                        
                        # For batch generation, we REPLACE the hue (not shift)
                        # This ensures colors are in the specified range
                        new_color = apply_colorize(
                            color,
                            target_hue=hue_normalized,
                            target_sat=None,  # Keep original saturation
                            value_mult=1.0 + group.val_shift
                        )
                        
                        new_palette[idx] = new_color
            
            # Form filename: Name_0.pal, Name_1.pal, etc.
            filename = f"{base_filename}_{i}.pal"
            full_path = os.path.join(output_dir, filename)
            
            PaletteHandler.save(full_path, new_palette)
            generated_files.append(full_path)

            if generate_preview:
                self._save_preview_image(output_dir, f"{base_filename}_{i}", new_palette)
            
        return generated_files

    def _save_preview_image(self, output_dir, base_name, palette):
        try:
            from PIL import Image, ImageDraw
        except ImportError:
            return # Pillow not installed

        # Create a 256x256 image (16x16 grid of 16x16 squares)
        cell_size = 16
        img_size = 16 * cell_size
        img = Image.new("RGB", (img_size, img_size), "black")
        draw = ImageDraw.Draw(img)

        for idx, color in enumerate(palette):
            x = (idx % 16) * cell_size
            y = (idx // 16) * cell_size
            draw.rectangle([x, y, x + cell_size, y + cell_size], fill=color)
        
        preview_path = os.path.join(output_dir, f"{base_name}.png")
        img.save(preview_path)
