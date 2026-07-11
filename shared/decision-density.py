#!/usr/bin/env python3
# python3 shared/decision-density.py
# python3 shared/decision-density.py --state-details
# python3 shared/decision-density.py --details --notes

from __future__ import annotations

import argparse
import re
from collections import Counter
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


@dataclass
class ReactivityMetrics:
    state_types: int = 0
    state_type_names: list[str] = field(default_factory=list)
    hook_definitions: int = 0
    hook_calls: int = 0
    hook_builtin_calls: int = 0
    hook_custom_calls: int = 0
    hook_call_breakdown: dict[str, int] = field(default_factory=dict)
    hook_definition_names: set[str] = field(default_factory=set)
    signal_constructions: int = 0
    signal_breakdown: dict[str, int] = field(default_factory=dict)


REACT_BUILTIN_HOOKS = frozenset(
    (
        "useCallback",
        "useContext",
        "useDebugValue",
        "useDeferredValue",
        "useEffect",
        "useId",
        "useImperativeHandle",
        "useInsertionEffect",
        "useLayoutEffect",
        "useMemo",
        "useReducer",
        "useRef",
        "useState",
        "useSyncExternalStore",
        "useTransition",
    )
)


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


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

if not (REPO_ROOT / "leptos-kanban/src").is_dir():
    raise RuntimeError(f"Leptos source directory not found below {REPO_ROOT}")

if not (REPO_ROOT / "react-kanban/src").is_dir():
    raise RuntimeError(f"React source directory not found below {REPO_ROOT}")


DEFAULT_PROJECTS = (
    ProjectConfig("Leptos", REPO_ROOT / "leptos-kanban/src", (".rs",)),
    ProjectConfig(
        "React",
        REPO_ROOT / "react-kanban/src",
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
        "--notes",
        action="store_true",
        help="Print the decision-pattern definition below the table.",
    )
    parser.add_argument(
        "--details",
        action="store_true",
        help="Print how the highest decision file was selected.",
    )
    parser.add_argument(
        "--state-details",
        action="store_true",
        help="Print detailed hook and signal breakdowns for the state/reactivity metrics.",
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
    reactivity_rows = [
        (project.name, measure_reactivity_project(project)) for project in projects
    ]

    if args.csv:
        print_csv(rows)
    else:
        print_table(rows)
        print_reactivity_table(reactivity_rows)
        if args.state_details:
            print_state_details(reactivity_rows)
        if args.notes:
            print_notes()
            print_reactivity_notes()
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


def measure_reactivity_project(project: ProjectConfig) -> ReactivityMetrics:
    metrics = ReactivityMetrics()

    state_root = state_object_root(project)
    if state_root.is_dir():
        state_project = ProjectConfig(
            project.name,
            state_root,
            project.extensions,
            project.excluded_parts,
        )
        for path in source_files(state_project):
            text = path.read_text(encoding="utf-8")
            state_type_names = collect_state_type_names(path, text)
            metrics.state_types += len(state_type_names)
            metrics.state_type_names.extend(state_type_names)

    for path in source_files(project):
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".rs":
            signal_breakdown = count_signal_constructions(text)
            metrics.signal_constructions += sum(signal_breakdown.values())
            metrics.signal_breakdown = add_counts(
                metrics.signal_breakdown,
                signal_breakdown,
            )
        else:
            hook_definitions = collect_hook_definitions(text)
            hook_calls = count_hook_calls(text)
            metrics.hook_definitions += len(hook_definitions)
            metrics.hook_definition_names.update(hook_definitions)
            metrics.hook_calls += sum(hook_calls.values())
            metrics.hook_call_breakdown = add_counts(
                metrics.hook_call_breakdown,
                hook_calls,
            )

    metrics.hook_builtin_calls = sum(
        count
        for name, count in metrics.hook_call_breakdown.items()
        if name in REACT_BUILTIN_HOOKS
    )
    metrics.hook_custom_calls = metrics.hook_calls - metrics.hook_builtin_calls
    return metrics


def state_object_root(project: ProjectConfig) -> Path:
    if ".rs" in project.extensions:
        return project.root / "types" / "state"

    serialize_root = project.root / "types" / "serialize"
    if serialize_root.is_dir():
        return serialize_root

    return project.root / "types" / "state"


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


def count_state_types(path: Path, text: str) -> int:
    return len(collect_state_type_names(path, text))


def collect_state_type_names(path: Path, text: str) -> list[str]:
    if path.suffix == ".rs":
        return re.findall(r"(?m)^\s*(?:pub\s+)?(?:struct|enum)\s+(\w+)", text)

    names = re.findall(
        r"(?m)^export\s+type\s+(\w+)\s*=\s*\{",
        text,
    )
    return [
        name
        for name in names
        if not name.startswith("Raw") and not name.endswith("Id")
    ]


def collect_hook_definitions(text: str) -> set[str]:
    return set(
        re.findall(
            r"(?m)^\s*export\s+function\s+(use[A-Z][A-Za-z0-9_]*)\s*\(",
            text,
        )
    )


def count_hook_calls(text: str) -> dict[str, int]:
    counts: Counter[str] = Counter()
    definition_pattern = re.compile(
        r"^\s*export\s+function\s+use[A-Z][A-Za-z0-9_]*\s*\("
    )
    call_pattern = re.compile(r"\b(use[A-Z][A-Za-z0-9_]*)\s*\(")

    for line in text.splitlines():
        if definition_pattern.search(line):
            continue
        counts.update(call_pattern.findall(line))

    return dict(counts)


def count_signal_constructions(text: str) -> dict[str, int]:
    return dict(
        Counter(
            re.findall(
                r"\b(RwSignal::new|Signal::derive|Signal::from|"
                r"create_signal|create_rw_signal|create_memo)\s*\(",
                text,
            )
        )
    )


def add_counts(left: dict[str, int], right: dict[str, int]) -> dict[str, int]:
    counts = Counter(left)
    counts.update(right)
    return dict(counts)


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


def print_reactivity_table(rows: list[tuple[str, ReactivityMetrics]]) -> None:
    print()
    print("State-/Reaktivitäts-Metriken:")

    comparison_rows = reactivity_table_rows(rows)
    headers = ("Kriterium", *(name for name, _metrics in rows))
    widths = [
        max(len(row[index]) for row in (headers, *comparison_rows))
        for index in range(len(headers))
    ]

    print(" | ".join(cell.ljust(widths[index]) for index, cell in enumerate(headers)))
    print("-+-".join("-" * width for width in widths))

    for row in comparison_rows:
        print(" | ".join(cell.ljust(widths[index]) for index, cell in enumerate(row)))


def print_state_details(rows: list[tuple[str, ReactivityMetrics]]) -> None:
    print()
    print("State-/Reaktivitäts-Details:")

    for name, metrics in rows:
        print(f"  {name}:")

        if metrics.state_type_names:
            print(
                f"    State-Objekte: {metrics.state_types} gesamt, "
                + ", ".join(sorted(metrics.state_type_names))
            )

        if metrics.hook_calls:
            print(
                "    Hook-Aufrufe: "
                f"{metrics.hook_calls} gesamt, "
                f"{metrics.hook_builtin_calls} Built-in, "
                f"{metrics.hook_custom_calls} Custom"
            )
            print_count_breakdown("    Hook-Aufrufe nach Name", metrics.hook_call_breakdown)

        if metrics.hook_definition_names:
            print(
                "    Hook-Definitionen: "
                + ", ".join(sorted(metrics.hook_definition_names))
            )

        if metrics.signal_constructions:
            print(f"    Signal-Konstruktionen: {metrics.signal_constructions} gesamt")
            print_count_breakdown("    Signal-Konstruktionen nach Typ", metrics.signal_breakdown)


def print_count_breakdown(title: str, counts: dict[str, int]) -> None:
    print(f"{title}:")
    for label, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        print(f"      {label}: {count}")


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


def reactivity_table_rows(
    rows: list[tuple[str, ReactivityMetrics]],
) -> list[tuple[str, ...]]:
    metrics_by_name = {name: metrics for name, metrics in rows}
    project_names = [name for name, _metrics in rows]

    comparison_rows = [
        ("State-Objekte", lambda metrics: str(metrics.state_types)),
        ("Hook-Definitionen", lambda metrics: str(metrics.hook_definitions)),
        ("Hook-Aufrufe", lambda metrics: str(metrics.hook_calls)),
        ("Signal-Konstruktionen", lambda metrics: str(metrics.signal_constructions)),
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


def print_reactivity_notes() -> None:
    print()
    print("State/reactivity patterns:")
    print("  State objects: Leptos structs below src/types/state; React object types below src/types/serialize")
    print("  React ID aliases and Raw DTO types are excluded from state objects")
    print("  Hooks: React-style useX definitions and invocations, excluding definition lines")
    print("  Signals: Leptos signal constructions via RwSignal::new, Signal::derive, Signal::from")


def print_highest_file_details(rows: list[tuple[str, Metrics]]) -> None:
    print()
    print("Highest decision file details:")
    for name, metrics in rows:
        print(f"  {name}: {format_path(metrics.highest_decision_file)}")
        print(f"    decision points: {metrics.highest_decision_file_points}")
        for label, count in sorted(
            metrics.highest_decision_file_breakdown.items(),
            key=lambda item: (-item[1], item[0]),
        ):
            print(f"    {label}: {count}")


def format_path(path: str) -> str:
    path_value = Path(path)
    try:
        return str(path_value.relative_to(REPO_ROOT))
    except ValueError:
        return str(path_value)


if __name__ == "__main__":
    raise SystemExit(main())
