"""Stormglass Keep grouped game actions: charged cells, beam meter, bonus tiers."""

import random

from game_calculations import GameCalculations
from game_events import (
    update_grid_mult_event,
    beam_meter_event,
    beam_clear_event,
    beam_wilds_event,
    beam_surge_event,
    enter_bonus_event,
)
from src.calculations.cluster import Cluster
from src.calculations.statistics import get_random_outcome
from src.events.events import update_freespin_event, fs_trigger_event


class GameExecutables(GameCalculations):
    """Game dependent grouped functions."""

    # ------------------------------------------------------------------ grid
    def reset_grid_mults(self, value: int = 0):
        """Set every cell to the same charge value."""
        self.position_multipliers = [
            [value for _ in range(self.config.num_rows[reel])] for reel in range(self.config.num_reels)
        ]

    def precharge_random_cells(self, count: int, value: int):
        """Beam Spin: charge a number of random cells before the first evaluation."""
        cells = [
            (reel, row) for reel in range(self.config.num_reels) for row in range(self.config.num_rows[reel])
        ]
        for reel, row in random.sample(cells, count):
            self.position_multipliers[reel][row] = value
        update_grid_mult_event(self)

    def update_grid_mults(self):
        """Charge every winning cell once per tumble: 0 -> 1 -> 2 -> 4 ... up to the cap."""
        winning_cells = set()
        for win in self.win_data["wins"]:
            for pos in win["positions"]:
                winning_cells.add((pos["reel"], pos["row"]))
        for reel, row in winning_cells:
            current = self.position_multipliers[reel][row]
            self.position_multipliers[reel][row] = min(max(current * 2, current + 1), self.max_board_mult)
        update_grid_mult_event(self)

    # ------------------------------------------------------------------ wins
    def get_clusters_update_wins(self):
        """Find clusters on the board and update the win manager."""
        clusters = Cluster.get_clusters(self.board, "wild")
        self.win_data = self.evaluate_clusters_with_grid(clusters)
        for win in self.win_data["wins"]:
            self.record({"kind": win["clusterSize"], "symbol": win["symbol"], "gametype": self.gametype})
        self.win_manager.update_spinwin(self.win_data["totalWin"])
        self.win_manager.tumble_win = self.win_data["totalWin"]

    def run_tumble_sequence(self, beam_start: int = 0):
        """Evaluate the current board, tumbling and firing the beam until no win remains."""
        self.beam_meter = beam_start
        self.beam_fired = set()
        self.get_clusters_update_wins()
        while self.win_data["totalWin"] > 0 and not self.wincap_triggered:
            self.emit_tumble_win_events()
            if self.wincap_triggered:
                break
            self.update_grid_mults()
            self.beam_meter += 1
            beam_meter_event(self)
            self.tumble_game_board()
            self.fire_beam()
            self.get_clusters_update_wins()
        self.set_end_tumble_event()
        self.win_manager.update_gametype_wins(self.gametype)

    # ------------------------------------------------------------------ beam
    def fire_beam(self):
        """Fire every beam stage whose threshold has been reached and not yet fired this spin."""
        for stage, threshold in self.config.beam_thresholds.items():
            if stage in self.beam_fired or self.beam_meter < threshold:
                continue
            self.beam_fired.add(stage)
            if stage == 1:
                self.beam_clear_lows()
            elif stage == 2:
                self.beam_add_wilds()
            elif stage == 3:
                self.beam_double_charges()

    def beam_clear_lows(self):
        """Stage 1: remove the lowest symbols without paying, then refill the board."""
        positions = []
        for reel, _ in enumerate(self.board):
            for row, sym in enumerate(self.board[reel]):
                if sym.name in self.config.beam_clear_symbols:
                    sym.explode = True
                    positions.append((reel, row))
        if positions:
            self.tumble_board()
        else:
            self.new_symbols_from_tumble = [[] for _ in range(self.config.num_reels)]
        beam_clear_event(self, positions)

    def beam_add_wilds(self):
        """Stage 2: turn random regular symbols into wilds."""
        candidates = [
            (reel, row)
            for reel, _ in enumerate(self.board)
            for row, sym in enumerate(self.board[reel])
            if not sym.check_attribute("wild", "scatter")
        ]
        count = min(get_random_outcome(self.config.beam_wild_counts), len(candidates))
        positions = sorted(random.sample(candidates, count))
        for reel, row in positions:
            self.board[reel][row] = self.create_symbol("W")
        self.get_special_symbols_on_board()
        beam_wilds_event(self, positions)

    def beam_double_charges(self):
        """Stage 3: every charged cell doubles."""
        for reel, _ in enumerate(self.position_multipliers):
            for row, current in enumerate(self.position_multipliers[reel]):
                if current >= 1:
                    self.position_multipliers[reel][row] = min(current * 2, self.max_board_mult)
        beam_surge_event(self)
        update_grid_mult_event(self)

    # ----------------------------------------------------------------- bonus
    def tier_for_scatters(self, scatter_count: int) -> str:
        """Bonus tier awarded for a number of scatters (5 or more is the top tier)."""
        best = None
        for name, tier in self.config.bonus_tiers.items():
            if scatter_count >= tier["scatters"] and (
                best is None or tier["scatters"] > self.config.bonus_tiers[best]["scatters"]
            ):
                best = name
        return best

    def run_freespin_from_base(self, scatter_key: str = "scatter") -> None:
        """Decide the bonus tier from the scatter count, then run the free spins."""
        scatter_count = self.count_special_symbols(scatter_key)
        self.bonus_tier = self.tier_for_scatters(scatter_count)
        self.record({"kind": scatter_count, "symbol": scatter_key, "gametype": self.gametype})
        self.record({"bonus": self.bonus_tier})
        self.tot_fs = self.config.bonus_tiers[self.bonus_tier]["spins"]
        fs_trigger_event(self, basegame_trigger=True, freegame_trigger=False)
        enter_bonus_event(self)
        self.run_freespin()

    def update_fs_retrigger_amt(self, scatter_key: str = "scatter") -> None:
        """Add the fixed retrigger award."""
        self.tot_fs += self.config.retrigger_spins
        self.retriggers += 1
        fs_trigger_event(self, freegame_trigger=True, basegame_trigger=False)

    def update_freespin(self) -> None:
        """Called before a new reveal during the free spins."""
        self.fs += 1
        update_freespin_event(self)
        self.win_manager.reset_spin_win()
        self.win_data = {}
