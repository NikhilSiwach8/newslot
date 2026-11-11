#!/usr/bin/env bash
# Set up the Stake Engine Math SDK next to this repo's game and link the game into it.
# The SDK clone (math-sdk/) is not committed; the game lives in math/stormglass_keep/.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SDK="${ROOT}/math-sdk"
GAME="stormglass_keep"

if [ ! -d "${SDK}" ]; then
  git clone --depth=1 https://github.com/StakeEngine/math-sdk.git "${SDK}"
fi

ln -sfn "${ROOT}/math/${GAME}" "${SDK}/games/${GAME}"

(cd "${SDK}" && make setup)

echo "Ready. Run the game with: cd math-sdk && make run GAME=${GAME}"
