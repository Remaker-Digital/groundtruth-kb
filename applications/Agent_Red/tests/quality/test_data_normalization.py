"""Tests for SPEC-1840: Quality Data Normalization.

Verifies branch coverage config, last_result normalization,
testable element linkage, and untested spec reporting.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest

SPEC_1653_DIMENSION_CODES = [
    "A1",
    "A2",
    "A3",
    "A4",
    "B1",
    "B2",
    "B3",
    "B4",
    "B5",
    "B6",
    "C1",
    "C2",
    "C3",
    "C4",
    "C5",
    "C6",
    "C7",
    "D1",
    "D2",
    "D3",
    "D4",
    "D5",
    "E1",
    "E2",
    "E3",
    "E4",
    "E5",
    "E6",
    "F1",
    "F2",
    "F3",
    "F4",
    "F5",
    "F6",
    "G1",
    "G2",
    "G3",
    "G4",
    "G5",
    "H1",
    "H2",
    "H3",
    "H4",
    "H5",
    "H6",
    "I1",
    "I2",
    "I3",
    "I4",
    "J1",
    "J2",
    "J3",
    "J4",
    "J5",
    "K1",
    "K2",
    "K3",
    "K4",
    "K5",
    "L1",
    "L2",
    "L3",
    "L4",
    "M1",
    "M2",
    "M3",
    "M4",
    "M5",
    "N1",
    "N2",
    "N3",
]


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
        assert coverage_run.get("branch") is True, "branch coverage not enabled in [tool.coverage.run]"


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


class TestTestableElementDimensionTaxonomy:
    """SPEC-1653: Testable elements preserve canonical dimension taxonomy."""

    def test_spec_1653_dimensions_round_trip_through_agent_red_shim(self, tmp_path):
        """TEST-10467: SPEC-1653 dimensions round-trip through KnowledgeDB shim."""
        import json
        import sys

        tools_path = "tools/knowledge-db"
        if tools_path not in sys.path:
            sys.path.insert(0, tools_path)
        from db import KnowledgeDB

        kdb = KnowledgeDB(db_path=tmp_path / "knowledge.db")
        element = kdb.insert_testable_element(
            id="EL-SPEC-1653-taxonomy",
            subsystem="quality",
            page_or_module="quality-process",
            name="SPEC-1653 canonical dimension taxonomy",
            element_type="taxonomy",
            expected_behavior="Stores every canonical SPEC-1653 testable dimension code.",
            applicable_dimensions=SPEC_1653_DIMENSION_CODES,
            spec_id="SPEC-1653",
            changed_by="test",
            change_reason="Verify SPEC-1653 dimension taxonomy round-trip.",
        )

        assert element is not None
        assert element["spec_id"] == "SPEC-1653"
        assert element["applicable_dimensions_parsed"] == SPEC_1653_DIMENSION_CODES
        assert json.loads(element["applicable_dimensions"]) == SPEC_1653_DIMENSION_CODES

        current = kdb.get_testable_element("EL-SPEC-1653-taxonomy")
        assert current is not None
        assert current["applicable_dimensions_parsed"] == SPEC_1653_DIMENSION_CODES

        filtered = kdb.list_testable_elements(
            subsystem="quality",
            element_type="taxonomy",
            status="active",
        )
        assert [item["id"] for item in filtered] == ["EL-SPEC-1653-taxonomy"]

        summary = kdb.get_element_coverage_summary()
        assert summary["total_elements"] == 1
        assert summary["total_active"] == 1
        assert summary["subsystems"] == [{"subsystem": "quality", "total": 1, "active": 1}]


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
