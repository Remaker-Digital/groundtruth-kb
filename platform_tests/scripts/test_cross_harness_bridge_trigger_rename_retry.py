# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Rename-retry semantics for cross-harness trigger state writes.

Authority: bridge `gtkb-cross-harness-trigger-windows-rename-race-001` GO at
`-004` (REVISED-1). IP-1 of the proposal: per-invocation temp paths +
`PermissionError`-only retry with `total_attempts=5` semantics.

Specs:
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 v2 (state-write reliability is
  foundational to the owner-out-of-loop dispatch contract).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import cross_harness_bridge_trigger as cht  # noqa: E402


def test_rename_succeeds_on_first_attempt(tmp_path: Path) -> None:
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.write_text("payload", encoding="utf-8")
    cht._rename_with_retry(src, dst)
    assert dst.read_text(encoding="utf-8") == "payload"
    assert not src.exists()


def test_rename_retries_permission_error_then_succeeds(tmp_path: Path) -> None:
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.write_text("payload", encoding="utf-8")

    real_replace = Path.replace
    call_count = {"n": 0}

    def flaky_replace(self, target):  # type: ignore[no-redef]
        call_count["n"] += 1
        if call_count["n"] < 3:
            raise PermissionError("WinError 32 simulated sharing violation")
        return real_replace(self, target)

    with patch.object(Path, "replace", flaky_replace):
        cht._rename_with_retry(src, dst, initial_backoff_s=0.001)

    assert dst.read_text(encoding="utf-8") == "payload"
    assert call_count["n"] == 3  # Two failures, third succeeds.


def test_rename_does_not_retry_filenotfounderror(tmp_path: Path) -> None:
    """WinError 2 propagates immediately — different bug class with per-invocation paths."""
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.write_text("payload", encoding="utf-8")

    call_count = {"n": 0}

    def fnf_replace(self, target):  # type: ignore[no-redef]
        call_count["n"] += 1
        raise FileNotFoundError("WinError 2 simulated missing temp")

    with patch.object(Path, "replace", fnf_replace), pytest.raises(FileNotFoundError):
        cht._rename_with_retry(src, dst, initial_backoff_s=0.001)

    assert call_count["n"] == 1, "FileNotFoundError must NOT be retried"


def test_rename_raises_after_total_attempts_exhausted(tmp_path: Path) -> None:
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.write_text("payload", encoding="utf-8")

    call_count = {"n": 0}

    def always_perm_error(self, target):  # type: ignore[no-redef]
        call_count["n"] += 1
        raise PermissionError("WinError 32 simulated, never recovers")

    with patch.object(Path, "replace", always_perm_error), pytest.raises(PermissionError):
        cht._rename_with_retry(src, dst, total_attempts=5, initial_backoff_s=0.001)

    assert call_count["n"] == 5, "Should exhaust exactly 5 total_attempts"


def test_rename_total_attempts_5_sleeps_4_times(tmp_path: Path) -> None:
    """Timing-semantics regression: total_attempts=5 sleeps after attempts 1-4 only."""
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.write_text("payload", encoding="utf-8")

    sleep_calls: list[float] = []

    def fake_sleep(s: float) -> None:
        sleep_calls.append(s)

    def always_perm_error(self, target):  # type: ignore[no-redef]
        raise PermissionError("WinError 32 simulated")

    with patch.object(cht, "time") as mock_time:
        mock_time.sleep = fake_sleep
        with patch.object(Path, "replace", always_perm_error), pytest.raises(PermissionError):
            cht._rename_with_retry(src, dst, total_attempts=5, initial_backoff_s=0.05)

    # 5 attempts, 4 sleeps before the final raise.
    assert len(sleep_calls) == 4, f"Expected 4 sleeps, got {len(sleep_calls)}: {sleep_calls}"
    # Exponential backoff: 50, 100, 200, 400 ms.
    assert sleep_calls == pytest.approx([0.05, 0.10, 0.20, 0.40], rel=0.001)


def test_write_dispatch_state_uses_per_invocation_temp_path(tmp_path: Path, monkeypatch) -> None:
    """Per-invocation temp paths eliminate shared-temp contention."""
    state_dir = tmp_path / "state"
    captured_temps: list[Path] = []

    real_write_text = Path.write_text

    def capture_write_text(self, *args, **kwargs):
        if str(self).endswith(".tmp"):
            captured_temps.append(self)
        return real_write_text(self, *args, **kwargs)

    with patch.object(Path, "write_text", capture_write_text):
        cht._write_dispatch_state(state_dir, {"a": 1})
        cht._write_dispatch_state(state_dir, {"a": 2})
        cht._write_dispatch_state(state_dir, {"a": 3})

    # Three different per-invocation temp paths — none shared.
    assert len({str(p) for p in captured_temps}) == 3, (
        f"Expected 3 distinct temp paths; got {captured_temps}"
    )
    # Each temp path matches the per-invocation pattern.
    import re
    pattern = re.compile(r"dispatch-state\.json\.\d+-[0-9a-f]{8}\.tmp$")
    for p in captured_temps:
        assert pattern.search(str(p)), f"Temp path doesn't match pattern: {p}"
    # No orphan *.tmp files in state_dir.
    assert not list(state_dir.glob("*.tmp")), "Orphan temp files remain after writes"
    # Final state matches last write.
    final = json.loads((state_dir / "dispatch-state.json").read_text(encoding="utf-8"))
    assert final == {"a": 3}
