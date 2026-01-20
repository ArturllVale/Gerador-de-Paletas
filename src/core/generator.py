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
                       groups,  # List of ColorGroup
                       start_number=0,
                       class_names=None,  # List of class names to generate for
                       random_saturation=False,
                       random_brightness=False):
        """
        Generates 'count' unique variations based on groups settings.
        Distributes hue evenly across 360° for guaranteed uniqueness.
        
        Args:
            start_number: Starting number for palette numbering (e.g., 100 -> 100, 101, 102...)
            class_names: List of RO class names. If provided, generates for each class.
                        If None/empty, uses base_filename.
        """
        import random
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        generated_files = []
        
        # Generate random phase shifts for each group to ensure independence
        group_phase_shifts = [random.random() for _ in range(len(groups))]
        
        # Determine which names to generate for
        # If no classes selected, use the base_filename
        names_to_generate = class_names if class_names else [base_filename]
        
        for i in range(count):
            new_palette = list(self.base_palette)  # Copy original
            
            # Generate random adjustment factors for this iteration if enabled
            iter_sat_shift = random.uniform(-0.3, 0.3) if random_saturation else 0.0
            iter_val_shift = random.uniform(-0.15, 0.15) if random_brightness else 0.0
            
            for g_idx, group in enumerate(groups):
                is_fixed = getattr(group, 'is_fixed', False)
                
                if is_fixed:
                    fixed_gradient = getattr(group, 'fixed_gradient', None)
                    if fixed_gradient and len(fixed_gradient) == 8:
                        sorted_indices = sorted(group.indices)
                        num_colors = len(sorted_indices)
                        
                        for j, idx in enumerate(sorted_indices):
                            if 0 <= idx < 256:
                                gradient_pos = int((j / max(num_colors - 1, 1)) * 7)
                                gradient_pos = min(gradient_pos, 7)
                                base_col = fixed_gradient[gradient_pos]
                                
                                r, g, b = base_col[0]/255, base_col[1]/255, base_col[2]/255
                                h, s, v = colorsys.rgb_to_hsv(r, g, b)
                                
                                s = max(0, min(1, s + group.sat_shift + iter_sat_shift))
                                v = max(0, min(1, v * (1 + group.val_shift + iter_val_shift)))
                                
                                r, g, b = colorsys.hsv_to_rgb(h, s, v)
                                new_palette[idx] = (int(r*255), int(g*255), int(b*255))
                else:
                    hue_start = getattr(group, 'hue_range_start', 0)
                    hue_end = getattr(group, 'hue_range_end', 360)
                    
                    hue_range = hue_end - hue_start
                    
                    if abs(hue_range) < 10:
                        hue_range = 360
                        hue_start = 0
                    elif hue_range < 0:
                        hue_range = hue_range + 360
                    
                    step = hue_range / max(count, 1)
                    if not hasattr(self, '_group_hues'):
                        self._group_hues = {}
                    
                    if g_idx not in self._group_hues:
                        slices = []
                        for k in range(count):
                            slice_start = hue_start + (k * step)
                            jitter = random.uniform(0, step * 0.8) 
                            slices.append(slice_start + jitter)
                        
                        random.shuffle(slices)
                        self._group_hues[g_idx] = slices
                        
                    hue_degrees = self._group_hues[g_idx][i]
                    hue_degrees = hue_degrees % 360
                    hue_normalized = hue_degrees / 360.0
                    
                    for idx in group.indices:
                        if 0 <= idx < 256:
                            color = new_palette[idx]
                            
                            new_color = apply_colorize(
                                color,
                                target_hue=hue_normalized,
                                target_sat=None,
                                value_mult=1.0 + group.val_shift + iter_val_shift
                            )
                            
                            if abs(iter_sat_shift) > 0 or abs(group.sat_shift) > 0:
                                r, g, b = new_color[0]/255, new_color[1]/255, new_color[2]/255
                                h, s, v = colorsys.rgb_to_hsv(r, g, b)
                                s = max(0, min(1, s + group.sat_shift + iter_sat_shift))
                                r, g, b = colorsys.hsv_to_rgb(h, s, v)
                                new_color = (int(r*255), int(g*255), int(b*255))
                            
                            new_palette[idx] = new_color
            
            # Calculate the actual palette number
            palette_number = start_number + i
            
            # Generate files for each class name (or base filename)
            for class_name in names_to_generate:
                # Male palette: {name}_³²_{n}.pal
                male_filename = f"{class_name}_³²_{palette_number}.pal"
                male_path = os.path.join(output_dir, male_filename)
                PaletteHandler.save(male_path, new_palette)
                generated_files.append(male_path)
                
                # Female palette: {name}_¿©_{n}.pal
                female_filename = f"{class_name}_¿©_{palette_number}.pal"
                female_path = os.path.join(output_dir, female_filename)
                PaletteHandler.save(female_path, new_palette)
                generated_files.append(female_path)
            
        return generated_files
