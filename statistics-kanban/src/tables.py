from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

import config as cfg
from data import collapse_equal_dom_mutation_boards


def create_performance_summary_table(
    measurements: pd.DataFrame,
    output_dir: Path,
) -> list[Path]:
    summary = summarize_performance(measurements)
    output_paths = []

    for framework in cfg.FRAMEWORK_ORDER:
        framework_summary = summary[summary["framework"] == framework]
        if framework_summary.empty:
            continue

        png_path = output_dir / cfg.PERFORMANCE_TABLE_FILENAME.format(
            framework=framework.lower(),
        )
        create_performance_summary_table_image(
            framework_summary,
            png_path,
            framework,
        )
        output_paths.append(png_path)

    return output_paths


def create_dom_mutation_summary_table(
    measurements: pd.DataFrame,
    output_dir: Path,
) -> list[Path]:
    if measurements.empty:
        return []

    summary = summarize_dom_mutations(measurements)
    png_path = output_dir / cfg.DOM_TABLE_FILENAME

    create_dom_mutation_summary_table_image(summary, png_path)

    return [png_path]


def create_complexity_summary_table(
    measurements: pd.DataFrame,
    output_dir: Path,
) -> Path | None:
    if measurements.empty:
        return None

    summary = summarize_complexity(measurements)
    display_summary = summary.rename(columns=cfg.COMPLEXITY_TABLE_COLUMN_LABELS)
    formatted = display_summary.copy()
    for column in cfg.COMPLEXITY_TABLE_NUMBER_COLUMNS:
        formatted[column] = formatted[column].map(
            lambda value: cfg.TABLE_NUMBER_FORMAT.format(value=value)
        )

    fig, ax = plt.subplots(figsize=cfg.COMPLEXITY_TABLE_FIGURE_SIZE)
    ax.axis(cfg.TABLE_AXIS_VISIBILITY)
    table = ax.table(
        cellText=formatted.astype(str).values.tolist(),
        colLabels=list(formatted.columns),
        cellLoc=cfg.TABLE_CELL_ALIGNMENT,
        colLoc=cfg.TABLE_CELL_ALIGNMENT,
        loc="center",
        colWidths=cfg.COMPLEXITY_TABLE_COLUMN_WIDTHS,
    )
    table.auto_set_font_size(False)
    table.set_fontsize(cfg.COMPLEXITY_TABLE_FONT_SIZE)
    table.scale(*cfg.COMPLEXITY_TABLE_SCALE)
    style_table(table, display_summary)

    ax.set_title(
        cfg.COMPLEXITY_TABLE_TITLE,
        pad=cfg.TABLE_TITLE_PAD,
        fontsize=cfg.TABLE_TITLE_FONT_SIZE,
        weight=cfg.TABLE_TITLE_FONT_WEIGHT,
    )
    fig.tight_layout()

    output_path = output_dir / cfg.COMPLEXITY_TABLE_FILENAME
    save_table_figure(fig, output_path)
    plt.close(fig)
    return output_path


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

    return sort_summary(summary)[cfg.PERFORMANCE_SUMMARY_COLUMNS]


def summarize_complexity(measurements: pd.DataFrame) -> pd.DataFrame:
    summary = (
        measurements.groupby("framework", observed=True)["cyclomatic_complexity"]
        .agg(
            mean="mean",
            min="min",
            max="max",
            standardabweichung=lambda values: values.std(ddof=1),
        )
        .reindex(cfg.FRAMEWORK_ORDER)
        .dropna(how="all")
        .reset_index()
    )
    numeric_columns = ["mean", "min", "max", "standardabweichung"]
    summary[numeric_columns] = summary[numeric_columns].round(2)
    return summary


def summarize_dom_mutations(measurements: pd.DataFrame) -> pd.DataFrame:
    summary = collapse_equal_dom_mutation_boards(measurements)[
        [
            "framework",
            "action",
            "board",
            "boards_collapsed",
            "mutationRecords",
            "textChanges",
            "attributeChanges",
            "addedElements",
            "removedElements",
        ]
    ].copy()

    summary = sort_dom_mutation_summary(summary)
    summary["action"] = summary["action"].map(
        lambda value: cfg.ACTION_LABELS.get(value, value)
    )
    summary["board"] = summary.apply(
        lambda row: (
            cfg.DOM_TABLE_ALL_BOARDS_LABEL
            if row["boards_collapsed"]
            else cfg.BOARD_LABELS.get(row["board"], row["board"])
        ),
        axis=1,
    )

    return summary.drop(columns="boards_collapsed")


def create_performance_summary_table_image(
    summary: pd.DataFrame,
    output_path: Path,
    framework: str,
) -> None:
    display_summary = summary.rename(columns=cfg.PERFORMANCE_TABLE_COLUMN_LABELS)

    row_count = len(display_summary)
    fig_height = max(
        cfg.PERFORMANCE_TABLE_MIN_HEIGHT,
        row_count * cfg.PERFORMANCE_TABLE_ROW_HEIGHT
        + cfg.PERFORMANCE_TABLE_HEIGHT_PADDING,
    )
    fig, ax = plt.subplots(
        figsize=(cfg.PERFORMANCE_TABLE_FIGURE_WIDTH, fig_height),
    )
    ax.axis(cfg.TABLE_AXIS_VISIBILITY)

    table = ax.table(
        cellText=format_table_values(display_summary),
        colLabels=list(display_summary.columns),
        cellLoc=cfg.TABLE_CELL_ALIGNMENT,
        colLoc=cfg.TABLE_CELL_ALIGNMENT,
        loc=cfg.PERFORMANCE_TABLE_LOCATION,
        colWidths=cfg.PERFORMANCE_TABLE_COLUMN_WIDTHS,
    )

    table.auto_set_font_size(False)
    table.set_fontsize(cfg.PERFORMANCE_TABLE_FONT_SIZE)
    table.scale(*cfg.PERFORMANCE_TABLE_SCALE)
    style_table(table, display_summary)

    ax.set_title(
        cfg.PERFORMANCE_TABLE_TITLE.format(framework=framework),
        pad=cfg.TABLE_TITLE_PAD,
        fontsize=cfg.TABLE_TITLE_FONT_SIZE,
        weight=cfg.TABLE_TITLE_FONT_WEIGHT,
    )
    fig.tight_layout()
    save_table_figure(fig, output_path)
    plt.close(fig)


def create_dom_mutation_summary_table_image(
    summary: pd.DataFrame,
    output_path: Path,
) -> None:
    display_summary = summary.rename(columns=cfg.DOM_TABLE_COLUMN_LABELS)

    row_count = len(display_summary)
    fig_height = max(
        cfg.DOM_TABLE_MIN_HEIGHT,
        row_count * cfg.DOM_TABLE_ROW_HEIGHT + cfg.DOM_TABLE_HEIGHT_PADDING,
    )
    fig, ax = plt.subplots(figsize=(cfg.DOM_TABLE_FIGURE_WIDTH, fig_height))
    ax.axis(cfg.TABLE_AXIS_VISIBILITY)

    table = ax.table(
        cellText=display_summary.astype(str).values.tolist(),
        colLabels=list(display_summary.columns),
        cellLoc=cfg.TABLE_CELL_ALIGNMENT,
        colLoc=cfg.TABLE_CELL_ALIGNMENT,
        loc=cfg.DOM_TABLE_LOCATION,
        bbox=cfg.DOM_TABLE_BBOX,
        colWidths=cfg.DOM_TABLE_COLUMN_WIDTHS,
    )

    table.auto_set_font_size(False)
    table.set_fontsize(cfg.DOM_TABLE_FONT_SIZE)
    table.scale(*cfg.DOM_TABLE_SCALE)
    style_table(table, display_summary)

    ax.set_title(
        cfg.DOM_TABLE_TITLE,
        pad=cfg.TABLE_TITLE_PAD,
        fontsize=cfg.TABLE_TITLE_FONT_SIZE,
        weight=cfg.TABLE_TITLE_FONT_WEIGHT,
    )
    fig.tight_layout()
    save_table_figure(fig, output_path)
    plt.close(fig)


def format_table_values(summary: pd.DataFrame) -> list[list[str]]:
    formatted = summary.copy()

    for column in cfg.PERFORMANCE_TABLE_NUMBER_COLUMNS:
        formatted[column] = formatted[column].map(
            lambda value: cfg.TABLE_NUMBER_FORMAT.format(value=value)
        )

    return formatted.astype(str).values.tolist()


def style_table(table, summary: pd.DataFrame) -> None:
    for (row, column), cell in table.get_celld().items():
        cell.set_edgecolor(cfg.TABLE_BORDER_COLOR)
        cell.set_linewidth(cfg.TABLE_BORDER_LINEWIDTH)

        if row == 0:
            cell.set_facecolor(cfg.TABLE_HEADER_COLOR)
            cell.set_text_props(
                weight=cfg.TABLE_TITLE_FONT_WEIGHT,
                color=cfg.TABLE_HEADER_TEXT_COLOR,
            )
            continue

        framework = summary.iloc[row - 1]["Framework"]
        base_color = (
            cfg.TABLE_EVEN_ROW_COLOR if row % 2 == 0 else cfg.TABLE_ODD_ROW_COLOR
        )
        cell.set_facecolor(base_color)
        cell.set_text_props(color=cfg.TABLE_BODY_TEXT_COLOR)

        if column == 0 and framework in cfg.FRAMEWORK_PALETTE:
            cell.set_facecolor(cfg.FRAMEWORK_PALETTE[framework])
            cell.set_text_props(
                weight=cfg.TABLE_TITLE_FONT_WEIGHT,
                color=cfg.TABLE_FRAMEWORK_TEXT_COLOR,
            )


def save_table_figure(figure, output_path: Path) -> None:
    figure.savefig(
        output_path,
        dpi=cfg.PLOT_DPI,
        bbox_inches=cfg.PLOT_BBOX_INCHES,
    )


def sort_summary(summary: pd.DataFrame) -> pd.DataFrame:
    summary = summary.copy()
    summary["framework"] = pd.Categorical(
        summary["framework"],
        categories=cfg.FRAMEWORK_ORDER,
        ordered=True,
    )
    summary["browser"] = pd.Categorical(
        summary["browser"],
        categories=cfg.BROWSER_ORDER,
        ordered=True,
    )
    summary["action"] = pd.Categorical(
        summary["action"],
        categories=[*cfg.ACTION_ORDER, *cfg.INITIAL_LOAD_ORDER],
        ordered=True,
    )
    summary["board"] = pd.Categorical(
        summary["board"],
        categories=[*cfg.BOARD_ORDER, cfg.INITIAL_LOAD_BOARD_LABEL],
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
        categories=cfg.FRAMEWORK_ORDER,
        ordered=True,
    )
    summary["action"] = pd.Categorical(
        summary["action"],
        categories=cfg.ACTION_ORDER,
        ordered=True,
    )
    summary["board"] = pd.Categorical(
        summary["board"],
        categories=cfg.BOARD_ORDER,
        ordered=True,
    )

    summary = summary.sort_values(["action", "board", "framework"])

    for column in ["framework", "action", "board"]:
        summary[column] = summary[column].astype(str)

    return summary
