#!/usr/bin/env python3
"""Deterministic Cursor dispatch readiness probe."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts import cursor_harness  # noqa: E402
from scripts.gtkb_bridge_writer import PROVIDER_VERDICT_STATUSES  # noqa: E402
from scripts.harness_projection_reader import load_harness_projection  # noqa: E402

HARNESS_ID = "E"
HARNESS_NAME = "cursor"
CURSOR_SHIM_RELATIVE = Path("scripts") / "cursor_harness.py"
CURSOR_DISPATCH_SKILL = "bridge-review"
CURSOR_VERIFICATION_SKILL = "verification"
DEFAULT_LIVE_PROMPT = "Reply with READY only."
DEFAULT_TIMEOUT_SECONDS = 60.0
DISPATCH_ROLES = frozenset({"loyal-opposition", "prime-builder"})


class VerificationError(RuntimeError):
    """Raised when Cursor readiness cannot be evaluated."""


def _hidden_process_kwargs() -> dict[str, int]:
    if sys.platform.startswith("win"):
        return {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)}
    return {}


def load_harness_record(project_root: Path, recipient: str = HARNESS_ID) -> dict[str, Any]:
    """Load the Cursor harness record from the generated registry projection."""

    registry = load_harness_projection(project_root)
    for record in registry.get("harnesses", []):
        if isinstance(record, dict) and str(record.get("id")) == recipient:
            return record
    raise VerificationError(f"recipient harness not found in registry: {recipient}")


def _headless_argv(record: dict[str, Any]) -> list[str]:
    surfaces = record.get("invocation_surfaces")
    headless = surfaces.get("headless", {}) if isinstance(surfaces, dict) else {}
    argv = headless.get("argv", []) if isinstance(headless, dict) else []
    if not isinstance(argv, list):
        return []
    return [part for part in argv if isinstance(part, str) and part]


def _argv_uses_cursor_shim(argv: list[str]) -> bool:
    normalized = [part.replace("\\", "/") for part in argv]
    return CURSOR_SHIM_RELATIVE.as_posix() in normalized


def _argv_selects_skill(argv: list[str], skill: str) -> bool:
    return "--skill" in argv and skill in argv


def _role_tokens(record: dict[str, Any]) -> set[str]:
    raw = record.get("role")
    if isinstance(raw, str):
        return {raw}
    if isinstance(raw, list):
        return {item for item in raw if isinstance(item, str)}
    return set()


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
        **_hidden_process_kwargs(),
    )
    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    return {
        "command": command,
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
    env = cursor_harness._cursor_agent_env()
    completed = active_runner(
        command,
        cwd=project_root,
        env=env,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
        **_hidden_process_kwargs(),
    )
    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    authenticated = False
    status = "unknown"
    message = ""
    try:
        payload = json.loads(stdout) if stdout.strip() else {}
    except json.JSONDecodeError:
        payload = {}
        message = "status output was not JSON"
    if isinstance(payload, dict):
        authenticated = bool(payload.get("isAuthenticated"))
        status = str(payload.get("status") or status)
        message = str(payload.get("message") or message)
    return {
        "authenticated": authenticated,
        "command": command,
        "cursor_api_key_available": bool(env.get("CURSOR_API_KEY")),
        "message": message,
        "returncode": completed.returncode,
        "status": status,
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
    """Return fail-closed Cursor headless dispatch readiness evidence."""

    checks: list[dict[str, Any]] = []

    def add_check(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})

    record = load_harness_record(project_root, recipient)
    record_ok = record.get("harness_name") == HARNESS_NAME and record.get("harness_type") == HARNESS_NAME
    add_check(
        "registry cursor record",
        record_ok,
        f"name={record.get('harness_name')!r}; type={record.get('harness_type')!r}",
    )

    argv = _headless_argv(record)
    argv_ok = bool(argv) and _argv_uses_cursor_shim(argv) and _argv_selects_skill(argv, CURSOR_DISPATCH_SKILL)
    add_check("registry headless argv", argv_ok, " ".join(argv) if argv else "missing argv")

    shim_path = project_root / CURSOR_SHIM_RELATIVE
    shim_ok = shim_path.is_file()
    add_check("cursor harness shim", shim_ok, CURSOR_SHIM_RELATIVE.as_posix())

    publication_contract = cursor_harness.governed_lo_publication_contract()
    publication_ok = (
        publication_contract.get("schema_version") == 1
        and publication_contract.get("execution_mode") == "ask"
        and publication_contract.get("output_format") == "text"
        and publication_contract.get("publisher") == "publish_lo_verdict"
        and publication_contract.get("supported_verdicts") == sorted(PROVIDER_VERDICT_STATUSES)
    )
    add_check(
        "governed read-only LO publication",
        publication_ok,
        json.dumps(publication_contract, sort_keys=True, separators=(",", ":")),
    )

    resolver = agent_resolver or cursor_harness._resolve_agent_command
    try:
        agent_command = resolver()
        agent_ok = bool(agent_command)
        agent_detail = " ".join(agent_command)
    except cursor_harness.CursorHarnessError as exc:
        agent_command = []
        agent_ok = False
        agent_detail = str(exc)
    add_check("headless Cursor Agent CLI", agent_ok, agent_detail)

    auth_probe: dict[str, Any] | None = None
    auth_ok = False
    if agent_ok:
        try:
            auth_probe = _run_auth_probe(
                agent_command,
                project_root=project_root,
                runner=auth_runner,
                timeout=min(timeout, 10.0),
            )
            auth_ok = bool(auth_probe["authenticated"])
            auth_detail = (
                f"status={auth_probe['status']}; message={auth_probe['message']}; "
                f"cursor_api_key_available={auth_probe['cursor_api_key_available']}"
            )
        except (OSError, subprocess.SubprocessError, subprocess.TimeoutExpired) as exc:
            auth_probe = {"authenticated": False, "error": f"{type(exc).__name__}: {exc}"}
            auth_detail = auth_probe["error"]
    else:
        auth_detail = "skipped because agent CLI is unavailable"
    add_check("headless Cursor Agent authentication", auth_ok, auth_detail)

    live_probe: dict[str, Any] | None = None
    live_ok = True
    if require_live and record_ok and argv_ok and shim_ok and agent_ok and auth_ok:
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
            live_probe = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
            live_ok = False
            detail = live_probe["error"]
        add_check("live bridge-review probe", live_ok, detail)

    ready_for_activation = record_ok and argv_ok and shim_ok and publication_ok and agent_ok and auth_ok and live_ok
    role = _role_tokens(record)
    dispatchable_now = (
        ready_for_activation
        and record.get("status") == "active"
        and bool(record.get("can_receive_dispatch"))
        and bool(role & DISPATCH_ROLES)
    )
    return {
        "agent_command": agent_command,
        "auth_probe": auth_probe,
        "cursor_adaptation": cursor_harness.cursor_adaptation_metadata(project_root),
        "checks": checks,
        "dispatchable_now": dispatchable_now,
        "first_failed_check": _first_failed_detail(checks),
        "harness_id": recipient,
        "headless_argv": argv,
        "live_probe": live_probe,
        "publication_contract": publication_contract,
        "ready": ready_for_activation,
        "recipient": recipient,
        "role": sorted(role),
        "status": record.get("status"),
        "can_receive_dispatch": bool(record.get("can_receive_dispatch")),
    }


def _load_project_env_local() -> None:
    try:
        from scripts._env import load_env_local
    except ImportError:
        from _env import load_env_local  # type: ignore[import-not-found]

    load_env_local()


def main(argv: list[str] | None = None) -> int:
    try:
        _load_project_env_local()
    except Exception:  # noqa: BLE001 - missing/unreadable .env.local must not block readiness probe
        pass
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipient", default=HARNESS_ID)
    parser.add_argument("--project-root", default=PROJECT_ROOT, type=Path)
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
        payload = {"error": str(exc), "harness_id": args.recipient, "ready": False}
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"ready={result['ready']}")
        print(f"dispatchable_now={result['dispatchable_now']}")
        print(f"first_failed_check={result['first_failed_check']}")
    return 0 if result["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
