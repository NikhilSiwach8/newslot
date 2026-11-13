"""Deterministic lookup-table weights for Infernal Kingdom (replaces the SDK optimizer).

    cd math-sdk && env/bin/python games/infernal_kingdom/tools/weights.py

Why: the SDK optimizer met the RTP targets but reshaped the base game badly. Natural play
has about a quarter of its winning base spins at 1x-5x; the optimizer left 0.6%, a gap
Stake's review flags. Here each criteria group gets exactly the probability its targets in
game_optimization.py imply, and inside a group books are weighted

    w(book) ~ (1 + payout) ** theta

with theta solved so the group mean hits its RTP share. theta = 0 is natural play; a small
theta is the gentlest change that hits the target, so the natural shape of wins survives.
Every book keeps a non-zero weight.

Writes library/publish_files/lookUpTable_<mode>_0.csv (id, weight, payout x100), the file
the optimizer would write; run.py then regenerates configs and runs the Stake checks.
"""

import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from game_config import GameConfig  # noqa: E402
from game_optimization import OptimizationSetup  # noqa: E402

LIB = os.path.join(HERE, "..", "library")
TOTAL_WEIGHT = 10 ** 15  # integer weights sum to about this (well inside uint64)


def read_books(mode):
    lut = []
    with open(os.path.join(LIB, "lookup_tables", f"lookUpTable_{mode}.csv")) as f:
        for line in f:
            i, _, pay = line.strip().split(",")
            lut.append((int(i), int(pay)))
    crit = {}
    for path in glob.glob(os.path.join(LIB, "attribution", f"{mode}_*.jsonl")):
        if not os.path.basename(path)[len(mode) + 1:].split(".")[0].isdigit():
            continue
        with open(path) as f:
            for line in f:
                row = json.loads(line)
                crit[row["id"]] = row["criteria"]
    missing = [i for i, _ in lut if i not in crit]
    assert not missing, f"{mode}: {len(missing)} books have no criteria record"
    return lut, crit


def tilt(payouts, target_mean, prior=None):
    """theta with mean of prior * (1+x)^theta-weighted payouts == target_mean (bisection)."""
    logs = [math.log1p(x) for x in payouts]
    prior = prior or [1.0] * len(payouts)
    lp = [math.log(p) for p in prior]

    def mean(theta):
        m = max(theta * l + q for l, q in zip(logs, lp))
        ws = [math.exp(theta * l + q - m) for l, q in zip(logs, lp)]
        return sum(w * x for w, x in zip(ws, payouts)) / sum(ws), ws

    lo, hi = -8.0, 8.0
    if not (mean(lo)[0] <= target_mean <= mean(hi)[0]):
        raise ValueError(f"target mean {target_mean:.4f} outside reachable range "
                         f"[{mean(lo)[0]:.4f}, {mean(hi)[0]:.4f}]")
    for _ in range(200):
        mid = (lo + hi) / 2
        if mean(mid)[0] < target_mean:
            lo = mid
        else:
            hi = mid
    theta = (lo + hi) / 2
    return theta, mean(theta)[1]


def group_targets(config, mode):
    """{criteria: (probability, mean payout)} from the optimizer targets of this mode."""
    bm = [b for b in config.bet_modes if b.get_name() == mode][0]
    cost = bm.get_cost()
    conds = config.opt_params[mode]["conditions"]
    out = {}
    rest_prob = 1.0
    rest = None
    for crit, c in conds.items():
        rtp, hr = c["rtp"], c.get("hr")
        if crit == "wincap":
            prob = rtp * cost / config.wincap
        elif crit == "0":
            out[crit] = None  # filled with whatever probability remains
            continue
        elif hr in (None, "x"):
            rest = crit
            out[crit] = (None, rtp)
            continue
        else:
            prob = 1.0 / hr
        out[crit] = (prob, rtp * cost / prob if prob else 0.0)
        rest_prob -= prob
    if rest is not None:  # buy modes: the bonus takes all remaining probability
        _, rtp = out[rest]
        out[rest] = (rest_prob, rtp * cost / rest_prob)
        rest_prob = 0.0
    if "0" in out:
        out["0"] = (rest_prob, 0.0)
    assert rest_prob >= -1e-12
    return out, cost


def weigh_mode(config, mode, tail_factor=1.0, tail_from=10_000):
    """tail_factor < 1 down-weights non-max-win books paying tail_from x or more (theta then
    re-balances the mean, moving weight into the rest of the range)."""
    lut, crit = read_books(mode)
    targets, cost = group_targets(config, mode)
    weights = {}
    report = []
    for c, (prob, mean) in targets.items():
        ids = [(i, p / 100) for i, p in lut if crit[i] == c]
        assert ids, f"{mode}: no books for criteria {c}"
        pays = [p for _, p in ids]
        if max(pays) - min(pays) < 1e-9:
            theta, ws = 0.0, [1.0] * len(ids)
        else:
            prior = [tail_factor if (c != "wincap" and p >= tail_from) else 1.0 for p in pays]
            theta, ws = tilt(pays, mean, prior)
        s = sum(ws)
        for (i, _), w in zip(ids, ws):
            weights[i] = max(1, round(TOTAL_WEIGHT * prob * w / s))
        report.append((c, len(ids), prob, mean, theta))
    W = sum(weights.values())
    rtp = sum(weights[i] * p / 100 for i, p in lut) / W / cost
    path = os.path.join(LIB, "publish_files", f"lookUpTable_{mode}_0.csv")
    with open(path, "w") as f:
        for i, p in lut:
            f.write(f"{i},{weights[i]},{p}\n")
    return rtp, report


TAIL_STEPS = [1.0, 0.8, 0.6, 0.45, 0.35, 0.25, 0.18, 0.12, 0.08]


def risk_failures(config, mode):
    """Stake Studio risk-check failures for the LUT just written (the SDK's own definitions)."""
    import contextlib
    import io as _io
    from utils.rgs_verification import verify_lookup_format, get_lut_statistics, get_risk_failures
    cost = [b for b in config.bet_modes if b.get_name() == mode][0].get_cost()
    path = os.path.join(LIB, "publish_files", f"lookUpTable_{mode}_0.csv")
    with contextlib.redirect_stdout(_io.StringIO()), contextlib.redirect_stderr(_io.StringIO()):
        dist, pays, wrange, lo, hi = verify_lookup_format(path)
        stats = get_lut_statistics(mode, dist, cost, pays, wrange, lo, hi, len(pays))
    return get_risk_failures(stats), stats


def weigh_mode_safely(config, mode):
    """Gentlest tail factor whose LUT passes every risk check (the last step if none does)."""
    for f in TAIL_STEPS:
        rtp, report = weigh_mode(config, mode, tail_factor=f)
        failures, stats = risk_failures(config, mode)
        if not failures:
            break
    return rtp, report, f, failures, stats


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    config = GameConfig()
    OptimizationSetup(config)
    modes = sys.argv[1].split(",") if len(sys.argv) > 1 else [b.get_name() for b in config.bet_modes]
    for mode in modes:
        rtp, report, f, failures, stats = weigh_mode_safely(config, mode)
        print(f"{mode:15s} tail factor {f}  risk failures {sorted(failures) or 'none'}  sd {stats.std:.1f}")
        print(f"{mode:15s} RTP {rtp:.6%}")
        for c, n, prob, mean, theta in report:
            print(f"    {c:9s} books {n:6d}  prob {prob:.3e}  mean {mean:10.3f}x  theta {theta:+.4f}")
