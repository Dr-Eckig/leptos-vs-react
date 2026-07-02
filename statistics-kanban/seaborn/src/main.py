from config import (
    BROWSER_ORDER,
    DATA_DIR,
    INITIAL_LOAD_ORDER,
    PLOTS_DIR,
)
from data import load_measurements, ordered_values
from plots import (
    configure_plot_theme,
    create_browser_boxplot,
    create_initial_load_boxplot,
)


def main() -> None:
    measurements = load_measurements(DATA_DIR)
    PLOTS_DIR.mkdir(exist_ok=True)

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

    print(f"Loaded {len(measurements)} measurements from {DATA_DIR}")
    print("Created plots:")
    for output_path in output_paths:
        print(f"- {output_path}")


if __name__ == "__main__":
    main()
