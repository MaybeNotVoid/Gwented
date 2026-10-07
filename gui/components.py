import customtkinter as ctk
import tkinter as tk

class QuantityStepper(ctk.CTkFrame):
    def __init__(self, master, initial=1, min_val=1, max_val=999, on_change=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.min_val = min_val
        self.max_val = max_val
        self.on_change = on_change
        self.value = initial

        self.btn_minus = ctk.CTkButton(
            self, text="−", width=28, height=28,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2b313d", hover_color="#3c4454",
            text_color="#e5e7eb", corner_radius=6,
            command=self.decrement
        )
        self.btn_minus.pack(side="left", padx=(0, 2))

        self.var = tk.StringVar(value=str(initial))
        self.entry = ctk.CTkEntry(
            self, width=44, height=28,
            textvariable=self.var, justify="center",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#1a1e26", border_color="#374151"
        )
        self.entry.pack(side="left", padx=2)
        self.entry.bind("<FocusOut>", self._validate)
        self.entry.bind("<Return>", self._validate)

        self.btn_plus = ctk.CTkButton(
            self, text="+", width=28, height=28,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2b313d", hover_color="#3c4454",
            text_color="#e5e7eb", corner_radius=6,
            command=self.increment
        )
        self.btn_plus.pack(side="left", padx=(2, 0))

    def get_value(self):
        try:
            val = int(self.var.get())
            return max(self.min_val, min(self.max_val, val))
        except ValueError:
            return self.min_val

    def set_value(self, val):
        val = max(self.min_val, min(self.max_val, val))
        self.value = val
        self.var.set(str(val))
        if self.on_change:
            self.on_change(val)

    def increment(self):
        self.set_value(self.get_value() + 1)

    def decrement(self):
        self.set_value(self.get_value() - 1)

    def _validate(self, event=None):
        self.set_value(self.get_value())


class ItemCard(ctk.CTkFrame):
    def __init__(self, master, item_data, on_send_callback, on_copy_callback, on_fav_toggle, is_fav=False, **kwargs):
        super().__init__(
            master,
            fg_color="#1e232d",
            corner_radius=8,
            border_width=1,
            border_color="#2f3747",
            **kwargs
        )
        self.item_data = item_data
        self.on_send_callback = on_send_callback
        self.on_copy_callback = on_copy_callback
        self.on_fav_toggle = on_fav_toggle
        self.is_fav = is_fav

        # Layout orizzontale
        self.grid_columnconfigure(1, weight=1)

        # Icona
        icon = item_data.get("icon", "📦")
        self.lbl_icon = ctk.CTkLabel(
            self, text=icon, font=ctk.CTkFont(size=20),
            width=36, height=36
        )
        self.lbl_icon.grid(row=0, column=0, rowspan=2, padx=(10, 8), pady=8)

        # Info: Nome Italiano in evidenza + Codice / Nome Originale
        name_it = item_data.get("name_it") or item_data.get("name") or item_data.get("code")
        orig_name = item_data.get("name", "")
        code_text = item_data.get("code", "")
        cat_name = item_data.get("category_name", "")

        self.lbl_name = ctk.CTkLabel(
            self, text=name_it,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#f3f4f6", anchor="w"
        )
        self.lbl_name.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=(6, 0))

        if orig_name and orig_name.lower() != name_it.lower():
            sub_info = f"Codice: {code_text}  •  Originale: {orig_name}  •  {cat_name}"
        else:
            sub_info = f"Codice: {code_text}  •  {cat_name}"

        self.lbl_sub = ctk.CTkLabel(
            self, text=sub_info,
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#9ca3af", anchor="w"
        )
        self.lbl_sub.grid(row=1, column=1, sticky="w", padx=(0, 10), pady=(0, 6))

        # Controlli a destra
        self.ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.ctrl_frame.grid(row=0, column=2, rowspan=2, padx=(10, 12), pady=8, sticky="e")

        # Selettore quantità (se applicabile a additem o spawn)
        has_qty = item_data.get("type") in ["additem", "spawn"]
        if has_qty:
            self.qty_stepper = QuantityStepper(self.ctrl_frame, initial=item_data.get("default_qty", 1), min_val=1, max_val=item_data.get("max_qty", 100))
            self.qty_stepper.pack(side="left", padx=(0, 8))
        else:
            self.qty_stepper = None

        # Pulsante Preferito
        fav_icon = "★" if self.is_fav else "☆"
        fav_color = "#f59e0b" if self.is_fav else "#6b7280"
        self.btn_fav = ctk.CTkButton(
            self.ctrl_frame, text=fav_icon, width=32, height=30,
            font=ctk.CTkFont(size=16),
            fg_color="#2b313d", hover_color="#3c4454",
            text_color=fav_color, corner_radius=6,
            command=self._toggle_fav
        )
        self.btn_fav.pack(side="left", padx=2)

        # Pulsante Copia
        self.btn_copy = ctk.CTkButton(
            self.ctrl_frame, text="📋", width=34, height=30,
            font=ctk.CTkFont(size=13),
            fg_color="#2b313d", hover_color="#3c4454",
            text_color="#d1d5db", corner_radius=6,
            command=self._copy_command
        )
        self.btn_copy.pack(side="left", padx=2)

        # Pulsante INVIA AL GIOCO
        self.btn_send = ctk.CTkButton(
            self.ctrl_frame, text="⚡ Invia al Gioco", width=110, height=30,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#b91c1c", hover_color="#dc2626", # Witcher Red
            text_color="#ffffff", corner_radius=6,
            command=self._send_command
        )
        self.btn_send.pack(side="left", padx=(4, 0))

    def _get_full_command(self):
        cmd_type = self.item_data.get("type", "additem")
        code = self.item_data.get("code", "")
        qty = self.qty_stepper.get_value() if self.qty_stepper else 1
        
        if cmd_type == "additem":
            # Sintassi standard: additem('ItemName', qty)
            return f"additem('{code}', {qty})"
        elif cmd_type == "spawn":
            return f"spawn('{code}', {qty})"
        elif cmd_type == "learnskill":
            return f"learnskill('{code}')"
        else:
            return code

    def _send_command(self):
        cmd = self._get_full_command()
        if self.on_send_callback:
            self.on_send_callback(cmd, self.item_data)

    def _copy_command(self):
        cmd = self._get_full_command()
        if self.on_copy_callback:
            self.on_copy_callback(cmd)

    def _toggle_fav(self):
        self.is_fav = not self.is_fav
        fav_icon = "★" if self.is_fav else "☆"
        fav_color = "#f59e0b" if self.is_fav else "#6b7280"
        self.btn_fav.configure(text=fav_icon, text_color=fav_color)
        if self.on_fav_toggle:
            self.on_fav_toggle(self.item_data["id"], self.is_fav)


class CheatCard(ctk.CTkFrame):
    def __init__(self, master, cheat_data, on_send_callback, on_copy_callback, **kwargs):
        super().__init__(
            master,
            fg_color="#1c212a",
            corner_radius=8,
            border_width=1,
            border_color="#2b3240",
            **kwargs
        )
        self.cheat_data = cheat_data
        self.on_send_callback = on_send_callback
        self.on_copy_callback = on_copy_callback

        self.grid_columnconfigure(1, weight=1)

        icon = cheat_data.get("icon", "⭐")
        self.lbl_icon = ctk.CTkLabel(
            self, text=icon, font=ctk.CTkFont(size=20),
            width=36, height=36
        )
        self.lbl_icon.grid(row=0, column=0, rowspan=2, padx=(10, 8), pady=8)

        name = cheat_data.get("display_name") or cheat_data.get("command")
        self.lbl_name = ctk.CTkLabel(
            self, text=name,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#f3f4f6", anchor="w"
        )
        self.lbl_name.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=(8, 0))

        cmd_text = cheat_data.get("command", "")
        desc = cheat_data.get("description", "")
        self.lbl_sub = ctk.CTkLabel(
            self, text=f"{cmd_text}  •  {desc}",
            font=ctk.CTkFont(size=11),
            text_color="#9ca3af", anchor="w"
        )
        self.lbl_sub.grid(row=1, column=1, sticky="w", padx=(0, 10), pady=(0, 8))

        # Bottoni a destra
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=0, column=2, rowspan=2, padx=(10, 12), pady=8, sticky="e")

        self.btn_copy = ctk.CTkButton(
            self.btn_frame, text="📋", width=34, height=30,
            font=ctk.CTkFont(size=13),
            fg_color="#2b313d", hover_color="#3c4454",
            text_color="#d1d5db", corner_radius=6,
            command=lambda: self.on_copy_callback(cmd_text)
        )
        self.btn_copy.pack(side="left", padx=2)

        self.btn_send = ctk.CTkButton(
            self.btn_frame, text="⚡ Esegui", width=90, height=30,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#ca8a04", hover_color="#eab308", # Gold / Yellow for cheats
            text_color="#000000", corner_radius=6,
            command=lambda: self.on_send_callback(cmd_text, self.cheat_data)
        )
        self.btn_send.pack(side="left", padx=(4, 0))
