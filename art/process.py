"""Cut generated art out of its magenta background and size it for the game.

    python3 art/process.py            # art/raw/*.png -> art/processed/*.png (+ preview.png)

Symbols are keyed, trimmed, centred on a square canvas and scaled to SYMBOL_PX.
Needs Pillow and numpy.
"""

import glob
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OUT = os.path.join(HERE, "processed")
SYMBOL_PX = 256  # board cells are 110px; 256 keeps symbols sharp on high-density screens
SYMBOL_FILL = 0.92  # share of the canvas the trimmed symbol may occupy
SYMBOLS = ["h1", "h2", "h3", "h4", "h5", "l1", "l2", "l3", "l4", "l5", "w", "hs", "s", "wb", "gb", "sp", "do"]
KEYED = set(SYMBOLS) | {"frame", "logo", "apocalypse_crown", "pact_blood", "pact_soul"} | {f"seal_{n}" for n in ["wrath", "greed", "envy", "pride", "lust", "sloth", "gluttony", "despair", "dominion"]} | {f"soul_{n}" for n in ["wrath", "greed", "envy", "pride", "lust", "sloth", "gluttony"]}


def key_out_magenta(image):
    """Return RGBA with the magenta background transparent.

    Only background connected to the image border is removed (flood fill from the edges), so
    purple or pink areas inside a symbol's outline are never eaten by the key.
    """
    rgb = image.convert("RGB")
    marker = (1, 254, 3)  # a colour that does not occur in the art
    filled = rgb.copy()
    w, h = filled.size
    step = max(1, min(w, h) // 40)
    seeds = [(x, y) for x in range(0, w, step) for y in (0, h - 1)] + [(x, y) for y in range(0, h, step) for x in (0, w - 1)]
    for seed in seeds:
        r, g, b = filled.getpixel(seed)
        if min(r, b) - g > 120:  # still magenta, i.e. not already filled and not part of the art
            ImageDraw.floodfill(filled, seed, marker, thresh=110)
    background = np.all(np.asarray(filled) == marker, axis=-1)

    pixels = np.asarray(rgb).astype(np.float32)
    # enclosed holes (a key's bow, an anchor's ring): remove only near-pure magenta there
    pure_magenta = (pixels[..., 0] > 215) & (pixels[..., 2] > 215) & (pixels[..., 1] < 70)
    background |= pure_magenta
    alpha = Image.fromarray(((~background) * 255).astype(np.uint8))
    # shave the outer pixel and soften, so no magenta fringe survives on the outline
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    # despill only in a thin band next to the removed background
    near_background = np.asarray(Image.fromarray((background * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7))) > 0
    excess = np.clip(np.minimum(pixels[..., 0], pixels[..., 2]) - pixels[..., 1], 0, None) * near_background
    pixels[..., 0] -= excess * 0.9
    pixels[..., 2] -= excess * 0.9
    result = Image.fromarray(np.clip(pixels, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    result.putalpha(alpha)
    return result


def to_square(image, size, fill):
    bbox = image.getchannel("A").point(lambda v: 255 if v > 16 else 0).getbbox()
    trimmed = image.crop(bbox)
    scale = size * fill / max(trimmed.size)
    resized = trimmed.resize((max(1, round(trimmed.width * scale)), max(1, round(trimmed.height * scale))), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(resized, ((size - resized.width) // 2, (size - resized.height) // 2), resized)
    return canvas


def preview(done):
    names = [n for n in SYMBOLS if n in done]
    if not names:
        return
    cell = 96
    sheet = Image.new("RGBA", (cell * len(names), cell * 2), (16, 32, 44, 255))
    for i, name in enumerate(names):
        symbol = Image.open(os.path.join(OUT, name + ".png"))
        for row, px in enumerate((80, 48)):
            small = symbol.resize((px, px), Image.LANCZOS)
            sheet.paste(small, (i * cell + (cell - px) // 2, row * cell + (cell - px) // 2), small)
    sheet.convert("RGB").save(os.path.join(OUT, "preview.png"))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    done = []
    for path in sorted(glob.glob(os.path.join(RAW, "*.png"))):
        name = os.path.splitext(os.path.basename(path))[0]
        image = Image.open(path)
        if name in KEYED:
            image = key_out_magenta(image)
            if name in SYMBOLS:
                image = to_square(image, SYMBOL_PX, SYMBOL_FILL)
        image.save(os.path.join(OUT, name + ".png"))
        done.append(name)
        print(name, image.size)
    preview(done)
