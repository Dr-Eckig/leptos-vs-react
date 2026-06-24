import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_DIR / ".matplotlib-cache"))

DATA_DIR = PROJECT_DIR / "data"
PLOTS_DIR = PROJECT_DIR / "plots"

MEMORY_ACTION_SUFFIX = "-js-heap-used"

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

INITIAL_LOAD_MEMORY_LABELS = {
    "initial-load-js-heap-used": "Belegter JS-Heap",
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

INITIAL_LOAD_MEMORY_ORDER = [
    "initial-load-js-heap-used",
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
BYTE_TICKS = [
    256 * 1024,
    512 * 1024,
    1024 * 1024,
    2 * 1024 * 1024,
    4 * 1024 * 1024,
    8 * 1024 * 1024,
    16 * 1024 * 1024,
    32 * 1024 * 1024,
    64 * 1024 * 1024,
]
