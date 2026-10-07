import json
import os
import re

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "database.json")

# Dizionari di traduzione specifica
POTION_MAP = {
    "Black Blood 1": "Pozione Sangue Nero (Base)",
    "Black Blood 2": "Pozione Sangue Nero Migliorata",
    "Black Blood 3": "Pozione Sangue Nero Superiore",
    "Blizzard 1": "Pozione Bora (Base)",
    "Blizzard 2": "Pozione Bora Migliorata",
    "Blizzard 3": "Pozione Bora Superiore",
    "Cat 1": "Pozione Gatto (Visione Notturna)",
    "Cat 2": "Pozione Gatto Migliorata",
    "Cat 3": "Pozione Gatto Superiore",
    "Clearing Potion": "Pozione della Rinascita (Reset Abilità)",
    "Full Moon 1": "Pozione Luna Piena (Base)",
    "Full Moon 2": "Pozione Luna Piena Migliorata",
    "Full Moon 3": "Pozione Luna Piena Superiore",
    "Golden Oriole 1": "Pozione Rigogolo Dorato (Immunità Veleno)",
    "Golden Oriole 2": "Pozione Rigogolo Dorato Migliorata",
    "Golden Oriole 3": "Pozione Rigogolo Dorato Superiore",
    "Killer Whale 1": "Pozione Orca (Respiro Subacqueo)",
    "Maribor Forest 1": "Pozione Foresta di Maribor (Adrenalina)",
    "Maribor Forest 2": "Pozione Foresta di Maribor Migliorata",
    "Maribor Forest 3": "Pozione Foresta di Maribor Superiore",
    "Petri Philtre 1": "Filtro di Petri (Intensità Segni)",
    "Petri Philtre 2": "Filtro di Petri Migliorato",
    "Petri Philtre 3": "Filtro di Petri Superiore",
    "Pheromone Potion Bear 1": "Pozione ai Feromoni d'Orso",
    "Pheromone Potion Drowner 1": "Pozione ai Feromoni di Annegato",
    "Pheromone Potion Nekker 1": "Pozione ai Feromoni di Nekker",
    "Pops Antidote": "Antidoto di Pop",
    "Swallow 1": "Pozione Rondine (Rigenerazione Salute)",
    "Swallow 2": "Pozione Rondine Migliorata",
    "Swallow 3": "Pozione Rondine Superiore",
    "Tawny Owl 1": "Pozione Gufo Reale (Rigenerazione Vigore)",
    "Tawny Owl 2": "Pozione Gufo Reale Migliorata",
    "Tawny Owl 3": "Pozione Gufo Reale Superiore",
    "Thunderbolt 1": "Pozione Tuono (Potenza Attacco)",
    "Thunderbolt 2": "Pozione Tuono Migliorata",
    "Thunderbolt 3": "Pozione Tuono Superiore",
    "Trial Potion Kit": "Kit di Pozioni della Prova delle Erbe",
    "Village drink": "Bevanda del Villaggio",
    "White Honey 1": "Pozione Miele Bianco (Azzera Tossicità)",
    "White Honey 2": "Pozione Miele Bianco Migliorata",
    "White Honey 3": "Pozione Miele Bianco Superiore",
    "White Raffards Decoction 1": "Decotto di Raffard il Bianco (Cura Immediata)",
    "White Raffards Decoction 2": "Decotto di Raffard il Bianco Migliorato",
    "White Raffards Decoction 3": "Decotto di Raffard il Bianco Superiore",
}

BOMB_MAP = {
    "Alkali Bomb 1": "Bomba Alcalina",
    "Alkali Bomb 2": "Bomba Alcalina Migliorata",
    "Alkali Bomb 3": "Bomba Alcalina Superiore",
    "Dancing Star 1": "Bomba Stella Danzante (Danno da Fuoco)",
    "Dancing Star 2": "Bomba Stella Danzante Migliorata",
    "Dancing Star 3": "Bomba Stella Danzante Superiore",
    "Devils Puffball 1": "Bomba Fungo del Diavolo (Nube Velenosa)",
    "Devils Puffball 2": "Bomba Fungo del Diavolo Migliorata",
    "Devils Puffball 3": "Bomba Fungo del Diavolo Superiore",
    "Dragons Dream 1": "Bomba Sogno del Drago (Gas Infiammabile)",
    "Dragons Dream 2": "Bomba Sogno del Drago Migliorata",
    "Dragons Dream 3": "Bomba Sogno del Drago Superiore",
    "Dwimeritium Bomb 1": "Bomba di Dimeritium (Blocca Magia)",
    "Dwimeritium Bomb 2": "Bomba di Dimeritium Migliorata",
    "Dwimeritium Bomb 3": "Bomba di Dimeritium Superiore",
    "Fungi Bomb 1": "Bomba ai Funghi",
    "Glue Bomb 1": "Bomba Vischiosa",
    "Grapeshot 1": "Bomba Mitraglia (Danno da Frammentazione)",
    "Grapeshot 2": "Bomba Mitraglia Migliorata",
    "Grapeshot 3": "Bomba Mitraglia Superiore",
    "Salt Bomb 1": "Bomba di Sale",
    "Samum 1": "Bomba Samum (Accecamento & Stordimento)",
    "Samum 2": "Bomba Samum Migliorata",
    "Samum 3": "Bomba Samum Superiore",
    "Shrapnel Bomb 1": "Bomba a Frammentazione",
    "Silver Dust Bomb 1": "Bomba Polvere di Luna (Blocca Trasformazioni)",
    "Silver Dust Bomb 2": "Bomba Polvere di Luna Migliorata",
    "Silver Dust Bomb 3": "Bomba Polvere di Luna Superiore",
    "Snow Ball": "Palla di Neve",
    "Tutorial Bomb": "Bomba Addestramento",
    "Virus Bomb 1": "Bomba Virale",
    "White Frost 1": "Bomba Vento del Nord (Congelamento)",
    "White Frost 2": "Bomba Vento del Nord Migliorata",
    "White Frost 3": "Bomba Vento del Nord Superiore",
}

RUNE_GLYPH_MAP = {
    "Dazhbog rune": "Runa Dazhbog (Probabilità Ustione)",
    "Dazhbog rune rare": "Runa Dazhbog Maggiore",
    "Devana rune": "Runa Devana (Probabilità Sanguinamento)",
    "Devana rune rare": "Runa Devana Maggiore",
    "Elemental rune": "Runa Elementale",
    "Elemental rune rare": "Runa Elementale Maggiore",
    "Forgotten soul": "Anima Dimenticata",
    "Forgotten soul rare": "Anima Dimenticata Rara",
    "Glyph aard": "Glifo di Aard (Intensità Segno)",
    "Glyph aard greater": "Glifo di Aard Maggiore",
    "Glyph aard lesser": "Glifo di Aard Minore",
    "Glyph axii": "Glifo di Axii (Intensità Segno)",
    "Glyph axii greater": "Glifo di Axii Maggiore",
    "Glyph axii lesser": "Glifo di Axii Minore",
    "Glyph igni": "Glifo di Igni (Intensità Segno)",
    "Glyph igni greater": "Glifo di Igni Maggiore",
    "Glyph igni lesser": "Glifo di Igni Minore",
    "Glyph quen": "Glifo di Quen (Intensità Segno)",
    "Glyph quen greater": "Glifo di Quen Maggiore",
    "Glyph quen lesser": "Glifo di Quen Minore",
    "Glyph yrden": "Glifo di Yrden (Intensità Segno)",
    "Glyph yrden greater": "Glifo di Yrden Maggiore",
    "Glyph yrden lesser": "Glifo di Yrden Minore",
    "Horse apex tail": "Coda di Cavallo Apex",
    "Horse Bag 1": "Bisaccia da Cavallo (Capacità +30)",
    "Horse Bag 2": "Bisaccia da Cavallo (Capacità +70)",
    "Horse Bag 3": "Bisaccia da Cavallo (Capacità +100)",
    "Horse Blinder 1": "Paraocchi da Cavallo (Panico -20)",
    "Horse Blinder 2": "Paraocchi da Cavallo (Panico -40)",
    "Horse Blinder 3": "Paraocchi da Cavallo (Panico -60)",
    "Horse Saddle 1": "Sella da Cavallo (Vigore +35)",
    "Horse Saddle 2": "Sella da Cavallo (Vigore +50)",
    "Horse Saddle 3": "Sella da Cavallo (Vigore +75)",
    "Horse Saddle 4": "Sella da Cavallo (Vigore +90)",
}

ARMOR_TIERS = {
    "": " (Base)",
    "1": " Migliorata",
    "2": " Superiore",
    "3": " Perfetta",
    "4": " Gran Maestro",
}

SCHOOL_MAP = {
    "Bear": "della Scuola dell'Orso",
    "Lynx": "della Scuola del Gatto",
    "Gryphon": "della Scuola del Grifone",
    "Wolf": "della Scuola del Lupo",
    "Viper": "della Scuola della Vipera",
    "Manticore": "della Scuola della Manticora",
}

PIECE_MAP = {
    "Armor": "Armatura",
    "Boots": "Stivali",
    "Gloves": "Guanti",
    "Pants": "Pantaloni",
}

SKILL_MAP = {
    "sword_s1": "Memoria Muscolare (Attacchi Veloci)",
    "sword_s2": "Colpi Precisi (Critico Attacchi Veloci)",
    "sword_s3": "Vortice (Attacco Rotante)",
    "sword_s4": "Riflessi Taglienti (Adrenalina Attacchi Veloci)",
    "sword_s5": "Forza Muscolare (Attacchi Pesanti)",
    "sword_s6": "Rompispada (Danno Corazza)",
    "sword_s7": "Fendente (Colpo Pesante Caricato)",
    "sword_s8": "Colpo di Grazia (Probabilità Critico)",
    "sword_s9": "Riflessi Fulminei (Deviazione Frecce)",
    "magic_s1": "Esplosione Aard (Portata Aard)",
    "magic_s2": "Aard Travolgente (Aard a 360°)",
    "magic_s3": "Corazza Quen (Danno da Esplosione)",
    "magic_s4": "Scudo Attivo (Quen Ripristina Salute)",
    "magic_s5": "Flusso di Fuoco (Igni a Getto Continuo)",
    "magic_s6": "Marionetta (Axii Trasforma Nemico in Alleato)",
    "magic_s7": "Trappola Magica (Yrden Rallenta e Danneggia)",
    "magic_s8": "Intensità Igni (Probabilità Ustione)",
    "alchemy_s1": "Tolleranza Acquisita (Tossicità Massima)",
    "alchemy_s2": "Lama Avvelenata (Veleno sulle Spade)",
    "alchemy_s3": "Effetto Prolungato (Durata Pozioni)",
    "alchemy_s4": "Rigenerazione (Salute da Pozioni)",
    "alchemy_s5": "Trattamento d'Olio (Protezione Mostri)",
    "alchemy_s6": "Frenesia (Rallentatore su Pericolo)",
    "alchemy_s7": "Bomba Efficace (Frammenti Extra)",
}

def translate_item(item):
    cat = item.get("category_key", "")
    code = item.get("code", "")
    name = item.get("name", code)
    
    if cat == "GwentCards":
        return name, ["gwent", "carta", "carte", "gwint", code.lower()]

    if cat == "Potions":
        if code in POTION_MAP:
            return POTION_MAP[code], ["pozione", "decotto", "alchimia", "cura"]
        if name in POTION_MAP:
            return POTION_MAP[name], ["pozione", "decotto", "alchimia", "cura"]

    if cat == "Bombs":
        if code in BOMB_MAP:
            return BOMB_MAP[code], ["bomba", "esplosivo", "danno"]
        if name in BOMB_MAP:
            return BOMB_MAP[name], ["bomba", "esplosivo", "danno"]

    if cat == "Upgradesand Runes":
        if code in RUNE_GLYPH_MAP:
            return RUNE_GLYPH_MAP[code], ["runa", "glifo", "potenziamento", "cavallo"]
        if name in RUNE_GLYPH_MAP:
            return RUNE_GLYPH_MAP[name], ["runa", "glifo", "potenziamento", "cavallo"]

    if cat == "Skills":
        code_clean = code.lower().replace(" ", "_")
        if code_clean in SKILL_MAP:
            return SKILL_MAP[code_clean], ["abilità", "talento", "skill", "combattimento", "segni", "alchimia"]

    if cat == "Armor":
        for school_en, school_it in SCHOOL_MAP.items():
            if school_en in code or school_en in name:
                for piece_en, piece_it in PIECE_MAP.items():
                    if piece_en in code or piece_en in name:
                        tier_num = ""
                        for t in ["4", "3", "2", "1"]:
                            if code.endswith(f" {t}") or code.endswith(f"_{t}") or name.endswith(f" {t}"):
                                tier_num = t
                                break
                        tier_str = ARMOR_TIERS.get(tier_num, " (Base)")
                        res_name = f"{piece_it} {school_it}{tier_str}"
                        extra_tags = [school_it.lower(), piece_it.lower(), "armatura", "witcher", "scuola"]
                        if "gatto" in school_it.lower():
                            extra_tags.extend(["lynx", "cat", "felino"])
                        elif "orso" in school_it.lower():
                            extra_tags.extend(["bear", "ursine"])
                        elif "grifone" in school_it.lower():
                            extra_tags.extend(["gryphon", "griffin"])
                        return res_name, extra_tags

        if "Heavy armor" in name:
            return name.replace("Heavy armor", "Armatura Pesante").replace("_crafted", " (Fabbricata)"), ["pesante", "armatura"]
        if "Light armor" in name:
            return name.replace("Light armor", "Armatura Leggera").replace("_crafted", " (Fabbricata)"), ["leggera", "armatura"]
        if "Medium armor" in name:
            return name.replace("Medium armor", "Armatura Media").replace("_crafted", " (Fabbricata)"), ["media", "armatura"]
        if "Starting Armor" in name:
            return "Armatura di Kaer Morhen Iniziale (Geralt)", ["kaer morhen", "iniziale", "geralt", "armatura"]
        if "Thyssen" in name:
            return "Armatura di Thyssen (Fabbricata)", ["thyssen", "armatura"]

    if cat == "Weapons":
        for school_en, school_it in SCHOOL_MAP.items():
            if school_en in code or school_en in name:
                tier_num = ""
                for t in ["4", "3", "2", "1"]:
                    if code.endswith(f" {t}") or code.endswith(f"_{t}") or name.endswith(f" {t}"):
                        tier_num = t
                        break
                tier_str = ARMOR_TIERS.get(tier_num, " (Base)")
                if "silver" in code.lower():
                    return f"Spada d'argento {school_it}{tier_str}", ["spada argento", "argento", school_it.lower(), "witcher"]
                elif "steel" in code.lower():
                    return f"Spada d'acciaio {school_it}{tier_str}", ["spada acciaio", "acciaio", school_it.lower(), "witcher"]
                elif "crossbow" in code.lower():
                    return f"Balestra {school_it}", ["balestra", school_it.lower()]

        WEAPON_NAMES = {
            "Aerondight": "Aerondight (Spada d'Argento Suprema)",
            "Iris": "Iris (Spada di Olgierd von Everec)",
            "Winters Blade": "Lama d'Inverno",
            "Winter's Blade": "Lama d'Inverno",
            "Bloodsword": "Spada Sanguinaria",
            "Blackunicorn": "Unicorno Nero",
            "Fate": "Destino (Spada d'Argento)",
            "Tor Zireael": "Tor Zireael (Spada d'Argento di Ciri)",
            "Blade of the Bits": "Lama dei Rifiuti (Spada di Hattori)",
            "Beannshie": "Beann'shie (Spada d'Acciaio)",
            "Ashrune": "Runa della Cenere",
            "Azurewrath": "Furia Azzurra",
            "Caerme": "Caerme",
            "Caranthil Staff": "Bastone di Caranthir",
            "Deireadh": "Deireadh",
            "Dyaebl": "D'yaebl",
            "Gwyhyr": "Gwyhyr Gnomesco",
            "Harvall": "Harvall",
            "Havcaaren": "Hav'caaren",
            "Inis": "Inis",
            "Moonblade": "Lama Lunare",
            "Princess Xenthia Sword": "Spada della Principessa Xenthia",
            "Reach of the Damned": "Portata dei Dannati",
            "Torlara": "Tor Lara",
            "Ultimatum": "Ultimatum",
            "Weeper": "Pianolente",
        }
        for w_k, w_v in WEAPON_NAMES.items():
            if w_k.lower() in code.lower() or w_k.lower() in name.lower():
                return w_v, ["spada", "arma", w_k.lower()]

        if "Shield" in name:
            return name.replace("Shield", "Scudo").replace("Bandit", "Banditi").replace("Guard", "Guardia"), ["scudo", "difesa"]
        if "bow" in code.lower():
            return "Arco Elfico" if "elven" in code.lower() else "Arco da Caccia", ["arco", "frecce"]

    if cat == "Schematics":
        clean = name.replace("schematic", "").replace("Schematic", "").strip()
        return f"Schema: {clean}", ["schema", "diagramma", "fabbricazione", "crafting"]

    if cat == "Books and Notes":
        return f"Libro / Nota: {name}", ["libro", "lore", "lettera", "bestiario", "documento"]

    MAT_MAP = {
        "Aether": "Etere (Ingrediente Alchemico)",
        "Albedo": "Albedo (Ingrediente Alchemico)",
        "Alchemical paste": "Pasta Alchemica",
        "Amethyst": "Ametista",
        "Amethyst dust": "Polvere di Ametista",
        "Amber": "Ambra",
        "Amber dust": "Polvere d'Ambra",
        "Dark Iron ingot": "Lingotto di Ferro Scuro",
        "Dark Steel ingot": "Lingotto d'Acciaio Scuro",
        "Dimeritium ingot": "Lingotto di Dimeritium",
        "Dimeritium ore": "Minerale di Dimeritium",
        "Dimeritium plate": "Piastra di Dimeritium",
        "Gold ingot": "Lingotto d'Oro",
        "Gold ore": "Minerale d'Oro",
        "Silver ingot": "Lingotto d'Argento",
        "Silver ore": "Minerale d'Argento",
        "Meteorite ingot": "Lingotto di Meteorite",
        "Meteorite ore": "Minerale di Meteorite",
        "Glowing ore": "Minerale Brillante",
        "Hardened leather": "Cuoio Indurito",
        "Cured leather": "Cuoio Conciato",
        "Draconid leather": "Pelle di Draconide",
        "Monster feather": "Piuma di Mostro",
        "Monster hair": "Peli di Mostro",
        "Monster heart": "Cuore di Mostro",
        "Monster claw": "Artiglio di Mostro",
        "Monster eye": "Occhio di Mostro",
        "Monster liver": "Fegato di Mostro",
        "Monster saliva": "Saliva di Mostro",
        "Ruby": "Rubino",
        "Ruby dust": "Polvere di Rubino",
        "Sapphire": "Zaffiro",
        "Sapphire dust": "Polvere di Zaffiro",
        "Diamond": "Diamante",
        "Diamond dust": "Polvere di Diamante",
    }
    for m_k, m_v in MAT_MAP.items():
        if m_k.lower() in code.lower() or m_k.lower() in name.lower():
            return m_v, ["materiale", "artigianato", "ingrediente", m_k.lower()]

    if cat == "Monsters":
        clean = code.replace("_quest__", "").replace("_", " ").title()
        return f"Mostro: {clean}", ["mostro", "creatura", "spawn"]
    if cat == "Animals":
        IT_ANIMALS = {"bat": "Pipistrello", "cat": "Gatto", "chicken": "Gallina", "cow": "Mucca", "deer": "Cervo", "dog": "Cane", "goat": "Capra", "goose": "Oca", "hare": "Lepre", "horse": "Cavallo (Ravelo)", "pig": "Maiale", "pigeon": "Piccione", "ram": "Ariete", "rat": "Topo", "rooster": "Gallo", "seagull": "Gabbiano", "sheep": "Pecora", "swallow": "Rondine", "toad": "Rospo", "wolf": "Lupo", "bear": "Orso"}
        c_low = code.lower()
        if c_low in IT_ANIMALS:
            return f"Animale: {IT_ANIMALS[c_low]}", ["animale", "fauna", "spawn", IT_ANIMALS[c_low].lower()]
        return f"Animale: {name}", ["animale", "fauna", "spawn"]
    if cat == "Characters":
        IT_CHARS = {"cirilla": "Ciri (Cirilla)", "grenn": "Geralt di Rivia", "keira": "Keira Metz", "triss": "Triss Merigold", "yennefer": "Yennefer di Vengerberg", "vesemir": "Vesemir", "zoltan": "Zoltan Chivay", "dandelion": "Ranuncolo"}
        c_low = code.lower()
        for ck, cv in IT_CHARS.items():
            if ck in c_low:
                return f"Personaggio: {cv}", ["personaggio", "npc", "spawn", cv.lower()]

    return name, [code.lower()]

def main():
    print("Caricamento database da:", DB_PATH)
    with open(DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data.get("items", [])
    print(f"Totale elementi da arricchire: {len(items)}")

    count_translated = 0
    for it in items:
        name_it, tags = translate_item(it)
        it["name_it"] = name_it
        it["tags"] = tags
        
        code = it.get("code", "")
        name = it.get("name", "")
        cat_name = it.get("category_name", "")
        tags_str = " ".join(tags)
        
        search_blob = f"{name_it} {name} {code} {cat_name} {tags_str}".lower()
        it["search_blob"] = re.sub(r'[\(\)\'\",_]', ' ', search_blob)
        count_translated += 1

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Completato! {count_translated} elementi arricchiti con successo.")

if __name__ == "__main__":
    main()
