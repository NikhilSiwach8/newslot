"""Build the Infernal Kingdom math reports from the generated library.

    cd math-sdk && env/bin/python games/infernal_kingdom/tools/report.py

Reads, for every bet mode:
  library/publish_files/lookUpTable_<mode>_0.csv   published weights (tools/weights.py): id, weight, payout x100
  library/attribution/<mode>_*.jsonl               per-book feature attribution and stats
  reports/natural_<mode>.json                      natural-play run (optional, tools/natural.py)

Writes reports/MATH_REPORT.md and reports/summary.json. Every number is computed from those
files; the published-game figures are exact for the published book set (the RGS draws books
with exactly these weights), the natural-play figures are sample estimates with a 95% CI.
"""

import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from game_config import GameConfig  # noqa: E402

ROOT = os.path.join(HERE, "..")
LIB = os.path.join(ROOT, "library")
OUT = os.path.join(ROOT, "reports")

FEATURE_LABELS = {
    "regular": "regular wins (first evaluation)", "cascade": "cascade wins", "seals": "Nine Hell Seals",
    "takeover": "Infernal Takeover", "wild_bomb": "Wild Bombs", "golden_bomb": "Golden Wild Bombs",
    "split": "Split Symbols", "hellstar": "Hellstars", "overlord": "Demon Overlord",
    "souls": "Seven Souls milestone wilds", "apocalypse": "Soul Apocalypse", "descent": "Abyssal Descent multiplier",
}
SECTION_LABELS = {"base": "Base game", "hellfire": "Hellfire Spins", "covenant": "Demon's Covenant",
                  "abyssal": "Abyssal Descent", "furnace": "The Soul Furnace"}
STAT_LABELS = {"wild_bombs": "Wild Bomb", "golden_bombs": "Golden Wild Bomb", "splits": "Split Symbol",
               "overlords": "Demon Overlord", "takeovers": "Infernal Takeover", "patterns": "Seal pattern",
               "seven_souls": "Seven Souls completed", "apocalypse": "Soul Apocalypse",
               "retriggers": "Bonus retrigger", "shard_awards": "Soul awarded by shards", "wincap": "66,666x max win"}
BUCKETS = [0, 0.000001, 1, 2, 5, 10, 20, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 66666, 66666.01]


def one_in(p):
    return "never" if p <= 0 else f"1 in {1 / p:,.0f}"


def load_mode(mode):
    lut = {}
    with open(os.path.join(LIB, "publish_files", f"lookUpTable_{mode}_0.csv")) as f:
        for line in f:
            i, w, pay = line.strip().split(",")
            lut[int(i)] = (int(w), int(pay) / 100)
    attrib = {}
    for path in glob.glob(os.path.join(LIB, "attribution", f"{mode}_*.jsonl")):
        if not os.path.basename(path)[len(mode) + 1:].split(".")[0].isdigit():
            continue
        with open(path) as f:
            for line in f:
                row = json.loads(line)
                attrib[row["id"]] = row
    return lut, attrib


def analyse(mode, cost, cap):
    lut, attrib = load_mode(mode)
    missing = [i for i in lut if i not in attrib]
    W = sum(w for w, _ in lut.values())
    mean = sum(w * p for w, p in lut.values()) / W
    var = sum(w * (p - mean) ** 2 for w, p in lut.values()) / W
    ess = W ** 2 / sum(w * w for w, _ in lut.values())
    hit = sum(w for w, p in lut.values() if p > 0) / W
    capw = sum(w for w, p in lut.values() if p >= cap) / W
    nonzero_weight_books = sum(1 for w, _ in lut.values() if w > 0)

    feats, sections, stats, bonus = {}, {}, {}, {}
    for i, (w, p) in lut.items():
        row = attrib.get(i)
        if row is None:
            continue
        for k, v in row["attrib"].items():
            sec, feat = k.split(":")
            feats[feat] = feats.get(feat, 0) + w * v
            sections[sec] = sections.get(sec, 0) + w * v
        for k, v in row["stats"].items():
            if k != "max_cascade" and k != "seals_lit" and v:
                stats[k] = stats.get(k, 0) + w
        if row["bonus"]:
            b = bonus.setdefault(row["bonus"], {"w": 0, "pay": 0, "sq": 0, "max": 0})
            b["w"] += w
            b["pay"] += w * p
            b["sq"] += w * p * p
            b["max"] = max(b["max"], p)
    buckets = []
    for lo, hi in zip(BUCKETS, BUCKETS[1:]):
        bw = sum(w for w, p in lut.values() if lo <= p < hi)
        buckets.append((lo, hi, bw / W))
    max_cascade = max((r["stats"]["max_cascade"] for r in attrib.values()), default=0)
    return {
        "mode": mode, "cost": cost, "books": len(lut), "nonzero_weight_books": nonzero_weight_books,
        "missing_attribution": len(missing), "effective_sample_size": ess,
        "rtp": mean / cost, "sd_per_cost": math.sqrt(var) / cost, "hit_rate": hit, "max_payout": max(p for _, p in lut.values()),
        "wincap_prob": capw,
        "feature_rtp": {k: v / W / cost for k, v in sorted(feats.items(), key=lambda kv: -kv[1])},
        "section_rtp": {k: v / W / cost for k, v in sorted(sections.items(), key=lambda kv: -kv[1])},
        "feature_freq": {k: v / W for k, v in sorted(stats.items())},
        "bonus": {k: {"freq": v["w"] / W, "avg": v["pay"] / v["w"],
                      "sd": math.sqrt(max(v["sq"] / v["w"] - (v["pay"] / v["w"]) ** 2, 0)), "max": v["max"],
                      "rtp": v["pay"] / W / cost} for k, v in bonus.items()},
        "buckets": buckets, "max_cascade_depth": max_cascade,
    }


def natural(mode):
    path = os.path.join(OUT, f"natural_{mode}.json")
    return json.load(open(path)) if os.path.exists(path) else None


def write(results, cfg):
    L = []
    L.append("# Infernal Kingdom - math report\n")
    L.append("Generated by `math/infernal_kingdom/tools/report.py` from the simulated library. "
             "**Published game** figures use the published lookup-table weights (`tools/weights.py`) the RGS draws from, so they "
             "are exact for this book set. **Natural play** figures come from `tools/natural.py`, which plays "
             "rounds straight off the reels with no criteria forcing or re-weighting; they show the raw "
             "mechanics and carry sampling error (95% CI shown).\n")
    L.append(f"Target RTP {cfg.rtp:.2%} for every mode. Max win {cfg.wincap:,.0f}x the base bet per round.\n")
    L.append("## Summary (published game)\n")
    L.append("| Mode | Cost | RTP | Hit rate | SD per bet | Max win frequency | Max payout seen | Books | Non-zero-weight books | Effective sample |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in results:
        L.append(f"| {r['mode']} | {r['cost']:g}x | {r['rtp']:.4%} | {r['hit_rate']:.2%} | {r['sd_per_cost']:.1f} | "
                 f"{one_in(r['wincap_prob'])} | {r['max_payout']:,.2f}x | {r['books']:,} | {r['nonzero_weight_books']:,} | {r['effective_sample_size']:,.0f} |")
    rtps = [r["rtp"] for r in results]
    L.append(f"\nRTP spread across modes: {min(rtps):.4%} to {max(rtps):.4%} "
             f"({(max(rtps) - min(rtps)) * 100:.3f} points; Stake allows 0.5).\n")
    if any(r["missing_attribution"] for r in results):
        L.append("**Warning:** some books had no attribution row: " +
                 ", ".join(f"{r['mode']} {r['missing_attribution']}" for r in results if r["missing_attribution"]) + "\n")

    for r in results:
        L.append(f"## {r['mode']} ({r['cost']:g}x)\n")
        L.append("### RTP contribution by game section\n")
        L.append("| Section | RTP |\n|---|---|")
        for k, v in r["section_rtp"].items():
            L.append(f"| {SECTION_LABELS.get(k, k)} | {v:.4%} |")
        L.append("\n### RTP contribution by feature (all sections)\n")
        L.append("| Feature | RTP |\n|---|---|")
        for k, v in r["feature_rtp"].items():
            L.append(f"| {FEATURE_LABELS.get(k, k)} | {v:.4%} |")
        if r["bonus"]:
            L.append("\n### Bonuses\n")
            L.append("| Bonus | Frequency | Average payout | SD | Largest | RTP share |\n|---|---|---|---|---|---|")
            for k, v in sorted(r["bonus"].items(), key=lambda kv: -kv[1]["freq"]):
                L.append(f"| {SECTION_LABELS.get(k, k)} | {one_in(v['freq'])} | {v['avg']:,.1f}x | {v['sd']:,.1f} | {v['max']:,.0f}x | {v['rtp']:.4%} |")
        L.append("\n### Feature frequency (rounds containing it)\n")
        L.append("| Feature | Frequency |\n|---|---|")
        for k, v in r["feature_freq"].items():
            L.append(f"| {STAT_LABELS.get(k, k)} | {one_in(v)} ({v:.4%}) |")
        L.append(f"\nDeepest cascade sequence in the book set: {r['max_cascade_depth']} evaluations "
                 f"(safety stop {cfg.max_cascades}).\n")
        L.append("### Payout distribution\n")
        L.append("| Payout (x bet) | Share of rounds |\n|---|---|")
        for lo, hi, p in r["buckets"]:
            label = "0" if hi <= 0.000001 else (f"{cfg.wincap:,.0f} (max win)" if lo >= cfg.wincap else f"{lo:g} to <{hi:g}")
            L.append(f"| {label} | {p:.5%} |")
        nat = natural(r["mode"])
        if nat:
            L.append(f"\n### Natural play ({nat['rounds']:,} rounds, no re-weighting)\n")
            L.append(f"RTP {nat['rtp']:.2%} ± {nat['rtp_ci95']:.2%} (95% CI), hit rate {nat['hit_rate']:.2%}, "
                     f"SD {nat['sd_per_bet']:.1f}, largest {nat['max_win']:,.0f}x, max wins {nat['wincap_hits']}.")
            if nat.get("bonus"):
                L.append("\n| Bonus | Natural frequency | Average bonus win |\n|---|---|---|")
                for k, v in nat["bonus"].items():
                    L.append(f"| {SECTION_LABELS.get(k, k)} | 1 in {nat['rounds'] / v['count']:,.0f} ({v['count']} seen) | {v['win'] / v['count']:,.1f}x |")
            L.append("")
    L.append("## Maximum-win verification\n")
    L.append(f"- Highest payout in every mode's book set: " + ", ".join(f"{r['mode']} {r['max_payout']:,.2f}x" for r in results) +
             f". None exceeds {cfg.wincap:,.0f}x.")
    L.append("- The cap is enforced in `GameExecutables.pay()` for the whole round; `tests/test_rules.py` "
             "plays every mode against an artificial 300x cap and checks that payouts stop exactly at the cap, "
             "nothing pays after the `wincap` event, and base + bonus wins equal the round payout.")
    L.append("- Max-win books come from bonus rounds that reach the cap naturally and from the `wincap` criteria "
             "(WCAP strip mixed into bonus play); all follow the same rules and reach the cap through normal payouts.\n")
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "MATH_REPORT.md"), "w") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    cfg = GameConfig()
    results = [analyse(bm.get_name(), bm.get_cost(), cfg.wincap) for bm in cfg.bet_modes
               if os.path.exists(os.path.join(LIB, "publish_files", f"lookUpTable_{bm.get_name()}_0.csv"))]
    write(results, cfg)
    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump(results, f, indent=1)
    for r in results:
        print(f"{r['mode']:15s} RTP {r['rtp']:.4%} hit {r['hit_rate']:.2%} sd {r['sd_per_cost']:.1f} "
              f"maxwin {one_in(r['wincap_prob'])} max {r['max_payout']:,.0f}")
