"""Rule tests for Infernal Kingdom. Run from the math-sdk clone:

    env/bin/python games/infernal_kingdom/tests/test_rules.py [ROUNDS]

Plain asserts, no test framework needed. Each check plays natural rounds (no criteria
forcing) and inspects the book events produced.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

import natural  # noqa: E402
from game_config import GameConfig, SEALS, SOULS  # noqa: E402
from gamestate import GameState  # noqa: E402
from src.config.distributions import Distribution  # noqa: E402
from src.wins.win_manager import WinManager  # noqa: E402

TRANSIENT = {"WB", "GB", "SP", "DO"}


def make_state(mode, wincap=None):
    config = GameConfig()
    if wincap is not None:
        config.wincap = wincap
    bm = [b for b in config.bet_modes if b.get_name() == mode][0]
    cond = {"reel_weights": {config.basegame_type: {"BR0": 1}, config.freegame_type: {"FR0": 1}},
            "force_wincap": False}
    if bm.get_buybonus():
        tier = [d for d in bm.get_distributions() if d.get_criteria() != "wincap"][0]._conditions
        cond.update(scatter_triggers=tier["scatter_triggers"], bonus_tier=tier["bonus_tier"], force_freegame=True)
    else:
        cond.update(natural=True, force_freegame=False)
    if not any(d.get_criteria() == "natural" for d in bm.get_distributions()):
        bm._distributions = list(bm._distributions) + [Distribution(criteria="natural", quota=1, conditions=cond)]
    gs = GameState(config)
    gs.skip_attribution = True
    gs.betmode = mode
    gs.criteria = "natural"
    gs.win_manager = WinManager(config.basegame_type, config.freegame_type, config.wincap)
    # Guard: an evaluation must never see a transient special symbol.
    original = gs.evaluate_ways

    def guarded():
        for reel in gs.board:
            for s in reel:
                assert s.name not in TRANSIENT, f"unresolved {s.name} at evaluation"
        return original()

    gs.evaluate_ways = guarded
    return gs, config


def play(gs, sim):
    gs.library, gs._library_lines, gs._payout_ints = {}, [], []
    gs.run_spin(sim)
    return gs.book.to_json()


def check_round(book, gs, config):
    events = book["events"]
    # Payout equals the cap-limited attribution sum and never exceeds the cap.
    assert book["payoutMultiplier"] <= round(config.wincap * 100)
    assert book["payoutMultiplier"] % 10 == 0, "Stake requires payouts in 0.1x steps"
    assert abs(sum(gs.attrib.values()) - gs.final_win) < 0.02
    assert abs(gs.win_manager.basegame_wins + gs.win_manager.freegame_wins - gs.final_win) < 0.02
    # Nothing pays after the cap is reached.
    capped = False
    for e in events:
        if e["type"] == "wincap":
            capped = True
        elif capped and e["type"] in ("winInfo", "instantWin") and e.get("totalWin", e.get("amount", 0)) > 0:
            raise AssertionError("payout after wincap")
    # Per spin: each seal lights once, each pattern resolves once, at most one takeover.
    lit, patterns, takeovers, apocalypses = set(), set(), 0, 0
    for e in events:
        t = e["type"]
        if t == "sealReset":
            lit = set(e["lit"])
            patterns = set()
        elif t == "reveal":
            takeovers = 0
        elif t == "sealLit":
            assert e["seal"] not in lit, "seal lit twice"
            lit.add(e["seal"])
            if e["seal"] == "dominion":
                assert len(lit) - 1 >= config.dominion_after
        elif t == "sealPattern":
            assert e["pattern"] not in patterns, "pattern resolved twice in one spin"
            patterns.add(e["pattern"])
            if e["pattern"] == "infernal_dominion":
                assert len(lit) == len(SEALS)
        elif t == "infernalTakeover":
            takeovers += 1
            assert takeovers == 1, "two takeovers in one spin"
        elif t == "soulCollected":
            assert len(set(e["collected"])) == len(e["collected"]) <= len(SOULS)
            assert 0 <= e["shards"] < config.shards_per_soul
        elif t == "soulApocalypse":
            apocalypses += 1
            assert sorted(e["souls"]) == sorted(SOULS)
    assert apocalypses <= 1, "Soul Apocalypse twice in one round"
    assert gs.stats["max_cascade"] < config.max_cascades, "cascade safety stop reached"
    if gs.tier:
        assert gs.tot_fs <= gs.tier["spins"] + config.max_retriggers * gs.tier["retrigger"]
    for e in events:
        if "board" in e:
            assert len(e["board"]) == 6 and all(len(r) == 4 for r in e["board"])


def test_determinism():
    gs, _ = make_state("base")
    a = [json.dumps(play(gs, i)) for i in range(50)]
    b = [json.dumps(play(gs, i)) for i in range(50)]
    assert a == b, "same seed gave different books"


def test_rules(rounds):
    for mode in ["base", "base_soul", "hellfire", "covenant_blood", "covenant_soul", "abyssal",
                 "furnace_blood", "furnace_soul"]:
        gs, config = make_state(mode)
        n = rounds if mode.startswith("base") else max(rounds // 10, 200)
        for i in range(n):
            check_round(play(gs, i), gs, config)
        print(f"  rules ok: {mode} ({n} rounds)")


def test_cap():
    """With an artificially low cap every rule above must still hold and payouts stop at the cap."""
    gs, config = make_state("furnace_blood", wincap=300.0)
    hits = 0
    for i in range(400):
        book = play(gs, i)
        check_round(book, gs, config)
        assert book["payoutMultiplier"] <= 30000
        hits += book["payoutMultiplier"] == 30000
    assert hits > 0, "cap test never reached the cap"
    GameConfig().wincap = 66666.0
    print(f"  cap ok: {hits}/400 bonus rounds stopped exactly at a 300x test cap")


if __name__ == "__main__":
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    test_determinism()
    print("  determinism ok")
    test_cap()
    test_rules(rounds)
    print("ALL TESTS PASSED")
