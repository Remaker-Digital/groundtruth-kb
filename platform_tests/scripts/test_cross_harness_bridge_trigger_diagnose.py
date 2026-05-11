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
    (state_dir / "dispatch-state.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
    )


def _seed_failures(state_dir: Path) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    failures = [
        {"error_message": "[WinError 32] sharing violation", "error_type": "PermissionError", "ts": "2026-05-09T22:20:18+00:00"},
        {"error_message": "[WinError 32] sharing violation", "error_type": "PermissionError", "ts": "2026-05-09T21:00:00+00:00"},
        {"error_message": "[WinError 5] access denied", "error_type": "PermissionError", "ts": "2026-05-09T18:05:12+00:00"},
        {"error_message": "[WinError 2] file not found", "error_type": "FileNotFoundError", "ts": "2026-05-09T21:23:24+00:00"},
        {"error_message": "Permission denied: 'dispatch-state.json.tmp'", "error_type": "PermissionError", "ts": "2026-05-09T17:32:41+00:00"},
    ]
    path = state_dir / "dispatch-failures.jsonl"
    path.write_text("\n".join(json.dumps(f) for f in failures) + "\n", encoding="utf-8")


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
