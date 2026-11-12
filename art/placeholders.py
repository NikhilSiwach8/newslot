"""Draw labelled placeholder art for Infernal Kingdom (Pillow only).

    python3 art/placeholders.py && python3 art/build_game_assets.py

Writes art/processed/<name>.png with the same names and sizes the final art will use
(see docs/ASSET_MANIFEST.md), so real art can replace these files one for one. Every
placeholder is marked PLACEHOLDER: none of it may ship.
"""

import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "processed")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
PX = 256

GOLD, CRIMSON, ORANGE, OBSIDIAN, IRON = "#D6A04A", "#A51D24", "#FF6A00", "#080708", "#211A1A"
EMERALD, VIOLET = "#14B86E", "#923DCE"

# name: (label, sublabel, fill, ink)
SYMBOLS = {
    "h1": ("DEMON", "KING", CRIMSON, GOLD),
    "h2": ("DRAGON", "", "#7A2A10", ORANGE),
    "h3": ("CROWN", "", IRON, CRIMSON),
    "h4": ("CHALICE", "", "#5C1015", GOLD),
    "h5": ("RING", "", "#183A2A", EMERALD),
    "l1": ("A", "", "#2A0C0E", CRIMSON),
    "l2": ("K", "", "#2A200C", GOLD),
    "l3": ("Q", "", "#0C2A1C", EMERALD),
    "l4": ("J", "", "#1E2226", "#C9CED6"),
    "l5": ("10", "", "#2A1A0C", "#B87333"),
    "w": ("WILD", "", OBSIDIAN, GOLD),
    "hs": ("HELL", "STAR", "#3A0A00", ORANGE),
    "s": ("HELL", "GATE", "#24083A", VIOLET),
    "wb": ("WILD", "BOMB", "#3A0C0C", ORANGE),
    "gb": ("GOLDEN", "BOMB", "#3A2A08", GOLD),
    "sp": ("SPLIT", "", "#141414", "#E8E8E8"),
    "do": ("OVER", "LORD", "#1A0006", CRIMSON),
}

BACKGROUNDS = {
    "bg_base_landscape": ((1920, 1080), "#1A0606", ORANGE),
    "bg_base_portrait": ((1080, 1920), "#1A0606", ORANGE),
    "bg_bonus_landscape": ((1920, 1080), "#0C1A12", EMERALD),
    "bg_takeover_landscape": ((1920, 1080), "#2A0004", CRIMSON),
}


def font(path, size):
    return ImageFont.truetype(path, size)


def centred(draw, y, text, f, fill):
    w = draw.textlength(text, font=f)
    draw.text(((PX - w) / 2, y), text, font=f, fill=fill)


def symbol(name, label, sub, fill, ink):
    img = Image.new("RGBA", (PX, PX), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((10, 10, PX - 10, PX - 10), radius=34, fill=fill, outline=GOLD, width=8)
    d.rounded_rectangle((24, 24, PX - 24, PX - 24), radius=24, outline=ink, width=3)
    size = 96 if len(label) <= 2 else (44 if len(label) <= 6 else 36)
    top = 70 if sub else (PX - size) / 2 - 18
    centred(d, top, label, font(FONT, size), ink)
    if sub:
        centred(d, top + size + 8, sub, font(FONT, 40), ink)
    centred(d, PX - 46, "PLACEHOLDER", font(SANS, 14), "#FFFFFF80")
    img.save(os.path.join(OUT, name + ".png"))


def background(name, size, base, glow):
    w, h = size
    img = Image.new("RGB", size, base)
    d = ImageDraw.Draw(img)
    for i in range(6):  # lava rivers along the bottom, fortress silhouette behind
        y = h * (0.78 + i * 0.035)
        d.ellipse((-w * 0.2 + i * 90, y, w * 0.6 + i * 140, y + h * 0.05), fill=glow)
    d.polygon([(w * 0.1, h * 0.75), (w * 0.2, h * 0.3), (w * 0.3, h * 0.75)], fill=OBSIDIAN)
    d.polygon([(w * 0.7, h * 0.75), (w * 0.82, h * 0.22), (w * 0.94, h * 0.75)], fill=OBSIDIAN)
    d.rectangle((w * 0.35, h * 0.35, w * 0.65, h * 0.75), fill=IRON)
    img = img.filter(ImageFilter.GaussianBlur(radius=max(w, h) / 160))
    d = ImageDraw.Draw(img)
    text = "PLACEHOLDER BACKGROUND"
    f = font(SANS, int(min(w, h) / 30))
    d.text((24, 24), text, font=f, fill="#FFFFFF")
    img.save(os.path.join(OUT, name + ".png"))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for n, spec in SYMBOLS.items():
        symbol(n, *spec)
    for n, (size, base, glow) in BACKGROUNDS.items():
        background(n, size, base, glow)
    print("wrote", len(SYMBOLS), "symbols and", len(BACKGROUNDS), "backgrounds to", OUT)
