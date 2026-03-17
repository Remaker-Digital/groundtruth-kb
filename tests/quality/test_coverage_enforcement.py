"""Tests for SPEC-1844: Line Coverage Enforcement and Per-Module Tracking.

Verifies coverage gate configuration, per-module targets,
and coverage delta tracking.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


class TestCoverageGateConfiguration:
    """SPEC-1844: Coverage gate in pyproject.toml."""

    def test_global_coverage_gate_configured(self):
        """TEST-10477: cov-fail-under >= 70 (ramp toward 80)."""
        import tomllib

        with open("pyproject.toml", "rb") as f:
            config = tomllib.load(f)

        fail_under = config["tool"]["coverage"]["report"]["fail_under"]
        assert fail_under >= 70, f"Global coverage gate too low: {fail_under}"

    def test_coverage_source_is_src(self):
        """Coverage measures src/ directory."""
        import tomllib

        with open("pyproject.toml", "rb") as f:
            config = tomllib.load(f)

        source = config["tool"]["coverage"]["run"]["source"]
        assert "src" in source


class TestPerModuleCoverageTracking:
    """SPEC-1844: Per-module coverage parsed and stored."""

    def test_parse_coverage_json_report(self):
        """TEST-10478: Coverage JSON parsed to per-module line and branch %."""
        from src.quality_metrics.coverage_tracking import parse_coverage_json

        # Simulated coverage.json structure
        coverage_data = {
            "meta": {"branch_coverage": True},
            "files": {
                "src/multi_tenant/auth.py": {
                    "summary": {
                        "covered_lines": 85,
                        "num_statements": 100,
                        "percent_covered": 85.0,
                        "covered_branches": 40,
                        "num_branches": 50,
                        "percent_covered_display": "85%",
                    }
                },
                "src/chat/session.py": {
                    "summary": {
                        "covered_lines": 70,
                        "num_statements": 100,
                        "percent_covered": 70.0,
                        "covered_branches": 30,
                        "num_branches": 50,
                        "percent_covered_display": "70%",
                    }
                },
            },
        }

        modules = parse_coverage_json(coverage_data)

        assert len(modules) == 2
        auth = next(m for m in modules if m["module"] == "src/multi_tenant/auth.py")
        assert auth["line_coverage"] == 85.0
        assert auth["branch_coverage"] == 80.0  # 40/50

    def test_identify_bottom_5_modules(self):
        """TEST-10480: Bottom 5 modules by coverage identified."""
        from src.quality_metrics.coverage_tracking import get_bottom_modules

        modules = [
            {"module": f"src/mod_{i}.py", "line_coverage": 50 + i * 5}
            for i in range(10)
        ]

        bottom = get_bottom_modules(modules, n=5)
        assert len(bottom) == 5
        assert bottom[0]["line_coverage"] == 50  # Lowest first


class TestCoverageDelta:
    """SPEC-1844: Coverage delta per session."""

    def test_positive_delta_detected(self):
        """Coverage going up produces positive delta."""
        from src.quality_metrics.coverage_tracking import compute_coverage_delta

        previous = {"global_line_coverage": 73.0}
        current = {"global_line_coverage": 75.0}

        delta = compute_coverage_delta(previous, current)
        assert delta == 2.0

    def test_negative_delta_detected(self):
        """Coverage going down produces negative delta."""
        from src.quality_metrics.coverage_tracking import compute_coverage_delta

        previous = {"global_line_coverage": 75.0}
        current = {"global_line_coverage": 73.0}

        delta = compute_coverage_delta(previous, current)
        assert delta == -2.0

    def test_ci_fails_on_gt_2_percent_module_drop(self):
        """TEST-10479: CI fails if module drops >2% below previous."""
        from src.quality_metrics.coverage_tracking import check_module_regression

        previous_modules = [
            {"module": "src/multi_tenant/auth.py", "line_coverage": 85.0},
        ]
        current_modules = [
            {"module": "src/multi_tenant/auth.py", "line_coverage": 82.0},  # 3% drop
        ]

        regressions = check_module_regression(previous_modules, current_modules, threshold=2.0)
        assert len(regressions) == 1
        assert regressions[0]["module"] == "src/multi_tenant/auth.py"
        assert regressions[0]["drop"] == 3.0
