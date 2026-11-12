---
name: slot-engine
description: Build, simulate, optimize and locally test slot games with Slot Engine, the community TypeScript toolkit (@slot-engine/core, @slot-engine/optimizer, @slot-engine/panel, @slot-engine/lgs) whose output is compatible with Stake Engine. Use when writing slot math in TypeScript instead of the Python Math SDK, defining symbols / reel sets / game modes / result sets, running simulations or RTP optimization with Slot Engine, exploring books in the Panel GUI, or running a local game server (LGS) so a frontend can be tested without uploading to Stake Engine.
---

# Slot Engine

Community TypeScript libraries for slot games — not affiliated with Stake. Upstream: <https://github.com/slot-engine/slot-engine>, docs: <https://slot-engine.dev/docs/core>.

| Package | Purpose |
|---|---|
| `@slot-engine/core` | Configure and simulate a game; writes books (JSONL) and lookup tables (CSV) in the Stake Engine format |
| `@slot-engine/optimizer` | Reweight lookup tables to hit a target RTP |
| `@slot-engine/panel` | Web GUI: run simulations, view statistics, explore game files, design reel sets |
| `@slot-engine/lgs` | Local game server that mimics the Stake Engine RGS endpoints from your published books |

Requires Node >= 22.15.0 (or >= 23.8.0) for native Zstandard.

## Read the real docs first

The API is young (core 0.4.x) and changes between minor versions. Do not write Slot Engine code from memory. Fetch the upstream docs and examples and read the relevant page:

```bash
bash .claude/skills/slot-engine/scripts/fetch-upstream.sh
```

This shallow-clones upstream to `.upstream/slot-engine` (gitignored) and prints the path. Then read:

| Need | Path under `.upstream/slot-engine/` |
|---|---|
| Quick start, terminology | `docs/content/docs/core/index.mdx`, `core/core-concepts.mdx` |
| Symbols, game modes, reel sets, result sets, hooks, custom state | `docs/content/docs/core/config/*.mdx` |
| Game flow, board / wallet / rng / data / game services | `docs/content/docs/core/game-implementation/`, `core/game-context/` |
| Win calculation (lines, clusters, ...) | `docs/content/docs/core/game-implementation/win-calculation.mdx` |
| Simulation, optimization, analysis | `docs/content/docs/core/game-tasks/*.mdx` |
| Upgrading between versions | `docs/content/docs/core/other/migration-guides.mdx` |
| Panel | `docs/content/docs/panel/` |
| LGS: config, sessions, storage, RGS endpoints | `docs/content/docs/lgs/` |
| Working games | `examples/lines_example`, `examples/cluster_example`, `examples/panel` |

Match the docs to the installed version (`node_modules/@slot-engine/core/package.json`); if they differ, check the migration guide.

## Shape of a game

```ts
import { defineUserState, defineSymbols, defineGameModes, InferGameType, createSlotGame } from "@slot-engine/core"

export const userState = defineUserState({ /* ... */ })
export const symbols = defineSymbols({ /* ... */ })
export const gameModes = defineGameModes({ /* ... */ })
export type GameType = InferGameType<typeof gameModes, typeof symbols, typeof userState>

export const game = createSlotGame<GameType>({
  id: "my-game",
  name: "My Game",
  rootDir: __dirname, // needed for LGS, and when running from another directory
  maxWinX: 5000,
  gameModes, symbols, userState,
  hooks: {}, // the whole game flow lives in one hook, built from service utilities
})

game.configureSimulation({ simRunsAmount: { base: 100_000, bonus: 100_000 }, concurrency: 16 })
game.runTasks({ doSimulation: true })
```

Run it — the flag is mandatory:

```bash
pnpm tsx ./index.ts --slot-engine-run
```

Output lands in the game's `__build__/` directory; `__build__/publish_files` is what gets uploaded to Stake Engine and what the LGS reads. Use about 10k sims per mode for quick checks and at least 500k for release.

## Local game server

```ts
import { EngineLgs, InMemoryStorage } from "@slot-engine/lgs"
import { game } from "./game"

new EngineLgs({ storage: new InMemoryStorage(), games: [game] }).start() // http://localhost:7771
```

Needs core >= 0.4.0, `rootDir: __dirname`, and a completed simulation for every mode. Development only: no authentication, no session expiry. It can also be passed to `createPanel()` to share the panel's port.

## Relation to this repo

`math/stormglass_keep` is built on the official Python Stake Math SDK (see the `stake-math-sdk` skill). Slot Engine is an alternative, not an add-on: the two do not share game code. Don't port or mix them unless asked. Differences that matter: Slot Engine is an npm dependency with typed config and a single game-flow hook; the Math SDK is a cloned Python codebase you subclass, and is the reference implementation Stake reviews against. Either way the published books must still pass Stake's math checks (RTP range, cross-mode RTP spread, max-win hit rate).
