#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT/statistics-kanban"

python3 -m venv .venv
.venv/bin/python -m pip install --requirement requirements.txt
.venv/bin/python src/main.py
