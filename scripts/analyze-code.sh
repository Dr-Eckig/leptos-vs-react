set -e

cargo install tokei

if ! command -v qlty >/dev/null 2>&1; then
  echo "Qlty CLI nicht gefunden. Installation: https://docs.qlty.sh/cli/quickstart" >&2
  exit 1
fi

mkdir -p "../results/implementation"

python3 "../shared/export_qlty_metrics.py" \
  --framework "Leptos" \
  --source "../leptos-kanban/src" \
  --output "../results/implementation/leptos-qlty-metrics.json"

python3 "../shared/export_qlty_metrics.py" \
  --framework "React" \
  --source "../react-kanban/src" \
  --output "../results/implementation/react-qlty-metrics.json"

python3 "../shared/implementation-metrics.py"
