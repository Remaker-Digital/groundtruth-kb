# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""--diagnose CLI flag for cross-harness trigger.

Authority: bridge `gtkb-cross-harness-trigger-windows-rename-race-001` GO at
`-004` (REVISED-1). IP-2 of the proposal: structured liveness summary
reporting failure distribution by error class (NOT collapsed).

Specs:
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 v2 (diagnose makes failures
  visible rather than silently accepted).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import cross_harness_bridge_trigger as cht  # noqa: E402


def _seed_state(state_dir: Path) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "recipients": {
            "codex": {
                "last_dispatched_signature": "abc12345abc12345",
                "last_result": "no_pending",
                "pending_count": 0,
                "selected_count": 0,
                "signature": "def67890def67890",
                "updated_at": "2026-05-10T12:00:00+00:00",
            },
            "prime": {
                "last_dispatched_signature": "111aaa111aaa111a",
                "last_result": "counterpart_active_session_present",
                "pending_count": 36,
                "selected_count": 2,
                "signature": "111aaa111aaa111a",
                "updated_at": "2026-05-10T12:00:00+00:00",
            },
        },
        "schema_version": 1,
        "updated_at": "2026-05-10T12:00:00+00:00",
    }
    (state_dir / "dispatch-state.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _seed_failures(state_dir: Path) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    failures = [
        {
            "error_message": "[WinError 32] sharing violation",
            "error_type": "PermissionError",
            "ts": "2026-05-09T22:20:18+00:00",
        },
        {
            "error_message": "[WinError 32] sharing violation",
            "error_type": "PermissionError",
            "ts": "2026-05-09T21:00:00+00:00",
        },
        {
            "error_message": "[WinError 5] access denied",
            "error_type": "PermissionError",
            "ts": "2026-05-09T18:05:12+00:00",
        },
        {
            "error_message": "[WinError 2] file not found",
            "error_type": "FileNotFoundError",
            "ts": "2026-05-09T21:23:24+00:00",
        },
        {
            "error_message": "Permission denied: 'dispatch-state.json.tmp'",
            "error_type": "PermissionError",
            "ts": "2026-05-09T17:32:41+00:00",
        },
    ]
    path = state_dir / "dispatch-failures.jsonl"
    path.write_text("\n".join(json.dumps(f) for f in failures) + "\n", encoding="utf-8")


def _seed_idle_state(state_dir: Path) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "recipients": {
            "prime-builder": {
                "last_dispatched_signature": "abc12345abc12345",
                "last_result": "no_actionable_change",
                "pending_count": 0,
                "selected_count": 0,
                "signature": "abc12345abc12345",
                "updated_at": "2026-06-23T00:00:00+00:00",
            },
            "loyal-opposition": {
                "last_dispatched_signature": "def67890def67890",
                "last_result": "no_actionable_change",
                "pending_count": 0,
                "selected_count": 0,
                "signature": "def67890def67890",
                "updated_at": "2026-06-23T00:00:00+00:00",
            },
        },
        "schema_version": 1,
        "updated_at": "2026-06-23T00:00:00+00:00",
    }
    (state_dir / "dispatch-state.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_heartbeat(project_root: Path, content: str) -> Path:
    path = project_root / ".gtkb-state" / "ops" / "storm-watchdog-heartbeat.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _diagnose_with_project_root(
    state_dir: Path,
    project_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> str:
    monkeypatch.setattr(cht, "_resolve_project_root", lambda _explicit=None: project_root)
    return cht._emit_diagnose_summary(state_dir)


def test_diagnose_emits_expected_sections(tmp_path: Path) -> None:
    state_dir = tmp_path / "state"
    _seed_state(state_dir)
    output = cht._emit_diagnose_summary(state_dir)
    assert "== Trigger infrastructure ==" in output
    assert "== Dispatch state ==" in output
    assert "== Per-recipient state ==" in output
    assert "== Recent failures ==" in output
    assert "== Liveness ==" in output
    assert "== Overall ==" in output
    assert "suppressed (target active session detected; by design)" in output


def test_diagnose_classifies_target_active_session_result(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state_dir = tmp_path / "state"
    _seed_state(state_dir)
    state_path = state_dir / "dispatch-state.json"
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    payload["recipients"]["prime"]["last_result"] = "target_active_session_present"
    state_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    monkeypatch.setattr(
        cht,
        "_read_role_assignments",
        lambda *a, **k: {
            "harnesses": {
                "C": {"status": "active", "role": ["prime-builder"]},
                "D": {"status": "active", "role": ["loyal-opposition"]},
            }
        },
    )
    output = cht._emit_diagnose_summary(state_dir)

    assert "suppressed (target active session detected; by design)" in output
    assert "HEALTHY" in output
    assert "DEGRADED" not in output


def test_diagnose_worker_liveness_absent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    state_dir = tmp_path / "state"
    _seed_idle_state(state_dir)

    output = _diagnose_with_project_root(state_dir, project_root, monkeypatch)

    assert "== Worker process-family liveness ==" in output
    assert "Heartbeat ABSENT" in output


def test_diagnose_worker_liveness_present(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    _write_heartbeat(
        project_root, "2026-06-23T00:00:00+00:00 codex=3 family=7 threshold=15 noncodex=4 noncodexThreshold=10\n"
    )
    state_dir = tmp_path / "state"
    _seed_idle_state(state_dir)

    output = _diagnose_with_project_root(state_dir, project_root, monkeypatch)

    assert "== Worker process-family liveness ==" in output
    assert "codex=3" in output
    assert "family=7" in output
    assert "threshold=15" in output
    assert "noncodex=4" in output
    assert "noncodexThreshold=10" in output


def test_diagnose_worker_liveness_stale_heartbeat(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    _write_heartbeat(project_root, "2000-01-01T00:00:00+00:00 codex=1 family=2 threshold=15\n")
    state_dir = tmp_path / "state"
    _seed_idle_state(state_dir)

    output = _diagnose_with_project_root(state_dir, project_root, monkeypatch)

    assert "== Worker process-family liveness ==" in output
    assert "[STALE]" in output


def test_diagnose_worker_liveness_unparsable_heartbeat(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    _write_heartbeat(project_root, "NOT-A-DATE codex=5 family=10 threshold=15\n")
    state_dir = tmp_path / "state"
    _seed_idle_state(state_dir)

    output = _diagnose_with_project_root(state_dir, project_root, monkeypatch)

    assert "== Worker process-family liveness ==" in output
    assert "Heartbeat PARSE ERROR" in output
    assert "NOT-A-DATE" in output


def test_diagnose_worker_liveness_false_idle_warning(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    _write_heartbeat(project_root, "2026-06-23T00:00:00+00:00 codex=0 family=5 threshold=15\n")
    state_dir = tmp_path / "state"
    _seed_idle_state(state_dir)

    output = _diagnose_with_project_root(state_dir, project_root, monkeypatch)

    assert "WARNING" in output
    assert "dispatch state appears idle but worker process families are active" in output


def test_diagnose_does_not_dispatch_or_modify_state(tmp_path: Path) -> None:
    state_dir = tmp_path / "state"
    _seed_state(state_dir)
    state_path = state_dir / "dispatch-state.json"
    pre_content = state_path.read_text(encoding="utf-8")
    pre_mtime = state_path.stat().st_mtime

    output = cht._emit_diagnose_summary(state_dir)
    assert isinstance(output, str)

    post_content = state_path.read_text(encoding="utf-8")
    post_mtime = state_path.stat().st_mtime
    assert pre_content == post_content, "State content must not change"
    assert pre_mtime == post_mtime, "State mtime must not change"
    # No orphan temps created either.
    assert not list(state_dir.glob("*.tmp"))


def test_diagnose_handles_missing_state_file_gracefully(tmp_path: Path) -> None:
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    # No dispatch-state.json seeded.
    output = cht._emit_diagnose_summary(state_dir)
    assert "ABSENT" in output
    assert "DEGRADED" in output


def test_diagnose_reports_failure_distribution_not_collapsed(tmp_path: Path) -> None:
    """Per Codex F1 on -002: failures must NOT be collapsed to one error type."""
    state_dir = tmp_path / "state"
    _seed_state(state_dir)
    _seed_failures(state_dir)
    output = cht._emit_diagnose_summary(state_dir)

    # All four classes from the seed must appear with separate counts.
    assert "WinError 32 (sharing violation): 2" in output
    assert "WinError 5 (access denied): 1" in output
    assert "WinError 2 (file not found): 1" in output
    assert "temp-path permission denied: 1" in output
    assert "Total in dispatch-failures.jsonl: 5" in output


def test_diagnose_recent_failures_excludes_suppressions(tmp_path: Path) -> None:
    """WI-4396: expected lease/contention suppressions routed through the shared
    writer land in dispatch-suppressions.jsonl, so the "Recent failures" view
    counts only real, actionable failures. The new "Expected suppressions"
    section reports the suppression count separately."""
    state_dir = tmp_path / "state"
    _seed_state(state_dir)

    # Seed a mix THROUGH the shared writer so routing applies (not by writing the
    # files directly, which would bypass the fix under test).
    cht._record_dispatch_failure(
        state_dir,
        {"ts": "2026-06-14T10:00:00+00:00", "reason": "work_intent_already_held", "launched": False},
    )
    cht._record_dispatch_failure(
        state_dir,
        {"ts": "2026-06-14T10:01:00+00:00", "reason": "work_intent_already_held", "launched": False},
    )
    cht._record_dispatch_failure(
        state_dir,
        {
            "ts": "2026-06-14T10:02:00+00:00",
            "reason": "implementation_authorization_packet_failed",
            "error_message": "[WinError 5] access denied",
            "error_type": "PermissionError",
            "launched": False,
        },
    )

    output = cht._emit_diagnose_summary(state_dir)

    # Only the one real failure is counted in the failures distribution.
    assert "Total in dispatch-failures.jsonl: 1" in output
    # The two expected suppressions are surfaced in their own section.
    assert "== Expected suppressions ==" in output
    assert "Total in dispatch-suppressions.jsonl: 2" in output
    assert "work_intent_already_held: 2" in output
