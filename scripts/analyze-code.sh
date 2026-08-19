#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
TOOLS_ROOT="$PROJECT_ROOT/.tools"
TOOLS_BIN="$TOOLS_ROOT/bin"

source "$SCRIPT_DIR/tool-versions.sh"

mkdir -p "$TOOLS_BIN"

cargo install tokei \
  --version "$TOKEI_VERSION" \
  --locked \
  --root "$TOOLS_ROOT"

TOKEI_BIN="$TOOLS_BIN/tokei"
if [[ "$($TOKEI_BIN --version)" != "tokei $TOKEI_VERSION"* ]]; then
  echo "Erwartet wurde Tokei $TOKEI_VERSION, installiert ist: $($TOKEI_BIN --version)" >&2
  exit 1
fi

QLTY_BIN="$TOOLS_BIN/qlty"
if [[ ! -x "$QLTY_BIN" ]] || [[ "$($QLTY_BIN --version)" != "qlty $QLTY_VERSION "* ]]; then
  command -v curl >/dev/null 2>&1 || {
    echo "curl wird fuer die Installation von Qlty benoetigt." >&2
    exit 1
  }

  curl --proto '=https' --tlsv1.2 --fail --silent --show-error --location https://qlty.sh \
    | QLTY_VERSION="$QLTY_VERSION" \
      QLTY_INSTALL_BIN_PATH="$TOOLS_BIN" \
      QLTY_NO_MODIFY_PATH=1 \
      sh
fi

if [[ "$($QLTY_BIN --version)" != "qlty $QLTY_VERSION "* ]]; then
  echo "Erwartet wurde Qlty $QLTY_VERSION, installiert ist: $($QLTY_BIN --version)" >&2
  exit 1
fi

mkdir -p "$PROJECT_ROOT/results/implementation"

PATH="$TOOLS_BIN:$PATH" python3 "$PROJECT_ROOT/shared/export_qlty_metrics.py" \
  --framework "Leptos" \
  --source "$PROJECT_ROOT/leptos-kanban/src" \
  --output "$PROJECT_ROOT/results/implementation/leptos-qlty-metrics.json"

PATH="$TOOLS_BIN:$PATH" python3 "$PROJECT_ROOT/shared/export_qlty_metrics.py" \
  --framework "React" \
  --source "$PROJECT_ROOT/react-kanban/src" \
  --output "$PROJECT_ROOT/results/implementation/react-qlty-metrics.json"

PATH="$TOOLS_BIN:$PATH" python3 "$PROJECT_ROOT/shared/implementation-metrics.py"
