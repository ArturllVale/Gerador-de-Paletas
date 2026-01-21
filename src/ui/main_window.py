import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import glob
import colorsys
import threading

from src.core.parsers.spr import SprParser
from src.core.parsers.act import ActParser
from src.core.logic.state import ProjectState
from src.core.generator import PaletteGenerator
from src.core.pal_handler import PaletteHandler
from src.core.color_math import apply_adjustments, apply_colorize

from src.ui.visualizer import PaletteVisualizer
from src.ui.components_v2 import GroupManagementFrame, GroupSettingsFrame
from src.ui.preview import SpritePreview
from src.ui.preview_window import PreviewWindow
from src.ui.class_selector import ClassSelectorWindow
from src.ui.icons import IconManager

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.icon_manager = IconManager()

        self.title("RO Palette Generator")
        self.geometry("1300x920")
        
        # Logic State
        self.project_state = ProjectState()
        self.current_spr = None
        self.current_active_group = None
        self.current_filename = "palette"
        
        # Layout: Row 0 = Top Menu, Row 1 = 3 columns
        self.grid_rowconfigure(1, weight=1)
        
        # Frame index for preview
        self.current_frame_index = 0
        self.is_playing = False
        self._preview_pending = None  # For throttled preview updates
        
        # --- Top Menu ---
        self.top_frame = ctk.CTkFrame(self, height=40)
        self.top_frame.grid(row=0, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        
        self.btn_load_spr = ctk.CTkButton(self.top_frame, text="Carregar SPR", command=self.load_spr)
        self.btn_load_spr.pack(side="left", padx=5, pady=5)
        
        self.btn_preview_mode = ctk.CTkButton(
            self.top_frame, 
            text="Modo Preview",
            image=self.icon_manager.get_icon("preview"),
            compound="left",
            command=self.enter_preview_mode,
            fg_color="#E07A5F",  # Orange
            hover_color="#C0583D"
        )
        self.btn_preview_mode.pack(side="left", padx=5, pady=5)
        
        # --- Theme Toggle ---
        # Default icon based on current mode (assuming Dark default if System)
        current_mode = ctk.get_appearance_mode()
        theme_icon_name = "theme_light" if current_mode == "Light" else "theme_dark"
        self.btn_theme = ctk.CTkButton(
            self.top_frame,
            text="",
            image=self.icon_manager.get_icon(theme_icon_name),
            width=40,
            command=self.toggle_theme
        )
        self.btn_theme.pack(side="right", padx=5, pady=5)

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
        
        # Store selected classes
        self.selected_classes = set()
        
        self.btn_generate = ctk.CTkButton(
            self.frame_gen_controls, 
            text="Gerar Paletas",
            image=self.icon_manager.get_icon("generate"),
            compound="left",
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
        
        # --- Main Content: 4 columns ---
        # Column 0: Groups + Visualizer (compact)
        # Column 1: Settings (compact)
        # Column 2: Classes (compact)
        # Column 3: Preview (expands)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=0)
        self.grid_columnconfigure(3, weight=1)
        
        # --- Column 0: Groups & Visualizer ---
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
        
        # Visualizer
        self.lbl_vis = ctk.CTkLabel(self.left_col, text="Visualizador de Paleta (Selecione cores → Criar Grupo)", font=("Roboto", 12, "bold"))
        self.lbl_vis.grid(row=1, column=0, sticky="w", padx=5)
        
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
        
        # Connect hover to preview highlight
        self.visualizer.on_hover_callback = self._on_palette_hover
        
        # --- Column 1: Settings ---
        self.mid_col = ctk.CTkFrame(self, fg_color="transparent")
        self.mid_col.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        self.settings_panel = GroupSettingsFrame(self.mid_col)
        self.settings_panel.pack(fill="both", expand=True)
        self.settings_panel.on_change_callback = self._update_preview
        
        # --- Column 2: Class Selector (embedded) ---
        self.class_col = ctk.CTkFrame(self)
        self.class_col.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)
        
        self.lbl_classes = ctk.CTkLabel(self.class_col, text="Selecione as classes", font=("Roboto", 12, "bold"))
        self.lbl_classes.pack(pady=5)
        
        # Buttons
        self.class_btn_frame = ctk.CTkFrame(self.class_col, fg_color="transparent")
        self.class_btn_frame.pack(fill="x", padx=5)
        ctk.CTkButton(self.class_btn_frame, text="Todos", width=60, command=self._select_all_classes).pack(side="left", padx=2)
        ctk.CTkButton(self.class_btn_frame, text="Limpar", width=60, command=self._clear_classes).pack(side="left", padx=2)
        
        # Scrollable checkboxes
        from src.ui.class_selector import RO_CLASSES
        self.class_scroll = ctk.CTkScrollableFrame(self.class_col, width=200, height=400)
        self.class_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.class_checkboxes = {}
        for internal_name, display_name in RO_CLASSES:
            var = ctk.BooleanVar(value=False)
            cb = ctk.CTkCheckBox(
                self.class_scroll,
                text=display_name,
                variable=var,
                command=lambda n=internal_name, v=var: self._on_class_toggle(n, v)
            )
            cb.pack(anchor="w", pady=1)
            self.class_checkboxes[internal_name] = (cb, var)
        
        # --- Column 3: Preview ---
        self.right_col = ctk.CTkFrame(self, fg_color="transparent")
        self.right_col.grid(row=1, column=3, sticky="nsew", padx=5, pady=5)
        self.right_col.grid_rowconfigure(1, weight=1)
        
        # Preview
        self.lbl_prev = ctk.CTkLabel(self.right_col, text="Prévia (Clique no sprite para selecionar cor)", font=("Roboto", 12, "bold"))
        self.lbl_prev.grid(row=0, column=0, sticky="nw", padx=5)
        
        self.preview = SpritePreview(self.right_col)
        self.preview.grid(row=1, column=0, sticky="nsew")
        self.preview.on_pixel_click = self._on_preview_click
        
        # Frame navigation controls
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
        
        self.btn_play = ctk.CTkButton(
            self.frame_nav,
            text="Play",
            image=self.icon_manager.get_icon("play"),
            compound="left",
            width=60,
            command=self._toggle_play,
            fg_color="#2CC985",
            hover_color="#229965"
        )
        self.btn_play.pack(side="left", padx=10)
    
    def _on_class_toggle(self, name, var):
        if var.get():
            self.selected_classes.add(name)
        else:
            self.selected_classes.discard(name)
    
    def _on_palette_hover(self, palette_index):
        """Highlight all selected pixels in preview when hovering over palette."""
        if palette_index is not None and self.visualizer.selected_indices:
            self.preview.highlight_pixels(self.visualizer.selected_indices)
        else:
            self.preview.highlight_pixels(None)
    
    def _select_all_classes(self):
        for internal_name, (cb, var) in self.class_checkboxes.items():
            var.set(True)
            self.selected_classes.add(internal_name)
    
    def _clear_classes(self):
        for internal_name, (cb, var) in self.class_checkboxes.items():
            var.set(False)
        self.selected_classes.clear()

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
        """Throttled preview update - coalesces rapid calls"""
        if self._preview_pending:
            self.after_cancel(self._preview_pending)
        self._preview_pending = self.after(16, self._do_update_preview)
    
    def _do_update_preview(self):
        """Actual preview update logic"""
        self._preview_pending = None
        
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
        
        # Get selected classes - always include base_filename, plus selected classes
        class_names = [self.current_filename]
        if self.selected_classes:
            class_names.extend(list(self.selected_classes))
        
        # Disable button during generation
        self.btn_generate.configure(state="disabled")
        
        # Create progress window
        self._progress_window = ctk.CTkToplevel(self)
        self._progress_window.title("Gerando Paletas...")
        self._progress_window.geometry("400x120")
        self._progress_window.transient(self)
        self._progress_window.grab_set()
        
        self._progress_label = ctk.CTkLabel(self._progress_window, text="Iniciando...")
        self._progress_label.pack(pady=10)
        
        num_names = len(class_names) if class_names else 1
        total_files = count * num_names * 2
        
        self._progress_bar = ctk.CTkProgressBar(self._progress_window, width=350)
        self._progress_bar.pack(pady=10)
        self._progress_bar.set(0)
        
        self._progress_detail = ctk.CTkLabel(self._progress_window, text=f"0 / {total_files}")
        self._progress_detail.pack(pady=5)
        
        # Store params for thread
        self._gen_params = {
            'output': output,
            'count': count,
            'class_names': class_names,
            'start_number': start_number,
            'total_files': total_files
        }
        
        # Start generation thread
        self._gen_thread = threading.Thread(target=self._generate_thread, daemon=True)
        self._gen_thread.start()
        
        # Start polling for completion
        self._poll_generation()
    
    def _generate_thread(self):
        """Worker thread for palette generation."""
        params = self._gen_params
        self._gen_error = None
        self._gen_current = 0
        
        try:
            gen = PaletteGenerator([x[:3] for x in self.project_state.palette])
            gen.generate_batch_with_progress(
                output_dir=params['output'],
                base_filename=self.current_filename,
                count=params['count'],
                groups=self.project_state.groups,
                start_number=params['start_number'],
                class_names=params['class_names'],
                random_saturation=self.chk_rand_sat.get() == 1,
                random_brightness=self.chk_rand_bri.get() == 1,
                progress_callback=self._update_gen_progress
            )
        except Exception as e:
            self._gen_error = str(e)
    
    def _update_gen_progress(self, current, total):
        """Callback from generator thread to update progress."""
        self._gen_current = current
        self._gen_total = total
    
    def _poll_generation(self):
        """Poll generation thread and update UI."""
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
        """Called when generation thread finishes."""
        params = self._gen_params
        
        # Close progress window
        self._progress_window.destroy()
        
        # Re-enable button
        self.btn_generate.configure(state="normal")
        
        if self._gen_error:
            messagebox.showerror("Erro", self._gen_error)
        else:
            messagebox.showinfo("Sucesso", f"Gerados {params['total_files']} arquivos ({params['count']} variações)!")
            os.startfile(params['output'])
        
        # Cleanup
        del self._gen_params
        del self._gen_thread
        del self._gen_current
        del self._gen_total
        del self._gen_error

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
            self.btn_play.configure(
                text="Pause",
                image=self.icon_manager.get_icon("pause"),
                fg_color="#FF5555",
                hover_color="#CC0000"
            )
            self._animate_loop()
        else:
            self.btn_play.configure(
                text="Play",
                image=self.icon_manager.get_icon("play"),
                fg_color="#2CC985",
                hover_color="#229965"
            )
    
    def _animate_loop(self):
        if self.is_playing:
            self._next_frame()
            # 150ms delay for animation
            self.after(150, self._animate_loop)

    def enter_preview_mode(self):
        """Open preview mode window"""
        PreviewWindow(self)

    def toggle_theme(self):
        """Switch between Light and Dark mode"""
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            ctk.set_appearance_mode("Light")
            self.btn_theme.configure(image=self.icon_manager.get_icon("theme_light"))
        else:
            ctk.set_appearance_mode("Dark")
            self.btn_theme.configure(image=self.icon_manager.get_icon("theme_dark"))
