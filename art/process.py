"""Cut generated art out of its magenta background and size it for the game.

    python3 art/process.py            # art/raw/*.png -> art/processed/*.png (+ preview.png)

Symbols are keyed, trimmed, centred on a square canvas and scaled to SYMBOL_PX.
Needs Pillow and numpy.
"""

import glob
import os

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OUT = os.path.join(HERE, "processed")
SYMBOL_PX = 256  # board cells are 80px; 256 keeps symbols sharp on high-density screens
SYMBOL_FILL = 0.92  # share of the canvas the trimmed symbol may occupy
KEYED = {"h1", "h2", "h3", "h4", "l1", "l2", "l3", "l4", "l5", "w", "s", "frame", "logo", "tile_foreground"}
SYMBOLS = ["h1", "h2", "h3", "h4", "l1", "l2", "l3", "l4", "l5", "w", "s"]


def key_out_magenta(image):
    """Return RGBA with the magenta background transparent and fringe colour removed."""
    rgb = np.asarray(image.convert("RGB")).astype(np.float32)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    # "magenta-ness": how far red and blue both sit above green
    excess = np.minimum(r, b) - g
    alpha = np.clip((150.0 - excess) / 90.0, 0.0, 1.0)  # >=150 fully background, <=60 fully kept
    # despill: pull red/blue back towards green where a magenta cast remains on edge pixels
    spill = np.clip(excess, 0, None) * (alpha < 1.0)
    rgb[..., 0] = r - spill * 0.9
    rgb[..., 2] = b - spill * 0.9
    out = np.dstack([np.clip(rgb, 0, 255), alpha * 255.0]).astype(np.uint8)
    result = Image.fromarray(out, "RGBA")
    # shave half a pixel off the edge so no fringe survives
    a = result.getchannel("A").filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.6))
    result.putalpha(a)
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
