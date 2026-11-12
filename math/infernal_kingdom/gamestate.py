"""Infernal Kingdom - simulation of one paid round (base spin plus any bonus it triggers)."""

import random

from game_override import GameStateOverride
from game_config import SOULS
from game_events import bargain_event, enter_bonus_event, fs_trigger_event, update_fs_event
from src.events.events import set_win_event, set_total_event, freespin_end_event


class GameState(GameStateOverride):
    """Core function handling simulation results."""

    def run_spin(self, sim, simulation_seed=None):
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.play_spin()
            set_win_event(self)
            set_total_event(self)
            self.win_manager.update_gametype_wins(self.gametype)

            scatters = self.count_scatters()
            if scatters >= self.config.retrigger_scatters and not self.wincap_triggered:
                conditions = self.get_current_distribution_conditions()
                if conditions["force_freegame"] or conditions.get("natural"):
                    self.bonus_tier = self.tier_for_scatters(scatters)
                    self.record({"bonus": self.bonus_tier})
                    self.run_freespin()
                else:
                    self.repeat = True  # a no-bonus criteria drew a bonus board: redraw

            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    def run_freespin(self):
        self.tier = self.config.bonus_tiers[self.bonus_tier]
        self.reset_fs_spin()
        self.tot_fs = self.tier["spins"]
        self.descent_active = self.tier["descent"]
        self.souls_active = True
        rate = self.tier["soul_rate"]
        if self.tier["pact"]:
            rate *= self.config.pacts[self.pact]["soul_rate_factor"]
            self.seals_persist = self.config.pacts[self.pact]["seals_persist"]
        self.soul_rate = rate
        self.souls = random.sample(SOULS, self.tier["start_souls"]) if self.tier["start_souls"] else []

        fs_trigger_event(self, retrigger=False)
        if self.tier["pact"]:
            bargain_event(self)
        enter_bonus_event(self)

        while self.fs < self.tot_fs and not self.wincap_triggered:
            self.fs += 1
            update_fs_event(self)
            self.win_manager.reset_spin_win()
            self.play_spin()
            if (not self.wincap_triggered and self.retriggers < self.config.max_retriggers
                    and self.count_scatters() >= self.config.retrigger_scatters):
                self.retriggers += 1
                self.stats["retriggers"] += 1
                self.tot_fs += self.tier["retrigger"]
                fs_trigger_event(self, retrigger=True)
            set_win_event(self)
            set_total_event(self)
            self.win_manager.update_gametype_wins(self.gametype)

        freespin_end_event(self)
