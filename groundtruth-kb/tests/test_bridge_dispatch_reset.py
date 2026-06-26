"""Spec-derived tests for WI-4793 dispatcher reset and drain."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path

from click.testing import CliRunner

from groundtruth_kb.bridge_dispatch_reset import (
    DISPATCH_STATE_FILENAME,
    DRAIN_MARKER_FILENAME,
    KILL_SWITCH_ENV_VAR,
    PROVENANCE_LEDGER_FILENAME,
    QUIESCE_STATE_FILENAME,
    DispatchStateDirs,
    drain,
    hard_reset,
    dispatch_is_draining,
    is_drain_marker_active,
    soft_reset,
)
from groundtruth_kb.cli import main


def _config_args(project_dir: Path) -> list[str]:
    return ["--config", str(project_dir / "groundtruth.toml")]


def _seed_state_dirs(project_dir: Path) -> DispatchStateDirs:
    state_dir = project_dir / ".gtkb-state" / "bridge-poller"
    state_dir.mkdir(parents=True)
    ops = project_dir / ".gtkb-state" / "ops" / "dispatch-provenance"
    ops.mkdir(parents=True)
    (ops / PROVENANCE_LEDGER_FILENAME).write_text("[]", encoding="utf-8")
    (state_dir / "dispatch-failures.jsonl").write_text(json.dumps({"reason": "test"}) + chr(10), encoding="utf-8")
    quality = project_dir / ".gtkb-state" / "ops" / "dispatch-quality.json"
    quality.write_text(json.dumps({"learned": True}), encoding="utf-8")
    dispatch_state = {
        "recipients": {
            "loyal-opposition": {
                "failure_count": 3,
                "circuit_breaker_tripped": True,
                "last_launch": {"pid": 4242},
                "signature": "abc",
                "last_dispatched_signature": "abc",
                "previous_launch_failed_logged_at": "2026-01-01T00:00:00+00:00",
            }
        }
    }
    (state_dir / DISPATCH_STATE_FILENAME).write_text(json.dumps(dispatch_state, indent=2), encoding="utf-8")
    (state_dir / QUIESCE_STATE_FILENAME).write_text(
        json.dumps({"records": {"k": {"quiesce_until": 1}}}, indent=2),
        encoding="utf-8",
    )
    return DispatchStateDirs.resolve(project_dir, state_dir=state_dir)


def _read_dispatch_state(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_soft_reset_clears_transient_preserves_audit(project_dir: Path) -> None:
    state_dirs = _seed_state_dirs(project_dir)
    state_dir = state_dirs.dispatch_dirs[0]
    result = soft_reset(state_dirs)
    assert result.recipients_cleared == 1
    assert result.provenance_ledgers_removed == 1
    recipient = _read_dispatch_state(state_dir / DISPATCH_STATE_FILENAME)["recipients"]["loyal-opposition"]
    assert recipient["failure_count"] == 0
    assert recipient["circuit_breaker_tripped"] is False
    assert "last_launch" not in recipient
    assert recipient["signature"] is None
    quiesce = json.loads((state_dir / QUIESCE_STATE_FILENAME).read_text(encoding="utf-8"))
    assert quiesce["records"] == {}
    assert (state_dir / "dispatch-failures.jsonl").read_text(encoding="utf-8").strip()
    assert not (state_dirs.provenance_dir / PROVENANCE_LEDGER_FILENAME).exists()
    assert (project_dir / ".gtkb-state" / "ops" / "dispatch-quality.json").exists()


def test_hard_reset_is_soft_plus_quality_surface(project_dir: Path) -> None:
    state_dirs = _seed_state_dirs(project_dir)
    result = hard_reset(state_dirs)
    assert result.recipients_cleared == 1
    assert result.quality_surfaces_cleared == 1
    assert not (project_dir / ".gtkb-state" / "ops" / "dispatch-quality.json").exists()


def test_hard_reset_without_confirm_is_refused(runner: CliRunner, project_dir: Path) -> None:
    state_dirs = _seed_state_dirs(project_dir)
    state_dir = state_dirs.dispatch_dirs[0]
    before = (state_dir / DISPATCH_STATE_FILENAME).read_text(encoding="utf-8")
    hard_flag = "--hard"
    result = runner.invoke(
        main,
        [
            *_config_args(project_dir),
            "bridge",
            "dispatch",
            "reset",
            hard_flag,
            "--state-dir",
            str(state_dir),
        ],
    )
    assert result.exit_code != 0
    assert "--confirm" in result.output
    assert (state_dir / DISPATCH_STATE_FILENAME).read_text(encoding="utf-8") == before


# WI4793_DRAIN_KILL_SWITCH_TEST
def test_drain_does_not_assert_kill_switch(project_dir: Path) -> None:
    state_dirs = _seed_state_dirs(project_dir)
    state_dir = state_dirs.dispatch_dirs[0]
    prior = os.environ.pop(KILL_SWITCH_ENV_VAR, None)
    terminated: list[int] = []

    def _terminate(pid: int) -> None:
        terminated.append(pid)

    try:
        result = drain(
            state_dirs,
            timeout_seconds=0.0,
            now_fn=lambda: 0.0,
            terminate_fn=_terminate,
            poll_interval=0.0,
        )
        assert result.drain_markers_written == 1
        assert (state_dir / DRAIN_MARKER_FILENAME).exists() is False
        assert (os.environ.get(KILL_SWITCH_ENV_VAR) == "1") is False
        assert terminated == []
    finally:
        if prior is not None:
            os.environ[KILL_SWITCH_ENV_VAR] = prior


# WI4793_DRAIN_WAIT_TEST
def test_drain_waits_then_terminates_stragglers(project_dir: Path) -> None:
    state_dirs = _seed_state_dirs(project_dir)
    state_dir = state_dirs.dispatch_dirs[0]
    lease_dir = state_dir / "leases"
    lease_dir.mkdir(parents=True)
    fresh = datetime.now(UTC).isoformat()
    (lease_dir / "doc-live.lock").write_text(
        json.dumps({"doc_slug": "doc-live", "pid": 7001, "heartbeat_at": fresh, "ttl_seconds": 300}),
        encoding="utf-8",
    )
    terminated: list[int] = []

    def _terminate(pid: int) -> None:
        terminated.append(pid)

    result = drain(
        state_dirs,
        timeout_seconds=0.0,
        now_fn=lambda: 0.0,
        terminate_fn=_terminate,
        poll_interval=0.0,
    )
    assert terminated == [7001]
    assert result.terminated_pids == [7001]
    terminated.clear()
    (lease_dir / "doc-live.lock").write_text(
        json.dumps({"doc_slug": "doc-live", "pid": 7002, "heartbeat_at": fresh, "ttl_seconds": 300}),
        encoding="utf-8",
    )

    def _release_early() -> float:
        (lease_dir / "doc-live.lock").unlink(missing_ok=True)
        return 0.0

    result2 = drain(
        state_dirs,
        timeout_seconds=1.0,
        now_fn=_release_early,
        terminate_fn=_terminate,
        poll_interval=0.0,
    )
    assert terminated == []
    assert result2.terminated_pids == []


# WI4793_DRY_RUN_TEST
def test_reset_dry_run_mutates_nothing(project_dir: Path) -> None:
    state_dirs = _seed_state_dirs(project_dir)
    state_dir = state_dirs.dispatch_dirs[0]
    before = {
        "dispatch": (state_dir / DISPATCH_STATE_FILENAME).read_text(encoding="utf-8"),
        "quiesce": (state_dir / QUIESCE_STATE_FILENAME).read_text(encoding="utf-8"),
        "provenance": (state_dirs.provenance_dir / PROVENANCE_LEDGER_FILENAME).read_text(encoding="utf-8"),
    }
    result = soft_reset(state_dirs, dry_run=True)
    assert result.recipients_cleared == 1
    assert (state_dir / DISPATCH_STATE_FILENAME).read_text(encoding="utf-8") == before["dispatch"]
    assert (state_dir / QUIESCE_STATE_FILENAME).read_text(encoding="utf-8") == before["quiesce"]
    assert (state_dirs.provenance_dir / PROVENANCE_LEDGER_FILENAME).read_text(encoding="utf-8") == before["provenance"]


def test_dispatch_is_draining_detects_marker(project_dir: Path) -> None:
    state_dir = project_dir / ".gtkb-state" / "bridge-poller"
    state_dir.mkdir(parents=True)
    assert not dispatch_is_draining(project_dir, state_dir)
    (state_dir / DRAIN_MARKER_FILENAME).write_text('{"active": true}', encoding="utf-8")
    assert dispatch_is_draining(project_dir, state_dir)


def test_run_trigger_skips_when_drain_marker_active(project_dir: Path) -> None:
    import importlib.util
    import sys

    trigger_path = Path(__file__).resolve().parents[2] / "scripts" / "cross_harness_bridge_trigger.py"
    spec = importlib.util.spec_from_file_location("cross_harness_bridge_trigger_drain_test", trigger_path)
    assert spec and spec.loader
    trigger = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = trigger
    spec.loader.exec_module(trigger)

    state_dir = project_dir / ".gtkb-state" / "bridge-poller"
    state_dir.mkdir(parents=True)
    (state_dir / DRAIN_MARKER_FILENAME).write_text(
        json.dumps({"active": True, "started_at": "2026-06-26T00:00:00+00:00"}),
        encoding="utf-8",
    )
    (project_dir / "groundtruth.toml").write_text(
        '[project]\nproject_name = "DrainTest"\nprofile = "dual-agent"\n',
        encoding="utf-8",
    )
    (project_dir / "bridge").mkdir(exist_ok=True)
    harness_state = project_dir / "harness-state"
    harness_state.mkdir(exist_ok=True)
    (harness_state / "harness-identities.json").write_text(
        json.dumps({"schema_version": 1, "harnesses": {}}),
        encoding="utf-8",
    )
    (harness_state / "harness-registry.json").write_text(
        json.dumps({"schema_version": 1, "harnesses": []}),
        encoding="utf-8",
    )

    summary = trigger.run_trigger(project_root=project_dir, state_dir=state_dir, dry_run=True)
    assert summary.get("skipped") is True
    assert summary.get("reason") == "dispatch_drain_active"
