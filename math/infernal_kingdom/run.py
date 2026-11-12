"""Generate books, lookup tables and configs for Infernal Kingdom.

Usage (from the math-sdk clone, after scripts/setup-math.sh):

    make run GAME=infernal_kingdom

Then build the reports:

    env/bin/python games/infernal_kingdom/tools/report.py
"""

import os
import shutil

from gamestate import GameState
from game_config import GameConfig
from game_optimization import OptimizationSetup
from optimization_program.run_script import OptimizationExecution
from utils.game_analytics.run_analysis import create_stat_sheet
from utils.rgs_verification import execute_all_tests
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs

if __name__ == "__main__":

    num_threads = 4
    rust_threads = 4
    batching_size = 25000
    compression = True
    profiling = False

    sims = int(float(os.environ.get("IK_SIMS", "1e5")))
    num_sim_args = {name: sims for name in
                    ["base", "base_soul", "hellfire", "covenant_blood", "covenant_soul",
                     "abyssal", "furnace_blood", "furnace_soul"]}
    only = os.environ.get("IK_MODES")
    if only:
        num_sim_args = {k: v for k, v in num_sim_args.items() if k in only.split(",")}

    run_conditions = {
        "run_sims": os.environ.get("IK_SKIP_SIMS") != "1",
        "run_optimization": True,
        "run_analysis": True,
        "run_format_checks": True,
    }
    target_modes = list(num_sim_args.keys())

    config = GameConfig()
    gamestate = GameState(config)
    if run_conditions["run_optimization"] or run_conditions["run_analysis"]:
        optimization_setup_class = OptimizationSetup(config)

    if run_conditions["run_sims"]:
        attribution = os.path.join(config.library_path, "attribution")
        for mode in target_modes:  # attribution sidecar files are appended to: clear this run's modes
            for f in os.listdir(attribution) if os.path.isdir(attribution) else []:
                if f.startswith(mode + "_") and f[len(mode) + 1:].split(".")[0].isdigit():
                    os.remove(os.path.join(attribution, f))
        create_books(gamestate, config, num_sim_args, batching_size, num_threads, compression, profiling)

    generate_configs(gamestate)

    if run_conditions["run_optimization"]:
        OptimizationExecution().run_all_modes(config, target_modes, rust_threads)
        generate_configs(gamestate)

    if run_conditions["run_analysis"]:
        custom_keys = [{"bonus": b} for b in ["hellfire", "covenant", "abyssal", "furnace"]]
        create_stat_sheet(gamestate, custom_keys=custom_keys)

    if run_conditions["run_format_checks"]:
        execute_all_tests(config)
