# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scripts/gtkb_dispatcher_daemon.py (WI-4787)."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import time
import types
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DAEMON_PATH = _REPO_ROOT / "scripts" / "gtkb_dispatcher_daemon.py"
_CODEX_INVOCATION = {"headless": {"argv": ["codex", "exec", "{{PROMPT}}", "--cd", "{{PROJECT_ROOT}}"]}}
_CLAUDE_INVOCATION = {
    "headless": {"argv": ["claude", "-p", "{{PROMPT}}", "--add-dir", "{{PROJECT_ROOT}}", "--output-format", "json"]}
}


def _load_daemon():
    spec = importlib.util.spec_from_file_location("gtkb_dispatcher_daemon_test", _DAEMON_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _make_project(root: Path) -> Path:
    (root / "groundtruth.toml").write_text(
        '[project]\nproject_name = "TestSynthetic"\nprofile = "dual-agent"\n',
        encoding="utf-8",
    )
    (root / "bridge").mkdir(exist_ok=True)
    harness_state = root / "harness-state"
    harness_state.mkdir(exist_ok=True)
    (harness_state / "harness-identities.json").write_text(
        json.dumps({"schema_version": 1, "harnesses": {"claude": {"id": "B"}, "codex": {"id": "A"}}}),
        encoding="utf-8",
    )
    (harness_state / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": [
                    {
                        "id": "A",
                        "harness_name": "codex",
                        "harness_type": "codex",
                        "status": "active",
                        "event_driven_hooks": True,
                        "role": ["loyal-opposition"],
                        "invocation_surfaces": _CODEX_INVOCATION,
                    },
                    {
                        "id": "B",
                        "harness_name": "claude",
                        "harness_type": "claude",
                        "status": "active",
                        "event_driven_hooks": True,
                        "role": ["prime-builder"],
                        "invocation_surfaces": _CLAUDE_INVOCATION,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    return root


def _write_bridge(root: Path, stem: str, status: str, version: int) -> None:
    body = f"{status}\n\n# {stem} v{version}\nauthor_session_context_id: fixture-author-session\n"
    (root / "bridge" / f"{stem}-{version:03d}.md").write_text(body, encoding="utf-8")


def test_daemon_tick_computes_shadow_decision(tmp_path: Path) -> None:
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    _write_bridge(root, "pb-go-thread", "GO", 2)
    result = daemon.run_tick(root)
    assert result["decisions"]
    log_path = daemon.daemon_state_dir(root) / daemon.SHADOW_LOG_FILENAME
    assert log_path.is_file()
    lines = log_path.read_text(encoding="utf-8").splitlines()
    record = json.loads(lines[-1])
    assert record.get("shadow_mode") is True
    assert record.get("spawned") is False
    assert "role" in record


def test_daemon_shadow_mode_never_spawns(tmp_path: Path) -> None:
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    _write_bridge(root, "pb-go-thread", "GO", 2)
    with patch("subprocess.Popen") as popen:
        for _ in range(3):
            daemon.run_tick(root)
        popen.assert_not_called()


def test_daemon_writes_heartbeat_each_tick(tmp_path: Path) -> None:
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    hb = daemon.daemon_state_dir(root) / daemon.HEARTBEAT_FILENAME
    daemon.run_tick(root)
    first = hb.read_text(encoding="utf-8").strip()
    time.sleep(1.1)
    daemon.run_tick(root)
    second = hb.read_text(encoding="utf-8").strip()
    assert second >= first


def test_daemon_single_instance_lock(tmp_path: Path) -> None:
    daemon = _load_daemon()
    state_dir = daemon.daemon_state_dir(tmp_path)
    assert daemon.acquire_daemon_lock(state_dir)
    assert not daemon.acquire_daemon_lock(state_dir)
    daemon.release_daemon_lock(state_dir)
    assert daemon.acquire_daemon_lock(state_dir)


def test_daemon_control_cli_status_reports_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from groundtruth_kb import cli as cli_module
    from groundtruth_kb.cli import main

    daemon = _load_daemon()
    root = _make_project(tmp_path)
    config = root / "groundtruth.toml"
    config.write_text(
        '[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n',
        encoding="utf-8",
    )
    daemon.run_tick(root)
    monkeypatch.setattr(cli_module, "_import_dispatcher_daemon_module", lambda _project_root: daemon)

    result = CliRunner().invoke(
        main,
        ["--config", str(config), "bridge", "dispatch", "daemon", "status", "--json"],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["mode"] == "shadow"
    assert payload.get("heartbeat_at")


# ---------------------------------------------------------------------------
# WI-4856: daemon status must be liveness-accurate (running derives from process
# liveness + heartbeat freshness, not lock presence) and mode/active_substrate
# derive from the active substrate selection.
# ---------------------------------------------------------------------------


def test_status_running_false_on_stale_lock_dead_daemon(tmp_path: Path) -> None:
    """A stale lock left by a dead daemon (no live PID, stale heartbeat) must
    report running=False (WI-4856 fix 1)."""
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    state_dir = daemon.daemon_state_dir(root)
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / daemon.LOCK_FILENAME).write_text(json.dumps({"pid": 999999}), encoding="utf-8")
    # No PID file -> daemon_process_alive False; far-past heartbeat -> not fresh.
    (state_dir / daemon.HEARTBEAT_FILENAME).write_text("2020-01-01T00:00:00Z\n", encoding="utf-8")
    status = daemon.collect_daemon_status(root)
    assert status["running"] is False


def test_status_running_true_when_pid_alive(tmp_path: Path) -> None:
    """A live daemon PID reports running=True regardless of lock/heartbeat
    (WI-4856 fix 1)."""
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    state_dir = daemon.daemon_state_dir(root)
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / daemon.PID_FILENAME).write_text(str(os.getpid()) + "\n", encoding="utf-8")
    status = daemon.collect_daemon_status(root)
    assert status["running"] is True


def test_status_running_true_when_lock_and_heartbeat_fresh(tmp_path: Path) -> None:
    """A fresh heartbeat plus a held lock reports running even when the PID file
    is absent (WI-4856 fix 1)."""
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    state_dir = daemon.daemon_state_dir(root)
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / daemon.LOCK_FILENAME).write_text(json.dumps({"pid": 999999}), encoding="utf-8")
    (state_dir / daemon.HEARTBEAT_FILENAME).write_text(daemon._now_iso() + "\n", encoding="utf-8")
    status = daemon.collect_daemon_status(root)
    assert status["running"] is True


def test_status_mode_live_when_substrate_daemon(tmp_path: Path) -> None:
    """mode=live and active_substrate are reported when the active substrate is
    dispatcher_daemon (WI-4856 fix 2)."""
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    (root / "harness-state" / "bridge-substrate.json").write_text(
        json.dumps({"substrate": "dispatcher_daemon"}), encoding="utf-8"
    )
    status = daemon.collect_daemon_status(root)
    assert status["mode"] == "live"
    assert status["active_substrate"] == "dispatcher_daemon"


def test_status_mode_shadow_when_substrate_cross_harness(tmp_path: Path) -> None:
    """mode=shadow when the active substrate is the cross-harness trigger
    (WI-4856 fix 2)."""
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    (root / "harness-state" / "bridge-substrate.json").write_text(
        json.dumps({"substrate": "cross_harness_trigger"}), encoding="utf-8"
    )
    status = daemon.collect_daemon_status(root)
    assert status["mode"] == "shadow"
    assert status["active_substrate"] == "cross_harness_trigger"


def test_run_tick_includes_health_monitoring(tmp_path: Path) -> None:
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    _write_bridge(root, "pb-go-thread", "GO", 2)
    result = daemon.run_tick(root)
    assert "monitoring" in result
    assert "health" in result
    assert "generated_at" in result["monitoring"]
    assert "per_role" in result["monitoring"]
    assert isinstance(result["health"], dict)
    status_path = daemon.daemon_state_dir(root) / daemon.STATUS_FILENAME
    status = json.loads(status_path.read_text(encoding="utf-8"))
    assert "monitoring" in status
    assert "health" in status


def test_run_tick_monitoring_failsoft(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    _write_bridge(root, "pb-go-thread", "GO", 2)

    def boom():
        raise RuntimeError("monitoring unavailable")

    monkeypatch.setattr(daemon, "_load_dispatch_monitor", boom)
    result = daemon.run_tick(root)
    assert result["decisions"]
    assert result.get("monitoring_error") == "monitoring unavailable"
    assert "monitoring" not in result


def test_shadow_decision_shrinks_remaining_items(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Multi-target roles must not re-offer the same docs (WI-4848 slice 2)."""
    from types import SimpleNamespace

    daemon = _load_daemon()
    root = _make_project(tmp_path)
    _write_bridge(root, "lo-doc-one", "NEW", 1)
    _write_bridge(root, "lo-doc-two", "NEW", 1)

    target_a = SimpleNamespace(dispatch_state_key="lo:A", harness_id="A", invocation_surfaces={})
    target_b = SimpleNamespace(dispatch_state_key="lo:B", harness_id="B", invocation_surfaces={})

    trigger = daemon._load_trigger_module()

    def _fake_resolve(role_label, project_root, state_dir, *, items=None):
        if role_label == "loyal-opposition":
            return [target_a, target_b]
        return []

    monkeypatch.setattr(trigger, "_resolve_dispatch_targets", _fake_resolve)

    decisions = daemon.compute_shadow_decisions(root, max_items=1)
    lo_decisions = [d for d in decisions if d.get("role") == "loyal-opposition" and d.get("would_dispatch")]
    assert len(lo_decisions) >= 2
    first_docs = set(lo_decisions[0]["would_dispatch"])
    second_docs = set(lo_decisions[1]["would_dispatch"])
    assert first_docs
    assert second_docs
    assert not first_docs & second_docs, (first_docs, second_docs)


def test_daemon_default_substrate_stays_shadow(tmp_path: Path) -> None:
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    _write_bridge(root, "pb-go-thread", "GO", 2)
    with patch("subprocess.Popen") as popen:
        result = daemon.run_tick(root)
    assert result["mode"] == "shadow"
    status = json.loads((daemon.daemon_state_dir(root) / daemon.STATUS_FILENAME).read_text(encoding="utf-8"))
    assert status["mode"] == "shadow"
    popen.assert_not_called()


def test_daemon_daemon_substrate_dispatches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    harness_state = root / "harness-state"
    (harness_state / "bridge-substrate.json").write_text(
        json.dumps({"substrate": daemon.DAEMON_SUBSTRATE}),
        encoding="utf-8",
    )
    _write_bridge(root, "pb-go-thread", "GO", 2)
    trigger = daemon._load_trigger_module()
    calls: list[dict] = []

    def _fake_spawn(**kwargs):
        calls.append(kwargs)
        return {"launched": True, "recipient": kwargs["target"].dispatch_state_key}

    monkeypatch.setattr(trigger, "_is_dispatch_ready", lambda *a, **k: True)
    monkeypatch.setattr(trigger, "_spawn_harness", _fake_spawn)
    result = daemon.run_tick(root)
    assert result["mode"] == "live"
    status = json.loads((daemon.daemon_state_dir(root) / daemon.STATUS_FILENAME).read_text(encoding="utf-8"))
    assert status["mode"] == "live"
    assert calls, "expected live tick to invoke _spawn_harness"


def test_daemon_live_skips_not_ready_target(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    (root / "harness-state" / "bridge-substrate.json").write_text(
        json.dumps({"substrate": daemon.DAEMON_SUBSTRATE}),
        encoding="utf-8",
    )
    _write_bridge(root, "pb-go-thread", "GO", 2)
    trigger = daemon._load_trigger_module()
    spawn_calls: list[dict] = []

    monkeypatch.setattr(trigger, "_is_dispatch_ready", lambda *a, **k: False)
    monkeypatch.setattr(
        trigger,
        "_spawn_harness",
        lambda **kwargs: spawn_calls.append(kwargs) or {"launched": True},
    )
    result = daemon.run_tick(root)
    assert result["mode"] == "live"
    assert not spawn_calls
    reasons = [d.get("reason") for d in result["decisions"] if d.get("reason")]
    assert any(str(r).endswith("_dispatch_not_ready") for r in reasons)


def test_daemon_live_honors_provider_backoff_skip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    (root / "harness-state" / "bridge-substrate.json").write_text(
        json.dumps({"substrate": daemon.DAEMON_SUBSTRATE}),
        encoding="utf-8",
    )
    _write_bridge(root, "pb-go-thread", "GO", 2)
    trigger = daemon._load_trigger_module()
    spawn_calls: list[dict] = []

    monkeypatch.setattr(trigger, "_is_dispatch_ready", lambda *a, **k: True)
    monkeypatch.setattr(
        trigger,
        "_provider_failure_backoff_skip",
        lambda **kwargs: {"reason": "provider_failure_backoff_active"},
    )
    monkeypatch.setattr(
        trigger,
        "_spawn_harness",
        lambda **kwargs: spawn_calls.append(kwargs) or {"launched": True},
    )
    result = daemon.run_tick(root)
    assert result["mode"] == "live"
    assert not spawn_calls
    assert any(d.get("reason") == "provider_failure_backoff_active" for d in result["decisions"])


# --- WI-4852: watchdog dormancy detection and fail-soft restart ---------------


_WATCHDOG_HEARTBEAT_TAIL = "codex=0 family=0 noncodex=0 threshold=15 noncodexThreshold=15 mode=liveness-aware(WI-4828)"


def _write_stale_watchdog_heartbeat(root: Path) -> None:
    """Write a watchdog heartbeat old enough to trigger dormancy detection.

    Uses the REAL storm-watchdog line format (leading ISO timestamp followed by
    space-separated population fields), so the daemon's heartbeat parse is
    exercised exactly as ``scripts/ops/harness_storm_watchdog.ps1`` writes it.
    """
    import datetime as dt

    watchdog_dir = root / ".gtkb-state" / "ops"
    watchdog_dir.mkdir(parents=True, exist_ok=True)
    stale_ts = dt.datetime(2020, 1, 1, 0, 0, 0, tzinfo=dt.UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    line = f"{stale_ts} {_WATCHDOG_HEARTBEAT_TAIL}"
    (watchdog_dir / "storm-watchdog-heartbeat.txt").write_text(line, encoding="utf-8")


def _write_fresh_watchdog_heartbeat(root: Path) -> None:
    """Write a current-timestamp heartbeat in the REAL storm-watchdog line format."""
    import datetime as dt

    watchdog_dir = root / ".gtkb-state" / "ops"
    watchdog_dir.mkdir(parents=True, exist_ok=True)
    fresh_ts = dt.datetime.now(dt.UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    line = f"{fresh_ts} {_WATCHDOG_HEARTBEAT_TAIL}"
    (watchdog_dir / "storm-watchdog-heartbeat.txt").write_text(line, encoding="utf-8")


def _set_live_substrate(daemon, root: Path) -> None:
    """Switch the daemon to LIVE mode (it owns executing remediation actions)."""
    (root / "harness-state" / "bridge-substrate.json").write_text(
        json.dumps({"substrate": daemon.DAEMON_SUBSTRATE}), encoding="utf-8"
    )


def test_run_tick_emits_restart_watchdog_when_dormant(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """LIVE-mode daemon emits restart_storm_watchdog and executes the restart on dormancy."""
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    _set_live_substrate(daemon, root)
    _write_stale_watchdog_heartbeat(root)

    monkeypatch.setattr(daemon, "_restart_storm_watchdog", lambda: {"launched": True, "returncode": 0})

    result = daemon.run_tick(root, dry_run=False)
    assert result["mode"] == "live"
    assert "watchdog_dormancy" in result
    wd = result["watchdog_dormancy"]
    assert wd["dormant"] is True
    assert wd.get("remediation_hint") == "restart_storm_watchdog"
    assert "watchdog_restart" in result
    assert result["watchdog_restart"]["launched"] is True


# ---------------------------------------------------------------------------
# WI-4855: daemon process-lifecycle hardening (start/stop control surface).
# These tests exercise the production CLI commands
# (gt bridge dispatch daemon start|stop) in groundtruth_kb/cli.py via
# CliRunner — the exposed control surface — per GOV-10/GOV-19 outside-in
# testing. cli is imported lazily inside each test so the daemon-script tests
# above stay independent of cli package importability.
# ---------------------------------------------------------------------------


def _daemon_cli_patches(gtcli, daemon, project_root: Path):
    """Patch context: resolve config to ``project_root`` and reuse the already
    loaded daemon module, so the synthetic project needs no real daemon script."""
    cfg = types.SimpleNamespace(project_root=project_root)
    return (
        patch.object(gtcli, "_resolve_config", return_value=cfg),
        patch.object(gtcli, "_import_dispatcher_daemon_module", return_value=daemon),
    )


def test_daemon_start_spawns_detached(tmp_path: Path) -> None:
    """Defect (3) true detach: ``start`` spawns the daemon with platform-detach
    flags so the daemon survives its launching shell / scheduled task."""
    from groundtruth_kb import cli as gtcli

    daemon = _load_daemon()
    captured: dict[str, object] = {}

    class _FakePopen:
        def __init__(self, args, **kwargs):
            captured["args"] = args
            captured["kwargs"] = kwargs
            self.pid = 4242

    cfg_patch, import_patch = _daemon_cli_patches(gtcli, daemon, tmp_path)
    with cfg_patch, import_patch, patch.object(gtcli.subprocess, "Popen", _FakePopen):
        result = CliRunner().invoke(gtcli.bridge_dispatch_daemon_start_cmd, [], obj={})

    assert result.exit_code == 0, result.output
    kwargs = captured["kwargs"]
    if os.name == "nt":
        flags = int(kwargs.get("creationflags", 0))
        assert flags & subprocess.DETACHED_PROCESS
        assert flags & subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        assert kwargs.get("start_new_session") is True
    assert captured["args"][0] == sys.executable


def test_daemon_start_refuses_when_live_instance_present(tmp_path: Path) -> None:
    """Defect (2) single-instance: with a live (lock-cleared) daemon process
    recorded in daemon.pid, a second ``start`` is refused via the real
    process-liveness probe (no lock file is present)."""
    from groundtruth_kb import cli as gtcli

    daemon = _load_daemon()
    state_dir = daemon.daemon_state_dir(tmp_path)
    state_dir.mkdir(parents=True, exist_ok=True)
    # Record the current (alive) test-process pid. No lock file is present, so
    # only process-liveness detection can catch the running instance.
    (state_dir / daemon.PID_FILENAME).write_text(str(os.getpid()) + "\n", encoding="utf-8")

    cfg_patch, import_patch = _daemon_cli_patches(gtcli, daemon, tmp_path)
    with cfg_patch, import_patch:
        result = CliRunner().invoke(gtcli.bridge_dispatch_daemon_start_cmd, [], obj={})

    # Refusal raises ClickException before the spawn branch; the success branch
    # would instead echo "Started ..." and exit 0.
    assert result.exit_code != 0
    assert "already running" in result.output
    assert "Started" not in result.output


def test_daemon_stop_terminates_process_tree(tmp_path: Path) -> None:
    """Defect (1) clean stop: ``stop`` terminates the recorded daemon process
    tree (via daemon.pid), clears the pid file, and releases the lock."""
    from groundtruth_kb import cli as gtcli

    daemon = _load_daemon()
    state_dir = daemon.daemon_state_dir(tmp_path)
    state_dir.mkdir(parents=True, exist_ok=True)

    # Real throwaway child process for stop to terminate.
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
    try:
        (state_dir / daemon.PID_FILENAME).write_text(str(child.pid) + "\n", encoding="utf-8")
        assert daemon.acquire_daemon_lock(state_dir) is True

        cfg_patch, import_patch = _daemon_cli_patches(gtcli, daemon, tmp_path)
        with cfg_patch, import_patch:
            result = CliRunner().invoke(gtcli.bridge_dispatch_daemon_stop_cmd, [], obj={})

        assert result.exit_code == 0, result.output
        # taskkill /T is asynchronous on Windows; poll for termination.
        deadline = time.time() + 10
        while time.time() < deadline and daemon._pid_is_running(child.pid):
            time.sleep(0.2)
        assert daemon._pid_is_running(child.pid) is False
        assert not (state_dir / daemon.PID_FILENAME).exists()
        assert daemon.read_daemon_status(tmp_path).get("running") is not True
    finally:
        if child.poll() is None:
            child.kill()
            child.wait(timeout=10)


# ---------------------------------------------------------------------------
# WI-4845: daemon passes a per-role worker --lifetime override so headless
# workers complete (LO ~1800s, PB ~5400s, env-configurable). The cap is
# resolved by trigger.worker_lifetime_seconds and threaded into the spawn
# command (run_with_status.py --lifetime) by trigger._spawn_harness, which the
# daemon's live-spawn path reuses.
# ---------------------------------------------------------------------------


def _spawn_target(trigger, role_label: str, mode: str):
    return trigger.DispatchTarget(
        needed_role_label=role_label,
        harness_id="D",
        command_handle="ollama",
        canonical_mode=mode,
        invocation_surfaces={"headless": {"argv": ["worker-cmd", "{{PROMPT}}"]}},
    )


def _capture_worker_command(trigger, target, tmp_path: Path, monkeypatch) -> list[str]:
    """Invoke _spawn_harness with a fake Popen; return the worker command (the
    one wrapping run_with_status.py), robust against any secondary poll spawn."""
    calls: list[tuple] = []

    class _FakeProcess:
        pid = 4242

    def _fake_popen(*args, **kwargs):
        calls.append(args)
        return _FakeProcess()

    monkeypatch.setattr(trigger, "_count_live_dispatched_processes", lambda runs_dir: 0)
    monkeypatch.setattr(trigger, "_is_spawn_rate_limited", lambda runs_dir: False)
    # Prime (implementer) dispatches issue impl-auth packets for the GO item
    # (WI-4770). That is orthogonal to the lifetime feature under test, so pass
    # it for the synthetic item; LO review dispatches do not reach this gate.
    monkeypatch.setattr(
        trigger,
        "_issue_dispatch_authorization_for_selected",
        lambda *a, **k: {"ok": True, "reason": None, "context": {}},
    )
    monkeypatch.setattr(trigger.subprocess, "Popen", _fake_popen)

    # Isolate each capture so a same-signature dedup from a prior spawn in the
    # same test cannot suppress this one.
    role = target.needed_role_label
    item = type(
        "FakeItem",
        (),
        {
            "document_name": f"gtkb-wi4845-{role}-thread",
            "top_status": "GO",
            "top_file": f"bridge/gtkb-wi4845-{role}-thread-002.md",
        },
    )()
    trigger._spawn_harness(
        target=target,
        items=[item],
        project_root=tmp_path,
        state_dir=tmp_path / role / "state",
        max_items=1,
        dry_run=False,
        dispatch_id=f"dispatch-wi4845-{role}",
    )
    for args in calls:
        if args and isinstance(args[0], list) and any("run_with_status" in str(part) for part in args[0]):
            return list(args[0])
    return []


def _lifetime_value(command: list[str]) -> str | None:
    if "--lifetime" not in command:
        return None
    return command[command.index("--lifetime") + 1]


def test_daemon_spawn_passes_per_role_lifetime(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The daemon live-spawn command carries the per-role --lifetime override:
    LO target -> 1800s, PB target -> 5400s (WI-4845 defaults)."""
    daemon = _load_daemon()
    trigger = daemon._load_trigger_module()
    monkeypatch.delenv(trigger.LO_WORKER_LIFETIME_ENV_VAR, raising=False)
    monkeypatch.delenv(trigger.PB_WORKER_LIFETIME_ENV_VAR, raising=False)

    lo_cmd = _capture_worker_command(trigger, _spawn_target(trigger, "loyal-opposition", "lo"), tmp_path, monkeypatch)
    assert _lifetime_value(lo_cmd) == str(trigger.LO_REVIEW_WORKER_LIFETIME_SECONDS) == "1800"

    pb_cmd = _capture_worker_command(trigger, _spawn_target(trigger, "prime-builder", "pb"), tmp_path, monkeypatch)
    assert _lifetime_value(pb_cmd) == str(trigger.PB_IMPL_WORKER_LIFETIME_SECONDS) == "5400"


def test_daemon_worker_lifetime_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """GTKB_WORKER_LIFETIME_LO_SECONDS / _PB_SECONDS override the per-role
    defaults; invalid/non-positive falls back; other roles get no cap (WI-4845)."""
    daemon = _load_daemon()
    trigger = daemon._load_trigger_module()

    monkeypatch.delenv(trigger.LO_WORKER_LIFETIME_ENV_VAR, raising=False)
    monkeypatch.delenv(trigger.PB_WORKER_LIFETIME_ENV_VAR, raising=False)
    assert trigger.worker_lifetime_seconds("loyal-opposition") == 1800
    assert trigger.worker_lifetime_seconds("prime-builder") == 5400
    assert trigger.worker_lifetime_seconds("some-other-role") is None
    assert trigger.worker_lifetime_seconds(None) is None

    monkeypatch.setenv(trigger.LO_WORKER_LIFETIME_ENV_VAR, "2400")
    monkeypatch.setenv(trigger.PB_WORKER_LIFETIME_ENV_VAR, "7200")
    assert trigger.worker_lifetime_seconds("loyal-opposition") == 2400
    assert trigger.worker_lifetime_seconds("prime-builder") == 7200

    monkeypatch.setenv(trigger.LO_WORKER_LIFETIME_ENV_VAR, "0")
    monkeypatch.setenv(trigger.PB_WORKER_LIFETIME_ENV_VAR, "not-an-int")
    assert trigger.worker_lifetime_seconds("loyal-opposition") == 1800
    assert trigger.worker_lifetime_seconds("prime-builder") == 5400


def test_run_tick_watchdog_restart_failsoft(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A restart failure must not abort the tick (fail-soft: watchdog_error recorded, tick succeeds)."""
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    _set_live_substrate(daemon, root)
    _write_stale_watchdog_heartbeat(root)

    def _failing_restart() -> None:
        raise RuntimeError("schtasks.exe not available in test environment")

    monkeypatch.setattr(daemon, "_restart_storm_watchdog", _failing_restart)

    result = daemon.run_tick(root, dry_run=False)
    assert result.get("tick_at")  # tick completed normally despite restart failure
    assert "watchdog_error" in result
    assert "schtasks" in result["watchdog_error"]


def test_run_tick_fresh_real_format_heartbeat_not_dormant(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A fresh real-format heartbeat is parsed as NOT dormant and triggers no restart.

    Regression guard for the heartbeat-parse defect: the storm watchdog writes
    the leading ISO timestamp followed by space-separated population fields, so
    the daemon must parse only the first token. A parse that fed the whole line
    to ``datetime.fromisoformat`` mis-reads every fresh heartbeat as ``0.0`` /
    dormant and would restart the healthy watchdog on every tick. Runs in LIVE
    mode so the buggy-parse failure mode (a restart firing) is observable.
    """
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    _set_live_substrate(daemon, root)
    _write_fresh_watchdog_heartbeat(root)

    called = {"restart": False}

    def _should_not_restart() -> dict:
        called["restart"] = True
        return {"launched": True, "returncode": 0}

    monkeypatch.setattr(daemon, "_restart_storm_watchdog", _should_not_restart)

    result = daemon.run_tick(root, dry_run=False)
    assert result["mode"] == "live"
    assert "watchdog_dormancy" in result
    wd = result["watchdog_dormancy"]
    assert wd["dormant"] is False
    assert "remediation_hint" not in wd
    assert "watchdog_restart" not in result
    assert called["restart"] is False


def test_run_tick_shadow_mode_records_dormancy_without_restart(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """SHADOW mode records the dormancy verdict + hint but executes NO restart.

    Guards the mode-gating decision: the dormancy verdict is observability
    (recorded like monitoring/health in both modes), but executing the restart
    is a subprocess spawn reserved for the live substrate, per the committed
    shadow-never-spawns invariant.
    """
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    _write_stale_watchdog_heartbeat(root)

    called = {"restart": False}

    def _should_not_restart() -> dict:
        called["restart"] = True
        return {"launched": True, "returncode": 0}

    monkeypatch.setattr(daemon, "_restart_storm_watchdog", _should_not_restart)

    result = daemon.run_tick(root, dry_run=False)
    assert result["mode"] == "shadow"
    assert "watchdog_dormancy" in result
    wd = result["watchdog_dormancy"]
    assert wd["dormant"] is True
    assert wd.get("remediation_hint") == "restart_storm_watchdog"
    assert "watchdog_restart" not in result
    assert called["restart"] is False
