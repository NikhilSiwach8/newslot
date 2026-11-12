"""Run a few rounds per bet mode in-process and print basic stats (no files written).

    cd math-sdk && env/bin/python games/infernal_kingdom/tools/smoke.py [rounds]
"""
import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from game_config import GameConfig
from gamestate import GameState

n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
modes = sys.argv[2].split(",") if len(sys.argv) > 2 else None
config = GameConfig()
gs = GameState(config)
gs.skip_attribution = True
for bm in config.bet_modes:
    if modes and bm.get_name() not in modes:
        continue
    gs.betmode = bm.get_name()
    from src.wins.win_manager import WinManager
    gs.win_manager = WinManager(config.basegame_type, config.freegame_type, bm.get_wincap())
    crits = [d.get_criteria() for d in bm.get_distributions()]
    t = time.time()
    tot, mx, nonzero = 0.0, 0.0, 0
    for i in range(n):
        gs.criteria = [c for c in crits if c != "wincap"][i % (len(crits) - 1)]
        gs.library, gs._library_lines, gs._payout_ints = {}, [], []
        gs.run_spin(i)
        tot += gs.final_win; mx = max(mx, gs.final_win); nonzero += gs.final_win > 0
        assert gs.final_win <= config.wincap
    print(f"{bm.get_name():15s} {n} rounds {time.time()-t:6.1f}s mean {tot/n:9.2f} max {mx:9.2f} nonzero {nonzero/n:.2f}")
