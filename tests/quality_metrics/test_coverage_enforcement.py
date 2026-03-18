"""Tests for SPEC-1844: Coverage Enforcement and Per-Module Tracking.

Verifies per-module targets, tier classification, coverage display,
and regression detection.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.quality_metrics.coverage_tracking import (
    check_module_targets,
    format_coverage_display,
    get_bottom_modules,
    load_module_targets,
    _classify_module_tier,
    check_module_regression,
    parse_coverage_json,
)


class TestModuleTargets:
    """WI-1487: Per-module coverage targets."""

    def test_targets_file_exists(self):
        """module_coverage_targets.json exists in quality_metrics."""
        path = Path(__file__).parent.parent.parent / "src" / "quality_metrics" / "module_coverage_targets.json"
        assert path.exists()

    def test_targets_has_four_tiers(self):
        targets = load_module_targets()
        assert set(targets["targets"].keys()) == {"critical", "high", "medium", "low"}

    def test_critical_tier_target_highest(self):
        targets = load_module_targets()
        critical = targets["targets"]["critical"]["target_pct"]
        low = targets["targets"]["low"]["target_pct"]
        assert critical > low

    def test_global_target(self):
        targets = load_module_targets()
        assert targets["global"]["target_pct"] == 80
        assert targets["global"]["current_gate_pct"] == 75

    def test_classify_auth_as_critical(self):
        targets = load_module_targets()
        tier, target = _classify_module_tier("src/multi_tenant/auth.py", targets["targets"])
        assert tier == "critical"
        assert target == 85

    def test_classify_superadmin_as_medium(self):
        targets = load_module_targets()
        tier, target = _classify_module_tier("src/multi_tenant/superadmin_api/_alerts.py", targets["targets"])
        assert tier == "medium"

    def test_classify_unknown_as_unclassified(self):
        targets = load_module_targets()
        tier, _ = _classify_module_tier("some/random/module.py", targets["targets"])
        assert tier == "unclassified"


class TestCheckModuleTargets:
    """WI-1487: Check modules against tier targets."""

    def test_detects_below_target(self):
        modules = [
            {"module": "src/multi_tenant/auth.py", "line_coverage": 50.0},
        ]
        targets = load_module_targets()
        violations = check_module_targets(modules, targets)
        assert len(violations) == 1
        assert violations[0]["tier"] == "critical"
        assert violations[0]["below_target"] > 0

    def test_no_violations_when_above_target(self):
        modules = [
            {"module": "src/multi_tenant/auth.py", "line_coverage": 90.0},
        ]
        targets = load_module_targets()
        violations = check_module_targets(modules, targets)
        assert len(violations) == 0


class TestCoverageDisplay:
    """WI-1488: Coverage display at session start."""

    def test_format_bottom_modules(self):
        modules = [
            {"module": "src/a.py", "line_coverage": 40.0},
            {"module": "src/b.py", "line_coverage": 60.0},
            {"module": "src/c.py", "line_coverage": 80.0},
        ]
        output = format_coverage_display(modules, n=2)
        assert "Bottom 2 modules" in output
        assert "src/a.py" in output
        assert "40.0%" in output

    def test_format_with_delta_arrows(self):
        current = [
            {"module": "src/a.py", "line_coverage": 45.0},
            {"module": "src/b.py", "line_coverage": 58.0},
        ]
        previous = [
            {"module": "src/a.py", "line_coverage": 40.0},
            {"module": "src/b.py", "line_coverage": 60.0},
        ]
        output = format_coverage_display(current, previous_modules=previous, n=2)
        assert "^" in output  # src/a.py improved
        assert "v" in output  # src/b.py degraded


class TestCoverageGateRamp:
    """WI-1486: Coverage gate ramp 70→75."""

    def test_pyproject_fail_under_is_75(self):
        """pyproject.toml fail_under should be 75 (first ramp step)."""
        import tomllib
        pyproject = Path(__file__).parent.parent.parent / "pyproject.toml"
        with open(pyproject, "rb") as f:
            config = tomllib.load(f)
        fail_under = config["tool"]["coverage"]["report"]["fail_under"]
        assert fail_under == 75


class TestModuleRegression:
    """Regression detection (existing function)."""

    def test_detects_regression(self):
        prev = [{"module": "src/a.py", "line_coverage": 80.0}]
        curr = [{"module": "src/a.py", "line_coverage": 70.0}]
        regressions = check_module_regression(prev, curr, threshold=2.0)
        assert len(regressions) == 1
        assert regressions[0]["drop"] == 10.0

    def test_no_regression_within_threshold(self):
        prev = [{"module": "src/a.py", "line_coverage": 80.0}]
        curr = [{"module": "src/a.py", "line_coverage": 79.0}]
        regressions = check_module_regression(prev, curr, threshold=2.0)
        assert len(regressions) == 0
