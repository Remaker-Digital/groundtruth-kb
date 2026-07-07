# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Spec-derived tests for the service/SoT availability watchdog (WI-5043)."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

from click.testing import CliRunner

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "groundtruth-kb" / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.project import doctor as doctor_mod  # noqa: E402
from groundtruth_kb.project.sot_registry import SoTArtifact  # noqa: E402
from groundtruth_kb.watchdog import service_sot  # noqa: E402


class _FakeComponent:
    def __init__(self, name: str, status: str, detail: str) -> None:
        self.name = name
        self.status = status
        self.detail = detail

    def to_json_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "status": self.status,
            "detail": self.detail,
            "source": f"source:{self.name}",
            "duration_ms": 1.0,
            "evidence": {},
        }


def _artifact(artifact_id: str, health_check: str, *, restore_action: str = "manual") -> SoTArtifact:
    return SoTArtifact(
        id=artifact_id,
        domain="specifications",
        lifecycle="active",
        storage_path=f"membase:{artifact_id}",
        authority_spec_id="GOV-TEST",
        mutation_api="test",
        versioning_policy="append_only_versioned",
        backup_policy="membase_export",
        health_check_function=health_check,
        owner_role="shared",
        restore_action=restore_action,
    )


def test_watchdog_enumerates_gt_status_and_sot_checks_without_restore(monkeypatch, tmp_path):
    def _fake_collect_operating_state(project_root, *, config, startup, components):
        assert project_root == tmp_path.resolve()
        assert startup is True
        assert components == ("db", "bridge")
        return SimpleNamespace(
            overall_status="WARN",
            components=(
                _FakeComponent("db", "PASS", "db ok"),
                _FakeComponent("bridge", "WARN", "bridge has pending work"),
            ),
        )

    monkeypatch.setattr(service_sot, "collect_operating_state", _fake_collect_operating_state)
    monkeypatch.setattr(
        service_sot,
        "load_sot_toml",
        lambda _path: (
            _artifact("membase-specifications", "_check_db_schema"),
            _artifact("bridge-dir", "_check_file_bridge_setup"),
        ),
    )
    monkeypatch.setattr(
        service_sot,
        "_invoke_health_check",
        lambda function_name, project_root: {
            "name": function_name,
            "status": "PASS",
            "detail": "ok",
            "found": True,
            "required": False,
        },
    )

    payload = service_sot.build_service_sot_status(tmp_path, components=("db", "bridge"), config=object())

    assert payload["overall_status"] == "WARN"
    assert payload["summary"]["gt_status_component_count"] == 2
    assert payload["summary"]["sot_artifact_probe_count"] == 2
    assert payload["restore_actions_executed"] == []
    assert payload["canonical_mutations_executed"] == []
    assert any("bridge" in finding for finding in payload["findings"])


def test_watchdog_records_probe_exception_as_failure(monkeypatch, tmp_path):
    def _boom(*_args, **_kwargs):
        raise RuntimeError("db unreachable")

    monkeypatch.setattr(service_sot, "collect_operating_state", _boom)
    monkeypatch.setattr(service_sot, "load_sot_toml", lambda _path: ())

    payload = service_sot.build_service_sot_status(tmp_path, config=object())

    assert payload["overall_status"] == "FAIL"
    assert any("db unreachable" in finding for finding in payload["findings"])


def test_health_check_invokes_target_with_optional_dependencies(monkeypatch, tmp_path):
    monkeypatch.setattr(
        doctor_mod,
        "_check_optional_dependency_test",
        lambda target, load_complex_health=None: SimpleNamespace(
            name="optional dependency test",
            status="pass",
            message=str(target),
            found=True,
            required=False,
        ),
        raising=False,
    )

    payload = service_sot._invoke_health_check("_check_optional_dependency_test", tmp_path)

    assert payload["status"] == "PASS"
    assert payload["found"] is True


def test_watchdog_executes_safe_restore_and_records_payload(monkeypatch, tmp_path):
    def _fake_collect_operating_state(project_root, *, config, startup, components):
        return SimpleNamespace(overall_status="PASS", components=())

    probes = iter(
        [
            {"name": "supervisor", "status": "WARN", "detail": "task disabled", "found": True, "required": False},
            {"name": "supervisor", "status": "WARN", "detail": "task disabled", "found": True, "required": False},
            {"name": "supervisor", "status": "PASS", "detail": "task ready", "found": True, "required": False},
        ]
    )
    calls: list[Path] = []

    monkeypatch.setattr(service_sot, "collect_operating_state", _fake_collect_operating_state)
    monkeypatch.setattr(
        service_sot,
        "load_sot_toml",
        lambda _path: (
            _artifact(
                "dispatcher-supervisor-task",
                "_check_dispatcher_daemon_supervisor_task",
                restore_action="ensure_alive",
            ),
        ),
    )
    monkeypatch.setattr(service_sot, "_invoke_health_check", lambda function_name, project_root: next(probes))
    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_supervisor.install_supervisor",
        lambda project_root: calls.append(project_root) or {"action": "install"},
    )

    payload = service_sot.build_service_sot_status(tmp_path, config=object())

    assert calls == [tmp_path.resolve()]
    assert payload["overall_status"] == "PASS"
    assert payload["summary"]["restore_actions_executed"] == 1
    assert payload["restore_actions_deferred"] == []
    assert payload["canonical_mutations_executed"] == []
    artifact = payload["sot_registry"]["artifacts"][0]
    assert artifact["status"] == "PASS"
    assert artifact["pre_restore_probe"]["status"] == "WARN"


def test_watchdog_clears_retry_debt_after_fresh_healthy_probe(tmp_path):
    artifact = _artifact(
        "dispatcher-supervisor-task",
        "_check_dispatcher_daemon_supervisor_task",
        restore_action="ensure_alive",
    )
    retry_state = {
        "schema_version": 1,
        "attempts": {
            "dispatcher-supervisor-task:ensure_alive": {
                "artifact_id": "dispatcher-supervisor-task",
                "restore_action": "ensure_alive",
                "attempts": 3,
            }
        },
    }
    probe = {"name": "supervisor", "status": "PASS", "detail": "task ready", "fresh": True}

    evaluated, executed, deferred = service_sot._evaluate_restore_for_artifact(
        artifact,
        probe,
        tmp_path,
        retry_state,
    )

    assert executed == []
    assert deferred == []
    assert retry_state["attempts"] == {}
    assert evaluated["restore_decision"]["reason_code"] == "probe_not_failed"
    assert evaluated["restore_retry_reset"]["attempts_cleared"] == 3
    assert evaluated["restore_retry_reset"]["reason_code"] == "healthy_probe"


def test_watchdog_keeps_retry_exhaustion_for_failing_probe(tmp_path):
    artifact = _artifact(
        "dispatcher-supervisor-task",
        "_check_dispatcher_daemon_supervisor_task",
        restore_action="ensure_alive",
    )
    retry_state = {
        "schema_version": 1,
        "attempts": {
            "dispatcher-supervisor-task:ensure_alive": {
                "artifact_id": "dispatcher-supervisor-task",
                "restore_action": "ensure_alive",
                "attempts": 3,
            }
        },
    }
    probe = {"name": "supervisor", "status": "WARN", "detail": "task disabled", "fresh": True}

    evaluated, executed, deferred = service_sot._evaluate_restore_for_artifact(
        artifact,
        probe,
        tmp_path,
        retry_state,
    )

    assert executed == []
    assert deferred[0]["reason_code"] == "retry_exhausted"
    assert evaluated["restore_decision"]["kind"] == "escalate"
    assert retry_state["attempts"]["dispatcher-supervisor-task:ensure_alive"]["attempts"] == 3


def test_watchdog_defers_safe_restore_when_disable_guard_active(monkeypatch, tmp_path):
    from groundtruth_kb.dispatcher_disable_guard import record_guarded_disable

    def _fake_collect_operating_state(project_root, *, config, startup, components):
        return SimpleNamespace(overall_status="PASS", components=())

    record_guarded_disable(
        tmp_path,
        task_names=["GTKB-DispatcherDaemon"],
        component="dispatcher-supervisor",
        ttl_seconds=600,
        reason="maintenance",
        actor="prime-builder/codex",
    )
    monkeypatch.setattr(service_sot, "collect_operating_state", _fake_collect_operating_state)
    monkeypatch.setattr(
        service_sot,
        "load_sot_toml",
        lambda _path: (
            _artifact(
                "dispatcher-supervisor-task",
                "_check_dispatcher_daemon_supervisor_task",
                restore_action="ensure_alive",
            ),
        ),
    )
    monkeypatch.setattr(
        service_sot,
        "_invoke_health_check",
        lambda function_name, project_root: {
            "name": "supervisor",
            "status": "WARN",
            "detail": "task disabled",
            "found": True,
            "required": False,
        },
    )
    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_supervisor.install_supervisor",
        lambda project_root: (_ for _ in ()).throw(AssertionError("restore should be suppressed")),
    )

    payload = service_sot.build_service_sot_status(tmp_path, config=object())

    assert payload["restore_actions_executed"] == []
    assert payload["restore_actions_deferred"][0]["reason_code"] == "disable_guard_active"
    assert payload["restore_actions_deferred"][0]["disable_guard"]["active"] is True


def test_write_service_sot_status_writes_json(tmp_path):
    payload = {"schema_version": 1, "overall_status": "PASS", "captured_at": "2026-07-06T00:00:00Z"}
    path = tmp_path / ".gtkb-state" / "watchdog" / "service-sot-status.json"

    service_sot.write_service_sot_status(payload, path)

    assert json.loads(path.read_text(encoding="utf-8")) == payload


def test_collect_task_status_marks_healthy_when_task_and_output_are_fresh(monkeypatch, tmp_path):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "gtkb_service_sot_watchdog.py").write_text("# stub\n", encoding="utf-8")
    service_sot.default_status_path(tmp_path).parent.mkdir(parents=True)
    service_sot.default_status_path(tmp_path).write_text(
        json.dumps({"captured_at": datetime.now(UTC).isoformat(), "overall_status": "PASS"}),
        encoding="utf-8",
    )
    task_payload = {
        "registered": True,
        "state": "Ready",
        "hidden": True,
        "execute": r"E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe",
        "arguments": r'"E:\GT-KB\scripts\gtkb_service_sot_watchdog.py" --project-root "E:\GT-KB"',
        "has_startup_trigger": True,
        "has_repetition_trigger": True,
        "triggers": [
            {"class": "MSFT_TaskBootTrigger"},
            {"class": "MSFT_TaskTimeTrigger", "repetition_interval": "PT5M"},
        ],
    }

    def _fake_powershell(command: str, *, timeout: int = 120):
        class _Proc:
            returncode = 0
            stdout = json.dumps(task_payload)
            stderr = ""

        return _Proc()

    monkeypatch.setattr(service_sot.os, "name", "nt")
    monkeypatch.setattr(service_sot, "_run_powershell", _fake_powershell)

    status = service_sot.collect_task_status(tmp_path)

    assert status["healthy"] is True
    assert status["registered"] is True
    assert status["uses_pythonw"] is True
    assert status["uses_runner_script"] is True
    assert status["findings"] == []


def test_collect_task_status_requires_startup_trigger(monkeypatch, tmp_path):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "gtkb_service_sot_watchdog.py").write_text("# stub\n", encoding="utf-8")
    service_sot.default_status_path(tmp_path).parent.mkdir(parents=True)
    service_sot.default_status_path(tmp_path).write_text(
        json.dumps({"captured_at": datetime.now(UTC).isoformat(), "overall_status": "PASS"}),
        encoding="utf-8",
    )
    task_payload = {
        "registered": True,
        "state": "Ready",
        "hidden": True,
        "execute": r"E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe",
        "arguments": r'"E:\GT-KB\scripts\gtkb_service_sot_watchdog.py" --project-root "E:\GT-KB"',
        "has_startup_trigger": False,
        "has_repetition_trigger": True,
        "triggers": [{"class": "MSFT_TaskTimeTrigger", "repetition_interval": "PT5M"}],
    }

    def _fake_powershell(command: str, *, timeout: int = 120):
        class _Proc:
            returncode = 0
            stdout = json.dumps(task_payload)
            stderr = ""

        return _Proc()

    monkeypatch.setattr(service_sot.os, "name", "nt")
    monkeypatch.setattr(service_sot, "_run_powershell", _fake_powershell)

    status = service_sot.collect_task_status(tmp_path)

    assert status["healthy"] is False
    assert any("startup trigger" in item for item in status["findings"])


def test_service_sot_installer_registers_startup_and_interval_triggers():
    install = _REPO_ROOT / "scripts" / "install_service_sot_watchdog_task.ps1"
    body = install.read_text(encoding="utf-8")

    assert "New-ScheduledTaskTrigger -AtStartup" in body
    assert "New-ScheduledTaskTrigger -Once" in body
    assert "$triggers = @($startupTrigger, $intervalTrigger)" in body
    assert "-Trigger $triggers" in body
    assert "-Force `" in body
    assert "Unregister-ScheduledTask" not in body


def test_doctor_service_sot_watchdog_reports_platform_task_health(monkeypatch, tmp_path):
    registry = tmp_path / "config" / "registry"
    registry.mkdir(parents=True)
    (registry / "sot-artifacts.toml").write_text("# platform registry marker\n", encoding="utf-8")
    monkeypatch.setattr(doctor_mod.os, "name", "nt")

    check = doctor_mod._check_service_sot_watchdog(
        tmp_path,
        load_task_status=lambda _target: {"healthy": True, "registered": True, "findings": []},
    )

    assert check.status == "pass"
    assert "GTKB-ServiceSoTWatchdog" in check.message


def test_cli_service_sot_watchdog_control_commands_dispatch(monkeypatch):
    from groundtruth_kb.cli import main

    calls: list[str] = []
    monkeypatch.setattr(
        "groundtruth_kb.watchdog.service_sot.install_task",
        lambda project_root, *, task_name, interval_minutes, dry_run: (
            calls.append(f"install:{task_name}:{interval_minutes}:{dry_run}")
            or {"action": "install", "task_name": task_name, "dry_run": dry_run}
        ),
    )
    monkeypatch.setattr(
        "groundtruth_kb.watchdog.service_sot.enable_task",
        lambda *, task_name: calls.append(f"enable:{task_name}") or {"action": "enable", "task_name": task_name},
    )
    monkeypatch.setattr(
        "groundtruth_kb.watchdog.service_sot.disable_task",
        lambda *, task_name: calls.append(f"disable:{task_name}") or {"action": "disable", "task_name": task_name},
    )
    monkeypatch.setattr(
        "groundtruth_kb.watchdog.service_sot.uninstall_task",
        lambda *, task_name, dry_run: (
            calls.append(f"uninstall:{task_name}:{dry_run}")
            or {"action": "uninstall", "task_name": task_name, "dry_run": dry_run}
        ),
    )

    runner = CliRunner()
    env = {"GTKB_PROJECT_ROOT": str(_REPO_ROOT)}
    commands = [
        ["watchdog", "service-sot", "install", "--task-name", "GTKB-ServiceSoT-Test", "--dry-run"],
        ["watchdog", "service-sot", "enable", "--task-name", "GTKB-ServiceSoT-Test"],
        ["watchdog", "service-sot", "disable", "--task-name", "GTKB-ServiceSoT-Test"],
        ["watchdog", "service-sot", "uninstall", "--task-name", "GTKB-ServiceSoT-Test", "--dry-run"],
    ]

    for command in commands:
        result = runner.invoke(main, command, env=env)
        assert result.exit_code == 0, result.output

    assert calls == [
        "install:GTKB-ServiceSoT-Test:5:True",
        "enable:GTKB-ServiceSoT-Test",
        "disable:GTKB-ServiceSoT-Test",
        "uninstall:GTKB-ServiceSoT-Test:True",
    ]
