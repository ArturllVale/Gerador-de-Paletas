import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import glob

from src.core.parsers.spr import SprParser
from src.core.parsers.act import ActParser
from src.core.logic.state import ProjectState
from src.core.generator import PaletteGenerator
from src.core.pal_handler import PaletteHandler

from src.ui.visualizer import PaletteVisualizer
from src.ui.components_v2 import GroupManagementFrame, GroupSettingsFrame
from src.ui.preview import SpritePreview
from src.ui.preview_window import PreviewWindow
from src.ui.class_selector import ClassSelectorWindow

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("RO Palette Generator")
        self.geometry("1100x900")
        
        # Logic State
        self.project_state = ProjectState()
        self.current_spr = None
        self.current_active_group = None
        self.current_filename = "palette"
        
        # Layout:
        # Top: File Controls
        # Row 1: 
        #   Col 0 (Left): Group Management & Visualizer
        #   Col 1 (Right): Settings & Preview
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Frame index for preview
        self.current_frame_index = 0
        self.is_playing = False
        
        # --- Top Menu ---
        self.top_frame = ctk.CTkFrame(self, height=40)
        self.top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.btn_load_spr = ctk.CTkButton(self.top_frame, text="Carregar SPR", command=self.load_spr)
        self.btn_load_spr.pack(side="left", padx=5, pady=5)
        
        self.btn_preview_mode = ctk.CTkButton(
            self.top_frame, 
            text="🎨 Modo Preview", 
            command=self.enter_preview_mode,
            fg_color="#E07A5F",  # Orange
            hover_color="#C0583D"
        )
        self.btn_preview_mode.pack(side="left", padx=5, pady=5)
        
        # --- Generate Palettes Button (General) ---
        self.frame_gen_controls = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        self.frame_gen_controls.pack(side="right", padx=10, pady=5)
        
        # Start number
        self.lbl_start = ctk.CTkLabel(self.frame_gen_controls, text="Iniciar em:")
        self.lbl_start.pack(side="left", padx=2)
        
        self.entry_start = ctk.CTkEntry(self.frame_gen_controls, width=50)
        self.entry_start.insert(0, "0")
        self.entry_start.pack(side="left", padx=2)
        
        self.lbl_count = ctk.CTkLabel(self.frame_gen_controls, text="Qtd:")
        self.lbl_count.pack(side="left", padx=2)
        
        self.entry_count = ctk.CTkEntry(self.frame_gen_controls, width=50)
        self.entry_count.insert(0, "10")
        self.entry_count.pack(side="left", padx=2)
        
        # Class selector button
        self.btn_class_selector = ctk.CTkButton(
            self.frame_gen_controls,
            text="📋 Classes",
            command=self._open_class_selector,
            width=80
        )
        self.btn_class_selector.pack(side="left", padx=5)
        
        # Store selected classes
        self.selected_classes = set()
        self.class_selector_window = None
        
        self.btn_generate = ctk.CTkButton(
            self.frame_gen_controls, 
            text="🎲 Gerar Paletas", 
            command=self.generate_all_groups,
            fg_color="#4CAF50",
            hover_color="#388E3C",
            width=140
        )
        self.btn_generate.pack(side="left", padx=5)

        # --- Random options ---
        self.chk_rand_sat = ctk.CTkCheckBox(self.frame_gen_controls, text="Sat. Aleatória", width=100)
        self.chk_rand_sat.pack(side="left", padx=5)
        
        self.chk_rand_bri = ctk.CTkCheckBox(self.frame_gen_controls, text="Brilho Aleatório", width=100)
        self.chk_rand_bri.pack(side="left", padx=5)
        
        self.lbl_info = ctk.CTkLabel(self.top_frame, text="Nenhum arquivo carregado")
        self.lbl_info.pack(side="left", padx=10)
        
        # --- Left Column: Groups & Visualizer ---
        self.left_col = ctk.CTkFrame(self, fg_color="transparent")
        self.left_col.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.left_col.grid_rowconfigure(2, weight=1) # Visualizer expands
        
        # Groups
        self.group_mgr = GroupManagementFrame(
            self.left_col, 
            add_group_cmd=None, # Removed explicit Add button
            remove_group_cmd=self.remove_group
        )
        self.group_mgr.btn_add.pack_forget() # Hide the add button
        self.group_mgr.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.group_mgr.on_group_select = self.select_group
        self.group_mgr.on_deselect = self.deselect_group
        
        # Visualizer
        self.lbl_vis = ctk.CTkLabel(self.left_col, text="Visualizador de Paleta (Selecione cores → Criar Grupo)", font=("Roboto", 12, "bold"))
        self.lbl_vis.grid(row=1, column=0, sticky="w", padx=5)
        
        # Visualizer Container
        self.vis_frame = ctk.CTkFrame(self.left_col)
        self.vis_frame.grid(row=2, column=0, sticky="nsew")
        
        self.visualizer = PaletteVisualizer(self.vis_frame)
        self.visualizer.grid(padx=10, pady=10)
        
        self.btn_create_group = ctk.CTkButton(self.left_col, text="Criar Grupo da Seleção", command=self.create_group_from_selection)
        self.btn_create_group.grid(row=3, column=0, pady=10, sticky="ew", padx=10)
        
        # Bind toggle event to update group indices
        original_click = self.visualizer._on_click
        original_drag = self.visualizer._on_drag
        
        def new_click(event):
            original_click(event)
            if self.current_active_group:
                self._sync_selection_to_group()
            self._update_preview() 
            
        def new_drag(event):
            original_drag(event)
            if self.current_active_group:
               self._sync_selection_to_group()

        self.visualizer.canvas.bind("<Button-1>", new_click)
        self.visualizer.canvas.bind("<B1-Motion>", new_drag)
        
        # --- Right Column: Settings & Preview ---
        self.right_col = ctk.CTkFrame(self, fg_color="transparent")
        self.right_col.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        self.right_col.grid_rowconfigure(1, weight=1)
        
        # Settings
        self.settings_panel = GroupSettingsFrame(self.right_col)
        self.settings_panel.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.settings_panel.on_change_callback = self._update_preview
        
        # Preview
        self.lbl_prev = ctk.CTkLabel(self.right_col, text="Prévia (Clique no sprite para selecionar cor)", font=("Roboto", 12, "bold"))
        self.lbl_prev.grid(row=1, column=0, sticky="nw", padx=5)
        
        self.preview = SpritePreview(self.right_col)
        self.preview.grid(row=2, column=0, sticky="nsew")
        self.preview.on_pixel_click = self._on_preview_click
        
        # Frame navigation controls
        self.frame_nav = ctk.CTkFrame(self.right_col, fg_color="transparent")
        self.frame_nav.grid(row=3, column=0, pady=5)
        
        self.btn_prev_frame = ctk.CTkButton(self.frame_nav, text="◀", width=40, command=self._prev_frame)
        self.btn_prev_frame.pack(side="left", padx=5)
        
        self.lbl_frame_info = ctk.CTkLabel(self.frame_nav, text="Frame: 0/0")
        self.lbl_frame_info.pack(side="left", padx=10)
        
        self.btn_next_frame = ctk.CTkButton(self.frame_nav, text="▶", width=40, command=self._next_frame)
        self.btn_next_frame.pack(side="left", padx=5)
        
        self.btn_play = ctk.CTkButton(self.frame_nav, text="▶ Play", width=60, command=self._toggle_play, fg_color="#2CC985", hover_color="#229965")
        self.btn_play.pack(side="left", padx=10)

    def load_spr(self):
        path = filedialog.askopenfilename(filetypes=[("RO Sprite", "*.spr")])
        if not path: return
        
        try:
            self.project_state.spr_parser = SprParser(path)
            self.project_state.spr_parser.extract_palette()
            self.project_state.spr_parser.parse_images()
            
            self.project_state.palette = self.project_state.spr_parser.palette
            self.current_filename = os.path.splitext(os.path.basename(path))[0]
            
            self.lbl_info.configure(text=f"Carregado: {self.current_filename}")
            
            # Reset UI
            self.current_frame_index = 0
            self.visualizer.set_palette([x[:3] for x in self.project_state.palette]) 
            self.project_state.groups.clear()
            self.group_mgr.update_groups(self.project_state.groups)
            self.settings_panel.load_group(None)
            self._update_preview()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar SPR: {e}")

    # def load_act(self): ... Removed from UI access

    def create_group_from_selection(self):
        selection = self.visualizer.get_selection_mask()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione cores primeiro!")
            return
            
        # Prompt for name
        dialog = ctk.CTkInputDialog(text="Nome do Grupo:", title="Novo Grupo")
        name = dialog.get_input()
        if not name: return
        
        group = self.project_state.add_group(name)
        group.set_indices(selection)
        
        self.group_mgr.update_groups(self.project_state.groups, selected_group=group)
        self.select_group(group)

    # def add_group(self, name="New Group"): ... Removed logic call

    def remove_group(self):
        if self.current_active_group:
            self.project_state.remove_group(self.current_active_group)
            self.current_active_group = None
            new_sel = self.project_state.groups[0] if self.project_state.groups else None
            self.group_mgr.update_groups(self.project_state.groups, selected_group=new_sel)
            self.select_group(new_sel)
            if not new_sel:
                self.visualizer.clear_selection()
            
    def select_group(self, group):
        self.current_active_group = group
        self.group_mgr.update_groups(self.project_state.groups, selected_group=group)
        self.settings_panel.load_group(group)
        
        if group:
            # Sync visualizer selection to group indices
            self.visualizer.selected_indices = group.indices.copy()
            self.visualizer._redraw_colors()
        else:
            self.visualizer.clear_selection()
    
    def deselect_group(self):
        """Deselect current group and clear visualizer selection"""
        self.current_active_group = None
        self.group_mgr.update_groups(self.project_state.groups, selected_group=None)
        self.settings_panel.load_group(None)
        self.visualizer.clear_selection()
        self._update_preview()
            
    def _sync_selection_to_group(self):
        if self.current_active_group:
            self.current_active_group.set_indices(self.visualizer.get_selection_mask())
            
    def _on_preview_click(self, palette_index):
        """Handle click on preview sprite - select the 8-color ramp containing this index"""
        if palette_index is None:
            return
            
        # Calculate the ramp (row of 8 colors in a 16x16 grid = half-row)
        # Each ramp is 8 consecutive indices: 0-7, 8-15, 16-23, etc.
        ramp_start = (palette_index // 8) * 8
        ramp_end = ramp_start + 8
        ramp_indices = set(range(ramp_start, min(ramp_end, 256)))
        
        # Check if ramp is already fully selected - if so, deselect it
        if ramp_indices.issubset(self.visualizer.selected_indices):
            # Deselect the ramp
            self.visualizer.selected_indices -= ramp_indices
        else:
            # Add the ramp to selection
            self.visualizer.selected_indices |= ramp_indices
            
        # Redraw all affected cells
        self.visualizer._redraw_colors()
        
        # Sync to active group if any
        if self.current_active_group:
            self._sync_selection_to_group()
            
    def _update_preview(self):
        if not self.project_state.spr_parser or not self.project_state.spr_parser.images:
            self.lbl_frame_info.configure(text="Frame: 0/0")
            return
            
        # 1. Get Base Image using current_frame_index
        total_frames = len(self.project_state.spr_parser.images)
        
        # Ensure index is valid
        if self.current_frame_index >= total_frames:
            self.current_frame_index = 0
        
        base_img = self.project_state.spr_parser.images[self.current_frame_index]
        
        # Update frame info label
        self.lbl_frame_info.configure(text=f"Frame: {self.current_frame_index + 1}/{total_frames}")
        
        # 2. Apply Group Transformations to Palette
        temp_pal = list(self.project_state.spr_parser.palette) # [r,g,b,a]
        
        # Apply logic for "Progress 100%" or just current settings?
        # User wants to see what the settings do.
        # Let's apply the current settings as if they were fully applied.
        
        for group in self.project_state.groups:
            # Check if group has fixed gradient
            is_fixed = getattr(group, 'is_fixed', False)
            
            if is_fixed:
                # Apply fixed gradient directly to indices
                fixed_gradient = getattr(group, 'fixed_gradient', None)
                if fixed_gradient and len(fixed_gradient) == 8:
                    sorted_indices = sorted(group.indices)
                    num_colors = len(sorted_indices)
                    
                    for j, idx in enumerate(sorted_indices):
                        if 0 <= idx < 256:
                            # Map index position to gradient position
                            gradient_pos = int((j / max(num_colors - 1, 1)) * 7)
                            gradient_pos = min(gradient_pos, 7)
                            base_col = fixed_gradient[gradient_pos]
                            
                            # Apply saturation and brightness adjustments
                            import colorsys
                            r, g, b = base_col[0]/255, base_col[1]/255, base_col[2]/255
                            h, s, v = colorsys.rgb_to_hsv(r, g, b)
                            
                            # Apply shifts
                            s = max(0, min(1, s + group.sat_shift))
                            v = max(0, min(1, v * (1 + group.val_shift)))
                            
                            r, g, b = colorsys.hsv_to_rgb(h, s, v)
                            new_col = (int(r*255), int(g*255), int(b*255))
                            temp_pal[idx] = (*new_col, 255)
            else:
                # Original logic for non-fixed groups
                shift = group.hue_shift_start
                
                for i in group.indices:
                    if 0 <= i < 256:
                        from src.core.color_math import apply_adjustments, apply_colorize
                        orig = temp_pal[i][:3]
                        
                        if getattr(group, 'mode', 'hsv') == 'colorize':
                            new_col = apply_colorize(
                                 orig,
                                 target_hue=shift,
                                 target_sat=group.sat_shift,
                                 value_mult=1.0 + group.val_shift
                            )
                        else:
                            new_col = apply_adjustments(
                                orig, 
                                hue_shift=shift, 
                                saturation_mult=1+group.sat_shift, 
                                value_mult=1+group.val_shift
                            )
                            
                        temp_pal[i] = (*new_col, 255)
        
        self.preview.set_sprite(base_img, palette=temp_pal)
        
    def _open_class_selector(self):
        """Open class selector window."""
        if self.class_selector_window is None or not self.class_selector_window.winfo_exists():
            self.class_selector_window = ClassSelectorWindow(self, self.selected_classes)
        else:
            self.class_selector_window.focus()
    
    def generate_all_groups(self):
        """Generate palettes considering all groups."""
        if not self.project_state.groups:
            messagebox.showwarning("Aviso", "Crie pelo menos um grupo de cores primeiro!")
            return
              
        try:
            count = int(self.entry_count.get())
        except ValueError:
            messagebox.showerror("Erro", "Quantidade inválida")
            return
        
        try:
            start_number = int(self.entry_start.get())
        except ValueError:
            start_number = 0

        output = filedialog.askdirectory()
        if not output: return
        
        # Get selected classes from the class selector
        # Always include base_filename, plus any selected classes
        class_names = [self.current_filename]
        if self.class_selector_window and self.class_selector_window.winfo_exists():
            self.selected_classes = self.class_selector_window.selected_classes
        
        if self.selected_classes:
            class_names.extend(list(self.selected_classes))
        
        try:
            gen = PaletteGenerator([x[:3] for x in self.project_state.palette])
            gen.generate_batch(
                output_dir=output,
                base_filename=self.current_filename,
                count=count,
                groups=self.project_state.groups,
                start_number=start_number,
                class_names=class_names,
                random_saturation=self.chk_rand_sat.get() == 1,
                random_brightness=self.chk_rand_bri.get() == 1
            )
            
            # Calculate total files generated
            num_names = len(class_names) if class_names else 1
            total_files = count * num_names * 2  # *2 for male/female
            messagebox.showinfo("Sucesso", f"Gerados {total_files} arquivos ({count} variações)!")
            os.startfile(output)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _prev_frame(self):
        if not self.project_state.spr_parser or not self.project_state.spr_parser.images:
            return
        total_frames = len(self.project_state.spr_parser.images)
        self.current_frame_index = (self.current_frame_index - 1) % total_frames
        self._update_preview()

    def _next_frame(self):
        if not self.project_state.spr_parser or not self.project_state.spr_parser.images:
            return
        total_frames = len(self.project_state.spr_parser.images)
        self.current_frame_index = (self.current_frame_index + 1) % total_frames
        self._update_preview()

    def _toggle_play(self):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.btn_play.configure(text="⏸ Pause", fg_color="#FF5555", hover_color="#CC0000")
            self._animate_loop()
        else:
            self.btn_play.configure(text="▶ Play", fg_color="#2CC985", hover_color="#229965")
    
    def _animate_loop(self):
        if self.is_playing:
            self._next_frame()
            # 150ms delay for animation
            self.after(150, self._animate_loop)

    def enter_preview_mode(self):
        """Open preview mode window"""
        PreviewWindow(self)
