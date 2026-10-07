import ctypes
from ctypes import wintypes
import threading
import time

user32 = ctypes.WinDLL('user32', use_last_error=True)

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000
WM_HOTKEY = 0x0312

VK_MAPPING = {
    "F1": 0x70,
    "F2": 0x71,
    "F3": 0x72,
    "F4": 0x73,
    "F5": 0x74,
    "F6": 0x75,
    "F7": 0x76,
    "F8": 0x77,
    "F9": 0x78,
    "F10": 0x79,
    "F11": 0x7A,
    "F12": 0x7B,
    "Backslash (\\)": 0xDC,
    "Insert": 0x2D,
    "Home": 0x24,
    "End": 0x23,
    "Pause": 0x13
}

class GlobalHotkeyManager:
    def __init__(self, on_hotkey_callback, hotkey_name="F2"):
        self.on_hotkey_callback = on_hotkey_callback
        self.hotkey_name = hotkey_name
        self.thread = None
        self.running = False
        self.hotkey_id = 1001

    def set_hotkey(self, name):
        was_running = self.running
        if was_running:
            self.stop()
        self.hotkey_name = name
        if was_running:
            self.start()

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()

    def stop(self):
        if not self.running:
            return
        self.running = False
        if self.thread and self.thread.is_alive():
            # Invia messaggio WM_QUIT al thread per svegliare GetMessage
            # (oppure il thread daemon terminerà in sicurezza)
            pass

    def _listen_loop(self):
        vk = VK_MAPPING.get(self.hotkey_name, 0x71)
        res = user32.RegisterHotKey(None, self.hotkey_id, MOD_NOREPEAT, vk)
        if not res:
            # Se fallisce la registrazione con MOD_NOREPEAT, prova senza
            user32.RegisterHotKey(None, self.hotkey_id, 0, vk)

        msg = wintypes.MSG()
        while self.running:
            # PeekMessage per permettere l'uscita pulita senza bloccare per sempre
            if user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1): # PM_REMOVE = 1
                if msg.message == WM_HOTKEY and msg.wParam == self.hotkey_id:
                    try:
                        self.on_hotkey_callback()
                    except Exception as e:
                        print(f"Errore callback hotkey: {e}")
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
            else:
                time.sleep(0.02)

        try:
            user32.UnregisterHotKey(None, self.hotkey_id)
        except Exception:
            pass
