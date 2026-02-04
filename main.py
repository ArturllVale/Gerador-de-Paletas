import customtkinter as ctk
from src.ui.main_window import MainWindow
from src.ui.hot_reload import ThemeHotReloader
from src.utils.resource_path import get_resource_path

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    
    theme_path = get_resource_path("src/ui/theme.json")
    ctk.set_default_color_theme(theme_path)
    
    app = MainWindow()
    
    # Hot reload theme.json changes in real-time
    hot_reloader = ThemeHotReloader(theme_path, app)
    hot_reloader.start()
    
    try:
        app.mainloop()
    finally:
        hot_reloader.stop()
