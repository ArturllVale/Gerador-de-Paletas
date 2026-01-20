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
        
        # --- Info & Zoom Frame ---
        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.pack(fill="x", padx=10, pady=5)
        
        # Info Label (Left)
        self.lbl_info = ctk.CTkLabel(self.info_frame, text="Carregue um SPR e uma pasta de paletas", text_color="gray")
        self.lbl_info.pack(side="left", padx=5)
        
        # Zoom controls (Right)
        self.btn_zoom_in = ctk.CTkButton(self.info_frame, text="+", width=30, command=self._zoom_in)
        self.btn_zoom_in.pack(side="right", padx=2)
        
        self.lbl_zoom_val = ctk.CTkLabel(self.info_frame, text="2x", width=30)
        self.lbl_zoom_val.pack(side="right", padx=2)
        
        self.btn_zoom_out = ctk.CTkButton(self.info_frame, text="-", width=30, command=self._zoom_out)
        self.btn_zoom_out.pack(side="right", padx=2)
        
        self.lbl_zoom = ctk.CTkLabel(self.info_frame, text="Zoom:")
        self.lbl_zoom.pack(side="right", padx=(10, 2))
        
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
        self.lbl_pal_name.pack(pady=(0, 5))
        
        # --- Animation Controls ---
        self.anim_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.anim_frame.pack(fill="x", padx=10, pady=5)
        
        # Action list (RO animations)
        self.actions = {
            0: "Idle (Parado)",
            1: "Walk (Andando)",
            2: "Sit (Sentado)",
            4: "Standby (Em Guarda)",
            5: "Attack 1",
            10: "Attack 2",
            11: "Attack 3",
            12: "Skill Cast",
        }
        
        self.lbl_anim = ctk.CTkLabel(self.anim_frame, text="Animação:", font=("Roboto", 11, "bold"))
        self.lbl_anim.pack(side="left", padx=(0, 5))
        
        self.action_var = ctk.StringVar(value="0: Idle (Parado)")
        self.combo_action = ctk.CTkComboBox(
            self.anim_frame,
            values=[f"{k}: {v}" for k, v in self.actions.items()],
            variable=self.action_var,
            width=180,
            command=self._on_action_change
        )
        self.combo_action.pack(side="left", padx=5)
        
        # Play/Pause
        self.is_playing = False
        self.animation_speed = 150  # ms between frames
        self.animation_job = None
        
        self.btn_play = ctk.CTkButton(
            self.anim_frame, 
            text="▶ Play", 
            width=80,
            fg_color="#4CAF50",
            hover_color="#388E3C",
            command=self._toggle_play
        )
        self.btn_play.pack(side="left", padx=5)
        
        # Speed control
        self.lbl_speed = ctk.CTkLabel(self.anim_frame, text="Vel:")
        self.lbl_speed.pack(side="left", padx=(10, 2))
        
        self.slider_speed = ctk.CTkSlider(
            self.anim_frame, 
            from_=50, 
            to=500, 
            width=80,
            command=self._on_speed_change
        )
        self.slider_speed.set(150)
        self.slider_speed.pack(side="left", padx=2)
        

        # Current action frames (will be calculated based on action and total frames)
        self.current_action = 0
        self.action_frames = []  # List of frame indices for current action
        self.action_frame_index = 0  # Current frame within action
        
        # Focus this window
        self.focus_force()
        self.grab_set()
    
    def _calculate_action_frames(self):
        """Calculate frame indices for current action based on RO sprite structure"""
        if not self.spr_parser or not self.spr_parser.images:
            self.action_frames = []
            return
            
        total_frames = len(self.spr_parser.images)
        
        # RO Body Sprite Frame Indices (from user):
        # Idle: 0-4
        # Walk: 5-44
        # Sit: 46 (single frame)
        # Standby: 54-59
        # Attack 1: 1, 66-69 (frame 1 is prep, then attack frames)
        # Attack 2: 80-87
        # Attack 3: 1, 96-101 (frame 1 is prep, then attack frames)
        # Skill Cast: 108-113
        
        # Define frame lists for each action
        action_frames_map = {
            0: list(range(0, 5)),           # Idle: 0-4
            1: list(range(5, 45)),          # Walk: 5-44
            2: [46],                         # Sit: single frame
            4: list(range(54, 60)),         # Standby: 54-59
            5: [1] + list(range(66, 70)),   # Attack 1: 1, 66-69
            10: list(range(80, 88)),        # Attack 2: 80-87
            11: [1] + list(range(96, 102)), # Attack 3: 1, 96-101
            12: list(range(108, 114)),      # Skill Cast: 108-113
        }
        
        if self.current_action in action_frames_map:
            # Use the predefined frame list directly
            self.action_frames = action_frames_map[self.current_action].copy()
        else:
            # Unknown action, use estimate
            frames_per_action = max(8, total_frames // 30)
            start_frame = self.current_action * frames_per_action
            end_frame = min(start_frame + frames_per_action, total_frames)
            
            if start_frame >= total_frames:
                self.action_frames = list(range(total_frames))
            else:
                self.action_frames = list(range(start_frame, end_frame))
        
        # Clamp all frames to valid range
        self.action_frames = [f for f in self.action_frames if 0 <= f < total_frames]
        self.action_frame_index = 0
    
    def _on_action_change(self, value):
        """Handle action selection change"""
        # Extract action ID from "0: Idle (Parado)" format
        try:
            action_id = int(value.split(":")[0])
            self.current_action = action_id
            self._calculate_action_frames()
            if self.action_frames:
                self.current_frame_index = self.action_frames[0]
                self._update_display()
        except:
            pass
    
    def _toggle_play(self):
        """Toggle animation play/pause"""
        self.is_playing = not self.is_playing
        
        if self.is_playing:
            self.btn_play.configure(text="⏸ Pause", fg_color="#FF5555", hover_color="#CC0000")
            self._animate()
        else:
            self.btn_play.configure(text="▶ Play", fg_color="#4CAF50", hover_color="#388E3C")
            if self.animation_job:
                self.after_cancel(self.animation_job)
                self.animation_job = None
    
    def _animate(self):
        """Advance animation frame"""
        if not self.is_playing or not self.action_frames:
            return
            
        # Advance to next frame in action
        self.action_frame_index = (self.action_frame_index + 1) % len(self.action_frames)
        self.current_frame_index = self.action_frames[self.action_frame_index]
        self._update_display()
        
        # Schedule next frame
        self.animation_job = self.after(self.animation_speed, self._animate)
    
    def _on_speed_change(self, value):
        """Handle speed slider change"""
        # Invert: low value = fast, high value = slow
        self.animation_speed = int(550 - value)
        
    def _zoom_in(self):
        current = self.preview.scale
        new_scale = min(10.0, current + 1.0)
        self.preview.set_scale(new_scale)
        self.lbl_zoom_val.configure(text=f"{int(new_scale)}x")

    def _zoom_out(self):
        current = self.preview.scale
        new_scale = max(1.0, current - 1.0)
        self.preview.set_scale(new_scale)
        self.lbl_zoom_val.configure(text=f"{int(new_scale)}x")
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
