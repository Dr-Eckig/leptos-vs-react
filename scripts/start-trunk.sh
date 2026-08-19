#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
TOOLS_ROOT="$PROJECT_ROOT/.tools"
TRUNK_BIN="$TOOLS_ROOT/bin/trunk"

source "$SCRIPT_DIR/tool-versions.sh"

cargo install trunk \
  --version "$TRUNK_VERSION" \
  --locked \
  --root "$TOOLS_ROOT"

if [[ "$($TRUNK_BIN --version)" != "trunk $TRUNK_VERSION"* ]]; then
  echo "Erwartet wurde Trunk $TRUNK_VERSION, installiert ist: $($TRUNK_BIN --version)" >&2
  exit 1
fi

cd "$PROJECT_ROOT/leptos-kanban"
"$TRUNK_BIN" build --release --locked
"$TRUNK_BIN" serve --release --locked --port=8080
