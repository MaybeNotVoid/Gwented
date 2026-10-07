# 🐺 Gwented - The Witcher 3 Console Assistant & Spawn Master

<p align="center">
  <img src="https://img.shields.io/badge/The_Witcher_3-Next--Gen_%26_Classic-blue?style=for-the-badge&logo=gogdotcom" alt="The Witcher 3" />
  <img src="https://img.shields.io/badge/Platform-Windows_10_%2F_11-0078D6?style=for-the-badge&logo=windows" alt="Platform Windows" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python" alt="Python Version" />
  <img src="https://img.shields.io/badge/UI-CustomTkinter-blueviolet?style=for-the-badge" alt="CustomTkinter" />
  <img src="https://img.shields.io/badge/Layout-Italian_Keyboard_Fix-green?style=for-the-badge" alt="Italian Keyboard Fix" />
</p>

---

## 📖 Panoramica

**Gwented** è un'applicazione desktop per **The Witcher 3: Wild Hunt**, creata appositamente per:
1. **Risolvere definitivamente l'apertura della console di debug sulle tastiere con layout italiano** (dove il tasto tilde `~` non esiste fisicamente).
2. Offrire un'interfaccia moderna in Dark Mode per sfogliare, cercare e **spawnare automaticamente con 1 click** qualsiasi oggetto, arma, armatura, pozione, abilità o carta di Gwent, con selezione della quantità ("fa tutto da sola").
3. Fornire la **traduzione completa in italiano** di oltre **2.500 oggetti e comandi** in corrispondenza con i nomi effettivi in-game.
4. Offrire una funzione dedicata per ottenere **tutte le 173 carte di Gwent in quadruplice copia (4x)** per comporre qualsiasi mazzo al massimo potenziale.

---

## 🎯 Il Problema della Tastiera Italiana in The Witcher 3

Nel motore di gioco di *The Witcher 3* (RedEngine), la console di debug ufficiale si apre tramite il tasto tilde (`~` o scancode hardware `0x29`).
Sulle **tastiere con layout italiano**:
* Il tasto fisico sotto `ESC` corrisponde a `\` e `|` (`VK_OEM_5` / `0xDC`), che il motore di gioco non riconosce come comando di apertura console.
* Le combinazioni `AltGr + ì` o `Alt + 126` inviano sequenze di composizione o codici ASCII che il gioco ignora completamente.
* Spesso, tentando di digitare codici complessi con parentesi `()`, apici `'` o trattini bassi `_`, il gioco scambia i caratteri o perde battute a causa del campionamento a 60 FPS di DirectInput.

### 💡 Come Gwented Risolve il Problema
* **Iniezione Hardware Diretta**: Gwented invia direttamente lo scancode hardware originale `0x29` e il virtual-key `VK_OEM_3`, aprendo la console all'istante su qualsiasi tastiera italiana senza dover cambiare lingua in Windows.
* **Tasto Rapido In-Gioco (F2)**: Mentre giochi a schermo intero o in finestra, premi **F2** per aprire e chiudere la console senza mai dover uscire dal gioco.
* **Chiusura Automatica Garantita**: La console viene chiusa in automatico subito dopo l'esecuzione del comando inviando il segnale toggle hardware corretto.

---

## ✨ Funzionalità Principali

### ⚡ 1. Automazione 1-Click ("Fa tutto da sola")
Basta scegliere l'oggetto o il trucco desiderato e cliccare **"⚡ Invia al Gioco"**:
1. Porta *The Witcher 3* in primo piano (`SetForegroundWindow`).
2. Apre la console con il segnale virtuale hardware.
3. Attende il completamento dell'animazione di discesa della barra (400 ms).
4. Pulisce la barra da eventuali caratteri residui.
5. Inserisce il comando con parametri e quantità esatte.
6. Invia `Invio` per eseguire il comando.
7. Richiude automaticamente la console di gioco!

### 📋 2. Doppio Motore d'Inserimento (Dual-Engine)
* **Incolla Rapido (`Ctrl + V`) [Consigliato & Predefinito]**: Inserisce il comando negli appunti di Windows a 64-bit e lo incolla all'istante (<50 ms). Zero caratteri persi, parentesi e apici sempre perfetti.
* **Digitazione Hardware (Layout IT)**: Motore di digitazione fisica riscritto con mappatura reale del layout italiano (`Shift + 8` per `(`, `Shift + 9` per `)`, ecc.), pausa di debounce (40 ms) per lettere doppie (es. `additem`) e tenuta di Shift a 35 ms per sincronizzazione frame a 60 FPS.
* **Selettore Rapido 1-Click**: Pulsante nell'header per passare istantaneamente tra le due modalità.

### 🃏 3. Mazzo Completo Gwent in 4x (692 Carte)
* Il comando classico `addgwintcards` fornisce solo 1 copia per carta, impedendo di sfruttare le abilità moltiplicatrici di *Legame Stretto*, le spie duplicate e i medici.
* Con il pulsante **`⚡ Gwent All 4x`**, Gwented inietta in serie **4 copie di ciascuna delle 173 carte** di gioco (totale **692 carte**) con contatore live a schermo e chiusura finale automatica.

### 🔍 4. Ricerca Ultra-Veloce Indicizzata (<5 ms)
* **Indice in memoria (`search_blob`)**: Oltre 2.500 elementi pre-indicizzati in memoria per ricerche istantanee senza alcun freeze.
* **Debounce intelligente (140 ms)**: Elimina i lag durante la digitazione.
* Cerca indifferentemente per **nome italiano** (*"orso"*, *"rondine"*, *"mitraglia"*), **nome originale inglese** (*"bear"*, *"swallow"*, *"grapeshot"*) o **codice console** (*"gwint_card_"*, *"addmoney"*).

### 🇮🇹 5. Traduzione Completa degli Oggetti In-Game
Tutti gli elementi del database sono associati ai loro corrispettivi ufficiali in italiano:
* **Armature Witcher**: Set Orso, Gatto, Grifone, Lupo, Vipera, Manticora in tutti i gradi (*Base*, *Migliorata*, *Superiore*, *Perfetta*, *Gran Maestro*) e pezzi (*Armatura*, *Guanti*, *Pantaloni*, *Stivali*).
* **Armi & Spade**: Spade d'argento, spade d'acciaio, armi reliquia (*Aerondight*, *Iris*, *Lama d'Inverno*, *Unicorno Nero*, *Lama dei Rifiuti*), balestre e scudi.
* **Pozioni & Decotti**: *Rondine*, *Tuono*, *Sangue Nero*, *Bora*, *Gatto*, *Filtro di Petri*, *Gufo Reale*, *Decotto di Raffard*, ecc.
* **Bombe**: *Mitraglia*, *Stella Danzante*, *Vento del Nord*, *Polvere di Luna*, *Sogno del Drago*, *Fungo del Diavolo*, *Samum*, *Dimeritium*.
* **Rune & Glifi**: *Chernobog*, *Dazhbog*, *Devana*, *Veles*, *Perun*, *Glifi dei Segni (Quen, Igni, Aard, Axii, Yrden)*, bisacce e selle per Ravelo.
* **Abilità & Talenti**: Nomi ufficiali in italiano (*Memoria Muscolare*, *Vortice*, *Scudo Attivo Quen*, *Flusso di Fuoco*, *Tolleranza Acquisita*, ecc.).

### 🔧 6. Rilevamento e Configurazione 1-Click di `general.ini`
L'app rileva automaticamente il percorso di installazione di The Witcher 3 (Steam o GOG) e controlla lo stato di `DBGConsoleOn=true`. Se la console non è ancora attiva, basta un click sul pulsante **"🔧 Abilita Console"** per configurare il file in automatico.

---

## 📊 Database dei Codici Incluso

| Categoria | N. Elementi | Descrizione |
|---|---|---|
| **🃏 Carte Gwent** | 173 | Eroi, spie, medici, meteo, leader con nomi leggibili e supporto 4x. |
| **⚔️ Armi & Spade** | 298 | Spade da witcher (argento e acciaio), armi reliquia, balestre e scudi. |
| **🛡️ Armature & Equip.** | 94 | Set completi delle scuole Witcher da Base a Gran Maestro. |
| **🧪 Pozioni & Decotti** | 44 | Tutte le pozioni e i decotti di alchimia. |
| **💣 Bombe** | 34 | Bombe standard, migliorate e superiori. |
| **💎 Rune & Glifi** | 102 | Potenziamenti per armi, armature e finimenti per cavallo. |
| **📜 Schemi di Creazione** | 252 | Diagrammi per fabbri e armaioli. |
| **📦 Materiali & Vari** | 442 | Lingotti, minerali, pelli, polveri e kit di riparazione. |
| **🔑 Oggetti di Missione** | 458 | Chiavi, documenti e manufatti di trama. |
| **📖 Libri & Lettere** | 257 | Bestiari e testi storici. |
| **👾 Mostri (Spawn)** | 223 | Creatura o boss evocabile direttamente nel mondo di gioco. |
| **🐺 Animali (Spawn)** | 31 | Fauna selvatica e domestica. |
| **🧙‍♂️ Personaggi (Spawn)** | 9 | NPC e compagni (Ciri, Triss, Yennefer, Vesemir, Zoltan). |
| **⚡ Abilità & Talenti** | 78 | Sblocco istantaneo di abilità e talenti (`learnskill`). |
| **⭐ Trucchi Rapidi** | 26 | God Mode, Salute piena (`healme`), +50k Corone, Viaggi rapidi, Meteo, ecc. |

---

## 🛠️ Requisiti di Sistema

* **Sistema Operativo**: Windows 10 o Windows 11 (64-bit)
* **Gioco**: *The Witcher 3: Wild Hunt* (Next-Gen v4.00+ DX11/DX12 oppure Classic v1.32, versioni Steam / GOG / Epic)
* **Python**: 3.10 o superiore

---

## 🚀 Installazione e Avvio

### 1. Clona o Scarica la Repository
```bash
git clone https://github.com/MaybeNotVoid/Gwented.git
cd Gwented
```

### 2. Installa le Dipendenze
```bash
pip install -r requirements.txt
```

### 3. Avvia l'Applicazione
È possibile avviare l'app in due modi:
* **Metodo Rapido**: Doppio click sul file **`Avvia_Gwented.bat`**
* **Da Terminale**:
  ```bash
  python run_app.py
  ```

---

## 🎮 Guida all'Utilizzo

1. **Avvia The Witcher 3** ed entra in partita (o nel menu).
2. **Avvia Gwented**. La barra di stato nell'angolo in alto a destra mostrerà `● The Witcher 3 In Esecuzione`.
3. **Cerca o Seleziona**:
   * Sfoglia le categorie nella barra laterale a sinistra.
   * Oppure usa la casella di ricerca in alto (es. digita *"orso"*, *"aerondight"*, *"rondine"*).
4. **Regola la Quantità**: Usa i pulsanti `+` / `-` sulla card dell'oggetto.
5. **Invia**: Clicca su **"⚡ Invia al Gioco"**.
   * L'app porterà automaticamente The Witcher 3 in primo piano, aprirà la console, inserirà il comando, lo eseguirà e richiuderà la console!
6. **Mazzo Gwent 4x**:
   * Clicca sul pulsante **`⚡ Gwent All 4x`** nella barra rapida in alto o nel banner della categoria Carte Gwent per ricevere tutte le 173 carte in quadruplice copia.
7. **Tasto Rapido In-Gioco (F2)**:
   * Mentre giochi a The Witcher 3, premi **F2** in qualsiasi momento per aprire o chiudere la console manualmente.

---

## 📂 Struttura del Progetto

```text
Gwented/
│
├── core/                       # Motore Win32 e logica di iniezione
│   ├── game_config.py          # Rilevamento installazione e gestione general.ini
│   ├── hotkey.py               # Manager per il tasto rapido globale F2
│   └── injector.py             # Focus gioco, gestione console, Ctrl+V, DirectInput e Gwent 4x
│
├── data/                       # Dati e configurazioni utente
│   ├── database.json           # Database di 2.522 oggetti con traduzioni italiane e search_blob
│   └── user_data.json          # Preferenze utente, preferiti e cronologia
│
├── gui/                        # Interfaccia grafica CustomTkinter
│   ├── app.py                  # Finestra principale, ricerca indicizzata, paginazione e sidebar
│   └── components.py           # Componenti UI (ItemCard, CheatCard, QuantityStepper)
│
├── scripts/                    # Script di utilità
│   └── enrich_translations.py  # Generatore di traduzioni e indici di ricerca
│
├── Avvia_Gwented.bat           # Launcher rapido per Windows
├── run_app.py                  # Entry point Python
├── requirements.txt            # Dipendenze Python
└── README.md                   # Documentazione completa
```

---

## 📜 Licenza e Note Legali

Questo progetto è distribuito sotto licenza **MIT**.
*The Witcher 3: Wild Hunt* è un marchio registrato di **CD PROJEKT RED**. Questo software è uno strumento non ufficiale creato per la community di giocatori a scopo di modding e accessibilità.
