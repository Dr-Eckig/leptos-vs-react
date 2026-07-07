from pathlib import Path

import pandas as pd

from config import (
    BROWSER_LABELS,
    BROWSER_ORDER,
    DOM_MUTATION_BROWSER,
    FRAMEWORK_ORDER,
    FRAMEWORK_PALETTE,
    INITIAL_LOAD_LABELS,
    INITIAL_LOAD_ORDER,
    MILLISECOND_TICKS,
    PLOTS_DIR,
)
from data import ordered_values, scenario_order

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter


def configure_plot_theme() -> None:
    sns.set_theme(style="whitegrid", context="paper")


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
    fig, axes = plt.subplots(
        1,
        len(browsers),
        figsize=(max(7, 4.8 * len(browsers)), 4.2),
        sharey=True,
    )

    if len(browsers) == 1:
        axes = [axes]

    handles = []
    labels = []

    for index, (ax, browser) in enumerate(zip(axes, browsers)):
        browser_measurements = initial_load_measurements[
            initial_load_measurements["browser"] == browser
        ]

        sns.boxplot(
            data=browser_measurements,
            x="performance_ms",
            y="metric",
            hue="framework",
            order=[INITIAL_LOAD_LABELS[action] for action in INITIAL_LOAD_ORDER],
            hue_order=FRAMEWORK_ORDER,
            palette=FRAMEWORK_PALETTE,
            dodge=True,
            fliersize=2.5,
            linewidth=1,
            ax=ax,
        )

        browser_label = BROWSER_LABELS.get(browser, browser.title())
        ax.set_title(browser_label, pad=10)
        ax.set_xlabel("Zeit in Millisekunden (logarithmische Skala)")
        ax.set_ylabel("Metrik" if index == 0 else "")
        ax.set_xscale("log")
        configure_millisecond_axis(ax)
        ax.grid(axis="x", which="both", linestyle="--", linewidth=0.5, alpha=0.55)
        ax.grid(axis="y", visible=False)

        current_handles, current_labels = remove_axis_legend(ax)

        if current_handles and not handles:
            handles = current_handles
            labels = current_labels

    place_figure_legend(fig, handles, labels)

    fig.suptitle("Initial Load: FCP und LCP nach Browser", y=1.02)
    sns.despine(left=True, bottom=False)
    fig.tight_layout(rect=(0, 0, 0.91 if handles else 1, 1))

    output_path = PLOTS_DIR / "initial-load-boxplots.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

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
    browser_measurements = measurements[
        measurements["browser"] == DOM_MUTATION_BROWSER
    ].copy()
    browser_label = BROWSER_LABELS.get(
        DOM_MUTATION_BROWSER,
        DOM_MUTATION_BROWSER.title(),
    )
    output_paths = []

    for scenario in scenario_labels:
        scenario_measurements = browser_measurements[
            browser_measurements["scenario"] == scenario
        ].copy()

        if scenario_measurements.empty:
            continue

        fig, ax = plt.subplots(figsize=(6.8, 4.4))
        sns.barplot(
            data=scenario_measurements,
            x="framework",
            y="rerenderedNodeEstimate",
            order=FRAMEWORK_ORDER,
            palette=FRAMEWORK_PALETTE,
            hue="framework",
            hue_order=FRAMEWORK_ORDER,
            legend=False,
            errorbar=None,
            ax=ax,
        )

        annotate_bars(ax)
        ax.set_title(f"DOM-Mutationen - {scenario}", pad=12)
        ax.set_xlabel("Framework")
        ax.set_ylabel("Mutierte DOM-Elementknoten")
        ax.set_ylim(0, max(1, scenario_measurements["rerenderedNodeEstimate"].max()) * 1.18)
        ax.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.55)
        ax.grid(axis="x", visible=False)
        ax.text(
            0.99,
            0.96,
            browser_label,
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=9,
            color="#4b5563",
        )
        sns.despine(left=False, bottom=False)
        fig.tight_layout()

        output_path = output_dir / f"{slugify(scenario)}.png"
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        output_paths.append(output_path)

    return output_paths


def annotate_bars(ax: Axes) -> None:
    for container in ax.containers:
        ax.bar_label(container, fmt="%.0f", padding=3, fontsize=9)


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


def remove_axis_legend(ax: Axes) -> tuple[list, list]:
    legend = ax.get_legend()

    if legend is None:
        return [], []

    handles, labels = ax.get_legend_handles_labels()
    legend.remove()

    return handles, labels


def place_figure_legend(fig: Figure, handles: list, labels: list) -> None:
    if not handles:
        return

    fig.legend(
        handles,
        labels,
        title="Framework",
        loc="center right",
        bbox_to_anchor=(1.0, 0.5),
        frameon=True,
    )
