set -e

cargo run --manifest-path ../statistics-kanban/polars/Cargo.toml -- ../statistics-kanban/seaborn/data ../statistics-kanban/polars/performance-summary.json