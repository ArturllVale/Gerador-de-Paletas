import os
import colorsys
import random
from src.core.pal_handler import PaletteHandler

class PaletteGenerator:
    def __init__(self, base_palette):
        self.base_palette = base_palette
        self._group_hues = {}

    def _generate_core(self,
                       output_dir, 
                       base_filename, 
                       count, 
                       groups,
                       start_number=0,
                       class_names=None,
                       random_saturation=False,
                       random_brightness=False,
                       progress_callback=None):
        """
        Unified core generation logic.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        generated_files = []
        names_to_generate = class_names if class_names else [base_filename]
        
        total_files = count * len(names_to_generate) * 2
        current_file_count = 0

        # Pre-process groups
        # We need to know which indices belong to which group and their settings
        # to avoid repeated attribute lookups inside the loop.
        processed_groups = []
        for g_idx, group in enumerate(groups):
            is_fixed = getattr(group, 'is_fixed', False)
            if is_fixed:
                fixed_gradient = getattr(group, 'fixed_gradient', None)
                if fixed_gradient and len(fixed_gradient) == 8:
                    sorted_indices = sorted(group.indices)
                    # Pre-calculate base colors for fixed gradient
                    num_colors = len(sorted_indices)
                    gradient_bases = []
                    for j in range(num_colors):
                        gradient_pos = int((j / max(num_colors - 1, 1)) * 7)
                        gradient_pos = min(gradient_pos, 7)
                        base_col = fixed_gradient[gradient_pos]
                        # Convert base_col to HSV once
                        r, g, b = base_col[0]/255.0, base_col[1]/255.0, base_col[2]/255.0
                        h, s, v = colorsys.rgb_to_hsv(r, g, b)
                        gradient_bases.append((h, s, v))
                    
                    processed_groups.append({
                        'type': 'fixed',
                        'indices': sorted_indices,
                        'gradient_bases': gradient_bases,
                        'sat_shift': group.sat_shift,
                        'val_shift': group.val_shift
                    })
                else:
                    processed_groups.append({'type': 'noop'})
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

                # Pre-calculate hue slices
                if g_idx not in self._group_hues:
                    slices = []
                    for k in range(count):
                        slice_start = hue_start + (k * step)
                        jitter = random.uniform(0, step * 0.8)
                        slices.append(slice_start + jitter)
                    random.shuffle(slices)
                    self._group_hues[g_idx] = slices

                processed_groups.append({
                    'type': 'variable',
                    'indices': group.indices,
                    'hues': self._group_hues[g_idx],
                    'sat_shift': group.sat_shift,
                    'val_shift': group.val_shift
                })

        # Pre-process class names
        processed_names = []
        for class_name in names_to_generate:
            clean_name = class_name
            if clean_name.endswith("_³²"):
                clean_name = clean_name[:-3]
            elif clean_name.endswith("_¿©"):
                clean_name = clean_name[:-3]
            processed_names.append(clean_name)

        # Pre-calculate random shifts if needed
        # We need 'count' sets of random shifts
        iter_sat_shifts = [random.uniform(-0.3, 0.3) if random_saturation else 0.0 for _ in range(count)]
        iter_val_shifts = [random.uniform(-0.15, 0.15) if random_brightness else 0.0 for _ in range(count)]

        # --- Main Generation Loop ---
        for i in range(count):
            # Working on a mutable list is faster than creating a new list every time if we are careful?
            # But we need to start from base_palette each time.
            new_palette = list(self.base_palette)
            
            iter_sat_shift = iter_sat_shifts[i]
            iter_val_shift = iter_val_shifts[i]

            for g_data in processed_groups:
                if g_data['type'] == 'fixed':
                    sat_shift = g_data['sat_shift'] + iter_sat_shift
                    val_shift = 1 + g_data['val_shift'] + iter_val_shift
                    
                    for j, idx in enumerate(g_data['indices']):
                        if 0 <= idx < 256:
                            h, s, v = g_data['gradient_bases'][j]

                            s = max(0.0, min(1.0, s + sat_shift))
                            v = max(0.0, min(1.0, v * val_shift))

                            r, g, b = colorsys.hsv_to_rgb(h, s, v)
                            new_palette[idx] = (int(r*255), int(g*255), int(b*255))

                elif g_data['type'] == 'variable':
                    hue_degrees = g_data['hues'][i] % 360
                    hue_normalized = hue_degrees / 360.0
                    
                    sat_shift_total = g_data['sat_shift'] + iter_sat_shift
                    val_mult_total = 1.0 + g_data['val_shift'] + iter_val_shift

                    for idx in g_data['indices']:
                        if 0 <= idx < 256:
                            # We can optimize this by avoiding tuple unpacking/packing overhead
                            # But new_palette[idx] returns a tuple.
                            r, g, b = new_palette[idx]

                            # Using colorsys.rgb_to_hsv is the bottleneck.
                            # Can we inline it?
                            # r, g, b are 0-255.
                            
                            # Normalize
                            rn, gn, bn = r/255.0, g/255.0, b/255.0
                            h, s, v = colorsys.rgb_to_hsv(rn, gn, bn)

                            new_s = max(0.0, min(1.0, s + sat_shift_total))
                            new_v = max(0.0, min(1.0, v * val_mult_total))
                            
                            r_out, g_out, b_out = colorsys.hsv_to_rgb(hue_normalized, new_s, new_v)
                            new_palette[idx] = (int(r_out*255), int(g_out*255), int(b_out*255))
            
            palette_number = start_number + i
            
            # Write files
            for clean_name in processed_names:
                # Male
                male_filename = f"{clean_name}_³²_{palette_number}.pal"
                male_path = os.path.join(output_dir, male_filename)
                PaletteHandler.save(male_path, new_palette)
                generated_files.append(male_path)
                current_file_count += 1
                if progress_callback:
                    progress_callback(current_file_count, total_files)

                # Female
                female_filename = f"{clean_name}_¿©_{palette_number}.pal"
                female_path = os.path.join(output_dir, female_filename)
                PaletteHandler.save(female_path, new_palette)
                generated_files.append(female_path)
                current_file_count += 1
                if progress_callback:
                    progress_callback(current_file_count, total_files)

        return generated_files

    def generate_batch(self,
                       output_dir,
                       base_filename,
                       count,
                       groups,
                       start_number=0,
                       class_names=None,
                       random_saturation=False,
                       random_brightness=False):
        return self._generate_core(output_dir, base_filename, count, groups, start_number,
                                   class_names, random_saturation, random_brightness)

    def generate_batch_with_progress(self,
                                     output_dir,
                                     base_filename,
                                     count,
                                     groups,
                                     start_number=0,
                                     class_names=None,
                                     random_saturation=False,
                                     random_brightness=False,
                                     progress_callback=None):
        return self._generate_core(output_dir, base_filename, count, groups, start_number,
                                   class_names, random_saturation, random_brightness, progress_callback)
