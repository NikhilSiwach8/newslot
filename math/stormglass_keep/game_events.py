"""Stormglass Keep custom book events.

Row indices in position lists follow the SDK convention: +1 when padding symbols are
included in the revealed board. `gridMultipliers` is indexed [reel][row] without padding.
"""

from src.events.events import json_ready_sym

UPDATE_GRID = "updateGrid"
BEAM_METER = "updateBeamMeter"
BEAM_CLEAR = "beamClear"
BEAM_WILDS = "beamWilds"
BEAM_SURGE = "beamSurge"
ENTER_BONUS = "enterBonus"


def _row(gamestate, row: int) -> int:
    return row + 1 if gamestate.config.include_padding else row


def update_grid_mult_event(gamestate):
    """Current charged-cell grid (0 = uncharged, 1 = charged, 2+ = multiplier)."""
    event = {
        "index": len(gamestate.book.events),
        "type": UPDATE_GRID,
        "gridMultipliers": [list(reel) for reel in gamestate.position_multipliers],
    }
    gamestate.book.add_event(event, copy=False)


def beam_meter_event(gamestate):
    """Beam meter value after a winning tumble."""
    event = {
        "index": len(gamestate.book.events),
        "type": BEAM_METER,
        "meter": int(gamestate.beam_meter),
    }
    gamestate.book.add_event(event)


def beam_clear_event(gamestate, positions: list):
    """Beam stage 1: low symbols are removed (no payout) and the board refills."""
    special_attributes = list(gamestate.config.special_symbols.keys())
    new_symbols = [
        [json_ready_sym(s, special_attributes) for s in reel_syms]
        for reel_syms in gamestate.new_symbols_from_tumble
    ]
    event = {
        "index": len(gamestate.book.events),
        "type": BEAM_CLEAR,
        "stage": 1,
        "explodingSymbols": [{"reel": p[0], "row": _row(gamestate, p[1])} for p in positions],
        "newSymbols": new_symbols,
    }
    gamestate.book.add_event(event, copy=False)


def beam_wilds_event(gamestate, positions: list):
    """Beam stage 2: wilds are placed on the board."""
    event = {
        "index": len(gamestate.book.events),
        "type": BEAM_WILDS,
        "stage": 2,
        "positions": [{"reel": p[0], "row": _row(gamestate, p[1])} for p in positions],
    }
    gamestate.book.add_event(event, copy=False)


def beam_surge_event(gamestate):
    """Beam stage 3: every charged cell doubles. Followed by an updateGrid event."""
    event = {
        "index": len(gamestate.book.events),
        "type": BEAM_SURGE,
        "stage": 3,
    }
    gamestate.book.add_event(event)


def enter_bonus_event(gamestate):
    """Which bonus tier was triggered: watch, eye or drowned."""
    tier = gamestate.config.bonus_tiers[gamestate.bonus_tier]
    event = {
        "index": len(gamestate.book.events),
        "type": ENTER_BONUS,
        "tier": gamestate.bonus_tier,
        "totalFs": int(gamestate.tot_fs),
        "maxMultiplier": int(tier["max_mult"]),
    }
    gamestate.book.add_event(event)
