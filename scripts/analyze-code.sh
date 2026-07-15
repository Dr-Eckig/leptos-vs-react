set -e

python3 -m lizard \
  -l rust \
  ../leptos-kanban/src \
  -i -1 \
  -o ../leptos-complexity.html

python3 -m lizard \
  -l typescript \
  -l tsx \
  ../react-kanban/src \
  -i -1 \
  -o ../react-complexity.html

# explorer.exe react-complexity.html
# explorer.exe leptos-complexity.html