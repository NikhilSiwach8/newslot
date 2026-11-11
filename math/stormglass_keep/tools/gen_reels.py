"""Generate the Stormglass Keep reel strips and print rough first-board statistics.

Standalone (standard library only). Run from anywhere:

    python3 math/stormglass_keep/tools/gen_reels.py            # write reels/*.csv
    python3 math/stormglass_keep/tools/gen_reels.py --stats    # also estimate hit rates

Strips are built from weighted symbol runs so that like symbols stack vertically,
which is what makes 5+ clusters land at a playable rate on a 7x7 board.
"""

import os
import random
import sys

NUM_REELS = 7
NUM_ROWS = 7
STRIP_LEN = 240
MIN_CLUSTER = 5
REELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reels")

# symbol weights, run-length weights, scatters per reel, seed
STRIPS = {
    "BR0": {
        "weights": {"L5": 16, "L4": 15, "L3": 13, "L2": 12, "L1": 11, "H4": 9, "H3": 8, "H2": 7, "H1": 5, "W": 1},
        "runs": {1: 68, 2: 32},
        "scatters": 3,
        "seed": 7101,
    },
    "FR0": {
        "weights": {"L5": 15, "L4": 14, "L3": 13, "L2": 12, "L1": 11, "H4": 9, "H3": 8, "H2": 7, "H1": 6, "W": 3},
        "runs": {1: 64, 2: 36},
        "scatters": 2,
        "seed": 7102,
    },
    "WCAP": {
        "weights": {"L5": 9, "L4": 9, "L3": 10, "L2": 10, "L1": 11, "H4": 11, "H3": 11, "H2": 11, "H1": 12, "W": 7},
        "runs": {1: 45, 2: 40, 3: 15},
        "scatters": 2,
        "seed": 7103,
    },
}


def pick(rng, table):
    return rng.choices(list(table.keys()), weights=list(table.values()))[0]


def build_reel(rng, spec):
    reel = []
    last = None
    while len(reel) < STRIP_LEN:
        sym = pick(rng, spec["weights"])
        if sym == last:
            continue
        run = 1 if sym == "W" else pick(rng, spec["runs"])
        reel.extend([sym] * run)
        last = sym
    reel = reel[:STRIP_LEN]
    # Scatters are spread evenly so no two can show on the same reel at once.
    gap = STRIP_LEN // spec["scatters"]
    offset = rng.randrange(gap)
    for i in range(spec["scatters"]):
        reel[(offset + i * gap + rng.randrange(-4, 5)) % STRIP_LEN] = "S"
    return reel


def build_strip(name):
    spec = STRIPS[name]
    rng = random.Random(spec["seed"])
    return [build_reel(rng, spec) for _ in range(NUM_REELS)]


def write_strip(name, strip):
    path = os.path.join(REELS_DIR, f"{name}.csv")
    with open(path, "w", encoding="UTF-8") as f:
        for pos in range(STRIP_LEN):
            f.write(",".join(strip[reel][pos] for reel in range(NUM_REELS)) + "\n")
    return path


def clusters_on(board):
    """Sizes of every 5+ cluster on a board[reel][row]; wilds join any neighbour."""
    seen = set()
    sizes = []
    for reel in range(NUM_REELS):
        for row in range(NUM_ROWS):
            sym = board[reel][row]
            if (reel, row) in seen or sym in ("W", "S"):
                continue
            local = {(reel, row)}
            stack = [(reel, row)]
            while stack:
                r, c = stack.pop()
                for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                    if 0 <= nr < NUM_REELS and 0 <= nc < NUM_ROWS and (nr, nc) not in local:
                        if board[nr][nc] == sym or board[nr][nc] == "W":
                            local.add((nr, nc))
                            stack.append((nr, nc))
            seen.update(p for p in local if board[p[0]][p[1]] == sym)
            if len(local) >= MIN_CLUSTER:
                sizes.append(len(local))
    return sizes


def stats(name, strip, trials=40000):
    rng = random.Random(99)
    hits = 0
    scatter_counts = {}
    for _ in range(trials):
        board = []
        for reel in range(NUM_REELS):
            stop = rng.randrange(STRIP_LEN)
            board.append([strip[reel][(stop + row) % STRIP_LEN] for row in range(NUM_ROWS)])
        if clusters_on(board):
            hits += 1
        n = sum(col.count("S") for col in board)
        scatter_counts[n] = scatter_counts.get(n, 0) + 1
    print(f"{name}: first-board hit rate {hits / trials:.3f}")
    for n in sorted(scatter_counts):
        if n >= 3:
            print(f"   {n} scatters: 1 in {trials / scatter_counts[n]:.0f}")


if __name__ == "__main__":
    for strip_name in STRIPS:
        built = build_strip(strip_name)
        print("wrote", os.path.relpath(write_strip(strip_name, built)))
        if "--stats" in sys.argv:
            stats(strip_name, built)
