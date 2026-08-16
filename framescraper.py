import requests
from bs4 import BeautifulSoup
import json

arrow_numpad = {
    # Converts from arrows to numpad notation
    "cursor-one": "1",
    "cursor-two": "2",
    "cursor-three": "3",
    "cursor-four": "4",
    "cursor-six": "6",
    "cursor-seven": "7",
    "cursor-eight": "8",
    "cursor-nine": "9",
    # converts for held arrows
    "cursor-b-one": "1_",
    "cursor-b-two": "2_",
    "cursor-b-three": "3_",
    "cursor-b-four": "4_",
    "cursor-b-six": "6_",
    "cursor-b-seven": "7_",
    "cursor-b-eight": "8_",
    "cursor-b-nine": "9_",
}

# Ids to get the proper links.
char_ids = {
    "01": "akira",
    "02": "pai", 
    "03": "lau", 
    "04": "wolf", 
    "05": "jeffry", 
    "06": "kage", 
    "07": "sarah", 
    "08": "jacky",
    "09": "shun",
    "10": "lion", 
    "11": "aoi", 
    "12": "lei", 
    "13": "vanessa",
    "14": "brad",
    "15": "goh", 
    "16": "eileen",
    "17": "blaze",
    "18": "taka",
    "19": "jean",
    "20": "dural",
}

# Evade is represented through circle and x symbols, need to convert to plain text
def convert_evade(value):
    value = value.strip()

    # Normalize UTF-8 escaped circle
    if value in ["〇", "\u00e3\u0080\u0087"]:
        return "any"

    # Normalize cross
    if value in ["×", "\u00c3\u0097"]:
        return "none"

    v = value.lower()
    if v == "front":
        return "front"
    if v == "back":
        return "back"

    if value in ["-", ""]:
        return ""

    return value

def i_hate_tildes(value):
    value = value.strip()

    # normalizes tildes so they don't show up as unicode for nonstandard tildes.
    value = (
        value.replace("～", "~")   
             .replace("〜", "~")  
             .replace("\u301c", "~")
             .replace("\uff5e", "~")
             .replace("\ufe58", "~")
             .replace("\u00e3\u0080\u009c", "~")
    )

    return value
    # why does anyone use nonstandard tildes? Let me know.


def parse(cell):
    parts = []

    for element in cell.contents:
        # checks for images, converts from arrows to numpad notation
        if hasattr(element, "name") and element.name == "img":
            src = element.get("src", "")
            base = src.split("/")[-1].split(".")[0]
            if base in arrow_numpad:
                parts.append(arrow_numpad[base])
        else:
            text = str(element).strip()
            if text:
                parts.append(text)

    return "".join(parts)

def scrape_vf(character):
    url = f"https://virtua-fighter.com/revo/en/character/skill/skill{character}_02.html"
    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    moves = []
    rows = soup.find_all("tr")

    for row in rows:
        cells = row.find_all("td")

        # Skip invalid rows
        if len(cells) != 16:
            continue

        values = [c.get_text(strip=True) for c in cells]

        name = values[0]
        command = parse(cells[1])
        level = values[2]
        damage = i_hate_tildes(cells[3])
        startup = values[4]
        active = values[5]
        total = values[6]
        on_guard = values[7]
        on_hit = values[8]
        on_ch = values[9]
        crouch_hit = values[10]
        crouch_ch = values[11]
        recovery_c = values[12]
        evade = convert_evade(values[13])
        sober = values[14]
        notes = parse(cells[15])

        move = {
            "name": name,
            "command": command,
            "level": level,
            "damage": damage,
            "startup": startup,
            "active": active,
            "total": total,
            "onGuard": on_guard,
            "onHit": on_hit,
            "onCounterHit": on_ch,
            "evade": evade,
            "sober": sober,
            "notes": notes
        }

        moves.append(move)

    return moves

# save to json
def save_json(moves, filename):
    with open(filename, "w") as f:
        json.dump(moves, f, indent=2)

if __name__ == "__main__":
    for char_id, name in char_ids.items():
        print(f"{name} frame data comin' right up!")    
        moves = scrape_vf(char_id)  
        save_json(moves, f"{name}.json")
        print(f"Scraped {len(moves)} moves for {name}.")
    print("Donezopotamus.")
