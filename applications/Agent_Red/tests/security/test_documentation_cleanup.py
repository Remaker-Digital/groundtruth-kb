"""Tests for documentation cleanup (S161 Group 5).

Validates SPEC-1700 (rate-limit procedure), SPEC-1701 (deployment runbook archive),
SPEC-1702 (operations index), SPEC-1703 (master test results).

These tests validate docs/ directory content which is only present
in the git working tree, not in Docker containers.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import pathlib
import re

import pytest


def get_docs_path() -> pathlib.Path:
    """Find the docs directory relative to CWD or the test file itself."""
    for p in [
        pathlib.Path("applications/Agent_Red/docs"),
        pathlib.Path("docs"),
        pathlib.Path(__file__).parents[2] / "docs",
    ]:
        if p.exists() and (p / "operations").exists():
            return p
    return pathlib.Path("docs")


DOCS = get_docs_path()
OPS = DOCS / "operations"
ARCHIVE = DOCS / "archive"


# Skip entire module when running inside the test host container
# (no docs/ directory available)
pytestmark = pytest.mark.skipif(
    not DOCS.exists() or not OPS.exists(),
    reason="docs/ directory not available (container environment)",
)


class TestRateLimitProcedureUpdate:
    """SPEC-1700: rate-limit-test-procedure.md MUST reflect 500 RPM."""

    def test_procedure_exists(self):
        assert (OPS / "rate-limit-test-procedure.md").exists()

    def test_references_500_rpm(self):
        text = (OPS / "rate-limit-test-procedure.md").read_text(encoding="utf-8")
        assert "500" in text, "Procedure must reference current 500 RPM limit"

    def test_no_stale_10_rpm_starter(self):
        text = (OPS / "rate-limit-test-procedure.md").read_text(encoding="utf-8")
        assert "10 rpm" not in text.lower(), "Stale 10 rpm reference must be removed"

    def test_no_stale_50_rpm_professional(self):
        text = (OPS / "rate-limit-test-procedure.md").read_text(encoding="utf-8")
        assert "50 rpm" not in text.lower(), "Stale 50 rpm reference must be removed"


class TestDeploymentRunbookArchive:
    """SPEC-1701: DEPLOYMENT-RUNBOOK.md MUST be archived."""

    def test_runbook_not_in_operations(self):
        assert not (OPS / "DEPLOYMENT-RUNBOOK.md").exists(), (
            "Deprecated runbook must be moved out of active operations folder"
        )

    def test_runbook_in_archive(self):
        assert (ARCHIVE / "DEPLOYMENT-RUNBOOK.md").exists(), "Deprecated runbook must be in docs/archive/"


class TestOperationsIndex:
    """SPEC-1702: docs/operations/INDEX.md MUST exist."""

    def test_index_exists(self):
        assert (OPS / "INDEX.md").exists()

    def test_index_lists_procedures(self):
        text = (OPS / "INDEX.md").read_text(encoding="utf-8")
        assert "rate-limit" in text.lower()
        assert "deployment" in text.lower() or "deploy" in text.lower()

    def test_index_has_status_column(self):
        text = (OPS / "INDEX.md").read_text(encoding="utf-8")
        assert "Status" in text or "status" in text

    def test_index_lists_all_procedure_files(self):
        text = (OPS / "INDEX.md").read_text(encoding="utf-8")
        md_files = [f.name for f in OPS.iterdir() if f.suffix == ".md" and f.name != "INDEX.md"]
        listed = sum(1 for f in md_files if f in text)
        assert listed >= len(md_files) * 0.8, f"INDEX must list at least 80% of ops docs ({listed}/{len(md_files)})"


class TestMasterTestResults:
    """SPEC-1703: MASTER-TEST-EXECUTION-RESULTS must show current counts."""

    def test_results_file_exists(self):
        assert (DOCS / "tests" / "MASTER-TEST-EXECUTION-RESULTS-1.0.md").exists()

    def test_shows_current_test_count(self):
        text = (DOCS / "tests" / "MASTER-TEST-EXECUTION-RESULTS-1.0.md").read_text(encoding="utf-8")
        numbers = [
            int(n.replace(",", ""))
            for n in re.findall(r"[\d,]+", text)
            if n.replace(",", "").isdigit() and int(n.replace(",", "")) > 5000
        ]
        assert any(n >= 6000 for n in numbers), "Master results must show 6000+ total tests (current: 6,171)"

    def test_shows_current_version(self):
        text = (DOCS / "tests" / "MASTER-TEST-EXECUTION-RESULTS-1.0.md").read_text(encoding="utf-8")
        assert "v1.12.0" not in text, "Must not reference stale v1.12.0"

    def test_no_stale_1826_count(self):
        text = (DOCS / "tests" / "MASTER-TEST-EXECUTION-RESULTS-1.0.md").read_text(encoding="utf-8")
        assert "1,826" not in text and "1826" not in text, "Stale 1,826 test count must be updated"
