# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scripts/gtkb_dispatcher_heartbeat.py (WI-4787)."""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_HEARTBEAT_PATH = _REPO_ROOT / "scripts" / "gtkb_dispatcher_heartbeat.py"
_DAEMON_PATH = _REPO_ROOT / "scripts" / "gtkb_dispatcher_daemon.py"


def _load_heartbeat():
    spec = importlib.util.spec_from_file_location("gtkb_dispatcher_heartbeat_test", _HEARTBEAT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_daemon():
    spec = importlib.util.spec_from_file_location("gtkb_dispatcher_daemon_hb_test", _DAEMON_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _make_project(root: Path) -> Path:
    (root / "groundtruth.toml").write_text('[project]\nproject_name = "HB"\n', encoding="utf-8")
    return root


def test_heartbeat_watchdog_flags_stale_daemon(tmp_path: Path) -> None:
    hb = _load_heartbeat()
    daemon = _load_daemon()
    root = _make_project(tmp_path)
    state_dir = daemon.daemon_state_dir(root)
    state_dir.mkdir(parents=True, exist_ok=True)
    stale_at = (
        (dt.datetime.now(dt.UTC) - dt.timedelta(seconds=300)).isoformat(timespec="seconds").replace("+00:00", "Z")
    )
    (state_dir / daemon.HEARTBEAT_FILENAME).write_text(stale_at + "\n", encoding="utf-8")
    evaluation = hb.evaluate_heartbeat(root, stale_seconds=180)
    assert evaluation["stale"] is True
    assert evaluation["reason"] == "daemon_stale"
    hb.append_alert(state_dir, evaluation)
    alerts = (state_dir / hb.ALERTS_FILENAME).read_text(encoding="utf-8").splitlines()
    assert alerts
    assert json.loads(alerts[-1])["reason"] == "daemon_stale"

    fresh_at = dt.datetime.now(dt.UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    (state_dir / daemon.HEARTBEAT_FILENAME).write_text(fresh_at + "\n", encoding="utf-8")
    fresh = hb.evaluate_heartbeat(root, stale_seconds=180)
    assert fresh["stale"] is False
    assert fresh["reason"] == "heartbeat_fresh"


def test_heartbeat_watchdog_runs_without_daemon_process(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    hb = _load_heartbeat()
    root = _make_project(tmp_path)
    hb_path = root / ".gtkb-state" / "dispatcher-daemon" / "heartbeat.txt"
    hb_path.parent.mkdir(parents=True, exist_ok=True)
    hb_path.write_text("not-a-timestamp\n", encoding="utf-8")

    def _boom():
        raise RuntimeError("daemon import blocked")

    monkeypatch.setattr("gtkb_dispatcher_daemon._load_trigger_module", _boom, raising=False)
    evaluation = hb.evaluate_heartbeat(root)
    assert evaluation["reason"] == "heartbeat_unreadable"
