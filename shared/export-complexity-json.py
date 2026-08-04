#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path


CSV_FIELDS = (
    "nloc",
    "cyclomatic_complexity",
    "token_count",
    "parameter_count",
    "length",
    "location",
    "file",
    "function_name",
    "long_name",
    "start_line",
    "end_line",
)
INTEGER_FIELDS = {
    "nloc",
    "cyclomatic_complexity",
    "token_count",
    "parameter_count",
    "length",
    "start_line",
    "end_line",
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export Lizard's function-level complexity metrics as JSON.",
    )
    parser.add_argument("--framework", required=True)
    parser.add_argument("--language", action="append", required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source = args.source.resolve()
    repo_root = Path(__file__).resolve().parent.parent
    source_argument = relative_or_absolute(source, repo_root)
    command = [sys.executable, "-m", "lizard"]
    for language in args.language:
        command.extend(("-l", language))
    command.extend((source_argument, "--csv", "-i", "-1"))

    result = subprocess.run(
        command,
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    functions = parse_lizard_csv(result.stdout)
    report = {
        "framework": args.framework,
        "languages": args.language,
        "source": source_argument,
        "functions": functions,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0


def parse_lizard_csv(csv_output: str) -> list[dict[str, int | str]]:
    functions = []
    for row_number, row in enumerate(csv.reader(csv_output.splitlines()), start=1):
        if not row:
            continue
        if len(row) != len(CSV_FIELDS):
            raise ValueError(
                f"Unexpected Lizard CSV row {row_number}: "
                f"expected {len(CSV_FIELDS)} columns, got {len(row)}"
            )

        function = dict(zip(CSV_FIELDS, row, strict=True))
        for field in INTEGER_FIELDS:
            function[field] = int(function[field])
        functions.append(function)

    return functions


def relative_or_absolute(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
