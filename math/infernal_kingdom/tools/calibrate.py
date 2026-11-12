"""Quick natural-play calibration with in-memory parameter tweaks (nothing is written).

    cd math-sdk && env/bin/python games/infernal_kingdom/tools/calibrate.py BASE_ROUNDS BONUS_ROUNDS
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import natural


def tweak(c):
    pass


def summarize(o, cost):
    sec = {}
    for k, v in o["attrib_rtp"].items():
        s, f = k.split(":")
        sec.setdefault(s, {})[f] = v
    print(f"== {o['mode']} n={o['rounds']} RTP {o['rtp']:.3f} ±{o['rtp_ci95']:.3f} hit {o['hit_rate']:.3f} sd {o['sd_per_bet']:.1f} "
          f"max {o['max_win']:.0f} caps {o['wincap_hits']}")
    for s, d in sec.items():
        print(f"   {s:9s} {sum(d.values()):7.3f} | " + ", ".join(f"{f} {v:.3f}" for f, v in sorted(d.items(), key=lambda kv: -kv[1])))
    for b, v in o["bonus"].items():
        print(f"   bonus {b}: n={v['count']} avg {v['win']/max(v['count'],1):.1f}x (1 in {o['rounds']/v['count']:.0f}) 7souls {v['souls7']} apoc {v['apocalypse']}")


if __name__ == "__main__":
    nb, nf = int(sys.argv[1]), int(sys.argv[2])
    modes = sys.argv[3].split(",") if len(sys.argv) > 3 else ["base", "hellfire", "covenant_blood", "covenant_soul", "abyssal", "furnace_blood", "furnace_soul"]
    for m in modes:
        n = nb if m.startswith("base") else nf
        summarize(natural.run(m, n, quiet=True, tweak=tweak), 1)
