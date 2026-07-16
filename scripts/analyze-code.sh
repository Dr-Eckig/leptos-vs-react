set -e

cargo install tokei

mkdir -p "../results/implementation"

python3 -m lizard \
  -l rust \
  "../leptos-kanban/src" \
  -i -1 \
  -o "../results/implementation/leptos-complexity.html"

python3 -m lizard \
  -l typescript \
  -l tsx \
  "../react-kanban/src" \
  -i -1 \
  -o "../results/implementation/react-complexity.html"

python3 "../shared/decision-density.py"
