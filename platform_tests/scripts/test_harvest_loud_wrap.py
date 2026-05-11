"""Tests for Phase 7 loud-wrap rollout in harvest_session_deliberations.py.

Covers the required verification (per bridge/gtkb-da-harvest-coverage-implementation-004.md
§Phase 7 test surface):
    - Simulated non-zero exit → ALARM
    - Simulated new warning (not in baseline) → ALARM
    - Simulated below-baseline → OK
    - Silent-mode (default, loud=False) → always OK even with warnings

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "harvest_session_deliberations.py"


def _load_script():
    spec = importlib.util.spec_from_file_location("harvest_session_deliberations", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["harvest_session_deliberations"] = module
    spec.loader.exec_module(module)
    return module


hsd = _load_script()


# ---------------------------------------------------------------------------
# Baseline load
# ---------------------------------------------------------------------------


class TestLoadWarningBaseline:
    def test_missing_file_returns_empty_baseline(self, tmp_path: Path) -> None:
        baseline = hsd.load_warning_baseline(tmp_path / "does-not-exist.json")
        assert baseline["warning_hashes"] == []
        assert baseline["version"] == 1

    def test_valid_file_roundtrips(self, tmp_path: Path) -> None:
        path = tmp_path / "baseline.json"
        payload = {
            "version": 1,
            "established_at": "2026-04-17T00:00:00Z",
            "warning_hashes": ["aaaabbbbccccdddd", "eeeeffffaaaa0000"],
        }
        path.write_text(json.dumps(payload), encoding="utf-8")
        loaded = hsd.load_warning_baseline(path)
        assert loaded["warning_hashes"] == ["aaaabbbbccccdddd", "eeeeffffaaaa0000"]

    def test_malformed_json_returns_empty_baseline(self, tmp_path: Path) -> None:
        path = tmp_path / "baseline.json"
        path.write_text("{not valid json", encoding="utf-8")
        baseline = hsd.load_warning_baseline(path)
        assert baseline["warning_hashes"] == []

    def test_non_dict_root_returns_empty_baseline(self, tmp_path: Path) -> None:
        path = tmp_path / "baseline.json"
        path.write_text("[1,2,3]", encoding="utf-8")
        baseline = hsd.load_warning_baseline(path)
        assert baseline["warning_hashes"] == []


# ---------------------------------------------------------------------------
# Verdict computation
# ---------------------------------------------------------------------------


class TestComputeWrapVerdict:
    def test_silent_mode_always_ok(self) -> None:
        """loud=False → OK regardless of state (v1 default)."""
        summary = {"exit_status": "error", "warnings": ["unknown warning"]}
        baseline = {"warning_hashes": []}
        verdict, reasons = hsd.compute_wrap_verdict(summary, baseline, loud=False)
        assert verdict == "OK"
        assert reasons == []

    def test_loud_ok_on_clean_run(self) -> None:
        """loud=True + clean exit + no warnings → OK."""
        summary = {"exit_status": "ok", "warnings": []}
        baseline = {"warning_hashes": []}
        verdict, reasons = hsd.compute_wrap_verdict(summary, baseline, loud=True)
        assert verdict == "OK"
        assert reasons == []

    def test_loud_ok_when_warnings_within_baseline(self) -> None:
        """loud=True + warnings all present in baseline → OK."""
        warnings = ["A", "B", "C"]
        hashes = [hsd._hash_warning(w) for w in warnings]
        summary = {"exit_status": "ok", "warnings": warnings}
        baseline = {"warning_hashes": hashes}
        verdict, reasons = hsd.compute_wrap_verdict(summary, baseline, loud=True)
        assert verdict == "OK"
        assert reasons == []

    def test_loud_alarm_on_nonzero_exit(self) -> None:
        """loud=True + exit_status != ok → ALARM."""
        summary = {"exit_status": "error", "warnings": []}
        baseline = {"warning_hashes": []}
        verdict, reasons = hsd.compute_wrap_verdict(summary, baseline, loud=True)
        assert verdict == "ALARM"
        assert any("exit_status" in r for r in reasons)

    def test_loud_alarm_on_new_warning(self) -> None:
        """loud=True + warning not in baseline → ALARM."""
        summary = {
            "exit_status": "ok",
            "warnings": ["known warning", "NOVEL WARNING THAT WAS NOT IN BASELINE"],
        }
        baseline = {"warning_hashes": [hsd._hash_warning("known warning")]}
        verdict, reasons = hsd.compute_wrap_verdict(summary, baseline, loud=True)
        assert verdict == "ALARM"
        assert any("warning" in r for r in reasons)

    def test_loud_alarm_combines_reasons(self) -> None:
        """Both exit error AND new warning → both reasons present."""
        summary = {"exit_status": "error", "warnings": ["brand new"]}
        baseline = {"warning_hashes": []}
        verdict, reasons = hsd.compute_wrap_verdict(summary, baseline, loud=True)
        assert verdict == "ALARM"
        assert len(reasons) == 2
        assert any("exit_status" in r for r in reasons)
        assert any("warning" in r for r in reasons)


# ---------------------------------------------------------------------------
# Hash stability
# ---------------------------------------------------------------------------


class TestHashStability:
    def test_hash_deterministic(self) -> None:
        assert hsd._hash_warning("abc") == hsd._hash_warning("abc")

    def test_hash_different_for_different_strings(self) -> None:
        assert hsd._hash_warning("abc") != hsd._hash_warning("abd")

    def test_hash_length_16(self) -> None:
        assert len(hsd._hash_warning("anything")) == 16
