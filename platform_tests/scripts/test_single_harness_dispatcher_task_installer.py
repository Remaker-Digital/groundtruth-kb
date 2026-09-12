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
Cleanup via try/finally removes test tasks on ordinary failure, but NOT when the
process is killed outright: pytest-timeout's thread method terminates the
process on Windows, so ``finally`` never runs and the registered task survives
armed. That is the measured provenance of the stray ``GTKB-SingleHarness-E2E-Test-*``
task recorded in WI-6316, and it is why the host-mutating end-to-end case below
is opt-in rather than merely timeout-bounded (WI-6222 Slice 1).
"""

from __future__ import annotations

import os
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INSTALLER = PROJECT_ROOT / "scripts" / "install_single_harness_dispatcher_task.ps1"
UNINSTALLER = PROJECT_ROOT / "scripts" / "uninstall_single_harness_dispatcher_task.ps1"

WINDOWS_ONLY = pytest.mark.skipif(sys.platform != "win32", reason="Windows-only Task Scheduler tests")

# WI-6222 Slice 1 — environment gate for the host-mutating end-to-end case.
#
# Unlike the other cases in this module, the end-to-end test does not merely
# inspect an installer's output: it REGISTERS a real Windows scheduled task,
# STARTS it, and polls for up to 30s for the dispatcher to write state. Two
# properties make it unsafe as a default-on test:
#
#   1. It mutates host state outside the project root, and its cleanup is not
#      kill-safe (see the module docstring and WI-6316).
#   2. It requires a working Task Scheduler environment in which a freshly
#      registered task actually runs. Where that environment is absent the poll
#      cannot succeed, and the test previously consumed its full budget and then
#      killed the entire sweep rather than failing honestly.
#
# The gate is opt-in rather than auto-detected because "can this host run a
# scheduled task end to end" is not reliably detectable without performing the
# very registration under test. Opt-in also keeps the case correct under the
# standing owner direction that legacy dispatcher authorities stay disabled
# pending Dispatcher Next (WI-5624): the substrate this exercises is slated for
# retirement, so it must not run by default.
SCHEDULED_TASK_E2E_ENV = "GTKB_SCHEDULED_TASK_E2E"
SCHEDULED_TASK_E2E_ONLY = pytest.mark.skipif(
    os.environ.get(SCHEDULED_TASK_E2E_ENV) != "1",
    reason=(
        f"host-mutating scheduled-task E2E; set {SCHEDULED_TASK_E2E_ENV}=1 to opt in "
        "(registers and starts a real Windows scheduled task)"
    ),
)


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
@SCHEDULED_TASK_E2E_ONLY
@pytest.mark.timeout(120)
def test_single_harness_dispatcher_end_to_end_via_scheduled_task(
    tmp_path: Path,
) -> None:
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
                "harnesses": {
                    "B": {
                        "role": ["prime-builder", "loyal-opposition"],
                        "harness_type": "claude",
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    (harness_state / "harness-registry.json").write_text(
        _json.dumps(
            {
                "schema_version": 1,
                "source_of_truth": "MemBase harnesses table (groundtruth.db)",
                "harnesses": [
                    {
                        "id": "B",
                        "harness_name": "claude",
                        "harness_type": "claude",
                        "status": "active",
                        "event_driven_hooks": True,
                        "role": ["prime-builder", "loyal-opposition"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    state_dir = tmp_path / ".gtkb-state" / "bridge-poller"
    state_dir.mkdir(parents=True, exist_ok=True)

    # Register the task manually (not via installer.ps1 because installer
    # has its own argument shape; we need --dry-run + scratch project root).
    dispatcher_path = str(PROJECT_ROOT / "scripts" / "single_harness_bridge_dispatcher.py")
    pythonw_exe = str(Path(sys.executable).with_name("pythonw.exe"))
    register_cmd = (
        f"$action = New-ScheduledTaskAction -Execute '{pythonw_exe}' "
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
