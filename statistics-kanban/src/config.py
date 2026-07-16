import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = PROJECT_DIR.parent
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_DIR / ".matplotlib-cache"))

RESULTS_DIR = REPO_ROOT / "results"
PERFORMANCE_RESULTS_DIR = RESULTS_DIR / "performance"
REACTIVITY_RESULTS_DIR = RESULTS_DIR / "reactivity"

DATA_DIR = PROJECT_DIR / "data"
DOM_MUTATION_DATA_DIR = PROJECT_DIR / "dom-mutations-data"
BUNDLE_SIZE_DATA_DIR = PROJECT_DIR / "bundle-size-data"
DOM_MUTATION_BROWSER = "chromium"
BUNDLE_SIZE_BROWSER = "chromium"

ACTION_LABELS = {
    "task-create": "Aufgabe erstellen",
    "task-edit": "Aufgabe bearbeiten",
    "task-delete": "Aufgabe löschen",
    "task-move-within-column": "Aufgabe innerhalb einer Spalte verschieben",
    "task-move-between-columns": "Aufgabe zwischen Spalten verschieben",
    "board-switch": "Board wechseln",
}

INITIAL_LOAD_LABELS = {
    "initial-load-fcp": "First Contentful Paint",
    "initial-load-lcp": "Largest Contentful Paint",
}

BOARD_LABELS = {
    "Board 1 (Leer)": "Leeres Board",
    "Board 2 (10 Tasks)": "Board mit 10 Tasks",
    "Board 3 (100 Tasks)": "Board mit 100 Tasks",
    "Board 4 (1000 Tasks)": "Board mit 1000 Tasks",
}

ACTION_ORDER = [
    "task-create",
    "task-edit",
    "task-delete",
    "task-move-within-column",
    "task-move-between-columns",
    "board-switch",
]

INITIAL_LOAD_ORDER = [
    "initial-load-fcp",
    "initial-load-lcp",
]

BOARD_ORDER = [
    "Board 1 (Leer)",
    "Board 2 (10 Tasks)",
    "Board 3 (100 Tasks)",
    "Board 4 (1000 Tasks)",
]

BROWSER_LABELS = {
    "chromium": "Chromium",
    "firefox": "Firefox",
    "webkit": "WebKit",
}

FRAMEWORK_ORDER = ["Leptos", "React"]
FRAMEWORK_PALETTE = {
    "Leptos": "#E87F61",
    "React": "#61dafb",
}
BROWSER_ORDER = ["chromium", "firefox", "webkit"]

MILLISECOND_TICKS = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000]
