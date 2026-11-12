"""Generate the Infernal Kingdom reel strips (standard library only).

    python3 math/infernal_kingdom/tools/gen_reels.py

Strips hold regular symbols, Infernal Wilds (W, reels 2-6) and Hell Gate scatters (S).
Wild Bombs, Golden Wild Bombs, Split Symbols, Hellstars and Demon Overlords are not on
the strips: they land through per-cell landing rates set in game_config.py, so their
frequency can be tuned independently of the strip layout.
"""

import os
import random

NUM_REELS = 6
NUM_ROWS = 4
STRIP_LEN = 260
REELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reels")

STRIPS = {
    # Base game.
    "BR0": {
        "weights": {"H1": 5, "H2": 6, "H3": 7, "H4": 8, "H5": 9, "L1": 11, "L2": 12, "L3": 13, "L4": 14, "L5": 15},
        "wilds": [0, 3, 3, 3, 3, 3],
        "scatters": [3, 3, 3, 3, 3, 3],
        "runs": {1: 70, 2: 30},
        "seed": 6601,
    },
    # All four bonuses.
    "FR0": {
        "weights": {"H1": 6, "H2": 7, "H3": 8, "H4": 9, "H5": 10, "L1": 11, "L2": 11, "L3": 12, "L4": 12, "L5": 13},
        "wilds": [0, 4, 4, 4, 4, 4],
        "scatters": [3, 3, 3, 3, 3, 3],
        "runs": {1: 65, 2: 35},
        "seed": 6602,
    },
    # Max-win distribution only: richer premium mix and more wilds so a 66,666x round
    # can be found in reasonable time. Same rules, different strip.
    "WCAP": {
        "weights": {"H1": 12, "H2": 12, "H3": 11, "H4": 11, "H5": 10, "L1": 9, "L2": 9, "L3": 8, "L4": 8, "L5": 8},
        "wilds": [0, 10, 10, 10, 10, 10],
        "scatters": [3, 3, 3, 3, 3, 3],
        "runs": {1: 45, 2: 40, 3: 15},
        "seed": 6603,
    },
}


def pick(rng, table):
    return rng.choices(list(table), weights=list(table.values()))[0]


def build_reel(rng, spec, reel):
    body = []
    last = None
    n_special = spec["wilds"][reel] + spec["scatters"][reel]
    while len(body) < STRIP_LEN - n_special:
        sym = pick(rng, spec["weights"])
        if sym == last:
            continue
        body.extend([sym] * pick(rng, spec["runs"]))
        last = sym
    body = body[: STRIP_LEN - n_special]
    # Scatters evenly spaced (gap >= NUM_ROWS, so at most one shows per reel);
    # wilds placed at random positions away from scatters.
    strip = list(body)
    step = STRIP_LEN // max(1, spec["scatters"][reel]) if spec["scatters"][reel] else None
    for i in range(spec["scatters"][reel]):
        strip.insert(min(len(strip), i * step + rng.randrange(step // 2)), "S")
    for _ in range(spec["wilds"][reel]):
        while True:
            pos = rng.randrange(len(strip))
            window = [strip[(pos + d) % len(strip)] for d in range(-NUM_ROWS, NUM_ROWS)]
            if "S" not in window and "W" not in window[NUM_ROWS - 1 : NUM_ROWS + 1]:
                strip.insert(pos, "W")
                break
    return strip[:STRIP_LEN] if len(strip) > STRIP_LEN else strip


def check_scatter_gap(strip):
    idx = [i for i, s in enumerate(strip) if s == "S"]
    for a, b in zip(idx, idx[1:] + [idx[0] + len(strip)]):
        assert b - a >= NUM_ROWS, "two scatters could show on one reel"


def main():
    os.makedirs(REELS_DIR, exist_ok=True)
    for name, spec in STRIPS.items():
        rng = random.Random(spec["seed"])
        reels = [build_reel(rng, spec, r) for r in range(NUM_REELS)]
        for r in reels:
            if "S" in r:
                check_scatter_gap(r)
        length = min(len(r) for r in reels)
        reels = [r[:length] for r in reels]
        with open(os.path.join(REELS_DIR, f"{name}.csv"), "w", encoding="utf-8") as f:
            for row in range(length):
                f.write(",".join(reels[r][row] for r in range(NUM_REELS)) + "\n")
        print(name, "length", length, {s: sum(r.count(s) for r in reels) for s in ("W", "S")})


if __name__ == "__main__":
    main()
