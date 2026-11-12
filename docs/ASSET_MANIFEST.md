# Infernal Kingdom - asset manifest

Status key: **placeholder** = labelled stand-in from `art/placeholders.py` (must be replaced);
**procedural** = drawn in code (Pixi shapes and text) until art exists; **SDK sample** =
Stake Web SDK sample asset copied by `scripts/setup-web.sh` (not allowed in a submission);
**missing** = not in the build yet. Prompts for every art item: `art/PROMPTS.md`.

Nothing is final art yet. Before submission every row must be final and original.

## Sprites (atlas `static/assets/infernal/symbols.json`, frames `ik_<name>.png`, 256x256)

| Name | Asset | Used by | Status |
|---|---|---|---|
| h1 | Demon King | reels | placeholder |
| h2 | Infernal Dragon | reels | placeholder |
| h3 | Cursed Crown | reels | placeholder |
| h4 | Blood Chalice | reels | placeholder |
| h5 | Soul Ring | reels | placeholder |
| l1 - l5 | A, K, Q, J, 10 | reels | placeholder |
| w | Infernal Wild | reels | placeholder |
| hs | Hellstar | reels | placeholder |
| s | Hell Gate scatter | reels | placeholder |
| wb | Wild Bomb | reels (before it resolves) | placeholder |
| gb | Golden Wild Bomb | reels (before it resolves) | placeholder |
| sp | Split Symbol | reels (before it resolves) | placeholder |
| do | Demon Overlord | reels (before it resolves) | placeholder |

## Backgrounds (`static/assets/infernal/*.webp`)

| Name | Size | Used | Status |
|---|---|---|---|
| bg_base_landscape | 1920x1080 | base game, wide screens | placeholder |
| bg_base_portrait | 1080x1920 | base game, tall screens | placeholder |
| bg_bonus_landscape | 1920x1080 | free spins | placeholder |
| bg_takeover_landscape | 1920x1080 | Infernal Takeover (red world) | placeholder |
| bg_bonus_portrait, bg_takeover_portrait | 1080x1920 | tall screens | missing (landscape is cropped) |

## UI art

| Name | Used by | Status |
|---|---|---|
| logo | game name / loading screen | missing (text "INFERNAL KINGDOM") |
| frame | reel frame | SDK sample frame |
| seal_<9 names> | Nine Hell Seals board (`HellSeals.svelte`) | procedural circles |
| soul_<7 names> | Seven Souls meter, Soul orbs on symbols | procedural circles |
| pact_blood, pact_soul | Demon's Bargain contracts (`FeatureOverlay.svelte`) | procedural panels |
| apocalypse_crown | Soul Apocalypse | procedural text |
| bet-mode / buy icons and dialog images | `betModeMeta.ts` | missing (empty slots) |
| loading screen, press-to-continue, win counters, free-spin intro/outro, transition, big-win | SDK components | SDK sample |

## Animations

| Animation | Book event | Status |
|---|---|---|
| Reel spin and cascade | `reveal`, `tumbleBoard` | SDK cascading reel motion with placeholder sprites |
| Symbol win | `winInfo` | pulse (code); removal burst is SDK sample spine |
| Wild Bomb / Golden Wild Bomb / Split / Overlord | `specialResolve` | banner text (code) |
| Seal light, patterns | `sealLit`, `sealPattern` | seal flash + line highlight (code) |
| Infernal Takeover | `infernalTakeover` | banner + red background swap (code) |
| Demon's Bargain | `demonsBargain` | two contract panels, chosen one sealed (code) |
| Soul collection, milestones | `soulCollected`, `soulMilestone` | meter flash + banner (code) |
| Soul Apocalypse | `soulApocalypse` | orbiting souls around the crown (code) |
| Maximum win | `wincap` | full-board 66,666x banner (code) |
| Big-win tiers | `setWin`, `freeSpinEnd` | SDK sample |

## Audio (`static/assets/audio/sounds.*`)

All audio is the SDK sample set (status: SDK sample). The Infernal Kingdom sound list and
brief are in `art/PROMPTS.md` ("Audio brief"); the event-to-sound mapping lives in
`game/bookEventHandlerMap.ts` and `game/sound.ts`.

## Fonts

`proxima-nova` from the SDK sample set; licence must be confirmed or replaced before
submission.
