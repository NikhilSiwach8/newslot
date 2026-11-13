# INFERNAL KINGDOM

*Rule Beyond the Flames.* A dark-fantasy 6x4, 4,096-ways cascading video slot for Stake
Engine, with the Nine Hell Seals, Infernal Takeover, Demon's Bargain, Seven Souls and the
Soul Apocalypse. Maximum win 66,666x the bet.

| Path | What |
|---|---|
| `math/infernal_kingdom/` | Math model on the Stake Engine Math SDK (Python): config, rules, reel strips, optimizer targets, tests, tools |
| `math/infernal_kingdom/reports/` | Simulation, RTP, volatility and max-win reports (generated) |
| `web-sdk/apps/infernal_kingdom/` | Frontend on the Stake Engine Web SDK (Svelte + PixiJS) |
| `docs/MATH_DESIGN.md` | Every rule and number, and why |
| `docs/GAME_RULES.md` | Player-facing rules and paytable |
| `docs/ASSET_MANIFEST.md` | Every art, animation and audio asset and its status |
| `art/` | Prompt pack (`PROMPTS.md`), generator, placeholder art and packing scripts |

## Run it

```bash
bash scripts/setup-math.sh
```

```bash
cd math-sdk && make run GAME=infernal_kingdom
```

```bash
cd math-sdk && env/bin/python games/infernal_kingdom/tests/test_rules.py
```

```bash
cd math-sdk && env/bin/python games/infernal_kingdom/tools/report.py
```

```bash
cd math-sdk && env/bin/python games/infernal_kingdom/tools/export_frontend.py
```

```bash
bash scripts/setup-web.sh
```

```bash
cd web-sdk && pnpm turbo run build --filter=infernal_kingdom...
```

```bash
cd web-sdk/apps/infernal_kingdom && PUBLIC_CHROMATIC=true npx storybook dev -p 6010 public --ci
```

## Not finished

- All art is labelled placeholder art; sounds, frame, fonts and several spines are Stake
  Web SDK samples. None of it may ship. See `docs/ASSET_MANIFEST.md`.
- The brief's "supplied math reference" was not available, so bonus entry, spin counts,
  buy prices and the Hellstar, Demon Overlord and Split Symbol rules are original designs.
- The Demon's Bargain pact is chosen before the bet (it selects the bet mode), because a
  Stake Engine round is fully decided when the bet is placed.
- Not yet run inside Stake Engine itself: tested with Storybook against real books and the
  SDK's format checks (all eight modes pass, 6 of 6 Studio risk checks).
- Every mode publishes at exactly 96.00%. Raw mechanics (natural play, 20,000 bonuses each)
  sit at 88-109%: Furnace Blood ~88% vs Soul ~100%, Covenant Blood ~90% vs Soul ~109%. The
  published weights close the gap with small tilts; Covenant could be tuned closer still.
  See `math/infernal_kingdom/reports/MATH_REPORT.md`.
