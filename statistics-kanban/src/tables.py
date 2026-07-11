from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from config import (
    ACTION_LABELS,
    ACTION_ORDER,
    BOARD_LABELS,
    BOARD_ORDER,
    BROWSER_ORDER,
    FRAMEWORK_ORDER,
    FRAMEWORK_PALETTE,
    INITIAL_LOAD_ORDER,
)


SUMMARY_COLUMNS = [
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


def create_performance_summary_table(
    measurements: pd.DataFrame,
    output_dir: Path,
) -> list[Path]:
    summary = summarize_performance(measurements)
    png_path = output_dir / "performance-summary-table.png"

    create_performance_summary_table_image(summary, png_path)

    return [png_path]


def create_dom_mutation_summary_table(
    measurements: pd.DataFrame,
    output_dir: Path,
) -> list[Path]:
    if measurements.empty:
        return []

    summary = summarize_dom_mutations(measurements)
    png_path = output_dir / "dom-mutations-summary-table.png"

    create_dom_mutation_summary_table_image(summary, png_path)

    return [png_path]


def summarize_performance(measurements: pd.DataFrame) -> pd.DataFrame:
    summary = (
        measurements.groupby(
            ["framework", "browser", "action", "board"],
            observed=True,
        )["performance_ms"]
        .agg(
            min="min",
            max="max",
            mean="mean",
            median="median",
            standardabweichung=lambda values: values.std(ddof=1),
        )
        .reset_index()
    )

    for column in ["min", "max", "mean", "median", "standardabweichung"]:
        summary[column] = summary[column].round(2)

    return sort_summary(summary)[SUMMARY_COLUMNS]


def summarize_dom_mutations(measurements: pd.DataFrame) -> pd.DataFrame:
    summary = measurements[
        [
            "framework",
            "action",
            "board",
            "mutationRecords",
            "textChanges",
            "attributeChanges",
            "addedElements",
            "removedElements",
        ]
    ].copy()

    summary = sort_dom_mutation_summary(summary)
    summary["action"] = summary["action"].map(lambda value: ACTION_LABELS.get(value, value))
    summary["board"] = summary["board"].map(lambda value: BOARD_LABELS.get(value, value))

    return summary


def create_performance_summary_table_image(
    summary: pd.DataFrame,
    output_path: Path,
) -> None:
    display_summary = summary.rename(
        columns={
            "framework": "Framework",
            "browser": "Browser",
            "action": "Action",
            "board": "Board",
            "min": "Min",
            "max": "Max",
            "mean": "Mean",
            "median": "Median",
            "standardabweichung": "Standardabweichung",
        },
    )

    row_count = len(display_summary)
    fig_height = max(8, row_count * 0.27 + 1.6)
    fig, ax = plt.subplots(figsize=(16, fig_height))
    ax.axis("off")

    table = ax.table(
        cellText=format_table_values(display_summary),
        colLabels=list(display_summary.columns),
        cellLoc="left",
        colLoc="left",
        loc="center",
        colWidths=[0.075, 0.075, 0.16, 0.16, 0.07, 0.07, 0.075, 0.075, 0.15],
    )

    table.auto_set_font_size(False)
    table.set_fontsize(7.5)
    table.scale(1, 1.25)
    style_table(table, display_summary)

    ax.set_title("Performance Summary", pad=18, fontsize=14, weight="bold")
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def create_dom_mutation_summary_table_image(
    summary: pd.DataFrame,
    output_path: Path,
) -> None:
    display_summary = summary.rename(
        columns={
            "framework": "Framework",
            "action": "Action",
            "board": "Board",
            "mutationRecords": "Mutation Records",
            "textChanges": "Textänderungen",
            "attributeChanges": "Attributänderungen",
            "addedElements": "Hinzugefügte Elemente",
            "removedElements": "Entfernte Elemente",
        },
    )

    row_count = len(display_summary)
    fig_height = max(8, row_count * 0.34 + 1.8)
    fig, ax = plt.subplots(figsize=(18, fig_height))
    ax.axis("off")

    table = ax.table(
        cellText=display_summary.astype(str).values.tolist(),
        colLabels=list(display_summary.columns),
        cellLoc="left",
        colLoc="left",
        loc="upper center",
        bbox=[0, 0, 1, 0.95],
        colWidths=[0.09, 0.2, 0.15, 0.1, 0.11, 0.125, 0.14, 0.125],
    )

    table.auto_set_font_size(False)
    table.set_fontsize(7.2)
    table.scale(1, 1.35)
    style_table(table, display_summary)

    ax.set_title("DOM-Mutationen Summary", pad=18, fontsize=14, weight="bold")
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def format_table_values(summary: pd.DataFrame) -> list[list[str]]:
    formatted = summary.copy()

    for column in ["Min", "Max", "Mean", "Median", "Standardabweichung"]:
        formatted[column] = formatted[column].map(lambda value: f"{value:.2f}")

    return formatted.astype(str).values.tolist()


def style_table(table, summary: pd.DataFrame) -> None:
    header_color = "#f0f2f5"
    border_color = "#d8dde3"
    odd_row_color = "#ffffff"
    even_row_color = "#f8fafc"

    for (row, column), cell in table.get_celld().items():
        cell.set_edgecolor(border_color)
        cell.set_linewidth(0.45)

        if row == 0:
            cell.set_facecolor(header_color)
            cell.set_text_props(weight="bold", color="#1f2933")
            continue

        framework = summary.iloc[row - 1]["Framework"]
        base_color = even_row_color if row % 2 == 0 else odd_row_color
        cell.set_facecolor(base_color)
        cell.set_text_props(color="#263238")

        if column == 0 and framework in FRAMEWORK_PALETTE:
            cell.set_facecolor(FRAMEWORK_PALETTE[framework])
            cell.set_text_props(weight="bold", color="#111827")


def sort_summary(summary: pd.DataFrame) -> pd.DataFrame:
    summary = summary.copy()
    summary["framework"] = pd.Categorical(
        summary["framework"],
        categories=FRAMEWORK_ORDER,
        ordered=True,
    )
    summary["browser"] = pd.Categorical(
        summary["browser"],
        categories=BROWSER_ORDER,
        ordered=True,
    )
    summary["action"] = pd.Categorical(
        summary["action"],
        categories=[*ACTION_ORDER, *INITIAL_LOAD_ORDER],
        ordered=True,
    )
    summary["board"] = pd.Categorical(
        summary["board"],
        categories=[*BOARD_ORDER, "Initial Load"],
        ordered=True,
    )

    summary = summary.sort_values(["framework", "browser", "action", "board"])

    for column in ["framework", "browser", "action", "board"]:
        summary[column] = summary[column].astype(str)

    return summary


def sort_dom_mutation_summary(summary: pd.DataFrame) -> pd.DataFrame:
    summary = summary.copy()
    summary["framework"] = pd.Categorical(
        summary["framework"],
        categories=FRAMEWORK_ORDER,
        ordered=True,
    )
    summary["action"] = pd.Categorical(
        summary["action"],
        categories=ACTION_ORDER,
        ordered=True,
    )
    summary["board"] = pd.Categorical(
        summary["board"],
        categories=BOARD_ORDER,
        ordered=True,
    )

    summary = summary.sort_values(["action", "board", "framework"])

    for column in ["framework", "action", "board"]:
        summary[column] = summary[column].astype(str)

    return summary
