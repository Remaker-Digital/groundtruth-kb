"""Tests for drift hook remediation text (GFR Slice D Finding 2.5).

Work item: WI-5646 (TEST-11691).
Governing: DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001,
DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-FILE-BRIDGE-AUTHORITY-001.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_dev_environment_inventory_drift.py"

spec = importlib.util.spec_from_file_location("check_dev_environment_inventory_drift", SCRIPT_PATH)
assert spec is not None
drift = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["check_dev_environment_inventory_drift"] = drift
spec.loader.exec_module(drift)


class TestDriftRemediationText:
    """Finding 2.5: render_summary should include remediation hint when drift is material."""

    def test_remediation_text_present_when_drift_material(self) -> None:
        result = {
            "status": "fail",
            "outcome": "material_drift",
            "material_inventory_drift": True,
            "changed_paths": [],
            "protected_changes": [],
            "diff_keys": ["foo"],
            "warnings": [],
            "review_evidence_present": False,
            "allow_review_evidence": False,
            "registry": "test",
            "inventory": "test",
            "blocking": [],
        }
        text = drift.render_summary(result)
        assert "Remediation:" in text
        assert "collect_dev_environment_inventory" in text

    def test_remediation_text_absent_when_no_drift(self) -> None:
        result = {
            "status": "pass",
            "outcome": "clean",
            "material_inventory_drift": False,
            "changed_paths": [],
            "protected_changes": [],
            "diff_keys": [],
            "warnings": [],
            "review_evidence_present": False,
            "allow_review_evidence": False,
            "registry": "test",
            "inventory": "test",
            "blocking": [],
        }
        text = drift.render_summary(result)
        assert "Remediation:" not in text
