"""Stormglass Keep - simulation of a single betting round."""

from game_override import GameStateOverride
from game_events import update_grid_mult_event


class GameState(GameStateOverride):
    """Core function handling simulation results."""

    def run_spin(self, sim, simulation_seed=None):
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.draw_board()

            if self.betmode == "beam":
                self.precharge_random_cells(
                    self.config.beam_spin_precharged_cells, self.config.beam_spin_precharge_value
                )

            self.run_tumble_sequence(beam_start=self.config.beam_start_by_mode.get(self.betmode, 0))

            if self.check_fs_condition() and self.check_freespin_entry():
                self.run_freespin_from_base()

            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    def run_freespin(self):
        tier = self.config.bonus_tiers[self.bonus_tier]
        self.reset_fs_spin()
        # Base-game charges do not carry in; the tier sets the starting grid and cap,
        # and charges then persist for the whole bonus.
        self.max_board_mult = tier["max_mult"]
        self.reset_grid_mults(tier["start_mult"])
        update_grid_mult_event(self)

        while self.fs < self.tot_fs and not self.wincap_triggered:
            self.update_freespin()
            self.draw_board()
            self.run_tumble_sequence(beam_start=tier["beam_start"])

            if (
                not self.wincap_triggered
                and self.retriggers < self.config.max_retriggers
                and self.check_fs_condition()
            ):
                self.update_fs_retrigger_amt()

        self.end_freespin()
