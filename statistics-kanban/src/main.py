from config import (
    BOARD_PERFORMANCE_RESULTS_DIR,
    BOARD_PLOT_SPECS,
    BROWSER_ORDER,
    BUNDLE_SIZE_BROWSER,
    BUNDLE_SIZE_DATA_DIR,
    DATA_DIR,
    DOM_MUTATION_DATA_DIR,
    INITIAL_LOAD_ORDER,
    IMPLEMENTATION_RESULTS_DIR,
    MINIMIZED_ACTION_GROUPS,
    MINIMIZED_PERFORMANCE_RESULTS_DIR,
    PERFORMANCE_RESULTS_DIR,
    REACTIVITY_RESULTS_DIR,
    SIGNIFICANCE_RESULTS_DIR,
)
from data import (
    load_bundle_size_measurements,
    load_complexity_measurements,
    load_dom_mutation_measurements,
    load_measurements,
    ordered_values,
)
from plots import (
    configure_plot_theme,
    create_board_boxplot,
    create_browser_boxplot,
    create_bundle_size_barplot,
    create_complexity_frequency_plot,
    create_dom_mutation_barplot,
    create_dom_mutation_task_management_barplot,
    create_initial_load_boxplot,
    create_minimized_boxplot,
)
from significance import test_performance_differences, write_significance_results
from tables import (
    create_complexity_summary_table,
    create_dom_mutation_summary_table,
    create_performance_summary_table,
)


def main() -> None:
    measurements = load_measurements(DATA_DIR)
    PERFORMANCE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    MINIMIZED_PERFORMANCE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    BOARD_PERFORMANCE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    REACTIVITY_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    IMPLEMENTATION_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    configure_plot_theme()

    complexity_measurements = load_complexity_measurements(
        IMPLEMENTATION_RESULTS_DIR,
    )
    complexity_plot = create_complexity_frequency_plot(complexity_measurements)

    action_measurements = measurements[
        (measurements["metric_unit"] == "ms")
        & ~measurements["action"].isin(INITIAL_LOAD_ORDER)
    ]

    output_paths = [
        create_browser_boxplot(action_measurements, browser)
        for browser in ordered_values(action_measurements["browser"], BROWSER_ORDER)
    ]
    if complexity_plot is not None:
        output_paths.append(complexity_plot)

    minimized_plot_paths = [
        create_minimized_boxplot(
            action_measurements,
            group_slug,
            actions,
            group_label,
            browser,
        )
        for group_slug, actions, group_label in MINIMIZED_ACTION_GROUPS
        for browser in ordered_values(
            action_measurements[action_measurements["action"].isin(actions)]["browser"],
            BROWSER_ORDER,
        )
    ]
    output_paths.extend(path for path in minimized_plot_paths if path is not None)

    board_plot_paths = [
        create_board_boxplot(
            action_measurements,
            board,
            board_slug,
            browser,
        )
        for board, board_slug in BOARD_PLOT_SPECS
        for browser in ordered_values(
            action_measurements[
                action_measurements["board"] == board
            ]["browser"],
            BROWSER_ORDER,
        )
    ]
    output_paths.extend(path for path in board_plot_paths if path is not None)

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
    dom_mutation_plot = create_dom_mutation_barplot(dom_mutation_measurements)

    if dom_mutation_plot is not None:
        output_paths.append(dom_mutation_plot)

    dom_mutation_task_management_plot = (
        create_dom_mutation_task_management_barplot(
            dom_mutation_measurements,
        )
    )

    if dom_mutation_task_management_plot is not None:
        output_paths.append(dom_mutation_task_management_plot)

    table_paths = create_performance_summary_table(
        measurements,
        PERFORMANCE_RESULTS_DIR,
    )
    significance_results = test_performance_differences(measurements)
    table_paths.extend(
        write_significance_results(significance_results, SIGNIFICANCE_RESULTS_DIR)
    )
    table_paths.extend(
        create_dom_mutation_summary_table(
            dom_mutation_measurements,
            REACTIVITY_RESULTS_DIR,
        )
    )
    complexity_table = create_complexity_summary_table(
        complexity_measurements,
        IMPLEMENTATION_RESULTS_DIR,
    )
    if complexity_table is not None:
        table_paths.append(complexity_table)

    print(f"Loaded {len(measurements)} measurements from {DATA_DIR}")
    print(
        f"Loaded {len(complexity_measurements)} complexity measurements "
        f"from {IMPLEMENTATION_RESULTS_DIR}"
    )
    print("Created plots:")
    for output_path in output_paths:
        print(f"- {output_path}")
    print("Created tables:")
    for table_path in table_paths:
        print(f"- {table_path}")


if __name__ == "__main__":
    main()
