from pathlib import Path

import pandas as pd

from config import (
    BROWSER_LABELS,
    BROWSER_ORDER,
    FRAMEWORK_ORDER,
    FRAMEWORK_PALETTE,
    INITIAL_LOAD_LABELS,
    INITIAL_LOAD_ORDER,
    MILLISECOND_TICKS,
    PLOTS_DIR,
)
from data import ordered_values, scenario_order

import seaborn as sns


def configure_plot_theme() -> None:
    sns.set_theme(
        style="whitegrid",
        context="paper",
        rc={"figure.max_open_warning": 0},
    )


def create_browser_boxplot(measurements: pd.DataFrame, browser: str) -> Path:
    browser_measurements = measurements[measurements["browser"] == browser]
    scenario_labels = ordered_values(
        browser_measurements["scenario"],
        scenario_order(),
    )

    height = max(7, len(scenario_labels) * 0.48)
    grid = sns.catplot(
        data=browser_measurements,
        kind="box",
        x="performance_ms",
        y="scenario",
        hue="framework",
        order=scenario_labels,
        hue_order=FRAMEWORK_ORDER,
        palette=FRAMEWORK_PALETTE,
        dodge=True,
        fliersize=2.5,
        linewidth=1,
        height=height,
        aspect=13 / height,
    )
    ax = grid.ax

    browser_label = BROWSER_LABELS.get(browser, browser.title())
    ax.set_title(f"Kanban-Performance nach Szenario - {browser_label}", pad=12)
    ax.set_xlabel("Ausführungsdauer in Millisekunden")
    ax.set_ylabel("Szenario: Aktion und Boardgröße")
    ax.set_xscale("log")
    configure_millisecond_axis(ax)
    ax.grid(axis="x", which="both", linestyle="--", linewidth=0.5, alpha=0.55)
    ax.grid(axis="y", visible=False)
    sns.move_legend(
        grid,
        "center left",
        title="Framework",
        bbox_to_anchor=(1.01, 0.5),
        frameon=True,
    )

    sns.despine(left=True, bottom=False)
    grid.figure.tight_layout()

    output_path = PLOTS_DIR / f"performance-boxplots-{browser}.png"
    grid.figure.savefig(output_path, dpi=300, bbox_inches="tight")
    close_grid(grid)

    return output_path


def create_initial_load_boxplot(measurements: pd.DataFrame) -> Path | None:
    initial_load_measurements = measurements[
        measurements["action"].isin(INITIAL_LOAD_ORDER)
    ].copy()

    if initial_load_measurements.empty:
        return None

    initial_load_measurements["metric"] = initial_load_measurements["action"].map(
        INITIAL_LOAD_LABELS,
    )
    initial_load_measurements["metric"] = pd.Categorical(
        initial_load_measurements["metric"],
        categories=[INITIAL_LOAD_LABELS[action] for action in INITIAL_LOAD_ORDER],
        ordered=True,
    )

    browsers = ordered_values(initial_load_measurements["browser"], BROWSER_ORDER)
    grid = sns.catplot(
        data=initial_load_measurements,
        kind="box",
        col="browser",
        col_order=browsers,
        x="performance_ms",
        y="metric",
        hue="framework",
        order=[INITIAL_LOAD_LABELS[action] for action in INITIAL_LOAD_ORDER],
        hue_order=FRAMEWORK_ORDER,
        palette=FRAMEWORK_PALETTE,
        dodge=True,
        fliersize=2.5,
        linewidth=1,
        height=4.2,
        aspect=1.15,
        sharey=True,
    )

    for index, (ax, browser) in enumerate(zip(grid.axes.flat, browsers)):
        browser_label = BROWSER_LABELS.get(browser, browser.title())
        ax.set_title(browser_label, pad=10)
        ax.set_xlabel("Zeit in Millisekunden")
        ax.set_ylabel("Metrik" if index == 0 else "")
        ax.set_xscale("log")
        configure_millisecond_axis(ax)
        ax.grid(axis="x", which="both", linestyle="--", linewidth=0.5, alpha=0.55)
        ax.grid(axis="y", visible=False)

    sns.move_legend(
        grid,
        "center right",
        title="Framework",
        bbox_to_anchor=(1.0, 0.5),
        frameon=True,
    )

    grid.figure.suptitle("Initial Load: FCP und LCP nach Browser", y=1.02)
    sns.despine(left=True, bottom=False)
    grid.figure.tight_layout(rect=(0, 0, 0.91, 1))

    output_path = PLOTS_DIR / "initial-load-boxplots.png"
    grid.figure.savefig(output_path, dpi=300, bbox_inches="tight")
    close_grid(grid)

    return output_path


def create_bundle_size_barplot(measurements: pd.DataFrame) -> Path | None:
    if measurements.empty:
        return None

    grid = sns.catplot(
        data=measurements,
        kind="bar",
        x="framework",
        y="bundle_size_kib",
        order=FRAMEWORK_ORDER,
        palette=FRAMEWORK_PALETTE,
        hue="framework",
        hue_order=FRAMEWORK_ORDER,
        legend=False,
        errorbar=None,
        height=4.4,
        aspect=6.8 / 4.4,
    )
    ax = grid.ax

    annotate_bars(ax, decimal_places=2)
    ax.set_title("Bundle-Größe", pad=12)
    ax.set_xlabel("Framework")
    ax.set_ylabel("Bundle-Größe in KiB")
    ax.set_ylim(0, max(1, measurements["bundle_size_kib"].max()) * 1.18)
    ax.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.55)
    ax.grid(axis="x", visible=False)
    sns.despine(left=False, bottom=False)
    grid.figure.tight_layout()

    output_path = PLOTS_DIR / "bundle-size.png"
    grid.figure.savefig(output_path, dpi=300, bbox_inches="tight")
    close_grid(grid)

    return output_path


def create_dom_mutation_scenario_barplots(measurements: pd.DataFrame) -> list[Path]:
    if measurements.empty:
        return []

    scenario_labels = ordered_values(
        measurements["scenario"],
        scenario_order(),
    )
    output_dir = PLOTS_DIR / "dom-mutations"
    output_dir.mkdir(exist_ok=True)
    output_paths = []

    for scenario in scenario_labels:
        scenario_measurements = measurements[
            measurements["scenario"] == scenario
        ].copy()

        if scenario_measurements.empty:
            continue

        grid = sns.catplot(
            data=scenario_measurements,
            kind="bar",
            x="framework",
            y="mutationRecords",
            order=FRAMEWORK_ORDER,
            palette=FRAMEWORK_PALETTE,
            hue="framework",
            hue_order=FRAMEWORK_ORDER,
            legend=False,
            errorbar=None,
            height=4.4,
            aspect=6.8 / 4.4,
        )
        ax = grid.ax

        annotate_bars(ax)
        ax.set_title(f"DOM-Mutationen - {scenario}", pad=12)
        ax.set_xlabel("Framework")
        ax.set_ylabel("Mutation Records")
        ax.set_ylim(0, max(1, scenario_measurements["mutationRecords"].max()) * 1.18)
        ax.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.55)
        ax.grid(axis="x", visible=False)
        sns.despine(left=False, bottom=False)
        grid.figure.tight_layout()

        output_path = output_dir / f"{slugify(scenario)}.png"
        grid.figure.savefig(output_path, dpi=300, bbox_inches="tight")
        close_grid(grid)
        output_paths.append(output_path)

    return output_paths


def close_grid(grid) -> None:
    manager = getattr(grid.figure.canvas, "manager", None)
    if manager is not None:
        manager.destroy()


def annotate_bars(ax, decimal_places: int = 0) -> None:
    value_format = f"%.{decimal_places}f"

    for container in ax.containers:
        ax.bar_label(container, fmt=value_format, padding=3, fontsize=9)


def slugify(value: str) -> str:
    replacements = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "Ä": "ae",
        "Ö": "oe",
        "Ü": "ue",
        "ß": "ss",
    }
    normalized = value

    for source, target in replacements.items():
        normalized = normalized.replace(source, target)

    slug = "".join(
        character.lower() if character.isalnum() else "-"
        for character in normalized
    )

    return "-".join(part for part in slug.split("-") if part)


def configure_millisecond_axis(ax) -> None:
    lower, upper = ax.get_xlim()
    ticks = [
        tick
        for tick in MILLISECOND_TICKS
        if lower <= tick <= upper
    ]

    ax.set_xticks(ticks)
    ax.set_xticklabels([format_millisecond_tick(tick) for tick in ticks])


def format_millisecond_tick(value: float) -> str:
    if value >= 1:
        return f"{value:.0f} ms"

    return f"{value:.1f} ms".replace(".", ",")
