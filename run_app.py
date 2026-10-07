import sys
import os

# Assicura che la directory root del progetto sia nel PYTHONPATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from gui.app import WitcherApp

def main():
    try:
        app = WitcherApp()
        app.mainloop()
    except Exception as e:
        import traceback
        print("Errore durante l'avvio dell'applicazione:")
        traceback.print_exc()
        input("\nPremi Invio per chiudere...")

if __name__ == "__main__":
    main()
