import os
import ctypes
from ctypes import wintypes
import time

user32 = ctypes.WinDLL('user32', use_last_error=True)
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

# Definizioni Win32
SW_RESTORE = 9
SW_SHOW = 5

VK_SHIFT = 0x10
SCANCODE_SHIFT = 0x2A

VK_CONTROL = 0x11
SCANCODE_CONTROL = 0x1D

VK_MENU = 0x12       # Alt
SCANCODE_MENU = 0x38

VK_RETURN = 0x0D
SCANCODE_RETURN = 0x1C

VK_ESCAPE = 0x1B
SCANCODE_ESCAPE = 0x01

VK_BACK = 0x08
SCANCODE_BACK = 0x0E

VK_OEM_3 = 0xC0      # Tilde / Grave su tastiere US
VK_OEM_5 = 0xDC      # Tasto '\' su tastiere Italiane
SCANCODE_TILDE = 0x29 # Scancode hardware per il tasto sotto ESC (41)

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_SCANCODE = 0x0008

INPUT_KEYBOARD = 1

# 64-bit safe Win32 API setup
kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalLock.restype = ctypes.c_void_p
kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalUnlock.restype = wintypes.BOOL

user32.OpenClipboard.argtypes = [wintypes.HWND]
user32.OpenClipboard.restype = wintypes.BOOL
user32.EmptyClipboard.argtypes = []
user32.EmptyClipboard.restype = wintypes.BOOL
user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
user32.SetClipboardData.restype = wintypes.HANDLE
user32.CloseClipboard.argtypes = []
user32.CloseClipboard.restype = wintypes.BOOL

user32.VkKeyScanW.argtypes = [wintypes.WCHAR]
user32.VkKeyScanW.restype = wintypes.SHORT
user32.MapVirtualKeyW.argtypes = [wintypes.UINT, wintypes.UINT]
user32.MapVirtualKeyW.restype = wintypes.UINT

class KeyBdInput(ctypes.Structure):
    _fields_ = [
        ('wVk', wintypes.WORD),
        ('wScan', wintypes.WORD),
        ('dwFlags', wintypes.DWORD),
        ('time', wintypes.DWORD),
        ('dwExtraInfo', ctypes.c_void_p)
    ]

class MouseInput(ctypes.Structure):
    _fields_ = [
        ('dx', wintypes.LONG),
        ('dy', wintypes.LONG),
        ('mouseData', wintypes.DWORD),
        ('dwFlags', wintypes.DWORD),
        ('time', wintypes.DWORD),
        ('dwExtraInfo', ctypes.c_void_p)
    ]

class HardwareInput(ctypes.Structure):
    _fields_ = [
        ('uMsg', wintypes.DWORD),
        ('wParamL', wintypes.WORD),
        ('wParamH', wintypes.WORD)
    ]

class Input_I(ctypes.Union):
    _fields_ = [
        ('ki', KeyBdInput),
        ('mi', MouseInput),
        ('hi', HardwareInput)
    ]

class Input(ctypes.Structure):
    _fields_ = [
        ('type', wintypes.DWORD),
        ('ii', Input_I)
    ]

user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(Input), ctypes.c_int]
user32.SendInput.restype = wintypes.UINT


class WitcherInjector:
    def __init__(self, console_key_mode="auto"):
        self.console_key_mode = console_key_mode
        # Parametri temporali ottimali per sincronizzazione RedEngine Next-Gen
        self.animation_delay = 0.40   # Tempo di discesa barra console (400ms)
        self.char_hold = 0.035        # Durata pressione tasto fisico (35ms per frame polling)
        self.char_delay = 0.020       # Pausa tra caratteri (20ms)
        self.close_method = "toggle"  # "toggle" (Tasto console ~ / 0x29) o "escape"
        self.input_mode = "clipboard" # "clipboard" (Predefinito & Veloce), "typing" (Hardware IT)

    def find_game_window(self):
        """Trova la finestra reale del processo witcher3.exe (evitando falsi positivi)."""
        found_hwnd = None
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        
        def enum_proc(hwnd, lParam):
            nonlocal found_hwnd
            if user32.IsWindowVisible(hwnd):
                # Escludi finestre di console o assistente
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buff, length + 1)
                    title = buff.value.lower()
                    if "gwented" in title or "cmd.exe" in title or "powershell" in title:
                        return True

                # 1. Controlla la classe della finestra (RedEngine usa 'The Witcher 3' o 'Witcher3')
                class_buf = ctypes.create_unicode_buffer(256)
                user32.GetClassNameW(hwnd, class_buf, 256)
                cls_name = class_buf.value
                if cls_name in ["The Witcher 3", "Witcher3"]:
                    found_hwnd = hwnd
                    return False

                # 2. Controlla l'eseguibile del processo
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
                                found_hwnd = hwnd
                                kernel32.CloseHandle(h_proc)
                                return False
                        kernel32.CloseHandle(h_proc)

            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(WNDENUMPROC(enum_proc), 0)
        return found_hwnd

    def focus_game(self, hwnd=None):
        if hwnd is None:
            hwnd = self.find_game_window()
        if not hwnd:
            return False

        fg_window = user32.GetForegroundWindow()
        if fg_window == hwnd:
            return True

        fg_thread = user32.GetWindowThreadProcessId(fg_window, None)
        app_thread = kernel32.GetCurrentThreadId()

        if fg_thread != app_thread:
            user32.AttachThreadInput(app_thread, fg_thread, True)

        user32.ShowWindow(hwnd, SW_RESTORE)
        user32.SetForegroundWindow(hwnd)
        user32.SetFocus(hwnd)

        if fg_thread != app_thread:
            user32.AttachThreadInput(app_thread, fg_thread, False)

        time.sleep(0.20)
        return True

    def trigger_console_toggle(self, hwnd=None):
        """Apre/chiude la console inviando lo scancode hardware originale 0x29."""
        user32.keybd_event(VK_OEM_3, SCANCODE_TILDE, 0, 0)
        time.sleep(0.04)
        user32.keybd_event(VK_OEM_3, SCANCODE_TILDE, KEYEVENTF_KEYUP, 0)

    def get_key_layout_info(self, char):
        """
        Rileva i codici virtuali (VK), scancode hardware e tasti modificatori
        in base al layout attivo dell'utente (es. Tastiera Italiana).
        """
        res = user32.VkKeyScanW(char)
        if res == -1:
            return None
        vk = res & 0xFF
        shift_state = (res >> 8) & 0xFF
        scancode = user32.MapVirtualKeyW(vk, 0)
        needs_shift = bool(shift_state & 0x01)
        needs_ctrl = bool(shift_state & 0x02)
        needs_alt = bool(shift_state & 0x04)
        return vk, scancode, needs_shift, needs_ctrl, needs_alt

    def type_char(self, char, prev_char=None):
        """
        Digita un singolo carattere utilizzando la mappatura hardware reale del layout attivo (es. Italiano).
        Include debounce frame per caratteri identici consecutivi e tempi di tenuta Shift stabili.
        """
        info = self.get_key_layout_info(char)
        if not info:
            return

        vk, scancode, needs_shift, needs_ctrl, needs_alt = info

        # Debounce per caratteri identici consecutivi (es. 'dd' in 'additem', '00' in '50000'):
        # In RedEngine / DirectInput, se un tasto viene rilasciato e ripremuto in meno di ~40ms,
        # il motore DirectInput lo campiona come tasto continuo e perde la seconda battuta!
        if prev_char == char:
            time.sleep(0.040)

        # 1. Premi modificatori
        if needs_ctrl:
            user32.keybd_event(VK_CONTROL, SCANCODE_CONTROL, 0, 0)
        if needs_alt:
            user32.keybd_event(VK_MENU, SCANCODE_MENU, 0, 0)
        if needs_shift:
            user32.keybd_event(VK_SHIFT, SCANCODE_SHIFT, 0, 0)
            time.sleep(0.035)  # Trattiene Shift prima di premere il tasto (copre il frame del motore)

        time.sleep(0.010)

        # 2. Premi e rilascia il tasto fisico del carattere
        user32.keybd_event(vk, scancode, 0, 0)
        time.sleep(self.char_hold)
        user32.keybd_event(vk, scancode, KEYEVENTF_KEYUP, 0)
        time.sleep(0.010)

        # 3. Rilascia modificatori
        if needs_shift:
            time.sleep(0.025)  # Trattiene Shift dopo il rilascio per evitare disallineamento tick
            user32.keybd_event(VK_SHIFT, SCANCODE_SHIFT, KEYEVENTF_KEYUP, 0)
        if needs_alt:
            user32.keybd_event(VK_MENU, SCANCODE_MENU, KEYEVENTF_KEYUP, 0)
        if needs_ctrl:
            user32.keybd_event(VK_CONTROL, SCANCODE_CONTROL, KEYEVENTF_KEYUP, 0)

        time.sleep(self.char_delay)

    def type_text(self, text):
        """Digita una stringa intera carattere per carattere con gestione layout e debounce."""
        prev = None
        for ch in text:
            self.type_char(ch, prev)
            prev = ch

    def paste_clipboard(self):
        """Invia la combinazione Ctrl + V con rilascio preventivo dei modificatori."""
        # Rilascia modificatori eventualmente premuti
        user32.keybd_event(VK_SHIFT, SCANCODE_SHIFT, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_MENU, SCANCODE_MENU, KEYEVENTF_KEYUP, 0)
        time.sleep(0.02)

        # Invia Ctrl + V
        user32.keybd_event(VK_CONTROL, SCANCODE_CONTROL, 0, 0)
        time.sleep(0.04)
        user32.keybd_event(0x56, 0x2F, 0, 0) # Key 'V' (Scancode 0x2F)
        time.sleep(0.04)
        user32.keybd_event(0x56, 0x2F, KEYEVENTF_KEYUP, 0)
        time.sleep(0.03)
        user32.keybd_event(VK_CONTROL, SCANCODE_CONTROL, KEYEVENTF_KEYUP, 0)
        time.sleep(0.08)

    def send_enter(self):
        """Invia Invio al gioco assicurandosi che Shift sia rilasciato."""
        user32.keybd_event(VK_SHIFT, SCANCODE_SHIFT, KEYEVENTF_KEYUP, 0)
        time.sleep(0.03)
        user32.keybd_event(VK_RETURN, SCANCODE_RETURN, 0, 0)
        time.sleep(0.05)
        user32.keybd_event(VK_RETURN, SCANCODE_RETURN, KEYEVENTF_KEYUP, 0)

    def send_escape(self):
        """Invia ESC al gioco per chiudere la console."""
        user32.keybd_event(VK_SHIFT, SCANCODE_SHIFT, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_CONTROL, SCANCODE_CONTROL, KEYEVENTF_KEYUP, 0)
        time.sleep(0.02)
        user32.keybd_event(VK_ESCAPE, SCANCODE_ESCAPE, 0, 0)
        time.sleep(0.05)
        user32.keybd_event(VK_ESCAPE, SCANCODE_ESCAPE, KEYEVENTF_KEYUP, 0)

    def clear_console_input(self):
        """Pulisce la barra della console con Backspace."""
        for _ in range(3):
            user32.keybd_event(VK_BACK, SCANCODE_BACK, 0, 0)
            time.sleep(0.025)
            user32.keybd_event(VK_BACK, SCANCODE_BACK, KEYEVENTF_KEYUP, 0)
            time.sleep(0.020)

    def set_clipboard_text(self, text):
        """Imposta il testo negli appunti di Windows via Win32 API in modo 64-bit safe."""
        try:
            GMEM_MOVEABLE = 0x0002
            CF_UNICODETEXT = 13
            if user32.OpenClipboard(None):
                user32.EmptyClipboard()
                text_bytes = (text + '\0').encode('utf-16le')
                h_mem = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(text_bytes))
                if h_mem:
                    p_mem = kernel32.GlobalLock(h_mem)
                    if p_mem:
                        ctypes.memmove(p_mem, text_bytes, len(text_bytes))
                        kernel32.GlobalUnlock(h_mem)
                        user32.SetClipboardData(CF_UNICODETEXT, h_mem)
                user32.CloseClipboard()
                return True
        except Exception as e:
            print(f"Errore set_clipboard_text: {e}")
        return False

    def execute_command(self, command, auto_close=True, status_callback=None):
        """
        Esegue la sequenza completa e automatica ("fa tutto da sola"):
        1. Porta The Witcher 3 in primo piano
        2. Invia il segnale per aprire la console
        3. Attende il completamento dell'animazione di discesa della console (400ms)
        4. Pulisce la barra da eventuali caratteri residui
        5. Copia negli appunti (per backup e modalità clipboard)
        6. Inserisce il comando (tramite Incolla Rapido Ctrl+V o digitazione layout IT)
        7. Invia Invio per eseguire il comando
        8. Attende l'elaborazione del gioco
        9. Richiude la console con ESC
        """
        hwnd = self.find_game_window()
        if not hwnd:
            return False, "Finestra di The Witcher 3 non trovata. Avvia prima il gioco!"

        # Copia sempre negli appunti per comodità e backup
        self.set_clipboard_text(command)

        if status_callback:
            status_callback("Porto The Witcher 3 in primo piano...")
        if not self.focus_game(hwnd):
            return False, "Impossibile portare The Witcher 3 in primo piano."

        time.sleep(0.20)

        # 1. Apri console
        if status_callback:
            status_callback("Apro la console in gioco...")
        self.trigger_console_toggle(hwnd)

        # 2. Attendi discesa animazione console (fondamentale per RedEngine)
        time.sleep(self.animation_delay)

        # 3. Pulisci la riga di input
        self.clear_console_input()
        time.sleep(0.06)

        # 4. Inserimento comando
        if self.input_mode == "clipboard":
            if status_callback:
                status_callback(f"Incollo comando rapido (Ctrl+V): {command}...")
            self.paste_clipboard()
        else:
            if status_callback:
                status_callback(f"Digitazione hardware (Layout IT): {command}...")
            self.type_text(command)

        # Pausa cruciale per assicurare che RedEngine registri l'input prima di Invio
        time.sleep(0.20)

        # 5. Invia Invio
        if status_callback:
            status_callback("Esecuzione comando (Invio)...")
        self.send_enter()
        time.sleep(0.35)

        # 6. Chiudi console
        if auto_close:
            if status_callback:
                status_callback("Chiusura console...")
            self.close_console(hwnd)

        return True, f"Comando '{command}' eseguito con successo in The Witcher 3!"

    def close_console(self, hwnd=None):
        """
        Chiude la console inviando il segnale hardware originale (scancode 0x29).
        In The Witcher 3, la console è un comando toggle legato al tasto console (~).
        """
        time.sleep(0.08)
        # Assicura il rilascio preventivo di tutti i modificatori
        user32.keybd_event(VK_SHIFT, SCANCODE_SHIFT, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_CONTROL, SCANCODE_CONTROL, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_MENU, SCANCODE_MENU, KEYEVENTF_KEYUP, 0)
        time.sleep(0.03)

        if self.close_method == "escape":
            self.send_escape()
        else:
            self.trigger_console_toggle(hwnd)
        time.sleep(0.12)

    def toggle_console(self):
        """Apre o chiude la console in gioco."""
        hwnd = self.find_game_window()
        if not hwnd:
            return False, "The Witcher 3 non è in esecuzione."
        self.focus_game(hwnd)
        time.sleep(0.15)
        self.trigger_console_toggle(hwnd)
        return True, "Segnale console inviato al gioco!"

    def give_all_gwent_cards(self, cards_list, count=4, status_callback=None):
        """
        Inietta tutte le carte Gwent nel gioco moltiplicate per count (es. 4x).
        Apre la console una volta sola, inietta rapidamente i comandi in serie,
        e infine richiude la console automaticamente.
        """
        hwnd = self.find_game_window()
        if not hwnd:
            return False, "Finestra di The Witcher 3 non trovata. Avvia prima il gioco!"

        if status_callback:
            status_callback("Porto The Witcher 3 in primo piano...")
        if not self.focus_game(hwnd):
            return False, "Impossibile portare The Witcher 3 in primo piano."

        time.sleep(0.20)

        # 1. Apri console
        if status_callback:
            status_callback(f"Apro la console per iniezione mazzo Gwent {count}x...")
        self.trigger_console_toggle(hwnd)
        time.sleep(self.animation_delay)
        self.clear_console_input()
        time.sleep(0.06)

        total = len(cards_list)
        # 2. Ciclo di iniezione veloce per tutte le carte
        for idx, card in enumerate(cards_list, 1):
            code = card.get("code")
            name_it = card.get("name_it", card.get("name", code))
            cmd = f"additem('{code}', {count})"

            if status_callback:
                status_callback(f"Gwent {count}x [{idx}/{total}]: {name_it}...")

            # Copia e incolla negli appunti
            self.set_clipboard_text(cmd)
            self.paste_clipboard()
            time.sleep(0.03)
            self.send_enter()
            time.sleep(0.04)

        # 3. Pausa finale e chiusura console
        time.sleep(0.25)
        if status_callback:
            status_callback("Chiusura console...")
        self.close_console(hwnd)

        return True, f"Tutte le {total} carte di Gwent aggiunte con successo in {count}x (Totale: {total * count} carte)!"
