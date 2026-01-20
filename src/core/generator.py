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
        import random
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        generated_files = []
        
        # Generate random phase shifts for each group to ensure independence
        group_phase_shifts = [random.random() for _ in range(len(groups))]
        
        for i in range(count):
            new_palette = list(self.base_palette) # Copy original
            
            for g_idx, group in enumerate(groups):
                # Check if this group has a fixed color
                is_fixed = getattr(group, 'is_fixed', False)
                
                if is_fixed:
                    # Use the fixed gradient (8 colors) - apply directly to indices
                    fixed_gradient = getattr(group, 'fixed_gradient', None)
                    if fixed_gradient and len(fixed_gradient) == 8:
                        import colorsys
                        # Map the gradient to the group indices
                        sorted_indices = sorted(group.indices)
                        num_colors = len(sorted_indices)
                        
                        for j, idx in enumerate(sorted_indices):
                            if 0 <= idx < 256:
                                # Map index position to gradient position
                                gradient_pos = int((j / max(num_colors - 1, 1)) * 7)
                                gradient_pos = min(gradient_pos, 7)  # Clamp to 0-7
                                base_col = fixed_gradient[gradient_pos]
                                
                                # Apply saturation and brightness adjustments
                                r, g, b = base_col[0]/255, base_col[1]/255, base_col[2]/255
                                h, s, v = colorsys.rgb_to_hsv(r, g, b)
                                
                                # Apply shifts
                                s = max(0, min(1, s + group.sat_shift))
                                v = max(0, min(1, v * (1 + group.val_shift)))
                                
                                r, g, b = colorsys.hsv_to_rgb(h, s, v)
                                new_palette[idx] = (int(r*255), int(g*255), int(b*255))
                else:
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
                    
                    # Distribute evenly within the specified range, but with random phase shift per group
                    step_fraction = (i / max(count, 1) + group_phase_shifts[g_idx]) % 1.0
                    hue_degrees = hue_start + (hue_range * step_fraction)

                    hue_degrees = hue_degrees % 360  # Normalize to 0-360
                    hue_normalized = hue_degrees / 360.0  # 0.0 to 1.0
                    
                    for idx in group.indices:
                        if 0 <= idx < 256:
                            color = new_palette[idx]
                            
                            # Apply colorize with the target hue
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
