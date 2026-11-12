"""Pack processed art into the web app's static folder.

    python3 art/placeholders.py && python3 art/build_game_assets.py   # placeholders
    python3 art/process.py && python3 art/build_game_assets.py        # generated art

Writes web-sdk/apps/infernal_kingdom/static/assets/infernal/:
  symbols.png + symbols.json   sprite sheet, frames named ik_<symbol>.png
  bg_*.webp                    backgrounds
"""

import json
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "processed")
OUT = os.path.join(HERE, "..", "web-sdk", "apps", "infernal_kingdom", "static", "assets", "infernal")
SYMBOLS = ["h1", "h2", "h3", "h4", "h5", "l1", "l2", "l3", "l4", "l5", "w", "hs", "s", "wb", "gb", "sp", "do"]
BACKGROUNDS = ["bg_base_landscape", "bg_base_portrait", "bg_bonus_landscape", "bg_takeover_landscape"]
CELL, PAD, COLUMNS = 256, 2, 4


def build_symbol_sheet():
    rows = -(-len(SYMBOLS) // COLUMNS)
    step = CELL + PAD * 2
    sheet = Image.new("RGBA", (COLUMNS * step, rows * step), (0, 0, 0, 0))
    frames = {}
    for index, name in enumerate(SYMBOLS):
        symbol = Image.open(os.path.join(SRC, name + ".png")).convert("RGBA")
        x, y = (index % COLUMNS) * step + PAD, (index // COLUMNS) * step + PAD
        sheet.paste(symbol, (x, y))
        frames[f"ik_{name}.png"] = {
            "frame": {"x": x, "y": y, "w": CELL, "h": CELL},
            "rotated": False,
            "trimmed": False,
            "spriteSourceSize": {"x": 0, "y": 0, "w": CELL, "h": CELL},
            "sourceSize": {"w": CELL, "h": CELL},
            "pivot": {"x": 0.5, "y": 0.5},
        }
    sheet.save(os.path.join(OUT, "symbols.png"), optimize=True)
    meta = {"image": "symbols.png", "format": "RGBA8888", "size": {"w": sheet.width, "h": sheet.height}, "scale": "1"}
    with open(os.path.join(OUT, "symbols.json"), "w", encoding="utf-8") as f:
        json.dump({"frames": frames, "meta": meta}, f, indent=1)


def build_backgrounds():
    for name in BACKGROUNDS:
        path = os.path.join(SRC, name + ".png")
        if os.path.exists(path):
            Image.open(path).convert("RGB").save(os.path.join(OUT, name + ".webp"), quality=86, method=6)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    build_symbol_sheet()
    build_backgrounds()
    for entry in sorted(os.listdir(OUT)):
        print(entry, os.path.getsize(os.path.join(OUT, entry)) // 1024, "KB")
