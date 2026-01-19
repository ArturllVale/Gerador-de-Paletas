import customtkinter as ctk

class SelectionControlFrame(ctk.CTkFrame):
    def __init__(self, master, select_all_command=None, clear_command=None, invert_command=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.btn_all = ctk.CTkButton(self, text="Select All", command=select_all_command, height=25)
        self.btn_all.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.btn_clear = ctk.CTkButton(self, text="Clear", command=clear_command, fg_color="transparent", border_width=1, height=25)
        self.btn_clear.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Invert can be added if needed, kept simple for now
        
class BatchControlFrame(ctk.CTkFrame):
    def __init__(self, master, generate_command=None, **kwargs):
        super().__init__(master, **kwargs)
        
        # Title
        self.label_title = ctk.CTkLabel(self, text="Batch Generator Settings", font=("Roboto", 16, "bold"))
        self.label_title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 20), sticky="w")
        
        # Count
        self.label_count = ctk.CTkLabel(self, text="Variations Count:")
        self.label_count.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.count_var = ctk.IntVar(value=10)
        self.entry_count = ctk.CTkEntry(self, textvariable=self.count_var, width=60)
        self.entry_count.grid(row=1, column=1, padx=10, pady=5, sticky="e")
        
        # Hue Range
        self.label_hue = ctk.CTkLabel(self, text="Hue Shift Range:")
        self.label_hue.grid(row=2, column=0, columnspan=2, padx=10, pady=(15, 5), sticky="w")
        
        # Start Hue
        self.label_hue_start = ctk.CTkLabel(self, text="Start:")
        self.label_hue_start.grid(row=3, column=0, padx=10, pady=0, sticky="w")
        self.slider_start = ctk.CTkSlider(self, from_=-1.0, to=1.0)
        self.slider_start.set(0.0)
        self.slider_start.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        
        # End Hue
        self.label_hue_end = ctk.CTkLabel(self, text="End:")
        self.label_hue_end.grid(row=4, column=0, padx=10, pady=0, sticky="w")
        self.slider_end = ctk.CTkSlider(self, from_=-1.0, to=1.0)
        self.slider_end.set(0.5)
        self.slider_end.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        
        # Preview Checkbox
        self.chk_preview = ctk.CTkCheckBox(self, text="Generate Preview Images")
        self.chk_preview.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # Generate Button
        self.btn_generate = ctk.CTkButton(self, text="GENERATE BATCH", command=generate_command, height=40, font=("Roboto", 14, "bold"))
        self.btn_generate.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

    def get_values(self):
        return {
            "count": self.count_var.get(),
            "hue_start": self.slider_start.get(),
            "hue_end": self.slider_end.get(),
            "generate_preview": self.chk_preview.get() == 1
        }
