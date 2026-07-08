#!/usr/bin/env python3
# python3 scripts/decision-density.py
# python3 scripts/decision-density.py --markdown
# python3 scripts/decision-density.py --details --notes

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ProjectConfig:
    name: str
    root: Path
    extensions: tuple[str, ...]
    excluded_parts: tuple[str, ...] = ()


@dataclass
class Metrics:
    files: int = 0
    loc: int = 0
    non_empty_loc: int = 0
    comment_lines: int = 0
    components: int = 0
    functions: int = 0
    types: int = 0
    decision_points: int = 0
    highest_decision_file: str = "-"
    highest_decision_file_points: int = 0
    highest_decision_file_breakdown: dict[str, int] = field(default_factory=dict)

    @property
    def decision_density(self) -> float:
        if self.non_empty_loc == 0:
            return 0.0
        return self.decision_points / self.non_empty_loc

    @property
    def approximate_complexity(self) -> int:
        return self.functions + self.decision_points


RUST_DECISION_PATTERNS = (
    ("if", r"\bif\b"),
    ("else if", r"\belse\s+if\b"),
    ("match", r"\bmatch\b"),
    ("for", r"\bfor\b"),
    ("while", r"\bwhile\b"),
    ("loop", r"\bloop\b"),
    ("&&", r"&&"),
    ("||", r"\|\|"),
    ("?", r"\?"),
    (".map", r"\.map\("),
    (".and_then", r"\.and_then\("),
    (".filter", r"\.filter\("),
)

TS_DECISION_PATTERNS = (
    ("if", r"\bif\b"),
    ("else if", r"\belse\s+if\b"),
    ("switch", r"\bswitch\b"),
    ("case", r"\bcase\b"),
    ("for", r"\bfor\b"),
    ("while", r"\bwhile\b"),
    ("ternary", r"\?\s*[^?:\n]+\s*:"),
    ("&&", r"&&"),
    ("||", r"\|\|"),
    (".map", r"\.map\("),
    (".filter", r"\.filter\("),
    (".find", r"\.find\("),
    (".some", r"\.some\("),
)


DEFAULT_PROJECTS = (
    ProjectConfig("Leptos", Path("leptos-kanban/src"), (".rs",)),
    ProjectConfig(
        "React",
        Path("react-kanban/src"),
        (".ts", ".tsx"),
        excluded_parts=("assets",),
    ),
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Measure LOC and a decision-density proxy for Leptos/React source code.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Optional custom source paths. If omitted, leptos-kanban/src and react-kanban/src are used.",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Print machine-readable CSV instead of the table.",
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Print a GitHub-flavored Markdown table instead of the terminal table.",
    )
    parser.add_argument(
        "--notes",
        action="store_true",
        help="Print the decision-pattern definition below the table.",
    )
    parser.add_argument(
        "--details",
        action="store_true",
        help="Print how the highest decision file was selected.",
    )
    args = parser.parse_args()

    if args.paths:
        projects = tuple(
            ProjectConfig(path.name, path, (".rs", ".ts", ".tsx"))
            for path in args.paths
        )
    else:
        projects = DEFAULT_PROJECTS

    rows = [(project.name, measure_project(project)) for project in projects]

    if args.csv:
        print_csv(rows)
    elif args.markdown:
        print_markdown_table(rows)
        if args.notes:
            print_notes()
        if args.details:
            print_highest_file_details(rows)
    else:
        print_table(rows)
        if args.notes:
            print_notes()
        if args.details:
            print_highest_file_details(rows)

    return 0


def measure_project(project: ProjectConfig) -> Metrics:
    metrics = Metrics()

    for path in source_files(project):
        text = path.read_text(encoding="utf-8")
        file_decision_breakdown = count_decision_points(path, text)
        file_decision_points = sum(file_decision_breakdown.values())

        metrics.files += 1
        metrics.loc += len(text.splitlines())
        metrics.non_empty_loc += count_non_empty_lines(text)
        metrics.comment_lines += count_comment_lines(text)
        metrics.components += count_components(path, text)
        metrics.functions += count_functions(path, text)
        metrics.types += count_types(path, text)
        metrics.decision_points += file_decision_points

        if file_decision_points > metrics.highest_decision_file_points:
            metrics.highest_decision_file = str(path)
            metrics.highest_decision_file_points = file_decision_points
            metrics.highest_decision_file_breakdown = file_decision_breakdown

    return metrics


def source_files(project: ProjectConfig) -> list[Path]:
    if project.root.is_file():
        candidates = [project.root]
    else:
        candidates = sorted(project.root.rglob("*"))

    return [
        path
        for path in candidates
        if path.is_file()
        and path.suffix in project.extensions
        and not any(part in project.excluded_parts for part in path.parts)
    ]


def count_non_empty_lines(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip())


def count_comment_lines(text: str) -> int:
    return sum(
        1
        for line in text.splitlines()
        if line.strip().startswith(("//", "/*", "*"))
    )


def count_components(path: Path, text: str) -> int:
    if path.suffix == ".rs":
        return len(re.findall(r"#\[component\]", text))

    return len(
        re.findall(
            r"(?m)^\s*(?:export\s+)?function\s+[A-Z][A-Za-z0-9_]*\s*\(",
            text,
        )
    )


def count_functions(path: Path, text: str) -> int:
    if path.suffix == ".rs":
        return len(
            re.findall(
                r"(?m)^\s*(?:pub\s+)?(?:async\s+)?fn\s+\w+",
                text,
            )
        )

    named_functions = len(
        re.findall(r"(?m)^\s*(?:export\s+)?function\s+\w+\s*\(", text)
    )
    arrow_functions = len(
        re.findall(
            r"(?m)^\s*(?:export\s+)?const\s+\w+\s*=\s*(?:\([^=]*\)|\w+)\s*=>",
            text,
        )
    )
    return named_functions + arrow_functions


def count_types(path: Path, text: str) -> int:
    if path.suffix == ".rs":
        return len(re.findall(r"(?m)^\s*(?:pub\s+)?(?:struct|enum)\s+\w+", text))

    return len(
        re.findall(
            r"(?m)^\s*(?:export\s+)?(?:type|interface|enum)\s+\w+",
            text,
        )
    )


def count_decision_points(path: Path, text: str) -> dict[str, int]:
    patterns = RUST_DECISION_PATTERNS if path.suffix == ".rs" else TS_DECISION_PATTERNS
    counts = {}

    for label, pattern in patterns:
        if label == "||":
            count = count_logical_or(text)
        else:
            count = len(re.findall(pattern, text))

        if count > 0:
            counts[label] = count

    return counts


def count_logical_or(text: str) -> int:
    count = 0

    for match in re.finditer(r"\|\|", text):
        line_start = text.rfind("\n", 0, match.start()) + 1
        line_end = text.find("\n", match.end())
        if line_end == -1:
            line_end = len(text)

        left = text[line_start:match.start()].rstrip()
        right = text[match.end():line_end].lstrip()

        if is_logical_or_context(left, right):
            count += 1

    return count


def is_logical_or_context(left: str, right: str) -> bool:
    if not left or not right:
        return False

    if left.endswith("move"):
        return False

    if left[-1] in "=([{,;":
        return False

    if right[0] in "{),];":
        return False

    return True


def print_csv(rows: list[tuple[str, Metrics]]) -> None:
    print(
        "project,files,loc,non_empty_loc,comment_lines,components,functions,"
        "types,decision_points,decision_density,approximate_complexity,"
        "highest_decision_file,highest_decision_file_points"
    )
    for name, metrics in rows:
        print(
            f"{name},{metrics.files},{metrics.loc},{metrics.non_empty_loc},"
            f"{metrics.comment_lines},{metrics.components},{metrics.functions},"
            f"{metrics.types},{metrics.decision_points},"
            f"{metrics.decision_density:.4f},{metrics.approximate_complexity},"
            f"{metrics.highest_decision_file},{metrics.highest_decision_file_points}"
        )


def print_table(rows: list[tuple[str, Metrics]]) -> None:
    comparison_rows = comparison_table_rows(rows)
    headers = ("Kriterium", *(name for name, _metrics in rows))
    widths = [
        max(len(row[index]) for row in (headers, *comparison_rows))
        for index in range(len(headers))
    ]

    print(" | ".join(cell.ljust(widths[index]) for index, cell in enumerate(headers)))
    print("-+-".join("-" * width for width in widths))

    for row in comparison_rows:
        print(" | ".join(cell.ljust(widths[index]) for index, cell in enumerate(row)))


def print_markdown_table(rows: list[tuple[str, Metrics]]) -> None:
    comparison_rows = comparison_table_rows(rows)
    project_names = [name for name, _metrics in rows]

    print("| Kriterium | " + " | ".join(project_names) + " |")
    print("|---|" + "|".join("---:" for _name in project_names) + "|")

    for row in comparison_rows:
        print("| " + " | ".join(row) + " |")


def comparison_table_rows(rows: list[tuple[str, Metrics]]) -> list[tuple[str, ...]]:
    metrics_by_name = {name: metrics for name, metrics in rows}
    project_names = [name for name, _metrics in rows]

    comparison_rows = [
        ("Quell-Dateien", lambda metrics: str(metrics.files)),
        ("LOC gesamt", lambda metrics: str(metrics.loc)),
        ("Nicht-leere LOC", lambda metrics: str(metrics.non_empty_loc)),
        ("Komponenten", lambda metrics: str(metrics.components)),
        ("Funktionen/Methoden", lambda metrics: str(metrics.functions)),
        ("Typen/Structs/Enums/Interfaces", lambda metrics: str(metrics.types)),
        (
            "Komplexitäts-Proxy: Entscheidungsstellen",
            lambda metrics: str(metrics.decision_points),
        ),
        (
            "Approx. Gesamtkomplexität: Funktionen + Entscheidungsstellen",
            lambda metrics: str(metrics.approximate_complexity),
        ),
        (
            "Komplexeste Datei nach Proxy",
            lambda metrics: (
                f"`{Path(metrics.highest_decision_file).name}`, "
                f"{metrics.highest_decision_file_points}"
            ),
        ),
    ]

    table_rows = []
    for criterion, format_value in comparison_rows:
        values = [format_value(metrics_by_name[name]) for name in project_names]
        table_rows.append((criterion, *values))

    return table_rows


def print_notes() -> None:
    print()
    print("Decision patterns:")
    print("  Rust: if, else if, match, for, while, loop, &&, ||, ?, map, and_then, filter")
    print("  TS/TSX: if, else if, switch, case, for, while, ternary, &&, ||, map, filter, find, some")
    print()
    print("Formula:")
    print("  decision density = decision points / non-empty LOC")


def print_highest_file_details(rows: list[tuple[str, Metrics]]) -> None:
    print()
    print("Highest decision file details:")
    for name, metrics in rows:
        print(f"  {name}: {metrics.highest_decision_file}")
        print(f"    decision points: {metrics.highest_decision_file_points}")
        for label, count in sorted(
            metrics.highest_decision_file_breakdown.items(),
            key=lambda item: (-item[1], item[0]),
        ):
            print(f"    {label}: {count}")


if __name__ == "__main__":
    raise SystemExit(main())
