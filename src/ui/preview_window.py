import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import glob

from src.core.parsers.spr import SprParser
from src.core.pal_handler import PaletteHandler
from src.ui.preview import SpritePreview


class PreviewWindow(ctk.CTkToplevel):
    """Separate window for previewing palettes on sprites"""
    
    def __init__(self, master=None):
        super().__init__(master)
        
        self.title("Modo Preview - Visualizador de Paletas")
        self.geometry("500x600")
        self.resizable(True, True)
        
        # State
        self.spr_parser = None
        self.palettes = []  # List of palette file paths
        self.current_palette_index = 0
        self.current_frame_index = 0
        
        # --- Top Controls ---
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(fill="x", padx=10, pady=10)
        
        self.btn_load_spr = ctk.CTkButton(
            self.top_frame, 
            text="📁 Carregar SPR", 
            command=self._load_spr
        )
        self.btn_load_spr.pack(side="left", padx=5)
        
        self.btn_load_folder = ctk.CTkButton(
            self.top_frame, 
            text="📂 Carregar Pasta de Paletas", 
            command=self._load_palette_folder,
            fg_color="#E07A5F",
            hover_color="#C0583D"
        )
        self.btn_load_folder.pack(side="left", padx=5)
        
        # --- Info Label ---
        self.lbl_info = ctk.CTkLabel(self, text="Carregue um SPR e uma pasta de paletas", text_color="gray")
        self.lbl_info.pack(pady=5)
        
        # --- Preview Area ---
        self.preview = SpritePreview(self)
        self.preview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # --- Navigation ---
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(fill="x", padx=10, pady=10)
        
        # Palette navigation
        self.lbl_pal = ctk.CTkLabel(self.nav_frame, text="Paleta:", font=("Roboto", 11, "bold"))
        self.lbl_pal.pack(side="left", padx=(0, 5))
        
        self.btn_prev_pal = ctk.CTkButton(self.nav_frame, text="◀", width=40, command=self._prev_palette)
        self.btn_prev_pal.pack(side="left", padx=2)
        
        self.lbl_pal_count = ctk.CTkLabel(self.nav_frame, text="0/0", width=60)
        self.lbl_pal_count.pack(side="left", padx=5)
        
        self.btn_next_pal = ctk.CTkButton(self.nav_frame, text="▶", width=40, command=self._next_palette)
        self.btn_next_pal.pack(side="left", padx=2)
        
        # Separator
        ctk.CTkLabel(self.nav_frame, text="   |   ").pack(side="left")
        
        # Frame navigation
        self.lbl_frame = ctk.CTkLabel(self.nav_frame, text="Frame:", font=("Roboto", 11, "bold"))
        self.lbl_frame.pack(side="left", padx=(10, 5))
        
        self.btn_prev_frame = ctk.CTkButton(self.nav_frame, text="◀", width=40, command=self._prev_frame)
        self.btn_prev_frame.pack(side="left", padx=2)
        
        self.lbl_frame_count = ctk.CTkLabel(self.nav_frame, text="0/0", width=60)
        self.lbl_frame_count.pack(side="left", padx=5)
        
        self.btn_next_frame = ctk.CTkButton(self.nav_frame, text="▶", width=40, command=self._next_frame)
        self.btn_next_frame.pack(side="left", padx=2)
        
        # Palette name
        self.lbl_pal_name = ctk.CTkLabel(self, text="", text_color="gray")
        self.lbl_pal_name.pack(pady=(0, 10))
        
        # Focus this window
        self.focus_force()
        self.grab_set()
        
    def _load_spr(self):
        """Load SPR file"""
        path = filedialog.askopenfilename(
            filetypes=[("RO Sprite", "*.spr")],
            title="Selecione o arquivo SPR"
        )
        if not path:
            return
            
        try:
            self.spr_parser = SprParser(path)
            self.spr_parser.extract_palette()
            self.spr_parser.parse_images()
            self.current_frame_index = 0
            
            spr_name = os.path.basename(path)
            self.lbl_info.configure(text=f"SPR: {spr_name}")
            
            self._update_display()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar SPR: {e}")
            
    def _load_palette_folder(self):
        """Load folder with .pal files"""
        folder = filedialog.askdirectory(title="Selecione a pasta com arquivos .pal")
        if not folder:
            return
            
        # Find all .pal files
        pal_files = glob.glob(os.path.join(folder, "*.pal"))
        if not pal_files:
            messagebox.showwarning("Aviso", "Nenhum arquivo .pal encontrado na pasta!")
            return
            
        # Sort files naturally
        pal_files.sort()
        
        self.palettes = pal_files
        self.current_palette_index = 0
        
        self._update_display()
        
    def _prev_palette(self):
        if not self.palettes:
            return
        self.current_palette_index = (self.current_palette_index - 1) % len(self.palettes)
        self._update_display()
        
    def _next_palette(self):
        if not self.palettes:
            return
        self.current_palette_index = (self.current_palette_index + 1) % len(self.palettes)
        self._update_display()
        
    def _prev_frame(self):
        if not self.spr_parser or not self.spr_parser.images:
            return
        total = len(self.spr_parser.images)
        self.current_frame_index = (self.current_frame_index - 1) % total
        self._update_display()
        
    def _next_frame(self):
        if not self.spr_parser or not self.spr_parser.images:
            return
        total = len(self.spr_parser.images)
        self.current_frame_index = (self.current_frame_index + 1) % total
        self._update_display()
        
    def _update_display(self):
        """Update the preview display"""
        # Update frame counter
        if self.spr_parser and self.spr_parser.images:
            total_frames = len(self.spr_parser.images)
            self.lbl_frame_count.configure(text=f"{self.current_frame_index + 1}/{total_frames}")
        else:
            self.lbl_frame_count.configure(text="0/0")
            
        # Update palette counter
        if self.palettes:
            total_pals = len(self.palettes)
            self.lbl_pal_count.configure(text=f"{self.current_palette_index + 1}/{total_pals}")
            pal_name = os.path.basename(self.palettes[self.current_palette_index])
            self.lbl_pal_name.configure(text=pal_name)
        else:
            self.lbl_pal_count.configure(text="0/0")
            self.lbl_pal_name.configure(text="")
            
        # Update preview
        if not self.spr_parser or not self.spr_parser.images:
            return
            
        # Get frame image
        if self.current_frame_index >= len(self.spr_parser.images):
            self.current_frame_index = 0
        base_img = self.spr_parser.images[self.current_frame_index]
        
        # Get palette
        if self.palettes:
            try:
                pal_path = self.palettes[self.current_palette_index]
                palette = PaletteHandler.load(pal_path)
                palette_rgba = [(r, g, b, 255) for r, g, b in palette]
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao carregar paleta: {e}")
                return
        else:
            # Use original palette from SPR
            palette_rgba = self.spr_parser.palette
            
        self.preview.set_sprite(base_img, palette=palette_rgba)
