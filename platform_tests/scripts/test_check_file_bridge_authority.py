"""Focused executable coverage for the WI-5193 file-bridge authority checker.

Asserts each of the six ``GOV-FILE-BRIDGE-AUTHORITY-001`` v3 executable
assertions (``FILE-BRIDGE-AUTH-A1``..``A6``) via
``scripts/check_file_bridge_authority.py``, plus a fail-closed ``A5`` case and
an anti-regression ``A3`` case for ``bridge/INDEX.md``. Composes with the
existing bridge state-report and compliance-gate tests.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_file_bridge_authority.py"
PACKAGE_SRC = REPO_ROOT / "groundtruth-kb" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))


@pytest.fixture(scope="module")
def checker():
    """Load the canonical checker module once for the module-scoped tests."""
    spec = importlib.util.spec_from_file_location("check_file_bridge_authority", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _assertion_report(checker, root: Path) -> dict:
    report = checker.audit_file_bridge_authority(root)
    assert report["schema_version"] == 1
    return {item["id"]: item for item in report["assertions"]}


def test_full_audit_passes_all_six_assertions(checker):
    """A1..A6 all present and PASS on the current tree."""
    by_id = _assertion_report(checker, REPO_ROOT)
    assert set(by_id) == {
        "FILE-BRIDGE-AUTH-A1",
        "FILE-BRIDGE-AUTH-A2",
        "FILE-BRIDGE-AUTH-A3",
        "FILE-BRIDGE-AUTH-A4",
        "FILE-BRIDGE-AUTH-A5",
        "FILE-BRIDGE-AUTH-A6",
    }
    for item in by_id.values():
        assert item["status"] == "PASS"


def test_a1_numbered_files_authoritative_chain(checker):
    """A1: status is derived from the numbered append-only file chain."""
    a1 = _assertion_report(checker, REPO_ROOT)["FILE-BRIDGE-AUTH-A1"]
    assert a1["status"] == "PASS"
    ids = {sub["id"] for sub in a1["subassertions"]}
    assert ids == {"numbered-files-authoritative-chain", "versioned-reader-only", "append-only-version-order"}


def test_a2_tafe_dispatch_runtime_authority(checker):
    """A2: runtime coordination derives from TAFE/dispatcher state, not Markdown."""
    a2 = _assertion_report(checker, REPO_ROOT)["FILE-BRIDGE-AUTH-A2"]
    assert a2["status"] == "PASS"
    ids = {sub["id"] for sub in a2["subassertions"]}
    assert ids == {"tafe-dispatch-runtime-authority", "no-markdown-runtime-inference", "dual-surface-conflict-denied"}


def test_a3_bridge_index_absent_and_anti_regression(checker):
    """A3: bridge/INDEX.md is absent and no writer/aggregate authority exists."""
    a3 = _assertion_report(checker, REPO_ROOT)["FILE-BRIDGE-AUTH-A3"]
    assert a3["status"] == "PASS"
    # Anti-regression guard: bridge/INDEX.md must not exist on the live tree.
    assert not (REPO_ROOT / "bridge" / "INDEX.md").exists()
    ids = {sub["id"] for sub in a3["subassertions"]}
    assert ids == {"bridge-index-absent", "bridge-index-no-writer", "bridge-index-reference-classified"}


def test_a3_anti_regression_detects_index_writer(checker, tmp_path: Path):
    """A3 anti-regression: a hypothetical INDEX.md writer is flagged as a violation."""
    (tmp_path / "scripts").mkdir(parents=True)
    (tmp_path / "scripts" / "writer.py").write_text(
        "pathlib.Path('bridge/INDEX.md').write_text('x')\n", encoding="utf-8"
    )
    scan = checker._index_reference_scan(tmp_path)
    assert scan["writers"], "expected the INDEX.md writer to be detected"


def test_a4_projections_context_only(checker):
    """A4: startup/dashboard/report/cache projections are context-only."""
    a4 = _assertion_report(checker, REPO_ROOT)["FILE-BRIDGE-AUTH-A4"]
    assert a4["status"] == "PASS"
    ids = {sub["id"] for sub in a4["subassertions"]}
    assert ids == {
        "startup-projection-context-only",
        "dashboard-report-cache-context-only",
        "fresh-live-read-required",
    }


def test_a5_fail_closed_on_malformed_status(checker):
    """A5 fail-closed: a non-canonical actionable status must be denied."""
    # A synthetic actionable document carrying a malformed (non-canonical) top
    # status must trip the malformed-status-denied sub-assertion.
    bad_item = SimpleNamespace(top_status="BOGUS")
    queue = SimpleNamespace(
        prime_actionable=[bad_item],
        loyal_opposition_actionable=[],
        status_counts={"UNKNOWN": 0},
    )
    snapshot = SimpleNamespace(queue=queue, automation=None)
    scan = {"duplicate_versions": [], "unreadable": []}
    a5 = checker._assert_a5(scan, snapshot)
    by_id = {sub["id"]: sub for sub in a5["subassertions"]}
    assert by_id["malformed-status-denied"]["status"] == "FAIL"
    assert a5["status"] == "FAIL"


def test_a6_lo_repair_authority(checker):
    """A6: LO repair authority is bridge-scoped and preserves history/independence."""
    a6 = _assertion_report(checker, REPO_ROOT)["FILE-BRIDGE-AUTH-A6"]
    assert a6["status"] == "PASS"
    ids = {sub["id"] for sub in a6["subassertions"]}
    assert ids == {"lo-repair-bridge-scope-only", "lo-repair-preserves-history", "lo-repair-no-self-review"}


def test_cli_exit_contract_passes(checker):
    """The CLI entry point returns 0 when all six assertions pass."""
    assert checker.main(["--project-root", str(REPO_ROOT)]) == 0
