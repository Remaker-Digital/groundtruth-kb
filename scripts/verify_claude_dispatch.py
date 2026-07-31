#!/usr/bin/env python3
"""Deterministic Claude Code dispatch readiness probe."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.harness_projection_reader import load_harness_projection  # noqa: E402

HARNESS_ID = "B"
HARNESS_NAME = "claude"
HARNESS_TYPE = "claude"
DEFAULT_LIVE_PROMPT = "Reply with READY only."
DEFAULT_TIMEOUT_SECONDS = 60.0


class VerificationError(RuntimeError):
    """Raised when Claude readiness cannot be evaluated."""


def _load_harness_record(project_root: Path, recipient: str = HARNESS_ID) -> dict[str, Any]:
    registry = load_harness_projection(project_root)
    for record in registry.get("harnesses", []):
        if isinstance(record, dict) and str(record.get("id")) == recipient:
            return record
    raise VerificationError(f"recipient harness not found in registry: {recipient}")


def _headless_argv(record: dict[str, Any]) -> list[str]:
    surfaces = record.get("invocation_surfaces")
    headless = surfaces.get("headless", {}) if isinstance(surfaces, dict) else {}
    argv = headless.get("argv", []) if isinstance(headless, dict) else []
    return [str(part) for part in argv if str(part)]


def _hidden_process_kwargs() -> dict[str, int]:
    if sys.platform.startswith("win"):
        return {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)}
    return {}


def _render_headless_command(
    argv: list[str],
    *,
    project_root: Path,
    prompt: str,
    resolved_executable: str | None,
) -> list[str]:
    command = [part.replace("{{PROMPT}}", prompt).replace("{{PROJECT_ROOT}}", str(project_root)) for part in argv]
    if command and resolved_executable:
        command[0] = resolved_executable
    return command


def _run_live_probe(
    command: list[str],
    *,
    project_root: Path,
    timeout: float,
    runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
) -> dict[str, Any]:
    active_runner = runner or subprocess.run
    completed = active_runner(
        command,
        cwd=project_root,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=timeout,
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


def evaluate_readiness(
    *,
    project_root: Path,
    recipient: str = HARNESS_ID,
    require_executable: bool = True,
    executable_resolver: Callable[[str], str | None] | None = None,
    require_live: bool = False,
    live_prompt: str = DEFAULT_LIVE_PROMPT,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    live_runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
) -> dict[str, Any]:
    record = _load_harness_record(project_root, recipient)
    if record.get("harness_type") != HARNESS_TYPE:
        raise VerificationError(f"recipient {recipient} is not {HARNESS_TYPE}: {record.get('harness_type')!r}")

    argv = _headless_argv(record)
    resolver = executable_resolver or shutil.which
    resolved_executable = resolver(argv[0]) if argv else None
    executable_ok = bool(resolved_executable) if require_executable else True
    static_ok = bool(argv) and executable_ok
    live_probe: dict[str, Any] | None = None
    live_ok = True
    live_detail = ""
    if require_live and static_ok:
        command = _render_headless_command(
            argv,
            project_root=project_root,
            prompt=live_prompt,
            resolved_executable=resolved_executable,
        )
        try:
            live_probe = _run_live_probe(
                command,
                project_root=project_root,
                timeout=timeout,
                runner=live_runner,
            )
            live_ok = bool(live_probe["ok"])
            live_detail = f"returncode={live_probe['returncode']}; stdout_bytes={live_probe['stdout_bytes']}"
        except (OSError, subprocess.SubprocessError, subprocess.TimeoutExpired) as exc:
            live_probe = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
            live_ok = False
            live_detail = live_probe["error"]
    elif require_live:
        live_ok = False
        live_detail = "skipped because static readiness failed"
    ready = static_ok and live_ok
    dispatchable = (
        static_ok
        and record.get("status") == "active"
        and bool(record.get("can_receive_dispatch"))
        and HARNESS_NAME in {str(record.get("harness_name")), str(record.get("harness_type"))}
    )
    dispatchable_now = dispatchable and live_ok
    first_failed_check = ""
    if not argv:
        first_failed_check = "headless argv: missing"
    elif not executable_ok:
        first_failed_check = f"headless executable: unresolved {argv[0]}"
    elif require_live and not live_ok:
        first_failed_check = f"live claude prompt probe: {live_detail or 'failed'}"
    return {
        "can_receive_dispatch": bool(record.get("can_receive_dispatch")),
        "dispatchable": dispatchable,
        "dispatchable_now": dispatchable_now,
        "executable_ok": executable_ok,
        "first_failed_check": first_failed_check,
        "harness_id": recipient,
        "harness_name": record.get("harness_name"),
        "headless_argv": argv,
        "live_probe": live_probe,
        "ready": ready,
        "require_executable": require_executable,
        "require_live": require_live,
        "resolved_executable": resolved_executable,
        "static_ok": static_ok,
        "status": record.get("status"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipient", default=HARNESS_ID)
    parser.add_argument("--project-root", default=PROJECT_ROOT, type=Path)
    parser.add_argument("--no-require-executable", action="store_true")
    parser.add_argument("--live", action="store_true", help="Run a bounded non-mutating Claude prompt probe.")
    parser.add_argument("--prompt", default=DEFAULT_LIVE_PROMPT)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        result = evaluate_readiness(
            project_root=args.project_root.resolve(),
            recipient=args.recipient,
            require_executable=not args.no_require_executable,
            require_live=args.live,
            live_prompt=args.prompt,
            timeout=args.timeout,
        )
    except VerificationError as exc:
        payload = {"error": str(exc), "harness_id": args.recipient, "static_ok": False}
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"static_ok={result['static_ok']}")
        print(f"dispatchable={result['dispatchable']}")
        print(f"ready={result['ready']}")
        print(f"dispatchable_now={result['dispatchable_now']}")
        print(f"resolved_executable={result['resolved_executable']}")
    return 0 if result["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
