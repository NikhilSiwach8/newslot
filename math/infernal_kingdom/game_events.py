"""Infernal Kingdom book events.

Boards are [reel][row], 6 reels x 4 rows, row 0 at the top, no padding rows.
Amounts are integer cents of the base bet (x100), like the SDK's own events.
Events that rewrite cells carry a full `board` snapshot so the client can always resync.
"""

from game_calculations import sym_json


def _cents(x: float) -> int:
    return int(round(x * 100))


def _pos(cells):
    return [{"reel": r, "row": row} for r, row in cells]


def _add(gs, event: dict):
    event["index"] = len(gs.book.events)
    gs.book.add_event(event, copy=False)


def reveal_event(gs):
    _add(gs, {"type": "reveal", "board": gs.board_json(), "gameType": gs.gametype,
              "reelStrip": gs.reelstrip_id})


def special_event(gs, kind: str, origin, cells, extra: dict = None):
    """kind: split | wildBomb | goldenWildBomb | overlord."""
    ev = {"type": "specialResolve", "kind": kind, "origin": {"reel": origin[0], "row": origin[1]},
          "positions": _pos(cells), "board": gs.board_json()}
    ev.update(extra or {})
    _add(gs, ev)


def win_info_event(gs, win_data: dict, paid: float):
    wins = []
    for w in win_data["wins"]:
        wins.append({"symbol": w["symbol"], "kind": w["kind"], "ways": w["ways"], "win": _cents(w["win"]),
                     "positions": _pos(w["positions"]),
                     "meta": {"wildMult": w["meta"]["wildMult"], "globalMult": w["meta"]["globalMult"], "winWithoutMult": _cents(w["meta"]["winWithoutMult"])}})
    ev = {"type": "winInfo", "totalWin": _cents(paid), "wins": wins}
    if paid < win_data["totalWin"]:
        ev["cappedFrom"] = _cents(win_data["totalWin"])
    _add(gs, ev)


def tumble_win_event(gs):
    _add(gs, {"type": "updateTumbleWin", "amount": _cents(gs.win_manager.spin_win)})


def tumble_event(gs, removed, new_symbols, reason: str):
    """Cells in `removed` disappear; survivors fall; `newSymbols[reel]` fill each reel from the top (top-down)."""
    _add(gs, {"type": "tumbleBoard", "reason": reason, "explodingSymbols": _pos(sorted(removed)),
              "newSymbols": [[sym_json(s) for s in reel] for reel in new_symbols]})


def seal_reset_event(gs, prelit):
    _add(gs, {"type": "sealReset", "lit": list(gs.seals_lit), "prelit": list(prelit)})


def seal_lit_event(gs, seal: str, reason: str):
    _add(gs, {"type": "sealLit", "seal": seal, "reason": reason, "lit": list(gs.seals_lit)})


def seal_power_event(gs, seal: str, details: dict):
    ev = {"type": "sealPower", "seal": seal, "board": gs.board_json()}
    ev.update(details)
    _add(gs, ev)


def seal_pattern_event(gs, pattern: str, lines, details: dict):
    ev = {"type": "sealPattern", "pattern": pattern, "lines": lines, "board": gs.board_json()}
    ev.update(details)
    _add(gs, ev)


def instant_win_event(gs, source: str, amount: float, cells):
    _add(gs, {"type": "instantWin", "source": source, "amount": _cents(amount), "positions": _pos(cells)})


def takeover_event(gs, reels, mult: int, trigger: str):
    _add(gs, {"type": "infernalTakeover", "trigger": trigger, "reels": list(reels), "multiplier": int(mult),
              "board": gs.board_json()})


def global_mult_event(gs, source: str):
    _add(gs, {"type": "globalMult", "source": source, "multiplier": gs.global_mult(),
              "dominion": int(gs.dominion_mult), "descent": int(gs.descent_mult)})


def soul_collected_event(gs, souls, duplicates, from_shards):
    _add(gs, {"type": "soulCollected", "souls": list(souls), "duplicates": list(duplicates),
              "fromShards": list(from_shards), "collected": list(gs.souls), "shards": int(gs.shards)})


def soul_milestone_event(gs, count: int, effect: str):
    _add(gs, {"type": "soulMilestone", "count": count, "effect": effect})


def apocalypse_event(gs, reels, mult: int):
    _add(gs, {"type": "soulApocalypse", "reels": list(reels), "multiplier": int(mult),
              "souls": list(gs.souls), "board": gs.board_json()})


def bargain_event(gs):
    _add(gs, {"type": "demonsBargain", "pact": gs.pact})


def enter_bonus_event(gs):
    _add(gs, {"type": "enterBonus", "bonus": gs.bonus_tier, "pact": gs.pact if gs.tier["pact"] else None,
              "totalFs": int(gs.tot_fs), "souls": list(gs.souls)})


def fs_trigger_event(gs, retrigger: bool):
    cells = gs.positions_where(lambda s: s.name == "S")
    _add(gs, {"type": "freeSpinTrigger", "retrigger": retrigger, "totalFs": int(gs.tot_fs), "positions": _pos(cells)})


def update_fs_event(gs):
    _add(gs, {"type": "updateFreeSpin", "amount": int(gs.fs), "total": int(gs.tot_fs)})


def purge_event(gs, removed):
    _add(gs, {"type": "abyssalPurge", "positions": _pos(sorted(removed))})
