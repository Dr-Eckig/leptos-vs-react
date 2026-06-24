set -e

cd ../leptos-kanban
trunk build --release
trunk serve --release --port=8080