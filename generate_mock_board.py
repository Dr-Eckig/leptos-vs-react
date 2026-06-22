# Generate: python3 generate_mock_board.py
"""Generate deterministic Kanban mock boards for local development."""

from __future__ import annotations

import json
import uuid
from datetime import date, timedelta
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_FILES = (
    PROJECT_ROOT / "react-kanban" / "mock_data" / "mock_board.json",
    PROJECT_ROOT / "leptos-kanban" / "mock_data" / "mock_board.json",
)
COLUMN_TYPES = ("todo", "in_progress", "done")
PRIORITIES = ("Low", "Medium", "High")
ID_NAMESPACE = uuid.UUID("12345678-1234-5678-1234-567812345678")


def make_id(*parts: object) -> str:
    return str(uuid.uuid5(ID_NAMESPACE, ":".join(str(part) for part in parts)))


def make_task(task_number: int, board_task_count: int) -> dict[str, str | None]:
    due_date = None
    if task_number % 5 != 0:
        due_date = (date(2026, 6, 1) + timedelta(days=task_number % 90)).isoformat()

    return {
        "id": make_id("task", board_task_count, task_number),
        "title": f"Task {task_number:04d} von {board_task_count}",
        "description": f"Automatisch generierte Mock-Aufgabe {task_number} für das Board mit {board_task_count} Tasks.",
        "dueDate": due_date,
        "priority": PRIORITIES[(task_number - 1) % len(PRIORITIES)],
    }


def make_columns(task_count: int) -> list[dict[str, object]]:
    columns: list[dict[str, object]] = [
        {
            "id": make_id("column", task_count, column_type),
            "columnType": column_type,
            "tasks": [],
            "wipLimit": None,
        }
        for column_type in COLUMN_TYPES
    ]

    for task_number in range(1, task_count + 1):
        column_index = (task_number - 1) % len(columns)
        columns[column_index]["tasks"].append(make_task(task_number, task_count))

    return columns


def make_board(index: int, task_count: int) -> dict[str, object]:
    title = "Board 1 (Leer)" if task_count == 0 else f"Board {index} ({task_count} Tasks)"
    return {
        "id": make_id("board", index, task_count),
        "title": title,
        "columns": make_columns(task_count),
    }


def main() -> None:
    task_counts = (0, 10, 100, 1000)
    boards = [
        make_board(index, task_count)
        for index, task_count in enumerate(task_counts, start=1)
    ]
    data = {
        "boards": boards,
        "currentBoardId": boards[0]["id"] if boards else None,
    }

    content = json.dumps(data, indent=2, ensure_ascii=True) + "\n"

    for output_file in OUTPUT_FILES:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
