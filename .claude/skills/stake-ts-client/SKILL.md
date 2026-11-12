---
name: stake-ts-client
description: Use the official Stake Engine TypeScript client (npm package `stake-engine`, repo engineio/ts-client) to talk to the RGS from a game frontend. Covers RGSClient setup from launch-URL parameters, Authenticate / Play / EndRound / Event, bet-level validation, the 1,000,000-scaled money format, DisplayAmount / ParseAmount, jurisdiction flags, and the balanceUpdate / roundActive window events. Use when wiring RGS calls, wallet or balance display, bet validation, round lifecycle, or debugging "sessionID / rgs_url is not set" and bet-amount errors.
---

# Stake Engine TypeScript client (`stake-engine`)

Thin browser client for the Stake Engine RGS. Upstream: <https://github.com/engineio/ts-client> (ISC, BETA — written against v0.1.32). RGS API docs: <https://stake-engine.com/docs/rgs>.

When exact behaviour matters, read the source rather than trusting this summary: it is ~650 lines in `src/client.ts`, `src/helpers.ts`, `src/types.ts` (in `node_modules/stake-engine/` once installed).

## Install

```bash
pnpm add stake-engine
```

In this repo the frontend lives in `web-sdk/apps/infernal_kingdom`. The Stake web-sdk already ships its own RGS layer (`packages/rgs-fetcher`, `rgs-requests`); don't run both against the same session. Use this client for a frontend that is not built on that layer, or deliberately replace it.

## Setup

```ts
import { RGSClient } from 'stake-engine';

const rgs = RGSClient({
  url: window.location.href, // launch URL supplied by the operator
  enforceBetLevels: true,     // default true
  protocol: 'https',          // default 'https'; 'http' for a local server
});
```

The constructor reads query parameters and throws when one is missing or invalid:

| Param | Required | Notes |
|---|---|---|
| `sessionID` | yes | sent with every request |
| `rgs_url` | yes | host only, no scheme; protocol comes from the option |
| `lang` | no | defaults to `en`; operator-chosen, not the browser language |
| `device` | no | `desktop` (default) or `mobile`; anything else throws |

## Calls

| Method | Endpoint | Returns |
|---|---|---|
| `Authenticate()` | `POST /wallet/authenticate` | `{ balance, config, jurisdictionFlags, round }` |
| `Play({ amount, mode })` | `POST /wallet/play` | `{ balance, round }` |
| `EndRound()` | `POST /wallet/end-round` | `{ balance }` |
| `Event(value)` | `POST /bet/event` | `{ event }` |

Rules enforced client-side:

- `Authenticate()` must be called first; every other call throws otherwise. It also fills `rgs.balance`, `rgs.authenticateConfig` (`minBet`, `maxBet`, `stepBet`, `defaultBetLevel`, `betLevels`) and `rgs.jurisdictionFlags`.
- If `Authenticate()` returns `round.active`, a round is still open: resume and finish it, then call `EndRound()`.
- `Play` throws if a round is active, if `amount` is not a multiple of `stepBet`, is outside `minBet..maxBet`, or (when `enforceBetLevels`) is not in `betLevels`.
- Call `EndRound()` only when `Play` returned an active round (a win to collect); a losing round is already closed.
- Non-2xx responses throw.

## Money

Amounts are integers scaled by 1,000,000: 1.00 of currency = `1_000_000`. Pass scaled values to `Play`, normally one of `betLevels`.

Exported helpers (v0.1.32 exports only these two plus `parseBalance`):

- `DisplayAmount(balance, { decimals?, removeSymbol?, trimDecimalForIntegers? })` — takes a `Balance` object `{ amount, currency }`, not a bare number; returns a string formatted in the browser locale with the currency symbol in the right position.
- `ParseAmount(val)` — API amount to a plain number (`1_000_000` → `1`).

To format a bet level, wrap it: `DisplayAmount({ amount: level, currency: rgs.balance.currency }, { trimDecimalForIntegers: true })`.

Use these rather than hand-formatting: symbol, decimals and symbol position vary by currency (JPY/KRW/IDR have 0 decimals; `XGC`/`XSC` are social-casino coins).

## Events

Dispatched on `window`; preferred way to keep UI in sync.

```ts
window.addEventListener('balanceUpdate', (e) => {
  const { amount, currency } = (e as CustomEvent).detail;
});
window.addEventListener('roundActive', (e) => {
  const { active } = (e as CustomEvent).detail; // disable bet controls while true
});
```

`balanceUpdate` fires whenever a response carries a balance. After a `Play` or `EndRound` the client also polls `/wallet/balance` every 60 s, so an idle player's balance stays current. Remove listeners on component teardown.

## Jurisdiction flags

`socialCasino`, `disabledFullscreen`, `disabledTurbo`, `disabledSuperTurbo`, `disabledAutoplay`, `disabledSlamstop`, `disabledSpacebar`, `disabledBuyFeature`, `displayNetPosition`, `displayRTP`, `displaySessionTimer`, `minimumRoundDuration`. The UI must honour each one (hide or disable the feature, show the required element, pad short rounds).

## Pitfalls

- The upstream README is ahead of or behind the code in places: the event is `balanceUpdate` (not `balanceUpdated`), and `DisplayBalance` and `API_MULTIPLIER` are documented but not exported — define `const API_MULTIPLIER = 1_000_000` yourself if needed.
- The client uses `window`, so create it in the browser only (`onMount`, not during SSR/prerender).
- Local testing needs `?sessionID=...&rgs_url=localhost:PORT` on the URL and `protocol: 'http'`.
