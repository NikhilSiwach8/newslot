"""Natural-play statistics: rounds played exactly as the reels fall, with no criteria
forcing and no redraws. This measures the raw game (trigger rates, feature frequencies,
RTP of the mechanics) before the optimizer re-weights books.

    cd math-sdk && env/bin/python games/infernal_kingdom/tools/natural.py ROUNDS MODE[,MODE] [SEED_OFFSET]

Writes math/infernal_kingdom/reports/natural_<mode>.json.
"""
import json, math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from game_config import GameConfig
from gamestate import GameState
from src.config.distributions import Distribution
from src.wins.win_manager import WinManager


def run(mode, n, offset=0, quiet=False, tweak=None):
    config = GameConfig()
    if tweak:
        tweak(config)
    bm = [b for b in config.bet_modes if b.get_name() == mode][0]
    natural = Distribution(criteria="natural", quota=1, conditions={
        "reel_weights": {config.basegame_type: {"BR0": 1}, config.freegame_type: {"FR0": 1}},
        "natural": True, "force_wincap": False, "force_freegame": False})
    if bm.get_buybonus():
        tier = [d for d in bm.get_distributions() if d.get_criteria() != "wincap"][0]
        natural = Distribution(criteria="natural", quota=1, conditions={
            "reel_weights": {config.basegame_type: {"BR0": 1}, config.freegame_type: {"FR0": 1}},
            "scatter_triggers": tier._conditions["scatter_triggers"], "bonus_tier": tier._conditions["bonus_tier"],
            "force_wincap": False, "force_freegame": True})
    bm._distributions = list(bm._distributions) + [natural]
    gs = GameState(config)
    gs.skip_attribution = True
    gs.betmode = mode
    gs.criteria = "natural"
    gs.win_manager = WinManager(config.basegame_type, config.freegame_type, bm.get_wincap())
    cost = bm.get_cost()
    wins, attrib, stats, bonus = [], {}, {}, {}
    t = time.time()
    for i in range(n):
        gs.library, gs._library_lines, gs._payout_ints = {}, [], []
        gs.run_spin(offset + i)
        w = gs.final_win
        assert w <= config.wincap + 1e-9
        assert abs(sum(gs.attrib.values()) - w) < 0.02, (gs.attrib, w)
        wins.append(w)
        for k, v in gs.attrib.items():
            attrib[k] = attrib.get(k, 0) + v
        for k, v in gs.stats.items():
            if k == "max_cascade":
                stats[k] = max(stats.get(k, 0), v)
            else:
                stats[k] = stats.get(k, 0) + v
            stats[k + "_rounds"] = stats.get(k + "_rounds", 0) + (v > 0)
        if gs.bonus_tier:
            b = bonus.setdefault(gs.bonus_tier, {"count": 0, "win": 0.0, "max": 0.0, "souls7": 0, "apocalypse": 0})
            b["count"] += 1; b["win"] += gs.win_manager.freegame_wins; b["max"] = max(b["max"], w)
            b["souls7"] += gs.stats["seven_souls"]; b["apocalypse"] += gs.stats["apocalypse"]
    mean = sum(wins) / n
    var = sum((x - mean) ** 2 for x in wins) / (n - 1)
    out = {
        "mode": mode, "rounds": n, "cost": cost, "seconds": round(time.time() - t, 1),
        "rtp": mean / cost, "rtp_ci95": 1.96 * math.sqrt(var / n) / cost,
        "sd_per_bet": math.sqrt(var) / cost, "hit_rate": sum(1 for x in wins if x > 0) / n,
        "max_win": max(wins), "wincap_hits": sum(1 for x in wins if x >= config.wincap),
        "attrib_rtp": {k: v / n / cost for k, v in sorted(attrib.items())},
        "stats": stats, "bonus": bonus,
    }
    if not quiet:
        os.makedirs(os.path.join(HERE, "..", "reports"), exist_ok=True)
        with open(os.path.join(HERE, "..", "reports", f"natural_{mode}.json"), "w") as f:
            json.dump(out, f, indent=1)
    return out


if __name__ == "__main__":
    n = int(sys.argv[1])
    offset = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    for mode in sys.argv[2].split(","):
        o = run(mode, n, offset)
        print(f"{mode:15s} n={n} {o['seconds']}s RTP {o['rtp']:.4f} ±{o['rtp_ci95']:.4f} hit {o['hit_rate']:.3f} "
              f"sd {o['sd_per_bet']:.1f} max {o['max_win']:.0f}")
        top = sorted(o["attrib_rtp"].items(), key=lambda kv: -kv[1])[:12]
        print("   ", ", ".join(f"{k} {v:.3f}" for k, v in top))
        print("   ", {k: (v["count"], round(v["win"] / max(v["count"], 1), 1)) for k, v in o["bonus"].items()})
