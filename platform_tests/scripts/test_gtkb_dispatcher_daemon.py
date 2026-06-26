# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scripts/gtkb_dispatcher_daemon.py (WI-4787)."""

from __future__ import annotations

import importlib.util
import json
import time
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
