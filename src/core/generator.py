import os
import colorsys
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
                       generate_preview=False,
                       random_saturation=False,
                       random_brightness=False):
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
            
            # Generate random adjustment factors for this iteration if enabled
            # Saturation: +/- 0.3 (clamped 0-1 later)
            # Brightness (Value): +/- 0.15 (clamped 0-1 later)
            iter_sat_shift = random.uniform(-0.3, 0.3) if random_saturation else 0.0
            iter_val_shift = random.uniform(-0.15, 0.15) if random_brightness else 0.0
            
            for g_idx, group in enumerate(groups):
                # Check if this group has a fixed color
                is_fixed = getattr(group, 'is_fixed', False)
                
                if is_fixed:
                    # Use the fixed gradient (8 colors) - apply directly to indices
                    fixed_gradient = getattr(group, 'fixed_gradient', None)
                    if fixed_gradient and len(fixed_gradient) == 8:
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
                                s = max(0, min(1, s + group.sat_shift + iter_sat_shift))
                                v = max(0, min(1, v * (1 + group.val_shift + iter_val_shift)))
                                
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
                    
                    # Stratified Sampling: Divide range into 'count' equal slices
                    # Pick one random point within each slice to ensure separation
                    # Then shuffle to randomize the output order
                    step = hue_range / max(count, 1)
                    # Pre-calculate all hue offsets for this group
                    if not hasattr(self, '_group_hues'):
                        self._group_hues = {}
                    
                    if g_idx not in self._group_hues:
                        # Generate linear slices with random jitter within the slice
                        # jitter = random.uniform(0, step) or center? 
                        # To maximize distinctiveness, using center + small jitter is safer than full random
                        # But user wants "random variations". 
                        # Method: take center of slice.
                        slices = []
                        for k in range(count):
                            slice_start = hue_start + (k * step)
                            # Add small random jitter (up to 80% of step) to avoid looking too mechanical
                            jitter = random.uniform(0, step * 0.8) 
                            slices.append(slice_start + jitter)
                        
                        random.shuffle(slices)
                        self._group_hues[g_idx] = slices
                        
                    hue_degrees = self._group_hues[g_idx][i]

                    hue_degrees = hue_degrees % 360  # Normalize to 0-360
                    hue_normalized = hue_degrees / 360.0  # 0.0 to 1.0
                    
                    for idx in group.indices:
                        if 0 <= idx < 256:
                            color = new_palette[idx]
                            
                            # Apply colorize with the target hue
                            new_color = apply_colorize(
                                color,
                                target_hue=hue_normalized,
                                target_sat=None, # Saturation handled below if using shifts, but maximize robustness
                                value_mult=1.0 + group.val_shift + iter_val_shift
                            )
                            
                            # If we need to apply saturation shift to the result of colorize
                            if abs(iter_sat_shift) > 0 or abs(group.sat_shift) > 0:
                                r, g, b = new_color[0]/255, new_color[1]/255, new_color[2]/255
                                h, s, v = colorsys.rgb_to_hsv(r, g, b)
                                s = max(0, min(1, s + group.sat_shift + iter_sat_shift))
                                r, g, b = colorsys.hsv_to_rgb(h, s, v)
                                new_color = (int(r*255), int(g*255), int(b*255))
                            
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
