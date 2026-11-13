# Infernal Kingdom: math design

Source of truth: `math/infernal_kingdom/game_config.py` (numbers) and
`game_executables.py` (rules). This document explains them. Measured results are in
`math/infernal_kingdom/reports/`; nothing here claims a result that is not in a report.

## 0. Starting point and what was invented

The brief asked to keep the bonus entry logic, spin counts, buy prices and the Wild Star,
Max Wild and Split Symbol rules of a "supplied math reference" (Forge Spins, Wayfinder's
Blessing, Mine Shaft Tumble, The Soul Forge). **No such reference was in the repository**,
and you chose to have these designed from scratch. So every structure below (scatter tiers,
spin counts, retriggers, buy prices, Hellstar, Demon Overlord, Split Symbol, bomb areas,
landing rates, seal powers, multiplier tables) is an original starting value, tuned by
simulation. If the reference turns up, these are the values to replace.

## 1. Board and wins

- 6 reels x 4 rows, 4,096 ways, left to right from reel 1, 3 to 6 of a kind.
- Per reel, a symbol counts its matching cells (a Split result counts 2) plus every wild on
  that reel. Ways = product of the per-reel counts over consecutive reels.
- A win needs at least one real symbol: wild-only ways pay nothing.
- **Wild multiplier**: the multipliers (x2 and up) of the wilds in a win are **added**.
  Wilds made together (one bomb, one Takeover, one Hellfire reel, one Overlord reel, the
  Apocalypse) share one multiplier and count it once per win.
  *Why:* the first version let each wild count its multiplier into the way count. On a
  4,096-ways grid a 3x3 bomb then multiplied wins by ~216, and simulated base RTP was over
  10,000%. The additive, grouped rule is bounded and easy to explain to players.
- Global multiplier (Infernal Dominion x Abyssal Descent) multiplies every win.

Paytable (x total bet per way):

| Symbol | 3 | 4 | 5 | 6 |
|---|---|---|---|---|
| H1 Demon King | 0.50 | 1.00 | 2.50 | 5.00 |
| H2 Infernal Dragon | 0.40 | 0.80 | 2.00 | 4.00 |
| H3 Cursed Crown | 0.30 | 0.60 | 1.50 | 3.00 |
| H4 Blood Chalice | 0.20 | 0.50 | 1.20 | 2.40 |
| H5 Soul Ring | 0.20 | 0.40 | 1.00 | 2.00 |
| L1 A | 0.10 | 0.20 | 0.50 | 1.00 |
| L2 K | 0.10 | 0.20 | 0.40 | 0.80 |
| L3 Q | 0.10 | 0.10 | 0.30 | 0.60 |
| L4 J | 0.10 | 0.10 | 0.20 | 0.50 |
| L5 10 | 0.10 | 0.10 | 0.20 | 0.40 |

## 2. Spin sequence (one base spin or one free spin)

1. Board drawn from the reel strips (`reels/BR0.csv` base, `FR0.csv` bonus; strips 260 long,
   3 scatters and 0/3-4 wilds per reel; `tools/gen_reels.py`).
2. Each newly landed regular cell may become a special (landing rates below) or, in a bonus,
   carry a Soul orb.
3. Landed specials resolve in fixed order: Split, Wild Bomb, Golden Wild Bomb, Demon Overlord
   (by reel, then row).
4. Bonus only: Abyssal purge (Abyssal Descent), then the 3-Soul extra wild.
5. Random Infernal Takeover roll.
6. Seal activations earned by bombs resolve.
7. Cascade loop: evaluate -> pay -> remove winning cells -> refill from the strip ->
   resolve landed specials -> light seals -> seal powers -> seal patterns -> evaluate again,
   until an evaluation pays nothing.
8. Bonus only: Soul Apocalypse, if due, with its own cascade loop.

Removal exceptions: Hellstars survive two removals; shielded wilds and Time-Locked symbols
survive one. Scatters are never removed or transformed.
A safety stop ends a cascade sequence after 60 evaluations; it was never reached in testing
(the rule tests assert this).

## 3. Special symbols

| Symbol | Where | Rule |
|---|---|---|
| W Infernal Wild | strips, reels 2-6 | Substitutes for H1-L5. Base x1; bonus multiplier from the bonus's wild table. |
| HS Hellstar | lands, reels 2-6 | Multiplier wild (x2/x3 base, x3/x5/x10 bonus) that survives its first two winning cascades. |
| WB Wild Bomb | lands, reels 2-5 | Turns a 2x2 area (bomb = top-left, shifted onto the board) into wilds sharing one multiplier. +1 seal activation. |
| GB Golden Wild Bomb | lands, reels 2-5 | 3x3 area centred on the bomb. Shared multiplier at least x1 base / x2 bonus. +2 seal activations. |
| SP Split Symbol | lands, any reel | Becomes one regular symbol (weighted, premiums rarer) that counts as two. |
| DO Demon Overlord | lands, reels 2-5 | Fills its reel with wilds, then every wild on the board takes the highest multiplier showing (min x2). Original take on a "max wild". |
| S Hell Gate | strips, all reels | Scatter, no pay. Counted when the cascades end. |

Landing rates per new cell (base / bonus): WB 0.0003 / 0.0012, GB 0.00002 / 0.0002,
SP 0.004 / 0.005, HS 0.0004 / 0.001, DO 0.00005 / 0.0002.

## 4. Nine Hell Seals

3x3 board: Wrath Greed Envy / Pride Lust Sloth / Gluttony Despair Dominion.

- **Lighting**: each qualifying winning cascade lights one random unlit seal (weights 10,
  Dominion 4). Base game: a cascade qualifies from the 2nd winning evaluation of the spin;
  bonus: every winning evaluation. Bombs add activations. Dominion cannot light until 5 other
  seals are lit. A seal lights at most once per spin.
- **Reset**: after every base spin and every free spin; Soul Pact keeps seals between free
  spins until all nine are lit (then resets). Bonuses can start spins with prelit seals
  (Hellfire 1, Covenant 1, Furnace 2; never Dominion); prelit seals do not fire powers.

| Seal | Power |
|---|---|
| Wrath - Hellfire | 1-2 random cells become wilds (Blood Pact 2-4) |
| Greed - Soul Harvest | The most common symbol is collected: pays 1x its 3-of-a-kind pay per cell, cells removed and refilled |
| Envy - Symbol Corruption | Every cell of one low symbol becomes one premium (H2-H5) |
| Pride - Infernal Shield | Single wilds survive the next removal (not Takeover/Hellfire/Apocalypse reels) |
| Lust - Wild Attraction | One wild on reels 2-6 (x2 in the base game) |
| Sloth - Time Lock | Premium symbols stay through the next removal |
| Gluttony - Devour | The two most common low symbols are removed and refilled (no pay) |
| Despair - Cataclysm | Regular symbols on 2 random reels are removed and refilled |
| Dominion - Infernal Takeover | Triggers the Takeover; if one already happened this spin, +1 global multiplier |

**Patterns**, resolved in this order, each at most once per spin (once per board in Soul Pact):
Hellfire (any row): one random reel 2-6 becomes wild. Soul Harvest (any column): Greed
power at 2x. Cataclysm (any diagonal): Despair on 3 reels. Infernal Dominion (all nine):
global multiplier x2 base / x3 bonus for the rest of the spin.

Finite by construction: at most 9 seal activations and 4 patterns per spin; every power acts
once; nothing re-lights a seal.

## 5. Infernal Takeover

Two distinct random reels from 2-6 become wild reels sharing one multiplier (base x1; bonus
x2/x3; Blood x3/x5; Soul x1/x2). Triggers: random roll at spin start (base 0.03%; Hellfire
0.8%, Covenant 1%, Abyssal 0.4%, Furnace 3% per spin) or the Dominion seal. **At most one per
spin**; a second trigger becomes +1 global multiplier. Its payout is bounded only by the
round cap; the reports show its measured contribution and largest observed rounds.

## 6. Bonuses

| Bonus | Natural trigger | Spins | Retrigger | Specials |
|---|---|---|---|---|
| Hellfire Spins | 3 scatters | 10 | 3+ scatters: +5 | wild table x1-x10, 1 prelit seal |
| Demon's Covenant | 4 scatters | 12 | +5 | Demon's Bargain pact, 1 prelit seal |
| Abyssal Descent | 5 scatters | 10 | +3 | growing multiplier (+1 per winning cascade, never resets, max x25), J/10 purged each spin |
| The Soul Furnace | 6 scatters | 12 | +5 | pact, 2 prelit seals, 2 Souls to start, 3% Takeover per spin |

At most 3 retriggers per bonus. Tier is set by the scatter count when the base cascades end.

### Demon's Bargain (Covenant, Furnace)

Stake Engine decides the whole round when the bet is placed ("player actions cannot influence
the outcome"), so **the pact is chosen before the bet**: it selects the bet mode. In the
base game, BASE = Blood Pact and BASE_SOUL (same 1x price) = Soul Pact; the buys exist per
pact. The contract scene in the bonus shows both contracts and seals the one chosen. Both
pacts are simulated separately and optimised to the same RTP.

| | Blood Pact | Soul Pact |
|---|---|---|
| Wild multipliers | x1-x25 (x2-x50 after 5 Souls) | x1-x5 (x2-x10) |
| Wrath wilds | 2-4 | 1-2 |
| Takeover | x3 / x5 | x1 / x2 |
| Single wilds | removed when they win | survive their first winning cascade |
| Seals | reset each free spin | persist until all nine are lit |
| Soul orb rate | x1.1 | x1.25 |
| Apocalypse | 3 reels, x7 | 2 reels, x5 |

### Seven Souls (all bonuses)

New regular cells carry a Soul orb with probability 1.2-1.6% per bonus (x pact factor). An
orb is collected when its symbol is removed (by a win or a seal) or turned into a wild. A new
Soul fills its slot; a duplicate becomes a Soul Shard; 3 shards award a random missing Soul
(configurable: `shards_per_soul`). Souls persist through the bonus and its retriggers.
Milestones (once each): 3 Souls - one extra wild at the start of every later spin;
5 Souls - wild multipliers use the enhanced ("_plus") table; 7 Souls - Soul Apocalypse.

### Soul Apocalypse

Once per bonus, after the cascades of the spin in which the 7th Soul arrives: 2 random reels
(Blood 3) become wild, every wild on the board takes at least the Apocalypse multiplier (x5,
Blood x7), and the board is evaluated and cascades again. It does not award the maximum win:
its payout comes from the board like any other.

## 7. Maximum win

- 66,666x the base bet, the same for every mode, applied to the **whole round** (base spin
  plus any bonus and retriggers).
- Every payout goes through `pay()`, which truncates the payout that reaches the cap, sets
  `wincap_triggered` and stops every further payout-generating action (cascades, seals,
  Takeover, free spins, Apocalypse). The `wincap` event comes after the win that reached it.
- Rule tests run every mode with an artificial 300x cap and check that books stop exactly
  at the cap, that nothing pays after it, and that base + free wins equal the payout.

## 8. Bet modes and RTP

| Mode | Cost | Contents |
|---|---|---|
| base | 1x | base game, Blood Pact for pact bonuses |
| base_soul | 1x | base game, Soul Pact for pact bonuses |
| hellfire | 75x | Hellfire Spins |
| covenant_blood / covenant_soul | 250x | Demon's Covenant with that pact |
| abyssal | 275x | Abyssal Descent |
| furnace_blood / furnace_soul | 500x | The Soul Furnace with that pact |

Target RTP 96.00% for every mode (`GameConfig.rtp`). Buy prices were set from measured
natural bonus averages so the re-weighting stays small. `game_optimization.py` sets the
frequency targets: Hellfire 1 in 370, Covenant 1 in 3,500,
Abyssal 1 in 14,000, Furnace 1 in 60,000, max win about 1 in 8.3 million base bets (Stake
asks for better than 1 in 10 million).

### Lookup-table weights

`tools/weights.py` (called by `run.py`) writes the published weights instead of the SDK
optimizer, which met the RTP but left 0.6% of winning base spins at 1x-5x against ~25% in
natural play. Each criteria group gets exactly the probability its targets imply; inside a
group a book's weight is `(1 + payout) ** theta`, with theta solved so the group's mean
matches its RTP share (theta = 0 is natural play; measured |theta| <= 0.13). If a mode
fails a Stake Studio risk check, books (outside the max-win group) paying 10,000x or more
are down-weighted by the gentlest factor that passes all six checks, and theta re-balances
the mean: base 0.6, base_soul 0.8, Furnace buys 0.12, all other buys 1.0. Every book keeps
a non-zero weight. `IK_OPTIMIZER=sdk` restores the SDK optimizer.

## 9. RTP attribution

Every payout is credited to one feature, written per book to
`library/attribution/<mode>_<pid>.jsonl`; `tools/report.py` weights them by the final lookup
tables. A ways win is credited by the first matching source among its wilds: Apocalypse,
Takeover, Golden Wild Bomb, Wild Bomb, Overlord, seal wilds/reels, Soul wild, Hellstar; then
seal-made symbols or an Infernal Dominion multiplier (seals), Split, Abyssal Descent
multiplier; otherwise "regular" (first evaluation of the spin) or "cascade". Seal instant
pays are "seals". This is an accounting convention: a win with several sources is credited
once, to the highest-priority one.

## 10. Tuning history (summary)

1. First pass: wild multiplier counted into ways; base RTP ~12,500%. Switched to additive
   grouped multipliers.
2. Seal chains (Pride shielding Takeover reels, Dominion lighting every ~40 spins) made
   rare 10,000x+ rounds common. Pride no longer shields reel wilds; Dominion needs 5 other
   seals; base seals start from the 2nd winning cascade; base specials rarer.
3. Soul Pact persistence also applied to Takeover reels; restricted to single wilds; Soul
   Pact Takeover multiplier lowered so it stays the lower-peak pact.
4. Strip length 200 -> 260 to bring Hellfire Spins to about 1 in 365 base spins.
5. Stake's format check requires every round payout to be a multiple of 0.1x. Pays of
   0.05/0.25 and the 0.5x Soul Harvest broke that, so every pay is now a multiple of 0.1
   (L3-L5 three-of-a-kind 0.10, H4 0.2/0.5/1.2/2.4) and Soul Harvest pays 1x (pattern 2x).
   With integer ways and multipliers every win stays on the 0.1x grid; the rule tests
   assert it for every book.
6. The first full run showed bonus books hitting the 60-evaluation safety stop: Hellstars
   stayed for the whole spin, so sticky x10 wilds kept completing wins after every refill.
   Hellstars now survive two winning cascades; the deepest sequence measured afterwards was
   10 evaluations. Bonus values fell, so buy prices moved to 75x / 250x / 350x / 550x.
7. The SDK optimizer met every RTP but removed most 1x-5x base wins (a gap Stake's review
   flags), even after the base targets were moved close to the natural split. It was
   replaced by deterministic power-tilt weights (section 8), which keep the natural shape:
   1x-2x and 2x-5x wins are now 5.3% and 4.2% of base rounds.
8. With natural tails restored, the Furnace buys and the base SD broke Stake Studio's risk
   limits (which lower the allowed maximum bet). A tail down-weight for 10,000x+ books,
   chosen per mode as the gentlest that passes, brings all six risk checks back to pass.
9. Natural play showed the Soul Pact paying far more than the Blood Pact in the Furnace
   (~107% vs ~78%), driven by Soul orbs feeding the Apocalypse (1 in 43 Soul Furnaces).
   Soul orb factors moved to Blood x1.1 / Soul x1.25 (Apocalypse 1 in ~96 Soul, ~377
   Blood Furnaces) and prices to the measured averages: Abyssal 275x, Furnace 500x.
