import os
import colorsys
import random
from src.core.pal_handler import PaletteHandler


class HairPaletteGenerator:
    """
    Generator for hair palettes with specific naming format:
    ¸Ó¸®{style_count}_{gender}_{palette_number}.pal
    
    Example: ¸Ó¸®40_¿©_8.pal (female hair, style count 40, palette 8)
    """
    
    def __init__(self, base_palette):
        self.base_palette = base_palette
        self._group_hues = {}
    
    def generate_hair_palettes(self,
                               output_dir,
                               style_count,
                               count,
                               groups,
                               start_number=0,
                               random_saturation=False,
                               random_brightness=False,
                               progress_callback=None):
        """
        Generate hair palettes with the specific naming format.
        
        Args:
            output_dir: Directory to save palette files
            style_count: Number of hair styles in the server (e.g., 40)
            count: Number of palettes to generate
            groups: Color groups with settings
            start_number: Starting palette number (default 0)
            random_saturation: Apply random saturation variation
            random_brightness: Apply random brightness variation
            progress_callback: Callback for progress updates (current, total)
        
        Returns:
            List of generated file paths
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        generated_files = []
        total_files = count * 2  # Male and female versions
        current_file_count = 0
        
        # Pre-process groups
        processed_groups = []
        for g_idx, group in enumerate(groups):
            is_fixed = getattr(group, 'is_fixed', False)
            if is_fixed:
                fixed_gradient = getattr(group, 'fixed_gradient', None)
                if fixed_gradient and len(fixed_gradient) == 8:
                    sorted_indices = sorted(group.indices)
                    num_colors = len(sorted_indices)
                    gradient_bases = []
                    for j in range(num_colors):
                        gradient_pos = int((j / max(num_colors - 1, 1)) * 7)
                        gradient_pos = min(gradient_pos, 7)
                        base_col = fixed_gradient[gradient_pos]
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
                
                # Pre-calculate hue slices using Golden Ratio
                if g_idx not in self._group_hues:
                    slices = []
                    golden_ratio = 0.618033988749895
                    base_offset = random.uniform(0, 360)
                    
                    for k in range(count):
                        golden_hue = (base_offset + (k * golden_ratio * 360)) % 360
                        jitter = random.uniform(-step * 0.5, step * 0.5)
                        final_hue = hue_start + ((golden_hue - hue_start + jitter) % hue_range)
                        slices.append(final_hue)
                    
                    random.shuffle(slices)
                    random.shuffle(slices)
                    random.shuffle(slices)
                    
                    self._group_hues[g_idx] = slices
                
                processed_groups.append({
                    'type': 'variable',
                    'indices': group.indices,
                    'hues': self._group_hues[g_idx],
                    'sat_shift': group.sat_shift,
                    'val_shift': group.val_shift
                })
        
        # Pre-calculate random shifts
        iter_sat_shifts = [random.uniform(-0.3, 0.3) if random_saturation else 0.0 for _ in range(count)]
        iter_val_shifts = [random.uniform(-0.15, 0.15) if random_brightness else 0.0 for _ in range(count)]
        
        # Main Generation Loop
        for i in range(count):
            new_palette = list(self.base_palette)
            
            iter_sat_shift = iter_sat_shifts[i]
            iter_val_shift = iter_val_shifts[i]
            
            for g_data in processed_groups:
                if g_data['type'] == 'fixed':
                    sat_shift = g_data['sat_shift']
                    val_shift = 1 + g_data['val_shift']
                    
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
                            r, g, b = new_palette[idx]
                            rn, gn, bn = r/255.0, g/255.0, b/255.0
                            h, s, v = colorsys.rgb_to_hsv(rn, gn, bn)
                            
                            hue_micro = random.uniform(-0.03, 0.03)
                            sat_micro = random.uniform(-0.08, 0.08)
                            val_micro = random.uniform(-0.05, 0.05)
                            
                            final_hue = (hue_normalized + hue_micro) % 1.0
                            new_s = max(0.0, min(1.0, s + sat_shift_total + sat_micro))
                            new_v = max(0.0, min(1.0, v * val_mult_total + val_micro))
                            
                            r_out, g_out, b_out = colorsys.hsv_to_rgb(final_hue, new_s, new_v)
                            new_palette[idx] = (int(r_out*255), int(g_out*255), int(b_out*255))
            
            palette_number = start_number + i
            
            # Female hair palette: ¸Ó¸®{style_count}_¿©_{number}.pal
            female_filename = f"¸Ó¸®{style_count}_¿©_{palette_number}.pal"
            female_path = os.path.join(output_dir, female_filename)
            PaletteHandler.save(female_path, new_palette)
            generated_files.append(female_path)
            current_file_count += 1
            if progress_callback:
                progress_callback(current_file_count, total_files)
            
            # Male hair palette: ¸Ó¸®{style_count}_³²_{number}.pal
            male_filename = f"¸Ó¸®{style_count}_³²_{palette_number}.pal"
            male_path = os.path.join(output_dir, male_filename)
            PaletteHandler.save(male_path, new_palette)
            generated_files.append(male_path)
            current_file_count += 1
            if progress_callback:
                progress_callback(current_file_count, total_files)
        
        return generated_files
