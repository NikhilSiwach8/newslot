"""Infernal Kingdom - symbols, the 4,096-ways evaluator and board helpers."""

import random

from src.calculations.symbol import Symbol, SymbolStorage
from src.calculations.statistics import get_random_outcome
from src.executables.executables import Executables
from game_config import REGULAR, PREMIUMS, LOWS


class IKSymbol(Symbol):
    """SDK symbol plus the per-cell state this game tracks."""

    __slots__ = ("soul", "src", "double", "shield", "lock", "group")

    def __init__(self, defn):
        super().__init__(defn)
        self.soul = None  # Seven Souls orb carried by a regular symbol (bonus only)
        self.src = "strip"  # where a wild (or transformed symbol) came from, for RTP attribution
        self.double = False  # Split Symbol result: counts as two symbols for ways
        self.shield = 0  # removals this symbol survives (Infernal Shield / Soul Pact)
        self.lock = 0  # Time Lock: survives the next removal step
        self.group = 0  # wilds sharing a group (one bomb, takeover...) share one multiplier


class IKSymbolStorage(SymbolStorage):
    def create_symbol(self, name):
        try:
            return IKSymbol(self.symbol_defs[name])
        except KeyError:
            raise ValueError(f"Symbol '{name}' is not registered")


def is_wild(sym) -> bool:
    return sym.name in ("W", "HS")


def is_regular(sym) -> bool:
    return sym.name in REGULAR


def sym_json(sym) -> dict:
    """Client representation of one cell."""
    out = {"name": sym.name}
    if is_wild(sym) and sym.multiplier and sym.multiplier > 1:
        out["multiplier"] = int(sym.multiplier)
        out["group"] = int(sym.group)
    if sym.soul:
        out["soul"] = sym.soul
    if sym.double:
        out["double"] = True
    return out


# Attribution priority: the first matching source names the feature a win is credited to.
WILD_SRC_PRIORITY = ["apocalypse", "takeover", "gbomb", "bomb", "overlord", "seal_reel", "seal", "soulwild", "hellstar"]
SRC_TO_FEATURE = {
    "apocalypse": "apocalypse",
    "takeover": "takeover",
    "gbomb": "golden_bomb",
    "bomb": "wild_bomb",
    "overlord": "overlord",
    "seal": "seals",
    "seal_reel": "seals",
    "soulwild": "souls",
    "hellstar": "hellstar",
}


class GameCalculations(Executables):
    """Board-level calculations."""

    def create_symbol_map(self) -> None:
        names = {k[1] for k in self.config.paytable}
        for syms in self.config.special_symbols.values():
            names.update(syms)
        self.symbol_storage = IKSymbolStorage(self.config, sorted(names))

    # ------------------------------------------------------------ randomness
    def wild_table_name(self) -> str:
        if self.gametype == self.config.basegame_type:
            return "base"
        tier = self.config.bonus_tiers[self.bonus_tier]
        name = tier["wild"] or self.config.pacts[self.pact]["wild"]
        return name + "_plus" if self.soul_mult_active else name

    def draw_wild_mult(self) -> int:
        return int(get_random_outcome(self.config.wild_tables[self.wild_table_name()]))

    def create_symbol(self, name: str):
        """Every symbol drawn from a strip goes through here: wilds get their multiplier."""
        sym = self.symbol_storage.create_symbol(name)
        if name == "W":
            sym.multiplier = self.draw_wild_mult()
            sym.shield = self.wild_shield_default()
            sym.group = self.new_group()
        elif name == "HS":
            sym.group = self.new_group()
            key = "base" if self.gametype == self.config.basegame_type else "bonus"
            sym.multiplier = int(get_random_outcome(self.config.hellstar_tables[key]))
            sym.src = "hellstar"
            sym.shield = self.config.hellstar_persist
        return sym

    def wild_shield_default(self) -> int:
        """Soul Pact: every Infernal Wild survives its first winning cascade."""
        if self.gametype == self.config.freegame_type and self.pact and self.config.bonus_tiers[self.bonus_tier]["pact"]:
            return 1 if self.config.pacts[self.pact]["wild_persist"] else 0
        return 0

    def new_group(self) -> int:
        self.group_counter = getattr(self, "group_counter", 0) + 1
        return self.group_counter

    def make_wild(self, src: str, mult: int = None, group: int = None):
        sym = self.symbol_storage.create_symbol("W")
        sym.multiplier = self.draw_wild_mult() if mult is None else int(mult)
        sym.group = self.new_group() if group is None else group
        sym.src = src
        # Soul Pact persistence applies to single wilds, never to whole-reel or area wilds.
        sym.shield = self.wild_shield_default() if src in ("strip", "seal", "soulwild") else 0
        return sym

    def make_regular(self, name: str, src: str = "strip", soul=None):
        sym = self.symbol_storage.create_symbol(name)
        sym.src = src
        sym.soul = soul
        return sym

    # ------------------------------------------------------------ geometry
    def cells(self):
        return [(r, row) for r in range(self.config.num_reels) for row in range(self.config.num_rows[r])]

    def positions_where(self, pred, reels=None):
        reels = range(self.config.num_reels) if reels is None else reels
        return [(r, row) for r in reels for row in range(self.config.num_rows[r]) if pred(self.board[r][row])]

    def board_json(self):
        return [[sym_json(s) for s in reel] for reel in self.board]

    def global_mult(self) -> int:
        return int(self.dominion_mult * self.descent_mult)

    # ------------------------------------------------------------ ways
    def evaluate_ways(self) -> dict:
        """4,096-ways evaluation, left to right from reel 1.

        Per reel, a symbol's count is its matching cells (a Split result counts 2) plus every
        wild on that reel; ways is the product of the counts over consecutive reels. A win
        needs 3+ reels and at least one real symbol (wild-only ways do not pay).
        Win multiplier: the multipliers (x2 and above) of the wilds in the win are added
        together, each multiplier group counted once (all wilds made by one bomb, takeover,
        overlord or apocalypse share a group). Then the global multiplier (Infernal
        Dominion x Abyssal Descent) applies.
        """
        gm = self.global_mult()
        wins = []
        total = 0.0
        for sym in REGULAR:
            ways, kind, positions, has_real, groups = 1, 0, [], False, {}
            for r in range(self.config.num_reels):
                count = 0
                reel_pos = []
                for row, s in enumerate(self.board[r]):
                    if s.name == sym:
                        count += 2 if s.double else 1
                        has_real = True
                        reel_pos.append((r, row))
                    elif s.name in ("W", "HS"):
                        count += 1
                        reel_pos.append((r, row))
                        if (s.multiplier or 1) > 1:
                            groups[s.group] = max(groups.get(s.group, 0), s.multiplier)
                if count == 0:
                    break
                kind += 1
                ways *= count
                positions += reel_pos
            if kind < 3 or not has_real or (kind, sym) not in self.config.paytable:
                continue
            wild_mult = sum(groups.values()) if groups else 1
            base = round(self.config.paytable[(kind, sym)] * ways, 2)
            win = round(base * wild_mult * gm, 2)
            wins.append({
                "symbol": sym, "kind": kind, "ways": ways, "win": win, "positions": positions,
                "meta": {"wildMult": wild_mult, "globalMult": gm, "winWithoutMult": base},
                "feature": self.classify_win(positions),
            })
            total += win
        return {"totalWin": round(total, 2), "wins": wins}

    def classify_win(self, positions) -> str:
        """Feature credited with a ways win (see WILD_SRC_PRIORITY)."""
        if self.apocalypse_phase:
            return "apocalypse"
        srcs = set()
        flags = set()
        for r, row in positions:
            s = self.board[r][row]
            if s.name in ("W", "HS"):
                srcs.add(s.src)
            elif s.src == "seal":
                flags.add("seal")
            elif s.double:
                flags.add("split")
        for src in WILD_SRC_PRIORITY:
            if src in srcs:
                return SRC_TO_FEATURE[src]
        if "seal" in flags or self.dominion_mult > 1:
            return "seals"
        if "split" in flags:
            return "split"
        if self.descent_mult > 1:
            return "descent"
        return "regular" if self.eval_index == 0 else "cascade"

    # ------------------------------------------------------------ misc
    def most_common_regular(self, pool):
        counts = {}
        for reel in self.board:
            for s in reel:
                if s.name in pool:
                    counts[s.name] = counts.get(s.name, 0) + 1
        if not counts:
            return None
        order = {n: i for i, n in enumerate(REGULAR)}  # ties go to the higher-paying symbol
        return sorted(counts.items(), key=lambda kv: (-kv[1], order[kv[0]]))[0][0]

    def pick(self, items, k):
        items = list(items)
        return sorted(random.sample(items, min(k, len(items))))


__all__ = ["GameCalculations", "IKSymbol", "is_wild", "is_regular", "sym_json", "PREMIUMS", "LOWS"]
