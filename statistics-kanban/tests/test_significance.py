import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pandas as pd


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from significance import (  # noqa: E402
    create_html_report,
    effect_magnitude,
    median_speedup,
    test_normality,
    test_performance_differences,
)


class SignificanceTest(unittest.TestCase):
    def test_effect_magnitude_uses_configured_boundaries(self) -> None:
        self.assertEqual(effect_magnitude(0.1), "vernachlässigbar")
        self.assertEqual(effect_magnitude(-0.2), "klein")
        self.assertEqual(effect_magnitude(0.4), "mittel")
        self.assertEqual(effect_magnitude(-0.5), "groß")

    def test_median_speedup_reports_direction_and_relative_advantage(self) -> None:
        framework, speedup = median_speedup(20.0, 50.0)

        self.assertEqual(framework, "Leptos")
        self.assertEqual(speedup, 60.0)

    @patch("significance.pg.multicomp")
    @patch("significance.pg.mwu")
    @patch("significance.calculate_cliffs_delta")
    def test_performance_comparison_uses_pingouin_and_cliffs_delta(
        self,
        calculate_cliffs_delta,
        mwu,
        multicomp,
    ) -> None:
        calculate_cliffs_delta.return_value = (1.0, "large")
        mwu.return_value = pd.DataFrame(
            {"U_val": [4.0], "p_val": [0.01], "RBC": [1.0]}
        )
        multicomp.return_value = (np.array([True]), np.array([0.01]))
        measurements = pd.DataFrame(
            {
                "browser": ["chromium"] * 4,
                "action": ["task-create"] * 4,
                "board": ["Board 1 (Leer)"] * 4,
                "framework": ["Leptos", "Leptos", "React", "React"],
                "performance_ms": [1.0, 2.0, 3.0, 4.0],
            }
        )

        results = test_performance_differences(measurements)

        np.testing.assert_array_equal(mwu.call_args.args[0], [3.0, 4.0])
        np.testing.assert_array_equal(mwu.call_args.args[1], [1.0, 2.0])
        np.testing.assert_array_equal(
            calculate_cliffs_delta.call_args.args[0],
            [3.0, 4.0],
        )
        np.testing.assert_array_equal(
            calculate_cliffs_delta.call_args.args[1],
            [1.0, 2.0],
        )
        self.assertEqual(
            mwu.call_args.kwargs,
            {
                "alternative": "two-sided",
                "method": "asymptotic",
                "use_continuity": True,
            },
        )
        np.testing.assert_array_equal(multicomp.call_args.args[0], [0.01])
        self.assertEqual(
            multicomp.call_args.kwargs,
            {"alpha": 0.05, "method": "holm"},
        )
        self.assertEqual(results.iloc[0]["u_statistic"], 4.0)
        self.assertEqual(results.iloc[0]["p_value"], 0.01)
        self.assertEqual(results.iloc[0]["cliffs_delta"], 1.0)

    def test_empty_html_report_contains_complete_page(self) -> None:
        report = create_html_report(pd.DataFrame(columns=[
            "significant", "noteworthy", "p_value_holm", "cliffs_delta"
        ]))

        self.assertIn("<!doctype html>", report)
        self.assertIn("Keine Vergleiche erfüllen beide Kriterien", report)

    @patch("significance.pg.multicomp")
    @patch("significance.shapiro")
    def test_normality_uses_shapiro_wilk_and_holm_correction(
        self,
        shapiro_mock,
        multicomp,
    ) -> None:
        shapiro_mock.side_effect = [
            SimpleNamespace(statistic=0.98, pvalue=0.4),
            SimpleNamespace(statistic=0.80, pvalue=0.001),
        ]
        multicomp.return_value = (
            np.array([False, True]),
            np.array([0.4, 0.002]),
        )
        measurements = pd.DataFrame(
            {
                "browser": ["chromium"] * 6,
                "action": ["task-create"] * 6,
                "board": ["Board 1 (Leer)"] * 6,
                "framework": ["Leptos"] * 3 + ["React"] * 3,
                "performance_ms": [1.0, 1.1, 0.9, 2.0, 5.0, 9.0],
            }
        )

        results = test_normality(measurements)

        np.testing.assert_array_equal(
            shapiro_mock.call_args_list[0].args[0],
            [1.0, 1.1, 0.9],
        )
        self.assertEqual(multicomp.call_args.kwargs, {
            "alpha": 0.05,
            "method": "holm",
        })
        self.assertFalse(results.iloc[0]["normality_rejected"])
        self.assertTrue(results.iloc[1]["normality_rejected"])
        self.assertEqual(results.iloc[1]["p_value_holm"], 0.002)


if __name__ == "__main__":
    unittest.main()
