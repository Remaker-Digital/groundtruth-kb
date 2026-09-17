#!/usr/bin/env python3
"""Bounded Claude launch checks using the selected native installation record.

Passing these checks establishes neither dispatchability nor complete harness
qualification. An actual prompt launch is opt-in with --live.
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import quote

from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.config import GTConfig, GTConfigError

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

HARNESS_ID = "B"
HARNESS_NAME = "claude"
HARNESS_TYPE = "claude"
DEFAULT_LIVE_PROMPT = "Reply with READY only."
DEFAULT_TIMEOUT_SECONDS = 60.0


class VerificationError(RuntimeError):
    """Raised when Claude readiness cannot be evaluated."""


def _load_harness_record(project_root: Path, recipient: str = HARNESS_ID) -> dict[str, Any]:
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
    if not math.isfinite(timeout) or timeout <= 0:
        raise VerificationError("timeout must be finite and positive")
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
            live_probe = {"ok": False, "error": type(exc).__name__}
            live_ok = False
            live_detail = live_probe["error"]
    elif require_live:
        live_ok = False
        live_detail = "skipped because static readiness failed"
    probe_passed = static_ok and live_ok
    first_failed_check = ""
    if not argv:
        first_failed_check = "headless argv: missing"
    elif not executable_ok:
        first_failed_check = "headless executable: unresolved"
    elif require_live and not live_ok:
        first_failed_check = f"live claude prompt probe: {live_detail or 'failed'}"
    return {
        "probe_scope": "launch_prerequisites_and_bounded_prompt" if require_live else "launch_prerequisites",
        "harness_qualification": "unqualified",
        "authority_source": "native_harness_record",
        "executable_ok": executable_ok,
        "first_failed_check": first_failed_check,
        "harness_id": recipient,
        "harness_name": record.get("harness_name"),
        "live_probe": live_probe,
        "probe_passed": probe_passed,
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
        print(f"probe_passed={result['probe_passed']}")
        print(f"harness_qualification={result['harness_qualification']}")
        print(f"resolved_executable={result['resolved_executable']}")
    return 0 if result["probe_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
