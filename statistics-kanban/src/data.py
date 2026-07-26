from pathlib import Path
from typing import Any

import pandas as pd

from config import (
    ACTION_LABELS,
    ACTION_ORDER,
    BOARD_LABELS,
    BOARD_ORDER,
    INITIAL_LOAD_ORDER,
)


def load_measurements(data_dir: Path) -> pd.DataFrame:
    json_files = sorted(data_dir.rglob("*.json"))

    if not json_files:
        raise FileNotFoundError(f"No JSON files found in {data_dir}")

    raw_measurements = pd.concat(
        [pd.read_json(json_file) for json_file in json_files],
        ignore_index=True,
    )
    missing_columns = required_columns() - set(raw_measurements.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required column(s): {missing}")

    if "warmUp" not in raw_measurements.columns:
        raw_measurements["warmUp"] = False

    raw_measurements = raw_measurements[
        ~raw_measurements["warmUp"].map(is_warm_up_measurement)
    ].copy()
    raw_measurements = raw_measurements[
        raw_measurements["action"].isin([*ACTION_ORDER, *INITIAL_LOAD_ORDER])
    ].copy()

    measurements = raw_measurements.copy()
    measurements["metric_unit"] = "ms"
    measurements["performance_value"] = measurements.apply(
        lambda row: parse_performance_value(row["performance"], row["metric_unit"]),
        axis=1,
    )
    measurements["performance_ms"] = measurements["performance_value"].where(
        measurements["metric_unit"] == "ms",
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


def load_dom_mutation_measurements(data_dir: Path) -> pd.DataFrame:
    json_files = sorted(data_dir.glob("*/dom-mutations.json"))

    if not json_files:
        return pd.DataFrame()

    measurements = pd.concat(
        [pd.read_json(json_file) for json_file in json_files],
        ignore_index=True,
    )
    missing_columns = required_dom_mutation_columns() - set(measurements.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required DOM mutation column(s): {missing}")

    measurements = measurements.copy()
    measurements["framework"] = measurements["framework"].str.title()
    measurements["scenario"] = measurements.apply(scenario_label, axis=1)
    measurements["scenario"] = pd.Categorical(
        measurements["scenario"],
        categories=scenario_order(),
        ordered=True,
    )

    numeric_columns = [
        "mutationRecords",
        "textChanges",
        "attributeChanges",
        "addedElements",
        "removedElements",
    ]

    for column in numeric_columns:
        measurements[column] = pd.to_numeric(measurements[column])

    measurements["domMutations"] = measurements[
        [
            "textChanges",
            "attributeChanges",
            "addedElements",
            "removedElements",
        ]
    ].sum(axis=1)

    return measurements.sort_values(["scenario", "framework"])


def collapse_equal_dom_mutation_boards(
    measurements: pd.DataFrame,
) -> pd.DataFrame:
    prepared_actions: list[pd.DataFrame] = []
    present_actions = set(measurements["action"].astype(str))
    action_order = [
        *[action for action in ACTION_ORDER if action in present_actions],
        *sorted(present_actions - set(ACTION_ORDER)),
    ]

    for action in action_order:
        action_measurements = measurements[
            measurements["action"] == action
        ].copy()
        boards_collapsed = all_boards_have_same_dom_mutation_value(
            action_measurements,
            action,
        )

        if boards_collapsed:
            action_measurements = action_measurements.drop_duplicates(
                subset=["framework"],
                keep="first",
            )

        action_measurements["boards_collapsed"] = boards_collapsed
        prepared_actions.append(action_measurements)

    if not prepared_actions:
        return measurements.assign(
            boards_collapsed=pd.Series(dtype=bool),
        )

    return pd.concat(prepared_actions, ignore_index=True)


def all_boards_have_same_dom_mutation_value(
    action_measurements: pd.DataFrame,
    action: str,
) -> bool:
    expected_boards = set(boards_for_action(action))

    if not expected_boards or action_measurements.empty:
        return False

    for _, framework_measurements in action_measurements.groupby(
        "framework",
        observed=True,
    ):
        measured_boards = set(framework_measurements["board"].astype(str))

        if (
            measured_boards != expected_boards
            or len(framework_measurements) != len(expected_boards)
            or framework_measurements["domMutations"].nunique(dropna=False) != 1
        ):
            return False

    return True


def load_bundle_size_measurements(data_dir: Path) -> pd.DataFrame:
    json_files = sorted(data_dir.rglob("bundle-size.json"))

    if not json_files:
        return pd.DataFrame()

    measurements = pd.concat(
        [pd.read_json(json_file) for json_file in json_files],
        ignore_index=True,
    )
    required = {"run", "browser", "framework", "bundleSizeBytes"}
    missing_columns = required - set(measurements.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required bundle-size column(s): {missing}")

    measurements = measurements.copy()
    measurements["browser"] = measurements["browser"].str.lower()
    measurements["framework"] = measurements["framework"].str.title()
    measurements["bundle_size_kib"] = (
        pd.to_numeric(measurements["bundleSizeBytes"]) / 1024
    )

    breakdown_columns = {
        "scriptSizeBytes": "script_size_kib",
        "stylesheetSizeBytes": "stylesheet_size_kib",
        "wasmSizeBytes": "wasm_size_kib",
    }
    for source_column, target_column in breakdown_columns.items():
        if source_column not in measurements.columns:
            measurements[source_column] = 0
        measurements[target_column] = (
            pd.to_numeric(measurements[source_column]).fillna(0) / 1024
        )

    measured_size_kib = measurements[list(breakdown_columns.values())].sum(axis=1)
    measurements["other_size_kib"] = (
        measurements["bundle_size_kib"] - measured_size_kib
    ).clip(lower=0)

    return measurements.sort_values(["browser", "framework", "run"])


def required_columns() -> set[str]:
    return {"run", "browser", "framework", "board", "action", "performance"}


def required_dom_mutation_columns() -> set[str]:
    return {
        "framework",
        "board",
        "action",
        "scenario",
        "mutationRecords",
        "textChanges",
        "attributeChanges",
        "addedElements",
        "removedElements",
    }


def is_warm_up_measurement(value: Any) -> bool:
    if pd.isna(value):
        return False

    if isinstance(value, bool):
        return value

    return str(value).strip().lower() == "true"


def parse_performance_value(value: Any, metric_unit: str) -> float:
    if isinstance(value, (int, float)):
        return float(value)

    normalized = str(value).strip()

    normalized = remove_suffix(normalized, "ms")

    normalized = normalized.strip().replace(",", ".")
    return float(normalized)


def remove_suffix(value: str, suffix: str) -> str:
    if value.lower().endswith(suffix):
        return value[: -len(suffix)]

    return value


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
    if action == "task-create":
        return BOARD_ORDER

    return BOARD_ORDER[1:]


def ordered_values(values: pd.Series, preferred_order: list[str]) -> list[str]:
    present_values = set(values.dropna().astype(str))
    ordered = [value for value in preferred_order if value in present_values]
    unexpected = sorted(present_values - set(ordered))

    return ordered + unexpected
