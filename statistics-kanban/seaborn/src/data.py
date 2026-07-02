from pathlib import Path
from typing import Any

import pandas as pd

from config import (
    ACTION_LABELS,
    ACTION_ORDER,
    BOARD_LABELS,
    BOARD_ORDER,
    INITIAL_LOAD_ORDER,
    MEMORY_ACTION_SUFFIX,
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

    if "jsHeap" not in raw_measurements.columns:
        raw_measurements["jsHeap"] = pd.NA

    if "warmUp" not in raw_measurements.columns:
        raw_measurements["warmUp"] = False

    raw_measurements = raw_measurements[
        ~raw_measurements["warmUp"].map(is_warm_up_measurement)
    ].copy()

    measurements = expand_measurements(raw_measurements)
    measurements["performance_value"] = measurements.apply(
        lambda row: parse_performance_value(row["performance"], row["metric_unit"]),
        axis=1,
    )
    measurements["performance_ms"] = measurements["performance_value"].where(
        measurements["metric_unit"] == "ms",
    )
    measurements["performance_bytes"] = measurements["performance_value"].where(
        measurements["metric_unit"] == "bytes",
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


def expand_measurements(raw_measurements: pd.DataFrame) -> pd.DataFrame:
    embedded_measurements = raw_measurements[
        ~raw_measurements["action"].map(is_memory_action)
    ].copy()
    memory_measurements = create_memory_measurements(embedded_measurements)

    if memory_measurements.empty:
        memory_measurements = raw_measurements[
            raw_measurements["action"].map(is_memory_action)
        ].copy()
        memory_measurements["metric_unit"] = "bytes"

    embedded_measurements["metric_unit"] = "ms"

    return pd.concat([embedded_measurements, memory_measurements], ignore_index=True)


def create_memory_measurements(measurements: pd.DataFrame) -> pd.DataFrame:
    memory_measurements = measurements[measurements["jsHeap"].notna()].copy()

    if memory_measurements.empty:
        return memory_measurements

    memory_measurements["action"] = memory_measurements["action"].map(
        memory_action_for,
    )
    memory_measurements["performance"] = memory_measurements["jsHeap"]
    memory_measurements["metric_unit"] = "bytes"

    return memory_measurements


def required_columns() -> set[str]:
    return {"run", "browser", "framework", "board", "action", "performance"}


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

    if metric_unit == "bytes":
        normalized = remove_suffix(normalized, "bytes")
        normalized = remove_suffix(normalized, "byte")
    else:
        normalized = remove_suffix(normalized, "ms")

    normalized = normalized.strip().replace(",", ".")
    return float(normalized)


def remove_suffix(value: str, suffix: str) -> str:
    if value.lower().endswith(suffix):
        return value[: -len(suffix)]

    return value


def is_memory_action(action: str) -> bool:
    return action.endswith(MEMORY_ACTION_SUFFIX)


def memory_action_for(action: str) -> str:
    if action in INITIAL_LOAD_ORDER:
        return "initial-load-js-heap-used"

    return f"{action}{MEMORY_ACTION_SUFFIX}"


def scenario_label(row: pd.Series) -> str:
    row_action = base_action(row["action"])
    action = ACTION_LABELS.get(row_action, str(row_action))
    board = BOARD_LABELS.get(row["board"], str(row["board"]))

    return f"{action} | {board}"


def base_action(action: str) -> str:
    if action.endswith(MEMORY_ACTION_SUFFIX):
        return action[: -len(MEMORY_ACTION_SUFFIX)]

    return action


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
