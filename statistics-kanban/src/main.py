from config import (
    BROWSER_ORDER,
    BUNDLE_SIZE_BROWSER,
    BUNDLE_SIZE_DATA_DIR,
    DATA_DIR,
    DOM_MUTATION_DATA_DIR,
    INITIAL_LOAD_ORDER,
    PLOTS_DIR,
)
from data import (
    load_bundle_size_measurements,
    load_dom_mutation_measurements,
    load_measurements,
    ordered_values,
)
from plots import (
    configure_plot_theme,
    create_browser_boxplot,
    create_bundle_size_barplot,
    create_dom_mutation_scenario_barplots,
    create_initial_load_boxplot,
)
from tables import create_dom_mutation_summary_table, create_performance_summary_table


def main() -> None:
    measurements = load_measurements(DATA_DIR)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    configure_plot_theme()

    action_measurements = measurements[
        (measurements["metric_unit"] == "ms")
        & ~measurements["action"].isin(INITIAL_LOAD_ORDER)
    ]

    output_paths = [
        create_browser_boxplot(action_measurements, browser)
        for browser in ordered_values(action_measurements["browser"], BROWSER_ORDER)
    ]

    initial_load_plot = create_initial_load_boxplot(measurements)

    if initial_load_plot is not None:
        output_paths.append(initial_load_plot)

    bundle_size_measurements = load_bundle_size_measurements(BUNDLE_SIZE_DATA_DIR)
    bundle_size_measurements = bundle_size_measurements[
        bundle_size_measurements["browser"] == BUNDLE_SIZE_BROWSER
    ]
    bundle_size_plot = create_bundle_size_barplot(bundle_size_measurements)

    if bundle_size_plot is not None:
        output_paths.append(bundle_size_plot)

    dom_mutation_measurements = load_dom_mutation_measurements(DOM_MUTATION_DATA_DIR)
    output_paths.extend(create_dom_mutation_scenario_barplots(dom_mutation_measurements))

    table_paths = create_performance_summary_table(measurements, PLOTS_DIR)
    table_paths.extend(
        create_dom_mutation_summary_table(dom_mutation_measurements, PLOTS_DIR)
    )

    print(f"Loaded {len(measurements)} measurements from {DATA_DIR}")
    print("Created plots:")
    for output_path in output_paths:
        print(f"- {output_path}")
    print("Created tables:")
    for table_path in table_paths:
        print(f"- {table_path}")


if __name__ == "__main__":
    main()
