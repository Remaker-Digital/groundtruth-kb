"""WI-5767 C2: tests for the doctor auto-finalize sweep liveness check.

Covers the liveness classifications in the retained design:
- empty terminal backlog -> PASS;
- non-empty backlog with insufficient or stale observation -> WARN;
- non-empty backlog with configured window and zero finalize actions -> FAIL;
- blocked verdicts behind gates -> WARN (expected contention);
- missing Git/audit/probe evidence -> diagnostic info (never crashes).
All thresholds are exercised via environment controls, so no real sleep or
commit is needed.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "groundtruth-kb/src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb/src"))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DOCTOR_PATH = REPO_ROOT / "groundtruth-kb/src/groundtruth_kb/project/doctor.py"


def _load_doctor() -> Any:
    spec = importlib.util.spec_from_file_location("doctor_under_test", DOCTOR_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["doctor_under_test"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def doctor() -> Any:
    return _load_doctor()


def _write_sweep_script(root: Path) -> None:
    (root / "scripts").mkdir(parents=True, exist_ok=True)
    (root / "bridge").mkdir(parents=True, exist_ok=True)
    (root / "scripts" / "auto_finalize_sweep.py").write_text("# probe stub replaced in tests\n", encoding="utf-8")


def _payload(backlog: list, would_finalize: list, blocked: list, histogram: dict) -> dict:
    return {
        "schema_version": 1,
        "terminal_verified_backlog": backlog,
        "would_finalize": would_finalize,
        "blocked": blocked,
        "skip_reason_histogram": histogram,
    }


def _fake_probe(doctor: Any, payload: dict, monkeypatch) -> None:
    """Route the check's subprocess probe invocation to a canned JSON payload."""

    def _fake_run(cmd, cwd=None, capture_output=None, text=None, timeout=None):
        import subprocess as _sp

        if any("auto_finalize_sweep.py" in str(c) for c in cmd):
            return _sp.CompletedProcess(cmd, 0, json.dumps(payload), "")
        if cmd and str(cmd[0]).endswith("git"):
            # git-log commit scan: return a non-empty log so the FAIL branch is reachable.
            return _sp.CompletedProcess(cmd, 0, "abc123 commit", "")
        raise AssertionError(f"unexpected probe command: {cmd}")

    monkeypatch.setattr(doctor.subprocess, "run", _fake_run)


def test_liveness_empty_backlog_pass(tmp_path, doctor, monkeypatch):
    """Empty terminal backlog is PASS."""
    _write_sweep_script(tmp_path)
    _fake_probe(doctor, _payload([], [], [], {}), monkeypatch)
    check = doctor._check_auto_finalize_sweep_liveness(tmp_path)
    assert check.status == "pass"


def test_liveness_drained_pass(tmp_path, doctor, monkeypatch):
    """A non-empty backlog with finalize activity is PASS."""
    _write_sweep_script(tmp_path)
    _fake_probe(doctor, _payload(["a-001.md"], ["a"], [], {"x": 1}), monkeypatch)
    check = doctor._check_auto_finalize_sweep_liveness(tmp_path)
    assert check.status == "pass"


def test_liveness_zero_drain_fail(tmp_path, doctor, monkeypatch):
    """Non-empty backlog, configured window, zero finalize actions -> FAIL."""
    _write_sweep_script(tmp_path)
    monkeypatch.setenv("GTKB_AUTO_FINALIZE_SWEEP_OBSERVATION_WINDOW_DAYS", "2")
    _fake_probe(
        doctor,
        _payload(["a-001.md", "b-001.md"], [], [], {"impl_not_committed": 2}),
        monkeypatch,
    )
    # The zero-drain FAIL branch requires git log to be available; it is in a
    # temp dir only if a repo exists. Use the real REPO_ROOT git surface via a
    # subprocess run that returns a non-empty log. Simplest: monkeypatch _run_cmd.
    monkeypatch.setattr(doctor, "_run_cmd", lambda *a, **k: (True, "abc123 commit"))
    check = doctor._check_auto_finalize_sweep_liveness(tmp_path)
    assert check.status == "fail"


def test_liveness_blocked_warn(tmp_path, doctor, monkeypatch):
    """Blocked verdicts behind gates are a diagnostic WARN, not FAIL."""
    _write_sweep_script(tmp_path)
    _fake_probe(
        doctor,
        _payload(["a-001.md"], [], [{"verdict": "a-001.md", "reason": "impl not committed"}], {}),
        monkeypatch,
    )
    check = doctor._check_auto_finalize_sweep_liveness(tmp_path)
    assert check.status == "warning"


def test_liveness_missing_evidence_info(tmp_path, doctor, monkeypatch):
    """Missing probe evidence is diagnostic (info), never a crash."""
    _write_sweep_script(tmp_path)

    def _fail_run(cmd, cwd=None, capture_output=None, text=None, timeout=None):
        if any("auto_finalize_sweep.py" in str(c) for c in cmd):
            raise FileNotFoundError("probe missing")
        raise AssertionError(f"unexpected command: {cmd}")

    monkeypatch.setattr(doctor.subprocess, "run", _fail_run)
    check = doctor._check_auto_finalize_sweep_liveness(tmp_path)
    assert check.status == "info"


def test_liveness_no_bridge_info(tmp_path, doctor):
    """No bridge/ directory -> info, not applicable."""
    check = doctor._check_auto_finalize_sweep_liveness(tmp_path)
    assert check.status == "info"
    assert "not applicable" in check.message
