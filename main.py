import customtkinter as ctk
from src.ui.main_window import MainWindow
from src.ui.hot_reload import ThemeHotReloader

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("src/ui/theme.json")
    
    app = MainWindow()
    
    # Hot reload theme.json changes in real-time
    hot_reloader = ThemeHotReloader("src/ui/theme.json", app)
    hot_reloader.start()
    
    try:
        app.mainloop()
    finally:
        hot_reloader.stop()
