import os
import json
import re
import requests
from bs4 import BeautifulSoup
from collections import defaultdict

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "database.json")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

URLS = {
    'cheats': 'https://www.ign.com/wikis/the-witcher-3-wild-hunt/PC_Console_Commands_and_Cheats_List',
    'items': 'https://www.ign.com/wikis/the-witcher-3-wild-hunt/Item_Spawn_Codes',
    'npcs': 'https://www.ign.com/wikis/the-witcher-3-wild-hunt/Enemy_and_NPC_Spawn_Codes',
    'talents': 'https://www.ign.com/wikis/the-witcher-3-wild-hunt/Talent_Codes'
}

# Traduzioni e nomi leggibili per le carte Gwent
GWENT_NAMES = {
    "gwint_card_albrich": "Albrich (Nilfgaard)",
    "gwint_card_arachas": "Arachas (Mostri)",
    "gwint_card_arachas_behemoth": "Colosso Arachas (Mostri)",
    "gwint_card_arachas2": "Arachas 2 (Mostri)",
    "gwint_card_arachas3": "Arachas 3 (Mostri)",
    "gwint_card_archer_support": "Supporto Arcieri (Nilfgaard)",
    "gwint_card_archer_support2": "Supporto Arcieri 2 (Nilfgaard)",
    "gwint_card_assire": "Assire var Anahid (Nilfgaard)",
    "gwint_card_avallach": "Avallac'h - Elfo Misterioso (Neutrale, Spia, Eroe)",
    "gwint_card_ballista": "Balista (Regni Settentrionali)",
    "gwint_card_ballista2": "Balista 2 (Regni Settentrionali)",
    "gwint_card_barclay": "Barclay Els (Scoia'tael)",
    "gwint_card_black_infantry": "Fanteria Nera degli Arcieri (Nilfgaard)",
    "gwint_card_black_infantry2": "Fanteria Nera degli Arcieri 2 (Nilfgaard)",
    "gwint_card_blue_stripes": "Commando delle Bande Blu (Regni Settentrionali)",
    "gwint_card_blue_stripes2": "Commando delle Bande Blu 2 (Regni Settentrionali)",
    "gwint_card_blue_stripes3": "Commando delle Bande Blu 3 (Regni Settentrionali)",
    "gwint_card_botchling": "Militare / Botchling (Mostri)",
    "gwint_card_brouver": "Brouver Hoog (Scoia'tael)",
    "gwint_card_catapult": "Catapulta (Regni Settentrionali)",
    "gwint_card_catapult2": "Catapulta 2 (Regni Settentrionali)",
    "gwint_card_celaelo": "Celaeno Harpy (Mostri)",
    "gwint_card_ciaran": "Ciaran aep Easnillien (Scoia'tael)",
    "gwint_card_ciri": "Cirilla Fiona Elen Riannon (Neutrale, Eroe, Forza 15)",
    "gwint_card_clear_sky": "Cielo Sereno (Meteo Neutrale)",
    "gwint_card_crinfrid": "Cacciatori di Draghi di Crinfrid (Regni Settentrionali)",
    "gwint_card_crinfrid2": "Cacciatori di Draghi di Crinfrid 2 (Regni Settentrionali)",
    "gwint_card_crinfrid3": "Cacciatori di Draghi di Crinfrid 3 (Regni Settentrionali)",
    "gwint_card_dandelion": "Ranuncolo / Dandelion (Neutrale, Corno del Comandante)",
    "gwint_card_decoy": "Esca / Spaventapasseri (Neutrale)",
    "gwint_card_decoy2": "Esca 2 (Neutrale)",
    "gwint_card_decoy3": "Esca 3 (Neutrale)",
    "gwint_card_dennis": "Dennis Cranmer (Scoia'tael)",
    "gwint_card_dethmold": "Dethmold (Regni Settentrionali)",
    "gwint_card_dijkstra": "Sigismund Dijkstra (Regni Settentrionali, Spia)",
    "gwint_card_draug": "Draug (Mostri, Eroe, Forza 10)",
    "gwint_card_earth_elemental": "Elementale della Terra (Mostri)",
    "gwint_card_elven_skirmisher": "Schermagliatore Elfico (Scoia'tael)",
    "gwint_card_elven_skirmisher2": "Schermagliatore Elfico 2 (Scoia'tael)",
    "gwint_card_elven_skirmisher3": "Schermagliatore Elfico 3 (Scoia'tael)",
    "gwint_card_emhyr_bronze": "Emhyr var Emreis - Sua Maestà Imperiale (Leader Nilfgaard)",
    "gwint_card_emhyr_gold": "Emhyr var Emreis - L'Incessante (Leader Nilfgaard)",
    "gwint_card_emhyr_silver": "Emhyr var Emreis - Imperatore di Nilfgaard (Leader Nilfgaard)",
    "gwint_card_emhyr": "Emhyr var Emreis - La Fiamma Bianca (Leader Nilfgaard)",
    "gwint_card_endrega": "Endriaga (Mostri)",
    "gwint_card_eredin_bronze": "Eredin - Comandante dei Cavalieri Rossi (Leader Mostri)",
    "gwint_card_eredin_gold": "Eredin - Signore di Tir ná Lia (Leader Mostri)",
    "gwint_card_eredin_silver": "Eredin - Distruttore di Mondi (Leader Mostri)",
    "gwint_card_eredin": "Eredin Bréacc Glas - Re della Caccia Selvaggia (Leader Mostri)",
    "gwint_card_esterad": "Esterad Thyssen (Regni Settentrionali, Eroe, Forza 10)",
    "gwint_card_filavandrel": "Filavandrel aep Faeliana (Scoia'tael)",
    "gwint_card_fiend": "Demone / Fiend (Mostri)",
    "gwint_card_fire_elemental": "Elementale del Fuoco (Mostri)",
    "gwint_card_fogling": "Ekimma / Focolare (Mostri)",
    "gwint_card_foltest_bronze": "Foltest - Signore Supremo di Temeria (Leader Regni)",
    "gwint_card_foltest_gold": "Foltest - Il Forgiatore di Acciaio (Leader Regni)",
    "gwint_card_foltest_silver": "Foltest - Comandante del Nord (Leader Regni)",
    "gwint_card_foltest": "Re Foltest - Re di Temeria (Leader Regni)",
    "gwint_card_forktail": "Codarotante / Forktail (Mostri)",
    "gwint_card_francesca_bronze": "Francesca Findabair - Margherita delle Valli (Leader Scoia'tael)",
    "gwint_card_francesca_gold": "Francesca Findabair - La Bellissima (Leader Scoia'tael)",
    "gwint_card_francesca_silver": "Francesca Findabair - Regina di Dol Blathanna (Leader Scoia'tael)",
    "gwint_card_francesca": "Francesca Findabair - Pura Elfa (Leader Scoia'tael)",
    "gwint_card_frightener": "Spaventatore / Frightener (Mostri)",
    "gwint_card_frost": "Gelo Mordente (Meteo Neutrale)",
    "gwint_card_frost2": "Gelo Mordente 2 (Meteo Neutrale)",
    "gwint_card_frost3": "Gelo Mordente 3 (Meteo Neutrale)",
    "gwint_card_gargoyle": "Gargoyle (Mostri)",
    "gwint_card_geralt": "Geralt di Rivia (Neutrale, Eroe, Forza 15)",
    "gwint_card_ghoul": "Ghoul (Mostri)",
    "gwint_card_ghoul2": "Ghoul 2 (Mostri)",
    "gwint_card_ghoul3": "Ghoul 3 (Mostri)",
    "gwint_card_grave_hag": "Strega del Sepolcro (Mostri)",
    "gwint_card_griffin": "Grifone (Mostri)",
    "gwint_card_harpy": "Arpia (Mostri)",
    "gwint_card_havekar_nurse": "Guaritrice Havekar (Scoia'tael, Medico)",
    "gwint_card_havekar_nurse2": "Guaritrice Havekar 2 (Scoia'tael, Medico)",
    "gwint_card_havekar_nurse3": "Guaritrice Havekar 3 (Scoia'tael, Medico)",
    "gwint_card_havekar_support": "Supporto Havekar (Scoia'tael)",
    "gwint_card_havekar_support2": "Supporto Havekar 2 (Scoia'tael)",
    "gwint_card_havekar_support3": "Supporto Havekar 3 (Scoia'tael)",
    "gwint_card_heavy_zerri": "Zerrikaniana da Assedio Pesante (Nilfgaard)",
    "gwint_card_horn": "Corno del Comandante (Neutrale)",
    "gwint_card_horn2": "Corno del Comandante 2 (Neutrale)",
    "gwint_card_horn3": "Corno del Comandante 3 (Neutrale)",
    "gwint_card_ida": "Ida Emean aep Sivney (Scoia'tael)",
    "gwint_card_imlerith": "Imlerith (Mostri, Eroe, Forza 10)",
    "gwint_card_iorveth": "Iorveth (Scoia'tael, Eroe, Forza 10)",
    "gwint_card_isengrim": "Isengrim Faoiltiarna (Scoia'tael, Eroe, Forza 10)",
    "gwint_card_john_natalis": "John Natalis (Regni Settentrionali, Eroe, Forza 10)",
    "gwint_card_kayran": "Kayran (Mostri, Eroe, Forza 8)",
    "gwint_card_leshen": "Leshen / Spirito della Foresta (Mostri, Eroe, Forza 10)",
    "gwint_card_letho": "Letho di Gulet (Nilfgaard, Eroe, Forza 10)",
    "gwint_card_menno": "Menno Coehoorn (Nilfgaard, Eroe, Medico, Forza 10)",
    "gwint_card_milva": "Milva (Scoia'tael, Forza 10)",
    "gwint_card_morvran": "Morvran Voorhis (Nilfgaard, Eroe, Forza 10)",
    "gwint_card_mysterious_elf": "Elfo Misterioso (Neutrale, Spia, Eroe)",
    "gwint_card_nekker": "Nekker (Mostri)",
    "gwint_card_nekker2": "Nekker 2 (Mostri)",
    "gwint_card_nekker3": "Nekker 3 (Mostri)",
    "gwint_card_poor_infantry": "Povera Fanteria (Regni Settentrionali)",
    "gwint_card_poor_infantry2": "Povera Fanteria 2 (Regni Settentrionali)",
    "gwint_card_poor_infantry3": "Povera Fanteria 3 (Regni Settentrionali)",
    "gwint_card_rain": "Pioggia Torrenziale (Meteo Neutrale)",
    "gwint_card_roche": "Vernon Roche (Regni Settentrionali, Eroe, Forza 10)",
    "gwint_card_scorch": "Incenerimento / Scorch (Neutrale)",
    "gwint_card_scorch2": "Incenerimento 2 (Neutrale)",
    "gwint_card_scorch3": "Incenerimento 3 (Neutrale)",
    "gwint_card_shilard": "Shilard Fitz-Oesterlen (Nilfgaard, Spia)",
    "gwint_card_stefan": "Stefan Skellen (Nilfgaard, Spia)",
    "gwint_card_thaler": "Thaler (Regni Settentrionali, Spia)",
    "gwint_card_tibor": "Tibor Eggebracht (Nilfgaard, Eroe, Forza 10)",
    "gwint_card_trebuchet": "Trabucco (Regni Settentrionali)",
    "gwint_card_trebuchet2": "Trabucco 2 (Regni Settentrionali)",
    "gwint_card_triss": "Triss Merigold (Neutrale, Eroe, Forza 7)",
    "gwint_card_ves": "Ves (Regni Settentrionali)",
    "gwint_card_villen": "Villentretenmerth (Neutrale, Forza 7, Scorch)",
    "gwint_card_vattier": "Vattier de Rideaux (Nilfgaard, Spia)",
    "gwint_card_werewolf": "Lupo Mannaro (Mostri)",
    "gwint_card_wyvern": "Viverna (Mostri)",
    "gwint_card_yaevinn": "Yaevinn (Scoia'tael)",
    "gwint_card_yennefer": "Yennefer di Vengerberg (Neutrale, Eroe, Medico, Forza 7)",
    "gwint_card_zoltan": "Zoltan Chivay (Neutrale, Forza 5)"
}

CATEGORY_MAP = {
    "GwentCards": {"name": "Carte Gwent", "icon": "🃏", "cmd_type": "additem"},
    "Weapons": {"name": "Armi & Spade", "icon": "⚔️", "cmd_type": "additem"},
    "Armor": {"name": "Armature & Equip.", "icon": "🛡️", "cmd_type": "additem"},
    "Potions": {"name": "Pozioni & Decotti", "icon": "🧪", "cmd_type": "additem"},
    "Bombs": {"name": "Bombe", "icon": "💣", "cmd_type": "additem"},
    "Upgradesand Runes": {"name": "Rune & Glifi", "icon": "💎", "cmd_type": "additem"},
    "Schematics": {"name": "Schemi di Creazione", "icon": "📜", "cmd_type": "additem"},
    "Books and Notes": {"name": "Libri & Lettere", "icon": "📖", "cmd_type": "additem"},
    "QuestItems": {"name": "Oggetti di Missione", "icon": "🔑", "cmd_type": "additem"},
    "Miscellaneous Items": {"name": "Materiali & Vari", "icon": "📦", "cmd_type": "additem"},
    "Monsters": {"name": "Mostri (Spawn)", "icon": "👾", "cmd_type": "spawn"},
    "Animals": {"name": "Animali (Spawn)", "icon": "🐺", "cmd_type": "spawn"},
    "Characters": {"name": "Personaggi (Spawn)", "icon": "🧙‍♂️", "cmd_type": "spawn"},
    "Miscellaneous": {"name": "Oggetti/Veicoli (Spawn)", "icon": "⛵", "cmd_type": "spawn"},
    "Skills": {"name": "Abilità & Talenti", "icon": "⚡", "cmd_type": "learnskill"}
}

def humanize_name(code):
    if code in GWENT_NAMES:
        return GWENT_NAMES[code]
    name = code
    for prefix in ["gwint_card_", "_quest__"]:
        if name.startswith(prefix):
            name = name[len(prefix):]
    name = name.replace("_", " ").replace("-", " ")
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
    return name.title().strip()

def build_database():
    database = {
        "categories": CATEGORY_MAP,
        "items": [],
        "cheats": []
    }

    # 1. Fetch Cheats
    print("Scaricamento trucchi e comandi...")
    curated_cheats = [
        {"id": "god_mode", "category": "Giocatore", "command": "god", "description": "Attiva/Disattiva invulnerabilità totale (God Mode)", "display_name": "God Mode (Immortalità)", "icon": "🛡️"},
        {"id": "heal_me", "category": "Giocatore", "command": "healme", "description": "Ripristina istantaneamente tutta la barra della salute di Geralt", "display_name": "Salute al Massimo (Heal)", "icon": "❤️"},
        {"id": "play_ciri", "category": "Giocatore", "command": "Ciri", "description": "Passa a giocare con il personaggio di Ciri", "display_name": "Gioca come Ciri", "icon": "🗡️"},
        {"id": "play_geralt", "category": "Giocatore", "command": "Geralt", "description": "Torna a giocare con Geralt di Rivia", "display_name": "Torna a Geralt", "icon": "🐺"},
        {"id": "add_money_10k", "category": "Economia", "command": "addmoney(10000)", "description": "Aggiunge 10.000 Corone", "display_name": "+10.000 Corone", "icon": "💰"},
        {"id": "add_money_50k", "category": "Economia", "command": "addmoney(50000)", "description": "Aggiunge 50.000 Corone", "display_name": "+50.000 Corone", "icon": "💰"},
        {"id": "add_money_100k", "category": "Economia", "command": "addmoney(100000)", "description": "Aggiunge 100.000 Corone", "display_name": "+100.000 Corone", "icon": "💰"},
        {"id": "level_up", "category": "Progressione", "command": "levelup", "description": "Aumenta il livello del personaggio di 1", "display_name": "Livello +1 (Level Up)", "icon": "⚡"},
        {"id": "add_exp_5k", "category": "Progressione", "command": "addexp(5000)", "description": "Aggiunge 5.000 punti Esperienza", "display_name": "+5.000 Esperienza", "icon": "📈"},
        {"id": "add_gwent_all", "category": "Gwent", "command": "addgwintcards", "description": "Sblocca e aggiunge UNA per ciascuna di tutte le carte Gwent nel gioco!", "display_name": "🃏 Sblocca Tutte le Carte Gwent", "icon": "🃏"},
        {"id": "win_gwent", "category": "Gwent", "command": "winGwint(100)", "description": "Vince istantaneamente la partita di Gwent in corso con 100 punti", "display_name": "🃏 Vinci Partita Gwent Attuale", "icon": "🏆"},
        {"id": "play_gwent_anywhere", "category": "Gwent", "command": "secretgwint", "description": "Avvia immediatamente una partita di Gwent ovunque ti trovi", "display_name": "🃏 Gioca a Gwent Ovunque", "icon": "🎮"},
        {"id": "kill_all_enemies", "category": "Combattimento", "command": "killall", "description": "Uccide all'istante tutti i nemici impegnati in combattimento", "display_name": "Uccidi Tutti i Nemici (Kill All)", "icon": "💀"},
        {"id": "unlock_signposts", "category": "Mappa", "command": "ShowAllFT(1)", "description": "Sblocca e scopre tutti i cartelli di viaggio rapido sulla mappa", "display_name": "Sblocca Tutti i Viaggi Rapidi (ShowAllFT)", "icon": "🗺️"},
        {"id": "unlock_pins", "category": "Mappa", "command": "ShowPins(1)", "description": "Rivela tutti i punti d'interesse (?) e icone sulla mappa", "display_name": "Rivela Tutta la Mappa (ShowPins)", "icon": "📍"},
        {"id": "night_vision_on", "category": "Giocatore", "command": "Cat(1)", "description": "Attiva la visione notturna", "display_name": "Visione Notturna Attiva", "icon": "👁️"},
        {"id": "night_vision_off", "category": "Giocatore", "command": "Cat(0)", "description": "Disattiva la visione notturna", "display_name": "Visione Notturna Disattiva", "icon": "🕶️"},
        {"id": "grow_beard", "category": "Aspetto", "command": "setbeard(1)", "description": "Fa crescere la barba a Geralt al massimo", "display_name": "Barba Folta", "icon": "🧔"},
        {"id": "shave_beard", "category": "Aspetto", "command": "shave", "description": "Rade completamente la barba di Geralt", "display_name": "Rasati a Zero", "icon": "🪒"},
        {"id": "stop_rain", "category": "Meteo", "command": "stoprain", "description": "Ferma la pioggia e fa tornare il sereno", "display_name": "Ferma Pioggia (Bel Tempo)", "icon": "☀️"},
        {"id": "make_it_rain", "category": "Meteo", "command": "makeitrain", "description": "Scatena un temporale con pioggia", "display_name": "Fai Piovere (Temporale)", "icon": "⛈️"},
        {"id": "goto_novigrad", "category": "Viaggio Rapido", "command": "gotoNovigrad", "description": "Teletrasporta immediatamente a Novigrad", "display_name": "Teletrasporto Novigrad", "icon": "🏰"},
        {"id": "goto_skellige", "category": "Viaggio Rapido", "command": "gotoSkellige", "description": "Teletrasporta immediatamente alle Isole Skellige", "display_name": "Teletrasporto Skellige", "icon": "⛵"},
        {"id": "goto_kaer_morhen", "category": "Viaggio Rapido", "command": "gotoKaerMorhen", "description": "Teletrasporta immediatamente a Kaer Morhen", "display_name": "Teletrasporto Kaer Morhen", "icon": "🏔️"},
        {"id": "goto_white_orchard", "category": "Viaggio Rapido", "command": "gotoProlog", "description": "Teletrasporta immediatamente a Bianco Frutteto", "display_name": "Teletrasporto Bianco Frutteto", "icon": "🌸"}
    ]
    database["cheats"].extend(curated_cheats)

    try:
        r = requests.get(URLS['cheats'], headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        wiki_div = soup.find('div', class_=lambda c: c and 'wiki-html' in c)
        if wiki_div:
            existing_cmds = {c["command"].lower() for c in database["cheats"]}
            for table in wiki_div.find_all('table'):
                rows = table.find_all('tr')
                cat_name = 'Comandi Console'
                if rows:
                    th = rows[0].find(['th', 'td'])
                    if th:
                        cat_name = th.get_text(strip=True)
                for row in rows[1:]:
                    cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                    if len(cells) >= 2:
                        raw_cmd = cells[0].split('Full List')[0].split('List of')[0].strip()
                        if raw_cmd and raw_cmd.lower() not in existing_cmds and '(' not in raw_cmd:
                            database["cheats"].append({
                                "id": f"ign_cheat_{len(database['cheats'])}",
                                "category": cat_name,
                                "command": raw_cmd,
                                "description": cells[1],
                                "display_name": raw_cmd,
                                "icon": "⚙️"
                            })
                            existing_cmds.add(raw_cmd.lower())
    except Exception as e:
        print(f"Warning fetching cheats IGN: {e}")

    # 2. Fetch Items
    print("Scaricamento oggetti (Armi, Armature, Gwent, Pozioni, ecc.)...")
    try:
        r = requests.get(URLS['items'], headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        wiki_div = soup.find('div', class_=lambda c: c and 'wiki-html' in c)
        if wiki_div:
            current_category = None
            for el in wiki_div.find_all(['h2', 'h3', 'ul']):
                if el.name in ['h2', 'h3']:
                    h_text = el.get_text(strip=True)
                    for raw_key in CATEGORY_MAP:
                        if raw_key.lower() in h_text.lower():
                            current_category = raw_key
                            break
                    else:
                        current_category = None
                elif el.name == 'ul' and current_category:
                    cat_info = CATEGORY_MAP.get(current_category, {"name": current_category, "icon": "📦", "cmd_type": "additem"})
                    for li in el.find_all('li'):
                        code = li.get_text(strip=True)
                        if code and len(code) > 1 and not code.startswith("http"):
                            item_obj = {
                                "id": f"item_{len(database['items'])}",
                                "code": code,
                                "name": humanize_name(code),
                                "category_key": current_category,
                                "category_name": cat_info["name"],
                                "icon": cat_info["icon"],
                                "type": cat_info["cmd_type"],
                                "default_qty": 1,
                                "max_qty": 100
                            }
                            database["items"].append(item_obj)
    except Exception as e:
        print(f"Warning fetching items IGN: {e}")

    # 3. Fetch NPCs
    print("Scaricamento PNG e Mostri...")
    try:
        r = requests.get(URLS['npcs'], headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        wiki_div = soup.find('div', class_=lambda c: c and 'wiki-html' in c)
        if wiki_div:
            current_category = None
            for el in wiki_div.find_all(['h2', 'h3', 'ul']):
                if el.name in ['h2', 'h3']:
                    h_text = el.get_text(strip=True)
                    for raw_key in ["Monsters", "Animals", "Characters", "Miscellaneous"]:
                        if raw_key.lower() in h_text.lower():
                            current_category = raw_key
                            break
                    else:
                        current_category = None
                elif el.name == 'ul' and current_category:
                    cat_info = CATEGORY_MAP.get(current_category, {"name": current_category, "icon": "👾", "cmd_type": "spawn"})
                    for li in el.find_all('li'):
                        code = li.get_text(strip=True)
                        if code and len(code) > 1 and not code.startswith("http"):
                            item_obj = {
                                "id": f"npc_{len(database['items'])}",
                                "code": code,
                                "name": humanize_name(code),
                                "category_key": current_category,
                                "category_name": cat_info["name"],
                                "icon": cat_info["icon"],
                                "type": "spawn",
                                "default_qty": 1,
                                "max_qty": 20
                            }
                            database["items"].append(item_obj)
    except Exception as e:
        print(f"Warning fetching NPCs IGN: {e}")

    # 4. Fetch Talents
    print("Scaricamento Abilità e Talenti...")
    try:
        r = requests.get(URLS['talents'], headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        wiki_div = soup.find('div', class_=lambda c: c and 'wiki-html' in c)
        if wiki_div:
            h = wiki_div.find(lambda e: e.name in ['h2', 'h3'] and 'Skills' in e.get_text())
            if h:
                ul = h.find_next_sibling('ul')
                if ul:
                    for li in ul.find_all('li'):
                        code = li.get_text(strip=True)
                        if code and len(code) > 1:
                            item_obj = {
                                "id": f"skill_{len(database['items'])}",
                                "code": code,
                                "name": humanize_name(code),
                                "category_key": "Skills",
                                "category_name": "Abilità & Talenti",
                                "icon": "⚡",
                                "type": "learnskill",
                                "default_qty": 1,
                                "max_qty": 5
                            }
                            database["items"].append(item_obj)
    except Exception as e:
        print(f"Warning fetching talents IGN: {e}")

    print(f"Totale Oggetti/Entità: {len(database['items'])}")
    print(f"Totale Trucchi/Comandi: {len(database['cheats'])}")

    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    print(f"Database salvato correttamente in: {DB_PATH}")

if __name__ == "__main__":
    build_database()
