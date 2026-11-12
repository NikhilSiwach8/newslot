"""Infernal Kingdom grouped game actions.

Order of play inside one spin (base game or one free spin):

  1. Board drawn from the reel strips; new cells may land as specials or carry Soul orbs.
  2. Landed specials resolve in fixed order: Split, Wild Bomb, Golden Wild Bomb, Demon Overlord.
  3. Bonus-only spin-start effects: Abyssal purge, then the 3-Soul extra wild.
  4. Random Infernal Takeover roll (at most one Takeover per spin, from any source).
  5. Seal activations earned by bombs are resolved.
  6. Cascade loop: evaluate ways -> pay -> remove winners -> refill -> resolve landed
     specials -> light seals (one per winning cascade plus bomb extras) -> each lit seal's
     power -> completed seal patterns (Hellfire, Soul Harvest, Cataclysm, Infernal
     Dominion; each at most once) -> evaluate again. Ends when an evaluation pays nothing.
  7. Bonus only: Soul Apocalypse, if seven Souls are held and it has not happened yet,
     followed by its own cascade loop.

Every payout goes through `pay()`, which never lets the round total pass the 66,666x cap
and stops all further payout-generating actions once the cap is reached.
"""

import random

from game_calculations import GameCalculations, is_wild, is_regular
from game_config import REGULAR, PREMIUMS, LOWS, SEALS, SEAL_LINES, PATTERN_ORDER, PATTERN_FOR_LINE, SOULS
from game_events import (
    reveal_event, special_event, win_info_event, tumble_win_event, tumble_event, seal_reset_event,
    seal_lit_event, seal_power_event, seal_pattern_event, instant_win_event, takeover_event,
    global_mult_event, soul_collected_event, soul_milestone_event, apocalypse_event, purge_event,
)
from src.calculations.statistics import get_random_outcome
from src.events.events import wincap_event

SPECIAL_ORDER = ["SP", "WB", "GB", "DO"]


class GameExecutables(GameCalculations):
    """Game-specific grouped functions."""

    # ================================================================ payouts
    def pay(self, amount: float, feature: str) -> float:
        """Add a payout, truncated so the round never exceeds the cap. Returns the amount paid."""
        if self.wincap_triggered:
            return 0.0
        headroom = round(self.config.wincap - self.win_manager.running_bet_win, 2)
        paid = round(min(round(amount, 2), max(headroom, 0.0)), 2)
        if paid > 0:
            self.win_manager.update_spinwin(paid)
            key = f"{self.section()}:{feature}"
            self.attrib[key] = round(self.attrib.get(key, 0.0) + paid, 2)
        if self.win_manager.running_bet_win >= self.config.wincap - 1e-9:
            self.wincap_triggered = True
            self.stats["wincap"] = 1
            self.wincap_pending = True  # event emitted after the win that reached the cap
        return paid

    def flush_wincap(self):
        if getattr(self, "wincap_pending", False):
            self.wincap_pending = False
            wincap_event(self)

    def section(self) -> str:
        return "base" if self.gametype == self.config.basegame_type else self.bonus_tier

    def pay_ways(self, win_data: dict) -> float:
        total = 0.0
        for w in win_data["wins"]:
            total += self.pay(w["win"], w["feature"])
        return round(total, 2)

    # ================================================================ landing
    def special_ctx(self):
        return "base" if self.gametype == self.config.basegame_type else "bonus"

    def special_rates(self):
        return self.config.special_rates["base" if self.gametype == self.config.basegame_type else "bonus"]

    def land(self, cells):
        """Newly landed regular cells may become specials, or (bonus) carry a Soul orb."""
        rates = self.special_rates()
        soul_rate = self.soul_rate if self.souls_active else 0.0
        for r, row in cells:
            sym = self.board[r][row]
            if not is_regular(sym):
                continue
            u = random.random()
            acc = 0.0
            replaced = False
            for name in ("WB", "GB", "SP", "HS", "DO"):
                if r not in self.config.special_reels[name]:
                    continue
                acc += rates[name]
                if u < acc:
                    self.board[r][row] = self.create_symbol(name)
                    replaced = True
                    break
            if not replaced and soul_rate and random.random() < soul_rate:
                sym.soul = random.choice(SOULS)

    def refill(self, removed, reason: str):
        """Remove cells, let survivors fall, draw new symbols from the strip above each reel."""
        removed = set(removed)
        for r, row in removed:
            self.release_soul(self.board[r][row])
        new_symbols = [[] for _ in range(self.config.num_reels)]
        new_cells = []
        for r in range(self.config.num_reels):
            keep = [s for row, s in enumerate(self.board[r]) if (r, row) not in removed]
            k = self.config.num_rows[r] - len(keep)
            if k == 0:
                continue
            strip = self.reelstrip[r]
            fresh = []
            for _ in range(k):
                self.reel_positions[r] = (self.reel_positions[r] - 1) % len(strip)
                fresh.insert(0, self.create_symbol(strip[self.reel_positions[r]]))
            self.board[r] = fresh + keep
            new_cells += [(r, row) for row in range(k)]
        self.land(new_cells)
        for r, row in new_cells:
            new_symbols[r].append(self.board[r][row])
        tumble_event(self, removed, new_symbols, reason)
        self.flush_souls()
        self.resolve_specials(new_cells)

    def initial_board(self):
        self.draw_board(emit_event=False)
        self.land(self.cells())
        reveal_event(self)
        self.resolve_specials(self.cells())

    # ================================================================ specials
    def resolve_specials(self, cells):
        for name in SPECIAL_ORDER:
            for r, row in sorted(cells):
                if self.board[r][row].name != name:
                    continue  # already consumed by an earlier special
                if name == "SP":
                    self.resolve_split(r, row)
                elif name == "WB":
                    self.resolve_bomb(r, row, 2, "bomb", "wildBomb")
                elif name == "GB":
                    self.resolve_bomb(r, row, 3, "gbomb", "goldenWildBomb")
                elif name == "DO":
                    self.resolve_overlord(r, row)

    def resolve_split(self, r, row):
        name = get_random_outcome(self.config.split_table)
        sym = self.make_regular(name)
        sym.double = True
        self.board[r][row] = sym
        self.stats["splits"] += 1
        special_event(self, "split", (r, row), [(r, row)], {"symbol": name})

    def bomb_area(self, r, row, size):
        nr, nrow = self.config.num_reels, self.config.num_rows[0]
        if size == 2:  # the bomb is the top-left cell, shifted to stay on the board
            r0, row0 = min(r, nr - 2), min(row, nrow - 2)
        else:  # 3x3 centred on the bomb, clamped to the board
            r0, row0 = min(max(r - 1, 0), nr - 3), min(max(row - 1, 0), nrow - 3)
        return [(a, b) for a in range(r0, r0 + size) for b in range(row0, row0 + size)]

    def resolve_bomb(self, r, row, size, src, kind):
        cells = [c for c in self.bomb_area(r, row, size) if self.board[c[0]][c[1]].name != "S"]
        mult = self.draw_wild_mult()
        if src == "gbomb":
            mult = max(mult, self.config.golden_bomb_min_mult[self.special_ctx()])
        group = self.new_group()
        for a, b in cells:
            old = self.board[a][b]
            if is_wild(old) and (a, b) != (r, row):
                continue  # existing wilds keep their own multiplier
            self.release_soul(old)
            self.board[a][b] = self.make_wild(src, mult, group)
        self.stats["golden_bombs" if src == "gbomb" else "wild_bombs"] += 1
        special_event(self, kind, (r, row), cells)
        self.flush_souls()
        self.pending_seals += self.config.seals_per_special["GB" if src == "gbomb" else "WB"]

    def resolve_overlord(self, r, row):
        """Demon Overlord: fills its reel with wilds, then every wild takes the highest multiplier showing (min x2)."""
        cells = [(r, b) for b in range(self.config.num_rows[r]) if self.board[r][b].name != "S"]
        group = self.new_group()
        for a, b in cells:
            if not is_wild(self.board[a][b]) or (a, b) == (r, row):
                self.release_soul(self.board[a][b])
                self.board[a][b] = self.make_wild("overlord", 1, group)
        top = max([2] + [s.multiplier or 1 for reel in self.board for s in reel if is_wild(s)])
        for reel in self.board:
            for s in reel:
                if is_wild(s):
                    s.multiplier = top
        self.stats["overlords"] += 1
        special_event(self, "overlord", (r, row), cells, {"multiplier": int(top)})
        self.flush_souls()

    # ================================================================ cascades
    def run_cascades(self):
        while not self.wincap_triggered:
            win_data = self.evaluate_ways()
            if win_data["totalWin"] <= 0 or self.cascade_count >= self.config.max_cascades:
                break
            paid = self.pay_ways(win_data)
            win_info_event(self, win_data, paid)
            tumble_win_event(self)
            self.flush_wincap()
            if self.wincap_triggered:
                break
            removed = set()
            for w in win_data["wins"]:
                for r, row in w["positions"]:
                    s = self.board[r][row]
                    if s.name == "HS" or s.lock > 0:
                        continue
                    if s.shield > 0:
                        s.shield -= 1
                        continue
                    removed.add((r, row))
            for reel in self.board:
                for s in reel:
                    s.lock = 0
            self.cascade_count += 1
            self.eval_index += 1
            self.stats["max_cascade"] = max(self.stats["max_cascade"], self.eval_index)
            self.refill(removed, "win")
            if self.descent_active and self.descent_mult < self.config.descent_max_mult:
                self.descent_mult += 1
                global_mult_event(self, "descent")
            if self.eval_index >= self.config.seal_first_qualifying_win[self.special_ctx()]:
                self.pending_seals += self.config.seals_per_win
            self.process_seals()

    # ================================================================ seals
    def reset_seals(self, prelit_count: int = 0):
        self.seals_lit = []
        self.patterns_done = set()
        prelit = []
        if prelit_count:
            pool = [s for s in SEALS if s != "dominion"]
            prelit = random.sample(pool, prelit_count)
            self.seals_lit = [s for s in SEALS if s in prelit]
        seal_reset_event(self, prelit)

    def process_seals(self):
        while self.pending_seals > 0 and not self.wincap_triggered:
            self.pending_seals -= 1
            unlit = [s for s in SEALS if s not in self.seals_lit]
            if len(self.seals_lit) < self.config.dominion_after:
                unlit = [s for s in unlit if s != "dominion"]
            if not unlit:
                self.pending_seals = 0
                break
            seal = random.choices(unlit, weights=[self.config.seal_weights[s] for s in unlit])[0]
            self.seals_lit.append(seal)
            self.stats["seals_lit"] += 1
            seal_lit_event(self, seal, "cascade")
            self.fire_seal(seal)
            self.check_patterns()
        self.pending_seals = 0

    def regular_cells(self, reels=None):
        return self.positions_where(is_regular, reels)

    def to_wild(self, cells, src, mult=None, shared=False):
        """Turn regular cells into wilds. shared=True: one multiplier group for all of them."""
        group = self.new_group() if shared else None
        if shared and mult is None:
            mult = self.draw_wild_mult()
        for r, row in cells:
            old = self.board[r][row]
            if is_wild(old) or old.name == "S":
                continue
            self.release_soul(old)
            self.board[r][row] = self.make_wild(src, mult, group)
        self.flush_souls()

    def ctx_key(self):
        """'blood' / 'soul' inside a pact bonus, 'bonus' in other bonuses, 'base' in the base game."""
        if self.gametype == self.config.basegame_type:
            return "base"
        return self.pact if self.tier["pact"] else "bonus"

    def fire_seal(self, seal):
        ctx = self.ctx_key()
        base = ctx == "base"
        if seal == "wrath":
            table = self.config.wrath_wilds["blood" if ctx == "blood" else "base"]
            cells = self.pick(self.regular_cells(), int(get_random_outcome(table)))
            self.to_wild(cells, "seal", 1 if base else None)
            seal_power_event(self, seal, {"positions": [{"reel": r, "row": b} for r, b in cells]})
        elif seal == "greed":
            self.harvest(self.config.harvest_factor["seal"], "greed")
        elif seal == "envy":
            present = {}
            for reel in self.board:
                for s in reel:
                    if s.name in LOWS:
                        present[s.name] = present.get(s.name, 0) + 1
            if present:
                low = random.choices(list(present), weights=list(present.values()))[0]
                target = get_random_outcome(self.config.envy_targets)
                cells = self.positions_where(lambda s: s.name == low)
                for r, b in cells:
                    old = self.board[r][b]
                    self.board[r][b] = self.make_regular(target, "seal", old.soul)
                seal_power_event(self, seal, {"from": low, "to": target,
                                              "positions": [{"reel": r, "row": b} for r, b in cells]})
            else:
                seal_power_event(self, seal, {"positions": []})
        elif seal == "pride":
            # Shields single wilds only: Takeover, Hellfire and Apocalypse reels are never shielded.
            cells = self.positions_where(lambda x: is_wild(x) and x.src not in ("takeover", "seal_reel", "apocalypse"))
            for r, b in cells:
                self.board[r][b].shield = max(self.board[r][b].shield, 1)
            seal_power_event(self, seal, {"positions": [{"reel": r, "row": b} for r, b in cells]})
        elif seal == "lust":
            cells = self.pick(self.regular_cells(range(1, self.config.num_reels)), 1)
            self.to_wild(cells, "seal", self.config.lust_base_mult if base else None)
            seal_power_event(self, seal, {"positions": [{"reel": r, "row": b} for r, b in cells]})
        elif seal == "sloth":
            cells = self.positions_where(lambda s: s.name in PREMIUMS)
            for r, b in cells:
                self.board[r][b].lock = 1
            seal_power_event(self, seal, {"positions": [{"reel": r, "row": b} for r, b in cells]})
        elif seal == "gluttony":
            counts = {}
            for reel in self.board:
                for s in reel:
                    if s.name in LOWS:
                        counts[s.name] = counts.get(s.name, 0) + 1
            order = {n: i for i, n in enumerate(LOWS)}
            types = [n for n, _ in sorted(counts.items(), key=lambda kv: (-kv[1], order[kv[0]]))][: self.config.gluttony_types]
            cells = self.positions_where(lambda s: s.name in types)
            seal_power_event(self, seal, {"symbols": types, "positions": [{"reel": r, "row": b} for r, b in cells]})
            if cells:
                self.refill(cells, "gluttony")
        elif seal == "despair":
            self.cataclysm(self.config.despair_reels["seal"], "despair")
        elif seal == "dominion":
            if not self.takeover_done:
                self.takeover("dominion")
            else:
                self.dominion_mult += self.config.dominion_repeat_mult_step
                seal_power_event(self, seal, {"multiplier": self.global_mult()})
                global_mult_event(self, "dominion")

    def harvest(self, factor, source):
        sym = self.most_common_regular(REGULAR)
        if sym is None:
            if source == "greed":
                seal_power_event(self, "greed", {"positions": []})
            return
        cells = self.positions_where(lambda s: s.name == sym)
        amount = round(factor * self.config.paytable[(3, sym)] * len(cells) * self.global_mult(), 2)
        if source == "greed":
            seal_power_event(self, "greed", {"symbol": sym, "positions": [{"reel": r, "row": b} for r, b in cells]})
        paid = self.pay(amount, "seals")
        instant_win_event(self, source, paid, cells)
        tumble_win_event(self)
        self.flush_wincap()
        if not self.wincap_triggered:
            self.refill(cells, source)

    def cataclysm(self, n_reels, source):
        reels = sorted(random.sample(range(self.config.num_reels), n_reels))
        cells = self.regular_cells(reels)
        if source == "despair":
            seal_power_event(self, "despair", {"reels": reels, "positions": [{"reel": r, "row": b} for r, b in cells]})
        if cells:
            self.refill(cells, source)
        return reels, cells

    def check_patterns(self):
        lit = {SEALS.index(s) for s in self.seals_lit}
        for pattern in PATTERN_ORDER:
            if self.wincap_triggered or pattern in self.patterns_done:
                continue
            if pattern == "infernal_dominion":
                if len(lit) == len(SEALS):
                    self.patterns_done.add(pattern)
                    self.stats["patterns"] += 1
                    ctx = "base" if self.gametype == self.config.basegame_type else "bonus"
                    self.dominion_mult *= self.config.dominion_mult[ctx]
                    seal_pattern_event(self, pattern, [list(range(9))], {"multiplier": self.global_mult()})
                    global_mult_event(self, "dominion")
                continue
            line_type = [t for t, p in PATTERN_FOR_LINE.items() if p == pattern][0]
            done_lines = [line for line in SEAL_LINES[line_type] if all(i in lit for i in line)]
            if not done_lines:
                continue
            self.patterns_done.add(pattern)
            self.stats["patterns"] += 1
            if pattern == "hellfire":
                reel = random.randrange(1, self.config.num_reels)
                cells = [(reel, b) for b in range(self.config.num_rows[reel])]
                base = self.gametype == self.config.basegame_type
                self.to_wild(cells, "seal_reel", 1 if base else None, shared=True)
                seal_pattern_event(self, pattern, done_lines, {"reels": [reel]})
            elif pattern == "soul_harvest":
                seal_pattern_event(self, pattern, done_lines, {})
                self.harvest(self.config.harvest_factor["pattern"], "soul_harvest")
            elif pattern == "cataclysm":
                reels, _ = self.cataclysm(self.config.despair_reels["pattern"], "cataclysm")
                seal_pattern_event(self, pattern, done_lines, {"reels": reels})

    # ================================================================ takeover
    def takeover(self, trigger):
        if self.takeover_done or self.wincap_triggered:
            return
        self.takeover_done = True
        self.stats["takeovers"] += 1
        reels = sorted(random.sample(range(1, self.config.num_reels), self.config.takeover_reels))
        ctx = self.ctx_key()
        mult = int(get_random_outcome(self.config.takeover_mult[ctx]))
        cells = [(r, b) for r in reels for b in range(self.config.num_rows[r])]
        self.to_wild(cells, "takeover", mult, shared=True)
        takeover_event(self, reels, mult, trigger)

    def roll_takeover(self):
        key = "base" if self.gametype == self.config.basegame_type else self.bonus_tier
        if random.random() < self.config.takeover_chance[key]:
            self.takeover("random")

    # ================================================================ souls
    def release_soul(self, sym):
        if sym.soul and self.souls_active:
            self.soul_queue.append(sym.soul)
        sym.soul = None

    def flush_souls(self):
        if not self.soul_queue:
            return
        new, dup, from_shards = [], [], []
        for soul in self.soul_queue:
            if len(self.souls) == len(SOULS):
                break
            if soul not in self.souls:
                self.souls.append(soul)
                new.append(soul)
            else:
                dup.append(soul)
                self.shards += 1
                if self.shards >= self.config.shards_per_soul:
                    self.shards -= self.config.shards_per_soul
                    missing = [s for s in SOULS if s not in self.souls]
                    if missing:
                        award = random.choice(missing)
                        self.souls.append(award)
                        from_shards.append(award)
                        self.stats["shard_awards"] += 1
        self.soul_queue = []
        if len(self.souls) == len(SOULS):
            self.shards = 0
        soul_collected_event(self, new, dup, from_shards)
        self.check_soul_milestones()

    def check_soul_milestones(self):
        n = len(self.souls)
        cfg = self.config
        if n >= cfg.soul_wild_milestone and "wild" not in self.milestones:
            self.milestones.add("wild")
            self.soul_wild_active = True
            soul_milestone_event(self, cfg.soul_wild_milestone, "extraWild")
        if n >= cfg.soul_mult_milestone and "mult" not in self.milestones:
            self.milestones.add("mult")
            self.soul_mult_active = True
            soul_milestone_event(self, cfg.soul_mult_milestone, "enhancedMultipliers")
        if n >= cfg.apocalypse_milestone and "apocalypse" not in self.milestones:
            self.milestones.add("apocalypse")
            self.apocalypse_pending = True
            self.stats["seven_souls"] = 1
            soul_milestone_event(self, cfg.apocalypse_milestone, "soulApocalypse")

    def soul_wild(self):
        cells = self.pick(self.regular_cells(range(1, self.config.num_reels)), 1)
        self.to_wild(cells, "soulwild")
        special_event(self, "soulWild", cells[0] if cells else (0, 0), cells)

    def soul_apocalypse(self):
        self.apocalypse_pending = False
        self.apocalypse_done = True
        self.stats["apocalypse"] = 1
        spec = self.config.apocalypse.get(self.pact if self.tier["pact"] else "default")
        reels = sorted(random.sample(range(1, self.config.num_reels), spec["reels"]))
        cells = [(r, b) for r in reels for b in range(self.config.num_rows[r])]
        self.to_wild(cells, "apocalypse", spec["mult"], shared=True)
        for reel in self.board:
            for s in reel:
                if is_wild(s):
                    s.multiplier = max(s.multiplier or 1, spec["mult"])
        apocalypse_event(self, reels, spec["mult"])
        self.apocalypse_phase = True
        self.run_cascades()
        self.apocalypse_phase = False

    # ================================================================ one spin
    def play_spin(self):
        """One base spin or one free spin (steps 1-7 in the module docstring)."""
        self.eval_index = 0
        self.cascade_count = 0
        self.takeover_done = False
        self.dominion_mult = 1
        self.pending_seals = 0
        if self.gametype == self.config.basegame_type:
            self.reset_seals(0)
        elif not self.seals_persist or len(self.seals_lit) == len(SEALS) or self.fs == 1:
            self.reset_seals(self.tier["seal_prelit"])
        self.initial_board()
        if self.gametype == self.config.freegame_type:
            if self.descent_active:
                purge = self.positions_where(lambda s: s.name in self.config.descent_purge)
                purge_event(self, purge)
                if purge:
                    self.refill(purge, "purge")
            if self.soul_wild_active:
                self.soul_wild()
        self.roll_takeover()
        self.process_seals()
        self.run_cascades()
        if self.apocalypse_pending and not self.apocalypse_done and not self.wincap_triggered:
            self.soul_apocalypse()

    def count_scatters(self) -> int:
        return sum(1 for reel in self.board for s in reel if s.name == "S")

    def tier_for_scatters(self, n):
        best = None
        for name, t in self.config.bonus_tiers.items():
            if n >= t["scatters"] and (best is None or t["scatters"] > self.config.bonus_tiers[best]["scatters"]):
                best = name
        return best
