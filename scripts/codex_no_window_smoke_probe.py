#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Run a bounded Codex no-window smoke and write schema-v2 evidence."""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.windows_subprocess import (  # noqa: E402
    create_private_desktop_name,
    no_window_subprocess_kwargs,
    prefer_pythonw_executable,
    private_desktop_popen_kwargs,
)

SCHEMA_VERSION = 3
DEFAULT_RUNS = 2
DEFAULT_COMMANDS_PER_RUN = 3
DEFAULT_TIMEOUT_SECONDS = 180
REQUESTED_PERMISSIONS_PROFILE = ":workspace"
EXPECTED_EFFECTIVE_PROFILE = "workspace-write"


def _session_scratch_dirname() -> str:
    """Session-scoped scratch subdirectory name per canon s17."""
    try:
        from scripts.gtkb_session_id import session_scratch_dirname
    except ImportError:  # pragma: no cover - direct script execution path
        from gtkb_session_id import session_scratch_dirname

    return session_scratch_dirname()


# Canon s17: probe artifacts are session-scoped scratch under the canonical
# scratchpad root, never `.gtkb-state` (and never the retired bridge-poller tree).
VERIFICATION_RELATIVE_PATH = Path("scratchpad") / _session_scratch_dirname() / "codex-no-window-verification.json"
RUN_WITH_STATUS_CONFIG_ENV_VAR = "GTKB_RUN_WITH_STATUS_CONFIG_B64"
_EFFECTIVE_PROFILE_RE = re.compile(r"(?im)^\s*sandbox:\s*([^\s\[]+)")
_ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


def _now() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


def _iso(value: dt.datetime) -> str:
    return value.astimezone(dt.UTC).isoformat().replace("+00:00", "Z")


def _preview(value: str, limit: int = 2000) -> str:
    return _ANSI_ESCAPE_RE.sub("", value)[:limit]


def verification_path(project_root: Path) -> Path:
    return project_root / VERIFICATION_RELATIVE_PATH


def _powershell_executable() -> str | None:
    return shutil.which("powershell") or shutil.which("pwsh")


def observe_visible_power_shell_windows() -> list[dict[str, Any]]:
    """Return visible pwsh/powershell window observations on Windows."""
    if sys.platform != "win32":
        return [{"skipped": True, "reason": "non-windows", "visible_count": 0}]
    powershell = _powershell_executable()
    if powershell is None:
        return [{"skipped": True, "reason": "powershell-not-found", "visible_count": 0}]
    command = [
        powershell,
        "-NoProfile",
        "-Command",
        (
            "Get-Process pwsh,powershell -ErrorAction SilentlyContinue | "
            "Where-Object { $_.MainWindowHandle -ne 0 } | "
            "Select-Object Id,ProcessName,MainWindowTitle | ConvertTo-Json -Compress"
        ),
    ]
    try:
        completed = subprocess.run(
            command,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            check=False,
            **no_window_subprocess_kwargs(),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [{"error": str(exc), "visible_count": 0}]
    raw = completed.stdout.strip()
    if not raw:
        return [{"visible_count": 0, "returncode": completed.returncode}]
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return [{"visible_count": 0, "returncode": completed.returncode, "stdout_preview": _preview(raw)}]
    rows = parsed if isinstance(parsed, list) else [parsed]
    visible_rows = [row for row in rows if isinstance(row, dict)]
    return [
        {
            "visible_count": len(visible_rows),
            "returncode": completed.returncode,
            "processes": visible_rows,
        }
    ]


def _markers(run_index: int, command_count: int, nonce: str) -> list[str]:
    return [f"GTKB-WI5135-R{run_index}-C{index}-{nonce}" for index in range(1, command_count + 1)]


def build_prompt(markers: list[str], sentinel_path: Path, sentinel_value: str) -> str:
    if len(markers) != 3:
        raise ValueError("sentinel lifecycle requires exactly three markers")
    path = str(sentinel_path).replace("\\", "\\\\").replace("'", "\\'")
    value = sentinel_value.replace("'", "\\'")
    create_marker, read_marker, remove_marker = (marker.replace("'", "\\'") for marker in markers)
    commands = "\n".join(
        [
            (
                '1. python -c "from pathlib import Path; '
                f"p=Path(r'{path}'); p.write_text('{value}', encoding='utf-8'); "
                f"assert p.is_file(); print('{create_marker}')\""
            ),
            (
                '2. python -c "from pathlib import Path; '
                f"p=Path(r'{path}'); assert p.read_text(encoding='utf-8') == '{value}'; "
                f"print('{read_marker}')\""
            ),
            (
                '3. python -c "from pathlib import Path; '
                f"p=Path(r'{path}'); p.unlink(); assert not p.exists(); print('{remove_marker}')\""
            ),
        ]
    )
    return (
        "Run the following shell commands exactly, in order, and then stop. "
        "Do not summarize; let the command output appear in stdout.\n"
        f"{commands}\n"
    )


def build_codex_command(codex_executable: str, prompt: str, project_root: Path) -> list[str]:
    return [
        codex_executable,
        "exec",
        "--model",
        "gpt-5.5",
        "-c",
        'approval_policy="never"',
        "-c",
        'model_reasoning_effort="xhigh"',
        "-c",
        'default_permissions=":workspace"',
        prompt,
        "--cd",
        str(project_root),
        "--add-dir",
        ".codex",
    ]


def _step_records(markers: list[str], transcript: str, returncode: int | None) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for index, marker in enumerate(markers, start=1):
        occurrence_count = transcript.count(marker)
        contains = occurrence_count >= 2
        records.append(
            {
                "index": index,
                "marker": marker,
                "returncode": returncode,
                "stdout_contains_marker": contains,
                "marker_occurrence_count": occurrence_count,
                "transcript_preview": _preview(transcript),
            }
        )
    return records


def observed_effective_profile(transcript: str) -> tuple[str | None, list[str]]:
    profiles = [match.group(1).strip().lower() for match in _EFFECTIVE_PROFILE_RE.finditer(transcript)]
    unique = list(dict.fromkeys(profiles))
    return (unique[0] if len(unique) == 1 else None), profiles


def _visible_detected(observations: list[dict[str, Any]]) -> bool:
    return any(int(obs.get("visible_count") or 0) > 0 for obs in observations if isinstance(obs, dict))


def _codex_launch_kwargs(desktop_name: str | None) -> dict[str, object]:
    if sys.platform == "win32" and desktop_name:
        return private_desktop_popen_kwargs(desktop_name=desktop_name)
    return no_window_subprocess_kwargs()


def _b64_json(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return base64.b64encode(raw).decode("ascii")


def _run_with_dispatch_wrapper(
    command: list[str],
    *,
    project_root: Path,
    desktop_name: str | None,
    timeout_seconds: int,
) -> subprocess.CompletedProcess[str]:
    proof_dir = project_root / "scratchpad" / _session_scratch_dirname() / "codex-no-window-smoke"
    proof_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{_now().strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    stdout_path = proof_dir / f"{stem}.stdout.log"
    stderr_path = proof_dir / f"{stem}.stderr.log"
    status_path = proof_dir / f"{stem}.exit_code"
    env = dict(os.environ)
    env[RUN_WITH_STATUS_CONFIG_ENV_VAR] = _b64_json(
        {
            "stdin_path": None,
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
            "lifetime_seconds": timeout_seconds,
            "status_file_path": str(status_path),
            "cmd_args": command,
        }
    )
    wrapped = [
        prefer_pythonw_executable(sys.executable),
        str(project_root / "scripts" / "run_with_status.py"),
        "--config-env",
    ]
    process = subprocess.Popen(
        wrapped,
        cwd=str(project_root),
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
        **_codex_launch_kwargs(desktop_name),
    )
    try:
        wrapper_returncode = process.wait(timeout=timeout_seconds + 30)
    except subprocess.TimeoutExpired:
        process.kill()
        wrapper_returncode = process.wait(timeout=10)
    deadline = time.monotonic() + 10
    while not status_path.exists() and time.monotonic() < deadline:
        time.sleep(0.1)
    try:
        status_text = status_path.read_text(encoding="utf-8").strip()
        child_returncode = int(status_text)
    except (OSError, ValueError):
        child_returncode = wrapper_returncode
    try:
        stdout = stdout_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        stdout = ""
    try:
        stderr = stderr_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        stderr = ""
    completed = subprocess.CompletedProcess(command, child_returncode, stdout=stdout, stderr=stderr)
    completed.wrapper_returncode = wrapper_returncode  # type: ignore[attr-defined]
    completed.wrapper_stdout_path = stdout_path.as_posix()  # type: ignore[attr-defined]
    completed.wrapper_stderr_path = stderr_path.as_posix()  # type: ignore[attr-defined]
    completed.wrapper_status_path = status_path.as_posix()  # type: ignore[attr-defined]
    return completed


def run_probe(
    *,
    project_root: Path,
    codex_executable: str,
    runs: int = DEFAULT_RUNS,
    commands_per_run: int = DEFAULT_COMMANDS_PER_RUN,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    command_runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    window_observer: Callable[[], list[dict[str, Any]]] = observe_visible_power_shell_windows,
    use_dispatch_wrapper: bool = False,
) -> dict[str, Any]:
    started = _now()
    nonce = uuid.uuid4().hex[:10]
    desktop_name = create_private_desktop_name("gtkb-codex-smoke") if sys.platform == "win32" else None
    run_records: list[dict[str, Any]] = []
    all_observations: list[dict[str, Any]] = []

    for run_index in range(1, runs + 1):
        if commands_per_run != 3:
            raise ValueError("commands_per_run must be 3 for the sentinel lifecycle")
        markers = _markers(run_index, commands_per_run, nonce)
        sentinel_dir = project_root / "scratchpad" / _session_scratch_dirname() / "codex-no-window-smoke"
        sentinel_dir.mkdir(parents=True, exist_ok=True)
        sentinel_path = sentinel_dir / f"wi5310-{run_index}-{uuid.uuid4().hex}.sentinel"
        sentinel_value = f"GTKB-WI5310-SENTINEL-{run_index}-{nonce}"
        before = window_observer()
        all_observations.extend(before)
        command = build_codex_command(
            codex_executable,
            build_prompt(markers, sentinel_path, sentinel_value),
            project_root,
        )
        wrapper_returncode = None
        wrapper_stdout_path = None
        wrapper_stderr_path = None
        wrapper_status_path = None
        try:
            if use_dispatch_wrapper:
                completed = _run_with_dispatch_wrapper(
                    command,
                    project_root=project_root,
                    desktop_name=desktop_name,
                    timeout_seconds=timeout_seconds,
                )
            else:
                completed = command_runner(
                    command,
                    cwd=str(project_root),
                    text=True,
                    capture_output=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=timeout_seconds,
                    check=False,
                    **_codex_launch_kwargs(desktop_name),
                )
            returncode = completed.returncode
            stdout = completed.stdout or ""
            stderr = completed.stderr or ""
            error = None
            wrapper_returncode = getattr(completed, "wrapper_returncode", None)
            wrapper_stdout_path = getattr(completed, "wrapper_stdout_path", None)
            wrapper_stderr_path = getattr(completed, "wrapper_stderr_path", None)
            wrapper_status_path = getattr(completed, "wrapper_status_path", None)
        except subprocess.TimeoutExpired as exc:
            returncode = None
            stdout = exc.stdout if isinstance(exc.stdout, str) else ""
            stderr = exc.stderr if isinstance(exc.stderr, str) else ""
            error = f"timeout after {timeout_seconds}s"
        except OSError as exc:
            returncode = None
            stdout = ""
            stderr = ""
            error = str(exc)
        transcript = f"{stdout}\n{stderr}"
        effective_profile, observed_profiles = observed_effective_profile(transcript)
        steps = _step_records(markers, transcript, returncode)
        residual_before_cleanup = sentinel_path.exists()
        cleanup_error = None
        if residual_before_cleanup:
            try:
                sentinel_path.unlink()
            except OSError as exc:
                cleanup_error = str(exc)
        residual_after_cleanup = sentinel_path.exists()
        sentinel_lifecycle_ok = (
            returncode == 0
            and all(step["stdout_contains_marker"] for step in steps)
            and not residual_before_cleanup
            and not residual_after_cleanup
        )
        after = window_observer()
        all_observations.extend(after)
        run_records.append(
            {
                "run_index": run_index,
                "command": command[:10] + ["..."],
                "returncode": returncode,
                "stdout_preview": _preview(stdout.replace(str(project_root), "{{PROJECT_ROOT}}")),
                "stderr_preview": _preview(stderr.replace(str(project_root), "{{PROJECT_ROOT}}")),
                "error": error,
                "command_steps": steps,
                "requested_permissions_profile": REQUESTED_PERMISSIONS_PROFILE,
                "observed_effective_profile": effective_profile,
                "observed_effective_profiles": observed_profiles,
                "effective_profile_ok": effective_profile == EXPECTED_EFFECTIVE_PROFILE,
                "sentinel_relative_path": sentinel_path.relative_to(project_root).as_posix(),
                "sentinel_create_ok": steps[0]["stdout_contains_marker"],
                "sentinel_read_ok": steps[1]["stdout_contains_marker"],
                "sentinel_remove_ok": steps[2]["stdout_contains_marker"],
                "sentinel_lifecycle_ok": sentinel_lifecycle_ok,
                "sentinel_residual_before_cleanup": residual_before_cleanup,
                "sentinel_residual_after_cleanup": residual_after_cleanup,
                "sentinel_cleanup_error": cleanup_error,
                "window_observations": [*before, *after],
                "wrapper_returncode": wrapper_returncode,
                "wrapper_stdout_path": wrapper_stdout_path,
                "wrapper_stderr_path": wrapper_stderr_path,
                "wrapper_status_path": wrapper_status_path,
            }
        )

    visible_window_detected = _visible_detected(all_observations)
    marker_chain_ok = all(
        step.get("stdout_contains_marker") is True and step.get("returncode") == 0
        for run in run_records
        for step in run["command_steps"]
    )
    effective_profile_ok = all(run["effective_profile_ok"] for run in run_records)
    sentinel_lifecycle_ok = all(run["sentinel_lifecycle_ok"] for run in run_records)
    wrapper_ok = all(run["wrapper_returncode"] == 0 for run in run_records) if use_dispatch_wrapper else True
    result = (
        "pass"
        if marker_chain_ok
        and effective_profile_ok
        and sentinel_lifecycle_ok
        and wrapper_ok
        and not visible_window_detected
        else "fail"
    )
    verified_at = _now()
    return {
        "schema_version": SCHEMA_VERSION,
        "probe": "codex_no_window_schema_v3_workspace_sentinel",
        "result": result,
        "requested_permissions_profile": REQUESTED_PERMISSIONS_PROFILE,
        "expected_effective_profile": EXPECTED_EFFECTIVE_PROFILE,
        "effective_profile_ok": effective_profile_ok,
        "sentinel_lifecycle_ok": sentinel_lifecycle_ok,
        "wrapper_ok": wrapper_ok,
        "visible_window_detected": visible_window_detected,
        "verified_at": _iso(verified_at),
        "expires_at": _iso(verified_at + dt.timedelta(hours=4)),
        "started_at": _iso(started),
        "finished_at": _iso(verified_at),
        "run_count": runs,
        "commands_per_run": commands_per_run,
        "containment_mechanism": "windows_private_desktop" if desktop_name else "direct_no_window",
        "containment_desktop": desktop_name,
        "dispatcher_wrapper_path": use_dispatch_wrapper,
        "marker_chain_ok": marker_chain_ok,
        "window_observations": all_observations,
        "runs": run_records,
    }


def write_payload(project_root: Path, payload: dict[str, Any], *, output: Path | None = None) -> Path:
    path = output or verification_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--codex-executable", default="codex")
    parser.add_argument("--runs", type=int, default=DEFAULT_RUNS)
    parser.add_argument("--commands-per-run", type=int, default=DEFAULT_COMMANDS_PER_RUN)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--dispatch-wrapper", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    project_root = args.project_root.resolve()
    payload = run_probe(
        project_root=project_root,
        codex_executable=args.codex_executable,
        runs=args.runs,
        commands_per_run=args.commands_per_run,
        timeout_seconds=args.timeout,
        use_dispatch_wrapper=args.dispatch_wrapper,
    )
    if not args.no_write:
        path = write_payload(project_root, payload, output=args.output)
        payload["verification_path"] = path.as_posix()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"result={payload['result']}")
        print(f"visible_window_detected={payload['visible_window_detected']}")
        if "verification_path" in payload:
            print(f"verification_path={payload['verification_path']}")
    return 0 if payload["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
