"""Tests for dispatcher daemon substrate doctor check (WI-4848 slice 3c)."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from groundtruth_kb.project.doctor import _check_dispatcher_daemon_substrate_readiness


def _write_fresh_heartbeat(state_dir: Path) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "daemon.lock").write_text("{}", encoding="utf-8")
    fresh = dt.datetime.now(dt.UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    (state_dir / "heartbeat.txt").write_text(fresh + "\n", encoding="utf-8")


def test_doctor_dispatcher_substrate_mismatch_warns(tmp_path: Path) -> None:
    root = tmp_path
    (root / "scripts").mkdir()
    (root / "scripts" / "gtkb_dispatcher_daemon.py").write_text(
        (Path(__file__).resolve().parents[2] / "scripts" / "gtkb_dispatcher_daemon.py").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (root / "harness-state").mkdir()
    (root / "harness-state" / "bridge-substrate.json").write_text(
        json.dumps({"substrate": "dispatcher_daemon"}),
        encoding="utf-8",
    )
    result = _check_dispatcher_daemon_substrate_readiness(root)
    assert result.status == "warning"
    assert "not healthy" in result.message


def test_doctor_dispatcher_substrate_healthy_ok(tmp_path: Path) -> None:
    root = tmp_path
    (root / "scripts").mkdir()
    (root / "scripts" / "gtkb_dispatcher_daemon.py").write_text(
        (Path(__file__).resolve().parents[2] / "scripts" / "gtkb_dispatcher_daemon.py").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (root / "harness-state").mkdir()
    (root / "harness-state" / "bridge-substrate.json").write_text(
        json.dumps({"substrate": "dispatcher_daemon"}),
        encoding="utf-8",
    )
    _write_fresh_heartbeat(root / ".gtkb-state" / "dispatcher-daemon")
    result = _check_dispatcher_daemon_substrate_readiness(root)
    assert result.status == "pass"
    assert "fresh" in result.message


def test_rollback_runbook_exists_and_cites_governed_command() -> None:
    root = Path(__file__).resolve().parents[2]
    runbook = root / ".claude" / "rules" / "dispatcher-daemon-substrate-rollback-runbook.md"
    text = runbook.read_text(encoding="utf-8")
    assert "dispatcher daemon is the only automated bridge-dispatch substrate" in text
    assert "manual owner assignment/scanning" in text
    assert "gt bridge dispatch health" in text
    assert "gt bridge dispatch daemon status" in text
