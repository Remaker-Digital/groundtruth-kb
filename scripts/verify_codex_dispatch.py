#!/usr/bin/env python3
"""Bounded Codex launch and ACL checks from a native installation record.

The optional prompt probe reports its observed process result. Neither cached
files nor these diagnostics establish dispatchability, model/profile conformance,
permissions behavior, window behavior or complete harness qualification.
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

from scripts.windows_subprocess import no_window_subprocess_kwargs  # noqa: E402

HARNESS_ID = "A"
HARNESS_TYPE = "codex"
DEFAULT_LIVE_PROMPT = "Reply with READY only."
DEFAULT_TIMEOUT_SECONDS = 60.0
FORBIDDEN_FLAGS = {"--dangerously-bypass-approvals-and-sandbox"}


class VerificationError(RuntimeError):
    """Raised when the selected native installation cannot be inspected."""


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


def _flag_values(argv: list[str], flag: str) -> list[str]:
    values: list[str] = []
    prefix = f"{flag}="
    for index, part in enumerate(argv):
        if part == flag:
            if index + 1 < len(argv):
                values.append(argv[index + 1])
        if part.startswith(prefix):
            values.append(part[len(prefix) :])
    return values


def _normalize_acl_check(payload: object, *, returncode: int | None = None) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {"ok": False, "error": "invalid_acl_report", "skipped": False}
    effective_returncode = payload.get("returncode", returncode)
    errors = payload.get("errors")
    errors_count = len(errors) if isinstance(errors, list) else payload.get("errors_count", 0)
    counts = {
        "errors_count": errors_count,
        "risky_deny_count": payload.get("risky_deny_count", 0),
        "checked_count": payload.get("checked_count", 0),
    }
    skipped = payload.get("skipped") is True
    valid = (
        all(type(value) is int and value >= 0 for value in counts.values())
        and (skipped or (counts["checked_count"] > 0 and "needs_repair" in payload))
        and (skipped or isinstance(errors, list) or "errors_count" in payload)
    )
    needs_repair = payload.get("needs_repair", False)
    ok = (
        valid
        and type(needs_repair) is bool
        and not needs_repair
        and payload.get("ok", True) is True
        and not payload.get("error")
        and (effective_returncode is None or type(effective_returncode) is int and effective_returncode == 0)
        and counts["errors_count"] == 0
        and counts["risky_deny_count"] == 0
    )
    return {
        "ok": ok,
        "returncode": effective_returncode,
        "needs_repair": needs_repair,
        **counts,
        "skipped": payload.get("skipped") is True,
        "error": "acl_check_failed" if payload.get("error") else None,
    }


def _check_codex_dotdir_acl(project_root: Path) -> dict[str, Any]:
    """Inspect the exact root with the existing operator script's Check mode."""
    if sys.platform != "win32":
        return {"ok": True, "skipped": True, "reason": "windows_acl_not_applicable"}
    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if powershell is None:
        return {"ok": False, "error": "powershell_unavailable"}
    command = [
        powershell,
        "-NoProfile",
        "-NonInteractive",
        "-File",
        str(PROJECT_ROOT / "scripts/repair_codex_dotdir_acl.ps1"),
        "-ProjectRoot",
        str(project_root),
        "-Mode",
        "Check",
        "-Json",
    ]
    try:
        completed = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
            **no_window_subprocess_kwargs(),
        )
        payload = json.loads(completed.stdout)
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        return {"ok": False, "error": type(exc).__name__}
    return _normalize_acl_check(payload, returncode=completed.returncode)


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
        **no_window_subprocess_kwargs(),
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
    acl_checker: Callable[[Path], dict[str, Any]] | None = None,
    require_live: bool = False,
    live_prompt: str = DEFAULT_LIVE_PROMPT,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    live_runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
) -> dict[str, Any]:
    if not math.isfinite(timeout) or timeout <= 0:
        raise VerificationError("timeout must be finite and positive")
    project_root = project_root.resolve()
    record = _load_harness_record(project_root, recipient)
    if record.get("harness_type") != HARNESS_TYPE:
        raise VerificationError("selected installation is not codex")
    argv = _headless_argv(record)
    resolver = executable_resolver or shutil.which
    resolved_executable = resolver(argv[0]) if argv else None
    executable_ok = bool(resolved_executable) if require_executable else True
    roots = _flag_values(argv, "--cd")
    # Without an explicit --cd, the prompt runner's cwd is the selected root.
    root_ok = not roots and "--cd" not in argv or roots in [["{{PROJECT_ROOT}}"], [str(project_root)]]
    flags_ok = not any(flag in argv for flag in FORBIDDEN_FLAGS)
    checks = [
        {"name": "native headless argv", "passed": bool(argv)},
        {"name": "executable", "passed": executable_ok},
        {"name": "selected project root", "passed": root_ok},
        {"name": "no broad bypass flag", "passed": flags_ok},
    ]
    launch_ok = all(c["passed"] for c in checks)
    acl = None
    if launch_ok:
        try:
            acl = _normalize_acl_check((acl_checker or _check_codex_dotdir_acl)(project_root))
        except Exception as exc:  # noqa: BLE001 - diagnostics retain a private typed failure
            acl = {"ok": False, "error": type(exc).__name__}
    checks.append({"name": "Codex ACL inspection", "passed": acl is not None and acl.get("ok") is True})
    live = None
    if require_live:
        if all(c["passed"] for c in checks):
            command = _render_headless_command(
                argv, project_root=project_root, prompt=live_prompt, resolved_executable=resolved_executable
            )
            try:
                live = _run_live_probe(command, project_root=project_root, timeout=timeout, runner=live_runner)
            except (OSError, subprocess.SubprocessError) as exc:
                live = {"ok": False, "error": type(exc).__name__}
        checks.append({"name": "bounded Codex prompt", "passed": live is not None and live.get("ok") is True})
    return {
        "probe_passed": all(c["passed"] for c in checks),
        "probe_scope": "launch_prerequisites_acl_and_bounded_prompt"
        if require_live
        else "launch_prerequisites_and_acl",
        "authority_source": "native_harness_record",
        "harness_qualification": "unqualified",
        "model_profile_conformance": "unqualified",
        "permissions_behavior": "unqualified",
        "window_behavior": "unqualified",
        "harness_id": recipient,
        "status": record.get("status"),
        "checks": checks,
        "first_failed_check": next((c["name"] for c in checks if not c["passed"]), ""),
        "acl_probe": acl,
        "live_probe": live,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipient", default=HARNESS_ID)
    parser.add_argument("--project-root", default=PROJECT_ROOT, type=Path)
    parser.add_argument("--no-require-executable", action="store_true")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--prompt", default=DEFAULT_LIVE_PROMPT)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = evaluate_readiness(
            project_root=args.project_root,
            recipient=args.recipient,
            require_executable=not args.no_require_executable,
            require_live=args.live,
            live_prompt=args.prompt,
            timeout=args.timeout,
        )
    except VerificationError as exc:
        if args.json:
            print(json.dumps({"error": str(exc), "harness_id": args.recipient, "probe_passed": False}))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"probe_passed={result['probe_passed']}")
        print(f"first_failed_check={result['first_failed_check']}")
        print("harness_qualification=unqualified")
    return 0 if result["probe_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
