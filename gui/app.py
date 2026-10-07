import os
import json
import time
import threading
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from core.game_config import WitcherGameConfig
from core.injector import WitcherInjector
from core.hotkey import GlobalHotkeyManager, VK_MAPPING
from gui.components import ItemCard, CheatCard, QuantityStepper

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(APP_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "database.json")
USER_DATA_PATH = os.path.join(DATA_DIR, "user_data.json")

class WitcherApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurazione Stile
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("The Witcher 3: Console & Spawn Master • Gwented Edition")
        self.geometry("1140x740")
        self.minsize(960, 620)
        self.configure(fg_color="#12151b")

        # Moduli Core
        self.game_cfg = WitcherGameConfig()
        self.injector = WitcherInjector(console_key_mode="auto")
        
        # Dati
        self.database = self.load_database()
        self.user_data = self.load_user_data()

        # Sincronizza opzioni con injector
        self.injector.animation_delay = self.user_data.get("animation_delay_ms", 400) / 1000.0
        self.injector.close_method = self.user_data.get("close_method", "toggle")
        self.injector.input_mode = self.user_data.get("input_mode", "clipboard")
        self._apply_typing_speed(self.user_data.get("typing_speed", "normale"))

        # Stato UI
        self.current_category = "GwentCards"
        self.search_query = ""
        self.current_page = 0
        self.items_per_page = 40
        self.filtered_items = []
        self.toast_job = None
        self.search_timer = None

        # Hotkey Manager
        hotkey_name = self.user_data.get("hotkey", "F2")
        self.hotkey_mgr = GlobalHotkeyManager(
            on_hotkey_callback=self._on_global_hotkey_triggered,
            hotkey_name=hotkey_name
        )
        if self.user_data.get("hotkey_enabled", True):
            self.hotkey_mgr.start()

        # Costruzione Layout
        self._build_header()
        self._build_main_layout()
        self._build_statusbar()

        # Carica categoria iniziale
        self._select_category("GwentCards")

        # Loop di monitoraggio stato gioco (ogni 2.5s)
        self._check_game_status_loop()

        # Chiusura pulita
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def load_database(self):
        if os.path.exists(DB_PATH):
            try:
                with open(DB_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._build_search_index(data.get("items", []))
                    return data
            except Exception as e:
                print(f"Errore caricamento database: {e}")
        return {"items": [], "cheats": [], "categories": {}}

    def _build_search_index(self, items):
        """Costruisce o normalizza i blob di ricerca per filtraggio istantaneo in memoria."""
        for it in items:
            if "search_blob" not in it:
                name_it = it.get("name_it", "")
                name = it.get("name", "")
                code = it.get("code", "")
                cat_name = it.get("category_name", "")
                tags_str = " ".join(it.get("tags", []))
                raw = f"{name_it} {name} {code} {cat_name} {tags_str}".lower()
                it["search_blob"] = "".join(c if c.isalnum() else " " for c in raw)
            else:
                it["search_blob"] = it["search_blob"].lower()

    def _apply_typing_speed(self, speed):
        if speed == "veloce":
            self.injector.char_hold = 0.015
            self.injector.char_delay = 0.010
        elif speed == "sicura":
            self.injector.char_hold = 0.035
            self.injector.char_delay = 0.025
        else:
            self.injector.char_hold = 0.020
            self.injector.char_delay = 0.015

    def load_user_data(self):
        default_data = {
            "favorites": [],
            "history": [],
            "hotkey": "F2",
            "hotkey_enabled": True,
            "auto_close_console": True,
            "animation_delay_ms": 400,
            "typing_speed": "normale",
            "close_method": "toggle",
            "input_mode": "clipboard"
        }
        if os.path.exists(USER_DATA_PATH):
            try:
                with open(USER_DATA_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    default_data.update(data)
            except Exception:
                pass
        return default_data

    def save_user_data(self):
        try:
            with open(USER_DATA_PATH, "w", encoding="utf-8") as f:
                json.dump(self.user_data, f, indent=2)
        except Exception as e:
            print(f"Errore salvataggio user_data: {e}")

    # ==========================
    # LAYOUT: HEADER
    # ==========================
    def _build_header(self):
        self.header_frame = ctk.CTkFrame(self, fg_color="#181c24", height=68, corner_radius=0)
        self.header_frame.pack(side="top", fill="x")
        self.header_frame.pack_propagate(False)

        # Titolo e Icona Witcher
        title_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_box.pack(side="left", padx=(18, 10), pady=8)

        lbl_logo = ctk.CTkLabel(
            title_box, text="🐺", font=ctk.CTkFont(size=26),
            width=36, height=36
        )
        lbl_logo.pack(side="left", padx=(0, 8))

        title_inner = ctk.CTkFrame(title_box, fg_color="transparent")
        title_inner.pack(side="left")

        lbl_app_name = ctk.CTkLabel(
            title_inner, text="THE WITCHER 3 : CONSOLE & SPAWN MASTER",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="#f3f4f6"
        )
        lbl_app_name.pack(anchor="w")

        lbl_subtitle = ctk.CTkLabel(
            title_inner, text="Fix Tastiera Italiana • Spawn Automatico 1-Click • Oltre 2.500 Codici",
            font=ctk.CTkFont(size=11),
            text_color="#9ca3af"
        )
        lbl_subtitle.pack(anchor="w")

        # Controlli a destra nell'header
        right_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        right_box.pack(side="right", padx=(10, 18), pady=8)

        # Badge stato gioco
        self.status_badge = ctk.CTkLabel(
            right_box, text="● Gioco Non Avviato",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#2b313d", text_color="#9ca3af",
            corner_radius=12, padx=12, pady=4
        )
        self.status_badge.pack(side="left", padx=6)

        # Pulsante rapido "Apri Console in Gioco"
        self.btn_toggle_console = ctk.CTkButton(
            right_box, text="🎮 Apri/Chiudi Console",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#374151", hover_color="#4b5563",
            text_color="#f3f4f6", corner_radius=6, height=32,
            command=self._on_manual_toggle_console
        )
        self.btn_toggle_console.pack(side="left", padx=6)

        # Tasto Rapido Badge
        hk_name = self.user_data.get("hotkey", "F2")
        self.lbl_hotkey_badge = ctk.CTkLabel(
            right_box, text=f"⚡ Hotkey: {hk_name}",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#854d0e", text_color="#fef08a",
            corner_radius=6, padx=8, pady=4
        )
        self.lbl_hotkey_badge.pack(side="left", padx=4)

        # Pulsante Rapido Modalità Input (Ctrl+V o Digitazione)
        mode = self.user_data.get("input_mode", "clipboard")
        mode_text = "📋 Ctrl+V" if mode == "clipboard" else "⌨️ Digitazione IT"
        mode_color = "#1e3a8a" if mode == "clipboard" else "#065f46"
        self.btn_mode_badge = ctk.CTkButton(
            right_box, text=f"{mode_text}",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=mode_color, hover_color="#2563eb",
            corner_radius=6, height=28, width=115,
            command=self._toggle_quick_input_mode
        )
        self.btn_mode_badge.pack(side="left", padx=4)

    # ==========================
    # LAYOUT: MAIN (Sidebar + Content)
    # ==========================
    def _build_main_layout(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=(8, 4))

        # SIDEBAR (Categorie)
        self.sidebar_frame = ctk.CTkFrame(self.main_container, fg_color="#161a22", width=220, corner_radius=8)
        self.sidebar_frame.pack(side="left", fill="y", padx=(0, 8))
        self.sidebar_frame.pack_propagate(False)

        # Titolo Sidebar
        lbl_cat_title = ctk.CTkLabel(
            self.sidebar_frame, text="CATEGORIE",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#6b7280"
        )
        lbl_cat_title.pack(anchor="w", padx=16, pady=(12, 6))

        # Scrollable per categorie
        self.cat_scroll = ctk.CTkScrollableFrame(self.sidebar_frame, fg_color="transparent")
        self.cat_scroll.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        self.category_buttons = {}
        
        # Categorie speciali in cima
        special_cats = [
            ("all", "Tutti gli Oggetti", "🌐"),
            ("fav", "I Miei Preferiti", "★"),
            ("Cheats", "Trucchi Rapidi", "⭐")
        ]
        for cat_id, cat_name, icon in special_cats:
            self._create_sidebar_btn(cat_id, cat_name, icon)

        # Separatore visivo
        sep = ctk.CTkFrame(self.cat_scroll, fg_color="#2b313d", height=1)
        sep.pack(fill="x", padx=6, pady=6)

        # Categorie database
        for cat_id, info in self.database.get("categories", {}).items():
            self._create_sidebar_btn(cat_id, info["name"], info["icon"])

        # Separatore visivo inferiore
        sep2 = ctk.CTkFrame(self.cat_scroll, fg_color="#2b313d", height=1)
        sep2.pack(fill="x", padx=6, pady=6)

        self._create_sidebar_btn("history", "Cronologia Comandi", "🕒")
        self._create_sidebar_btn("settings", "Guida Tastiera & Config", "⚙️")

        # AREA CONTENUTO CENTRALE
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="#181c24", corner_radius=8)
        self.content_frame.pack(side="left", fill="both", expand=True)

        # Barra superiore del contenuto: Ricerca + Filtri Rapidi
        self.toolbar_frame = ctk.CTkFrame(self.content_frame, fg_color="#1b2029", height=54, corner_radius=8)
        self.toolbar_frame.pack(fill="x", padx=10, pady=10)
        self.toolbar_frame.pack_propagate(False)

        # Casella di Ricerca
        self.search_entry = ctk.CTkEntry(
            self.toolbar_frame, width=280, height=34,
            placeholder_text="🔍 Cerca nome, codice (es: Geralt, Orso, addmoney)...",
            font=ctk.CTkFont(size=12),
            fg_color="#12151b", border_color="#374151"
        )
        self.search_entry.pack(side="left", padx=(10, 8), pady=10)
        self.search_entry.bind("<KeyRelease>", self._on_search_key)

        # Pulsante cancella ricerca
        btn_clear_search = ctk.CTkButton(
            self.toolbar_frame, text="✖", width=30, height=34,
            font=ctk.CTkFont(size=11),
            fg_color="#2b313d", hover_color="#3c4454",
            text_color="#9ca3af", corner_radius=6,
            command=self._clear_search
        )
        btn_clear_search.pack(side="left", padx=(0, 10))

        # Contatore elementi trovati
        self.lbl_count = ctk.CTkLabel(
            self.toolbar_frame, text="0 elementi",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#9ca3af"
        )
        self.lbl_count.pack(side="left", padx=4)

        # Quick Cheats Shortcuts (a destra della toolbar)
        quick_cheats_box = ctk.CTkFrame(self.toolbar_frame, fg_color="transparent")
        quick_cheats_box.pack(side="right", padx=(0, 10))

        btn_god = ctk.CTkButton(
            quick_cheats_box, text="🛡️ God Mode", width=82, height=28,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#831843", hover_color="#9d174d",
            command=lambda: self.send_command_to_game("god")
        )
        btn_god.pack(side="left", padx=3)

        btn_heal = ctk.CTkButton(
            quick_cheats_box, text="❤️ Cura", width=68, height=28,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#065f46", hover_color="#047857",
            command=lambda: self.send_command_to_game("healme")
        )
        btn_heal.pack(side="left", padx=3)

        btn_money = ctk.CTkButton(
            quick_cheats_box, text="💰 +50k Corone", width=105, height=28,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#854d0e", hover_color="#a16207",
            command=lambda: self.send_command_to_game("addmoney(50000)")
        )
        btn_money.pack(side="left", padx=3)

        btn_all_gwent = ctk.CTkButton(
            quick_cheats_box, text="🃏 Gwent (1x)", width=95, height=28,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#1e3a8a", hover_color="#1d4ed8",
            command=lambda: self.send_command_to_game("addgwintcards")
        )
        btn_all_gwent.pack(side="left", padx=3)

        btn_all_gwent_4x = ctk.CTkButton(
            quick_cheats_box, text="⚡ Gwent All 4x", width=115, height=28,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#6d28d9", hover_color="#7c3aed",
            command=self._on_give_all_gwent_4x
        )
        btn_all_gwent_4x.pack(side="left", padx=3)

        # Area Lista Elementi (Scrollable)
        self.items_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.items_container.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        self.items_scroll = ctk.CTkScrollableFrame(self.items_container, fg_color="transparent")
        self.items_scroll.pack(fill="both", expand=True)

        # Barra di Paginazione inferiore
        self.pagination_frame = ctk.CTkFrame(self.content_frame, fg_color="#161a22", height=42, corner_radius=6)
        self.pagination_frame.pack(fill="x", padx=10, pady=(0, 8))
        self.pagination_frame.pack_propagate(False)

        self.btn_prev_page = ctk.CTkButton(
            self.pagination_frame, text="◀ Pagina Prec.", width=100, height=26,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#2b313d", hover_color="#3c4454",
            command=self._prev_page
        )
        self.btn_prev_page.pack(side="left", padx=10, pady=8)

        self.lbl_page_info = ctk.CTkLabel(
            self.pagination_frame, text="Pagina 1 di 1",
            font=ctk.CTkFont(size=11),
            text_color="#9ca3af"
        )
        self.lbl_page_info.pack(side="left", expand=True)

        self.btn_next_page = ctk.CTkButton(
            self.pagination_frame, text="Pagina Succ. ▶", width=100, height=26,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#2b313d", hover_color="#3c4454",
            command=self._next_page
        )
        self.btn_next_page.pack(side="right", padx=10, pady=8)

    # ==========================
    # LAYOUT: STATUSBAR & TOAST
    # ==========================
    def _build_statusbar(self):
        self.statusbar = ctk.CTkFrame(self, fg_color="#0e1117", height=32, corner_radius=0)
        self.statusbar.pack(side="bottom", fill="x")
        self.statusbar.pack_propagate(False)

        # Messaggio notifica (Toast)
        self.lbl_toast = ctk.CTkLabel(
            self.statusbar, text="Pronto. Scegli un oggetto o comando e premi 'Invia al Gioco'.",
            font=ctk.CTkFont(size=11),
            text_color="#9ca3af", anchor="w"
        )
        self.lbl_toast.pack(side="left", padx=14)

        # Opzione Auto-Close Console
        self.chk_autoclose = ctk.CTkCheckBox(
            self.statusbar, text="Chiudi console automaticamente dopo l'invio",
            font=ctk.CTkFont(size=11),
            checkbox_width=16, checkbox_height=16,
            fg_color="#b91c1c", hover_color="#dc2626",
            command=self._on_toggle_autoclose
        )
        if self.user_data.get("auto_close_console", True):
            self.chk_autoclose.select()
        else:
            self.chk_autoclose.deselect()
        self.chk_autoclose.pack(side="right", padx=14)

    # ==========================
    # SIDEBAR CREATOR & LOGIC
    # ==========================
    def _create_sidebar_btn(self, cat_id, cat_name, icon):
        btn = ctk.CTkButton(
            self.cat_scroll, text=f"{icon}  {cat_name}",
            font=ctk.CTkFont(size=12),
            fg_color="transparent", hover_color="#242a36",
            text_color="#d1d5db", anchor="w",
            height=34, corner_radius=6,
            command=lambda: self._select_category(cat_id)
        )
        btn.pack(fill="x", pady=1)
        self.category_buttons[cat_id] = btn

    def _select_category(self, cat_id):
        self.current_category = cat_id
        self.current_page = 0

        # Aggiorna evidenziazione pulsanti sidebar
        for cid, btn in self.category_buttons.items():
            if cid == cat_id:
                btn.configure(fg_color="#272e3d", text_color="#ffffff", font=ctk.CTkFont(size=12, weight="bold"))
            else:
                btn.configure(fg_color="transparent", text_color="#d1d5db", font=ctk.CTkFont(size=12))

        self._refresh_items_list()

    def _on_search_key(self, event=None):
        # Debouncing 140ms per eliminare lag e freeze alla digitazione
        if self.search_timer:
            self.after_cancel(self.search_timer)
        self.search_timer = self.after(140, self._perform_search)

    def _perform_search(self):
        new_query = self.search_entry.get().strip().lower()
        if new_query != self.search_query:
            self.search_query = new_query
            self.current_page = 0
            self._refresh_items_list()

    def _clear_search(self):
        if self.search_timer:
            self.after_cancel(self.search_timer)
            self.search_timer = None
        self.search_entry.delete(0, "end")
        self.search_query = ""
        self.current_page = 0
        self._refresh_items_list()

    # ==========================
    # FILTRO ED ELENCO ELEMENTI
    # ==========================
    def _refresh_items_list(self):
        # Pulisci scrollable frame corrente
        for widget in self.items_scroll.winfo_children():
            widget.destroy()

        cat = self.current_category

        # Caso speciale: SCHERMATA IMPOSTAZIONI / GUIDA TASTIERA IT
        if cat == "settings":
            self.pagination_frame.pack_forget()
            self._render_settings_view()
            return
        else:
            if not self.pagination_frame.winfo_ismapped():
                self.pagination_frame.pack(fill="x", padx=10, pady=(0, 8))

        # Caso speciale: TRUCCHI / CHEATS
        if cat == "Cheats":
            self._render_cheats_view()
            return

        # Caso speciale: CRONOLOGIA
        if cat == "history":
            self._render_history_view()
            return

        # Filtra oggetti normali
        all_items = self.database.get("items", [])
        favs = set(self.user_data.get("favorites", []))

        # Filtro per categoria
        if cat == "all":
            category_items = all_items
        elif cat == "fav":
            category_items = [it for it in all_items if it.get("id") in favs]
        else:
            category_items = [it for it in all_items if it.get("category_key") == cat]

        # Filtro di ricerca ultra-rapido con indice search_blob
        query = self.search_query.strip().lower()
        if query:
            terms = query.split()
            filtered = [
                it for it in category_items
                if all(term in it.get("search_blob", "") for term in terms)
            ]
        else:
            filtered = category_items

        self.filtered_items = filtered
        total_items = len(filtered)
        self.lbl_count.configure(text=f"{total_items} elementi")

        # Banner promozionale 4x per Carte Gwent
        if cat == "GwentCards" and not query:
            banner = ctk.CTkFrame(self.items_scroll, fg_color="#241442", corner_radius=8, border_width=1, border_color="#6d28d9")
            banner.pack(fill="x", pady=(2, 10), padx=2)

            b_left = ctk.CTkFrame(banner, fg_color="transparent")
            b_left.pack(side="left", padx=12, pady=10)

            lbl_b1 = ctk.CTkLabel(
                b_left, text="🃏 Sblocca Tutte le 173 Carte Gwent in 4x Copia",
                font=ctk.CTkFont(size=13, weight="bold"), text_color="#f5f3ff"
            )
            lbl_b1.pack(anchor="w")
            lbl_b2 = ctk.CTkLabel(
                b_left, text="Aggiunge 4 copie di ciascuna carta per mazzi imbattibili (totale 692 carte: spie, medici e abilità Legame Stretto al massimo).",
                font=ctk.CTkFont(size=11), text_color="#c4b5fd"
            )
            lbl_b2.pack(anchor="w")

            btn_b_4x = ctk.CTkButton(
                banner, text="⚡ Inietta Carte Gwent (4x)",
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#7c3aed", hover_color="#8b5cf6",
                height=32, width=190,
                command=self._on_give_all_gwent_4x
            )
            btn_b_4x.pack(side="right", padx=12, pady=10)

        if total_items == 0:
            lbl_empty = ctk.CTkLabel(
                self.items_scroll,
                text="Nessun elemento trovato per questa categoria o ricerca.",
                font=ctk.CTkFont(size=14), text_color="#6b7280"
            )
            lbl_empty.pack(pady=40)
            self.lbl_page_info.configure(text="Pagina 0 di 0")
            self.btn_prev_page.configure(state="disabled")
            self.btn_next_page.configure(state="disabled")
            return

        # Calcolo Paginazione
        total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        self.current_page = max(0, min(self.current_page, total_pages - 1))
        
        self.lbl_page_info.configure(text=f"Pagina {self.current_page + 1} di {total_pages} (Mostrati {min(self.items_per_page, total_items)} per pagina)")
        self.btn_prev_page.configure(state="normal" if self.current_page > 0 else "disabled")
        self.btn_next_page.configure(state="normal" if self.current_page < total_pages - 1 else "disabled")

        start_idx = self.current_page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_items)

        # Rendering delle card
        for it in filtered[start_idx:end_idx]:
            is_fav = it.get("id") in favs
            card = ItemCard(
                self.items_scroll,
                item_data=it,
                on_send_callback=self._on_item_send,
                on_copy_callback=self._on_copy_command,
                on_fav_toggle=self._on_fav_toggle,
                is_fav=is_fav
            )
            card.pack(fill="x", pady=3)

    def _render_cheats_view(self):
        cheats = self.database.get("cheats", [])
        query = self.search_query
        if query:
            cheats = [
                c for c in cheats
                if query in c.get("display_name", "").lower() or
                   query in c.get("command", "").lower() or
                   query in c.get("description", "").lower()
            ]

        self.lbl_count.configure(text=f"{len(cheats)} trucchi disponibili")
        self.lbl_page_info.configure(text=f"Tutti i trucchi ({len(cheats)})")
        self.btn_prev_page.configure(state="disabled")
        self.btn_next_page.configure(state="disabled")

        # Banner Gwent 4x speciale
        if not query or "gwent" in query or "4x" in query or "carte" in query:
            banner = ctk.CTkFrame(self.items_scroll, fg_color="#241442", corner_radius=8, border_width=1, border_color="#6d28d9")
            banner.pack(fill="x", pady=(2, 10), padx=2)

            b_left = ctk.CTkFrame(banner, fg_color="transparent")
            b_left.pack(side="left", padx=12, pady=10)

            lbl_b1 = ctk.CTkLabel(
                b_left, text="🃏 Sblocca Tutte le 173 Carte Gwent in 4x Copia",
                font=ctk.CTkFont(size=13, weight="bold"), text_color="#f5f3ff"
            )
            lbl_b1.pack(anchor="w")
            lbl_b2 = ctk.CTkLabel(
                b_left, text="Inietta automaticamente 4 copie di ogni carta Gwent per costruire mazzi imbattibili (totale 692 carte).",
                font=ctk.CTkFont(size=11), text_color="#c4b5fd"
            )
            lbl_b2.pack(anchor="w")

            btn_b_4x = ctk.CTkButton(
                banner, text="⚡ Inietta Gwent (4x)",
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#7c3aed", hover_color="#8b5cf6",
                height=32, width=190,
                command=self._on_give_all_gwent_4x
            )
            btn_b_4x.pack(side="right", padx=12, pady=10)

        for c in cheats:
            card = CheatCard(
                self.items_scroll,
                cheat_data=c,
                on_send_callback=self._on_cheat_send,
                on_copy_callback=self._on_copy_command
            )
            card.pack(fill="x", pady=3)

    def _render_history_view(self):
        history = self.user_data.get("history", [])
        self.lbl_count.configure(text=f"{len(history)} comandi recenti")
        self.lbl_page_info.configure(text=f"Cronologia ({len(history)})")
        self.btn_prev_page.configure(state="disabled")
        self.btn_next_page.configure(state="disabled")

        if not history:
            lbl = ctk.CTkLabel(self.items_scroll, text="Nessun comando nella cronologia.", font=ctk.CTkFont(size=14), text_color="#6b7280")
            lbl.pack(pady=40)
            return

        # Pulsante cancella cronologia
        btn_clear_hist = ctk.CTkButton(
            self.items_scroll, text="🗑️ Cancella Cronologia",
            fg_color="#374151", hover_color="#4b5563",
            height=28, font=ctk.CTkFont(size=11),
            command=self._clear_history
        )
        btn_clear_hist.pack(anchor="e", pady=(0, 8))

        for entry in reversed(history):
            cmd = entry.get("command", "")
            t_str = entry.get("time", "")
            
            row = ctk.CTkFrame(self.items_scroll, fg_color="#1e232d", corner_radius=6)
            row.pack(fill="x", pady=2)
            row.grid_columnconfigure(0, weight=1)

            lbl = ctk.CTkLabel(
                row, text=f"{cmd}",
                font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
                text_color="#f3f4f6", anchor="w"
            )
            lbl.grid(row=0, column=0, padx=12, pady=6, sticky="w")

            lbl_time = ctk.CTkLabel(
                row, text=t_str, font=ctk.CTkFont(size=10),
                text_color="#6b7280"
            )
            lbl_time.grid(row=0, column=1, padx=8, pady=6)

            btn_re = ctk.CTkButton(
                row, text="⚡ Re-invia", width=80, height=26,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#b91c1c", hover_color="#dc2626",
                command=lambda c=cmd: self.send_command_to_game(c)
            )
            btn_re.grid(row=0, column=2, padx=(4, 10), pady=6)

    def _render_settings_view(self):
        panel = ctk.CTkFrame(self.items_scroll, fg_color="#181c24")
        panel.pack(fill="both", expand=True, padx=20, pady=10)

        # Titolo
        lbl_title = ctk.CTkLabel(
            panel, text="🛠️ Guida Tastiera Italiana & Configurazione Gioco",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#f3f4f6"
        )
        lbl_title.pack(anchor="w", pady=(0, 12))

        # Box esplicativo Tastiera IT
        box_it = ctk.CTkFrame(panel, fg_color="#1f2937", corner_radius=8, border_width=1, border_color="#374151")
        box_it.pack(fill="x", pady=6)

        lbl_it_title = ctk.CTkLabel(
            box_it, text="💡 Perché il tasto tilde (~) non apre la console su tastiere italiane?",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#f59e0b"
        )
        lbl_it_title.pack(anchor="w", padx=14, pady=(10, 4))

        it_text = (
            "Nel motore di gioco di The Witcher 3 (RedEngine), il comando per aprire la console di debug è legato "
            "al codice tasto OEM_3 (tilde/accento grave), che sulle tastiere US si trova sotto il tasto ESC.\n"
            "Sulle tastiere italiane, quel tasto fisico corrisponde a '\\' e '|', che produce il codice VK_OEM_5. "
            "Inoltre, digitare la tilde con [AltGr + ì] invia una sequenza di tasti che il gioco non riconosce.\n\n"
            "✨ COME RISOLVE QUESTO IL NOSTRO PROGRAMMA:\n"
            "1. L'app inietta direttamente lo scancode hardware originale (0x29) e VK_OEM_3 al processo di The Witcher 3.\n"
            "2. Puoi usare il tasto rapido F2 mentre sei in partita per aprire/chiudere la console istantaneamente.\n"
            "3. Con il pulsante 'Invia al Gioco', l'app apre la console, digita il comando e la richiude da sola!"
        )
        lbl_it_desc = ctk.CTkLabel(
            box_it, text=it_text, justify="left",
            font=ctk.CTkFont(size=12), text_color="#d1d5db"
        )
        lbl_it_desc.pack(anchor="w", padx=14, pady=(0, 12))

        # Box Configurazione general.ini
        box_cfg = ctk.CTkFrame(panel, fg_color="#1f2937", corner_radius=8, border_width=1, border_color="#374151")
        box_cfg.pack(fill="x", pady=6)

        lbl_cfg_title = ctk.CTkLabel(
            box_cfg, text="📁 Rilevamento Gioco e Stato Console (general.ini)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#60a5fa"
        )
        lbl_cfg_title.pack(anchor="w", padx=14, pady=(10, 6))

        game_dir = self.game_cfg.game_path or "Non rilevato automaticamente"
        lbl_game_dir = ctk.CTkLabel(
            box_cfg, text=f"Percorso installazione: {game_dir}",
            font=ctk.CTkFont(family="Consolas", size=11), text_color="#9ca3af"
        )
        lbl_game_dir.pack(anchor="w", padx=14, pady=2)

        enabled, status_msg = self.game_cfg.is_console_enabled()
        status_color = "#34d399" if enabled else "#f87171"
        lbl_cfg_status = ctk.CTkLabel(
            box_cfg, text=f"Stato Console: {status_msg}",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=status_color
        )
        lbl_cfg_status.pack(anchor="w", padx=14, pady=4)

        btn_enable_console = ctk.CTkButton(
            box_cfg, text="🔧 Abilita Console (Aggiungi DBGConsoleOn=true a general.ini)",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#047857", hover_color="#059669",
            command=self._on_enable_console_click
        )
        btn_enable_console.pack(anchor="w", padx=14, pady=(4, 12))

        # Box Tasto Rapido In-Gioco
        box_hk = ctk.CTkFrame(panel, fg_color="#1f2937", corner_radius=8, border_width=1, border_color="#374151")
        box_hk.pack(fill="x", pady=6)

        lbl_hk_title = ctk.CTkLabel(
            box_hk, text="⌨️ Tasto Rapido Globale In-Game (Apre la console mentre giochi)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#c084fc"
        )
        lbl_hk_title.pack(anchor="w", padx=14, pady=(10, 6))

        hk_row = ctk.CTkFrame(box_hk, fg_color="transparent")
        hk_row.pack(fill="x", padx=14, pady=(0, 12))

        lbl_sel_hk = ctk.CTkLabel(hk_row, text="Scegli Tasto Rapido:", font=ctk.CTkFont(size=12), text_color="#e5e7eb")
        lbl_sel_hk.pack(side="left", padx=(0, 10))

        self.cmb_hotkey = ctk.CTkComboBox(
            hk_row, values=list(VK_MAPPING.keys()),
            width=140, font=ctk.CTkFont(size=12),
            command=self._on_hotkey_change
        )
        self.cmb_hotkey.set(self.user_data.get("hotkey", "F2"))
        self.cmb_hotkey.pack(side="left", padx=4)

        btn_test_toggle = ctk.CTkButton(
            hk_row, text="🧪 Prova Apertura Console nel Gioco",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#4b5563", hover_color="#6b7280",
            command=self._on_manual_toggle_console
        )
        btn_test_toggle.pack(side="left", padx=14)

        # Box Parametri Automazione Avanzati
        box_auto = ctk.CTkFrame(panel, fg_color="#1f2937", corner_radius=8, border_width=1, border_color="#374151")
        box_auto.pack(fill="x", pady=6)

        lbl_auto_title = ctk.CTkLabel(
            box_auto, text="⚙️ Parametri di Temporizzazione Automazione (Consigliati)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#10b981"
        )
        lbl_auto_title.pack(anchor="w", padx=14, pady=(10, 6))

        # Riga 1: Attesa animazione console
        row_time = ctk.CTkFrame(box_auto, fg_color="transparent")
        row_time.pack(fill="x", padx=14, pady=4)

        lbl_anim = ctk.CTkLabel(row_time, text="Attesa discesa console:", width=180, anchor="w", font=ctk.CTkFont(size=12))
        lbl_anim.pack(side="left")

        self.cmb_anim = ctk.CTkComboBox(
            row_time, values=["300 ms", "400 ms (Consigliato)", "500 ms", "600 ms", "700 ms"],
            width=190, font=ctk.CTkFont(size=12),
            command=self._on_anim_delay_change
        )
        current_delay = self.user_data.get("animation_delay_ms", 400)
        self.cmb_anim.set(f"{current_delay} ms (Consigliato)" if current_delay == 400 else f"{current_delay} ms")
        self.cmb_anim.pack(side="left", padx=6)

        # Riga 2: Velocità digitazione
        row_speed = ctk.CTkFrame(box_auto, fg_color="transparent")
        row_speed.pack(fill="x", padx=14, pady=4)

        lbl_spd = ctk.CTkLabel(row_speed, text="Velocità digitazione:", width=180, anchor="w", font=ctk.CTkFont(size=12))
        lbl_spd.pack(side="left")

        self.cmb_speed = ctk.CTkComboBox(
            row_speed, values=["normale (Consigliata)", "veloce", "sicura (Lenta)"],
            width=190, font=ctk.CTkFont(size=12),
            command=self._on_speed_change
        )
        self.cmb_speed.set(self.user_data.get("typing_speed", "normale"))
        self.cmb_speed.pack(side="left", padx=6)

        # Riga 3: Metodo chiusura
        row_close = ctk.CTkFrame(box_auto, fg_color="transparent")
        row_close.pack(fill="x", padx=14, pady=4)

        lbl_cl = ctk.CTkLabel(row_close, text="Tasto chiusura console:", width=180, anchor="w", font=ctk.CTkFont(size=12))
        lbl_cl.pack(side="left")

        self.cmb_close = ctk.CTkComboBox(
            row_close, values=["Tasto Console (~) [Consigliato]", "Tasto ESC"],
            width=220, font=ctk.CTkFont(size=12),
            command=self._on_close_method_change
        )
        current_method = self.user_data.get("close_method", "toggle")
        self.cmb_close.set("Tasto Console (~) [Consigliato]" if current_method == "toggle" else "Tasto ESC")
        self.cmb_close.pack(side="left", padx=6)

        # Riga 4: Metodo inserimento comando
        row_mode = ctk.CTkFrame(box_auto, fg_color="transparent")
        row_mode.pack(fill="x", padx=14, pady=(4, 12))

        lbl_mode = ctk.CTkLabel(row_mode, text="Modalità scrittura:", width=180, anchor="w", font=ctk.CTkFont(size=12))
        lbl_mode.pack(side="left")

        self.cmb_mode = ctk.CTkComboBox(
            row_mode, values=[
                "Incolla Rapido (Ctrl+V) [Consigliato]",
                "Digitazione Hardware (Layout IT)",
                "Digitazione Lenta di Sicurezza"
            ],
            width=270, font=ctk.CTkFont(size=12),
            command=self._on_input_mode_change
        )
        current_mode = self.user_data.get("input_mode", "clipboard")
        if current_mode in ["typing", "redengine"]:
            self.cmb_mode.set("Digitazione Hardware (Layout IT)")
        elif current_mode == "slow":
            self.cmb_mode.set("Digitazione Lenta di Sicurezza")
        else:
            self.cmb_mode.set("Incolla Rapido (Ctrl+V) [Consigliato]")
        self.cmb_mode.pack(side="left", padx=6)

    # ==========================
    # AZIONI ED ESECUZIONE
    # ==========================
    def _on_item_send(self, command, item_data):
        self.send_command_to_game(command)

    def _on_cheat_send(self, command, cheat_data):
        self.send_command_to_game(command)

    def _on_give_all_gwent_4x(self):
        cards = [it for it in self.database.get("items", []) if it.get("category_key") == "GwentCards"]
        if not cards:
            self.show_toast("Nessuna carta Gwent trovata nel database.", is_error=True)
            return

        def status_cb(msg):
            self.after(0, lambda: self.show_toast(msg))

        def run_batch():
            success, msg = self.injector.give_all_gwent_cards(cards, count=4, status_callback=status_cb)
            if success:
                self.after(0, lambda: self.show_toast(f"✅ {msg}"))
            else:
                self.after(0, lambda: self.show_toast(f"⚠️ {msg}", is_error=True))

        threading.Thread(target=run_batch, daemon=True).start()

    def _on_copy_command(self, command):
        self.clipboard_clear()
        self.clipboard_append(command)
        self.show_toast(f"📋 Comando copiato negli appunti: {command}")

    def _on_fav_toggle(self, item_id, is_fav):
        favs = self.user_data.get("favorites", [])
        if is_fav and item_id not in favs:
            favs.append(item_id)
        elif not is_fav and item_id in favs:
            favs.remove(item_id)
        self.user_data["favorites"] = favs
        self.save_user_data()

    def _on_manual_toggle_console(self):
        success, msg = self.injector.toggle_console()
        if success:
            self.show_toast("🎮 Segnale console inviato a The Witcher 3!")
        else:
            self.show_toast(f"⚠️ {msg}", is_error=True)

    def _on_global_hotkey_triggered(self):
        # Callback richiamata quando l'utente preme il tasto F2 in background
        print(f"Hotkey {self.user_data.get('hotkey', 'F2')} attivata in background!")
        self.injector.toggle_console()

    def _on_toggle_autoclose(self):
        val = bool(self.chk_autoclose.get())
        self.user_data["auto_close_console"] = val
        self.save_user_data()

    def _on_hotkey_change(self, choice):
        self.user_data["hotkey"] = choice
        self.save_user_data()
        self.hotkey_mgr.set_hotkey(choice)
        self.lbl_hotkey_badge.configure(text=f"⚡ Hotkey: {choice}")
        self.show_toast(f"Tasto rapido aggiornato a: {choice}")

    def _on_anim_delay_change(self, choice):
        # Es: '400 ms (Consigliato)' -> 400
        ms_val = int(choice.split()[0])
        self.user_data["animation_delay_ms"] = ms_val
        self.save_user_data()
        self.injector.animation_delay = ms_val / 1000.0
        self.show_toast(f"Attesa animazione console impostata a: {ms_val} ms")

    def _on_speed_change(self, choice):
        clean = choice.split()[0].lower()
        self.user_data["typing_speed"] = clean
        self.save_user_data()
        self._apply_typing_speed(clean)
        self.show_toast(f"Velocità digitazione impostata a: {clean}")

    def _on_close_method_change(self, choice):
        method = "escape" if "ESC" in choice else "toggle"
        self.user_data["close_method"] = method
        self.save_user_data()
        self.injector.close_method = method
        self.show_toast(f"Metodo chiusura console impostato a: {'ESC' if method == 'escape' else 'Tasto Console'}")

    def _update_mode_badge(self, mode):
        if hasattr(self, 'btn_mode_badge'):
            if mode == "clipboard":
                self.btn_mode_badge.configure(text="📋 Ctrl+V", fg_color="#1e3a8a")
            else:
                self.btn_mode_badge.configure(text="⌨️ Digitazione IT", fg_color="#065f46")

    def _toggle_quick_input_mode(self):
        current = self.user_data.get("input_mode", "clipboard")
        new_mode = "typing" if current == "clipboard" else "clipboard"
        self.user_data["input_mode"] = new_mode
        self.save_user_data()
        self.injector.input_mode = new_mode
        self._update_mode_badge(new_mode)
        label = "Incolla Rapido (Ctrl+V)" if new_mode == "clipboard" else "Digitazione Hardware (Layout IT)"
        self.show_toast(f"⚡ Modalità cambiata a: {label}")
        if hasattr(self, 'cmb_mode'):
            self.cmb_mode.set(
                "Incolla Rapido (Ctrl+V) [Consigliato]" if new_mode == "clipboard" else "Digitazione Hardware (Layout IT)"
            )

    def _on_input_mode_change(self, choice):
        if "Ctrl+V" in choice or "Incolla" in choice:
            mode = "clipboard"
        elif "Lenta" in choice:
            mode = "slow"
            self.injector.char_hold = 0.050
            self.injector.char_delay = 0.035
        else:
            mode = "typing"
            self.injector.char_hold = 0.035
            self.injector.char_delay = 0.020
        self.user_data["input_mode"] = mode
        self.save_user_data()
        self.injector.input_mode = mode
        self._update_mode_badge(mode)
        self.show_toast(f"Modalità inserimento: {choice}")

    def _on_enable_console_click(self):
        ok, msg = self.game_cfg.enable_console()
        if ok:
            messagebox.showinfo("Configurazione Console", msg)
            self._render_settings_view()
        else:
            messagebox.showerror("Errore", msg)

    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._refresh_items_list()
            self.items_scroll._parent_canvas.yview_moveto(0)

    def _next_page(self):
        total_pages = (len(self.filtered_items) + self.items_per_page - 1) // self.items_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self._refresh_items_list()
            self.items_scroll._parent_canvas.yview_moveto(0)

    def send_command_to_game(self, command):
        """
        Esegue l'automazione completa: porta il gioco in primo piano, apre la console,
        digita il comando, preme Enter, e la richiude.
        """
        auto_close = self.user_data.get("auto_close_console", True)
        
        # Esegui in un thread separato per evitare blocchi dell'interfaccia grafica
        def status_cb(msg):
            self.after(0, lambda: self.show_toast(msg))

        def run_injection():
            success, msg = self.injector.execute_command(
                command, auto_close=auto_close, status_callback=status_cb
            )
            # Torna al thread UI
            self.after(0, lambda: self._handle_injection_result(command, success, msg))

        threading.Thread(target=run_injection, daemon=True).start()

    def _handle_injection_result(self, command, success, msg):
        if success:
            self.show_toast(f"✅ Inviato: {command}")
            # Salva nella cronologia
            history = self.user_data.get("history", [])
            t_str = time.strftime("%H:%M:%S")
            history.append({"command": command, "time": t_str})
            if len(history) > 100:
                history = history[-100:]
            self.user_data["history"] = history
            self.save_user_data()
        else:
            self.show_toast(f"⚠️ {msg}", is_error=True)

    def show_toast(self, message, is_error=False):
        if self.toast_job:
            self.after_cancel(self.toast_job)
        
        color = "#f87171" if is_error else "#34d399"
        self.lbl_toast.configure(text=message, text_color=color)
        
        # Ripristina testo dopo 4 secondi
        def reset_toast():
            self.lbl_toast.configure(
                text="Pronto. Scegli un oggetto o comando e premi 'Invia al Gioco'.",
                text_color="#9ca3af"
            )
        self.toast_job = self.after(4000, reset_toast)

    def _clear_history(self):
        self.user_data["history"] = []
        self.save_user_data()
        self._refresh_items_list()
        self.show_toast("Cronologia cancellata.")

    def _check_game_status_loop(self):
        is_running = self.game_cfg.is_game_running()
        if is_running:
            self.status_badge.configure(
                text="● The Witcher 3 In Esecuzione",
                fg_color="#065f46", text_color="#a7f3d0"
            )
        else:
            self.status_badge.configure(
                text="● In Attesa di The Witcher 3",
                fg_color="#2b313d", text_color="#9ca3af"
            )
        # Ricontrolla tra 2.5 secondi
        self.after(2500, self._check_game_status_loop)

    def _on_closing(self):
        self.hotkey_mgr.stop()
        self.destroy()

if __name__ == "__main__":
    app = WitcherApp()
    app.mainloop()
