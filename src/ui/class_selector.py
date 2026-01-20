"""
Class Selector Window for Ragnarok Online palette generation.
Allows selecting multiple classes to generate palettes with specific naming conventions.
"""
import customtkinter as ctk

# (internal_name, display_name)
RO_CLASSES = [
    # Novice
    ("ÃÊº¸ÀÚ", "Novice"),
    ("½´ÆÛ³ëºñ½º", "Super Novice"),
    # 1ª Job (1-1)
    ("¼ºÁ÷ÀÚ", "Acolyte"),
    ("±Ã¼ö", "Archer"),
    ("¸¶¹ý»ç", "Magician"),
    ("»óÀÎ", "Merchant"),
    ("°Ë»ç", "Swordsman"),
    ("µµµÏ", "Thief"),
    # 2-1 Jobs
    ("ÇÁ¸®½ºÆ®", "Priest"),
    ("¼ºÅõ»ç", "Priest (var)"),
    ("ÇåÅÍ", "Hunter"),
    ("À§Àúµå", "Wizard"),
    ("Á¦Ã¶°ø", "Blacksmith"),
    ("±â»ç", "Knight"),
    ("¾î¼¼½Å", "Assassin"),
    # 2-2 Jobs
    ("¸ùÅ©", "Monk"),
    ("¹Ùµå", "Bard"),
    ("¹«Èñ", "Dancer"),
    ("¼¼ÀÌÁö", "Sage"),
    ("¿¬±Ý¼ú»ç", "Alchemist"),
    ("Å©·ç¼¼ÀÌ´õ", "Crusader"),
    ("·Î±×", "Rogue"),
    # Transcendent 2-1
    ("ÇÏÀÌÇÁ¸®", "High Priest"),
    ("¼ºÅõ»ç2", "High Priest (alt)"),
    ("½º³ªÀÌÆÛ", "Sniper"),
    ("ÇÏÀÌÀ§Àúµå", "High Wizard"),
    ("ÈÀÌÆ®½º¹Ì½º", "Whitesmith"),
    ("·Îµå³ªÀÌÆ®", "Lord Knight"),
    ("¾î½Ø½ÅÅ©·Î½º", "Assassin Cross"),
    # Transcendent 2-2
    ("Ã¨ÇÇ¿Â", "Champion"),
    ("Å¬¶ó¿î", "Clown"),
    ("Áý½Ã", "Gypsy"),
    ("ÇÁ·ÎÆä¼", "Professor"),
    ("Å©¸®¿¡ÀÌÅÍ", "Creator"),
    ("ÆÈ¶óµò", "Paladin"),
    ("½ºÅäÄ¿", "Stalker"),
    # 3-1 Jobs
    ("¾ÆÅ©ºñ¼ó", "Archbishop"),
    ("·¹ÀÎÁ®", "Ranger"),
    ("¿ö·Ï", "Warlock"),
    ("¹ÌÄÉ´Ð", "Mechanic"),
    ("·é³ªÀÌÆ®", "Rune Knight"),
    ("±æ·ÎÆ¾Å©·Î½º", "Guillotine Cross"),
    # 3-2 Jobs
    ("½´¶ó", "Sura"),
    ("¹Î½ºÆ®·²", "Minstrel"),
    ("¿ø´õ·¯", "Wanderer"),
    ("¼Ò¼·¯", "Sorcerer"),
    ("Á¦³×¸¯", "Genetic"),
    ("°¡µå", "Royal Guard"),
    ("½¦µµ¿ìÃ¼ÀÌ¼", "Shadow Chaser"),
    # Expanded
    ("°Ç³Ê", "Gunslinger"),
    ("´ÑÀÚ", "Ninja"),
    ("ÅÂ±Ç¼Ò³â", "Taekwon"),
    ("±Ç¼º", "Star Gladiator"),
    ("¼Ò¿ï¸µÄ¿", "Soul Linker"),
    ("¼ºÁ¦", "Star Emperor"),
    ("¼Ò¿ï¸®ÆÛ", "Soul Reaper"),
    ("»êÅ¸", "Natal"),
    ("¿©¸§", "Praia"),
    ("¿î¿µÀÚ", "GM"),
]


class ClassSelectorWindow(ctk.CTkToplevel):
    """Window with checkboxes for selecting RO classes."""
    
    def __init__(self, parent, selected_classes):
        super().__init__(parent)
        self.title("Selecionar Classes")
        self.geometry("400x600")
        self.resizable(True, True)
        
        # Keep on top of parent window
        self.transient(parent)
        self.lift()
        self.focus_force()
        
        # Store references to checkboxes
        self.checkboxes = {}
        # Use the SAME set from parent so changes persist
        self.selected_classes = selected_classes
        # Use the SAME set from parent so changes persist
        self.selected_classes = selected_classes
        
        # Top buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(btn_frame, text="Selecionar Todos", command=self._select_all, width=120).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Limpar", command=self._clear_all, width=80).pack(side="left", padx=5)
        
        # Scrollable frame for checkboxes
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Classes RO")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create checkboxes
        for internal_name, display_name in RO_CLASSES:
            var = ctk.BooleanVar(value=internal_name in self.selected_classes)
            cb = ctk.CTkCheckBox(
                self.scroll_frame,
                text=f"{display_name}",
                variable=var,
                command=lambda n=internal_name, v=var: self._on_toggle(n, v)
            )
            cb.pack(anchor="w", pady=2)
            self.checkboxes[internal_name] = (cb, var)
        
        # Bottom info
        self.lbl_count = ctk.CTkLabel(self, text=f"Selecionadas: {len(self.selected_classes)}")
        self.lbl_count.pack(pady=5)
    
    def _on_toggle(self, name, var):
        if var.get():
            self.selected_classes.add(name)
        else:
            self.selected_classes.discard(name)
        self._update_count()
    
    def _select_all(self):
        for internal_name, (cb, var) in self.checkboxes.items():
            var.set(True)
            self.selected_classes.add(internal_name)
        self._update_count()
    
    def _clear_all(self):
        for internal_name, (cb, var) in self.checkboxes.items():
            var.set(False)
        self.selected_classes.clear()
        self._update_count()
    
    def _update_count(self):
        self.lbl_count.configure(text=f"Selecionadas: {len(self.selected_classes)}")
    
    def get_selected_classes(self):
        """Returns list of selected internal class names."""
        return list(self.selected_classes)
