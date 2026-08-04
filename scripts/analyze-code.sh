set -e

cargo install tokei

mkdir -p "../results/implementation"

python3 -m lizard \
  -l rust \
  "../leptos-kanban/src" \
  -i -1 \
  -o "../results/implementation/leptos-complexity.html"

python3 "../shared/export-complexity-json.py" \
  --framework "Leptos" \
  --language rust \
  --source "../leptos-kanban/src" \
  --output "../results/implementation/leptos-complexity.json"

python3 -m lizard \
  -l typescript \
  -l tsx \
  "../react-kanban/src" \
  -i -1 \
  -o "../results/implementation/react-complexity.html"

python3 "../shared/export-complexity-json.py" \
  --framework "React" \
  --language typescript \
  --language tsx \
  --source "../react-kanban/src" \
  --output "../results/implementation/react-complexity.json"

python3 "../shared/implementation-metrics.py"
