#!/usr/bin/env bash
# Shallow-clone (or update) slot-engine/slot-engine for its docs and examples.
set -euo pipefail
root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
dest="${1:-$root/.upstream/slot-engine}"
if [ -d "$dest/.git" ]; then
  git -C "$dest" pull --ff-only --depth 1 -q || echo "warning: could not update, using existing copy" >&2
else
  mkdir -p "$(dirname "$dest")"
  git clone --depth 1 -q https://github.com/slot-engine/slot-engine.git "$dest"
fi
echo "$dest"
