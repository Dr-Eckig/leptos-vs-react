from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import ticker as mticker
import numpy as np
import pandas as pd

import config as cfg
from data import (
    collapse_equal_dom_mutation_boards,
    ordered_values,
    scenario_order,
)

import seaborn as sns


def configure_plot_theme() -> None:
    sns.set_theme(
        style=cfg.PLOT_THEME_STYLE,
        context=cfg.PLOT_THEME_CONTEXT,
        rc=cfg.PLOT_THEME_RC,
    )


def create_normality_histograms(
    measurements: pd.DataFrame,
    normality_results: pd.DataFrame,
) -> list[Path]:
    """Create one normality overview per browser/action combination."""
    performance = measurements.dropna(subset=["performance_ms"]).copy()
    output_paths: list[Path] = []
    action_order = [*cfg.ACTION_ORDER, *cfg.INITIAL_LOAD_ORDER]

    for browser in ordered_values(performance["browser"], cfg.BROWSER_ORDER):
        browser_measurements = performance[performance["browser"] == browser]
        for action in ordered_values(browser_measurements["action"], action_order):
            action_measurements = browser_measurements[
                browser_measurements["action"] == action
            ]
            output_path = create_normality_histogram(
                action_measurements,
                normality_results,
                browser,
                action,
            )
            if output_path is not None:
                output_paths.append(output_path)

    return output_paths


def create_normality_histogram(
    measurements: pd.DataFrame,
    normality_results: pd.DataFrame,
    browser: str,
    action: str,
) -> Path | None:
    if measurements.empty:
        return None

    preferred_boards = [*cfg.BOARD_ORDER, cfg.INITIAL_LOAD_BOARD_LABEL]
    boards = ordered_values(measurements["board"], preferred_boards)
    frameworks = ordered_values(measurements["framework"], cfg.FRAMEWORK_ORDER)
    height = max(
        cfg.NORMALITY_HISTOGRAM_MIN_HEIGHT,
        len(boards) * cfg.NORMALITY_HISTOGRAM_HEIGHT_PER_BOARD,
    )
    fig, axes = plt.subplots(
        len(boards),
        len(frameworks),
        figsize=(cfg.NORMALITY_HISTOGRAM_WIDTH, height),
        squeeze=False,
    )

    for row_index, board in enumerate(boards):
        board_label = cfg.BOARD_LABELS.get(board, board)
        for column_index, framework in enumerate(frameworks):
            ax = axes[row_index, column_index]
            sample = measurements[
                (measurements["board"] == board)
                & (measurements["framework"] == framework)
            ]["performance_ms"].to_numpy(dtype=float)

            if len(sample) == 0:
                ax.set_visible(False)
                continue

            color = cfg.FRAMEWORK_PALETTE.get(framework, "#64748b")
            sns.histplot(
                sample,
                bins=cfg.NORMALITY_HISTOGRAM_BINS,
                stat="density",
                color=color,
                alpha=cfg.NORMALITY_HISTOGRAM_BAR_ALPHA,
                edgecolor=cfg.NORMALITY_HISTOGRAM_BAR_EDGE_COLOR,
                ax=ax,
                label="Histogramm",
            )
            add_fitted_normal_curve(ax, sample)

            mean = float(np.mean(sample))
            median = float(np.median(sample))
            ax.axvline(
                mean,
                color=cfg.NORMALITY_HISTOGRAM_MEAN_COLOR,
                linestyle="--",
                linewidth=1.3,
                label="Mittelwert",
            )
            ax.axvline(
                median,
                color=cfg.NORMALITY_HISTOGRAM_MEDIAN_COLOR,
                linestyle=":",
                linewidth=1.6,
                label="Median",
            )
            add_normality_assessment(
                ax,
                normality_results,
                browser,
                action,
                board,
                framework,
                len(sample),
            )

            ax.set_title(framework)
            ax.set_xlabel(cfg.NORMALITY_HISTOGRAM_X_LABEL)
            ax.set_ylabel(
                f"{board_label}\n{cfg.NORMALITY_HISTOGRAM_Y_LABEL}"
                if column_index == 0
                else cfg.NORMALITY_HISTOGRAM_Y_LABEL
            )
            configure_histogram_millisecond_axis(ax)
            configure_value_grid(ax, "y")
            ax.grid(axis="x", visible=False)
            sns.despine(ax=ax)

    browser_label = cfg.BROWSER_LABELS.get(browser, browser.title())
    action_label = cfg.ACTION_LABELS.get(
        action,
        cfg.INITIAL_LOAD_LABELS.get(action, action),
    )
    fig.suptitle(
        cfg.NORMALITY_HISTOGRAM_TITLE.format(
            action=action_label,
            browser=browser_label,
        ),
        y=0.995,
    )
    handles, labels = axes[0, 0].get_legend_handles_labels()
    if handles:
        fig.legend(
            handles,
            labels,
            loc="lower center",
            bbox_to_anchor=(0.5, 0.045),
            ncol=len(handles),
            frameon=cfg.PLOT_LEGEND_FRAME,
        )
    fig.text(
        0.5,
        0.012,
        cfg.NORMALITY_HISTOGRAM_FOOTNOTE,
        ha="center",
        fontsize=9,
    )
    bottom_margin = min(0.24, 1.0 / height)
    fig.tight_layout(rect=(0, bottom_margin, 1, 0.97))

    output_path = cfg.NORMALITY_HISTOGRAM_RESULTS_DIR / browser / (
        cfg.NORMALITY_HISTOGRAM_FILENAME.format(action=action, browser=browser)
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_figure(fig, output_path)
    plt.close(fig)
    return output_path


def add_fitted_normal_curve(ax, sample: np.ndarray) -> None:
    standard_deviation = float(np.std(sample, ddof=1))
    if not np.isfinite(standard_deviation) or standard_deviation <= 0:
        return

    lower = float(np.min(sample))
    upper = float(np.max(sample))
    x_values = np.linspace(lower, upper, 300)
    mean = float(np.mean(sample))
    y_values = (
        np.exp(-0.5 * ((x_values - mean) / standard_deviation) ** 2)
        / (standard_deviation * np.sqrt(2 * np.pi))
    )
    ax.plot(
        x_values,
        y_values,
        color=cfg.NORMALITY_HISTOGRAM_NORMAL_COLOR,
        linewidth=1.8,
        label="Angepasste Normalverteilung",
    )


def add_normality_assessment(
    ax,
    normality_results: pd.DataFrame,
    browser: str,
    action: str,
    board: str,
    framework: str,
    sample_size: int,
) -> None:
    result = normality_results[
        (normality_results["browser"] == browser)
        & (normality_results["action"] == action)
        & (normality_results["board"] == board)
        & (normality_results["framework"] == framework)
    ]
    if result.empty:
        assessment = f"n = {sample_size}\nShapiro-Wilk: nicht verfügbar"
        face_color = "#f1f5f9"
    else:
        row = result.iloc[0]
        rejected = bool(row["normality_rejected"])
        decision = "Normalverteilung verworfen" if rejected else "Nicht verworfen"
        p_value = format_probability_expression(float(row["p_value_holm"]))
        assessment = f"n = {sample_size}\np$_{{Holm}}$ {p_value}\n{decision}"
        face_color = "#fee2e2" if rejected else "#dcfce7"

    ax.text(
        0.98,
        0.96,
        assessment,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=8.5,
        bbox={
            "boxstyle": "round,pad=0.35",
            "facecolor": face_color,
            "edgecolor": "#94a3b8",
            "alpha": 0.92,
        },
    )


def format_probability_expression(value: float) -> str:
    if value < 0.001:
        return "< 0,001"
    return f"= {value:.3f}".replace(".", ",")


def create_complexity_frequency_plot(
    measurements: pd.DataFrame,
) -> Path | None:
    if measurements.empty:
        return None

    frameworks = ordered_values(
        measurements["framework"],
        cfg.FRAMEWORK_ORDER,
    )
    complexity_order = list(
        range(
            int(measurements["cyclomatic_complexity"].min()),
            int(measurements["cyclomatic_complexity"].max()) + 1,
        )
    )
    frequency_index = pd.MultiIndex.from_product(
        [frameworks, complexity_order],
        names=["framework", "cyclomatic_complexity"],
    )
    frequency = (
        measurements.groupby(
            ["framework", "cyclomatic_complexity"],
            observed=True,
        )
        .size()
        .rename("function_count")
        .reindex(frequency_index, fill_value=0)
        .reset_index()
    )
    frequency["percentage"] = frequency.groupby("framework")[
        "function_count"
    ].transform(lambda counts: counts / counts.sum() * 100)
    fig, ax = plt.subplots(figsize=cfg.COMPLEXITY_DISTRIBUTION_FIGURE_SIZE)
    sns.barplot(
        data=frequency,
        x="cyclomatic_complexity",
        y="percentage",
        hue="framework",
        order=complexity_order,
        hue_order=cfg.FRAMEWORK_ORDER,
        palette=cfg.FRAMEWORK_PALETTE,
        width=cfg.COMPLEXITY_DISTRIBUTION_BAR_WIDTH,
        errorbar=None,
        ax=ax,
    )

    ax.set_title(cfg.COMPLEXITY_DISTRIBUTION_TITLE, pad=cfg.PLOT_TITLE_PAD)
    ax.set_xlabel(cfg.COMPLEXITY_DISTRIBUTION_X_LABEL)
    ax.set_ylabel(cfg.COMPLEXITY_DISTRIBUTION_Y_LABEL)
    ax.set_ylim(bottom=0)
    configure_value_grid(ax, "y")
    ax.grid(axis="x", visible=False)
    ax.legend(
        title=cfg.PLOT_LEGEND_TITLE,
        frameon=cfg.PLOT_LEGEND_FRAME,
    )
    sns.despine(left=False, bottom=cfg.PLOT_DESPINE_BOTTOM)
    fig.tight_layout()

    output_path = (
        cfg.IMPLEMENTATION_RESULTS_DIR
        / cfg.COMPLEXITY_DISTRIBUTION_FILENAME
    )
    save_figure(fig, output_path)
    plt.close(fig)
    return output_path


def create_browser_boxplot(measurements: pd.DataFrame, browser: str) -> Path:
    browser_measurements = measurements[measurements["browser"] == browser]
    scenario_labels = ordered_values(
        browser_measurements["scenario"],
        scenario_order(),
    )

    height = max(
        cfg.SCENARIO_PLOT_MIN_HEIGHT,
        len(scenario_labels) * cfg.SCENARIO_PLOT_HEIGHT_PER_ROW,
    )
    grid = sns.catplot(
        data=browser_measurements,
        kind="box",
        x="performance_ms",
        y="scenario",
        hue="framework",
        order=scenario_labels,
        hue_order=cfg.FRAMEWORK_ORDER,
        palette=cfg.FRAMEWORK_PALETTE,
        dodge=cfg.BOXPLOT_DODGE,
        fliersize=cfg.BOXPLOT_FLIER_SIZE,
        linewidth=cfg.BOXPLOT_LINEWIDTH,
        height=height,
        aspect=cfg.SCENARIO_PLOT_WIDTH / height,
    )
    ax = grid.ax

    browser_label = cfg.BROWSER_LABELS.get(browser, browser.title())
    ax.set_title(
        cfg.PERFORMANCE_PLOT_TITLE.format(browser=browser_label),
        pad=cfg.PLOT_TITLE_PAD,
    )
    ax.set_xlabel(cfg.PERFORMANCE_PLOT_X_LABEL)
    ax.set_ylabel(cfg.PERFORMANCE_PLOT_Y_LABEL)
    ax.set_xscale(cfg.PLOT_VALUE_SCALE)
    configure_millisecond_axis(ax)
    add_alternating_row_background(ax, len(scenario_labels))
    configure_value_grid(ax, "x", which="both")
    ax.grid(axis="y", visible=False)
    sns.move_legend(
        grid,
        cfg.SCENARIO_LEGEND_LOCATION,
        title=cfg.PLOT_LEGEND_TITLE,
        bbox_to_anchor=cfg.SCENARIO_LEGEND_ANCHOR,
        frameon=cfg.PLOT_LEGEND_FRAME,
    )

    sns.despine(
        left=cfg.PLOT_DESPINE_LEFT,
        bottom=cfg.PLOT_DESPINE_BOTTOM,
    )
    grid.figure.tight_layout()

    output_path = cfg.PERFORMANCE_RESULTS_DIR / cfg.PERFORMANCE_PLOT_FILENAME.format(
        browser=browser,
    )
    save_figure(grid.figure, output_path)
    close_grid(grid)

    return output_path


def create_minimized_boxplot(
    measurements: pd.DataFrame,
    group_slug: str,
    actions: tuple[str, ...],
    group_label: str,
    browser: str,
) -> Path | None:
    group_measurements = measurements[
        measurements["action"].isin(actions)
        & (measurements["browser"] == browser)
    ].copy()

    if group_measurements.empty:
        return None

    scenario_labels = ordered_values(
        group_measurements["scenario"],
        scenario_order(),
    )
    height = max(
        cfg.MINIMIZED_PLOT_MIN_HEIGHT,
        len(scenario_labels) * cfg.MINIMIZED_PLOT_HEIGHT_PER_ROW,
    )
    grid = sns.catplot(
        data=group_measurements,
        kind="box",
        x="performance_ms",
        y="scenario",
        hue="framework",
        order=scenario_labels,
        hue_order=cfg.FRAMEWORK_ORDER,
        palette=cfg.FRAMEWORK_PALETTE,
        dodge=cfg.BOXPLOT_DODGE,
        fliersize=cfg.BOXPLOT_FLIER_SIZE,
        linewidth=cfg.BOXPLOT_LINEWIDTH,
        height=height,
        aspect=cfg.MINIMIZED_PLOT_WIDTH / height,
    )
    ax = grid.ax
    browser_label = cfg.BROWSER_LABELS.get(browser, browser.title())
    ax.set_title(
        cfg.MINIMIZED_PLOT_TITLE.format(
            group=group_label,
            browser=browser_label,
        ),
        pad=cfg.PLOT_TITLE_PAD,
    )
    ax.set_xlabel(cfg.MINIMIZED_PLOT_X_LABEL)
    ax.set_ylabel(cfg.MINIMIZED_PLOT_Y_LABEL)
    ax.set_xscale(cfg.PLOT_VALUE_SCALE)
    configure_millisecond_axis(ax, cfg.MINIMIZED_MILLISECOND_TICKS)
    add_alternating_row_background(ax, len(scenario_labels))
    configure_value_grid(ax, "x", which="both")
    ax.grid(axis="y", visible=False)

    sns.move_legend(
        grid,
        cfg.MINIMIZED_PLOT_LEGEND_LOCATION,
        title=cfg.PLOT_LEGEND_TITLE,
        bbox_to_anchor=cfg.MINIMIZED_PLOT_LEGEND_ANCHOR,
        frameon=cfg.PLOT_LEGEND_FRAME,
    )
    sns.despine(
        left=cfg.PLOT_DESPINE_LEFT,
        bottom=cfg.PLOT_DESPINE_BOTTOM,
    )
    grid.figure.tight_layout()

    output_path = cfg.MINIMIZED_PERFORMANCE_RESULTS_DIR / (
        cfg.MINIMIZED_PLOT_FILENAME.format(group=group_slug, browser=browser)
    )
    save_figure(grid.figure, output_path)
    close_grid(grid)

    return output_path


def create_board_boxplot(
    measurements: pd.DataFrame,
    board: str,
    board_slug: str,
    browser: str,
) -> Path | None:
    board_measurements = measurements[
        (measurements["board"] == board)
        & (measurements["browser"] == browser)
    ].copy()

    if board_measurements.empty:
        return None

    action_order = [
        action
        for action in cfg.ACTION_ORDER
        if action in set(board_measurements["action"])
    ]
    board_measurements["action_label"] = board_measurements["action"].map(
        cfg.ACTION_LABELS,
    )
    action_labels = [cfg.ACTION_LABELS[action] for action in action_order]
    height = max(
        cfg.BOARD_PLOT_MIN_HEIGHT,
        len(action_labels) * cfg.BOARD_PLOT_HEIGHT_PER_ACTION,
    )
    grid = sns.catplot(
        data=board_measurements,
        kind="box",
        x="performance_ms",
        y="action_label",
        hue="framework",
        order=action_labels,
        hue_order=cfg.FRAMEWORK_ORDER,
        palette=cfg.FRAMEWORK_PALETTE,
        dodge=cfg.BOXPLOT_DODGE,
        fliersize=cfg.BOXPLOT_FLIER_SIZE,
        linewidth=cfg.BOXPLOT_LINEWIDTH,
        height=height,
        aspect=cfg.BOARD_PLOT_WIDTH / height,
    )
    ax = grid.ax
    board_label = cfg.BOARD_LABELS.get(board, board)
    browser_label = cfg.BROWSER_LABELS.get(browser, browser.title())
    ax.set_title(
        cfg.BOARD_PLOT_TITLE.format(
            board=board_label,
            browser=browser_label,
        ),
        pad=cfg.PLOT_TITLE_PAD,
    )
    ax.set_xlabel(cfg.BOARD_PLOT_X_LABEL)
    ax.set_ylabel(cfg.BOARD_PLOT_Y_LABEL)
    ax.set_xscale(cfg.PLOT_VALUE_SCALE)
    configure_millisecond_axis(ax)
    add_alternating_row_background(ax, len(action_labels))
    configure_value_grid(ax, "x", which="both")
    ax.grid(axis="y", visible=False)
    sns.move_legend(
        grid,
        cfg.MINIMIZED_PLOT_LEGEND_LOCATION,
        title=cfg.PLOT_LEGEND_TITLE,
        bbox_to_anchor=cfg.MINIMIZED_PLOT_LEGEND_ANCHOR,
        frameon=cfg.PLOT_LEGEND_FRAME,
    )
    sns.despine(
        left=cfg.PLOT_DESPINE_LEFT,
        bottom=cfg.PLOT_DESPINE_BOTTOM,
    )
    grid.figure.tight_layout()

    output_path = cfg.BOARD_PERFORMANCE_RESULTS_DIR / (
        cfg.BOARD_PLOT_FILENAME.format(
            board_slug=board_slug,
            browser=browser,
        )
    )
    save_figure(grid.figure, output_path)
    close_grid(grid)

    return output_path


def create_initial_load_boxplot(measurements: pd.DataFrame) -> Path | None:
    initial_load_measurements = prepare_initial_load_measurements(measurements)

    if initial_load_measurements.empty:
        return None

    browsers = ordered_values(
        initial_load_measurements["browser"],
        cfg.BROWSER_ORDER,
    )
    grid = sns.catplot(
        data=initial_load_measurements,
        kind="box",
        col="browser",
        col_order=browsers,
        x="performance_ms",
        y="metric",
        hue="framework",
        order=[cfg.INITIAL_LOAD_LABELS[action] for action in cfg.INITIAL_LOAD_ORDER],
        hue_order=cfg.FRAMEWORK_ORDER,
        palette=cfg.FRAMEWORK_PALETTE,
        dodge=cfg.BOXPLOT_DODGE,
        fliersize=cfg.BOXPLOT_FLIER_SIZE,
        linewidth=cfg.BOXPLOT_LINEWIDTH,
        height=cfg.INITIAL_LOAD_PLOT_HEIGHT,
        aspect=cfg.INITIAL_LOAD_PLOT_ASPECT,
        sharey=cfg.INITIAL_LOAD_SHARE_Y,
    )

    for index, (ax, browser) in enumerate(zip(grid.axes.flat, browsers)):
        browser_label = cfg.BROWSER_LABELS.get(browser, browser.title())
        ax.set_title(browser_label, pad=cfg.INITIAL_LOAD_SUBPLOT_TITLE_PAD)
        ax.set_xlabel(cfg.INITIAL_LOAD_PLOT_X_LABEL)
        ax.set_ylabel(cfg.INITIAL_LOAD_PLOT_Y_LABEL if index == 0 else "")
        ax.set_xscale(cfg.PLOT_VALUE_SCALE)
        configure_millisecond_axis(ax)
        add_alternating_row_background(ax, len(cfg.INITIAL_LOAD_ORDER))
        configure_value_grid(ax, "x", which="both")
        ax.grid(axis="y", visible=False)

    sns.move_legend(
        grid,
        cfg.INITIAL_LOAD_LEGEND_LOCATION,
        title=cfg.PLOT_LEGEND_TITLE,
        bbox_to_anchor=cfg.INITIAL_LOAD_LEGEND_ANCHOR,
        frameon=cfg.PLOT_LEGEND_FRAME,
    )

    grid.figure.suptitle(
        cfg.INITIAL_LOAD_PLOT_TITLE,
        y=cfg.INITIAL_LOAD_PLOT_TITLE_Y,
    )
    sns.despine(
        left=cfg.PLOT_DESPINE_LEFT,
        bottom=cfg.PLOT_DESPINE_BOTTOM,
    )
    grid.figure.tight_layout(rect=cfg.INITIAL_LOAD_LAYOUT_RECT)

    output_path = cfg.PERFORMANCE_RESULTS_DIR / cfg.INITIAL_LOAD_PLOT_FILENAME
    save_figure(grid.figure, output_path)
    close_grid(grid)

    return output_path


def create_initial_load_browser_boxplot(
    measurements: pd.DataFrame,
    browser: str,
) -> Path | None:
    browser_measurements = prepare_initial_load_measurements(measurements)
    browser_measurements = browser_measurements[
        browser_measurements["browser"] == browser
    ]

    if browser_measurements.empty:
        return None

    metric_order = [
        cfg.INITIAL_LOAD_LABELS[action] for action in cfg.INITIAL_LOAD_ORDER
    ]
    grid = sns.catplot(
        data=browser_measurements,
        kind="box",
        x="performance_ms",
        y="metric",
        hue="framework",
        order=metric_order,
        hue_order=cfg.FRAMEWORK_ORDER,
        palette=cfg.FRAMEWORK_PALETTE,
        dodge=cfg.BOXPLOT_DODGE,
        fliersize=cfg.BOXPLOT_FLIER_SIZE,
        linewidth=cfg.BOXPLOT_LINEWIDTH,
        height=cfg.INITIAL_LOAD_BROWSER_PLOT_HEIGHT,
        aspect=(
            cfg.INITIAL_LOAD_BROWSER_PLOT_WIDTH
            / cfg.INITIAL_LOAD_BROWSER_PLOT_HEIGHT
        ),
    )
    ax = grid.ax
    browser_label = cfg.BROWSER_LABELS.get(browser, browser.title())
    ax.set_title(
        cfg.INITIAL_LOAD_BROWSER_PLOT_TITLE.format(browser=browser_label),
        pad=cfg.PLOT_TITLE_PAD,
    )
    ax.set_xlabel(cfg.INITIAL_LOAD_PLOT_X_LABEL)
    ax.set_ylabel(cfg.INITIAL_LOAD_PLOT_Y_LABEL)
    configure_linear_millisecond_axis(ax)
    add_alternating_row_background(ax, len(metric_order))
    configure_value_grid(ax, "x", which="both")
    ax.grid(axis="y", visible=False)
    sns.move_legend(
        grid,
        cfg.INITIAL_LOAD_BROWSER_LEGEND_LOCATION,
        title=cfg.PLOT_LEGEND_TITLE,
        bbox_to_anchor=cfg.INITIAL_LOAD_BROWSER_LEGEND_ANCHOR,
        frameon=cfg.PLOT_LEGEND_FRAME,
    )
    sns.despine(
        left=cfg.PLOT_DESPINE_LEFT,
        bottom=cfg.PLOT_DESPINE_BOTTOM,
    )
    grid.figure.tight_layout()

    output_path = cfg.BOARD_PERFORMANCE_RESULTS_DIR / (
        cfg.INITIAL_LOAD_BROWSER_PLOT_FILENAME.format(browser=browser)
    )
    save_figure(grid.figure, output_path)
    close_grid(grid)
    return output_path


def prepare_initial_load_measurements(measurements: pd.DataFrame) -> pd.DataFrame:
    prepared = measurements[
        measurements["action"].isin(cfg.INITIAL_LOAD_ORDER)
    ].copy()
    prepared["metric"] = prepared["action"].map(cfg.INITIAL_LOAD_LABELS)
    prepared["metric"] = pd.Categorical(
        prepared["metric"],
        categories=[
            cfg.INITIAL_LOAD_LABELS[action] for action in cfg.INITIAL_LOAD_ORDER
        ],
        ordered=True,
    )
    return prepared


def create_bundle_size_barplot(measurements: pd.DataFrame) -> Path | None:
    if measurements.empty:
        return None

    summary = (
        measurements.groupby("framework", observed=True)[
            [column for column, _label, _color in cfg.BUNDLE_SIZE_PARTS]
            + ["bundle_size_kib"]
        ]
        .mean()
        .reindex(cfg.FRAMEWORK_ORDER)
        .dropna(how="all")
    )
    frameworks = list(summary.index)
    fig, ax = plt.subplots(figsize=cfg.BUNDLE_SIZE_FIGURE_SIZE)
    bottoms = pd.Series(0.0, index=summary.index)

    for column, label, color in cfg.BUNDLE_SIZE_PARTS:
        values = summary[column].fillna(0)
        if values.max() <= 0:
            continue
        ax.bar(
            frameworks,
            values,
            bottom=bottoms,
            label=label,
            color=color,
            edgecolor=cfg.BUNDLE_SIZE_BAR_EDGE_COLOR,
            linewidth=cfg.BUNDLE_SIZE_BAR_LINEWIDTH,
        )
        bottoms += values

    for index, framework in enumerate(frameworks):
        total = summary.loc[framework, "bundle_size_kib"]
        ax.text(
            index,
            total,
            cfg.BUNDLE_SIZE_TOTAL_FORMAT.format(value=total),
            ha=cfg.BUNDLE_SIZE_TOTAL_HORIZONTAL_ALIGNMENT,
            va=cfg.BUNDLE_SIZE_TOTAL_VERTICAL_ALIGNMENT,
            fontsize=cfg.BUNDLE_SIZE_TOTAL_FONT_SIZE,
            fontweight=cfg.BUNDLE_SIZE_TOTAL_FONT_WEIGHT,
        )

    ax.set_title(cfg.BUNDLE_SIZE_PLOT_TITLE, pad=cfg.PLOT_TITLE_PAD)
    ax.set_xlabel(cfg.BUNDLE_SIZE_PLOT_X_LABEL)
    ax.set_ylabel(cfg.BUNDLE_SIZE_PLOT_Y_LABEL)
    ax.set_ylim(
        0,
        max(1, summary["bundle_size_kib"].max()) * cfg.PLOT_VALUE_LIMIT_FACTOR,
    )
    configure_value_grid(ax, "y")
    ax.grid(axis="x", visible=False)
    ax.legend(
        title=cfg.BUNDLE_SIZE_LEGEND_TITLE,
        frameon=cfg.PLOT_LEGEND_FRAME,
    )
    sns.despine(left=False, bottom=cfg.PLOT_DESPINE_BOTTOM)
    fig.tight_layout()

    output_path = cfg.PERFORMANCE_RESULTS_DIR / cfg.BUNDLE_SIZE_PLOT_FILENAME
    save_figure(fig, output_path)
    plt.close(fig)

    return output_path


def create_dom_mutation_barplot(measurements: pd.DataFrame) -> Path | None:
    return _create_dom_mutation_barplot(
        measurements,
        cfg.DOM_MUTATION_PLOT_TITLE,
        cfg.DOM_MUTATION_PLOT_FILENAME,
    )


def create_dom_mutation_task_management_barplot(
    measurements: pd.DataFrame,
) -> Path | None:
    task_management_measurements = measurements[
        measurements["action"].isin(
            cfg.DOM_MUTATION_TASK_MANAGEMENT_ACTIONS,
        )
    ]

    return _create_dom_mutation_barplot(
        task_management_measurements,
        cfg.DOM_MUTATION_TASK_MANAGEMENT_PLOT_TITLE,
        cfg.DOM_MUTATION_TASK_MANAGEMENT_PLOT_FILENAME,
    )


def create_dom_mutation_board_switch_barplot(
    measurements: pd.DataFrame,
) -> Path | None:
    board_switch_measurements = measurements[
        measurements["action"] == cfg.DOM_MUTATION_BOARD_SWITCH_ACTION
    ]

    return _create_dom_mutation_barplot(
        board_switch_measurements,
        cfg.DOM_MUTATION_BOARD_SWITCH_PLOT_TITLE,
        cfg.DOM_MUTATION_BOARD_SWITCH_PLOT_FILENAME,
    )


def _create_dom_mutation_barplot(
    measurements: pd.DataFrame,
    title: str,
    filename: str,
) -> Path | None:
    if measurements.empty:
        return None

    measurements = prepare_dom_mutation_plot_data(measurements)
    scenario_labels = list(dict.fromkeys(measurements["scenario_display"]))

    height = max(
        cfg.SCENARIO_PLOT_MIN_HEIGHT,
        len(scenario_labels) * cfg.SCENARIO_PLOT_HEIGHT_PER_ROW,
    )
    grid = sns.catplot(
        data=measurements,
        kind="bar",
        x="domMutations",
        y="scenario_display",
        hue="framework",
        order=scenario_labels,
        hue_order=cfg.FRAMEWORK_ORDER,
        palette=cfg.FRAMEWORK_PALETTE,
        errorbar=None,
        height=height,
        aspect=cfg.SCENARIO_PLOT_WIDTH / height,
    )
    ax = grid.ax

    annotate_bars(ax)
    ax.set_title(title, pad=cfg.PLOT_TITLE_PAD)
    ax.set_xlabel(cfg.DOM_MUTATION_PLOT_X_LABEL)
    ax.set_ylabel(cfg.DOM_MUTATION_PLOT_Y_LABEL)
    ax.set_xlim(
        0,
        max(1, measurements["domMutations"].max())
        * cfg.PLOT_VALUE_LIMIT_FACTOR,
    )
    add_alternating_row_background(ax, len(scenario_labels))
    configure_value_grid(ax, "x")
    ax.grid(axis="y", visible=False)
    sns.move_legend(
        grid,
        cfg.SCENARIO_LEGEND_LOCATION,
        title=cfg.PLOT_LEGEND_TITLE,
        bbox_to_anchor=cfg.SCENARIO_LEGEND_ANCHOR,
        frameon=cfg.PLOT_LEGEND_FRAME,
    )

    sns.despine(
        left=cfg.PLOT_DESPINE_LEFT,
        bottom=cfg.PLOT_DESPINE_BOTTOM,
    )
    grid.figure.tight_layout()

    output_path = cfg.REACTIVITY_RESULTS_DIR / filename
    save_figure(grid.figure, output_path)
    close_grid(grid)

    return output_path


def prepare_dom_mutation_plot_data(measurements: pd.DataFrame) -> pd.DataFrame:
    prepared = collapse_equal_dom_mutation_boards(measurements)
    prepared["scenario_display"] = prepared.apply(
        lambda row: (
            cfg.SCENARIO_ACTION_LABELS.get(row["action"], row["action"])
            if row["boards_collapsed"]
            else str(row["scenario"])
        ),
        axis=1,
    )

    return prepared


def close_grid(grid) -> None:
    manager = getattr(grid.figure.canvas, "manager", None)
    if manager is not None:
        manager.destroy()


def annotate_bars(ax, decimal_places: int = 0) -> None:
    value_format = f"%.{decimal_places}f"

    for container in ax.containers:
        ax.bar_label(
            container,
            fmt=value_format,
            padding=cfg.BAR_LABEL_PADDING,
            fontsize=cfg.BAR_LABEL_FONT_SIZE,
        )


def add_alternating_row_background(ax, row_count: int) -> None:
    for row_index in range(0, row_count, 2):
        ax.axhspan(
            row_index - 0.5,
            row_index + 0.5,
            color=cfg.PLOT_ROW_BAND_COLOR,
            alpha=cfg.PLOT_ROW_BAND_ALPHA,
            zorder=0,
        )


def configure_value_grid(ax, axis: str, **kwargs) -> None:
    ax.grid(
        axis=axis,
        linestyle=cfg.PLOT_GRID_LINESTYLE,
        linewidth=cfg.PLOT_GRID_LINEWIDTH,
        alpha=cfg.PLOT_GRID_ALPHA,
        **kwargs,
    )


def save_figure(figure, output_path: Path) -> None:
    figure.savefig(
        output_path,
        dpi=cfg.PLOT_DPI,
        bbox_inches=cfg.PLOT_BBOX_INCHES,
    )


def configure_millisecond_axis(
    ax,
    configured_ticks: list[float] = cfg.MILLISECOND_TICKS,
) -> None:
    lower, upper = ax.get_xlim()
    ticks = [
        tick
        for tick in configured_ticks
        if lower <= tick <= upper
    ]

    ax.set_xticks(ticks)
    ax.set_xticklabels([format_millisecond_tick(tick) for tick in ticks])
    ax.xaxis.set_minor_formatter(mticker.NullFormatter())
    ax.xaxis.get_offset_text().set_visible(False)


def configure_linear_millisecond_axis(ax) -> None:
    ax.xaxis.set_major_formatter(
        mticker.FuncFormatter(
            lambda value, _position: format_millisecond_tick(value),
        )
    )
    ax.xaxis.set_minor_formatter(mticker.NullFormatter())
    ax.xaxis.get_offset_text().set_visible(False)


def configure_histogram_millisecond_axis(ax) -> None:
    lower, upper = ax.get_xlim()
    span = upper - lower
    decimal_places = 2 if span < 1 else 1 if span < 10 else 0

    ax.xaxis.set_major_locator(mticker.MaxNLocator(nbins=6, min_n_ticks=4))
    ax.xaxis.set_major_formatter(
        mticker.FuncFormatter(
            lambda value, _position: (
                f"{value:.{decimal_places}f} ms".replace(".", ",")
            ),
        )
    )
    ax.xaxis.set_minor_formatter(mticker.NullFormatter())
    ax.xaxis.get_offset_text().set_visible(False)


def format_millisecond_tick(value: float) -> str:
    if value >= 1:
        return f"{value:.0f} ms"

    return f"{value:.1f} ms".replace(".", ",")
