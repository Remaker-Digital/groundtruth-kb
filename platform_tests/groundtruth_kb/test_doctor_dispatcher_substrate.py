"""Tests for dispatcher daemon substrate doctor check (WI-4848 slice 3c)."""

from __future__ import annotations

import json
from pathlib import Path

from groundtruth_kb.project import doctor as doctor_mod
from groundtruth_kb.project.doctor import _check_dispatcher_daemon_substrate_readiness


def _write_dispatcher_daemon_substrate(root: Path) -> None:
    (root / "harness-state").mkdir()
    (root / "harness-state" / "bridge-substrate.json").write_text(
        json.dumps({"substrate": "dispatcher_daemon"}),
        encoding="utf-8",
    )


def _write_daemon_status_script(root: Path, *, running: bool, heartbeat_age: float | None) -> None:
    status = {"running": running, "heartbeat_age_seconds": heartbeat_age}
    (root / "scripts").mkdir()
    (root / "scripts" / "gtkb_dispatcher_daemon.py").write_text(
        f"def collect_daemon_status(project_root):\n    return {status!r}\n",
        encoding="utf-8",
    )


def test_doctor_dispatcher_substrate_mismatch_warns(tmp_path: Path) -> None:
    root = tmp_path
    _write_daemon_status_script(root, running=False, heartbeat_age=None)
    _write_dispatcher_daemon_substrate(root)
    result = _check_dispatcher_daemon_substrate_readiness(root)
    assert result.status == "warning"
    assert "not healthy" in result.message


def test_doctor_dispatcher_substrate_healthy_ok(tmp_path: Path) -> None:
    root = tmp_path
    _write_daemon_status_script(root, running=True, heartbeat_age=0.0)
    _write_dispatcher_daemon_substrate(root)
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


def test_doctor_supervisor_task_consumes_complex_health(monkeypatch, tmp_path: Path) -> None:
    _write_dispatcher_daemon_substrate(tmp_path)
    calls: list[Path] = []

    def _fake_complex_health(target: Path):
        calls.append(target)
        return {
            "components": {
                "supervisor": {
                    "status": {"healthy": True, "registered": True, "findings": []},
                    "severity": "PASS",
                }
            }
        }

    monkeypatch.setattr(doctor_mod.os, "name", "nt")
    monkeypatch.setattr("groundtruth_kb.dispatcher_complex.collect_complex_health", _fake_complex_health)

    check = doctor_mod._check_dispatcher_daemon_supervisor_task(tmp_path)

    assert calls == [tmp_path]
    assert check.status == "pass"
    assert "GTKB-DispatcherDaemon supervisor" in check.message


def test_doctor_supervisor_task_warns_with_install_hint_from_complex_health(monkeypatch, tmp_path: Path) -> None:
    _write_dispatcher_daemon_substrate(tmp_path)

    def _fake_complex_health(target: Path):
        return {
            "components": {
                "supervisor": {
                    "status": {
                        "healthy": False,
                        "registered": True,
                        "findings": ["scheduled task 'GTKB-DispatcherDaemon' is disabled"],
                    },
                    "severity": "WARN",
                }
            }
        }

    monkeypatch.setattr(doctor_mod.os, "name", "nt")
    monkeypatch.setattr("groundtruth_kb.dispatcher_complex.collect_complex_health", _fake_complex_health)

    check = doctor_mod._check_dispatcher_daemon_supervisor_task(tmp_path)

    assert check.status == "warning"
    assert check.found is True
    assert "scheduled task 'GTKB-DispatcherDaemon' is disabled" in check.message
    assert "gt bridge dispatch daemon supervisor install" in check.message


def test_doctor_supervisor_and_watchdog_share_complex_health_reader(monkeypatch, tmp_path: Path) -> None:
    _write_dispatcher_daemon_substrate(tmp_path)
    calls: list[Path] = []

    def _fake_complex_health(target: Path):
        calls.append(target)
        return {
            "components": {
                "supervisor": {
                    "status": {"healthy": True, "registered": True, "findings": []},
                    "severity": "PASS",
                },
                "watchdog": {
                    "status": {"healthy": True, "registered": True, "findings": []},
                    "severity": "PASS",
                    "heartbeat": {"fresh": True},
                },
            }
        }

    monkeypatch.setattr(doctor_mod.os, "name", "nt")
    monkeypatch.setattr("groundtruth_kb.dispatcher_complex.collect_complex_health", _fake_complex_health)

    reader = doctor_mod._dispatcher_complex_health_reader(tmp_path)
    supervisor = doctor_mod._check_dispatcher_daemon_supervisor_task(tmp_path, reader)
    watchdog = doctor_mod._check_dispatcher_daemon_watchdog_task(tmp_path, reader)

    assert calls == [tmp_path]
    assert supervisor.status == "pass"
    assert watchdog.status == "pass"
