"""
Hot reload module for theme.json changes.
Uses watchdog to monitor file changes and applies them in real-time.
"""
import json
import os
import threading
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    # Dummy classes to prevent NameError
    class FileSystemEventHandler: pass
    class Observer: pass
import customtkinter as ctk


class ThemeReloadHandler(FileSystemEventHandler):
    """Handles theme.json file modification events."""
    
    def __init__(self, theme_path: str, root_window: ctk.CTk):
        super().__init__()
        self.theme_path = os.path.normpath(theme_path)
        self.root = root_window
        self._debounce_timer = None
        self._lock = threading.Lock()
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        modified_path = os.path.normpath(event.src_path)
        if modified_path != self.theme_path:
            return
        
        # Debounce rapid file saves (e.g., from editors saving multiple times)
        with self._lock:
            if self._debounce_timer:
                self._debounce_timer.cancel()
            self._debounce_timer = threading.Timer(0.2, self._apply_theme)
            self._debounce_timer.start()
    
    def _apply_theme(self):
        """Reload and apply theme from JSON file."""
        try:
            with open(self.theme_path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            
            # Schedule UI update on main thread
            self.root.after(0, lambda: self._update_widgets(theme_data))
            print(f"[HotReload] Theme reloaded: {self.theme_path}")
            
        except json.JSONDecodeError as e:
            print(f"[HotReload] Invalid JSON: {e}")
        except Exception as e:
            print(f"[HotReload] Error reloading theme: {e}")
    
    def _update_widgets(self, theme_data: dict):
        """Recursively update all widgets with new theme colors."""
        self._apply_to_widget(self.root, theme_data)
    
    def _apply_to_widget(self, widget, theme_data: dict):
        """Apply theme properties to a single widget and its children."""
        widget_type = type(widget).__name__
        
        if widget_type in theme_data:
            props = theme_data[widget_type]
            self._configure_widget(widget, props)
        
        # Recurse into children
        try:
            for child in widget.winfo_children():
                self._apply_to_widget(child, theme_data)
        except Exception:
            pass
    
    def _configure_widget(self, widget, props: dict):
        """Configure widget with theme properties."""
        # Map theme keys to widget configure keys
        config_map = {
            'fg_color': 'fg_color',
            'bg_color': 'bg_color', 
            'border_color': 'border_color',
            'text_color': 'text_color',
            'button_color': 'button_color',
            'button_hover_color': 'button_hover_color',
            'hover_color': 'hover_color',
            'progress_color': 'progress_color',
            'placeholder_text_color': 'placeholder_text_color',
            'checkmark_color': 'checkmark_color',
        }
        
        for theme_key, config_key in config_map.items():
            if theme_key in props:
                value = props[theme_key]
                # CustomTkinter expects tuple for light/dark mode
                if isinstance(value, list) and len(value) == 2:
                    value = tuple(value)
                try:
                    widget.configure(**{config_key: value})
                except Exception:
                    pass  # Widget may not support this property


class ThemeHotReloader:
    """Manages hot-reloading of theme.json."""
    
    def __init__(self, theme_path: str, root_window: ctk.CTk):
        self.theme_path = os.path.abspath(theme_path)
        self.theme_dir = os.path.dirname(self.theme_path)
        self.root = root_window
        self.observer = None
        self.handler = None
    
    def start(self):
        """Start watching for theme changes."""
        if not WATCHDOG_AVAILABLE:
            print("[HotReload] Watchdog module not found (dev only). Hot reload disabled.")
            return

        self.handler = ThemeReloadHandler(self.theme_path, self.root)
        self.observer = Observer()
        self.observer.schedule(self.handler, self.theme_dir, recursive=False)
        self.observer.start()
        print(f"[HotReload] Watching: {self.theme_path}")
    
    def stop(self):
        """Stop watching for theme changes."""
        if not WATCHDOG_AVAILABLE:
            return

        if self.observer:
            self.observer.stop()
            self.observer.join()
            print("[HotReload] Stopped")
