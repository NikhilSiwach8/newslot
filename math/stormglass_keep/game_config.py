"""Stormglass Keep - game configuration.

7x7 cluster-pays tumbling game with charged cells, a beam meter and three bonus tiers.
All payouts and max wins are expressed in multiples of the base (1x) bet.
"""

import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


class GameConfig(Config):
    """Singleton Stormglass Keep configuration."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "stormglass_keep"
        self.provider_number = 0
        self.working_name = "Stormglass Keep"
        self.wincap = 10000.0
        self.win_type = "cluster"
        self.rtp = 0.9630
        self.construct_paths()

        # Board
        self.num_reels = 7
        self.num_rows = [7] * self.num_reels
        self.include_padding = True

        # Paytable: cluster-size bands -> payout
        t1, t2, t3, t4 = (5, 5), (6, 8), (9, 12), (13, 49)
        pays = {
            "H1": (8.0, 20.0, 40.0, 100.0),  # keeper's key
            "H2": (3.2, 8.0, 16.0, 64.0),  # anchor
            "H3": (2.0, 5.0, 11.0, 48.0),  # bell
            "H4": (1.6, 4.0, 9.6, 32.0),  # compass
            "L1": (1.0, 2.4, 6.4, 16.0),
            "L2": (0.6, 1.9, 5.6, 13.0),
            "L3": (0.5, 1.6, 4.8, 10.0),
            "L4": (0.3, 1.3, 4.0, 8.0),
            "L5": (0.2, 0.8, 2.4, 6.4),
        }
        pay_group = {}
        for sym, values in pays.items():
            for band, value in zip((t1, t2, t3, t4), values):
                pay_group[(band, sym)] = value
        self.paytable = self.convert_range_table(pay_group)

        self.special_symbols = {"wild": ["W"], "scatter": ["S"]}

        # --- Charged cells -------------------------------------------------
        # Grid values: 0 = uncharged, 1 = charged (no multiplier yet), 2+ = multiplier.
        # Each further win on a cell doubles it up to the cap.
        self.maximum_board_mult = 128
        self.beam_spin_precharged_cells = 6
        self.beam_spin_precharge_value = 4

        # --- Beam meter ----------------------------------------------------
        # The meter counts consecutive winning tumbles in one spin. A stage fires the
        # first time the meter is at or above its threshold after a win.
        self.beam_thresholds = {1: 4, 2: 6, 3: 8}
        self.beam_clear_symbols = ["L4", "L5"]  # stage 1 removes these
        self.beam_wild_counts = {3: 5, 4: 3, 5: 2}  # stage 2 adds this many wilds (value: weight)
        self.beam_start_by_mode = {"beam": 4}  # meter head start for base-game spins, by bet mode

        # --- Bonus tiers ---------------------------------------------------
        # Tier is decided by the number of scatters on the board when the tumbles end.
        self.bonus_tiers = {
            # In every bonus the beam meter starts each spin at 2, so the second win in a row fires stage one.
            "watch": {"scatters": 3, "spins": 10, "start_mult": 1, "max_mult": 128, "beam_start": 2},
            "eye": {"scatters": 4, "spins": 12, "start_mult": 2, "max_mult": 128, "beam_start": 2},
            "drowned": {"scatters": 5, "spins": 15, "start_mult": 4, "max_mult": 1024, "beam_start": 2},
        }
        self.retrigger_spins = 5
        self.max_retriggers = 1

        # Used by the SDK for trigger thresholds and anticipation; spin counts come from bonus_tiers.
        self.freespin_triggers = {
            self.basegame_type: {3: 10, 4: 12, 5: 15},
            self.freegame_type: {3: 5, 4: 5, 5: 5},
        }
        self.anticipation_triggers = {
            self.basegame_type: min(self.freespin_triggers[self.basegame_type].keys()) - 1,
            self.freegame_type: min(self.freespin_triggers[self.freegame_type].keys()) - 1,
        }

        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv", "WCAP": "WCAP.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))

        # Declared max win per mode. Beam Spin cannot trigger a bonus, so its cap is lower.
        mode_maxwins = {
            "base": 10000,
            "surge": 10000,
            "beam": 2500,
            "bonus": 10000,
            "super": 10000,
            "mystery": 10000,
        }

        base_reels = {self.basegame_type: {"BR0": 1}, self.freegame_type: {"FR0": 1}}
        wincap_reels = {self.basegame_type: {"BR0": 1}, self.freegame_type: {"FR0": 1, "WCAP": 5}}

        def wincap_dist(mode, scatter_triggers, tier=None):
            conditions = {
                "reel_weights": wincap_reels,
                "scatter_triggers": scatter_triggers,
                "force_wincap": True,
                "force_freegame": True,
            }
            if tier is not None:
                conditions["bonus_tier"] = tier
            return Distribution(
                criteria="wincap",
                quota=0.001,
                win_criteria=mode_maxwins[mode],
                conditions=conditions,
            )

        def tier_dist(tier, quota):
            return Distribution(
                criteria=tier,
                quota=quota,
                conditions={
                    "reel_weights": base_reels,
                    "scatter_triggers": {self.bonus_tiers[tier]["scatters"]: 1},
                    "bonus_tier": tier,
                    "force_wincap": False,
                    "force_freegame": True,
                },
            )

        def zero_dist(quota, reel_weights):
            return Distribution(
                criteria="0",
                quota=quota,
                win_criteria=0.0,
                conditions={"reel_weights": reel_weights, "force_wincap": False, "force_freegame": False},
            )

        def basegame_dist(quota, reel_weights):
            return Distribution(
                criteria="basegame",
                quota=quota,
                conditions={
                    "reel_weights": reel_weights,
                    "require_win": True,
                    "force_wincap": False,
                    "force_freegame": False,
                },
            )

        def natural_trigger_distributions(mode):
            """Base-style mode: every bonus tier can trigger from scatters."""
            return [
                wincap_dist(mode, {4: 1, 5: 2}),
                tier_dist("drowned", 0.01),
                tier_dist("eye", 0.03),
                tier_dist("watch", 0.08),
                zero_dist(0.38, base_reels),
                basegame_dist(0.5, base_reels),
            ]

        beam_reels = {self.basegame_type: {"FR0": 1}}
        beam_wincap_reels = {self.basegame_type: {"FR0": 1, "WCAP": 5}}

        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=mode_maxwins["base"],
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=natural_trigger_distributions("base"),
            ),
            # Surge Spin: same game as base, bonuses weighted to trigger far more often.
            BetMode(
                name="surge",
                cost=3.0,
                rtp=self.rtp,
                max_win=mode_maxwins["surge"],
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=natural_trigger_distributions("surge"),
            ),
            # Beam Spin: six cells pre-charged at x4, meter starts at stage one, no bonus trigger.
            BetMode(
                name="beam",
                cost=20.0,
                rtp=self.rtp,
                max_win=mode_maxwins["beam"],
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.001,
                        win_criteria=mode_maxwins["beam"],
                        conditions={
                            "reel_weights": beam_wincap_reels,
                            "force_wincap": True,
                            "force_freegame": False,
                        },
                    ),
                    zero_dist(0.2, beam_reels),
                    basegame_dist(0.8, beam_reels),
                ],
            ),
            # Keeper's Watch bonus buy.
            BetMode(
                name="bonus",
                cost=100.0,
                rtp=self.rtp,
                max_win=mode_maxwins["bonus"],
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[wincap_dist("bonus", {3: 1}, "watch"), tier_dist("watch", 1.0)],
            ),
            # Eye of the Storm super bonus buy.
            BetMode(
                name="super",
                cost=300.0,
                rtp=self.rtp,
                max_win=mode_maxwins["super"],
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[wincap_dist("super", {4: 1}, "eye"), tier_dist("eye", 1.0)],
            ),
            # Mystery Buy: 65% plain base spin, 25% Eye of the Storm, 10% The Drowned Light.
            # The split is enforced by the optimizer hit-rates in game_optimization.py.
            BetMode(
                name="mystery",
                cost=170.0,
                rtp=self.rtp,
                max_win=mode_maxwins["mystery"],
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    wincap_dist("mystery", {4: 1, 5: 2}),
                    tier_dist("drowned", 0.25),
                    tier_dist("eye", 0.35),
                    Distribution(
                        criteria="nobonus",
                        quota=0.4,
                        conditions={
                            "reel_weights": base_reels,
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
        ]
