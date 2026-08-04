import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = PROJECT_DIR.parent
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_DIR / ".matplotlib-cache"))

RESULTS_DIR = REPO_ROOT / "results"
PERFORMANCE_RESULTS_DIR = RESULTS_DIR / "performance"
MINIMIZED_PERFORMANCE_RESULTS_DIR = PERFORMANCE_RESULTS_DIR / "minimized"
BOARD_PERFORMANCE_RESULTS_DIR = PERFORMANCE_RESULTS_DIR / "by-board"
REACTIVITY_RESULTS_DIR = RESULTS_DIR / "reactivity"
IMPLEMENTATION_RESULTS_DIR = RESULTS_DIR / "implementation"

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

BOARD_PLOT_SPECS = (
    ("Board 1 (Leer)", "empty-board"),
    ("Board 2 (10 Tasks)", "board-with-10-tasks"),
    ("Board 3 (100 Tasks)", "board-with-100-tasks"),
    ("Board 4 (1000 Tasks)", "board-with-1000-tasks"),
)

BROWSER_LABELS = {
    "chromium": "Chromium",
    "firefox": "Firefox",
    "webkit": "WebKit",
}

FRAMEWORK_ORDER = ["Leptos", "React"]
FRAMEWORK_PALETTE = {
    "Leptos": "#EF3B39",
    "React": "#61dafb",
}
BROWSER_ORDER = ["chromium", "firefox", "webkit"]

MILLISECOND_TICKS = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000]

# Shared plot appearance
PLOT_THEME_STYLE = "whitegrid"
PLOT_THEME_CONTEXT = "paper"
PLOT_THEME_RC = {"figure.max_open_warning": 0}
PLOT_DPI = 300
PLOT_BBOX_INCHES = "tight"
PLOT_TITLE_PAD = 12
PLOT_GRID_LINESTYLE = "--"
PLOT_GRID_LINEWIDTH = 0.5
PLOT_GRID_ALPHA = 0.55
PLOT_VALUE_LIMIT_FACTOR = 1.18
PLOT_LEGEND_TITLE = "Framework"
PLOT_LEGEND_FRAME = True
PLOT_VALUE_SCALE = "log"
PLOT_DESPINE_LEFT = True
PLOT_DESPINE_BOTTOM = False
BAR_LABEL_PADDING = 3
BAR_LABEL_FONT_SIZE = 9

# Scenario boxplots
SCENARIO_PLOT_MIN_HEIGHT = 7
SCENARIO_PLOT_HEIGHT_PER_ROW = 0.48
SCENARIO_PLOT_WIDTH = 13
BOXPLOT_FLIER_SIZE = 2.5
BOXPLOT_LINEWIDTH = 1
BOXPLOT_DODGE = True
PERFORMANCE_PLOT_TITLE = "Kanban-Performance nach Szenario - {browser}"
PERFORMANCE_PLOT_X_LABEL = "Ausführungsdauer in Millisekunden"
PERFORMANCE_PLOT_Y_LABEL = "Szenario: Aktion und Boardgröße"
PERFORMANCE_PLOT_FILENAME = "performance-boxplots-{browser}.png"
SCENARIO_LEGEND_LOCATION = "center left"
SCENARIO_LEGEND_ANCHOR = (1.01, 0.5)

# Focused performance boxplots
MINIMIZED_ACTION_GROUPS = (
    (
        "task-management",
        ("task-create", "task-edit", "task-delete"),
        "Aufgaben erstellen, bearbeiten und löschen",
    ),
    (
        "task-movement",
        ("task-move-within-column", "task-move-between-columns"),
        "Aufgaben innerhalb und zwischen Spalten verschieben",
    ),
    ("board-switch", ("board-switch",), "Board wechseln"),
)
MINIMIZED_PLOT_MIN_HEIGHT = 4.8
MINIMIZED_PLOT_HEIGHT_PER_ROW = 0.55
MINIMIZED_PLOT_WIDTH = 10
MINIMIZED_PLOT_TITLE = "Kanban-Performance: {group} - {browser}"
MINIMIZED_PLOT_X_LABEL = "Ausführungsdauer in Millisekunden"
MINIMIZED_PLOT_Y_LABEL = "Szenario: Aktion und Boardgröße"
MINIMIZED_PLOT_FILENAME = "performance-boxplots-{group}-{browser}.png"
MINIMIZED_PLOT_LEGEND_LOCATION = "center left"
MINIMIZED_PLOT_LEGEND_ANCHOR = (1.01, 0.5)
MINIMIZED_MILLISECOND_TICKS = [5, 20, 100, 500, 2000]

# One interaction boxplot per board size
BOARD_PLOT_MIN_HEIGHT = 4.8
BOARD_PLOT_HEIGHT_PER_ACTION = 0.65
BOARD_PLOT_WIDTH = 10
BOARD_PLOT_TITLE = "Kanban-Performance: {board} – {browser}"
BOARD_PLOT_X_LABEL = "Ausführungsdauer in Millisekunden"
BOARD_PLOT_Y_LABEL = "Aktion"
BOARD_PLOT_FILENAME = "performance-boxplots-{board_slug}-{browser}.png"

# Initial-load boxplot
INITIAL_LOAD_PLOT_HEIGHT = 4.2
INITIAL_LOAD_PLOT_ASPECT = 1.15
INITIAL_LOAD_SHARE_Y = True
INITIAL_LOAD_PLOT_TITLE = "Initial Load: FCP und LCP nach Browser"
INITIAL_LOAD_PLOT_TITLE_Y = 1.02
INITIAL_LOAD_PLOT_X_LABEL = "Zeit in Millisekunden"
INITIAL_LOAD_PLOT_Y_LABEL = "Metrik"
INITIAL_LOAD_SUBPLOT_TITLE_PAD = 10
INITIAL_LOAD_LEGEND_LOCATION = "center right"
INITIAL_LOAD_LEGEND_ANCHOR = (1.0, 0.5)
INITIAL_LOAD_LAYOUT_RECT = (0, 0, 0.91, 1)
INITIAL_LOAD_PLOT_FILENAME = "initial-load-boxplots.png"

# Bundle-size plot
BUNDLE_SIZE_PARTS = (
    ("stylesheet_size_kib", "CSS", "#2965F1"),
    ("script_size_kib", "JavaScript", "#F7DD1E"),
    ("wasm_size_kib", "WebAssembly", "#654FF0"),
    ("other_size_kib", "Nicht aufgeschlüsselt", "#94a3b8"),
)
BUNDLE_SIZE_FIGURE_SIZE = (6.8, 4.8)
BUNDLE_SIZE_BAR_EDGE_COLOR = "white"
BUNDLE_SIZE_BAR_LINEWIDTH = 0.7
BUNDLE_SIZE_TOTAL_FONT_SIZE = 9
BUNDLE_SIZE_TOTAL_FONT_WEIGHT = "bold"
BUNDLE_SIZE_TOTAL_HORIZONTAL_ALIGNMENT = "center"
BUNDLE_SIZE_TOTAL_VERTICAL_ALIGNMENT = "bottom"
BUNDLE_SIZE_TOTAL_FORMAT = "{value:.2f} KiB"
BUNDLE_SIZE_PLOT_TITLE = "Bundle-Größe"
BUNDLE_SIZE_PLOT_X_LABEL = "Framework"
BUNDLE_SIZE_PLOT_Y_LABEL = "Bundle-Größe in KiB"
BUNDLE_SIZE_LEGEND_TITLE = "Bestandteil"
BUNDLE_SIZE_PLOT_FILENAME = "bundle-size.png"

# DOM-mutation plot
DOM_MUTATION_PLOT_TITLE = "Erfasste DOM-Änderungen nach Szenario"
DOM_MUTATION_PLOT_X_LABEL = (
    "Anzahl (Text- und Attributänderungen, hinzugefügte und entfernte Elemente)"
)
DOM_MUTATION_PLOT_Y_LABEL = "Szenario"
DOM_MUTATION_PLOT_FILENAME = "dom-mutations.png"
DOM_MUTATION_TASK_MANAGEMENT_ACTIONS = (
    "task-create",
    "task-edit",
    "task-delete",
    "task-move-within-column",
    "task-move-between-columns",
)
DOM_MUTATION_TASK_MANAGEMENT_PLOT_TITLE = (
    "Erfasste DOM-Änderungen im Task-Management"
)
DOM_MUTATION_TASK_MANAGEMENT_PLOT_FILENAME = (
    "dom-mutations-task-management.png"
)

# Cyclomatic-complexity distribution
COMPLEXITY_DISTRIBUTION_TITLE = "Verteilung der zyklomatischen Komplexität"
COMPLEXITY_DISTRIBUTION_X_LABEL = "Zyklomatische Komplexität pro Funktion"
COMPLEXITY_DISTRIBUTION_Y_LABEL = "Anteil der Funktionen in Prozent"
COMPLEXITY_DISTRIBUTION_FILENAME = "cyclomatic-complexity-frequency.png"
COMPLEXITY_DISTRIBUTION_FIGURE_SIZE = (9.2, 5.4)
COMPLEXITY_DISTRIBUTION_BAR_WIDTH = 0.8

# Summary tables
PERFORMANCE_SUMMARY_COLUMNS = [
    "framework",
    "browser",
    "action",
    "board",
    "min",
    "max",
    "mean",
    "median",
    "standardabweichung",
]
PERFORMANCE_TABLE_COLUMN_LABELS = {
    "framework": "Framework",
    "browser": "Browser",
    "action": "Action",
    "board": "Board",
    "min": "Min",
    "max": "Max",
    "mean": "Mean",
    "median": "Median",
    "standardabweichung": "Standardabweichung",
}
PERFORMANCE_TABLE_NUMBER_COLUMNS = [
    "Min",
    "Max",
    "Mean",
    "Median",
    "Standardabweichung",
]
PERFORMANCE_TABLE_FILENAME = "performance-summary-table-{framework}.png"
PERFORMANCE_TABLE_TITLE = "Performance Summary – {framework}"
PERFORMANCE_TABLE_FIGURE_WIDTH = 16
PERFORMANCE_TABLE_MIN_HEIGHT = 8
PERFORMANCE_TABLE_ROW_HEIGHT = 0.27
PERFORMANCE_TABLE_HEIGHT_PADDING = 1.6
PERFORMANCE_TABLE_COLUMN_WIDTHS = [
    0.075,
    0.075,
    0.16,
    0.16,
    0.07,
    0.07,
    0.075,
    0.075,
    0.15,
]
PERFORMANCE_TABLE_FONT_SIZE = 7.5
PERFORMANCE_TABLE_SCALE = (1, 1.25)
PERFORMANCE_TABLE_LOCATION = "center"

COMPLEXITY_TABLE_COLUMN_LABELS = {
    "framework": "Framework",
    "mean": "Arithm. Mittel",
    "median": "Median",
    "min": "Minimum",
    "max": "Maximum",
    "standardabweichung": "Standardabweichung",
}
COMPLEXITY_TABLE_NUMBER_COLUMNS = [
    "Arithm. Mittel",
    "Median",
    "Minimum",
    "Maximum",
    "Standardabweichung",
]
COMPLEXITY_TABLE_FILENAME = "cyclomatic-complexity-summary-table.png"
COMPLEXITY_TABLE_TITLE = "Zyklomatische Komplexität im Vergleich"
COMPLEXITY_TABLE_FIGURE_SIZE = (10, 3.2)
COMPLEXITY_TABLE_COLUMN_WIDTHS = [0.18, 0.17, 0.13, 0.13, 0.13, 0.24]
COMPLEXITY_TABLE_FONT_SIZE = 9
COMPLEXITY_TABLE_SCALE = (1, 1.4)

DOM_TABLE_COLUMN_LABELS = {
    "framework": "Framework",
    "action": "Action",
    "board": "Board",
    "mutationRecords": "Mutation Records",
    "textChanges": "Textänderungen",
    "attributeChanges": "Attributänderungen",
    "addedElements": "Hinzugefügte Elemente",
    "removedElements": "Entfernte Elemente",
}
DOM_TABLE_FILENAME = "dom-mutations-summary-table.png"
DOM_TABLE_TITLE = "DOM-Mutationen Summary"
DOM_TABLE_ALL_BOARDS_LABEL = "Alle Boards"
DOM_TABLE_FIGURE_WIDTH = 18
DOM_TABLE_MIN_HEIGHT = 8
DOM_TABLE_ROW_HEIGHT = 0.34
DOM_TABLE_HEIGHT_PADDING = 1.8
DOM_TABLE_BBOX = (0, 0, 1, 0.95)
DOM_TABLE_COLUMN_WIDTHS = [0.09, 0.2, 0.15, 0.1, 0.11, 0.125, 0.14, 0.125]
DOM_TABLE_FONT_SIZE = 7.2
DOM_TABLE_SCALE = (1, 1.35)
DOM_TABLE_LOCATION = "upper center"

TABLE_CELL_ALIGNMENT = "left"
TABLE_AXIS_VISIBILITY = "off"
TABLE_HEADER_COLOR = "#f0f2f5"
TABLE_BORDER_COLOR = "#d8dde3"
TABLE_ODD_ROW_COLOR = "#ffffff"
TABLE_EVEN_ROW_COLOR = "#f8fafc"
TABLE_HEADER_TEXT_COLOR = "#1f2933"
TABLE_BODY_TEXT_COLOR = "#263238"
TABLE_FRAMEWORK_TEXT_COLOR = "#111827"
TABLE_BORDER_LINEWIDTH = 0.45
TABLE_TITLE_PAD = 18
TABLE_TITLE_FONT_SIZE = 14
TABLE_TITLE_FONT_WEIGHT = "bold"
TABLE_NUMBER_FORMAT = "{value:.2f}"
INITIAL_LOAD_BOARD_LABEL = "Initial Load"
