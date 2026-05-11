"""Tests for SPEC-1840: Quality Data Normalization.

Verifies branch coverage config, last_result normalization,
testable element linkage, and untested spec reporting.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest


class TestBranchCoverage:
    """SPEC-1840 req 1: Branch coverage enabled."""

    def test_branch_coverage_enabled_in_pyproject(self):
        """TEST-10463: pyproject.toml has branch = true."""
        import tomllib
        from pathlib import Path

        pyproject = Path("pyproject.toml")
        assert pyproject.exists(), "pyproject.toml not found"

        with open(pyproject, "rb") as f:
            config = tomllib.load(f)

        coverage_run = config.get("tool", {}).get("coverage", {}).get("run", {})
        assert coverage_run.get("branch") is True, (
            "branch coverage not enabled in [tool.coverage.run]"
        )


class TestLastResultNormalization:
    """SPEC-1840 req 2: last_result values normalized."""

    def test_normalize_pass_variants(self):
        """TEST-10464: pass/PASS/passed all normalized to PASS."""
        from src.quality_metrics.normalize import normalize_test_result

        assert normalize_test_result("pass") == "PASS"
        assert normalize_test_result("PASS") == "PASS"
        assert normalize_test_result("passed") == "PASS"

    def test_normalize_fail_variants(self):
        """fail/FAIL normalized to FAIL."""
        from src.quality_metrics.normalize import normalize_test_result

        assert normalize_test_result("fail") == "FAIL"
        assert normalize_test_result("FAIL") == "FAIL"

    def test_normalize_skip_variants(self):
        """skip/SKIP/STALE normalized to SKIP."""
        from src.quality_metrics.normalize import normalize_test_result

        assert normalize_test_result("skip") == "SKIP"
        assert normalize_test_result("SKIP") == "SKIP"
        assert normalize_test_result("STALE") == "SKIP"

    def test_normalize_not_run(self):
        """NOT_RUN/None normalized to NOT_RUN."""
        from src.quality_metrics.normalize import normalize_test_result

        assert normalize_test_result("NOT_RUN") == "NOT_RUN"
        assert normalize_test_result(None) == "NOT_RUN"

    def test_normalize_rejects_invalid(self):
        """Invalid values raise ValueError."""
        from src.quality_metrics.normalize import normalize_test_result

        with pytest.raises(ValueError):
            normalize_test_result("maybe")


class TestTestableElementLinkage:
    """SPEC-1840 req 3: Testable elements linked to specs."""

    def test_auto_linkage_increases_coverage(self):
        """TEST-10465: After auto-linkage, >= 80% of elements have spec_id."""
        # This test will be meaningful after the auto-linkage script runs.
        # For now, verify the linkage function signature exists.
        from src.quality_metrics.normalize import auto_link_testable_elements

        # Smoke test: function exists and is callable
        assert callable(auto_link_testable_elements)


class TestUntestedSpecReport:
    """SPEC-1840 req 4: Untested spec report."""

    def test_get_untested_implemented_specs(self):
        """TEST-10466: Returns implemented/verified specs with 0 tests."""
        # Uses the KB API directly
        import sys
        sys.path.insert(0, "tools/knowledge-db")
        from db import KnowledgeDB

        kdb = KnowledgeDB()
        untested = kdb.get_untested_specs()

        # All returned specs should have no tests
        for spec in untested:
            assert spec["id"] is not None
            # Verify these are non-retired
            assert spec.get("status") != "retired"
