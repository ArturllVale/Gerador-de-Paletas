class ColorGroup:
    def __init__(self, name, mode="hsv"):
        self.name = name
        self.mode = mode # "hsv" or "colorize"
        self.indices = set()
        
        # Color settings
        self.hue_shift_start = 0.0  # For preview visualization
        self.hue_shift_end = 0.0    # Deprecated, kept for compatibility
        self.sat_shift = 0.0
        self.val_shift = 0.0
        
        # Hue range for generation (in degrees 0-360)
        self.hue_range_start = 0    # 0° = Red
        self.hue_range_end = 360    # 360° = Full spectrum
        
        # Count for this group (if varying individually, but usually global count is used)
        
    def add_index(self, idx):
        self.indices.add(idx)
        
    def remove_index(self, idx):
        if idx in self.indices:
            self.indices.remove(idx)
            
    def set_indices(self, indices):
        self.indices = set(indices)

class ProjectState:
    def __init__(self):
        self.groups = []
        self.palette = [] # Original 256 colors
        self.spr_parser = None
        self.act_parser = None
        
        # Global settings
        self.generation_count = 10
        self.output_dir = ""
        self.prefix = "palette"
        
    def add_group(self, name):
        # Ensure unique name
        base_name = name
        ctr = 1
        while any(g.name == name for g in self.groups):
            name = f"{base_name} {ctr}"
            ctr += 1
            
        new_group = ColorGroup(name)
        self.groups.append(new_group)
        return new_group
        
    def remove_group(self, group):
        if group in self.groups:
            self.groups.remove(group)
            
    def get_group_by_index(self, idx):
        """Returns the group that owns this index, if any."""
        for g in self.groups:
            if idx in g.indices:
                return g
        return None
