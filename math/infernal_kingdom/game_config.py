"""INFERNAL KINGDOM - game configuration.

6x4 board, 4,096 ways, cascading wins. Every payout and cap is a multiple of the base
(1x) bet. Every numeric value here is a starting design value chosen for this game (no
external reference math was supplied); they are tuned by simulation and the optimizer.
See docs/MATH_DESIGN.md for the reasoning behind each block.
"""

import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode

PREMIUMS = ["H1", "H2", "H3", "H4", "H5"]
LOWS = ["L1", "L2", "L3", "L4", "L5"]
REGULAR = PREMIUMS + LOWS

# Nine Hell Seals, laid out row by row on the 3x3 seal board.
SEALS = ["wrath", "greed", "envy", "pride", "lust", "sloth", "gluttony", "despair", "dominion"]
SEAL_LINES = {
    "horizontal": [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
    "vertical": [[0, 3, 6], [1, 4, 7], [2, 5, 8]],
    "diagonal": [[0, 4, 8], [2, 4, 6]],
}
# Pattern effects in their fixed resolution order (each at most once per spin).
PATTERN_ORDER = ["hellfire", "soul_harvest", "cataclysm", "infernal_dominion"]
PATTERN_FOR_LINE = {"horizontal": "hellfire", "vertical": "soul_harvest", "diagonal": "cataclysm"}

SOULS = ["wrath", "greed", "envy", "pride", "lust", "sloth", "gluttony"]

BONUSES = ["hellfire", "covenant", "abyssal", "furnace"]


class GameConfig(Config):
    """Singleton Infernal Kingdom configuration."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "infernal_kingdom"
        self.provider_number = 0
        self.working_name = "Infernal Kingdom"
        self.win_type = "ways"
        self.rtp = 0.9600  # configurable target; every bet mode uses it
        self.wincap = 66666.0  # hard cap for the whole paid round, base game + bonus
        self.construct_paths()

        # ------------------------------------------------------------- board
        self.num_reels = 6
        self.num_rows = [4] * self.num_reels
        self.include_padding = False
        self.max_cascades = 60  # safety stop per evaluation sequence; never reached in testing

        # ---------------------------------------------------------- paytable
        # Pay per way for 3, 4, 5, 6 of a kind.
        pays = {
            "H1": (0.50, 1.00, 2.50, 5.00),  # Demon King
            "H2": (0.40, 0.80, 2.00, 4.00),  # Infernal Dragon
            "H3": (0.30, 0.60, 1.50, 3.00),  # Cursed Crown
            "H4": (0.25, 0.50, 1.20, 2.50),  # Blood Chalice
            "H5": (0.20, 0.40, 1.00, 2.00),  # Soul Ring
            "L1": (0.10, 0.20, 0.50, 1.00),  # A
            "L2": (0.10, 0.20, 0.40, 0.80),  # K
            "L3": (0.05, 0.10, 0.30, 0.60),  # Q
            "L4": (0.05, 0.10, 0.25, 0.50),  # J
            "L5": (0.05, 0.10, 0.20, 0.40),  # 10
        }
        self.paytable = {}
        for sym, values in pays.items():
            for kind, value in zip((3, 4, 5, 6), values):
                self.paytable[(kind, sym)] = value

        # W Infernal Wild, HS Hellstar (sticky multiplier wild), S Hell Gate scatter,
        # WB Wild Bomb, GB Golden Wild Bomb, SP Split Symbol, DO Demon Overlord.
        # WB/GB/SP/DO resolve the moment they land and never take part in an evaluation.
        self.special_symbols = {
            "wild": ["W", "HS"],
            "scatter": ["S"],
            "bomb": ["WB", "GB"],
            "split": ["SP"],
            "overlord": ["DO"],
        }

        # ---------------------------------------------------- special landing
        # Chance that a newly landed regular symbol is replaced by a special, per cell.
        # Applied to the initial board and every refill. Reels are 0-based.
        self.special_reels = {
            "WB": [1, 2, 3, 4],
            "GB": [1, 2, 3, 4],
            "SP": [0, 1, 2, 3, 4, 5],
            "HS": [1, 2, 3, 4, 5],
            "DO": [1, 2, 3, 4],
        }
        self.special_rates = {
            "base": {"WB": 0.0003, "GB": 0.00002, "SP": 0.0040, "HS": 0.0004, "DO": 0.00005},
            "bonus": {"WB": 0.0012, "GB": 0.0002, "SP": 0.0050, "HS": 0.0010, "DO": 0.0002},
        }
        # Split Symbol becomes one regular symbol that counts as two (drawn from this table).
        self.split_table = {"H1": 2, "H2": 3, "H3": 4, "H4": 5, "H5": 6, "L1": 6, "L2": 6, "L3": 6, "L4": 6, "L5": 6}

        # ---------------------------------------------------- wild multipliers
        # Multiplier tables (value: weight). "base" tables apply in the base game; bonus
        # tables are chosen per bonus and pact below. A wild on a reel counts as its
        # multiplier for that reel's way count, so multipliers on different reels multiply.
        self.wild_tables = {
            "base": {1: 1},
            "hellfire": {1: 60, 2: 25, 3: 10, 5: 4, 10: 1},
            "hellfire_plus": {2: 50, 3: 30, 5: 14, 10: 5, 25: 1},
            "blood": {1: 50, 2: 25, 3: 12, 5: 8, 10: 4, 25: 1},
            "blood_plus": {2: 40, 3: 28, 5: 18, 10: 10, 25: 3, 50: 1},
            "soul": {1: 60, 2: 28, 3: 10, 5: 2},
            "soul_plus": {2: 55, 3: 30, 5: 12, 10: 3},
            "abyssal": {1: 80, 2: 17, 3: 3},
            "abyssal_plus": {1: 55, 2: 33, 3: 10, 5: 2},
        }
        self.hellstar_tables = {"base": {2: 3, 3: 1}, "bonus": {3: 4, 5: 3, 10: 1}}
        self.golden_bomb_min_mult = {"base": 1, "bonus": 2}  # Golden Wild Bomb multiplier floor

        # ---------------------------------------------------- Nine Hell Seals
        self.seal_weights = {s: 10 for s in SEALS}
        self.seal_weights["dominion"] = 4  # the Demon King's seal is the rarest
        self.seals_per_win = 1  # seals lit by each qualifying winning cascade
        # A winning cascade qualifies from this winning evaluation of the spin onward.
        self.seal_first_qualifying_win = {"base": 2, "bonus": 1}
        self.dominion_after = 5  # Dominion can only light once this many other seals are lit
        self.seals_per_special = {"WB": 1, "GB": 2}  # extra activations when a bomb explodes
        self.wrath_wilds = {"base": {1: 3, 2: 1}, "blood": {2: 5, 3: 3, 4: 1}}
        self.lust_base_mult = 2
        self.envy_targets = {"H5": 4, "H4": 3, "H3": 2, "H2": 1}
        self.harvest_factor = {"seal": 0.5, "pattern": 1.0}  # x the 3-of-a-kind pay per symbol
        self.gluttony_types = 2  # number of low symbol types devoured
        self.despair_reels = {"seal": 2, "pattern": 3}
        self.dominion_mult = {"base": 2, "bonus": 3}  # Infernal Dominion global multiplier
        self.dominion_repeat_mult_step = 1  # Dominion seal after a takeover this spin: +1 global mult

        # ---------------------------------------------------- Infernal Takeover
        self.takeover_reels = 2
        self.takeover_chance = {"base": 0.0003, "hellfire": 0.008, "covenant": 0.010, "abyssal": 0.004, "furnace": 0.03}
        self.takeover_mult = {"base": {1: 1}, "bonus": {2: 2, 3: 1}, "blood": {3: 2, 5: 1}, "soul": {1: 2, 2: 1}}

        # ---------------------------------------------------- Seven Souls
        self.shards_per_soul = 3  # duplicate Souls become Soul Shards; this many shards award a missing Soul
        self.soul_wild_milestone = 3  # unlocks one extra Infernal Wild at the start of every later spin
        self.soul_mult_milestone = 5  # wild multipliers switch to the "_plus" table
        self.apocalypse_milestone = 7
        self.apocalypse = {
            "default": {"reels": 2, "mult": 5},
            "blood": {"reels": 3, "mult": 7},
            "soul": {"reels": 2, "mult": 5},
        }

        # ---------------------------------------------------- bonuses
        # Tier is set by the number of Hell Gate scatters on the board when the cascades end.
        self.bonus_tiers = {
            "hellfire": {"scatters": 3, "spins": 10, "retrigger": 5, "pact": False, "wild": "hellfire",
                         "seal_prelit": 1, "soul_rate": 0.012, "start_souls": 0, "descent": False},
            "covenant": {"scatters": 4, "spins": 12, "retrigger": 5, "pact": True, "wild": None,
                         "seal_prelit": 1, "soul_rate": 0.012, "start_souls": 0, "descent": False},
            "abyssal": {"scatters": 5, "spins": 10, "retrigger": 3, "pact": False, "wild": "abyssal",
                        "seal_prelit": 0, "soul_rate": 0.014, "start_souls": 0, "descent": True},
            "furnace": {"scatters": 6, "spins": 12, "retrigger": 5, "pact": True, "wild": None,
                        "seal_prelit": 2, "soul_rate": 0.016, "start_souls": 2, "descent": False},
        }
        self.max_retriggers = 3
        self.retrigger_scatters = 3
        self.descent_max_mult = 25  # Abyssal Descent multiplier ceiling
        self.descent_purge = ["L4", "L5"]  # removed from every Abyssal Descent reveal before evaluation
        self.pacts = {
            "blood": {"wild": "blood", "soul_rate_factor": 0.8, "seals_persist": False, "wild_persist": False},
            "soul": {"wild": "soul", "soul_rate_factor": 1.5, "seals_persist": True, "wild_persist": True},
        }

        self.freespin_triggers = {
            self.basegame_type: {3: 10, 4: 12, 5: 10, 6: 12},
            self.freegame_type: {3: 5, 4: 5, 5: 5, 6: 5},
        }
        self.anticipation_triggers = {self.basegame_type: 2, self.freegame_type: 2}

        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv", "WCAP": "WCAP.csv"}
        self.reels = {name: self.read_reels_csv(os.path.join(self.reels_path, f)) for name, f in reels.items()}

        self.build_bet_modes()

    # ------------------------------------------------------------------ modes
    def build_bet_modes(self):
        cap = self.wincap
        base_reels = {self.basegame_type: {"BR0": 1}, self.freegame_type: {"FR0": 1}}
        wcap_reels = {self.basegame_type: {"BR0": 1}, self.freegame_type: {"FR0": 1, "WCAP": 4}}
        tier_scatters = {name: {t["scatters"]: 1} for name, t in self.bonus_tiers.items()}

        def wincap_dist(tier):
            return Distribution(
                criteria="wincap", quota=0.001, win_criteria=cap,
                conditions={"reel_weights": wcap_reels, "scatter_triggers": tier_scatters[tier],
                            "bonus_tier": tier, "force_wincap": True, "force_freegame": True},
            )

        def tier_dist(tier, quota):
            return Distribution(
                criteria=tier, quota=quota,
                conditions={"reel_weights": base_reels, "scatter_triggers": tier_scatters[tier],
                            "bonus_tier": tier, "force_wincap": False, "force_freegame": True},
            )

        def plain(criteria, quota, win_criteria=None, require_win=False):
            return Distribution(
                criteria=criteria, quota=quota, win_criteria=win_criteria,
                conditions={"reel_weights": base_reels, "require_win": require_win,
                            "force_wincap": False, "force_freegame": False},
            )

        def base_mode(name, pact):
            return BetMode(
                name=name, cost=1.0, rtp=self.rtp, max_win=cap, auto_close_disabled=False,
                is_feature=True, is_buybonus=False,
                distributions=[
                    wincap_dist("furnace"),
                    tier_dist("furnace", 0.005), tier_dist("abyssal", 0.01),
                    tier_dist("covenant", 0.02), tier_dist("hellfire", 0.06),
                    plain("0", 0.40, win_criteria=0.0), plain("basegame", 0.50, require_win=True),
                ],
            )

        def buy_mode(name, tier, cost):
            return BetMode(
                name=name, cost=cost, rtp=self.rtp, max_win=cap, auto_close_disabled=False,
                is_feature=False, is_buybonus=True,
                distributions=[wincap_dist(tier), tier_dist(tier, 0.999)],
            )

        # The Demon's Bargain pact is chosen by the player BEFORE the bet and selects the
        # mode: Stake Engine rounds are fully decided when the bet is placed, so a choice
        # made mid-round could not change the outcome.
        self.mode_pact = {
            "base": "blood", "base_soul": "soul",
            "hellfire": None, "covenant_blood": "blood", "covenant_soul": "soul",
            "abyssal": None, "furnace_blood": "blood", "furnace_soul": "soul",
        }
        self.buy_costs = {"hellfire": 100.0, "covenant": 300.0, "abyssal": 350.0, "furnace": 600.0}
        self.bet_modes = [
            base_mode("base", "blood"),
            base_mode("base_soul", "soul"),
            buy_mode("hellfire", "hellfire", self.buy_costs["hellfire"]),
            buy_mode("covenant_blood", "covenant", self.buy_costs["covenant"]),
            buy_mode("covenant_soul", "covenant", self.buy_costs["covenant"]),
            buy_mode("abyssal", "abyssal", self.buy_costs["abyssal"]),
            buy_mode("furnace_blood", "furnace", self.buy_costs["furnace"]),
            buy_mode("furnace_soul", "furnace", self.buy_costs["furnace"]),
        ]
