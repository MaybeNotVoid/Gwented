import os
import winreg
import configparser
import ctypes
from ctypes import wintypes

class WitcherGameConfig:
    KNOWN_STEAM_PATHS = [
        r"C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3",
        r"C:\Program Files\Steam\steamapps\common\The Witcher 3",
        r"D:\SteamLibrary\steamapps\common\The Witcher 3",
        r"E:\SteamLibrary\steamapps\common\The Witcher 3",
        r"F:\SteamLibrary\steamapps\common\The Witcher 3",
        r"G:\SteamLibrary\steamapps\common\The Witcher 3"
    ]
    
    KNOWN_GOG_PATHS = [
        r"C:\GOG Games\The Witcher 3 Wild Hunt",
        r"D:\GOG Games\The Witcher 3 Wild Hunt",
        r"C:\Program Files (x86)\GOG Galaxy\Games\The Witcher 3 Wild Hunt"
    ]

    def __init__(self, custom_path=None):
        self.game_path = custom_path or self.detect_game_path()
        self.documents_path = os.path.expanduser(r"~\Documents\The Witcher 3")

    def detect_game_path(self):
        # 1. Prova percorsi Steam noti
        for p in self.KNOWN_STEAM_PATHS:
            if os.path.exists(os.path.join(p, "bin", "x64", "witcher3.exe")) or \
               os.path.exists(os.path.join(p, "bin", "x64_dx12", "witcher3.exe")) or \
               os.path.exists(os.path.join(p, "bin", "config", "base", "general.ini")):
                return p

        # 2. Prova percorsi GOG noti
        for p in self.KNOWN_GOG_PATHS:
            if os.path.exists(os.path.join(p, "bin", "config", "base", "general.ini")):
                return p

        # 3. Prova tramite Registro Windows
        for key_root in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
            for sub in [
                r"SOFTWARE\GOG.com\Games\1207664643",
                r"SOFTWARE\GOG.com\Games\1495134320",
                r"SOFTWARE\WOW6432Node\GOG.com\Games\1207664643",
                r"SOFTWARE\WOW6432Node\GOG.com\Games\1495134320"
            ]:
                try:
                    with winreg.OpenKey(key_root, sub) as key:
                        path, _ = winreg.QueryValueEx(key, "PATH")
                        if path and os.path.exists(path):
                            return path
                except Exception:
                    pass

        return None

    def get_general_ini_path(self):
        if not self.game_path:
            return None
        return os.path.join(self.game_path, "bin", "config", "base", "general.ini")

    def is_console_enabled(self):
        ini_path = self.get_general_ini_path()
        if not ini_path or not os.path.exists(ini_path):
            return False, "File general.ini non trovato"
        
        try:
            with open(ini_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            if "DBGConsoleOn=true" in content:
                return True, "Console attiva in general.ini"
            return False, "DBGConsoleOn=true assente in general.ini"
        except Exception as e:
            return False, f"Errore lettura: {e}"

    def enable_console(self):
        ini_path = self.get_general_ini_path()
        if not ini_path:
            return False, "Cartella di The Witcher 3 non trovata"
        
        if not os.path.exists(ini_path):
            # Prova a creare la directory se non esiste
            os.makedirs(os.path.dirname(ini_path), exist_ok=True)
            with open(ini_path, "w", encoding="utf-8") as f:
                f.write("[General]\nConfigVersion=7\nDBGConsoleOn=true\n")
            return True, "File general.ini creato con successo con DBGConsoleOn=true"

        try:
            # Backup
            bak_path = ini_path + ".bak"
            with open(ini_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            with open(bak_path, "w", encoding="utf-8") as f:
                f.write(content)

            lines = content.splitlines()
            new_lines = []
            has_general = False
            dbg_added = False

            for line in lines:
                stripped = line.strip()
                if stripped.lower() == "[general]":
                    has_general = True
                    new_lines.append(line)
                    if not dbg_added:
                        new_lines.append("DBGConsoleOn=true")
                        dbg_added = True
                    continue
                if stripped.lower().startswith("dbgconsoleon"):
                    continue
                new_lines.append(line)

            if not has_general:
                new_lines.insert(0, "[General]\nDBGConsoleOn=true")

            with open(ini_path, "w", encoding="utf-8") as f:
                f.write("\n".join(new_lines) + "\n")

            # Opzionale: per Next-Gen aggiorna anche dx12user.settings se presente in Documenti
            if os.path.exists(self.documents_path):
                for fname in ["dx12user.settings", "user.settings"]:
                    doc_cfg = os.path.join(self.documents_path, fname)
                    if os.path.exists(doc_cfg):
                        try:
                            with open(doc_cfg, "r", encoding="utf-8", errors="ignore") as df:
                                d_content = df.read()
                            if "DBGConsoleOn" not in d_content:
                                with open(doc_cfg, "a", encoding="utf-8") as df:
                                    df.write("\n[General]\nDBGConsoleOn=true\n")
                        except Exception:
                            pass

            return True, "Console abilitata con successo (general.ini aggiornato)"
        except Exception as e:
            return False, f"Impossibile modificare general.ini: {e}"

    def is_game_running(self):
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        found = False
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

        def enum_proc(hwnd, lParam):
            nonlocal found
            if user32.IsWindowVisible(hwnd):
                # Controlla classe finestra
                class_buf = ctypes.create_unicode_buffer(256)
                user32.GetClassNameW(hwnd, class_buf, 256)
                if class_buf.value in ["The Witcher 3", "Witcher3"]:
                    found = True
                    return False

                # Controlla eseguibile processo
                pid = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                if pid.value != 0:
                    h_proc = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
                    if h_proc:
                        buf = ctypes.create_unicode_buffer(1024)
                        size = wintypes.DWORD(1024)
                        if kernel32.QueryFullProcessImageNameW(h_proc, 0, buf, ctypes.byref(size)):
                            exe = os.path.basename(buf.value).lower()
                            if exe == "witcher3.exe":
                                found = True
                                kernel32.CloseHandle(h_proc)
                                return False
                        kernel32.CloseHandle(h_proc)
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(WNDENUMPROC(enum_proc), 0)
        return found
