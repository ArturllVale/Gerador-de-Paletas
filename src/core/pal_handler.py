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
            
            # Unpack all 1024 bytes at once
            # Each color is 4 bytes: R, G, B, Reserved
            # 256 colors * 4 bytes = 1024 bytes
            # 'BBBB' * 256

            # Using iter_unpack is cleaner in Py3
            for r, g, b, _ in struct.iter_unpack('BBBB', data):
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

        # Pre-allocate buffer logic or pack all at once
        # Construct a bytearray or a list of bytes

        # Optimized: create a flat list of values to pack
        values = []
        for idx, (r, g, b) in enumerate(palette):
            reserved = 0 if idx == 0 else 255
            values.extend((r, g, b, reserved))

        # Pack all 1024 bytes at once
        # 'BBBB' * 256 = 'B' * 1024
        packed_data = struct.pack('B' * 1024, *values)

        with open(file_path, 'wb') as f:
            f.write(packed_data)
