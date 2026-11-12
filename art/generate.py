"""Generate Infernal Kingdom art with the OpenAI image API.

    python3 art/generate.py [name ...]      # no names = everything not already in art/raw

Not run yet: the project currently uses labelled placeholders (art/placeholders.py).
Reads OPENAI_API_KEY from the environment. Writes PNGs to art/raw/, then:

    python3 art/process.py && python3 art/build_game_assets.py

The same prompts, with notes, are in art/PROMPTS.md.
"""

import base64
import json
import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

MODEL = "gpt-image-2"
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")

STYLE = (
    "Premium cinematic 3D casino-game render, dark fantasy: molten gold #D6A04A, blood crimson #A51D24, "
    "infernal orange #FF6A00, obsidian #080708 and blackened iron #211A1A, with rare emerald soul light "
    "#14B86E and violet magic #923DCE as accents. Physically based materials (forged iron, polished gold, "
    "glowing lava, faceted gems), one strong warm key light from the upper left, a cool rim light, crisp "
    "silhouette readable at small size, consistent three-quarter front perspective and scale across the "
    "set. Original design, not based on any existing game. No watermark, no border."
)
NO_TEXT = " No text, no letters, no numbers."
MAGENTA = "isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background"
SYMBOL = f"Single slot-game symbol, centred, filling about 80 percent of the frame, {MAGENTA}: "
LETTER = f"Single slot-game card symbol, centred, filling about 75 percent of the frame, {MAGENTA}: "
SQUARE, WIDE, TALL = "1024x1024", "1536x1024", "1024x1536"
CALM = " Keep the centre of the image darker and calmer so a 6 by 4 reel set can sit over it."

ASSETS = {
    # premium symbols
    "h1": (SQUARE, SYMBOL + "the Demon King, a horned infernal monarch, head and shoulders, obsidian skin with molten cracks, a black iron crown, burning gold eyes, regal and menacing."),
    "h2": (SQUARE, SYMBOL + "an Infernal Dragon head in molten armour plates, lava glowing between the scales, jaws open with ember breath."),
    "h3": (SQUARE, SYMBOL + "a Cursed Crown of black iron with jagged spikes and burning crimson gemstones."),
    "h4": (SQUARE, SYMBOL + "a golden Blood Chalice with engraved runes, swirling red magical energy rising from the cup."),
    "h5": (SQUARE, SYMBOL + "a cursed gold Soul Ring holding a large emerald with a trapped glowing soul inside."),
    # low symbols
    "l1": (SQUARE, LETTER + "the capital letter A in a heavy engraved serif, crimson enamel with a molten gold edge." ),
    "l2": (SQUARE, LETTER + "the capital letter K in a heavy engraved serif, polished gold with dark engraving."),
    "l3": (SQUARE, LETTER + "the capital letter Q in a heavy engraved serif, emerald enamel with a gold edge."),
    "l4": (SQUARE, LETTER + "the capital letter J in a heavy engraved serif, brushed silver with dark engraving."),
    "l5": (SQUARE, LETTER + "the number 10 in a heavy engraved serif, aged bronze with dark engraving."),
    # specials
    "w": (SQUARE, SYMBOL + "the Infernal Wild: the Demon King's burning crown emblem on a black iron shield edged with molten gold, flames rising behind."),
    "hs": (SQUARE, SYMBOL + "the Hellstar: a five-pointed star forged from blackened iron with a white-hot molten core and orange flame points."),
    "s": (SQUARE, SYMBOL + "the Hell Gate scatter: a gothic infernal portal arch of obsidian with violet fire swirling inside."),
    "wb": (SQUARE, SYMBOL + "the Wild Bomb: a round black iron bomb bound with gold bands, a burning fuse, cracks leaking orange light."),
    "gb": (SQUARE, SYMBOL + "the Golden Wild Bomb: a larger ornate bomb of polished molten gold with crimson gems and a blazing fuse."),
    "sp": (SQUARE, SYMBOL + "the Split Symbol: a cracked obsidian rune tablet splitting into two halves with gold light pouring from the crack."),
    "do": (SQUARE, SYMBOL + "the Demon Overlord: the Demon King in full figure, wings spread, mid-transformation into a pillar of flame."),
    # seals and souls (UI)
    **{f"seal_{n}": (SQUARE, SYMBOL + f"a round infernal seal medallion of blackened iron and gold, the sigil of {n.upper()} engraved at its centre, unlit.")
       for n in ["wrath", "greed", "envy", "pride", "lust", "sloth", "gluttony", "despair", "dominion"]},
    **{f"soul_{n}": (SQUARE, SYMBOL + f"a glowing soul gem, {c}, a faint ghostly face inside, gold claw setting.")
       for n, c in [("wrath", "crimson"), ("greed", "gold"), ("envy", "emerald"), ("pride", "violet"),
                    ("lust", "magenta"), ("sloth", "deep blue"), ("gluttony", "orange")]},
    "apocalypse_crown": (SQUARE, SYMBOL + "the Apocalypse Crown: the Demon King's crown reforged in white-gold fire, seven coloured soul gems set around it."),
    "pact_blood": (TALL, f"An infernal contract scroll, crimson parchment, molten weapons crossed above it, glowing crimson runes, a wax seal of blood, {MAGENTA}."),
    "pact_soul": (TALL, f"An infernal contract scroll, golden parchment, emerald soul crystals above it, green magical runes, an emerald wax seal, {MAGENTA}."),
    # backgrounds
    "bg_base_landscape": (WIDE, "A gigantic infernal fortress on a volcanic plain, rivers of lava, volcanic mountains, demonic statues and burning chains, smoke and embers." + CALM),
    "bg_base_portrait": (TALL, "A gigantic infernal fortress seen from below, rivers of lava at the bottom, volcanic mountains, demonic statues and burning chains." + CALM),
    "bg_bonus_landscape": (WIDE, "Inside the Demon King's throne hall, an obsidian throne, emerald soul flames in braziers, gold and iron pillars." + CALM),
    "bg_takeover_landscape": (WIDE, "The infernal fortress engulfed in crimson light, the sky turned red, the huge silhouette of the Demon King rising behind it." + CALM),
    # frame and logo
    "frame": (SQUARE, f"A square slot reel frame of blackened iron with molten-gold borders and engraved infernal runes, thin (about 6 percent of the width on each side), touching the image edges, the large empty centre flat solid magenta #FF00FF, {MAGENTA}."),
    "logo": (WIDE, f'Game logo lettering reading exactly "INFERNAL KINGDOM" on two lines, forged molten-gold letters with blackened iron edges, small flames, a horned crown above, {MAGENTA}.'),
}


def generate(name):
    size, prompt = ASSETS[name]
    full = prompt + " " + STYLE + ("" if name in ("logo", "l1", "l2", "l3", "l4", "l5") else NO_TEXT)
    body = json.dumps({"model": MODEL, "prompt": full, "size": size, "quality": "high", "n": 1}).encode()
    request = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=body,
        headers={
            "Authorization": "Bearer " + os.environ.get("OPENAI_API_KEY", "sk-placeholder"),
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            data = json.load(response)
    except urllib.error.HTTPError as error:
        return name, "FAILED " + error.read().decode()[:300]
    with open(os.path.join(RAW, name + ".png"), "wb") as f:
        f.write(base64.b64decode(data["data"][0]["b64_json"]))
    return name, "ok"


if __name__ == "__main__":
    os.makedirs(RAW, exist_ok=True)
    names = sys.argv[1:] or [n for n in ASSETS if not os.path.exists(os.path.join(RAW, n + ".png"))]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for name, status in pool.map(generate, names):
            print(name, status, flush=True)
