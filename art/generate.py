"""Generate Stormglass Keep art with the OpenAI image API.

    python3 art/generate.py [name ...]      # no names = everything not already in art/raw

Reads OPENAI_API_KEY from the environment. Writes PNGs to art/raw/.
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
    "Painterly stylised game art, hand-painted look with a crisp readable silhouette, storm-lit "
    "lighthouse theme, palette of deep teal and slate blue with warm amber lamp-light accents, soft rim "
    "light, subtle wet-glass reflections, high detail, no watermark, no border."
)
NO_TEXT = " No text, no letters, no numbers."
MAGENTA = "isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background"
SYMBOL = f"Single slot-game symbol icon, centred, filling about 80 percent of the frame, {MAGENTA}: "

SQUARE, WIDE, TALL = "1024x1024", "1536x1024", "1024x1536"

ASSETS = {
    # symbols
    "h1": (SQUARE, SYMBOL + "an ornate antique brass lighthouse keeper's key with a glowing amber gem in the bow, gold rim."),
    "h2": (SQUARE, SYMBOL + "a heavy iron ship's anchor wrapped with wet rope, teal patina, gold rim highlights."),
    "h3": (SQUARE, SYMBOL + "a brass ship's bell on a small bracket, polished, with storm reflections."),
    "h4": (SQUARE, SYMBOL + "an open brass navigator's compass with a glowing needle."),
    "l1": (SQUARE, SYMBOL + "a smooth piece of sea glass, deep ruby red, cut like a faceted heart-shaped gem, inner glow."),
    "l2": (SQUARE, SYMBOL + "a smooth piece of sea glass, warm amber orange, teardrop shape, inner glow."),
    "l3": (SQUARE, SYMBOL + "a smooth piece of sea glass, emerald green, hexagonal shape, inner glow."),
    "l4": (SQUARE, SYMBOL + "a smooth piece of sea glass, cobalt blue, tall diamond shape, inner glow."),
    "l5": (SQUARE, SYMBOL + "a smooth piece of sea glass, pale violet, round pebble shape, inner glow."),
    "w": (SQUARE, SYMBOL + "a jagged bolt of white-gold lightning trapped inside a round glass orb held by a brass ring, crackling energy."),
    "s": (SQUARE, SYMBOL + "a storm lantern with a blazing amber flame, brass frame, short light rays bursting outward."),
    # backgrounds
    "bg_base_landscape": (WIDE, "Night storm seascape seen from a cliff, a tall stone lighthouse on the right third with its amber beam cutting through rain, crashing teal waves, lightning in heavy clouds, the centre of the image kept darker and calmer so a game board can sit over it."),
    "bg_base_portrait": (TALL, "Night storm seascape composed vertically, a tall stone lighthouse rising at the top with its amber beam cutting through rain, lightning in heavy clouds, crashing teal waves at the bottom, the centre of the image kept darker and calmer so a game board can sit over it."),
    "bg_bonus_landscape": (WIDE, "Inside a lighthouse lantern room at the height of a storm, a huge glass lens glowing amber, rain streaming down the tall windows, lightning outside, the centre of the image kept darker and calmer so a game board can sit over it."),
    "bg_drowned_landscape": (WIDE, "A lighthouse lantern room sunk deep underwater, the lamp extinguished, cold blue-green light filtering down from above, drifting bubbles and kelp, eerie and quiet, the centre of the image kept darker and calmer so a game board can sit over it."),
    # frame, logo, tile
    "frame": (SQUARE, f"A square ornate picture frame made of riveted brass and weathered iron lighthouse glazing bars, seen straight on, the frame is thin (about 6 percent of the width on each side) and touches the image edges, the large empty centre is flat solid magenta #FF00FF, {MAGENTA}."),
    "logo": (WIDE, f'Game logo lettering reading exactly "STORMGLASS KEEP" on two lines, bold cast-brass letters with glass inlays lit from within by amber light, a small lightning bolt accent, {MAGENTA}.'),
    "tile_background": (TALL, "Bright storm-lit sky and sea, glowing teal and amber clouds lit from behind by lightning, bright all the way to the edges, no dark vignette, no dark corners."),
    "tile_foreground": (TALL, f"The top of a lighthouse with its lantern blazing amber light and a lightning bolt striking it, large and centred, {MAGENTA}."),
}


def generate(name):
    size, prompt = ASSETS[name]
    full = prompt + " " + STYLE + ("" if name == "logo" else NO_TEXT)
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
