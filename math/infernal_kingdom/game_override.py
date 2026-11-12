"""Infernal Kingdom per-round state, criteria checks and RTP-attribution output."""

import json
import os

from game_executables import GameExecutables

STAT_KEYS = ["wild_bombs", "golden_bombs", "splits", "overlords", "takeovers", "seals_lit", "patterns",
             "max_cascade", "shard_awards", "seven_souls", "apocalypse", "wincap", "retriggers"]


class GameStateOverride(GameExecutables):
    """Override or extend universal state.py functions."""

    def reset_book(self):
        super().reset_book()
        # Modes without a pact (Hellfire, Abyssal buys) never play a pact bonus in a kept
        # book: a cascade into a higher tier is rejected by check_repeat. "blood" only keeps
        # such rejected attempts well-defined.
        self.pact = self.config.mode_pact.get(getattr(self, "betmode", "base")) or "blood"
        self.bonus_tier = None
        self.tier = None
        self.retriggers = 0
        self.seals_lit = []
        self.patterns_done = set()
        self.seals_persist = False
        self.pending_seals = 0
        self.takeover_done = False
        self.dominion_mult = 1
        self.descent_mult = 1
        self.descent_active = False
        self.eval_index = 0
        self.cascade_count = 0
        self.souls_active = False
        self.soul_rate = 0.0
        self.souls = []
        self.shards = 0
        self.soul_queue = []
        self.milestones = set()
        self.soul_wild_active = False
        self.soul_mult_active = False
        self.apocalypse_pending = False
        self.apocalypse_done = False
        self.apocalypse_phase = False
        self.attrib = {}
        self.group_counter = 0
        self.stats = {k: 0 for k in STAT_KEYS}

    def assign_special_sym_function(self):
        pass

    def draw_board(self, emit_event: bool = True, trigger_symbol: str = "scatter") -> None:
        """Analysis-only 'natural' criteria: plain reel stops, no forcing and no redraws."""
        if self.get_current_distribution_conditions().get("natural"):
            self.create_board_reelstrips()
        else:
            super().draw_board(emit_event, trigger_symbol)

    def check_repeat(self) -> None:
        """Reject a simulation that does not satisfy its distribution criteria."""
        if self.repeat is False:
            conditions = self.get_current_distribution_conditions()
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True
            if conditions["force_freegame"] and not self.triggered_freegame:
                self.repeat = True
            required = conditions.get("bonus_tier")
            if required is not None and self.bonus_tier != required:
                self.repeat = True
            if conditions.get("require_win") and self.win_manager.running_bet_win == 0:
                self.repeat = True
        self.repeat_count += 1
        self.check_current_repeat_count()

    # ------------------------------------------------------------ attribution

    def imprint_wins(self) -> None:
        super().imprint_wins()
        if getattr(self, "skip_attribution", False):
            return
        if getattr(self, "_attr_file", None) is None or self._attr_mode != self.betmode:
            folder = os.path.join(self.config.library_path, "attribution")
            os.makedirs(folder, exist_ok=True)
            self._attr_mode = self.betmode
            self._attr_file = open(os.path.join(folder, f"{self.betmode}_{os.getpid()}.jsonl"), "a", encoding="utf-8")
        line = {"id": self.book_id, "criteria": self.criteria, "payout": self.final_win,
                "bonus": self.bonus_tier, "attrib": self.attrib, "stats": self.stats,
                "souls": len(self.souls)}
        self._attr_file.write(json.dumps(line) + "\n")
        self._attr_file.flush()
