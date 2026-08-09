#!/usr/bin/env python3
# python3 shared/implementation-metrics.py

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
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
    code_loc: int = 0
    non_empty_loc: int = 0
    comment_lines: int = 0
    components: int = 0


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


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
HTML_OUTPUT_PATH = REPO_ROOT / "results/implementation/implementation-metrics.html"

LOC_GROUP_ORDER = (
    "App und Einstieg",
    "Kanban-Komponenten",
    "UI-Komponenten",
    "Drag-and-drop",
    "Zustand und Reaktivität",
    "Datenmodelle und Validierung",
    "Messinstrumentierung",
    "Sonstiger Glue-Code",
)

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
        description="Measure implementation and reactivity metrics for Leptos/React source code.",
    )
    parser.add_argument(
        "--console",
        action="store_true",
        help="Additionally print the metrics to the console.",
    )
    args = parser.parse_args()

    rows = [(project.name, measure_project(project)) for project in DEFAULT_PROJECTS]
    loc_group_rows = [
        (project.name, measure_loc_groups(project))
        for project in DEFAULT_PROJECTS
    ]
    reactivity_rows = [
        (project.name, measure_reactivity_project(project))
        for project in DEFAULT_PROJECTS
    ]

    write_html_report(
        HTML_OUTPUT_PATH,
        rows,
        loc_group_rows,
        reactivity_rows,
    )
    if args.console:
        print_table(rows)
        print_loc_group_table(loc_group_rows)
        print_reactivity_table(reactivity_rows)
        print_state_details(reactivity_rows)

    return 0


def measure_project(project: ProjectConfig) -> Metrics:
    paths = source_files(project)
    metrics = measure_tokei(paths)

    for path in paths:
        text = path.read_text(encoding="utf-8")
        metrics.components += count_components(path, text)

    return metrics


def measure_loc_groups(project: ProjectConfig) -> dict[str, int]:
    grouped_paths: dict[str, list[Path]] = {
        group: [] for group in LOC_GROUP_ORDER
    }

    for path in source_files(project):
        grouped_paths[classify_loc_group(project, path)].append(path)

    group_loc = {
        group: measure_tokei(paths).code_loc
        for group, paths in grouped_paths.items()
    }
    total_loc = measure_tokei(source_files(project)).code_loc
    if sum(group_loc.values()) != total_loc:
        raise RuntimeError(
            f"Grouped LOC for {project.name} do not add up to total LOC"
        )
    return group_loc


def classify_loc_group(project: ProjectConfig, path: Path) -> str:
    relative_path = path.relative_to(project.root)
    parts = relative_path.parts

    if relative_path.name in {"app.rs", "App.tsx", "main.rs", "main.tsx"}:
        return "App und Einstieg"
    if parts[:2] == ("components", "kanban"):
        return "Kanban-Komponenten"
    if parts[:2] == ("components", "ui"):
        return "UI-Komponenten"
    if (
        parts[:2] == ("components", "drag_and_drop")
        or parts[:2] == ("types", "drag_and_drop")
        or relative_path.name == "drag_and_drop.rs"
    ):
        return "Drag-and-drop"
    if (
        parts[:1] == ("hooks",)
        or parts[:2] == ("types", "state")
        or relative_path.name == "app_context.rs"
    ):
        return "Zustand und Reaktivität"
    if parts[:1] == ("types",):
        return "Datenmodelle und Validierung"
    if relative_path.stem == "performance":
        return "Messinstrumentierung"
    return "Sonstiger Glue-Code"


def measure_tokei(paths: list[Path]) -> Metrics:
    if not paths:
        return Metrics()

    try:
        result = subprocess.run(
            ["tokei", "--output", "json", *(str(path) for path in paths)],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as error:
        raise RuntimeError("tokei is required to collect file and LOC metrics") from error
    except subprocess.CalledProcessError as error:
        message = error.stderr.strip() or "unknown tokei error"
        raise RuntimeError(f"tokei failed: {message}") from error

    report = json.loads(result.stdout)
    totals = report["Total"]
    file_names = {
        file_report["name"]
        for language, language_report in report.items()
        if language != "Total"
        for file_report in language_report.get("reports", [])
    }

    code = int(totals["code"])
    comments = int(totals["comments"])
    blanks = int(totals["blanks"])

    return Metrics(
        files=len(file_names),
        loc=code + comments + blanks,
        code_loc=code,
        non_empty_loc=code + comments,
        comment_lines=comments,
    )


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


def count_components(path: Path, text: str) -> int:
    if path.suffix == ".rs":
        return len(re.findall(r"#\[component\]", text))

    return len(
        re.findall(
            r"(?m)^\s*(?:export\s+)?function\s+[A-Z][A-Za-z0-9_]*\s*\(",
            text,
        )
    )


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


def print_loc_group_table(rows: list[tuple[str, dict[str, int]]]) -> None:
    print()
    print("Code-LOC nach Funktionsbereich (ohne Leer- und Kommentarzeilen):")
    headers = ("Bereich", *(name for name, _groups in rows))
    table_rows = loc_group_table_rows(rows, include_comparison=False)
    widths = [
        max(len(row[index]) for row in (headers, *table_rows))
        for index in range(len(headers))
    ]
    print(" | ".join(cell.ljust(widths[index]) for index, cell in enumerate(headers)))
    print("-+-".join("-" * width for width in widths))
    for row in table_rows:
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


def loc_group_table_rows(
    rows: list[tuple[str, dict[str, int]]],
    *,
    include_comparison: bool = True,
) -> list[tuple[str, ...]]:
    group_values = {name: groups for name, groups in rows}
    project_names = [name for name, _groups in rows]
    table_rows: list[tuple[str, ...]] = []

    for group in LOC_GROUP_ORDER:
        values = [group_values[name][group] for name in project_names]
        row = [group, *(str(value) for value in values)]
        if include_comparison and len(values) == 2:
            difference = values[0] - values[1]
            if difference == 0:
                more_loc = "Gleichstand"
            else:
                more_loc = project_names[0] if difference > 0 else project_names[1]
            row.extend((f"{difference:+d}", more_loc))
        table_rows.append(tuple(row))

    totals = [sum(group_values[name].values()) for name in project_names]
    total_row = ["Gesamt", *(str(value) for value in totals)]
    if include_comparison and len(totals) == 2:
        difference = totals[0] - totals[1]
        more_loc = (
            "Gleichstand"
            if difference == 0
            else project_names[0] if difference > 0 else project_names[1]
        )
        total_row.extend((f"{difference:+d}", more_loc))
    table_rows.append(tuple(total_row))
    return table_rows


def write_html_report(
    output_path: Path,
    implementation_rows: list[tuple[str, Metrics]],
    loc_group_rows: list[tuple[str, dict[str, int]]],
    reactivity_rows: list[tuple[str, ReactivityMetrics]],
) -> None:
    sections = [
        "<h1>Implementierungsmetriken</h1>",
        html_table(
            ("Kriterium", *(name for name, _metrics in implementation_rows)),
            comparison_table_rows(implementation_rows),
        ),
    ]

    project_names = [name for name, _groups in loc_group_rows]
    sections.extend(
        (
            "<h2>Code-LOC nach Funktionsbereich</h2>",
            "<p>Die Quelldateien werden nach vergleichbaren fachlichen "
            "Verantwortlichkeiten gruppiert. Jede Datei gehört genau zu einem "
            "Bereich. Gezählt werden ausschließlich Codezeilen, also keine "
            "Leer- oder Kommentarzeilen. Die Gruppen summieren sich auf die "
            "gesamten Code-LOC. Die "
            "Differenz ist als Leptos minus React angegeben.</p>",
            html_table(
                (
                    "Funktionsbereich",
                    *(f"{name} Code-LOC" for name in project_names),
                    "Differenz (L−R)",
                    "Mehr LOC",
                ),
                loc_group_table_rows(loc_group_rows),
            ),
        )
    )

    sections.extend(
        (
            "<h2>State-/Reaktivitäts-Metriken</h2>",
            html_table(
                ("Kriterium", *(name for name, _metrics in reactivity_rows)),
                reactivity_table_rows(reactivity_rows),
            ),
        )
    )

    sections.extend(
        (
            "<h2>State-/Reaktivitäts-Details</h2>",
            html_state_details(reactivity_rows),
        )
    )

    document = f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Implementierungsmetriken</title>
  <style>
    :root {{ color-scheme: light; font-family: Inter, system-ui, sans-serif; }}
    body {{ margin: 0 auto; max-width: 1100px; padding: 2rem; color: #1f2937; background: #f8fafc; }}
    h1, h2, h3 {{ color: #111827; }}
    h2 {{ margin-top: 2.5rem; }}
    table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; background: #fff; box-shadow: 0 1px 3px #0000001a; }}
    th, td {{ padding: .7rem .85rem; border: 1px solid #dbe2ea; text-align: left; }}
    th {{ background: #e8eef5; font-weight: 650; }}
    tbody tr:nth-child(even) {{ background: #f8fafc; }}
    .details {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; }}
    .card {{ padding: 1rem 1.2rem; border: 1px solid #dbe2ea; border-radius: .5rem; background: #fff; box-shadow: 0 1px 3px #00000012; }}
    .card h3 {{ margin-top: 0; }}
    .card table {{ box-shadow: none; font-size: .92rem; }}
    code {{ padding: .1rem .25rem; border-radius: .2rem; background: #e8eef5; }}
  </style>
</head>
<body>
  {''.join(sections)}
</body>
</html>
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(document, encoding="utf-8")


def html_table(headers: tuple[str, ...], rows: list[tuple[str, ...]]) -> str:
    header_cells = "".join(f"<th>{html.escape(value)}</th>" for value in headers)
    body_rows = "".join(
        "<tr>" + "".join(f"<td>{html.escape(value)}</td>" for value in row) + "</tr>"
        for row in rows
    )
    return f"<table><thead><tr>{header_cells}</tr></thead><tbody>{body_rows}</tbody></table>"


def html_state_details(rows: list[tuple[str, ReactivityMetrics]]) -> str:
    cards = []
    for name, metrics in rows:
        details = []

        if metrics.state_type_names:
            state_names = ", ".join(sorted(metrics.state_type_names))
            details.append(
                f"<p><strong>State-Objekte:</strong> {metrics.state_types} gesamt<br>"
                f"{html.escape(state_names)}</p>"
            )

        if metrics.hook_calls:
            details.append(
                f"<p><strong>Hook-Aufrufe:</strong> {metrics.hook_calls} gesamt, "
                f"{metrics.hook_builtin_calls} Built-in, "
                f"{metrics.hook_custom_calls} Custom</p>"
            )
            details.append(
                html_breakdown_table("Hook-Aufrufe nach Name", metrics.hook_call_breakdown)
            )

        if metrics.hook_definition_names:
            hook_names = ", ".join(sorted(metrics.hook_definition_names))
            details.append(
                f"<p><strong>Hook-Definitionen:</strong> {html.escape(hook_names)}</p>"
            )

        if metrics.signal_constructions:
            details.append(
                f"<p><strong>Signal-Konstruktionen:</strong> "
                f"{metrics.signal_constructions} gesamt</p>"
            )
            details.append(
                html_breakdown_table(
                    "Signal-Konstruktionen nach Typ",
                    metrics.signal_breakdown,
                )
            )

        cards.append(
            f'<section class="card"><h3>{html.escape(name)}</h3>{"".join(details)}</section>'
        )

    return f'<div class="details">{"".join(cards)}</div>'


def html_breakdown_table(title: str, counts: dict[str, int]) -> str:
    rows = [
        (label, str(count))
        for label, count in sorted(
            counts.items(),
            key=lambda item: (-item[1], item[0]),
        )
    ]
    return f"<h4>{html.escape(title)}</h4>" + html_table(("Name", "Anzahl"), rows)


if __name__ == "__main__":
    raise SystemExit(main())
