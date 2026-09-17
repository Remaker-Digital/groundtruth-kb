#!/usr/bin/env python3
"""Bounded Cursor launch/authentication checks using a native installation record.

Passing these checks establishes neither dispatchability nor complete harness
qualification. An actual prompt launch is opt-in with --live.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import quote

from groundtruth_kb import cursor_harness
from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.config import GTConfig, GTConfigError

HARNESS_ID = "E"
HARNESS_NAME = "cursor"
CURSOR_SHIM_RELATIVE = Path("scripts") / "cursor_harness.py"
CURSOR_DISPATCH_SKILL = "bridge-review"
CURSOR_VERIFICATION_SKILL = "verification"
DEFAULT_LIVE_PROMPT = "Reply with READY only."
DEFAULT_TIMEOUT_SECONDS = 60.0


class VerificationError(RuntimeError):
    """Raised when Cursor readiness cannot be evaluated."""


def load_harness_record(project_root: Path, recipient: str = HARNESS_ID) -> dict[str, Any]:
    """Read the exact record; missing or unavailable authority has no fallback."""
    if not recipient or recipient != recipient.strip():
        raise VerificationError("An exact native installation ID is required")
    try:
        config = GTConfig.load(project_root.resolve() / "groundtruth.toml", discover=False)
        if not config.authority_url:
            raise VerificationError("native_authority_not_configured")
        record = AuthorityClient(config.authority_url, timeout=10).request(
            "GET", f"/v1/harnesses/{quote(recipient, safe='')}"
        )
    except (OSError, GTConfigError, ValueError) as exc:
        raise VerificationError("invalid_selected_configuration") from exc
    except AuthorityClientError as exc:
        raise VerificationError(f"native_harness_read_failed: {exc.code}") from exc
    if not isinstance(record, dict) or record.get("id") != recipient:
        raise VerificationError("invalid_native_harness_response")
    return record


def _headless_argv(record: dict[str, Any]) -> list[str]:
    surfaces = record.get("invocation_surfaces")
    headless = surfaces.get("headless", {}) if isinstance(surfaces, dict) else {}
    argv = headless.get("argv", []) if isinstance(headless, dict) else []
    return argv if isinstance(argv, list) and argv and all(isinstance(part, str) and part for part in argv) else []


def _argv_uses_cursor_shim(argv: list[str]) -> bool:
    normalized = [part.replace("\\", "/") for part in argv]
    return CURSOR_SHIM_RELATIVE.as_posix() in normalized


def _argv_selects_skill(argv: list[str], skill: str) -> bool:
    positions = [index for index, part in enumerate(argv) if part == "--skill"]
    return len(positions) == 1 and positions[0] + 1 < len(argv) and argv[positions[0] + 1] == skill


def _first_failed_detail(checks: list[dict[str, Any]]) -> str:
    for check in checks:
        if not check.get("passed"):
            return f"{check.get('name')}: {check.get('detail') or 'failed'}"
    return ""


def _run_live_probe(
    *,
    project_root: Path,
    prompt: str,
    skill: str,
    timeout: float,
    runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
) -> dict[str, Any]:
    command = [
        sys.executable,
        str(project_root / CURSOR_SHIM_RELATIVE),
        "--prompt",
        prompt,
        "--skill",
        skill,
        "--timeout",
        str(timeout),
    ]
    active_runner = runner or subprocess.run
    completed = active_runner(
        command,
        cwd=project_root,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=timeout + 5.0,
        check=False,
        creationflags=cursor_harness._windows_no_window_creationflags(),
    )
    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    return {
        "ok": completed.returncode == 0 and bool(stdout.strip()),
        "returncode": completed.returncode,
        "stderr_bytes": len(stderr.encode("utf-8")),
        "stdout_bytes": len(stdout.encode("utf-8")),
    }


def _run_auth_probe(
    agent_command: list[str],
    *,
    project_root: Path,
    runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
    timeout: float = 10.0,
) -> dict[str, Any]:
    command = [*agent_command, "status", "--format", "json"]
    active_runner = runner or subprocess.run
    env = cursor_harness._cursor_agent_env(project_root=project_root)
    completed = active_runner(
        command,
        cwd=project_root,
        env=env,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
        creationflags=cursor_harness._windows_no_window_creationflags(),
    )
    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    authenticated = False
    try:
        payload = json.loads(stdout) if stdout.strip() else {}
    except json.JSONDecodeError:
        payload = {}
    if isinstance(payload, dict):
        authenticated = payload.get("isAuthenticated") is True and completed.returncode == 0
    return {
        "authenticated": authenticated,
        "cursor_api_key_available": bool(env.get("CURSOR_API_KEY")),
        "returncode": completed.returncode,
        "stderr_bytes": len(stderr.encode("utf-8")),
        "stdout_bytes": len(stdout.encode("utf-8")),
    }


def evaluate_readiness(
    *,
    project_root: Path,
    recipient: str = HARNESS_ID,
    require_live: bool = False,
    live_prompt: str = DEFAULT_LIVE_PROMPT,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    agent_resolver: Callable[[], list[str]] | None = None,
    auth_runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
    live_runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
) -> dict[str, Any]:
    """Check launch prerequisites, not bridge qualification or activation.

    Role comes from a receiving context's exact init marker, never this record.
    """
    if not math.isfinite(timeout) or timeout <= 0:
        raise VerificationError("timeout must be finite and positive")
    checks: list[dict[str, Any]] = []

    def add_check(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})

    record = load_harness_record(project_root, recipient)
    record_ok = record.get("harness_name") == HARNESS_NAME and record.get("harness_type") == HARNESS_NAME
    add_check(
        "native cursor record",
        record_ok,
        f"name={record.get('harness_name')!r}; type={record.get('harness_type')!r}",
    )

    argv = _headless_argv(record)
    argv_ok = bool(argv) and _argv_uses_cursor_shim(argv) and _argv_selects_skill(argv, CURSOR_DISPATCH_SKILL)
    add_check("native headless argv", argv_ok, "configured" if argv else "missing argv")

    shim_path = project_root / CURSOR_SHIM_RELATIVE
    shim_ok = shim_path.is_file()
    add_check("cursor harness shim", shim_ok, CURSOR_SHIM_RELATIVE.as_posix())

    try:
        for skill in (CURSOR_DISPATCH_SKILL, CURSOR_VERIFICATION_SKILL):
            cursor_harness._skill_system_prompt(skill, project_root=project_root)
        instructions_ok = True
        instructions_detail = "Current review routes load from this harness's own projection"
    except cursor_harness.CursorHarnessError as exc:
        instructions_ok = False
        instructions_detail = str(exc)
    add_check("local review instructions", instructions_ok, instructions_detail)

    resolver = agent_resolver or cursor_harness._resolve_agent_command
    try:
        agent_command = resolver()
        agent_ok = bool(agent_command)
        agent_detail = "resolved" if agent_ok else "unavailable"
    except cursor_harness.CursorHarnessError as exc:
        agent_command = []
        agent_ok = False
        agent_detail = type(exc).__name__
    add_check("headless Cursor Agent CLI", agent_ok, agent_detail)

    auth_probe: dict[str, Any] | None = None
    auth_ok = False
    if record_ok and argv_ok and shim_ok and instructions_ok and agent_ok:
        try:
            auth_probe = _run_auth_probe(
                agent_command,
                project_root=project_root,
                runner=auth_runner,
                timeout=min(timeout, 10.0),
            )
            auth_ok = bool(auth_probe["authenticated"])
            auth_detail = (
                f"authenticated={auth_probe['authenticated']}; "
                f"cursor_api_key_available={auth_probe['cursor_api_key_available']}"
            )
        except (OSError, subprocess.SubprocessError, subprocess.TimeoutExpired) as exc:
            auth_probe = {"authenticated": False, "error": type(exc).__name__}
            auth_detail = auth_probe["error"]
    else:
        auth_detail = "not run because launch prerequisites failed"
    add_check("headless Cursor Agent authentication", auth_ok, auth_detail)

    live_probe: dict[str, Any] | None = None
    live_ok = True
    if require_live and record_ok and argv_ok and shim_ok and instructions_ok and agent_ok and auth_ok:
        try:
            live_probe = _run_live_probe(
                project_root=project_root,
                prompt=live_prompt,
                skill=CURSOR_DISPATCH_SKILL,
                timeout=timeout,
                runner=live_runner,
            )
            live_ok = bool(live_probe["ok"])
            detail = f"returncode={live_probe['returncode']}; stdout_bytes={live_probe['stdout_bytes']}"
        except (OSError, subprocess.SubprocessError, subprocess.TimeoutExpired) as exc:
            live_probe = {"ok": False, "error": type(exc).__name__}
            live_ok = False
            detail = live_probe["error"]
        add_check("live bridge-review probe", live_ok, detail)
    elif require_live:
        live_ok = False
        add_check("live bridge-review probe", False, "not run because launch prerequisites failed")

    probe_passed = record_ok and argv_ok and shim_ok and instructions_ok and agent_ok and auth_ok and live_ok
    return {
        "auth_probe": auth_probe,
        "cursor_adaptation": cursor_harness.cursor_adaptation_metadata(project_root),
        "checks": checks,
        "probe_scope": "launch_prerequisites_authentication_and_bounded_prompt"
        if require_live
        else "launch_prerequisites_and_authentication",
        "harness_qualification": "unqualified",
        "authority_source": "native_harness_record",
        "first_failed_check": _first_failed_detail(checks),
        "harness_id": recipient,
        "live_probe": live_probe,
        "probe_passed": probe_passed,
        "recipient": recipient,
        "status": record.get("status"),
    }


def main(argv: list[str] | None = None, *, project_root: Path | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipient", default=HARNESS_ID)
    parser.add_argument("--project-root", default=project_root or Path.cwd(), type=Path)
    parser.add_argument("--live", action="store_true", help="Run a live non-mutating bridge-review prompt probe.")
    parser.add_argument("--prompt", default=DEFAULT_LIVE_PROMPT)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        result = evaluate_readiness(
            project_root=args.project_root.resolve(),
            recipient=args.recipient,
            require_live=args.live,
            live_prompt=args.prompt,
            timeout=args.timeout,
        )
    except VerificationError as exc:
        payload = {"error": str(exc), "harness_id": args.recipient, "probe_passed": False}
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))  # print-ok: readiness JSON protocol output
        else:
            sys.stderr.write(f"ERROR: {exc}\n")
        return 2

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))  # print-ok: readiness JSON protocol output
    else:
        print(f"probe_passed={result['probe_passed']}")  # print-ok: readiness key=value protocol output
        print(f"harness_qualification={result['harness_qualification']}")  # print-ok: protocol output
        print(f"first_failed_check={result['first_failed_check']}")  # print-ok: protocol output
    return 0 if result["probe_passed"] else 1
