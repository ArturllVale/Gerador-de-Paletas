import os
import requests
import threading
from PIL import Image
import customtkinter as ctk

class IconManager:
    """
    Manages fetching and loading of icons (emojis) for the application.
    Uses Twemoji assets.
    """

    # Mapping of logical names to Twemoji codepoints (hex)
    ICONS = {
        "preview": "1f3a8",       # 🎨
        "theme_light": "2600",    # ☀️
        "theme_dark": "1f319",    # 🌙
        "generate": "1f3b2",      # 🎲
        "prev": "25c0",           # ◀
        "next": "25b6",           # ▶
        "play": "25b6",           # ▶ (Using same for play)
        "pause": "23f8",          # ⏸
        "art": "1f3a8",           # 🎨 (alias)
        "rainbow": "1f308",       # 🌈
        "water": "1f4a7",         # 💧
        "sun": "2600",            # ☀️ (alias)
    }

    BASE_URL = "https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/"

    def __init__(self, cache_dir="assets/icons"):
        self.cache_dir = cache_dir
        self.images = {}
        self._download_threads = {}

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def get_icon(self, name, size=(20, 20)):
        """
        Returns a CTkImage for the given icon name.
        Downloads it in background if not present.
        Returns None if downloading.
        """
        if name not in self.ICONS:
            print(f"Warning: Icon '{name}' not defined in IconManager.")
            return None

        codepoint = self.ICONS[name]
        filename = f"{codepoint}.png"
        filepath = os.path.join(self.cache_dir, filename)

        # Download if missing
        if not os.path.exists(filepath):
            if codepoint not in self._download_threads:
                 # Start download in a separate thread
                 t = threading.Thread(target=self._download_icon, args=(codepoint, filepath))
                 t.start()
                 self._download_threads[codepoint] = t
            return None

        # Load and cache CTkImage
        cache_key = (name, size)
        if cache_key in self.images:
            return self.images[cache_key]

        try:
            pil_image = Image.open(filepath)
            ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=size)
            self.images[cache_key] = ctk_image
            return ctk_image
        except Exception as e:
            # If image is corrupted or empty (failed download), maybe remove it?
            print(f"Error loading icon image {filepath}: {e}")
            return None

    def _download_icon(self, codepoint, filepath):
        url = f"{self.BASE_URL}{codepoint}.png"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(response.content)
            else:
                print(f"Failed to download icon {codepoint}: HTTP {response.status_code}")
        except Exception as e:
            print(f"Failed to download icon {codepoint}: {e}")
        finally:
            # Remove from active threads list so we can retry later if it failed
            # or just to clean up
            if codepoint in self._download_threads:
                del self._download_threads[codepoint]
