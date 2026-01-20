import customtkinter as ctk

class GroupManagementFrame(ctk.CTkFrame):
    def __init__(self, master, add_group_cmd=None, remove_group_cmd=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        self.lbl_title = ctk.CTkLabel(self, text="Grupos de Cores", font=("Roboto", 14, "bold"))
        self.lbl_title.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Buttons Frame
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=1, column=0, padx=5, pady=0, sticky="ew")
        
        self.btn_add = ctk.CTkButton(self.btn_frame, text="Adicionar", command=add_group_cmd, width=100)
        self.btn_add.pack(side="left", padx=2)
        
        self.btn_remove = ctk.CTkButton(self.btn_frame, text="Remover Grupo", command=remove_group_cmd, fg_color="#FF5555", hover_color="#CC0000", width=80)
        self.btn_remove.pack(side="left", padx=2)
        
        self.btn_clear = ctk.CTkButton(self.btn_frame, text="Limpar Seleção", command=self._on_clear_click, 
                                        fg_color="#666666", hover_color="#888888", width=70)
        self.btn_clear.pack(side="left", padx=2)
        
        # Group List (Scrollable)
        self.scroll_frame = ctk.CTkScrollableFrame(self, height=100)
        self.scroll_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        
        # Bind click on the internal frame of CTkScrollableFrame to deselect
        # CTkScrollableFrame has internal _parent_frame that receives clicks
        self.scroll_frame._parent_frame.bind("<Button-1>", self._on_empty_click)
        # Also bind to the scrollable frame itself
        self.scroll_frame.bind("<Button-1>", self._on_empty_click)
        
        self.group_buttons = {}
        self.selected_group = None
        self.on_group_select = None
        self.on_deselect = None  # Callback for deselecting

    def update_groups(self, groups, selected_group=None):
        # Clear existing
        for btn in self.group_buttons.values():
            btn.destroy()
        self.group_buttons.clear()
        
        self.selected_group = selected_group
        
        for group in groups:
            fg_color = "transparent"
            if group == selected_group:
                fg_color = ("#3B8ED0", "#1F6AA5") # Theme active color for button
                
            btn = ctk.CTkButton(
                self.scroll_frame, 
                text=group.name, 
                fg_color=fg_color,
                anchor="w",
                command=lambda g=group: self._on_click(g)
            )
            btn.pack(fill="x", pady=2)
            self.group_buttons[group.name] = btn
            
    def _on_click(self, group):
        if self.on_group_select:
            self.on_group_select(group)
    
    def _on_empty_click(self, event):
        """Handle click on empty area - deselect current group"""
        if self.on_deselect:
            self.on_deselect()
    
    def _on_clear_click(self):
        """Handle clear button click - deselect current group"""
        if self.on_deselect:
            self.on_deselect()


from src.ui.icons import IconManager

class GradientEditor(ctk.CTkFrame):
    """A widget for editing a gradient - define first and last color, auto-interpolate middle colors"""
    
    # Presets de tons de pele
    SKIN_PRESETS = {
        "Personalizado": None,
        "Moreno Médio": ((224, 184, 138), (90, 47, 27)),      # #E0B88A → #5A2F1B
        "Moreno Escuro": ((211, 160, 108), (63, 31, 18)),     # #D3A06C → #3F1F12
        "Negro": ((192, 138, 90), (26, 11, 6)),               # #C08A5A → #1A0B06
    }
    
    def __init__(self, master, on_change_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.icon_manager = IconManager()
        
        self.on_change_callback = on_change_callback
        self.first_color = (255, 200, 150)  # Light color
        self.last_color = (80, 30, 10)      # Dark color
        
        # Title
        self.lbl_title = ctk.CTkLabel(
            self,
            text="Degradê Fixo:",
            image=self.icon_manager.get_icon("art", size=(16, 16)),
            compound="left",
            font=("Roboto", 11, "bold")
        )
        self.lbl_title.pack(anchor="w", padx=5, pady=(5, 2))
        
        # Presets frame
        self.presets_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.presets_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        self.lbl_preset = ctk.CTkLabel(self.presets_frame, text="Predefinição:")
        self.lbl_preset.pack(side="left", padx=(0, 5))
        
        self.preset_dropdown = ctk.CTkOptionMenu(
            self.presets_frame,
            values=list(self.SKIN_PRESETS.keys()),
            command=self._on_preset_change,
            width=140
        )
        self.preset_dropdown.set("Personalizado")
        self.preset_dropdown.pack(side="left", padx=5)
        
        # Color picker frame
        self.picker_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.picker_frame.pack(fill="x", padx=5, pady=5)
        
        # First color
        self.lbl_first = ctk.CTkLabel(self.picker_frame, text="Primeira:")
        self.lbl_first.pack(side="left", padx=(0, 5))
        
        self.btn_first = ctk.CTkButton(
            self.picker_frame,
            text="",
            width=40,
            height=30,
            fg_color=self._rgb_to_hex(self.first_color),
            hover_color=self._rgb_to_hex(self.first_color),
            command=self._pick_first_color
        )
        self.btn_first.pack(side="left", padx=5)
        
        # Last color
        self.lbl_last = ctk.CTkLabel(self.picker_frame, text="Última:")
        self.lbl_last.pack(side="left", padx=(15, 5))
        
        self.btn_last = ctk.CTkButton(
            self.picker_frame,
            text="",
            width=40,
            height=30,
            fg_color=self._rgb_to_hex(self.last_color),
            hover_color=self._rgb_to_hex(self.last_color),
            command=self._pick_last_color
        )
        self.btn_last.pack(side="left", padx=5)
        
        # Preview frame - show the 8 interpolated colors
        self.lbl_preview = ctk.CTkLabel(self, text="Prévia do Degradê:", font=("Roboto", 10))
        self.lbl_preview.pack(anchor="w", padx=5, pady=(5, 2))
        
        self.preview_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.preview_frame.pack(fill="x", padx=5, pady=5)
        
        self.preview_labels = []
        for i in range(8):
            lbl = ctk.CTkLabel(
                self.preview_frame,
                text="",
                width=35,
                height=25,
                corner_radius=4
            )
            lbl.pack(side="left", padx=1)
            self.preview_labels.append(lbl)
        
        # Update preview
        self._update_preview()
    
    def _rgb_to_hex(self, rgb):
        r, g, b = rgb
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _clamp(self, value):
        return max(0, min(255, int(value)))
    
    def _interpolate_gradient(self):
        """Generate 8 colors by interpolating between first and last color"""
        colors = []
        for i in range(8):
            r = self._clamp((self.last_color[0] - self.first_color[0]) / 7 * i + self.first_color[0])
            g = self._clamp((self.last_color[1] - self.first_color[1]) / 7 * i + self.first_color[1])
            b = self._clamp((self.last_color[2] - self.first_color[2]) / 7 * i + self.first_color[2])
            colors.append((r, g, b))
        return colors
    
    def _update_preview(self):
        """Update the preview labels with interpolated colors"""
        colors = self._interpolate_gradient()
        for i, color in enumerate(colors):
            hex_color = self._rgb_to_hex(color)
            self.preview_labels[i].configure(fg_color=hex_color)
    
    def _on_preset_change(self, preset_name):
        """Handle preset selection change"""
        if preset_name == "Personalizado":
            return
        
        preset = self.SKIN_PRESETS.get(preset_name)
        if preset:
            self.first_color = preset[0]
            self.last_color = preset[1]
            self.btn_first.configure(
                fg_color=self._rgb_to_hex(self.first_color),
                hover_color=self._rgb_to_hex(self.first_color)
            )
            self.btn_last.configure(
                fg_color=self._rgb_to_hex(self.last_color),
                hover_color=self._rgb_to_hex(self.last_color)
            )
            self._update_preview()
            if self.on_change_callback:
                self.on_change_callback()
    
    def _pick_first_color(self):
        from src.ui.color_picker import ColorPickerDialog
        color = ColorPickerDialog.ask_color(self.winfo_toplevel(), self.first_color, "Primeira Cor do Degradê")
        if color:
            self.first_color = color
            hex_color = self._rgb_to_hex(color)
            self.btn_first.configure(fg_color=hex_color, hover_color=hex_color)
            self.preset_dropdown.set("Personalizado")  # Reset preset when manually changed
            self._update_preview()
            if self.on_change_callback:
                self.on_change_callback()
    
    def _pick_last_color(self):
        from src.ui.color_picker import ColorPickerDialog
        color = ColorPickerDialog.ask_color(self.winfo_toplevel(), self.last_color, "Última Cor do Degradê")
        if color:
            self.last_color = color
            hex_color = self._rgb_to_hex(color)
            self.btn_last.configure(fg_color=hex_color, hover_color=hex_color)
            self.preset_dropdown.set("Personalizado")  # Reset preset when manually changed
            self._update_preview()
            if self.on_change_callback:
                self.on_change_callback()
    
    def set_gradient(self, colors):
        """Set the gradient from a list of 8 RGB tuples (uses first and last)"""
        if colors and len(colors) >= 2:
            self.first_color = colors[0]
            self.last_color = colors[-1]
            self.btn_first.configure(
                fg_color=self._rgb_to_hex(self.first_color), 
                hover_color=self._rgb_to_hex(self.first_color)
            )
            self.btn_last.configure(
                fg_color=self._rgb_to_hex(self.last_color), 
                hover_color=self._rgb_to_hex(self.last_color)
            )
            self._update_preview()
    
    def get_gradient(self):
        """Get the 8 interpolated colors"""
        return self._interpolate_gradient()


class GroupSettingsFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.icon_manager = IconManager()
        
        self.current_group = None
        self.on_change_callback = None
        
        self.lbl_title = ctk.CTkLabel(self, text="Configurações do Grupo", font=("Roboto", 16, "bold"))
        self.lbl_title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        
        # Name
        self.entry_name = ctk.CTkEntry(self, placeholder_text="Nome do Grupo")
        self.entry_name.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.entry_name.bind("<FocusOut>", self._update_name)
        
        # Mode Switch
        self.switch_mode = ctk.CTkSwitch(self, text="Modo Colorir (para branco/cinza)", command=self._on_mode_change)
        self.switch_mode.grid(row=2, column=0, columnspan=2, padx=10, pady=(10,0), sticky="w")
        
        # --- Fixed Color Checkbox ---
        self.checkbox_fixed = ctk.CTkCheckBox(self, text="🔒 Cor Fixa (Manual)", command=self._on_fixed_change)
        self.checkbox_fixed.grid(row=3, column=0, columnspan=2, padx=10, pady=(10,0), sticky="w")
        
        # Gradient Editor (8 colors)
        self.gradient_editor = GradientEditor(self, on_change_callback=self._on_gradient_change)
        self.gradient_editor.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Preview Hue (visualization only)
        self.lbl_hue_preview = ctk.CTkLabel(
            self,
            text="Cor (Visualização):",
            image=self.icon_manager.get_icon("art", size=(16, 16)),
            compound="left"
        )
        self.lbl_hue_preview.grid(row=5, column=0, columnspan=2, padx=10, pady=(10,0), sticky="w")
        
        self.slider_h_start = ctk.CTkSlider(self, from_=0.0, to=1.0)
        self.slider_h_start.grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
        # Hue Range for Generation - Color Pickers
        self.lbl_hue_range = ctk.CTkLabel(
            self,
            text="Faixa de Cores (Geração):",
            image=self.icon_manager.get_icon("rainbow", size=(16, 16)),
            compound="left",
            font=("Roboto", 11, "bold")
        )
        self.lbl_hue_range.grid(row=7, column=0, columnspan=2, padx=10, pady=(15,0), sticky="w")
        
        self.frame_hue_range = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_hue_range.grid(row=8, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
        # Start Color
        self.lbl_hue_start = ctk.CTkLabel(self.frame_hue_range, text="De:")
        self.lbl_hue_start.pack(side="left", padx=(0, 5))
        
        self.color_start = "#FF0000"  # Default red
        self.btn_color_start = ctk.CTkButton(
            self.frame_hue_range, 
            text="", 
            width=40, 
            height=25,
            fg_color=self.color_start,
            hover_color=self.color_start,
            command=self._pick_color_start
        )
        self.btn_color_start.pack(side="left", padx=5)
        
        # End Color
        self.lbl_hue_end = ctk.CTkLabel(self.frame_hue_range, text="Até:")
        self.lbl_hue_end.pack(side="left", padx=(15, 5))
        
        self.color_end = "#FF0000"  # Default red (full spectrum when same)
        self.btn_color_end = ctk.CTkButton(
            self.frame_hue_range, 
            text="", 
            width=40, 
            height=25,
            fg_color=self.color_end,
            hover_color=self.color_end,
            command=self._pick_color_end
        )
        self.btn_color_end.pack(side="left", padx=5)
        
        # Info label
        self.lbl_hue_info = ctk.CTkLabel(self, text="(Cores iguais = espectro completo)", 
                                          text_color="gray", font=("Roboto", 10))
        self.lbl_hue_info.grid(row=9, column=0, columnspan=2, padx=10, pady=0, sticky="w")
        
        # Sat
        self.lbl_sat = ctk.CTkLabel(
            self,
            text="Saturação:",
            image=self.icon_manager.get_icon("water", size=(16, 16)),
            compound="left"
        )
        self.lbl_sat.grid(row=10, column=0, padx=10, pady=(10,0), sticky="w")
        self.slider_sat = ctk.CTkSlider(self, from_=-1.0, to=1.0)
        self.slider_sat.grid(row=11, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
        # Val
        self.lbl_val = ctk.CTkLabel(
            self,
            text="Brilho:",
            image=self.icon_manager.get_icon("sun", size=(16, 16)),
            compound="left"
        )
        self.lbl_val.grid(row=12, column=0, padx=10, pady=0, sticky="w")
        self.slider_val = ctk.CTkSlider(self, from_=-1.0, to=1.0)
        self.slider_val.grid(row=13, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        # Events
        self.slider_h_start.configure(command=self._on_change)
        self.slider_sat.configure(command=self._on_change)
        self.slider_val.configure(command=self._on_change)

    def _rgb_to_hue(self, hex_color):
        """Convert hex color to hue in degrees (0-360)"""
        import colorsys
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        return h * 360
    
    def _hue_to_rgb(self, hue_degrees):
        """Convert hue (0-360) to hex color"""
        import colorsys
        h = (hue_degrees % 360) / 360.0
        r, g, b = colorsys.hsv_to_rgb(h, 1.0, 1.0)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _pick_color_start(self):
        from src.ui.color_picker import ColorPickerDialog
        current_rgb = self._hex_to_rgb(self.color_start) if isinstance(self.color_start, str) else (255, 0, 0)
        color = ColorPickerDialog.ask_color(self.winfo_toplevel(), current_rgb, "Escolha a Cor Inicial")
        if color:
            hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
            self.color_start = hex_color
            self.btn_color_start.configure(fg_color=self.color_start, hover_color=self.color_start)
            if self.current_group:
                self.current_group.hue_range_start = self._rgb_to_hue(self.color_start)
    
    def _pick_color_end(self):
        from src.ui.color_picker import ColorPickerDialog
        current_rgb = self._hex_to_rgb(self.color_end) if isinstance(self.color_end, str) else (255, 0, 0)
        color = ColorPickerDialog.ask_color(self.winfo_toplevel(), current_rgb, "Escolha a Cor Final")
        if color:
            hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
            self.color_end = hex_color
            self.btn_color_end.configure(fg_color=self.color_end, hover_color=self.color_end)
            if self.current_group:
                self.current_group.hue_range_end = self._rgb_to_hue(self.color_end)

    def _on_gradient_change(self):
        """Handle gradient color change"""
        if self.current_group:
            self.current_group.fixed_gradient = self.gradient_editor.get_gradient()
            if self.on_change_callback:
                self.on_change_callback()

    def _on_fixed_change(self):
        """Handle fixed color checkbox toggle"""
        if self.current_group:
            self.current_group.is_fixed = self.checkbox_fixed.get() == 1
            self._update_fixed_state()
            if self.on_change_callback:
                self.on_change_callback()

    def _update_fixed_state(self):
        """Enable/disable controls based on is_fixed state"""
        is_fixed = self.checkbox_fixed.get() == 1
        state = "disabled" if is_fixed else "normal"
        
        # Disable hue range controls when fixed
        self.btn_color_start.configure(state=state)
        self.btn_color_end.configure(state=state)
        
        # Show/hide gradient editor based on state
        if is_fixed:
            self.gradient_editor.grid()
        else:
            self.gradient_editor.grid_remove()

    def load_group(self, group):
        self.current_group = group
        if not group:
            self.entry_name.delete(0, "end")
            self.switch_mode.deselect()
            self.checkbox_fixed.deselect()
            self.slider_h_start.set(0)
            self.color_start = "#FF0000"
            self.color_end = "#FF0000"
            self.btn_color_start.configure(fg_color=self.color_start, hover_color=self.color_start)
            self.btn_color_end.configure(fg_color=self.color_end, hover_color=self.color_end)
            self.slider_sat.set(0)
            self.slider_val.set(0)
            self._update_labels()
            self._update_fixed_state()
            # Disable all controls when no group
            self._set_all_controls_state("disabled")
            return
            
        # Enable controls
        self._set_all_controls_state("normal")
        
        self.entry_name.delete(0, "end")
        self.entry_name.insert(0, group.name)
        
        if group.mode == "colorize":
            self.switch_mode.select()
        else:
            self.switch_mode.deselect()
        
        # Load is_fixed state
        if getattr(group, 'is_fixed', False):
            self.checkbox_fixed.select()
        else:
            self.checkbox_fixed.deselect()
            
        self.slider_h_start.set(group.hue_shift_start)
        
        # Load color range from group
        hue_start = getattr(group, 'hue_range_start', 0)
        hue_end = getattr(group, 'hue_range_end', 360)
        self.color_start = self._hue_to_rgb(hue_start)
        self.color_end = self._hue_to_rgb(hue_end)
        self.btn_color_start.configure(fg_color=self.color_start, hover_color=self.color_start)
        self.btn_color_end.configure(fg_color=self.color_end, hover_color=self.color_end)
        
        # Load fixed gradient
        gradient = getattr(group, 'fixed_gradient', None)
        if gradient:
            self.gradient_editor.set_gradient(gradient)
        
        self.slider_sat.set(group.sat_shift)
        self.slider_val.set(group.val_shift)
        self._update_labels()
        self._update_fixed_state()

    def _set_all_controls_state(self, state):
        """Enable or disable all controls"""
        self.entry_name.configure(state=state)
        self.switch_mode.configure(state=state)
        self.checkbox_fixed.configure(state=state)
        self.slider_h_start.configure(state=state)
        self.slider_sat.configure(state=state)
        self.slider_val.configure(state=state)
        self.btn_color_start.configure(state=state)
        self.btn_color_end.configure(state=state)
        
    def _update_labels(self):
        # Change labels based on mode
        is_colorize = self.switch_mode.get() == 1
        if is_colorize:
            self.lbl_hue_preview.configure(text="Cor Alvo (Visualização):")
            self.lbl_sat.configure(text="Saturação Alvo:")
            self.slider_sat.configure(from_=0.0, to=1.0)
        else:
            self.lbl_hue_preview.configure(text="Cor (Visualização):")
            self.lbl_sat.configure(text="Saturação:")
            self.slider_sat.configure(from_=-1.0, to=1.0)
            
    def _update_name(self, event):
        if self.current_group:
            self.current_group.name = self.entry_name.get()
    
    def _on_mode_change(self):
        if self.current_group:
            self.current_group.mode = "colorize" if self.switch_mode.get() == 1 else "hsv"
            self._update_labels()
            if self.on_change_callback:
                self.on_change_callback()
            
    def _on_change(self, value):
        if self.current_group:
            self.current_group.hue_shift_start = self.slider_h_start.get()
            self.current_group.sat_shift = self.slider_sat.get()
            self.current_group.val_shift = self.slider_val.get()
            if self.on_change_callback:
                self.on_change_callback()

