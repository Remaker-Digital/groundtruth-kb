# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for soft_reset stale dispatch-runs pruning (WI-4861).

soft_reset must reap stale/orphaned dispatch-runs sidecars (dead-PID or exited
workers) so the live-worker count is accurate after a soft reset, while
preserving genuinely-live workers.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import psutil

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))
for module_name in list(sys.modules):
    if module_name == "groundtruth_kb" or module_name.startswith("groundtruth_kb."):
        del sys.modules[module_name]

from groundtruth_kb.bridge_dispatch_reset import DispatchStateDirs, soft_reset  # noqa: E402

# A never-allocated high PID: dead on both Windows (tasklist no match) and POSIX
# (os.kill -> ProcessLookupError).
_DEAD_PID = 999999


def _runs_dir(root: Path) -> Path:
    runs = root / ".gtkb-state" / "bridge-poller" / "dispatch-runs"
    runs.mkdir(parents=True, exist_ok=True)
    return runs


def _current_create_time() -> float:
    return float(psutil.Process(os.getpid()).create_time())


def _write_sidecar(
    runs_dir: Path,
    dispatch_id: str,
    *,
    pid: int,
    exit_code: str | None = None,
    create_time: float | None = None,
) -> None:
    (runs_dir / f"{dispatch_id}.pid").write_text(str(pid), encoding="utf-8")
    if create_time is not None:
        (runs_dir / f"{dispatch_id}.create_time_epoch").write_text(f"{create_time:.6f}", encoding="utf-8")
    if exit_code is not None:
        (runs_dir / f"{dispatch_id}.exit_code").write_text(exit_code, encoding="utf-8")


def test_soft_reset_prunes_dead_pid_dispatch_run(tmp_path: Path) -> None:
    """A dead-PID sidecar with no exit_code is pruned (WI-4861)."""
    runs_dir = _runs_dir(tmp_path)
    _write_sidecar(runs_dir, "dispatch-dead", pid=_DEAD_PID)
    result = soft_reset(DispatchStateDirs.resolve(tmp_path))
    assert result.stale_dispatch_runs_pruned == 1
    assert not (runs_dir / "dispatch-dead.pid").exists()


def test_soft_reset_prunes_exited_dispatch_run(tmp_path: Path) -> None:
    """A worker with an exit_code present is pruned even if its PID is alive."""
    runs_dir = _runs_dir(tmp_path)
    _write_sidecar(runs_dir, "dispatch-exited", pid=os.getpid(), exit_code="0")
    result = soft_reset(DispatchStateDirs.resolve(tmp_path))
    assert result.stale_dispatch_runs_pruned == 1
    assert not (runs_dir / "dispatch-exited.pid").exists()
    assert not (runs_dir / "dispatch-exited.exit_code").exists()


def test_soft_reset_preserves_live_dispatch_run(tmp_path: Path) -> None:
    """A live worker (PID alive, no exit_code) is NOT pruned by a soft reset."""
    runs_dir = _runs_dir(tmp_path)
    _write_sidecar(runs_dir, "dispatch-live", pid=os.getpid(), create_time=_current_create_time())
    result = soft_reset(DispatchStateDirs.resolve(tmp_path))
    assert result.stale_dispatch_runs_pruned == 0
    assert (runs_dir / "dispatch-live.pid").exists()
    assert (runs_dir / "dispatch-live.create_time_epoch").exists()


def test_soft_reset_prunes_live_pid_with_missing_create_time(tmp_path: Path) -> None:
    """A live PID without create-time provenance is stale evidence, not a live worker."""
    runs_dir = _runs_dir(tmp_path)
    _write_sidecar(runs_dir, "dispatch-missing-provenance", pid=os.getpid())
    result = soft_reset(DispatchStateDirs.resolve(tmp_path))
    assert result.stale_dispatch_runs_pruned == 1
    assert not (runs_dir / "dispatch-missing-provenance.pid").exists()


def test_soft_reset_prunes_stdout_stderr_only_dispatch_run(tmp_path: Path) -> None:
    """WI-4893: stdout/stderr-only ghosts are pruned even when no .pid exists."""
    runs_dir = _runs_dir(tmp_path)
    (runs_dir / "dispatch-ghost.stdout.log").write_text("partial", encoding="utf-8")
    (runs_dir / "dispatch-ghost.stderr.log").write_text("", encoding="utf-8")
    result = soft_reset(DispatchStateDirs.resolve(tmp_path))
    assert result.stale_dispatch_runs_pruned == 1
    assert not (runs_dir / "dispatch-ghost.stdout.log").exists()
    assert not (runs_dir / "dispatch-ghost.stderr.log").exists()


def test_soft_reset_does_not_touch_dispatcher_daemon_pid(tmp_path: Path) -> None:
    """The dispatcher daemon pid sidecar is outside dispatch-run pruning scope."""
    _runs_dir(tmp_path)
    daemon_dir = tmp_path / ".gtkb-state" / "dispatcher-daemon"
    daemon_dir.mkdir(parents=True)
    daemon_pid = daemon_dir / "daemon.pid"
    daemon_pid.write_text(str(os.getpid()), encoding="utf-8")
    result = soft_reset(DispatchStateDirs.resolve(tmp_path))
    assert result.stale_dispatch_runs_pruned == 0
    assert daemon_pid.exists()


def test_soft_reset_dry_run_does_not_remove(tmp_path: Path) -> None:
    """dry_run counts the prune but leaves the sidecar on disk."""
    runs_dir = _runs_dir(tmp_path)
    _write_sidecar(runs_dir, "dispatch-dead", pid=_DEAD_PID)
    result = soft_reset(DispatchStateDirs.resolve(tmp_path), dry_run=True)
    assert result.stale_dispatch_runs_pruned == 1
    assert (runs_dir / "dispatch-dead.pid").exists()


def test_soft_reset_clears_recipient_last_result(tmp_path: Path) -> None:
    """soft_reset must clear recipient last_result, pending_count, and selected_count."""
    import json

    poller_dir = tmp_path / ".gtkb-state" / "bridge-poller"
    poller_dir.mkdir(parents=True, exist_ok=True)
    dispatch_state = poller_dir / "dispatch-state.json"
    state_payload = {
        "recipients": {
            "loyal-opposition:F": {
                "circuit_breaker_tripped": True,
                "last_result": "spawn_rate_limited",
                "pending_count": 2,
                "selected_count": 1,
                "failure_count": 3,
                "updated_at": "2026-06-29T07:25:59Z",
            }
        },
        "schema_version": 1,
    }
    dispatch_state.write_text(json.dumps(state_payload), encoding="utf-8")

    result = soft_reset(DispatchStateDirs.resolve(tmp_path))
    assert result.recipients_cleared == 1

    saved = json.loads(dispatch_state.read_text(encoding="utf-8"))
    entry = saved["recipients"]["loyal-opposition:F"]
    assert entry["circuit_breaker_tripped"] is False
    assert entry["last_result"] == "no_pending"
    assert entry["pending_count"] == 0
    assert entry["selected_count"] == 0
    assert entry["failure_count"] == 0
