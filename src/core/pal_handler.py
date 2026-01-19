import struct
import os

class PaletteHandler:
    @staticmethod
    def load(file_path):
        """
        Loads a .pal file.
        Format: 256 colors, each 4 bytes (R, G, B, Reserved).
        Total size should be 1024 bytes.
        Returns: List of (r, g, b) tuples.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_size = os.path.getsize(file_path)
        if file_size < 1024:
            raise ValueError(f"Invalid .pal file size: {file_size} bytes. Expected at least 1024 bytes.")

        palette = []
        with open(file_path, 'rb') as f:
            data = f.read(1024) # Read only the first 1024 bytes relevant for the palette
            
            for i in range(0, 1024, 4):
                # Unpack 4 bytes: Red, Green, Blue, Reserved (usually 0)
                r, g, b, _ = struct.unpack('BBBB', data[i:i+4])
                palette.append((r, g, b))
        
        return palette

    @staticmethod
    def save(file_path, palette):
        """
        Saves a list of (r, g, b) tuples to a .pal file.
        Must be exactly 256 colors.
        """
        if len(palette) != 256:
            raise ValueError(f"Invalid palette length: {len(palette)}. Expected 256 colors.")

        with open(file_path, 'wb') as f:
            for idx, color in enumerate(palette):
                r, g, b = color
                
                # Match Reference Logic (PaletteSelector.xaml.cs):
                # Sets alpha (4th byte) to 255 for all, except index 0 which is 0.
                reserved = 0 if idx == 0 else 255
                
                # Pack as R, G, B, Reserved/Alpha
                packed_data = struct.pack('BBBB', r, g, b, reserved)
                f.write(packed_data)
