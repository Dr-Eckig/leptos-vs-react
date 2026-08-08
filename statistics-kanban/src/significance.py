from html import escape
from pathlib import Path

import config as cfg

import numpy as np
import pandas as pd
import pingouin as pg
from scipy.stats import shapiro


GROUP_COLUMNS = ["browser", "action", "board"]
RESULT_COLUMNS = [
    *GROUP_COLUMNS,
    "n_leptos",
    "n_react",
    "median_leptos_ms",
    "median_react_ms",
    "median_difference_ms",
    "faster_framework",
    "median_speedup_percent",
    "u_statistic",
    "p_value",
    "p_value_holm",
    "cliffs_delta",
    "effect_magnitude",
    "significant",
    "noteworthy",
]
NORMALITY_GROUP_COLUMNS = [*GROUP_COLUMNS, "framework"]
NORMALITY_RESULT_COLUMNS = [
    *NORMALITY_GROUP_COLUMNS,
    "sample_size",
    "shapiro_w",
    "p_value",
    "p_value_holm",
    "normality_rejected",
    "assessment",
]


def test_performance_differences(measurements: pd.DataFrame) -> pd.DataFrame:
    """Compare Leptos and React for every browser/action/board scenario.

    Runs are independent samples. A two-sided Mann-Whitney U test is used with
    tie correction and continuity correction. Holm's method controls the
    family-wise error rate across all scenarios.
    """
    performance = measurements.dropna(subset=["performance_ms"]).copy()
    records: list[dict[str, object]] = []

    for keys, scenario in performance.groupby(GROUP_COLUMNS, observed=True):
        samples = {
            framework: group["performance_ms"].to_numpy(dtype=float)
            for framework, group in scenario.groupby("framework", observed=True)
        }
        leptos = samples.get("Leptos", np.array([], dtype=float))
        react = samples.get("React", np.array([], dtype=float))
        if len(leptos) == 0 or len(react) == 0:
            continue

        test_result = pg.mwu(
            leptos,
            react,
            alternative="two-sided",
            method="asymptotic",
            use_continuity=True,
        )
        test_row = test_result.iloc[0]
        u_statistic = float(test_row["U_val"])
        p_value = float(test_row["p_val"])
        # For two independent samples, Pingouin's rank-biserial correlation is
        # algebraically identical to Cliff's delta with the same sample order.
        cliffs_delta = float(test_row["RBC"])
        leptos_median = float(np.median(leptos))
        react_median = float(np.median(react))
        faster_framework, speedup = median_speedup(leptos_median, react_median)

        records.append(
            {
                **dict(zip(GROUP_COLUMNS, keys)),
                "n_leptos": len(leptos),
                "n_react": len(react),
                "median_leptos_ms": leptos_median,
                "median_react_ms": react_median,
                "median_difference_ms": leptos_median - react_median,
                "faster_framework": faster_framework,
                "median_speedup_percent": speedup,
                "u_statistic": u_statistic,
                "p_value": p_value,
                "cliffs_delta": cliffs_delta,
                "effect_magnitude": effect_magnitude(cliffs_delta),
            }
        )

    if not records:
        return pd.DataFrame(columns=RESULT_COLUMNS)

    results = pd.DataFrame.from_records(records)
    reject, corrected_p_values = pg.multicomp(
        results["p_value"].to_numpy(),
        alpha=cfg.SIGNIFICANCE_ALPHA,
        method="holm",
    )
    results["p_value_holm"] = corrected_p_values
    results["significant"] = reject
    results["noteworthy"] = results["significant"] & (
        results["cliffs_delta"].abs() >= cfg.SIGNIFICANCE_MIN_EFFECT
    )
    results = sort_results(results)
    return results[RESULT_COLUMNS]


def test_normality(measurements: pd.DataFrame) -> pd.DataFrame:
    """Run a Shapiro-Wilk test for every individual benchmark sample.

    Each framework/browser/action/board combination is tested separately,
    because normality is a property of an individual sample rather than of a
    scenario after pooling frameworks. Holm's method controls the family-wise
    error rate across all tested samples.
    """
    performance = measurements.dropna(subset=["performance_ms"]).copy()
    records: list[dict[str, object]] = []

    for keys, sample_group in performance.groupby(
        NORMALITY_GROUP_COLUMNS,
        observed=True,
    ):
        sample = sample_group["performance_ms"].to_numpy(dtype=float)
        if len(sample) < 3:
            continue

        test_result = shapiro(sample)
        records.append(
            {
                **dict(zip(NORMALITY_GROUP_COLUMNS, keys)),
                "sample_size": len(sample),
                "shapiro_w": float(test_result.statistic),
                "p_value": float(test_result.pvalue),
            }
        )

    if not records:
        return pd.DataFrame(columns=NORMALITY_RESULT_COLUMNS)

    results = pd.DataFrame.from_records(records)
    reject, corrected_p_values = pg.multicomp(
        results["p_value"].to_numpy(),
        alpha=cfg.NORMALITY_ALPHA,
        method="holm",
    )
    results["p_value_holm"] = corrected_p_values
    results["normality_rejected"] = reject
    results["assessment"] = np.where(
        results["normality_rejected"],
        "Hinweis gegen Normalverteilung",
        "Kein Hinweis gegen Normalverteilung",
    )
    results = sort_normality_results(results)
    return results[NORMALITY_RESULT_COLUMNS]


def effect_magnitude(delta: float) -> str:
    absolute_delta = abs(delta)
    if absolute_delta < cfg.CLIFFS_DELTA_SMALL:
        return "vernachlässigbar"
    if absolute_delta < cfg.CLIFFS_DELTA_MEDIUM:
        return "klein"
    if absolute_delta < cfg.CLIFFS_DELTA_LARGE:
        return "mittel"
    return "groß"


def median_speedup(leptos_median: float, react_median: float) -> tuple[str, float]:
    if leptos_median == react_median:
        return "Gleichstand", 0.0

    faster = "Leptos" if leptos_median < react_median else "React"
    slower_median = max(leptos_median, react_median)
    faster_median = min(leptos_median, react_median)
    speedup = (slower_median - faster_median) / slower_median * 100
    return faster, speedup


def write_significance_report(
    results: pd.DataFrame,
    output_dir: Path,
    normality_results: pd.DataFrame | None = None,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / cfg.SIGNIFICANCE_REPORT_FILENAME

    if normality_results is None:
        normality_results = pd.DataFrame(columns=NORMALITY_RESULT_COLUMNS)

    report_path.write_text(
        create_html_report(results, normality_results),
        encoding="utf-8",
    )
    return [report_path]


def create_html_report(
    results: pd.DataFrame,
    normality_results: pd.DataFrame | None = None,
) -> str:
    if normality_results is None:
        normality_results = pd.DataFrame(columns=NORMALITY_RESULT_COLUMNS)
    noteworthy_mask = results["noteworthy"].fillna(False).astype(bool)
    noteworthy = results[noteworthy_mask].copy()
    noteworthy = noteworthy.sort_values(
        ["p_value_holm", "cliffs_delta"],
        ascending=[True, False],
        key=lambda values: values.abs() if values.name == "cliffs_delta" else values,
    )

    significant_count = int(results["significant"].sum())
    noteworthy_table = html_table(noteworthy)
    all_results_table = html_table(results)
    normality_table = html_normality_table(normality_results)
    normality_rejected_count = int(
        normality_results["normality_rejected"].fillna(False).astype(bool).sum()
    )

    return f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Signifikanztests der Performance-Ergebnisse</title>
  <style>
    :root {{ color-scheme: light; --ink: #17212b; --muted: #5d6975;
      --line: #d9e0e7; --panel: #f6f8fa; --leptos: #ef3b39; --react: #087ea4; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; color: var(--ink); background: #fff; font: 15px/1.5 system-ui, sans-serif; }}
    main {{ width: min(1500px, 94vw); margin: 3rem auto 5rem; }}
    h1 {{ margin-bottom: .4rem; font-size: clamp(1.8rem, 3vw, 2.7rem); }}
    h2 {{ margin-top: 2.5rem; }}
    .intro {{ max-width: 900px; color: var(--muted); }}
    .cards {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1rem; margin: 2rem 0; }}
    .card {{ padding: 1.1rem 1.25rem; border: 1px solid var(--line); border-radius: 12px; background: var(--panel); }}
    .number {{ display: block; font-size: 2rem; font-weight: 750; }}
    .label {{ color: var(--muted); }}
    .table-wrap {{ overflow-x: auto; border: 1px solid var(--line); border-radius: 10px; }}
    table {{ width: 100%; border-collapse: collapse; white-space: nowrap; }}
    th, td {{ padding: .58rem .7rem; border-bottom: 1px solid var(--line); text-align: right; }}
    th {{ position: sticky; top: 0; background: #edf1f5; font-size: .82rem; }}
    th:nth-child(-n+3), td:nth-child(-n+3), th:nth-child(6), td:nth-child(6),
    th:nth-child(9), td:nth-child(9) {{ text-align: left; }}
    tbody tr:last-child td {{ border-bottom: 0; }}
    tbody tr:hover {{ background: #f8fafc; }}
    .Leptos {{ color: var(--leptos); font-weight: 700; }}
    .React {{ color: var(--react); font-weight: 700; }}
    details {{ margin-top: 2.5rem; }}
    summary {{ cursor: pointer; font-size: 1.25rem; font-weight: 700; margin-bottom: 1rem; }}
    .note {{ max-width: 1000px; padding: 1rem 1.2rem; border-left: 4px solid #8b98a5; background: var(--panel); }}
    @media (max-width: 700px) {{ .cards {{ grid-template-columns: 1fr; }} main {{ margin-top: 1.5rem; }} }}
  </style>
</head>
<body>
<main>
  <h1>Signifikanztests der Performance-Ergebnisse</h1>
  <p class="intro">React und Leptos werden je Browser, Aktion und Board durch einen
  zweiseitigen Mann-Whitney-U-Test aus Pingouin verglichen. Pingouin liefert auch
  die rank-biseriale Korrelation als das algebraisch identische Cliff’s Delta und
  korrigiert alle p-Werte nach Holm (α = {cfg.SIGNIFICANCE_ALPHA:.2f}). Verwendet
  werden die asymptotische Methode sowie Bindungs- und Stetigkeitskorrektur. Als aussagekräftig
  gelten korrigiert signifikante Ergebnisse mit mindestens mittlerem Effekt
  (|Cliff’s δ| ≥ {cfg.SIGNIFICANCE_MIN_EFFECT:.2f}).</p>

  <section class="cards" aria-label="Zusammenfassung">
    <div class="card"><span class="number">{len(results)}</span><span class="label">Vergleiche insgesamt</span></div>
    <div class="card"><span class="number">{significant_count}</span><span class="label">Holm-korrigiert signifikant</span></div>
    <div class="card"><span class="number">{len(noteworthy)}</span><span class="label">Aussagekräftige Vergleiche</span></div>
    <div class="card"><span class="number">{normality_rejected_count} / {len(normality_results)}</span><span class="label">Normalverteilung verworfen</span></div>
  </section>

  <h2>Aussagekräftige Ergebnisse</h2>
  {noteworthy_table}

  <details>
    <summary>Alle {len(results)} Tests anzeigen</summary>
    {all_results_table}
  </details>

  <h2>Prüfung auf Normalverteilung</h2>
  <p class="intro">Jede Kombination aus Framework, Browser, Aktion und Board wird
  separat mit dem Shapiro-Wilk-Test geprüft. Die p-Werte werden über alle
  Normalitätstests nach Holm korrigiert (α = {cfg.NORMALITY_ALPHA:.2f}). Ein
  korrigierter p-Wert unter α ist ein Hinweis gegen Normalverteilung. Ein
  größerer p-Wert beweist keine Normalverteilung, sondern bedeutet lediglich,
  dass sie mit diesen Daten nicht verworfen wird.</p>
  <details>
    <summary>Alle {len(normality_results)} Normalitätstests anzeigen</summary>
    {normality_table}
  </details>

  <h2>Interpretation</h2>
  <p class="note">Ein positives Cliff’s δ bedeutet tendenziell höhere Laufzeiten
  für Leptos, ein negatives δ tendenziell höhere Laufzeiten für React. Der Vorteil
  basiert deskriptiv auf den Medianen; der U-Test prüft die Verteilungen. Die
  Inferenz setzt unabhängige Läufe voraus und gilt für die gemessenen
  Benchmark-Bedingungen. Sie ersetzt keine Replikation in unabhängigen Sitzungen.</p>
  <p class="note">Der Mann-Whitney-U-Test ist nicht auf normalverteilte Daten
  angewiesen. Die Normalitätsprüfung dient daher der Beschreibung und
  Plausibilisierung der gewählten nichtparametrischen Auswertung.</p>
</main>
</body>
</html>
"""


def html_table(results: pd.DataFrame) -> str:
    if results.empty:
        return '<p class="note">Keine Vergleiche erfüllen beide Kriterien.</p>'

    rows = []
    for row in results.itertuples(index=False):
        browser = cfg.BROWSER_LABELS.get(row.browser, row.browser)
        action = cfg.ACTION_LABELS.get(
            row.action,
            cfg.INITIAL_LOAD_LABELS.get(row.action, row.action),
        )
        board = cfg.BOARD_LABELS.get(row.board, row.board)
        rows.append(
            "<tr>"
            f"<td>{escape(str(browser))}</td>"
            f"<td>{escape(str(action))}</td>"
            f"<td>{escape(str(board))}</td>"
            f"<td>{row.median_leptos_ms:.2f} ms</td>"
            f"<td>{row.median_react_ms:.2f} ms</td>"
            f'<td class="{escape(row.faster_framework)}">{escape(row.faster_framework)}</td>'
            f"<td>{row.median_speedup_percent:.1f} %</td>"
            f"<td>{row.cliffs_delta:.3f}</td>"
            f"<td>{escape(row.effect_magnitude)}</td>"
            f"<td>{row.p_value_holm:.3g}</td>"
            f"<td>{'ja' if row.significant else 'nein'}</td>"
            "</tr>"
        )

    return (
        '<div class="table-wrap"><table><thead><tr>'
        "<th>Browser</th><th>Aktion</th><th>Board</th>"
        "<th>Median Leptos</th><th>Median React</th><th>Schneller</th>"
        "<th>Vorteil</th><th>Cliff’s δ</th><th>Effekt</th>"
        "<th>p (Holm)</th><th>Signifikant</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )


def html_normality_table(results: pd.DataFrame) -> str:
    if results.empty:
        return '<p class="note">Keine auswertbaren Messgruppen vorhanden.</p>'

    rows = []
    for row in results.itertuples(index=False):
        browser = cfg.BROWSER_LABELS.get(row.browser, row.browser)
        action = cfg.ACTION_LABELS.get(
            row.action,
            cfg.INITIAL_LOAD_LABELS.get(row.action, row.action),
        )
        board = cfg.BOARD_LABELS.get(row.board, row.board)
        rows.append(
            "<tr>"
            f"<td>{escape(str(browser))}</td>"
            f"<td>{escape(str(action))}</td>"
            f"<td>{escape(str(board))}</td>"
            f'<td class="{escape(row.framework)}">{escape(row.framework)}</td>'
            f"<td>{row.sample_size}</td>"
            f"<td>{row.shapiro_w:.4f}</td>"
            f"<td>{row.p_value:.3g}</td>"
            f"<td>{row.p_value_holm:.3g}</td>"
            f"<td>{'ja' if row.normality_rejected else 'nein'}</td>"
            "</tr>"
        )

    return (
        '<div class="table-wrap"><table><thead><tr>'
        "<th>Browser</th><th>Aktion</th><th>Board</th><th>Framework</th>"
        "<th>n</th><th>Shapiro-Wilk W</th><th>p</th><th>p (Holm)</th>"
        "<th>Normalverteilung verworfen</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )


def sort_results(results: pd.DataFrame) -> pd.DataFrame:
    results = results.copy()
    results["browser"] = pd.Categorical(
        results["browser"], categories=cfg.BROWSER_ORDER, ordered=True
    )
    results["action"] = pd.Categorical(
        results["action"],
        categories=[*cfg.ACTION_ORDER, *cfg.INITIAL_LOAD_ORDER],
        ordered=True,
    )
    results["board"] = pd.Categorical(
        results["board"],
        categories=[*cfg.BOARD_ORDER, cfg.INITIAL_LOAD_BOARD_LABEL],
        ordered=True,
    )
    results = results.sort_values(GROUP_COLUMNS)
    for column in GROUP_COLUMNS:
        results[column] = results[column].astype(str)
    return results


def sort_normality_results(results: pd.DataFrame) -> pd.DataFrame:
    results = sort_results(results)
    results["framework"] = pd.Categorical(
        results["framework"], categories=cfg.FRAMEWORK_ORDER, ordered=True
    )
    results = results.sort_values(NORMALITY_GROUP_COLUMNS)
    results["framework"] = results["framework"].astype(str)
    return results
