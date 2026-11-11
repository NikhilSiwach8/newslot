"""Stormglass Keep overrides of the universal SDK state functions."""

from game_executables import GameExecutables


class GameStateOverride(GameExecutables):
    """Override or extend universal state.py functions."""

    def reset_book(self):
        super().reset_book()
        self.tumble_win = 0
        self.bonus_tier = None
        self.retriggers = 0
        self.beam_meter = 0
        self.beam_fired = set()
        self.max_board_mult = self.config.maximum_board_mult
        # Charges never carry between rounds: the grid is cleared for every new book.
        self.reset_grid_mults()

    def assign_special_sym_function(self):
        pass

    def check_repeat(self) -> None:
        """Reject a simulation that does not satisfy its distribution criteria."""
        if self.repeat is False:
            conditions = self.get_current_distribution_conditions()
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True

            if conditions["force_freegame"] and not self.triggered_freegame:
                self.repeat = True

            required_tier = conditions.get("bonus_tier")
            if required_tier is not None and self.bonus_tier != required_tier:
                self.repeat = True

            if conditions.get("require_win") and self.win_manager.running_bet_win == 0:
                self.repeat = True

        self.repeat_count += 1
        self.check_current_repeat_count()
