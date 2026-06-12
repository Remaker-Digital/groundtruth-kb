#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Activate the single-harness bridge dispatcher only when topology requires it.

This is the harness-neutral activation layer for the regular bridge check and
dispatch operation. It is safe to call from either Codex or Claude Code hooks:

* single-harness role-set topology -> ensure the Windows scheduled task exists;
* multi-harness topology -> ensure the scheduled task is not active;
* optional one-shot dispatch -> delegate to single_harness_bridge_dispatcher.py.

The dispatcher itself remains the source of truth for bridge queue parsing,
signature deduplication, active-session suppression, and worker spawning.
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

DEFAULT_TASK_NAME = "GTKB-SingleHarnessBridgeDispatcher"
DEFAULT_INTERVAL_MINUTES = 5
DEFAULT_MAX_ITEMS = 999
DEFAULT_STATE_SUBDIR = (".gtkb-state", "bridge-poller")
AUTOMATION_STATE_FILENAME = "single-harness-automation-state.json"


def _now_iso() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def _load_dispatcher_module():
    name = "_single_harness_bridge_dispatcher_for_automation"
    if name in sys.modules:
        return sys.modules[name]
    dispatcher_path = Path(__file__).resolve().parent / "single_harness_bridge_dispatcher.py"
    spec = importlib.util.spec_from_file_location(name, dispatcher_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load dispatcher from {dispatcher_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _resolve_project_root(explicit: Path | None) -> Path:
    dispatcher = _load_dispatcher_module()
    return dispatcher._resolve_project_root(explicit)


def _ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _run_powershell(args: list[str], *, timeout: int = 30) -> dict[str, Any]:
    powershell = shutil.which("powershell.exe")
    if powershell is None:
        return {
            "returncode": 127,
            "stdout": "",
            "stderr": "powershell.exe not found",
            "command": ["powershell.exe", *args],
        }
    completed = subprocess.run(
        [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "command": ["powershell.exe", *args],
    }


def _task_snapshot(task_name: str) -> dict[str, Any]:
    script = f"""
$ErrorActionPreference = 'Stop'
$t = Get-ScheduledTask -TaskName {_ps_quote(task_name)} -ErrorAction SilentlyContinue
if ($null -eq $t) {{
    [pscustomobject]@{{ exists = $false }} | ConvertTo-Json -Compress
    exit 0
}}
$info = Get-ScheduledTaskInfo -TaskName {_ps_quote(task_name)} -ErrorAction SilentlyContinue
[pscustomobject]@{{
    exists = $true
    taskName = [string]$t.TaskName
    taskPath = [string]$t.TaskPath
    state = [string]$t.State
    execute = [string]$t.Actions[0].Execute
    arguments = [string]$t.Actions[0].Arguments
    hidden = [bool]$t.Settings.Hidden
    lastRunTime = $(if ($null -ne $info) {{ [string]$info.LastRunTime.ToString('o') }} else {{ $null }})
    lastTaskResult = $(if ($null -ne $info) {{ [int]$info.LastTaskResult }} else {{ $null }})
}} | ConvertTo-Json -Compress
"""
    result = _run_powershell(["-Command", script])
    snapshot: dict[str, Any] = {
        "exists": False,
        "probe_returncode": result["returncode"],
    }
    if result["returncode"] != 0:
        snapshot["probe_error"] = result["stderr"]
        return snapshot
    stdout = str(result.get("stdout") or "").strip()
    if not stdout:
        snapshot["probe_error"] = "empty task probe output"
        return snapshot
    try:
        parsed = json.loads(stdout.splitlines()[-1])
    except json.JSONDecodeError as exc:
        snapshot["probe_error"] = f"invalid task probe JSON: {exc}"
        snapshot["probe_stdout"] = stdout
        return snapshot
    if isinstance(parsed, dict):
        parsed["probe_returncode"] = result["returncode"]
        return parsed
    snapshot["probe_error"] = "task probe JSON was not an object"
    return snapshot


def _normalized(text: str) -> str:
    return text.replace("\\", "/").lower()


def _task_matches_desired(
    snapshot: dict[str, Any],
    *,
    project_root: Path,
    max_items: int,
) -> bool:
    if not snapshot.get("exists"):
        return False
    if str(snapshot.get("state", "")).lower() == "disabled":
        return False
    execute = _normalized(str(snapshot.get("execute", "")))
    if not execute.endswith("pythonw.exe"):
        return False
    arguments = _normalized(str(snapshot.get("arguments", "")))
    dispatcher_path = _normalized(str(project_root / "scripts" / "single_harness_bridge_dispatcher.py"))
    project_root_text = _normalized(str(project_root))
    return (
        dispatcher_path in arguments
        and "--project-root" in arguments
        and project_root_text in arguments
        and "--max-items" in arguments
        and str(max_items) in arguments
        and bool(snapshot.get("hidden")) is True
    )


def _invoke_installer(
    *,
    project_root: Path,
    task_name: str,
    interval_minutes: int,
    max_items: int,
    dry_run: bool,
) -> dict[str, Any]:
    installer = project_root / "scripts" / "install_single_harness_dispatcher_task.ps1"
    args = [
        "-File",
        str(installer),
        "-ProjectRoot",
        str(project_root),
        "-TaskName",
        task_name,
        "-IntervalMinutes",
        str(interval_minutes),
        "-MaxItems",
        str(max_items),
    ]
    if dry_run:
        args.append("-DryRun")
    return _run_powershell(args, timeout=60)


def _invoke_uninstaller(*, project_root: Path, task_name: str, dry_run: bool) -> dict[str, Any]:
    uninstaller = project_root / "scripts" / "uninstall_single_harness_dispatcher_task.ps1"
    args = ["-File", str(uninstaller), "-TaskName", task_name]
    if dry_run:
        args.append("-DryRun")
    return _run_powershell(args, timeout=30)


def _write_state(state_dir: Path, payload: dict[str, Any]) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    state_path = state_dir / AUTOMATION_STATE_FILENAME
    state_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _is_single_harness_dispatcher_active_substrate(project_root: Path) -> bool:
    """Return True if single_harness_dispatcher is the active substrate.

    Reads harness-state/bridge-substrate.json when present.
    If substrate is registered but not 'single_harness_dispatcher', returns False.
    If file is missing or invalid, default to True (fail open for backwards compatibility).
    """
    path = project_root / "harness-state" / "bridge-substrate.json"
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                substrate = data.get("substrate")
                if substrate and substrate != "single_harness_dispatcher":
                    return False
        except Exception:
            pass
    return True


def ensure_single_harness_automation(
    *,
    project_root: Path,
    state_dir: Path,
    task_name: str = DEFAULT_TASK_NAME,
    interval_minutes: int = DEFAULT_INTERVAL_MINUTES,
    max_items: int = DEFAULT_MAX_ITEMS,
    dispatch_now: bool = False,
    dry_run: bool = False,
    force_register: bool = False,
) -> dict[str, Any]:
    """Ensure scheduled-task activation matches the current role-map topology."""
    if not _is_single_harness_dispatcher_active_substrate(project_root):
        return {
            "skipped": True,
            "reason": "single_harness_dispatcher_substrate_inactive",
            "activated": False,
            "action": "inert",
        }

    dispatcher = _load_dispatcher_module()
    applicable, harness_id = dispatcher._is_single_harness_topology_applicable(project_root)
    command_handle = dispatcher._resolve_command_handle(project_root, harness_id) if harness_id else None

    # FAB-01 step 4: the scheduled-task wake activates for the gated-wake
    # condition (single-harness topology OR no active event-source harness), not
    # single-harness topology alone. In the normal multi-harness-with-event-source
    # topology, wake_applicable is False and the task is deactivated so the
    # cross-harness trigger remains the sole substrate.
    wake_applicable, wake_reason = dispatcher._gated_wake_applicable(project_root)

    payload: dict[str, Any] = {
        "schema_version": 1,
        "updated_at": _now_iso(),
        "project_root": str(project_root),
        "state_dir": str(state_dir),
        "task_name": task_name,
        "interval_minutes": interval_minutes,
        "max_items": max_items,
        "single_harness_applicable": applicable,
        "gated_wake_applicable": wake_applicable,
        "wake_reason": wake_reason,
        "harness_id": harness_id,
        "command_handle": command_handle,
        "dry_run": dry_run,
    }

    if sys.platform != "win32":
        payload.update(
            {
                "activated": False,
                "action": "unsupported_platform",
                "reason": "single-harness scheduled-task activation is Windows-only in this slice",
            }
        )
    elif wake_applicable:
        before = _task_snapshot(task_name)
        payload["task_before"] = before
        if force_register or not _task_matches_desired(before, project_root=project_root, max_items=max_items):
            install = _invoke_installer(
                project_root=project_root,
                task_name=task_name,
                interval_minutes=interval_minutes,
                max_items=max_items,
                dry_run=dry_run,
            )
            payload["task_install"] = install
            payload["activated"] = install["returncode"] == 0
            payload["action"] = "registered_or_updated"
        else:
            payload["activated"] = True
            payload["action"] = "already_active"
    else:
        uninstall = _invoke_uninstaller(project_root=project_root, task_name=task_name, dry_run=dry_run)
        payload["task_uninstall"] = uninstall
        payload["activated"] = False
        payload["action"] = "deactivated_no_wake_needed"

    if dispatch_now and wake_applicable:
        # enforce_wake_gate is defense-in-depth: the dispatch cycle re-checks
        # wake applicability so a topology change between activation and dispatch
        # cannot cause a spurious spawn.
        payload["dispatch_now"] = dispatcher.run_dispatcher(
            project_root=project_root,
            state_dir=state_dir,
            max_items=max_items,
            dry_run=dry_run,
            enforce_wake_gate=True,
        )
    elif dispatch_now:
        payload["dispatch_now"] = {"skipped": True, "reason": "wake_gate_not_applicable"}

    if not dry_run:
        try:
            _write_state(state_dir, payload)
        except OSError as exc:
            payload["state_write_error"] = str(exc)

    return payload


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=None)
    parser.add_argument("--state-dir", type=Path, default=None)
    parser.add_argument("--task-name", default=DEFAULT_TASK_NAME)
    parser.add_argument("--interval-minutes", type=int, default=DEFAULT_INTERVAL_MINUTES)
    parser.add_argument("--max-items", type=int, default=DEFAULT_MAX_ITEMS)
    parser.add_argument("--ensure", action="store_true")
    parser.add_argument("--dispatch-now", action="store_true")
    parser.add_argument("--force-register", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_argparser().parse_args(argv)
    try:
        project_root = _resolve_project_root(args.project_root)
        state_dir = (
            args.state_dir.resolve() if args.state_dir is not None else project_root.joinpath(*DEFAULT_STATE_SUBDIR)
        )
        # This CLI always reconciles scheduled-task activation; --ensure is
        # retained as an explicit hook/documentation flag.
        payload = ensure_single_harness_automation(
            project_root=project_root,
            state_dir=state_dir,
            task_name=args.task_name,
            interval_minutes=args.interval_minutes,
            max_items=args.max_items,
            dispatch_now=args.dispatch_now,
            dry_run=args.dry_run,
            force_register=args.force_register,
        )
        if args.verbose:
            print(json.dumps(payload, indent=2, sort_keys=True))
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - hook-safe fire-and-forget behavior
        print(f"single-harness bridge automation error (suppressed): {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
