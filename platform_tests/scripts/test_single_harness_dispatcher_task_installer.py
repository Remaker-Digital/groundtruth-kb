# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Windows Task Scheduler installer/uninstaller tests for IP-2 of
bridge/gtkb-single-harness-bridge-dispatcher-slice-2-005.md (Codex GO at -006).

Specs:
- DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 § Platform Bindings (Windows):
  pythonw.exe + Hidden=$true for the CREATE_NO_WINDOW requirement.
- F2 of -004 closure: installer accepts [switch]$DryRun.
- F3 of -004 closure: structured assertion shape (Execute + tokenized Arguments).
- F4 of -004 closure: no-console settings verified.

All tests use nonce-suffixed task names to avoid mutating the production task.
Cleanup via try/finally ensures test tasks are removed even on failure.
"""

from __future__ import annotations

import re
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INSTALLER = PROJECT_ROOT / "scripts" / "install_single_harness_dispatcher_task.ps1"
UNINSTALLER = PROJECT_ROOT / "scripts" / "uninstall_single_harness_dispatcher_task.ps1"

WINDOWS_ONLY = pytest.mark.skipif(sys.platform != "win32", reason="Windows-only Task Scheduler tests")


def _nonce_task_name(prefix: str = "GTKB-SingleHarnessBridgeDispatcher-Test") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _run_powershell(*args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Invoke powershell.exe with given args; capture stdout/stderr."""
    return subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass"] + list(args),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def _unregister_silent(task_name: str) -> None:
    """Best-effort unregister; ignores errors (used in cleanup)."""
    _run_powershell(
        "-Command",
        f"Unregister-ScheduledTask -TaskName '{task_name}' -Confirm:$false -ErrorAction SilentlyContinue",
    )


# ──────────────────────────────────────────────────────────────────────────
# Installer/uninstaller dry-run paths — cross-platform (subprocess invocation
# of powershell.exe; runs only on Windows).
# ──────────────────────────────────────────────────────────────────────────


@WINDOWS_ONLY
def test_installer_dry_run_does_not_register() -> None:
    """F2 of -004: -DryRun prints rendered command line; does NOT register."""
    task_name = _nonce_task_name()
    try:
        result = _run_powershell(
            "-File",
            str(INSTALLER),
            "-ProjectRoot",
            str(PROJECT_ROOT),
            "-TaskName",
            task_name,
            "-DryRun",
        )
        assert result.returncode == 0, f"installer exit={result.returncode}: {result.stderr}"
        assert "WOULD REGISTER" in result.stdout
        assert f"TaskName={task_name}" in result.stdout
        assert "--max-items 999" in result.stdout
        # Task must NOT exist.
        check = _run_powershell(
            "-Command",
            f"if (Get-ScheduledTask -TaskName '{task_name}' -ErrorAction SilentlyContinue) "
            f"{{ Write-Output 'EXISTS' }} else {{ Write-Output 'ABSENT' }}",
        )
        assert "ABSENT" in check.stdout, "DryRun mutated Task Scheduler state"
    finally:
        _unregister_silent(task_name)


@WINDOWS_ONLY
def test_uninstaller_dry_run_does_not_unregister() -> None:
    """F2 of -004 parity: uninstaller -DryRun prints intent; does NOT unregister."""
    task_name = _nonce_task_name()
    try:
        # Pre-register so we can verify dry-run leaves it.
        register_result = _run_powershell(
            "-File",
            str(INSTALLER),
            "-ProjectRoot",
            str(PROJECT_ROOT),
            "-TaskName",
            task_name,
        )
        assert register_result.returncode == 0, f"pre-register failed: {register_result.stderr}"

        # Dry-run uninstall.
        uninstall_result = _run_powershell("-File", str(UNINSTALLER), "-TaskName", task_name, "-DryRun")
        assert uninstall_result.returncode == 0
        assert "WOULD UNREGISTER" in uninstall_result.stdout
        assert f"TaskName={task_name}" in uninstall_result.stdout

        # Task still present.
        check = _run_powershell(
            "-Command",
            f"if (Get-ScheduledTask -TaskName '{task_name}' -ErrorAction SilentlyContinue) "
            f"{{ Write-Output 'EXISTS' }} else {{ Write-Output 'ABSENT' }}",
        )
        assert "EXISTS" in check.stdout
    finally:
        _unregister_silent(task_name)


@WINDOWS_ONLY
def test_installer_registers_task() -> None:
    """T-SHD-S2-installer-registers: installer registers a task."""
    task_name = _nonce_task_name()
    try:
        result = _run_powershell(
            "-File",
            str(INSTALLER),
            "-ProjectRoot",
            str(PROJECT_ROOT),
            "-TaskName",
            task_name,
        )
        assert result.returncode == 0, f"installer failed: {result.stderr}"
        check = _run_powershell(
            "-Command",
            f"if (Get-ScheduledTask -TaskName '{task_name}' -ErrorAction SilentlyContinue) "
            f"{{ Write-Output 'EXISTS' }} else {{ Write-Output 'ABSENT' }}",
        )
        assert "EXISTS" in check.stdout
    finally:
        _unregister_silent(task_name)


@WINDOWS_ONLY
def test_installer_idempotent() -> None:
    """T-SHD-S2-installer-idempotent: re-running with same task name does not duplicate."""
    task_name = _nonce_task_name()
    try:
        for _ in range(2):
            result = _run_powershell(
                "-File",
                str(INSTALLER),
                "-ProjectRoot",
                str(PROJECT_ROOT),
                "-TaskName",
                task_name,
            )
            assert result.returncode == 0
        # Exactly one task with this name should exist.
        count_check = _run_powershell(
            "-Command",
            f"@(Get-ScheduledTask -TaskName '{task_name}' -ErrorAction SilentlyContinue).Count",
        )
        assert count_check.stdout.strip() == "1"
    finally:
        _unregister_silent(task_name)


@WINDOWS_ONLY
def test_uninstaller_removes_task() -> None:
    """T-SHD-S2-uninstall: registered task is removed by uninstaller."""
    task_name = _nonce_task_name()
    try:
        _run_powershell(
            "-File",
            str(INSTALLER),
            "-ProjectRoot",
            str(PROJECT_ROOT),
            "-TaskName",
            task_name,
        )
        result = _run_powershell("-File", str(UNINSTALLER), "-TaskName", task_name)
        assert result.returncode == 0
        assert "Unregistered" in result.stdout
        check = _run_powershell(
            "-Command",
            f"if (Get-ScheduledTask -TaskName '{task_name}' -ErrorAction SilentlyContinue) "
            f"{{ Write-Output 'EXISTS' }} else {{ Write-Output 'ABSENT' }}",
        )
        assert "ABSENT" in check.stdout
    finally:
        _unregister_silent(task_name)


@WINDOWS_ONLY
def test_uninstaller_idempotent_on_missing_task() -> None:
    """Uninstalling a non-existent task succeeds with informational message."""
    task_name = _nonce_task_name()
    result = _run_powershell("-File", str(UNINSTALLER), "-TaskName", task_name)
    assert result.returncode == 0
    assert "not registered" in result.stdout.lower()


@WINDOWS_ONLY
def test_installer_preserves_non_targeted_task() -> None:
    """F3 of -002 closure: installer with one task name does not modify a
    separately-registered task with a different name."""
    preserve_name = _nonce_task_name("GTKB-Preserve-Test")
    target_name = _nonce_task_name()
    try:
        # Pre-register a preserve-target task with a distinct name.
        preserve_register = _run_powershell(
            "-File",
            str(INSTALLER),
            "-ProjectRoot",
            str(PROJECT_ROOT),
            "-TaskName",
            preserve_name,
        )
        assert preserve_register.returncode == 0

        # Run installer for a DIFFERENT task name.
        target_register = _run_powershell(
            "-File",
            str(INSTALLER),
            "-ProjectRoot",
            str(PROJECT_ROOT),
            "-TaskName",
            target_name,
        )
        assert target_register.returncode == 0

        # Both tasks must exist independently.
        check = _run_powershell(
            "-Command",
            f"$p = Get-ScheduledTask -TaskName '{preserve_name}' -ErrorAction SilentlyContinue; "
            f"$t = Get-ScheduledTask -TaskName '{target_name}' -ErrorAction SilentlyContinue; "
            f'Write-Output "$($null -ne $p)|$($null -ne $t)"',
        )
        assert "True|True" in check.stdout, f"preserve task or target task missing: {check.stdout!r}"
    finally:
        _unregister_silent(preserve_name)
        _unregister_silent(target_name)


@WINDOWS_ONLY
def test_installer_task_action_uses_absolute_script_path() -> None:
    """F3 of -004 closure (corrected assertion shape): inspect Execute +
    tokenized Arguments rather than full-string anchored regex."""
    task_name = _nonce_task_name()
    try:
        result = _run_powershell(
            "-File",
            str(INSTALLER),
            "-ProjectRoot",
            str(PROJECT_ROOT),
            "-TaskName",
            task_name,
        )
        assert result.returncode == 0
        # Read action via Get-ScheduledTask.
        probe = _run_powershell(
            "-Command",
            f"$t = Get-ScheduledTask -TaskName '{task_name}'; "
            f'Write-Output "EXEC=$($t.Actions[0].Execute)"; '
            f'Write-Output "ARGS=$($t.Actions[0].Arguments)"',
        )
        assert probe.returncode == 0
        lines = probe.stdout.splitlines()
        exec_line = next((l for l in lines if l.startswith("EXEC=")), "")
        args_line = next((l for l in lines if l.startswith("ARGS=")), "")
        assert exec_line.endswith("pythonw.exe"), f"F4: Execute must be pythonw.exe (got {exec_line!r})"
        # Tokenize Arguments respecting quoted segments. First token = script path.
        args_value = args_line[len("ARGS=") :]
        # Drive-anchored absolute path ending in scripts\single_harness_bridge_dispatcher.py.
        first_token_re = re.compile(
            r'^"?([A-Z]:\\.*\\scripts\\single_harness_bridge_dispatcher\.py)"?',
            re.IGNORECASE,
        )
        match = first_token_re.match(args_value)
        assert match is not None, (
            f"F3: first argument must be absolute path ending in "
            f"scripts\\single_harness_bridge_dispatcher.py (got args={args_value!r})"
        )
        # Verify --project-root is separately present.
        assert "--project-root" in args_value, "F3: --project-root flag missing"
        assert "--max-items 999" in args_value, "regular automation must dispatch the full selected queue"
    finally:
        _unregister_silent(task_name)


@WINDOWS_ONLY
def test_single_harness_dispatcher_end_to_end_via_scheduled_task(tmp_path: Path) -> None:
    """End-to-end validation per F1 of -008 closure:
    scheduled task -> dispatcher -> applicability gate -> signature compute
    -> dispatch-state.json written. Proves the full chain works in an isolated
    sandbox without touching the production task or production state.

    Setup:
    1. Synthesize an isolated single-harness scratch project under tmp_path.
    2. Register a nonce-named scheduled task pointing at the real dispatcher
       with --project-root <scratch> --dry-run (no actual subprocess spawn;
       no codex/claude binary needed inside the scratch project).
    3. Run the task via Start-ScheduledTask + wait briefly.
    4. Assert dispatch-state.json was created in <scratch>/state with
       applicability satisfied AND no spawn launched (dry-run).
    5. Cleanup: unregister the test task.
    """
    task_name = _nonce_task_name("GTKB-SingleHarness-E2E-Test")
    # Build isolated single-harness scratch project.
    (tmp_path / "groundtruth.toml").write_text(
        '[project]\nproject_name = "E2EScratch"\nprofile = "dual-agent"\n',
        encoding="utf-8",
    )
    (tmp_path / "bridge").mkdir(exist_ok=True)
    # NEW entry actionable for LO.
    (tmp_path / "bridge" / "example-thread-001.md").write_text(
        "bridge_kind: implementation_proposal\n", encoding="utf-8"
    )
    (tmp_path / "bridge" / "INDEX.md").write_text(
        "# bridge index\n\nDocument: example-thread\nNEW: bridge/example-thread-001.md\n",
        encoding="utf-8",
    )
    harness_state = tmp_path / "harness-state"
    harness_state.mkdir(exist_ok=True)
    import json as _json

    (harness_state / "harness-identities.json").write_text(
        _json.dumps({"schema_version": 1, "harnesses": {"claude": {"id": "B"}}}),
        encoding="utf-8",
    )
    (harness_state / "role-assignments.json").write_text(
        _json.dumps(
            {
                "schema_version": 1,
                "harnesses": {"B": {"role": ["prime-builder", "loyal-opposition"], "harness_type": "claude"}},
            }
        ),
        encoding="utf-8",
    )
    state_dir = tmp_path / ".gtkb-state" / "bridge-poller"
    state_dir.mkdir(parents=True, exist_ok=True)

    # Register the task manually (not via installer.ps1 because installer
    # has its own argument shape; we need --dry-run + scratch project root).
    dispatcher_path = str(PROJECT_ROOT / "scripts" / "single_harness_bridge_dispatcher.py")
    register_cmd = (
        f"$action = New-ScheduledTaskAction -Execute 'pythonw.exe' "
        f'-Argument \'"{dispatcher_path}" --project-root "{tmp_path}" --dry-run\' '
        f"-WorkingDirectory '{tmp_path}'; "
        f"$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddYears(1); "
        f"$settings = New-ScheduledTaskSettingsSet -Hidden; "
        f"Register-ScheduledTask -TaskName '{task_name}' -Action $action "
        f"-Trigger $trigger -Settings $settings -RunLevel Limited "
        f"-Description 'E2E test'"
    )
    try:
        register = _run_powershell("-Command", register_cmd, timeout=30)
        assert register.returncode == 0, f"register failed: {register.stderr}"

        # Trigger the task immediately.
        start = _run_powershell("-Command", f"Start-ScheduledTask -TaskName '{task_name}'")
        assert start.returncode == 0, f"start failed: {start.stderr}"

        # Wait for completion. The dispatcher should run + exit quickly
        # (no subprocess spawn under --dry-run).
        import time

        deadline = time.time() + 30
        dispatch_state_path = state_dir / "dispatch-state.json"
        while time.time() < deadline:
            if dispatch_state_path.is_file():
                break
            time.sleep(1)

        assert dispatch_state_path.is_file(), (
            "dispatch-state.json not created within 30s; scheduled task did not "
            "invoke the dispatcher successfully. Task may have failed to run."
        )

        # Inspect the written state. Applicability passed; LO had pending work;
        # dry-run reported no actual spawn.
        state = _json.loads(dispatch_state_path.read_text(encoding="utf-8"))
        recipients = state.get("recipients", {})
        assert "loyal-opposition" in recipients
        lo_state = recipients["loyal-opposition"]
        # Dry-run path leaves last_result either as the dry_run reason in last_launch
        # or as a dispatched signature update.
        assert lo_state.get("pending_count", 0) >= 1, f"LO should have had pending work; got {lo_state}"

        # Verify no real subprocess artifacts (no .stdout.log/.stderr.log in dispatch-runs).
        runs_dir = state_dir / "dispatch-runs"
        # dispatch-runs exists only when a real spawn was attempted; under
        # --dry-run it should be absent OR empty.
        if runs_dir.exists():
            run_logs = list(runs_dir.glob("*.log"))
            assert run_logs == [], f"--dry-run should not produce dispatch-runs/*.log files; found: {run_logs}"
    finally:
        _unregister_silent(task_name)


@WINDOWS_ONLY
def test_installer_task_action_uses_no_console_settings() -> None:
    """F4 of -004 closure: task uses pythonw.exe AND Hidden=$true setting."""
    task_name = _nonce_task_name()
    try:
        result = _run_powershell(
            "-File",
            str(INSTALLER),
            "-ProjectRoot",
            str(PROJECT_ROOT),
            "-TaskName",
            task_name,
        )
        assert result.returncode == 0
        probe = _run_powershell(
            "-Command",
            f"$t = Get-ScheduledTask -TaskName '{task_name}'; "
            f'Write-Output "EXEC=$($t.Actions[0].Execute)"; '
            f'Write-Output "HIDDEN=$($t.Settings.Hidden)"',
        )
        lines = probe.stdout.splitlines()
        exec_line = next((l for l in lines if l.startswith("EXEC=")), "")
        hidden_line = next((l for l in lines if l.startswith("HIDDEN=")), "")
        assert exec_line.endswith("pythonw.exe"), f"F4: Execute must be pythonw.exe (got {exec_line!r})"
        assert "True" in hidden_line, f"F4: Settings.Hidden must be True (got {hidden_line!r})"
    finally:
        _unregister_silent(task_name)
