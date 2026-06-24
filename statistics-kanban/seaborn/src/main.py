import os
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_DIR / ".matplotlib-cache"))

import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter


DATA_DIR = PROJECT_DIR / "data"
PLOTS_DIR = PROJECT_DIR / "plots"

ACTION_LABELS = {
    "task-create": "Aufgabe erstellen",
    "task-edit": "Aufgabe bearbeiten",
    "task-delete": "Aufgabe löschen",
    "task-move-within-column": "Aufgabe innerhalb einer Spalte verschieben",
    "task-move-between-columns": "Aufgabe zwischen Spalten verschieben",
    "board-switch": "Board wechseln",
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


def main() -> None:
    measurements = load_measurements(DATA_DIR)
    PLOTS_DIR.mkdir(exist_ok=True)

    sns.set_theme(style="whitegrid", context="paper")

    output_paths = [
        create_browser_boxplot(measurements, browser)
        for browser in ordered_values(measurements["browser"], BROWSER_ORDER)
    ]

    print(f"Loaded {len(measurements)} measurements from {DATA_DIR}")
    print("Created plots:")
    for output_path in output_paths:
        print(f"- {output_path}")


def load_measurements(data_dir: Path) -> pd.DataFrame:
    json_files = sorted(data_dir.rglob("*.json"))

    if not json_files:
        raise FileNotFoundError(f"No JSON files found in {data_dir}")

    frames = [pd.read_json(json_file) for json_file in json_files]
    measurements = pd.concat(frames, ignore_index=True)
    missing_columns = required_columns() - set(measurements.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required column(s): {missing}")

    measurements["performance_ms"] = measurements["performance"].map(
        parse_performance_ms,
    )
    measurements["browser"] = measurements["browser"].str.lower()
    measurements["framework"] = measurements["framework"].str.title()
    measurements["scenario"] = measurements.apply(scenario_label, axis=1)
    measurements["scenario"] = pd.Categorical(
        measurements["scenario"],
        categories=scenario_order(),
        ordered=True,
    )

    return measurements.sort_values(["browser", "scenario", "framework", "run"])


def create_browser_boxplot(measurements: pd.DataFrame, browser: str) -> Path:
    browser_measurements = measurements[measurements["browser"] == browser]
    scenario_labels = ordered_values(
        browser_measurements["scenario"],
        scenario_order(),
    )

    fig_height = max(7, len(scenario_labels) * 0.48)
    fig, ax = plt.subplots(figsize=(13, fig_height))

    sns.boxplot(
        data=browser_measurements,
        x="performance_ms",
        y="scenario",
        hue="framework",
        order=scenario_labels,
        hue_order=FRAMEWORK_ORDER,
        palette=FRAMEWORK_PALETTE,
        dodge=True,
        fliersize=2.5,
        linewidth=1,
        ax=ax,
    )

    browser_label = BROWSER_LABELS.get(browser, browser.title())
    ax.set_title(f"Kanban-Performance nach Szenario - {browser_label}", pad=12)
    ax.set_xlabel("Ausführungsdauer in Millisekunden (logarithmische Skala)")
    ax.set_ylabel("Szenario: Aktion und Boardgröße")
    ax.set_xscale("log")
    configure_millisecond_axis(ax)
    ax.grid(axis="x", which="both", linestyle="--", linewidth=0.5, alpha=0.55)
    ax.grid(axis="y", visible=False)
    ax.legend(
        title="Framework",
        loc="center left",
        bbox_to_anchor=(1.01, 0.5),
        frameon=True,
    )

    sns.despine(left=True, bottom=False)
    fig.tight_layout()

    output_path = PLOTS_DIR / f"performance-boxplots-{browser}.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return output_path


def configure_millisecond_axis(ax: Axes) -> None:
    lower, upper = ax.get_xlim()
    ticks = [
        tick
        for tick in MILLISECOND_TICKS
        if lower <= tick <= upper
    ]

    ax.xaxis.set_major_locator(FixedLocator(ticks))
    ax.xaxis.set_major_formatter(FuncFormatter(format_millisecond_tick))
    ax.xaxis.set_minor_formatter(NullFormatter())


def format_millisecond_tick(value: float, _position: int) -> str:
    if value >= 1:
        return f"{value:.0f} ms"

    return f"{value:.1f} ms".replace(".", ",")


def required_columns() -> set[str]:
    return {"run", "browser", "framework", "board", "action", "performance"}


def parse_performance_ms(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)

    normalized = str(value).strip().removesuffix("ms").strip().replace(",", ".")
    return float(normalized)


def scenario_label(row: pd.Series) -> str:
    action = ACTION_LABELS.get(row["action"], str(row["action"]))
    board = BOARD_LABELS.get(row["board"], str(row["board"]))

    return f"{action} | {board}"


def scenario_order() -> list[str]:
    return [
        f"{ACTION_LABELS[action]} | {BOARD_LABELS[board]}"
        for action in ACTION_ORDER
        for board in boards_for_action(action)
    ]


def boards_for_action(action: str) -> list[str]:
    if action in {"task-create", "board-switch"}:
        return BOARD_ORDER

    return BOARD_ORDER[1:]


def ordered_values(values: pd.Series, preferred_order: list[str]) -> list[str]:
    present_values = set(values.dropna().astype(str))
    ordered = [value for value in preferred_order if value in present_values]
    unexpected = sorted(present_values - set(ordered))

    return ordered + unexpected


if __name__ == "__main__":
    main()
