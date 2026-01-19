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
        
        self.btn_remove = ctk.CTkButton(self.btn_frame, text="Remover", command=remove_group_cmd, fg_color="#FF5555", hover_color="#CC0000", width=80)
        self.btn_remove.pack(side="left", padx=2)
        
        # Group List (Scrollable)
        self.scroll_frame = ctk.CTkScrollableFrame(self, height=100)
        self.scroll_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        
        self.group_buttons = {}
        self.selected_group = None
        self.on_group_select = None

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

class GroupSettingsFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
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
        
        # Preview Hue (visualization only)
        self.lbl_hue_preview = ctk.CTkLabel(self, text="🎨 Cor (Visualização):")
        self.lbl_hue_preview.grid(row=3, column=0, columnspan=2, padx=10, pady=(10,0), sticky="w")
        
        self.slider_h_start = ctk.CTkSlider(self, from_=0.0, to=1.0)
        self.slider_h_start.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
        # Hue Range for Generation - Color Pickers
        self.lbl_hue_range = ctk.CTkLabel(self, text="🌈 Faixa de Cores (Geração):", font=("Roboto", 11, "bold"))
        self.lbl_hue_range.grid(row=5, column=0, columnspan=2, padx=10, pady=(15,0), sticky="w")
        
        self.frame_hue_range = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_hue_range.grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
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
        self.lbl_hue_info.grid(row=7, column=0, columnspan=2, padx=10, pady=0, sticky="w")
        
        # Sat
        self.lbl_sat = ctk.CTkLabel(self, text="💧 Saturação:")
        self.lbl_sat.grid(row=8, column=0, padx=10, pady=(10,0), sticky="w")
        self.slider_sat = ctk.CTkSlider(self, from_=-1.0, to=1.0)
        self.slider_sat.grid(row=9, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
        # Val
        self.lbl_val = ctk.CTkLabel(self, text="☀️ Brilho:")
        self.lbl_val.grid(row=10, column=0, padx=10, pady=0, sticky="w")
        self.slider_val = ctk.CTkSlider(self, from_=-1.0, to=1.0)
        self.slider_val.grid(row=11, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        # --- Generation Settings ---
        self.frame_gen = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_gen.grid(row=12, column=0, columnspan=2, padx=10, pady=(20, 10), sticky="ew")
        
        self.lbl_count = ctk.CTkLabel(self.frame_gen, text="Quantidade:")
        self.lbl_count.pack(side="left", padx=5)
        
        self.entry_count = ctk.CTkEntry(self.frame_gen, width=50)
        self.entry_count.insert(0, "10")
        self.entry_count.pack(side="left", padx=5)
        
        self.btn_gen_group = ctk.CTkButton(self.frame_gen, text="Gerar Paletas", fg_color="#E07A5F", hover_color="#C0583D")
        self.btn_gen_group.pack(side="right", padx=5, fill="x", expand=True)

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

    def _pick_color_start(self):
        from tkinter import colorchooser
        color = colorchooser.askcolor(title="Escolha a Cor Inicial", color=self.color_start)
        if color[1]:
            self.color_start = color[1]
            self.btn_color_start.configure(fg_color=self.color_start, hover_color=self.color_start)
            if self.current_group:
                self.current_group.hue_range_start = self._rgb_to_hue(self.color_start)
    
    def _pick_color_end(self):
        from tkinter import colorchooser
        color = colorchooser.askcolor(title="Escolha a Cor Final", color=self.color_end)
        if color[1]:
            self.color_end = color[1]
            self.btn_color_end.configure(fg_color=self.color_end, hover_color=self.color_end)
            if self.current_group:
                self.current_group.hue_range_end = self._rgb_to_hue(self.color_end)

    def load_group(self, group):
        self.current_group = group
        if not group:
            self.entry_name.delete(0, "end")
            self.switch_mode.deselect()
            self.slider_h_start.set(0)
            self.color_start = "#FF0000"
            self.color_end = "#FF0000"
            self.btn_color_start.configure(fg_color=self.color_start, hover_color=self.color_start)
            self.btn_color_end.configure(fg_color=self.color_end, hover_color=self.color_end)
            self.slider_sat.set(0)
            self.slider_val.set(0)
            self.btn_gen_group.configure(state="disabled")
            self._update_labels()
            return
            
        self.entry_name.delete(0, "end")
        self.entry_name.insert(0, group.name)
        
        if group.mode == "colorize":
            self.switch_mode.select()
        else:
            self.switch_mode.deselect()
            
        self.slider_h_start.set(group.hue_shift_start)
        
        # Load color range from group
        hue_start = getattr(group, 'hue_range_start', 0)
        hue_end = getattr(group, 'hue_range_end', 360)
        self.color_start = self._hue_to_rgb(hue_start)
        self.color_end = self._hue_to_rgb(hue_end)
        self.btn_color_start.configure(fg_color=self.color_start, hover_color=self.color_start)
        self.btn_color_end.configure(fg_color=self.color_end, hover_color=self.color_end)
        
        self.slider_sat.set(group.sat_shift)
        self.slider_val.set(group.val_shift)
        self.btn_gen_group.configure(state="normal")
        self._update_labels()
        
    def _update_labels(self):
        # Change labels based on mode
        is_colorize = self.switch_mode.get() == 1
        if is_colorize:
            self.lbl_hue_preview.configure(text="🎨 Cor Alvo (Visualização):")
            self.lbl_sat.configure(text="💧 Saturação Alvo:")
            self.slider_sat.configure(from_=0.0, to=1.0)
        else:
            self.lbl_hue_preview.configure(text="🎨 Cor (Visualização):")
            self.lbl_sat.configure(text="💧 Saturação:")
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

