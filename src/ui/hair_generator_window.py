import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
import colorsys

from src.core.parsers.spr import SprParser
from src.core.logic.state import ProjectState
from src.core.hair_generator import HairPaletteGenerator
from src.core.color_math import apply_adjustments, apply_colorize

from src.ui.visualizer import PaletteVisualizer
from src.ui.components_v2 import GroupManagementFrame, GroupSettingsFrame
from src.ui.preview import SpritePreview
from src.ui.icons import IconManager


class HairGeneratorWindow(ctk.CTkToplevel):
    """Window for generating hair palettes (Cebelos)."""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.icon_manager = IconManager()
        self.title("Gerador de Paletas de Cabelo")
        self.geometry("1200x850")
        self.transient(parent)
        
        # Logic State
        self.project_state = ProjectState()
        self.current_spr = None
        self.current_active_group = None
        self.current_frame_index = 0
        self._preview_pending = None
        
        # Layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)
        
        self._create_top_bar()
        self._create_left_column()
        self._create_mid_column()
        self._create_right_column()
    
    def _create_top_bar(self):
        """Create top menu bar with generation controls."""
        self.top_frame = ctk.CTkFrame(self, height=40)
        self.top_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        
        # Load SPR Button
        self.btn_load_spr = ctk.CTkButton(
            self.top_frame,
            text="Carregar SPR",
            command=self.load_spr
        )
        self.btn_load_spr.pack(side="left", padx=5, pady=5)
        
        # Info label
        self.lbl_info = ctk.CTkLabel(self.top_frame, text="Nenhum arquivo carregado")
        self.lbl_info.pack(side="left", padx=10)
        
        # --- Generation Controls (right side) ---
        self.frame_gen_controls = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        self.frame_gen_controls.pack(side="right", padx=10, pady=5)
        
        # Hair style count
        self.lbl_styles = ctk.CTkLabel(self.frame_gen_controls, text="Estilos:")
        self.lbl_styles.pack(side="left", padx=2)
        
        self.entry_styles = ctk.CTkEntry(self.frame_gen_controls, width=50)
        self.entry_styles.insert(0, "40")
        self.entry_styles.pack(side="left", padx=2)
        
        # Start number
        self.lbl_start = ctk.CTkLabel(self.frame_gen_controls, text="Iniciar em:")
        self.lbl_start.pack(side="left", padx=2)
        
        self.entry_start = ctk.CTkEntry(self.frame_gen_controls, width=50)
        self.entry_start.insert(0, "0")
        self.entry_start.pack(side="left", padx=2)
        
        # Quantity
        self.lbl_count = ctk.CTkLabel(self.frame_gen_controls, text="Qtd:")
        self.lbl_count.pack(side="left", padx=2)
        
        self.entry_count = ctk.CTkEntry(self.frame_gen_controls, width=50)
        self.entry_count.insert(0, "10")
        self.entry_count.pack(side="left", padx=2)
        
        # Generate button
        self.btn_generate = ctk.CTkButton(
            self.frame_gen_controls,
            text="Gerar Paletas",
            image=self.icon_manager.get_icon("generate"),
            compound="left",
            command=self.generate_palettes,
            width=140
        )
        self.btn_generate.pack(side="left", padx=5)
        
        # Random options
        self.chk_rand_sat = ctk.CTkCheckBox(self.frame_gen_controls, text="Sat. Aleatória", width=100)
        self.chk_rand_sat.pack(side="left", padx=5)
        
        self.chk_rand_bri = ctk.CTkCheckBox(self.frame_gen_controls, text="Brilho Aleatório", width=100)
        self.chk_rand_bri.pack(side="left", padx=5)
    
    def _create_left_column(self):
        """Create left column with groups and visualizer."""
        self.left_col = ctk.CTkFrame(self, fg_color="transparent")
        self.left_col.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.left_col.grid_rowconfigure(2, weight=1)
        
        # Groups
        self.group_mgr = GroupManagementFrame(
            self.left_col,
            add_group_cmd=None,
            remove_group_cmd=self.remove_group
        )
        self.group_mgr.btn_add.pack_forget()
        self.group_mgr.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.group_mgr.on_group_select = self.select_group
        self.group_mgr.on_deselect = self.deselect_group
        
        # Visualizer label
        self.lbl_vis = ctk.CTkLabel(
            self.left_col,
            text="Visualizador de Paleta (Selecione cores → Criar Grupo)",
            font=("Roboto", 12, "bold")
        )
        self.lbl_vis.grid(row=1, column=0, sticky="w", padx=5)
        
        # Visualizer frame
        self.vis_frame = ctk.CTkFrame(self.left_col)
        self.vis_frame.grid(row=2, column=0, sticky="nsew")
        
        self.visualizer = PaletteVisualizer(self.vis_frame)
        self.visualizer.grid(padx=10, pady=10)
        
        # Create group button
        self.btn_create_group = ctk.CTkButton(
            self.left_col,
            text="Criar Grupo da Seleção",
            command=self.create_group_from_selection
        )
        self.btn_create_group.grid(row=3, column=0, pady=10, sticky="ew", padx=10)
        
        # Bind visualizer events
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
        
        # Connect hover to preview highlight
        self.visualizer.on_hover_callback = self._on_palette_hover
    
    def _create_mid_column(self):
        """Create middle column with group settings."""
        self.mid_col = ctk.CTkFrame(self, fg_color="transparent")
        self.mid_col.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        self.settings_panel = GroupSettingsFrame(self.mid_col)
        self.settings_panel.pack(fill="both", expand=True)
        self.settings_panel.on_change_callback = self._update_preview
    
    def _create_right_column(self):
        """Create right column with preview."""
        self.right_col = ctk.CTkFrame(self, fg_color="transparent")
        self.right_col.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)
        self.right_col.grid_rowconfigure(1, weight=1)
        
        # Preview label
        self.lbl_prev = ctk.CTkLabel(
            self.right_col,
            text="Prévia (Clique no sprite para selecionar cor)",
            font=("Roboto", 12, "bold")
        )
        self.lbl_prev.grid(row=0, column=0, sticky="nw", padx=5)
        
        # Preview
        self.preview = SpritePreview(self.right_col)
        self.preview.grid(row=1, column=0, sticky="nsew")
        self.preview.on_pixel_click = self._on_preview_click
        
        # Frame navigation
        self.frame_nav = ctk.CTkFrame(self.right_col, fg_color="transparent")
        self.frame_nav.grid(row=2, column=0, pady=5)
        
        self.btn_prev_frame = ctk.CTkButton(
            self.frame_nav,
            text="",
            image=self.icon_manager.get_icon("prev"),
            width=40,
            command=self._prev_frame
        )
        self.btn_prev_frame.pack(side="left", padx=5)
        
        self.lbl_frame_info = ctk.CTkLabel(self.frame_nav, text="Frame: 0/0")
        self.lbl_frame_info.pack(side="left", padx=10)
        
        self.btn_next_frame = ctk.CTkButton(
            self.frame_nav,
            text="",
            image=self.icon_manager.get_icon("next"),
            width=40,
            command=self._next_frame
        )
        self.btn_next_frame.pack(side="left", padx=5)
    
    # --- Group Management ---
    
    def create_group_from_selection(self):
        selection = self.visualizer.get_selection_mask()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione cores primeiro!")
            return
        
        dialog = ctk.CTkInputDialog(text="Nome do Grupo:", title="Novo Grupo")
        name = dialog.get_input()
        if not name:
            return
        
        group = self.project_state.add_group(name)
        group.set_indices(selection)
        
        self.group_mgr.update_groups(self.project_state.groups, selected_group=group)
        self.select_group(group)
    
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
            self.visualizer.selected_indices = group.indices.copy()
            self.visualizer._redraw_colors()
        else:
            self.visualizer.clear_selection()
    
    def deselect_group(self):
        self.current_active_group = None
        self.group_mgr.update_groups(self.project_state.groups, selected_group=None)
        self.settings_panel.load_group(None)
        self.visualizer.clear_selection()
        self._update_preview()
    
    def _sync_selection_to_group(self):
        if self.current_active_group:
            self.current_active_group.set_indices(self.visualizer.get_selection_mask())
    
    # --- Preview ---
    
    def _on_palette_hover(self, palette_index):
        if palette_index is not None and self.visualizer.selected_indices:
            self.preview.highlight_pixels(self.visualizer.selected_indices)
        else:
            self.preview.highlight_pixels(None)
    
    def _on_preview_click(self, palette_index):
        if palette_index is None:
            return
        
        ramp_start = (palette_index // 8) * 8
        ramp_end = ramp_start + 8
        ramp_indices = set(range(ramp_start, min(ramp_end, 256)))
        
        if ramp_indices.issubset(self.visualizer.selected_indices):
            self.visualizer.selected_indices -= ramp_indices
        else:
            self.visualizer.selected_indices |= ramp_indices
        
        self.visualizer._redraw_colors()
        
        if self.current_active_group:
            self._sync_selection_to_group()
    
    def _update_preview(self):
        if self._preview_pending:
            self.after_cancel(self._preview_pending)
        self._preview_pending = self.after(16, self._do_update_preview)
    
    def _do_update_preview(self):
        self._preview_pending = None
        
        if not self.project_state.spr_parser or not self.project_state.spr_parser.images:
            self.lbl_frame_info.configure(text="Frame: 0/0")
            return
        
        total_frames = len(self.project_state.spr_parser.images)
        
        if self.current_frame_index >= total_frames:
            self.current_frame_index = 0
        
        base_img = self.project_state.spr_parser.images[self.current_frame_index]
        self.lbl_frame_info.configure(text=f"Frame: {self.current_frame_index + 1}/{total_frames}")
        
        temp_pal = list(self.project_state.spr_parser.palette)
        
        for group in self.project_state.groups:
            is_fixed = getattr(group, 'is_fixed', False)
            
            if is_fixed:
                fixed_gradient = getattr(group, 'fixed_gradient', None)
                if fixed_gradient and len(fixed_gradient) == 8:
                    sorted_indices = sorted(group.indices)
                    num_colors = len(sorted_indices)
                    
                    for j, idx in enumerate(sorted_indices):
                        if 0 <= idx < 256:
                            gradient_pos = int((j / max(num_colors - 1, 1)) * 7)
                            gradient_pos = min(gradient_pos, 7)
                            base_col = fixed_gradient[gradient_pos]
                            
                            r, g, b = base_col[0]/255, base_col[1]/255, base_col[2]/255
                            h, s, v = colorsys.rgb_to_hsv(r, g, b)
                            
                            s = max(0, min(1, s + group.sat_shift))
                            v = max(0, min(1, v * (1 + group.val_shift)))
                            
                            r, g, b = colorsys.hsv_to_rgb(h, s, v)
                            new_col = (int(r*255), int(g*255), int(b*255))
                            temp_pal[idx] = (*new_col, 255)
            else:
                shift = group.hue_shift_start
                
                for i in group.indices:
                    if 0 <= i < 256:
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
    
    # --- Frame Navigation ---
    
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
    
    # --- SPR Loading ---
    
    def load_spr(self):
        path = filedialog.askopenfilename(filetypes=[("RO Sprite", "*.spr")])
        if not path:
            return
        
        try:
            self.project_state.spr_parser = SprParser(path)
            self.project_state.spr_parser.extract_palette()
            self.project_state.spr_parser.parse_images()
            
            self.project_state.palette = self.project_state.spr_parser.palette
            filename = os.path.splitext(os.path.basename(path))[0]
            
            self.lbl_info.configure(text=f"Carregado: {filename}")
            
            # Reset UI
            self.current_frame_index = 0
            self.visualizer.set_palette([x[:3] for x in self.project_state.palette])
            self.project_state.groups.clear()
            self.group_mgr.update_groups(self.project_state.groups)
            self.settings_panel.load_group(None)
            self._update_preview()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar SPR: {e}")
    
    # --- Generation ---
    
    def generate_palettes(self):
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
        
        try:
            style_count = int(self.entry_styles.get())
        except ValueError:
            style_count = 40
        
        output = filedialog.askdirectory()
        if not output:
            return
        
        # Disable button during generation
        self.btn_generate.configure(state="disabled")
        
        # Create progress window
        self._progress_window = ctk.CTkToplevel(self)
        self._progress_window.title("Gerando Paletas de Cabelo...")
        self._progress_window.geometry("400x120")
        self._progress_window.transient(self)
        self._progress_window.grab_set()
        
        self._progress_label = ctk.CTkLabel(self._progress_window, text="Iniciando...")
        self._progress_label.pack(pady=10)
        
        total_files = count * 2  # Male and female
        
        self._progress_bar = ctk.CTkProgressBar(self._progress_window, width=350)
        self._progress_bar.pack(pady=10)
        self._progress_bar.set(0)
        
        self._progress_detail = ctk.CTkLabel(self._progress_window, text=f"0 / {total_files}")
        self._progress_detail.pack(pady=5)
        
        # Store params for thread
        self._gen_params = {
            'output': output,
            'count': count,
            'style_count': style_count,
            'start_number': start_number,
            'total_files': total_files
        }
        
        # Start generation thread
        self._gen_thread = threading.Thread(target=self._generate_thread, daemon=True)
        self._gen_thread.start()
        
        # Start polling for completion
        self._poll_generation()
    
    def _generate_thread(self):
        params = self._gen_params
        self._gen_error = None
        self._gen_current = 0
        
        try:
            gen = HairPaletteGenerator([x[:3] for x in self.project_state.palette])
            gen.generate_hair_palettes(
                output_dir=params['output'],
                style_count=params['style_count'],
                count=params['count'],
                groups=self.project_state.groups,
                start_number=params['start_number'],
                random_saturation=self.chk_rand_sat.get() == 1,
                random_brightness=self.chk_rand_bri.get() == 1,
                progress_callback=self._update_gen_progress
            )
        except Exception as e:
            self._gen_error = str(e)
    
    def _update_gen_progress(self, current, total):
        self._gen_current = current
        self._gen_total = total
    
    def _poll_generation(self):
        if hasattr(self, '_gen_current') and hasattr(self, '_gen_total'):
            progress = self._gen_current / max(self._gen_total, 1)
            self._progress_bar.set(progress)
            self._progress_label.configure(text=f"Gerando paleta {self._gen_current}...")
            self._progress_detail.configure(text=f"{self._gen_current} / {self._gen_total}")
        
        if self._gen_thread.is_alive():
            self.after(50, self._poll_generation)
        else:
            self._finish_generation()
    
    def _finish_generation(self):
        params = self._gen_params
        
        # Close progress window
        self._progress_window.destroy()
        
        # Re-enable button
        self.btn_generate.configure(state="normal")
        
        if self._gen_error:
            messagebox.showerror("Erro", self._gen_error)
        else:
            messagebox.showinfo(
                "Sucesso",
                f"Gerados {params['total_files']} arquivos de paleta de cabelo!\n\n"
                f"Formato: ¸Ó¸®{params['style_count']}_{{gênero}}_{{número}}.pal"
            )
            os.startfile(params['output'])
        
        # Cleanup
        del self._gen_params
        del self._gen_thread
        del self._gen_current
        del self._gen_total
        del self._gen_error
