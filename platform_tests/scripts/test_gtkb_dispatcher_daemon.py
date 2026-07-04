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

import psutil
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


def _make_codex_prime_project(root: Path) -> Path:
    root = _make_project(root)
    (root / "harness-state" / "harness-registry.json").write_text(
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
                        "role": ["prime-builder"],
                        "invocation_surfaces": _CODEX_INVOCATION,
                    },
                    {
                        "id": "B",
                        "harness_name": "claude",
                        "harness_type": "claude",
                        "status": "active",
                        "event_driven_hooks": True,
                        "role": ["loyal-opposition"],
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


def _write_go_thread(root: Path, stem: str) -> None:
    _write_bridge(root, stem, "NEW", 1)
    _write_bridge(root, stem, "GO", 2)


def _set_manual_substrate(root: Path) -> None:
    (root / "harness-state" / "bridge-substrate.json").write_text(
        json.dumps({"substrate": "none"}),
        encoding="utf-8",
    )


def test_daemon_tick_computes_shadow_decision(tmp_path: Path) -> None:
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    _set_manual_substrate(root)
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
    _set_manual_substrate(root)
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
    assert payload["mode"] == "live"
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
    """A live daemon PID reports running=True when create-time provenance
    matches (WI-4893 PID-reuse guard)."""
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    state_dir = daemon.daemon_state_dir(root)
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / daemon.PID_FILENAME).write_text(str(os.getpid()) + "\n", encoding="utf-8")
    _write_daemon_pid_provenance(daemon, state_dir, os.getpid())
    status = daemon.collect_daemon_status(root)
    assert status["running"] is True
    assert status["pid_provenance_verified"] is True


def test_status_running_false_when_daemon_pid_provenance_mismatches(tmp_path: Path) -> None:
    """WI-4893: daemon status must not trust a reused PID."""
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    state_dir = daemon.daemon_state_dir(root)
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / daemon.PID_FILENAME).write_text(str(os.getpid()) + "\n", encoding="utf-8")
    (state_dir / daemon.PID_CREATE_TIME_FILENAME).write_text("1.000000", encoding="utf-8")

    status = daemon.collect_daemon_status(root)

    assert status["running"] is False
    assert status["pid_provenance_verified"] is False


def test_status_running_true_for_legacy_daemon_loop_without_sidecar(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """WI-4893 residual: a pre-provenance daemon loop must block duplicate start.

    The create-time sidecar is the preferred proof. During rolling hardening,
    however, an already-running daemon may predate that sidecar. If its live
    process command line is the dispatcher daemon loop for this project root,
    status/start must treat it as alive to prevent a second loop from spawning.
    """
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    state_dir = daemon.daemon_state_dir(root)
    state_dir.mkdir(parents=True, exist_ok=True)
    pid = 4242
    (state_dir / daemon.PID_FILENAME).write_text(f"{pid}\n", encoding="utf-8")
    command = [
        sys.executable,
        str(root / "scripts" / "gtkb_dispatcher_daemon.py"),
        "--loop",
        "--project-root",
        str(root),
    ]

    monkeypatch.setattr(daemon, "_pid_is_running", lambda candidate: candidate == pid)
    monkeypatch.setattr(daemon, "_process_command_line", lambda candidate: command if candidate == pid else [])

    status = daemon.collect_daemon_status(root)

    assert daemon.daemon_process_alive(state_dir) is True
    assert status["running"] is True
    assert status["pid_provenance_verified"] is False


def test_status_running_false_for_unrelated_pid_without_sidecar(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """WI-4893 residual: PID-only evidence still must not trust unrelated processes."""
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    state_dir = daemon.daemon_state_dir(root)
    state_dir.mkdir(parents=True, exist_ok=True)
    pid = 4242
    (state_dir / daemon.PID_FILENAME).write_text(f"{pid}\n", encoding="utf-8")

    monkeypatch.setattr(daemon, "_pid_is_running", lambda candidate: candidate == pid)
    monkeypatch.setattr(daemon, "_process_command_line", lambda _candidate: [sys.executable, "-c", "pass"])
    monkeypatch.setattr(daemon, "_matching_daemon_loop_pids", lambda _state_dir: [])

    assert daemon.daemon_process_alive(state_dir) is False
    assert daemon.collect_daemon_status(root)["running"] is False


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


def test_status_mode_shadow_when_substrate_none(tmp_path: Path) -> None:
    """mode=shadow when bridge automation is paused for manual assignment."""
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    _set_manual_substrate(root)
    status = daemon.collect_daemon_status(root)
    assert status["mode"] == "shadow"
    assert status["active_substrate"] == "none"


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

    runtime = daemon._load_dispatch_runtime()

    def _fake_resolve(role_label, project_root, state_dir, *, items=None):
        if role_label == "loyal-opposition":
            return [target_a, target_b]
        return []

    monkeypatch.setattr(runtime, "_resolve_dispatch_targets", _fake_resolve)

    decisions = daemon.compute_shadow_decisions(root, max_items=1)
    lo_decisions = [d for d in decisions if d.get("role") == "loyal-opposition" and d.get("would_dispatch")]
    assert len(lo_decisions) >= 2
    first_docs = set(lo_decisions[0]["would_dispatch"])
    second_docs = set(lo_decisions[1]["would_dispatch"])
    assert first_docs
    assert second_docs
    assert not first_docs & second_docs, (first_docs, second_docs)


def test_daemon_default_substrate_is_live(tmp_path: Path) -> None:
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    result = daemon.run_tick(root, dry_run=True)
    assert result["mode"] == "live"
    status = daemon.collect_daemon_status(root)
    assert status["mode"] == "live"
    assert status["active_substrate"] == daemon.DAEMON_SUBSTRATE


def test_daemon_daemon_substrate_dispatches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    harness_state = root / "harness-state"
    (harness_state / "bridge-substrate.json").write_text(
        json.dumps({"substrate": daemon.DAEMON_SUBSTRATE}),
        encoding="utf-8",
    )
    _write_bridge(root, "pb-go-thread", "GO", 2)
    runtime = daemon._load_dispatch_runtime()
    calls: list[dict] = []

    def _fake_spawn(**kwargs):
        calls.append(kwargs)
        return {"launched": True, "recipient": kwargs["target"].dispatch_state_key}

    monkeypatch.setattr(runtime, "_is_dispatch_ready", lambda *a, **k: True)
    monkeypatch.setattr(runtime, "_spawn_harness", _fake_spawn)
    result = daemon.run_tick(root)
    assert result["mode"] == "live"
    status = json.loads((daemon.daemon_state_dir(root) / daemon.STATUS_FILENAME).read_text(encoding="utf-8"))
    assert status["mode"] == "live"
    assert calls, "expected live tick to invoke _spawn_harness"
    state = runtime._load_dispatch_state(daemon._bridge_poller_state_dir(root), root)
    launch = state["recipients"]["prime-builder:B"]["last_launch"]
    assert launch["launched"] is True
    assert launch["recipient"] == "prime-builder:B"


def test_daemon_operator_quiesce_suppresses_live_spawns(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    _write_bridge(root, "pb-go-thread", "GO", 2)
    runtime = daemon._load_dispatch_runtime()
    daemon.set_operator_quiesce(
        root,
        reason="entangled commit window",
        actor="operator",
        ttl_seconds=600,
    )
    calls: list[dict] = []
    monkeypatch.setattr(runtime, "_is_dispatch_ready", lambda *a, **k: True)
    monkeypatch.setattr(runtime, "_spawn_harness", lambda **kwargs: calls.append(kwargs))

    result = daemon.run_tick(root)

    assert result["mode"] == "live"
    assert result["operator_quiesce"]["active"] is True
    assert calls == []
    assert "spawn_results" not in result
    dispatchable = [record for record in result["decisions"] if record.get("would_dispatch")]
    assert dispatchable
    assert {record.get("reason") for record in dispatchable} == {runtime.OPERATOR_QUIESCE_ACTIVE_REASON}
    status = daemon.collect_daemon_status(root)
    assert status["operator_quiesce"]["active"] is True


def test_daemon_quiesce_cli_set_status_clear_and_worker_clear_guard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    worker_env_vars = ("GTKB_BRIDGE_POLLER_RUN_ID", "GTKB_DISPATCH_ID", "GTKB_WORK_INTENT_SESSION_ID")
    for env_var in worker_env_vars:
        monkeypatch.delenv(env_var, raising=False)

    rc = daemon.main(
        [
            "quiesce",
            "set",
            "--project-root",
            str(root),
            "--reason",
            "commit window",
            "--actor",
            "operator",
            "--ttl-seconds",
            "60",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert payload["active"] is True
    assert payload["reason"] == "commit window"

    rc = daemon.main(["quiesce", "status", "--project-root", str(root)])
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert payload["active"] is True

    monkeypatch.setenv("GTKB_WORK_INTENT_SESSION_ID", "2026-07-03T15-18-10Z-prime-builder-A-demo")
    rc = daemon.main(
        [
            "quiesce",
            "clear",
            "--project-root",
            str(root),
            "--reason",
            "worker attempted clear",
            "--actor",
            "worker",
        ]
    )
    captured = capsys.readouterr()
    assert rc == 2
    assert "dispatched workers may not clear" in captured.err

    for env_var in worker_env_vars:
        monkeypatch.delenv(env_var, raising=False)
    rc = daemon.main(
        [
            "quiesce",
            "clear",
            "--project-root",
            str(root),
            "--reason",
            "window complete",
            "--actor",
            "operator",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert payload["active"] is False
    assert payload["status"] == "cleared"


def test_daemon_live_spawns_do_not_duplicate_lo_documents_across_targets(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    runtime = daemon._load_dispatch_runtime()
    selected = [
        types.SimpleNamespace(
            document_name="duplicate-thread", top_status="NEW", top_file="bridge/duplicate-thread-001.md"
        )
    ]
    target_a = runtime.DispatchTarget(
        needed_role_label="loyal-opposition",
        harness_id="A",
        command_handle="codex",
        canonical_mode="lo",
        invocation_surfaces=_CODEX_INVOCATION,
    )
    target_d = runtime.DispatchTarget(
        needed_role_label="loyal-opposition",
        harness_id="D",
        command_handle="ollama",
        canonical_mode="lo",
        invocation_surfaces={"headless": {"argv": ["ollama-harness", "{{PROMPT}}"]}},
    )
    calls: list[str] = []

    def _fake_spawn_harness(**kwargs):
        calls.append(kwargs["target"].dispatch_state_key)
        return {
            "dispatch_id": kwargs.get("dispatch_id"),
            "recipient": kwargs["target"].dispatch_state_key,
            "launched": True,
            "reason": "launched",
        }

    monkeypatch.setattr(runtime, "_spawn_harness", _fake_spawn_harness)

    results = daemon._execute_live_spawns(
        root,
        [
            {
                "role": "loyal-opposition",
                "recipient": target_a.dispatch_state_key,
                "signature": runtime._signature(selected),
                "_spawn_target": target_a,
                "_spawn_selected": selected,
            },
            {
                "role": "loyal-opposition",
                "recipient": target_d.dispatch_state_key,
                "signature": runtime._signature(selected),
                "_spawn_target": target_d,
                "_spawn_selected": selected,
            },
        ],
        max_items=1,
        dry_run=False,
    )

    assert calls == ["loyal-opposition:A"]
    assert results[0]["launched"] is True
    assert results[1]["reason"] == runtime.DOCUMENT_LEASE_HELD_RESULT
    state = runtime._load_dispatch_state(daemon._bridge_poller_state_dir(root), root)
    assert state["recipients"]["loyal-opposition:D"]["last_result"] == runtime.DOCUMENT_LEASE_HELD_RESULT


def test_daemon_live_dedupe_survives_newer_unsuffixed_substrate_mismatch_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    daemon = _load_daemon()
    root = _make_codex_prime_project(tmp_path)
    (root / "harness-state" / "bridge-substrate.json").write_text(
        json.dumps({"substrate": daemon.DAEMON_SUBSTRATE}),
        encoding="utf-8",
    )
    _write_bridge(root, "pb-go-thread", "GO", 2)
    runtime = daemon._load_dispatch_runtime()
    calls: list[dict] = []

    def _fake_spawn(**kwargs):
        calls.append(kwargs)
        return {"launched": True, "recipient": kwargs["target"].dispatch_state_key}

    monkeypatch.setattr(runtime, "_is_dispatch_ready", lambda *a, **k: True)
    monkeypatch.setattr(runtime, "_spawn_harness", _fake_spawn)

    first = daemon.run_tick(root)
    assert first["mode"] == "live"
    assert len(calls) == 1
    state_dir = daemon._bridge_poller_state_dir(root)
    state_path = state_dir / runtime.DISPATCH_STATE_FILENAME
    state = json.loads(state_path.read_text(encoding="utf-8"))
    prime_state = state["recipients"]["prime-builder:A"]
    signature = prime_state["last_dispatched_signature"]
    prime_state["failure_class"] = "subprocess_execution_failed"
    prime_state["last_failure_reason"] = "subprocess_execution_failed"

    state["recipients"]["prime-builder"] = {
        "updated_at": "2026-06-29T07:46:04+00:00",
        "last_result": "substrate_mismatch_inert",
        "pending_count": 0,
        "selected_count": 0,
    }
    state_path.write_text(json.dumps(state), encoding="utf-8")

    calls.clear()
    second = daemon.run_tick(root)

    assert second["mode"] == "live"
    assert calls == []
    assert len(second["spawn_results"]) == 1
    assert second["spawn_results"][0]["recipient"] == "prime-builder:A"
    assert second["spawn_results"][0]["launched"] is False
    assert second["spawn_results"][0]["reason"] == "work_intent_already_held"
    repaired_state = json.loads(state_path.read_text(encoding="utf-8"))["recipients"]["prime-builder:A"]
    assert repaired_state["last_dispatched_signature"] == signature
    assert repaired_state["last_result"] == "work_intent_already_held"
    assert repaired_state["pending_count"] == 0
    assert "failure_class" not in repaired_state
    assert "last_failure_reason" not in repaired_state


def test_daemon_live_skips_not_ready_target(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    (root / "harness-state" / "bridge-substrate.json").write_text(
        json.dumps({"substrate": daemon.DAEMON_SUBSTRATE}),
        encoding="utf-8",
    )
    _write_bridge(root, "pb-go-thread", "GO", 2)
    runtime = daemon._load_dispatch_runtime()
    spawn_calls: list[dict] = []

    monkeypatch.setattr(runtime, "_is_dispatch_ready", lambda *a, **k: False)
    monkeypatch.setattr(
        runtime,
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
    runtime = daemon._load_dispatch_runtime()
    spawn_calls: list[dict] = []

    monkeypatch.setattr(runtime, "_is_dispatch_ready", lambda *a, **k: True)
    monkeypatch.setattr(
        runtime,
        "_provider_failure_backoff_skip",
        lambda **kwargs: {"reason": "provider_failure_backoff_active"},
    )
    monkeypatch.setattr(
        runtime,
        "_spawn_harness",
        lambda **kwargs: spawn_calls.append(kwargs) or {"launched": True},
    )
    result = daemon.run_tick(root)
    assert result["mode"] == "live"
    assert not spawn_calls
    assert any(d.get("reason") == "provider_failure_backoff_active" for d in result["decisions"])


def test_daemon_reconciles_nonzero_exit_and_falls_back_to_next_lo(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A completed nonzero same-signature LO run must not strand the item as unchanged."""
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    (root / "harness-state" / "bridge-substrate.json").write_text(
        json.dumps({"substrate": daemon.DAEMON_SUBSTRATE}),
        encoding="utf-8",
    )
    _write_bridge(root, "lo-fail-thread", "NEW", 1)
    runtime = daemon._load_dispatch_runtime()
    state_dir = daemon._bridge_poller_state_dir(root)
    index_text = runtime._read_bridge_state_live(root)
    _, lo_items = runtime._compute_actionable(index_text, root)

    target_a = types.SimpleNamespace(
        dispatch_state_key="loyal-opposition:A",
        harness_id="A",
        needed_role_label="loyal-opposition",
        invocation_surfaces={},
    )
    target_c = types.SimpleNamespace(
        dispatch_state_key="loyal-opposition:C",
        harness_id="C",
        needed_role_label="loyal-opposition",
        invocation_surfaces={},
    )
    selected, signature = runtime._target_selected_signature(target_a, lo_items, 1)
    assert [item.document_name for item in selected] == ["lo-fail-thread"]

    dispatch_id = "failed-lo-run"
    runs_dir = state_dir / runtime.DISPATCH_RUNS_SUBDIR
    runs_dir.mkdir(parents=True, exist_ok=True)
    (runs_dir / f"{dispatch_id}.exit_code").write_text("1", encoding="utf-8")
    launched_at = daemon._now_iso()
    runtime._write_dispatch_state(
        state_dir,
        {
            "schema_version": 1,
            "updated_at": launched_at,
            "recipients": {
                target_a.dispatch_state_key: {
                    "updated_at": launched_at,
                    "last_result": "launched",
                    "pending_count": 1,
                    "selected_count": 1,
                    "last_dispatched_signature": signature,
                    "signature": signature,
                    "last_launch": {
                        "dispatch_id": dispatch_id,
                        "recipient": target_a.dispatch_state_key,
                        "launched": True,
                        "launched_at": launched_at,
                        "needed_role_label": "loyal-opposition",
                        "selected_documents": ["lo-fail-thread"],
                        "signature": signature,
                        "status_file_path": str(runs_dir / f"{dispatch_id}.exit_code"),
                    },
                }
            },
        },
    )

    spawn_calls: list[dict] = []

    def _fake_resolve(role_label, *args, **kwargs):
        if role_label == "loyal-opposition":
            return [target_a, target_c]
        return []

    monkeypatch.setattr(runtime, "_resolve_dispatch_targets", _fake_resolve)
    monkeypatch.setattr(runtime, "_is_dispatch_ready", lambda *a, **k: True)
    monkeypatch.setattr(
        runtime,
        "_spawn_harness",
        lambda **kwargs: (
            spawn_calls.append(kwargs)
            or {
                "dispatch_id": "fallback-lo-run",
                "recipient": kwargs["target"].dispatch_state_key,
                "launched": True,
            }
        ),
    )
    monkeypatch.setattr(daemon, "_restart_storm_watchdog", lambda: {"launched": False, "returncode": 0})

    result = daemon.run_tick(root, max_items=1)

    assert result["mode"] == "live"
    assert spawn_calls
    assert spawn_calls[0]["target"].dispatch_state_key == target_c.dispatch_state_key
    lo_decisions = [record for record in result["decisions"] if record["role"] == "loyal-opposition"]
    assert lo_decisions[0]["recipient"] == target_a.dispatch_state_key
    assert lo_decisions[0]["reason"] == "provider_failure_backoff_active"
    assert lo_decisions[1]["recipient"] == target_c.dispatch_state_key
    assert lo_decisions[1]["spawned"] is True

    state = runtime._load_dispatch_state(state_dir, root)
    failed_state = state["recipients"][target_a.dispatch_state_key]
    assert failed_state["last_dispatched_signature"] is None
    assert failed_state["failure_count"] == 1
    assert failed_state["last_result"] == "provider_failure_backoff_active"
    fallback_state = state["recipients"][target_c.dispatch_state_key]
    assert fallback_state["last_launch"]["dispatch_id"] == "fallback-lo-run"


# --- WI-4852: watchdog dormancy detection and fail-soft restart ---------------


_WATCHDOG_HEARTBEAT_TAIL = "codex=0 family=0 noncodex=0 threshold=15 noncodexThreshold=15 mode=liveness-aware(WI-4828)"


def _write_stale_watchdog_heartbeat(root: Path) -> None:
    """Write a watchdog heartbeat old enough to runtime dormancy detection.

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
        assert flags & subprocess.CREATE_NO_WINDOW
    else:
        assert kwargs.get("start_new_session") is True
    assert kwargs.get("stdin") == subprocess.DEVNULL
    assert kwargs.get("stdout") == subprocess.DEVNULL
    assert kwargs.get("stderr") == subprocess.DEVNULL
    expected_exe = gtcli._prefer_windows_gui_python(sys.executable)
    assert captured["args"][0] == expected_exe


def test_daemon_start_refuses_when_live_instance_present(tmp_path: Path) -> None:
    """Defect (2) single-instance: with a live (lock-cleared) daemon process
    recorded in daemon.pid with matching create-time provenance, a second
    ``start`` is refused."""
    from groundtruth_kb import cli as gtcli

    daemon = _load_daemon()
    state_dir = daemon.daemon_state_dir(tmp_path)
    state_dir.mkdir(parents=True, exist_ok=True)
    # Record the current (alive) test-process pid. No lock file is present, so
    # only PID + create-time liveness detection can catch the running instance.
    (state_dir / daemon.PID_FILENAME).write_text(str(os.getpid()) + "\n", encoding="utf-8")
    _write_daemon_pid_provenance(daemon, state_dir, os.getpid())

    cfg_patch, import_patch = _daemon_cli_patches(gtcli, daemon, tmp_path)
    with cfg_patch, import_patch:
        result = CliRunner().invoke(gtcli.bridge_dispatch_daemon_start_cmd, [], obj={})

    # Refusal raises ClickException before the spawn branch; the success branch
    # would instead echo "Started ..." and exit 0.
    assert result.exit_code != 0
    assert "already running" in result.output
    assert "Started" not in result.output


def test_daemon_start_allows_reused_pid_without_matching_provenance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """WI-4893: a daemon.pid pointing at an unrelated live process must not
    block daemon start when create-time provenance mismatches."""
    from groundtruth_kb import cli as gtcli

    daemon = _load_daemon()
    state_dir = daemon.daemon_state_dir(tmp_path)
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / daemon.PID_FILENAME).write_text("4242\n", encoding="utf-8")
    (state_dir / daemon.PID_CREATE_TIME_FILENAME).write_text("123.000000", encoding="utf-8")
    monkeypatch.setattr(daemon, "_pid_is_running", lambda pid: pid == 4242)
    monkeypatch.setattr(daemon, "_pid_create_time_epoch", lambda pid: 456.0 if pid == 4242 else None)
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
    assert "Started" in result.output
    assert captured["args"]


def test_daemon_stop_terminates_legacy_daemon_loop_without_sidecar(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """WI-4893 residual: stop can clean up a pre-provenance daemon loop.

    This is the containment path for the observed storm: a legacy daemon loop
    had no create-time sidecar, so the stop command cleared state while leaving
    the old loop alive. Command-line identity is sufficient to terminate the
    daemon loop, but not unrelated PID reuse.
    """
    from groundtruth_kb import bridge_dispatch_reset
    from groundtruth_kb import cli as gtcli

    daemon = _load_daemon()
    state_dir = daemon.daemon_state_dir(tmp_path)
    state_dir.mkdir(parents=True, exist_ok=True)
    pid = 4242
    (state_dir / daemon.PID_FILENAME).write_text(f"{pid}\n", encoding="utf-8")
    (state_dir / daemon.LOCK_FILENAME).write_text(json.dumps({"pid": pid}), encoding="utf-8")
    command = [
        sys.executable,
        str(tmp_path / "scripts" / "gtkb_dispatcher_daemon.py"),
        "--loop",
        "--project-root",
        str(tmp_path),
    ]
    terminated: list[int] = []

    monkeypatch.setattr(daemon, "_pid_is_running", lambda candidate: candidate == pid)
    monkeypatch.setattr(daemon, "_process_command_line", lambda candidate: command if candidate == pid else [])
    monkeypatch.setattr(daemon, "_matching_daemon_loop_pids", lambda _state_dir: [])
    monkeypatch.setattr(bridge_dispatch_reset, "terminate_pid_tree", lambda candidate: terminated.append(candidate))

    cfg_patch, import_patch = _daemon_cli_patches(gtcli, daemon, tmp_path)
    with cfg_patch, import_patch:
        result = CliRunner().invoke(gtcli.bridge_dispatch_daemon_stop_cmd, [], obj={})

    assert result.exit_code == 0, result.output
    assert terminated == [pid]
    assert "tree terminated" in result.output
    assert not (state_dir / daemon.PID_FILENAME).exists()
    assert not (state_dir / daemon.LOCK_FILENAME).exists()


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
        _write_daemon_pid_provenance(daemon, state_dir, child.pid)
        _write_daemon_lock_record(daemon, state_dir, os.getpid())

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
        assert not (state_dir / daemon.LOCK_FILENAME).exists()
        assert daemon.read_daemon_status(tmp_path).get("running") is not True
    finally:
        if child.poll() is None:
            child.kill()
            child.wait(timeout=10)


def test_daemon_stop_ignores_unverified_pid_and_clears_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """WI-4893: stop must not terminate a PID-only daemon record.

    PID reuse means daemon.pid without create-time provenance is stale evidence.
    The command still clears the stale pid/lock files so operators can recover.
    """
    from groundtruth_kb import bridge_dispatch_reset
    from groundtruth_kb import cli as gtcli

    daemon = _load_daemon()
    state_dir = daemon.daemon_state_dir(tmp_path)
    state_dir.mkdir(parents=True, exist_ok=True)
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
    terminated: list[int] = []
    try:
        (state_dir / daemon.PID_FILENAME).write_text(str(child.pid) + "\n", encoding="utf-8")
        (state_dir / daemon.LOCK_FILENAME).write_text(json.dumps({"pid": child.pid}), encoding="utf-8")
        monkeypatch.setattr(bridge_dispatch_reset, "terminate_pid_tree", lambda pid: terminated.append(pid))

        cfg_patch, import_patch = _daemon_cli_patches(gtcli, daemon, tmp_path)
        with cfg_patch, import_patch:
            result = CliRunner().invoke(gtcli.bridge_dispatch_daemon_stop_cmd, [], obj={})

        assert result.exit_code == 0, result.output
        assert "unverified pid ignored" in result.output
        assert terminated == []
        assert child.poll() is None
        assert not (state_dir / daemon.PID_FILENAME).exists()
        assert not (state_dir / daemon.PID_CREATE_TIME_FILENAME).exists()
        assert not (state_dir / daemon.LOCK_FILENAME).exists()
    finally:
        if child.poll() is None:
            child.kill()
            child.wait(timeout=10)


# ---------------------------------------------------------------------------
# WI-4845/WI-5003: daemon passes a per-role worker --lifetime override so headless
# workers complete (LO Opus floor, PB ~5400s, env-configurable). The cap is
# resolved by runtime.worker_lifetime_seconds and threaded into the spawn
# command (run_with_status.py --lifetime) by runtime._spawn_harness, which the
# daemon's live-spawn path reuses.
# ---------------------------------------------------------------------------


def _spawn_target(runtime, role_label: str, mode: str):
    harness_id = "A" if role_label == "prime-builder" else "D"
    command_handle = "codex" if role_label == "prime-builder" else "ollama"
    return runtime.DispatchTarget(
        needed_role_label=role_label,
        harness_id=harness_id,
        command_handle=command_handle,
        canonical_mode=mode,
        invocation_surfaces={"headless": {"argv": ["worker-cmd", "{{PROMPT}}"]}},
    )


def _capture_worker_command(runtime, target, tmp_path: Path, monkeypatch) -> list[str]:
    """Invoke _spawn_harness with a fake Popen; return the worker command (the
    one wrapping run_with_status.py), robust against any secondary poll spawn."""
    calls: list[tuple] = []

    class _FakeProcess:
        pid = 4242

    def _fake_popen(*args, **kwargs):
        calls.append(args)
        return _FakeProcess()

    monkeypatch.setattr(runtime, "_count_live_dispatched_processes", lambda runs_dir: 0)
    monkeypatch.setattr(runtime, "_is_spawn_rate_limited", lambda runs_dir: False)
    # Prime (implementer) dispatches issue impl-auth packets for the GO item
    # (WI-4770). That is orthogonal to the lifetime feature under test, so pass
    # it for the synthetic item; LO review dispatches do not reach this gate.
    monkeypatch.setattr(
        runtime,
        "_issue_dispatch_authorization_for_selected",
        lambda *a, **k: {"ok": True, "reason": None, "context": {}},
    )
    monkeypatch.setattr(runtime.subprocess, "Popen", _fake_popen)

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
    runtime._spawn_harness(
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


def test_daemon_live_spawns_filter_prime_work_intent_claims(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """WI-4844: daemon live mode must not pass already-claimed Prime work into a worker."""
    daemon = _load_daemon()
    root = _make_codex_prime_project(tmp_path)
    runtime = daemon._load_dispatch_runtime()
    registry = sys.modules["bridge_work_intent_registry"]
    state_dir = daemon._bridge_poller_state_dir(root)
    target = runtime.DispatchTarget(
        needed_role_label="prime-builder",
        harness_id="A",
        command_handle="codex",
        canonical_mode="pb",
        invocation_surfaces=_CODEX_INVOCATION,
    )
    holder_session = "2026-06-22T00-00-00Z-prime-builder-A-abc123"

    for slug in ("held-thread", "open-thread"):
        _write_go_thread(root, slug)
    assert registry.acquire("held-thread", holder_session, project_root=root)

    selected = [
        types.SimpleNamespace(document_name="held-thread", top_status="GO", top_file="bridge/held-thread-002.md"),
        types.SimpleNamespace(document_name="open-thread", top_status="GO", top_file="bridge/open-thread-002.md"),
    ]
    captured_documents: list[str] = []

    def _fake_spawn_harness(**kwargs):
        captured_documents.extend(item.document_name for item in kwargs["items"])
        return {
            "dispatch_id": kwargs.get("dispatch_id"),
            "recipient": kwargs["target"].dispatch_state_key,
            "launched": False,
            "reason": "synthetic_launch_failed",
        }

    monkeypatch.setattr(runtime, "_spawn_harness", _fake_spawn_harness)

    result = daemon._execute_live_spawns(
        root,
        [
            {
                "role": "prime-builder",
                "recipient": target.dispatch_state_key,
                "signature": runtime._signature(selected),
                "_spawn_target": target,
                "_spawn_selected": selected,
            }
        ],
        max_items=2,
        dry_run=False,
    )

    assert captured_documents == ["open-thread"]
    assert result[0]["work_intent_slugs"] == ["open-thread"]
    assert registry.current_holder("open-thread", project_root=root) is None
    state = runtime._load_dispatch_state(state_dir, root)
    recipient_state = state["recipients"][target.dispatch_state_key]
    assert recipient_state["work_intent_held_filtered_count"] == 1
    assert recipient_state["pending_count"] == 1
    assert recipient_state["selected_count"] == 0


def test_wi4994_daemon_prime_fanout_launches_independent_documents(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    daemon = _load_daemon()
    root = _make_codex_prime_project(tmp_path)
    runtime = daemon._load_dispatch_runtime()
    for slug in ("first-pb-thread", "second-pb-thread"):
        _write_go_thread(root, slug)
    launched_batches: list[list[str]] = []

    def _fake_spawn_harness(**kwargs):
        launched_batches.append([item.document_name for item in kwargs["items"]])
        return {
            "dispatch_id": kwargs.get("dispatch_id"),
            "recipient": kwargs["target"].dispatch_state_key,
            "launched": True,
            "reason": "launched",
        }

    monkeypatch.setattr(runtime, "_is_dispatch_ready", lambda *args, **kwargs: True)
    monkeypatch.setattr(runtime, "_spawn_harness", _fake_spawn_harness)

    result = daemon.run_tick(root, max_items=2)

    assert result["mode"] == "live"
    assert len(launched_batches) == 2
    assert all(len(batch) == 1 for batch in launched_batches)
    assert {batch[0] for batch in launched_batches} == {"first-pb-thread", "second-pb-thread"}
    sessions = [item["work_intent_session_id"] for item in result["spawn_results"]]
    assert len(set(sessions)) == 2
    state = runtime._load_dispatch_state(daemon._bridge_poller_state_dir(root), root)
    recipient_state = state["recipients"]["prime-builder:A"]
    assert recipient_state["fanout_launched_count"] == 2
    assert set(recipient_state["last_dispatched_signatures_by_document"]) == {"first-pb-thread", "second-pb-thread"}


def test_wi4994_daemon_prime_fanout_held_document_does_not_block_later_unheld(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    daemon = _load_daemon()
    root = _make_codex_prime_project(tmp_path)
    runtime = daemon._load_dispatch_runtime()
    registry = sys.modules["bridge_work_intent_registry"]
    for slug in ("held-pb-thread", "free-pb-thread"):
        _write_go_thread(root, slug)
    holder_session = "2026-07-03T12-00-00Z-prime-builder-A-held"
    from gtkb_session_id import per_session_role_marker_path

    marker_path = per_session_role_marker_path(root, holder_session)
    marker_path.parent.mkdir(parents=True, exist_ok=True)
    marker_path.write_text(json.dumps({"role": "prime-builder", "session_id": holder_session}), encoding="utf-8")
    assert registry.acquire("held-pb-thread", holder_session, project_root=root)
    launched_docs: list[str] = []

    def _fake_spawn_harness(**kwargs):
        launched_docs.extend(item.document_name for item in kwargs["items"])
        return {
            "dispatch_id": kwargs.get("dispatch_id"),
            "recipient": kwargs["target"].dispatch_state_key,
            "launched": True,
            "reason": "launched",
        }

    monkeypatch.setattr(runtime, "_is_dispatch_ready", lambda *args, **kwargs: True)
    monkeypatch.setattr(runtime, "_spawn_harness", _fake_spawn_harness)

    result = daemon.run_tick(root, max_items=2)

    assert launched_docs == ["free-pb-thread"]
    reasons = [item.get("reason") for item in result["spawn_results"]]
    assert "work_intent_already_held" in reasons
    assert "launched" in reasons
    state = runtime._load_dispatch_state(daemon._bridge_poller_state_dir(root), root)
    recipient_state = state["recipients"]["prime-builder:A"]
    assert recipient_state["fanout_skipped_held_count"] == 1
    assert recipient_state["fanout_launched_count"] == 1


def test_wi4994_daemon_prime_fanout_dedupes_same_document_not_different_document(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    daemon = _load_daemon()
    root = _make_codex_prime_project(tmp_path)
    runtime = daemon._load_dispatch_runtime()
    state_dir = daemon._bridge_poller_state_dir(root)
    target = runtime.DispatchTarget(
        needed_role_label="prime-builder",
        harness_id="A",
        command_handle="codex",
        canonical_mode="pb",
        invocation_surfaces=_CODEX_INVOCATION,
    )
    selected_a = [types.SimpleNamespace(document_name="same-thread", top_status="GO", top_file="bridge/same-002.md")]
    selected_b = [
        types.SimpleNamespace(document_name="different-thread", top_status="GO", top_file="bridge/diff-002.md")
    ]
    for slug in ("same-thread", "different-thread"):
        _write_go_thread(root, slug)
    sig_a = runtime._signature(selected_a)
    sig_b = runtime._signature(selected_b)
    state_dir.mkdir(parents=True, exist_ok=True)
    runtime._write_dispatch_state(
        state_dir,
        {
            "schema_version": 1,
            "updated_at": daemon._now_iso(),
            "recipients": {
                "prime-builder:A": {
                    "last_dispatched_signatures_by_document": {"same-thread": sig_a},
                }
            },
        },
    )
    launched_docs: list[str] = []

    def _fake_spawn_harness(**kwargs):
        launched_docs.extend(item.document_name for item in kwargs["items"])
        return {
            "dispatch_id": kwargs.get("dispatch_id"),
            "recipient": kwargs["target"].dispatch_state_key,
            "launched": True,
            "reason": "launched",
        }

    monkeypatch.setattr(runtime, "_spawn_harness", _fake_spawn_harness)

    results = daemon._execute_live_spawns(
        root,
        [
            {
                "role": "prime-builder",
                "recipient": target.dispatch_state_key,
                "signature": sig_a,
                "_spawn_target": target,
                "_spawn_selected": selected_a,
            },
            {
                "role": "prime-builder",
                "recipient": target.dispatch_state_key,
                "signature": sig_b,
                "_spawn_target": target,
                "_spawn_selected": selected_b,
            },
        ],
        max_items=1,
        dry_run=False,
    )

    assert [item.get("reason") for item in results] == ["unchanged", "launched"]
    assert launched_docs == ["different-thread"]


def test_wi5002_daemon_prime_fanout_unchanged_clears_stale_failure_fields(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    daemon = _load_daemon()
    root = _make_codex_prime_project(tmp_path)
    runtime = daemon._load_dispatch_runtime()
    state_dir = daemon._bridge_poller_state_dir(root)
    target = runtime.DispatchTarget(
        needed_role_label="prime-builder",
        harness_id="A",
        command_handle="codex",
        canonical_mode="pb",
        invocation_surfaces=_CODEX_INVOCATION,
    )
    selected = [types.SimpleNamespace(document_name="same-thread", top_status="GO", top_file="bridge/same-002.md")]
    _write_go_thread(root, "same-thread")
    signature = runtime._signature(selected)
    state_dir.mkdir(parents=True, exist_ok=True)
    runtime._write_dispatch_state(
        state_dir,
        {
            "schema_version": 1,
            "updated_at": daemon._now_iso(),
            "recipients": {
                "prime-builder:A": {
                    "last_dispatched_signatures_by_document": {"same-thread": signature},
                    "failure_class": "subprocess_execution_failed",
                    "last_failure_reason": "subprocess_execution_failed",
                }
            },
        },
    )

    monkeypatch.setattr(runtime, "_spawn_harness", lambda **kwargs: pytest.fail("unchanged branch must not spawn"))

    results = daemon._execute_live_spawns(
        root,
        [
            {
                "role": "prime-builder",
                "recipient": target.dispatch_state_key,
                "signature": signature,
                "_spawn_target": target,
                "_spawn_selected": selected,
            },
        ],
        max_items=1,
        dry_run=False,
    )

    assert [item.get("reason") for item in results] == ["unchanged"]
    recipient_state = runtime._load_dispatch_state(state_dir, root)["recipients"]["prime-builder:A"]
    assert recipient_state["last_result"] == "unchanged"
    assert "failure_class" not in recipient_state
    assert "last_failure_reason" not in recipient_state


def test_wi4994_daemon_prime_fanout_records_at_cap_per_spawn_attempt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    daemon = _load_daemon()
    root = _make_codex_prime_project(tmp_path)
    runtime = daemon._load_dispatch_runtime()
    for slug in ("first-cap-thread", "second-cap-thread"):
        _write_go_thread(root, slug)
    call_count = 0

    def _fake_spawn_harness(**kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return {
                "dispatch_id": kwargs.get("dispatch_id"),
                "recipient": kwargs["target"].dispatch_state_key,
                "launched": True,
                "reason": "launched",
            }
        return {
            "dispatch_id": kwargs.get("dispatch_id"),
            "recipient": kwargs["target"].dispatch_state_key,
            "launched": False,
            "reason": "per_role_concurrency_cap_reached",
        }

    monkeypatch.setattr(runtime, "_is_dispatch_ready", lambda *args, **kwargs: True)
    monkeypatch.setattr(runtime, "_spawn_harness", _fake_spawn_harness)

    result = daemon.run_tick(root, max_items=2)

    assert [item.get("reason") for item in result["spawn_results"]] == [
        "launched",
        "per_role_concurrency_cap_reached",
    ]
    state = runtime._load_dispatch_state(daemon._bridge_poller_state_dir(root), root)
    recipient_state = state["recipients"]["prime-builder:A"]
    assert recipient_state["fanout_launched_count"] == 1
    assert recipient_state["fanout_at_cap_count"] == 1


def test_wi4992_daemon_all_impl_auth_quarantine_suppresses_until_signature_changes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    daemon = _load_daemon()
    root = _make_codex_prime_project(tmp_path)
    runtime = daemon._load_dispatch_runtime()
    target = runtime.DispatchTarget(
        needed_role_label="prime-builder",
        harness_id="A",
        command_handle="codex",
        canonical_mode="pb",
        invocation_surfaces=_CODEX_INVOCATION,
    )
    selected = [
        types.SimpleNamespace(document_name="auth-quarantined-thread", top_status="GO", top_file="bridge/auth-002.md")
    ]
    _write_go_thread(root, "auth-quarantined-thread")
    spawn_calls = 0

    def _fake_issue(*args, **kwargs):
        return {
            "ok": False,
            "reason": "all_impl_auth_quarantined",
            "failed_slug": "auth-quarantined-thread",
            "error": "new requirements required",
        }

    def _unexpected_popen(*args, **kwargs):
        raise AssertionError("impl-auth quarantine must not launch a worker")

    monkeypatch.setattr(runtime, "_issue_dispatch_authorization_for_selected", _fake_issue)
    monkeypatch.setattr(runtime.subprocess, "Popen", _unexpected_popen)
    real_spawn = runtime._spawn_harness

    def _counting_spawn(**kwargs):
        nonlocal spawn_calls
        spawn_calls += 1
        return real_spawn(**kwargs)

    monkeypatch.setattr(runtime, "_spawn_harness", _counting_spawn)
    decision = {
        "role": "prime-builder",
        "recipient": target.dispatch_state_key,
        "signature": runtime._signature(selected),
        "_spawn_target": target,
        "_spawn_selected": selected,
    }

    first = daemon._execute_live_spawns(root, [decision], max_items=1, dry_run=False)
    second = daemon._execute_live_spawns(root, [decision], max_items=1, dry_run=False)

    assert spawn_calls == 1
    assert first[0]["reason"] == "all_impl_auth_quarantined"
    assert second[0]["reason"] == "all_impl_auth_quarantined"
    state = runtime._load_dispatch_state(daemon._bridge_poller_state_dir(root), root)
    recipient_state = state["recipients"]["prime-builder:A"]
    assert recipient_state["fanout_impl_auth_quarantined_count"] == 1
    assert recipient_state["impl_auth_quarantined_signatures_by_document"]["auth-quarantined-thread"]


def test_wi4992_daemon_impl_auth_quarantine_does_not_block_implementable_document(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    daemon = _load_daemon()
    root = _make_codex_prime_project(tmp_path)
    runtime = daemon._load_dispatch_runtime()
    for slug in ("blocked-auth-thread", "implementable-thread"):
        _write_go_thread(root, slug)
    launched_docs: list[str] = []

    def _fake_issue(selected, **kwargs):
        bridge_id = selected[0].document_name
        if bridge_id == "blocked-auth-thread":
            return {
                "ok": False,
                "reason": "all_impl_auth_quarantined",
                "failed_slug": bridge_id,
                "error": "new requirements required",
            }
        return {
            "ok": True,
            "reason": None,
            "context": {
                "bridge_ids": [bridge_id],
                "current_bridge_id": bridge_id,
                "packets": [{"bridge_id": bridge_id, "packet_hash": f"hash-{bridge_id}"}],
            },
        }

    class _FakeProcess:
        pid = 4242

    def _fake_popen(*args, **kwargs):
        launched_docs.append(kwargs["env"]["GTKB_IMPLEMENTATION_AUTH_CURRENT_BRIDGE_ID"])
        return _FakeProcess()

    monkeypatch.setattr(runtime, "_is_dispatch_ready", lambda *args, **kwargs: True)
    monkeypatch.setattr(runtime, "_issue_dispatch_authorization_for_selected", _fake_issue)
    monkeypatch.setattr(runtime.subprocess, "Popen", _fake_popen)
    monkeypatch.setattr(runtime, "_pid_create_time_epoch", lambda pid: 123.0)

    result = daemon.run_tick(root, max_items=2)

    result_reasons = [
        item.get("reason") or ("launched" if item.get("launched") else None) for item in result["spawn_results"]
    ]
    assert sorted(result_reasons) == ["all_impl_auth_quarantined", "launched"]
    assert launched_docs == ["implementable-thread"]
    state = runtime._load_dispatch_state(daemon._bridge_poller_state_dir(root), root)
    recipient_state = state["recipients"]["prime-builder:A"]
    assert recipient_state["fanout_impl_auth_quarantined_count"] == 1
    assert recipient_state["fanout_launched_count"] == 1


def test_daemon_execute_live_spawns_reconciles_terminal_bridge_residue(tmp_path: Path) -> None:
    """WI-4935: daemon-owned state writes clear stale failover rows for terminal docs."""
    daemon = _load_daemon()
    root = _make_codex_prime_project(tmp_path)
    runtime = daemon._load_dispatch_runtime()
    state_dir = daemon._bridge_poller_state_dir(root)
    _write_bridge(root, "done-thread", "NEW", 1)
    _write_bridge(root, "done-thread", "VERIFIED", 2)
    (root / "bridge" / "INDEX.md").write_text(
        "# bridge index\n\nDocument: done-thread\nVERIFIED: bridge/done-thread-002.md\nNEW: bridge/done-thread-001.md\n",
        encoding="utf-8",
    )
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "dispatch-state.json").write_text(
        json.dumps(
            {
                "recipients": {
                    "loyal-opposition:B": {
                        "last_result": "subprocess_execution_failed",
                        "failure_class": "subprocess_execution_failed",
                        "failure_count": 2,
                        "circuit_breaker_tripped": True,
                        "pending_count": 1,
                        "selected_count": 1,
                        "last_launch": {
                            "dispatch_id": "prior-claude",
                            "recipient": "loyal-opposition:B",
                            "launched": True,
                            "primary_bridge_id": "done-thread",
                            "selected_documents": ["done-thread"],
                            "signature": "stale-signature",
                            "exit_failure_reason": "subprocess_execution_failed",
                        },
                    }
                },
                "schema_version": 1,
                "updated_at": "2026-06-30T09:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )

    result = daemon._execute_live_spawns(root, [], max_items=2, dry_run=False)

    assert result == []
    state = runtime._load_dispatch_state(state_dir, root)
    recipient_state = state["recipients"]["loyal-opposition:B"]
    assert recipient_state["last_result"] == "terminal_bridge_reconciled"
    assert recipient_state["pending_count"] == 0
    assert recipient_state["selected_count"] == 0
    assert recipient_state["failure_count"] == 0
    assert recipient_state["circuit_breaker_tripped"] is False
    assert "failure_class" not in recipient_state


def test_daemon_live_skips_owner_hold_prime_no_go(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    daemon = _load_daemon()
    root = _make_codex_prime_project(tmp_path)
    (root / "harness-state" / "bridge-substrate.json").write_text(
        json.dumps({"substrate": daemon.DAEMON_SUBSTRATE}),
        encoding="utf-8",
    )
    doc = "owner-hold-thread"
    _write_bridge(root, doc, "NEW", 1)
    (root / "bridge" / f"{doc}-002.md").write_text(
        "NO-GO\n\n## Required Revisions\n\n1. **Hold for Owner Decision:** wait for the topology decision.\n",
        encoding="utf-8",
    )
    (root / "bridge" / "INDEX.md").write_text(
        f"# bridge index\n\nDocument: {doc}\nNO-GO: bridge/{doc}-002.md\nNEW: bridge/{doc}-001.md\n",
        encoding="utf-8",
    )
    runtime = daemon._load_dispatch_runtime()
    spawn_calls: list[dict] = []

    monkeypatch.setattr(runtime, "_is_dispatch_ready", lambda *a, **k: True)
    monkeypatch.setattr(runtime, "_spawn_harness", lambda **kwargs: spawn_calls.append(kwargs))

    result = daemon.run_tick(root, max_items=2)

    assert result["mode"] == "live"
    assert spawn_calls == []
    decision = next(record for record in result["decisions"] if record["role"] == "prime-builder")
    assert decision["would_dispatch"] == []
    state = runtime._load_dispatch_state(daemon._bridge_poller_state_dir(root), root)
    recipient_state = state["recipients"]["prime-builder:A"]
    assert recipient_state["last_result"] == "no_pending"
    assert recipient_state["pending_count"] == 0
    assert recipient_state["selected_count"] == 0


def test_daemon_live_skips_headless_ineligible_prime_no_go(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    daemon = _load_daemon()
    root = _make_codex_prime_project(tmp_path)
    (root / "harness-state" / "bridge-substrate.json").write_text(
        json.dumps({"substrate": daemon.DAEMON_SUBSTRATE}),
        encoding="utf-8",
    )
    doc = "headless-ineligible-thread"
    (root / "bridge" / f"{doc}-001.md").write_text(
        "NEW\n\nbridge_kind: implementation_proposal\nauthor_session_context_id: fixture-author-session\n",
        encoding="utf-8",
    )
    (root / "bridge" / f"{doc}-002.md").write_text(
        "\n".join(
            [
                "NO-GO",
                "",
                "The dispatch loop must be broken. Every headless Codex auto-dispatch for this thread",
                "produces the same ACL deny; the dispatcher re-queues for Codex; the cycle repeats.",
                "Do not re-dispatch to Codex headless for this specific task until ACL remediation is confirmed.",
            ]
        ),
        encoding="utf-8",
    )
    (root / "bridge" / "INDEX.md").write_text(
        f"# bridge index\n\nDocument: {doc}\nNO-GO: bridge/{doc}-002.md\nNEW: bridge/{doc}-001.md\n",
        encoding="utf-8",
    )
    runtime = daemon._load_dispatch_runtime()
    spawn_calls: list[dict] = []

    monkeypatch.setattr(runtime, "_is_dispatch_ready", lambda *a, **k: True)
    monkeypatch.setattr(runtime, "_spawn_harness", lambda **kwargs: spawn_calls.append(kwargs))

    result = daemon.run_tick(root, max_items=2)

    assert result["mode"] == "live"
    assert spawn_calls == []
    decision = next(record for record in result["decisions"] if record["role"] == "prime-builder")
    assert decision["would_dispatch"] == []
    state = runtime._load_dispatch_state(daemon._bridge_poller_state_dir(root), root)
    recipient_state = state["recipients"]["prime-builder:A"]
    assert recipient_state["last_result"] == "no_pending"
    assert recipient_state["pending_count"] == 0
    assert recipient_state["selected_count"] == 0


def test_daemon_spawn_passes_per_role_lifetime(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The daemon live-spawn command carries the per-role --lifetime override:
    LO target -> Opus floor, PB target -> 5400s."""
    daemon = _load_daemon()
    runtime = daemon._load_dispatch_runtime()
    monkeypatch.delenv(runtime.LO_WORKER_LIFETIME_ENV_VAR, raising=False)
    monkeypatch.delenv(runtime.PB_WORKER_LIFETIME_ENV_VAR, raising=False)

    lo_cmd = _capture_worker_command(runtime, _spawn_target(runtime, "loyal-opposition", "lo"), tmp_path, monkeypatch)
    assert runtime.LO_REVIEW_WORKER_LIFETIME_SECONDS == runtime.OPUS_CLASS_WORKER_LIFETIME_FLOOR_SECONDS == 3600
    assert _lifetime_value(lo_cmd) == str(runtime.LO_REVIEW_WORKER_LIFETIME_SECONDS)

    pb_cmd = _capture_worker_command(runtime, _spawn_target(runtime, "prime-builder", "pb"), tmp_path, monkeypatch)
    assert _lifetime_value(pb_cmd) == str(runtime.PB_IMPL_WORKER_LIFETIME_SECONDS) == "5400"


def test_daemon_worker_lifetime_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """GTKB_WORKER_LIFETIME_LO_SECONDS / _PB_SECONDS override the per-role
    defaults; invalid/non-positive falls back; other roles get no cap (WI-4845)."""
    daemon = _load_daemon()
    runtime = daemon._load_dispatch_runtime()

    monkeypatch.delenv(runtime.LO_WORKER_LIFETIME_ENV_VAR, raising=False)
    monkeypatch.delenv(runtime.PB_WORKER_LIFETIME_ENV_VAR, raising=False)
    assert runtime.worker_lifetime_seconds("loyal-opposition") == runtime.OPUS_CLASS_WORKER_LIFETIME_FLOOR_SECONDS
    assert runtime.worker_lifetime_seconds("prime-builder") == 5400
    assert runtime.worker_lifetime_seconds("some-other-role") is None
    assert runtime.worker_lifetime_seconds(None) is None

    monkeypatch.setenv(runtime.LO_WORKER_LIFETIME_ENV_VAR, "2400")
    monkeypatch.setenv(runtime.PB_WORKER_LIFETIME_ENV_VAR, "7200")
    assert runtime.worker_lifetime_seconds("loyal-opposition") == 2400
    assert runtime.worker_lifetime_seconds("prime-builder") == 7200

    monkeypatch.setenv(runtime.LO_WORKER_LIFETIME_ENV_VAR, "0")
    monkeypatch.setenv(runtime.PB_WORKER_LIFETIME_ENV_VAR, "not-an-int")
    assert runtime.worker_lifetime_seconds("loyal-opposition") == runtime.OPUS_CLASS_WORKER_LIFETIME_FLOOR_SECONDS
    assert runtime.worker_lifetime_seconds("prime-builder") == 5400


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
    _set_manual_substrate(root)
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


# ---------------------------------------------------------------------------
# WI-4857: reap_inflight_dispatched_workers + _reap_dispatched_workers tests
# ---------------------------------------------------------------------------


def _make_runs_dir(root: Path) -> Path:
    """Return the bridge-poller dispatch-runs directory (created on demand)."""
    daemon = _load_daemon()
    runtime = daemon._load_dispatch_runtime()
    runs_dir = daemon._bridge_poller_state_dir(root) / runtime.DISPATCH_RUNS_SUBDIR
    runs_dir.mkdir(parents=True, exist_ok=True)
    return runs_dir


def _write_pid_provenance_sidecar(runs_dir: Path, dispatch_id: str, pid: int) -> None:
    create_time = float(psutil.Process(pid).create_time())
    (runs_dir / f"{dispatch_id}.create_time_epoch").write_text(f"{create_time:.6f}", encoding="utf-8")


def _write_daemon_pid_provenance(daemon, state_dir: Path, pid: int) -> None:
    create_time = float(psutil.Process(pid).create_time())
    (state_dir / daemon.PID_CREATE_TIME_FILENAME).write_text(f"{create_time:.6f}", encoding="utf-8")


def _write_daemon_lock_record(daemon, state_dir: Path, pid: int) -> None:
    create_time = float(psutil.Process(pid).create_time())
    payload = {
        "pid": pid,
        "pid_create_time_epoch": create_time,
        "acquired_at": "2026-06-29T00:00:00Z",
        "mode": "shadow",
    }
    (state_dir / daemon.LOCK_FILENAME).write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def test_reap_inflight_terminates_live_worker(tmp_path: Path) -> None:
    """A live worker with no exit_code sidecar is terminated and recorded.

    Spec-derived from WI-4857: ``reap_inflight_dispatched_workers`` must
    terminate the process, write exit_code "124", and return count 1.
    """
    daemon = _load_daemon()
    runtime = daemon._load_dispatch_runtime()
    runs_dir = _make_runs_dir(tmp_path)

    # Spawn a real long-lived sleeper so we have a live PID to reap.
    sleeper = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(60)"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    dispatch_id = "test-dispatch-live-001"
    try:
        (runs_dir / f"{dispatch_id}.pid").write_text(str(sleeper.pid) + "\n", encoding="utf-8")
        _write_pid_provenance_sidecar(runs_dir, dispatch_id, sleeper.pid)
        # No exit_code sidecar — simulates an orphaned worker.
        reaped = runtime.reap_inflight_dispatched_workers(runs_dir)
        assert reaped == 1
        exit_code_file = runs_dir / f"{dispatch_id}.exit_code"
        assert exit_code_file.exists(), "exit_code sidecar must be written"
        assert exit_code_file.read_text(encoding="utf-8").strip() == "124"
        # Process should be dead now.
        sleeper.wait(timeout=5)
    finally:
        if sleeper.poll() is None:
            sleeper.terminate()
            sleeper.wait(timeout=5)


def test_reap_inflight_refuses_live_worker_without_provenance(tmp_path: Path) -> None:
    """A live PID without create-time provenance is not terminated.

    Spec-derived from WI-4893 and the WI-4834 provenance precedent: PID-only
    evidence is insufficient because PID reuse can target the wrong process.
    """
    daemon = _load_daemon()
    runtime = daemon._load_dispatch_runtime()
    runs_dir = _make_runs_dir(tmp_path)

    sleeper = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(60)"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    dispatch_id = "test-dispatch-missing-provenance-001"
    try:
        (runs_dir / f"{dispatch_id}.pid").write_text(str(sleeper.pid) + "\n", encoding="utf-8")
        reaped = runtime.reap_inflight_dispatched_workers(runs_dir)
        assert reaped == 0
        assert sleeper.poll() is None, "PID-only evidence must not terminate a live process"
        assert not (runs_dir / f"{dispatch_id}.exit_code").exists()
    finally:
        if sleeper.poll() is None:
            sleeper.terminate()
            sleeper.wait(timeout=5)


def test_reap_inflight_skips_completed_worker(tmp_path: Path) -> None:
    """A live worker whose exit_code sidecar is already populated is not reaped.

    Spec-derived from WI-4857: already-exited workers must not be disturbed.
    """
    daemon = _load_daemon()
    runtime = daemon._load_dispatch_runtime()
    runs_dir = _make_runs_dir(tmp_path)

    sleeper = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(60)"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    dispatch_id = "test-dispatch-completed-002"
    try:
        (runs_dir / f"{dispatch_id}.pid").write_text(str(sleeper.pid) + "\n", encoding="utf-8")
        _write_pid_provenance_sidecar(runs_dir, dispatch_id, sleeper.pid)
        # Pre-populate exit_code — worker already recorded its outcome.
        (runs_dir / f"{dispatch_id}.exit_code").write_text("0\n", encoding="utf-8")
        reaped = runtime.reap_inflight_dispatched_workers(runs_dir)
        assert reaped == 0
        # Process must still be alive (we did not kill it).
        assert sleeper.poll() is None, "completed worker must not be killed"
    finally:
        sleeper.terminate()
        sleeper.wait(timeout=5)


def test_reap_inflight_skips_dead_pid(tmp_path: Path) -> None:
    """A sidecar whose PID is already dead produces no reap and no error.

    Spec-derived from WI-4857: dead-PID sidecars (stale orphans) are safe to
    skip and must not cause ``reap_inflight_dispatched_workers`` to raise.
    """
    daemon = _load_daemon()
    runtime = daemon._load_dispatch_runtime()
    runs_dir = _make_runs_dir(tmp_path)

    # Spawn and immediately wait so the PID is definitely dead.
    gone = subprocess.Popen(
        [sys.executable, "-c", "raise SystemExit(0)"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    gone.wait(timeout=10)
    dead_pid = gone.pid

    dispatch_id = "test-dispatch-dead-003"
    (runs_dir / f"{dispatch_id}.pid").write_text(str(dead_pid) + "\n", encoding="utf-8")
    # No exit_code sidecar.
    reaped = runtime.reap_inflight_dispatched_workers(runs_dir)
    assert reaped == 0
    exit_code_file = runs_dir / f"{dispatch_id}.exit_code"
    assert not exit_code_file.exists(), "no exit_code should be written for a dead PID"


def test_daemon_reap_helper_reaps_orphan(tmp_path: Path) -> None:
    """_reap_dispatched_workers terminates a live orphan under the bridge-poller dir.

    Spec-derived from WI-4857: the daemon-level wrapper resolves the correct
    runs_dir path and delegates to the runtime helper successfully.
    """
    daemon = _load_daemon()
    runs_dir = _make_runs_dir(tmp_path)

    sleeper = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(60)"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    dispatch_id = "test-daemon-orphan-004"
    try:
        (runs_dir / f"{dispatch_id}.pid").write_text(str(sleeper.pid) + "\n", encoding="utf-8")
        _write_pid_provenance_sidecar(runs_dir, dispatch_id, sleeper.pid)
        # No exit_code sidecar — simulate orphaned worker.
        reaped = daemon._reap_dispatched_workers(tmp_path)
        assert reaped == 1
        exit_code_file = runs_dir / f"{dispatch_id}.exit_code"
        assert exit_code_file.exists()
        assert exit_code_file.read_text(encoding="utf-8").strip() == "124"
        sleeper.wait(timeout=5)
    finally:
        if sleeper.poll() is None:
            sleeper.terminate()
            sleeper.wait(timeout=5)
