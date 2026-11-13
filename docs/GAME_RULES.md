# INFERNAL KINGDOM - game rules

*Rule Beyond the Flames.*

These are the player-facing rules and paytable. Keep them in step with
`math/infernal_kingdom/game_config.py`; RTP figures come from
`math/infernal_kingdom/reports/MATH_REPORT.md`.

## The game

- 6 reels, 4 rows, 4,096 ways to win.
- Wins pay for 3 to 6 matching symbols on adjacent reels, starting from the leftmost reel.
- Ways are counted per symbol: the number of matching symbols (and wilds) on each reel,
  multiplied together across the reels in the win.
- Only the highest win per symbol is paid; wins on different symbols are added.
- All wins are multiplied by the bet. Malfunction voids all pays and plays.

## Cascades

After every win the winning symbols are removed, the remaining symbols fall and new symbols
drop in from above. Cascades continue while new wins form.

## Paytable (x bet, per way)

| Symbol | 3 | 4 | 5 | 6 |
|---|---|---|---|---|
| Demon King | 0.50 | 1.00 | 2.50 | 5.00 |
| Infernal Dragon | 0.40 | 0.80 | 2.00 | 4.00 |
| Cursed Crown | 0.30 | 0.60 | 1.50 | 3.00 |
| Blood Chalice | 0.20 | 0.50 | 1.20 | 2.40 |
| Soul Ring | 0.20 | 0.40 | 1.00 | 2.00 |
| A | 0.10 | 0.20 | 0.50 | 1.00 |
| K | 0.10 | 0.20 | 0.40 | 0.80 |
| Q | 0.10 | 0.10 | 0.30 | 0.60 |
| J | 0.10 | 0.10 | 0.20 | 0.50 |
| 10 | 0.10 | 0.10 | 0.20 | 0.40 |

## Special symbols

- **Infernal Wild** (reels 2-6) substitutes for every paying symbol. Wilds in free spins can
  carry a multiplier. A win needs at least one paying symbol.
- **Wild multipliers**: the multipliers of the wilds in a win are added together. Wilds
  created together by one feature share one multiplier, counted once per win.
- **Hellstar** (reels 2-6): a wild with a multiplier that stays on the reels through its
  first two winning cascades.
- **Wild Bomb** (reels 2-5): explodes when it lands and turns a 2x2 area into wilds.
- **Golden Wild Bomb** (reels 2-5): turns the 3x3 area around it into wilds; in free spins
  they carry at least x2.
- **Split Symbol**: becomes a paying symbol that counts as two of that symbol.
- **Demon Overlord** (reels 2-5): fills its reel with wilds, then every wild on the reels
  takes the highest wild multiplier showing (at least x2).
- **Hell Gate** (scatter): 3, 4, 5 or 6 Hell Gates when the cascades end trigger a bonus.
  Hell Gates do not pay.

## Nine Hell Seals

A 3x3 board of seals. In the base game each winning cascade from the second one in a spin
lights one seal; in free spins every winning cascade lights one. Wild Bombs light one extra
seal, Golden Wild Bombs two. Each seal lights at most once per spin, and the Dominion seal
can only light after five other seals. Seals reset after every spin.

| Seal | Power when it lights |
|---|---|
| Wrath | Hellfire: 1-2 symbols become wilds (2-4 with the Blood Pact) |
| Greed | Soul Harvest: the most common symbol is collected for an instant win (its 3-of-a-kind pay for each one) |
| Envy | Corruption: every symbol of one low type becomes one premium symbol |
| Pride | Infernal Shield: single wilds survive the next cascade |
| Lust | Wild Attraction: one wild appears on reels 2-6 |
| Sloth | Time Lock: premium symbols stay through the next cascade |
| Gluttony | Devour: the two most common low symbols are removed |
| Despair | Cataclysm: two reels collapse and refill |
| Dominion | Infernal Takeover |

Completed lines on the seal board trigger, once each per spin, in this order:
any row - **Hellfire** (a reel becomes wild); any column - **Soul Harvest** (double the Greed pay); any diagonal -
**Cataclysm** (three reels collapse); all nine seals - **Infernal Dominion** (every later win
in the spin x2, x3 in free spins).

## Infernal Takeover

The Demon King turns two random reels (2-6) into wild reels. It can trigger at random at the
start of any spin, or from the Dominion seal, at most once per spin.

## Bonuses

| Hell Gates | Bonus | Free spins | Features |
|---|---|---|---|
| 3 | Hellfire Spins | 10 | multiplier wilds x1-x10 |
| 4 | Demon's Covenant | 12 | Demon's Bargain pact |
| 5 | Abyssal Descent | 10 | a win multiplier that grows by 1 with every winning cascade and never resets (up to x25); J and 10 are purged from every spin's first board |
| 6 | The Soul Furnace | 12 | Demon's Bargain pact, starts with 2 Souls and 2 lit seals, Infernal Takeover far more often |

3 or more Hell Gates during free spins award +5 free spins (+3 in Abyssal Descent), up to 3
times per bonus. The Nine Hell Seals and the Seven Souls are active in every bonus.

### Demon's Bargain

Demon's Covenant and The Soul Furnace are played under a pact, **chosen before you bet**:
play normally for the **Blood Pact**, or activate **Soul Pact** (same bet). Buying one of
these bonuses, you choose the pact by choosing the buy.

- **Blood Pact**: higher wild multipliers, more Hellfire wilds, Takeover wilds x3 or x5.
  Higher peaks, more volatile.
- **Soul Pact**: single wilds survive their first winning cascade, the Hell Seals stay lit
  between free spins until all nine are lit, more Soul orbs. Lower peaks.

Both pacts have the same return to player.

### Seven Souls

During free spins, symbols can carry a Soul orb (Wrath, Greed, Envy, Pride, Lust, Sloth,
Gluttony). The Soul is collected when its symbol is removed or turns into a wild. A Soul you
already hold becomes a Soul Shard; 3 shards award a missing Soul. Souls are kept for the
whole bonus, including retriggers.

- 3 Souls: one extra Infernal Wild at the start of every later free spin.
- 5 Souls: enhanced wild multipliers for the rest of the bonus.
- 7 Souls: **Soul Apocalypse**.

### Soul Apocalypse

Once per bonus, after the spin in which the seventh Soul is collected: two reels (three with
the Blood Pact) become wild, every wild takes at least x5 (x7 with the Blood Pact), and the
reels are evaluated and cascade again. It does not guarantee any particular win.

## Bet modes and buys

| Option | Cost | RTP |
|---|---|---|
| Base game (Blood Pact) | 1x bet | 96.00% |
| Soul Pact (base game) | 1x bet | 96.00% |
| Buy Hellfire Spins | 75x bet | 96.00% |
| Buy Demon's Covenant (Blood or Soul) | 250x bet | 96.00% |
| Buy Abyssal Descent | 350x bet | 96.00% |
| Buy The Soul Furnace (Blood or Soul) | 550x bet | 96.00% |

RTP values are the theoretical return of each option over a very large number of rounds,
taken from the optimised math model; see the math report for the exact figures.

## Maximum win

The maximum win is **66,666x the bet** per round, for every option. It covers the whole
round: the base spin, every cascade, every feature, the bonus and its retriggers. When a round
reaches it, the round ends and pays 66,666x.

## Disclaimer

Winnings are settled according to the amount received from the RGS and not from events
within the web browser. Animations do not affect the outcome, which is decided when the bet
is placed.
