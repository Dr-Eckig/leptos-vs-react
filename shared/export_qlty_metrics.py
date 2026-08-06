#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path


ANSI_ESCAPE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
TABLE_COLUMNS = (
    "function_name",
    "fields",
    "cyclomatic_complexity",
    "cognitive_complexity",
    "lines",
    "nloc",
)
INTEGER_COLUMNS = set(TABLE_COLUMNS[1:])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export Qlty's function-level metrics as JSON.",
    )
    parser.add_argument("--framework", required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source = args.source.resolve()
    repo_root = Path(__file__).resolve().parent.parent
    source_argument = relative_or_absolute(source, repo_root)
    environment = os.environ.copy()
    environment["QLTY_TELEMETRY"] = "off"

    result = subprocess.run(
        [
            "qlty",
            "metrics",
            "--quiet",
            "--no-upgrade-check",
            "--functions",
            source_argument,
        ],
        cwd=repo_root,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )
    functions = parse_qlty_metrics(result.stdout)
    if not functions:
        raise ValueError(f"Qlty returned no function metrics for {source_argument}")

    report = {
        "framework": args.framework,
        "tool": "qlty",
        "source": source_argument,
        "functions": functions,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0


def parse_qlty_metrics(output: str) -> list[dict[str, int | str]]:
    functions: list[dict[str, int | str]] = []
    current_file: str | None = None

    for line_number, raw_line in enumerate(output.splitlines(), start=1):
        line = ANSI_ESCAPE.sub("", raw_line).strip()
        if not line:
            continue

        if "|" not in line:
            if "+" not in line:
                current_file = line
            continue

        values = [value.strip() for value in line.split("|")]
        if values[0] == "function":
            continue
        if current_file is None or len(values) != len(TABLE_COLUMNS):
            raise ValueError(f"Unexpected Qlty output at line {line_number}: {line}")

        function = dict(zip(TABLE_COLUMNS, values, strict=True))
        for column in INTEGER_COLUMNS:
            try:
                function[column] = int(function[column])
            except ValueError as error:
                raise ValueError(
                    f"Invalid {column} in Qlty output at line {line_number}: {line}"
                ) from error
        function["file"] = current_file
        functions.append(function)

    return sorted(
        functions,
        key=lambda function: (
            str(function["file"]),
            str(function["function_name"]),
            int(function["cyclomatic_complexity"]),
            int(function["cognitive_complexity"]),
        ),
    )


def relative_or_absolute(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
