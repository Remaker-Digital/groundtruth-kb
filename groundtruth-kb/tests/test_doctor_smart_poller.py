# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for gt project doctor smart-poller activation check.

Per ``bridge/gtkb-bridge-poller-notify-activation-2026-04-29-004.md`` GO
(REVISED-1 at -003 §5): the doctor check verifies the activation chain
from runner script through scheduled task to fresh notification artifacts.

Per -004 GO guardrail 2: the check inspects the ACTUAL scheduled-task
action target — not just the task name — to confirm the wrapper-based
activation pattern is in place rather than a direct-runner registration.

These tests run the check function in isolation against synthetic project
trees. PowerShell-shelling tests (task registered/target-wrong) are
mocked via monkeypatch on _run_cmd.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from groundtruth_kb.project import doctor as doctor_module
from groundtruth_kb.project.doctor import _check_smart_bridge_poller


def _make_project(tmp_path: Path, *, runner: bool = True, wrapper: bool = True) -> Path:
    """Build a synthetic project root with optional runner + wrapper presence."""
    project = tmp_path / "project"
    (project / "groundtruth-kb" / "scripts").mkdir(parents=True, exist_ok=True)
    (project / "scripts").mkdir(parents=True, exist_ok=True)
    if runner:
        (project / "groundtruth-kb" / "scripts" / "bridge_poller_runner.py").write_text(
            "# stub runner\n", encoding="utf-8"
        )
    if wrapper:
        (project / "scripts" / "run_smart_bridge_poller.ps1").write_text(
            '# wrapper\n$runnerPath = Join-Path $projectRoot "groundtruth-kb\\scripts\\bridge_poller_runner.py"\n',
            encoding="utf-8",
        )
    return project


def _make_run_cmd_mock(*, validate_ok: bool = True, validate_output: str = "", task_xml: str = ""):
    """Return a _run_cmd substitute that discriminates between ValidateOnly and Get-ScheduledTask calls.

    The doctor's smart-poller check shells out twice:
      - powershell -File <wrapper> -ValidateOnly  (check 3)
      - powershell -Command "Get-ScheduledTask ..."  (checks 5+6)

    Tests provide what each call should return; this builds a single mock that
    routes based on whether '-ValidateOnly' or 'Get-ScheduledTask' appears in args.
    """

    def _mock(cmd_args, **kwargs):
        joined = " ".join(str(a) for a in cmd_args)
        if "-ValidateOnly" in joined:
            return (validate_ok, validate_output)
        return (True, task_xml)

    return _mock


def _make_audit(project: Path, *, age_seconds: float = 1.0) -> None:
    """Create an audit event file with the specified mtime age (in seconds)."""
    audit_dir = project / ".gtkb-state" / "bridge-poller" / "poller-runs"
    audit_dir.mkdir(parents=True, exist_ok=True)
    fpath = audit_dir / "test-run.jsonl"
    fpath.write_text('{"kind":"scan"}\n', encoding="utf-8")
    target_mtime = time.time() - age_seconds
    import os

    os.utime(fpath, (target_mtime, target_mtime))


# --- Test 1: runner missing → fail ------------------------------------------


def test_runner_missing_fails(tmp_path: Path) -> None:
    project = _make_project(tmp_path, runner=False)
    result = _check_smart_bridge_poller(project)
    assert result.status == "fail"
    assert "runner missing" in result.message


# --- Test 2: wrapper missing → fail -----------------------------------------


def test_wrapper_missing_fails(tmp_path: Path) -> None:
    project = _make_project(tmp_path, wrapper=False)
    result = _check_smart_bridge_poller(project)
    assert result.status == "fail"
    assert "wrapper missing" in result.message


# --- Test 3: wrapper -ValidateOnly fails (Phase 2 rebase outstanding) -----


def test_wrapper_validate_only_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Doctor calls wrapper -ValidateOnly; if it returns non-zero (e.g., the
    $runnerPath doesn't resolve), doctor reports fail with Phase-2-rebase hint."""
    project = _make_project(tmp_path)
    # ValidateOnly returns failure (e.g., wrapper threw because runnerPath doesn't exist).
    monkeypatch.setattr(
        doctor_module,
        "_run_cmd",
        _make_run_cmd_mock(validate_ok=False, validate_output="Smart-poller runner not found at C:\\bad\\path"),
    )
    result = _check_smart_bridge_poller(project)
    assert result.status == "fail"
    assert "ValidateOnly failed" in result.message


# --- Test 3b: wrapper -ValidateOnly resolves DIFFERENT runner → fail ------


def test_wrapper_resolves_different_runner_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """If wrapper -ValidateOnly succeeds but resolves a runner path that's not
    the expected one, doctor flags a customized/rebase-mid-flight wrapper."""
    project = _make_project(tmp_path)
    monkeypatch.setattr(
        doctor_module,
        "_run_cmd",
        _make_run_cmd_mock(validate_ok=True, validate_output="OK runner=C:\\different\\custom\\runner.py"),
    )
    result = _check_smart_bridge_poller(project)
    assert result.status == "fail"
    assert "different runner path" in result.message


# --- Test 4: task not registered → warning (initial-install state) ---------


def test_task_not_registered_warns(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = _make_project(tmp_path)
    # ValidateOnly returns OK with expected runner path (mocked); Get-ScheduledTask returns empty.
    monkeypatch.setattr(
        doctor_module,
        "_run_cmd",
        _make_run_cmd_mock(
            validate_ok=True,
            validate_output="OK runner=groundtruth-kb\\scripts\\bridge_poller_runner.py",
            task_xml="",
        ),
    )
    result = _check_smart_bridge_poller(project)
    assert result.status == "warning"
    assert "not registered" in result.message
    assert "install_smart_poller_task.ps1" in result.message


# --- Test 5: task target wrong (direct runner, not wrapper) → fail ---------


def test_task_target_does_not_include_wrapper_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Per -004 GO guardrail 2 + -006 follow-up: doctor must inspect the actual
    action target. If task points at pythonw directly instead of the VBS
    launcher, the Phase-2-stable activation pattern is broken."""
    project = _make_project(tmp_path)
    # Task XML output that mentions pythonw + runner directly but NOT the VBS.
    bad_task_xml = """
    Execute: pythonw.exe
    Arguments: "E:\\GT-KB\\groundtruth-kb\\scripts\\bridge_poller_runner.py" --interval 15
    """
    monkeypatch.setattr(
        doctor_module,
        "_run_cmd",
        _make_run_cmd_mock(
            validate_ok=True,
            validate_output="OK runner=groundtruth-kb\\scripts\\bridge_poller_runner.py",
            task_xml=bad_task_xml,
        ),
    )
    result = _check_smart_bridge_poller(project)
    assert result.status == "fail"
    assert "VBS launcher" in result.message
    assert "Finding 1" in result.message  # cites -004 finding


# --- Test 6: task registered + target ok but no audit event → warning ------


def test_task_registered_no_audit_warns(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = _make_project(tmp_path)
    fake_task_xml = '\nExecute: wscript.exe\nArguments: "E:\\GT-KB\\scripts\\run_smart_bridge_poller.vbs"\n'
    monkeypatch.setattr(
        doctor_module,
        "_run_cmd",
        _make_run_cmd_mock(
            validate_ok=True,
            validate_output="OK runner=groundtruth-kb\\scripts\\bridge_poller_runner.py",
            task_xml=fake_task_xml,
        ),
    )
    result = _check_smart_bridge_poller(project)
    assert result.status == "warning"
    assert "no audit events" in result.message or "not have started" in result.message


# --- Test 7: stale audit event → fail --------------------------------------


def test_stale_audit_event_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = _make_project(tmp_path)
    _make_audit(project, age_seconds=120.0)  # > 60s threshold
    fake_task_xml = '\nExecute: wscript.exe\nArguments: "E:\\GT-KB\\scripts\\run_smart_bridge_poller.vbs"\n'
    monkeypatch.setattr(
        doctor_module,
        "_run_cmd",
        _make_run_cmd_mock(
            validate_ok=True,
            validate_output="OK runner=groundtruth-kb\\scripts\\bridge_poller_runner.py",
            task_xml=fake_task_xml,
        ),
    )
    result = _check_smart_bridge_poller(project)
    assert result.status == "fail"
    assert "audit event" in result.message
    assert "stuck" in result.message or "Task may be stuck" in result.message


# --- Test 8: full healthy state → pass --------------------------------------


def test_full_healthy_state_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = _make_project(tmp_path)
    _make_audit(project, age_seconds=5.0)
    # No notification files (steady state with no actionable pending work).
    fake_task_xml = '\nExecute: wscript.exe\nArguments: "E:\\GT-KB\\scripts\\run_smart_bridge_poller.vbs"\n'
    monkeypatch.setattr(
        doctor_module,
        "_run_cmd",
        _make_run_cmd_mock(
            validate_ok=True,
            validate_output="OK runner=groundtruth-kb\\scripts\\bridge_poller_runner.py",
            task_xml=fake_task_xml,
        ),
    )
    result = _check_smart_bridge_poller(project)
    assert result.status == "pass"
    assert "smart-poller active" in result.message


# --- Test 9: stale notification (file present but old) → fail --------------


def test_stale_notification_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = _make_project(tmp_path)
    _make_audit(project, age_seconds=5.0)  # audit fresh

    # Create stale notification file
    notify_dir = project / ".gtkb-state" / "bridge-poller" / "notifications"
    notify_dir.mkdir(parents=True, exist_ok=True)
    fpath = notify_dir / "pending-bridge-action-prime.json"
    fpath.write_text('{"schema_version":2}', encoding="utf-8")
    target_mtime = time.time() - 120.0  # > 60s threshold
    import os

    os.utime(fpath, (target_mtime, target_mtime))

    fake_task_xml = '\nExecute: wscript.exe\nArguments: "E:\\GT-KB\\scripts\\run_smart_bridge_poller.vbs"\n'
    monkeypatch.setattr(
        doctor_module,
        "_run_cmd",
        _make_run_cmd_mock(
            validate_ok=True,
            validate_output="OK runner=groundtruth-kb\\scripts\\bridge_poller_runner.py",
            task_xml=fake_task_xml,
        ),
    )
    result = _check_smart_bridge_poller(project)
    assert result.status == "fail"
    assert "notification stale" in result.message.lower()
