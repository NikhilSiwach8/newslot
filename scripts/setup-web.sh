#!/usr/bin/env bash
# Set up the Stake Engine Web SDK workspace around this repo's frontend app.
# Only web-sdk/apps/infernal_kingdom/ is committed here; the rest of the SDK is fetched
# from upstream at a pinned commit. Needs Node 22.16+ and pnpm 10.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SDK="${ROOT}/web-sdk"
APP="${SDK}/apps/infernal_kingdom"
UPSTREAM="https://github.com/StakeEngine/web-sdk.git"
PIN="1843d60"

if [ ! -f "${SDK}/turbo.json" ]; then
  TMP="$(mktemp -d)"
  git clone "${UPSTREAM}" "${TMP}/web-sdk"
  git -C "${TMP}/web-sdk" checkout --quiet "${PIN}"
  rm -rf "${TMP}/web-sdk/.git"
  mkdir -p "${SDK}"
  cp -rn "${TMP}/web-sdk/." "${SDK}/"
  rm -rf "${TMP}"
fi

# Placeholder art and sound: the SDK's cluster sample assets. These are not allowed in a
# Stake Engine submission and must be replaced with original Infernal Kingdom assets.
# Infernal Kingdom's own art in static/assets/infernal/ is committed and is not overwritten.
if [ ! -d "${APP}/static/assets/sprites" ]; then
  mkdir -p "${APP}/static"
  cp -rn "${SDK}/apps/cluster/static/." "${APP}/static/"
fi

(cd "${SDK}" && pnpm install)

echo "Ready. Start Storybook with:"
echo "  cd web-sdk/apps/infernal_kingdom && PUBLIC_CHROMATIC=true npx storybook dev -p 6010 public --ci"
