import struct
import io
from PIL import Image

class SprParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.header = None
        self.palette = [] # List of (r,g,b,a)
        self.images = [] # List of PIL.Image objects (indexed)
        self.version = 0

    def parse_images(self):
        """
        Parses all indexed images from the file.
        Returns a list of PIL Images (P mode).
        """
        self.images = []
        with open(self.file_path, 'rb') as f:
            f.seek(4) # Skip SP + Minor + Major
            version_minor = struct.unpack('B', f.read(1))[0] # Wait, I read minor/major manually above
            # Let's trust the seek order.
            # Header is 2 (SP) + 1 (Min) + 1 (Maj) = 4 bytes.
            # Actually above I did 2 + 1 + 1. Correct.
            
            # Re-read header to be safe in this isolated method or just seek:
            f.seek(2)
            minor = struct.unpack('B', f.read(1))[0]
            major = struct.unpack('B', f.read(1))[0]
            version = major * 100 + minor
            
            num_indexed = struct.unpack('<H', f.read(2))[0]
            num_rgba = 0
            if version >= 200:
                num_rgba = struct.unpack('<H', f.read(2))[0]
            
            for _ in range(num_indexed):
                width = struct.unpack('<H', f.read(2))[0]
                height = struct.unpack('<H', f.read(2))[0]
                
                # Read encoded size
                if version >= 201:
                    encoded_size = struct.unpack('<H', f.read(2))[0]
                else:
                    encoded_size = width * height
                
                # Decompress RLE for version 2.1+
                pixel_data = bytearray(width * height)
                idx = 0
                end_idx = width * height
                
                if version >= 201:
                    # RLE compressed: 00 XX = XX transparent pixels, otherwise direct pixel value
                    bytes_read = 0
                    while idx < end_idx and bytes_read < encoded_size:
                        b = struct.unpack('B', f.read(1))[0]
                        bytes_read += 1
                        
                        if b == 0:
                            # Transparent run
                            count = struct.unpack('B', f.read(1))[0]
                            bytes_read += 1
                            for _ in range(count):
                                if idx < end_idx:
                                    pixel_data[idx] = 0  # Transparent
                                    idx += 1
                        else:
                            # Direct pixel value
                            if idx < end_idx:
                                pixel_data[idx] = b
                                idx += 1
                else:
                    # Uncompressed
                    data = f.read(width * height)
                    pixel_data = bytearray(data)

                # Create PIL Image
                img = Image.frombytes('P', (width, height), bytes(pixel_data))
                self.images.append(img)
            
            # Read palette to apply to images
            f.seek(-1024, 2)
            pal_data = f.read(1024)
            # PIL expects flat [r,g,b, r,g,b...]
            # Source is [r,g,b,a, r,g,b,a...]
            flat_pal = []
            for i in range(0, 1024, 4):
                flat_pal.extend(pal_data[i:i+3]) # Ignore alpha for PIL 'P' palette
            
            # Apply palette to all images
            for img in self.images:
                img.putpalette(flat_pal)
                
        return self.images

    def extract_palette(self):
        """
        Robustly extracts the palette from the end of the file.
        """
        with open(self.file_path, 'rb') as f:
            f.seek(-1024, 2) # Seek to end - 1024
            data = f.read(1024)
            
            if len(data) < 1024:
                raise ValueError("Filesize too small to contain palette")
            
            s_pal = []
            for i in range(0, 1024, 4):
                r, g, b, a = struct.unpack('BBBB', data[i:i+4])
                # Reference logic: Reserved (alpha) should be 255 (visible) for color indices > 0
                # But when reading, we just store what's there.
                s_pal.append((r, g, b, a))
                
            self.palette = s_pal
            return s_pal
    
    def get_image(self, index):
        # Todo: Implement proper RLE decompression to get the image
        # For V1 of this plan, let's focus on getting the Palette perfect.
        pass
