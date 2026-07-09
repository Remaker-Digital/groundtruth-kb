#!/usr/bin/env python3
"""Deterministic Codex dispatch readiness probe."""

from __future__ import annotations

import argparse
import datetime as dt
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
from scripts.windows_subprocess import no_window_subprocess_kwargs  # noqa: E402

HARNESS_ID = "A"
HARNESS_NAME = "codex"
HARNESS_TYPE = "codex"
REQUIRED_MODEL = "gpt-5.5"
REQUIRED_APPROVAL_CONFIG = 'approval_policy="never"'
REQUIRED_REASONING_CONFIG = 'model_reasoning_effort="xhigh"'
REQUIRED_SANDBOX_MODE = "workspace-write"
FORBIDDEN_SANDBOX_MODES = {"danger-full-access"}
FORBIDDEN_FLAGS = {"--dangerously-bypass-approvals-and-sandbox"}
CODEX_NO_WINDOW_VERIFICATION_RELATIVE_PATH = (
    ".gtkb-state",
    "bridge-poller",
    "codex-no-window-verification.json",
)
CODEX_NO_WINDOW_VERIFICATION_MAX_AGE_SECONDS = 4 * 60 * 60
CODEX_WINDOWS_SANDBOX_SETUP_STATUS = "0xc0000142"


class VerificationError(RuntimeError):
    """Raised when Codex readiness cannot be evaluated."""


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


def _flag_value(argv: list[str], flag: str) -> str | None:
    values = _flag_values(argv, flag)
    return values[0] if values else None


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


def _has_flag_value(argv: list[str], flag: str, expected: str) -> bool:
    return _flag_value(argv, flag) == expected


def _has_config(argv: list[str], expected: str) -> bool:
    return expected in argv


def _is_codex_helper_add_dir(value: str, project_root: Path) -> bool:
    normalized = value.replace("\\", "/").rstrip("/")
    if normalized == "{{PROJECT_ROOT}}/.codex":
        return True
    path = Path(value)
    candidate = path if path.is_absolute() else project_root / path
    try:
        return candidate.resolve() == (project_root / ".codex").resolve()
    except OSError:
        return False


def _normalize_acl_check(payload: dict[str, Any], *, returncode: int | None = None) -> dict[str, Any]:
    effective_returncode = payload.get("returncode", returncode)
    needs_repair = bool(payload.get("needs_repair"))
    errors = payload.get("errors")
    errors_count = len(errors) if isinstance(errors, list) else int(payload.get("errors_count") or 0)
    ok = bool(payload.get("ok", (effective_returncode in {None, 0}) and not needs_repair and errors_count == 0))
    return {
        "ok": ok,
        "returncode": effective_returncode,
        "needs_repair": needs_repair,
        "risky_deny_count": int(payload.get("risky_deny_count") or 0),
        "errors_count": errors_count,
        "checked_count": int(payload.get("checked_count") or 0),
        "sandbox_group": payload.get("sandbox_group"),
        "current_identity": payload.get("current_identity"),
        "skipped": bool(payload.get("skipped", False)),
        "error": payload.get("error"),
    }


def _check_codex_dotdir_acl(project_root: Path, *, repair: bool = False) -> dict[str, Any]:
    if sys.platform != "win32":
        return _normalize_acl_check({"ok": True, "skipped": True, "error": "non-windows"})

    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if powershell is None:
        return _normalize_acl_check({"ok": False, "error": "PowerShell not found"}, returncode=None)

    script_path = PROJECT_ROOT / "scripts" / "repair_codex_dotdir_acl.ps1"
    shell_args = ["-NoProfile"]
    if Path(powershell).name.lower() == "powershell.exe":
        shell_args.extend(["-ExecutionPolicy", "Bypass"])

    def _run(mode: str) -> dict[str, Any]:
        command = [
            powershell,
            *shell_args,
            "-File",
            str(script_path),
            "-ProjectRoot",
            str(project_root),
            "-Mode",
            mode,
            "-Json",
        ]
        try:
            completed = subprocess.run(
                command,
                text=True,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
                check=False,
                # WI-5071: the .codex ACL repair powershell runner must stay
                # headless; every peer dispatch verifier applies the no-window
                # disposition.
                **no_window_subprocess_kwargs(),
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return _normalize_acl_check({"ok": False, "error": str(exc)}, returncode=None)

        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            return _normalize_acl_check(
                {"ok": False, "error": f"ACL check emitted invalid JSON: {exc}"},
                returncode=completed.returncode,
            )
        return _normalize_acl_check(payload, returncode=completed.returncode)

    result = _run("Check")
    # WI-5065 opt-in idempotent pre-attestation auto-repair: when the caller
    # requests repair and the read-only Check found removable risky-Deny ACEs
    # (with no read error), escalate to Apply and re-Check so a foreign-SID deny
    # that reappeared before the .driveignore exclusion settled is stripped just
    # in time. The default path stays read-only.
    if repair and result.get("needs_repair") and not result.get("error"):
        _run("Apply")
        result = _run("Check")
    return result


def _parse_utc_timestamp(value: object) -> dt.datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.astimezone(dt.UTC) if parsed.tzinfo else parsed.replace(tzinfo=dt.UTC)


def _codex_no_window_verification_path(project_root: Path) -> Path:
    return project_root.joinpath(*CODEX_NO_WINDOW_VERIFICATION_RELATIVE_PATH)


def _load_codex_no_window_verification(project_root: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(_codex_no_window_verification_path(project_root).read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


def _verification_text(payload: dict[str, Any] | None) -> str:
    if not isinstance(payload, dict):
        return ""
    fields = ("stderr_preview", "stdout_preview", "error", "message", "status_exit_code")
    return "\n".join(str(payload.get(field) or "") for field in fields)


def _codex_live_failure_class(payload: dict[str, Any] | None, reason: str) -> str:
    text = _verification_text(payload).lower()
    if CODEX_WINDOWS_SANDBOX_SETUP_STATUS in text:
        return "codex_windows_sandbox_setup_failed_0xc0000142"
    if reason == "codex_no_window_probe_detected_visible_window":
        return "codex_no_window_visible_window_detected"
    if reason in {
        "missing_codex_no_window_verification",
        "codex_no_window_verification_expired",
        "codex_no_window_verification_missing_timestamp",
        "codex_no_window_verification_stale",
    }:
        return reason
    return "codex_no_window_probe_not_passing" if reason == "codex_no_window_probe_not_passing" else reason


def evaluate_live_headless_readiness(project_root: Path) -> dict[str, Any]:
    payload = _load_codex_no_window_verification(project_root)
    path = _codex_no_window_verification_path(project_root)
    if payload is None:
        reason = "missing_codex_no_window_verification"
        return {
            "ready": False,
            "reason": reason,
            "failure_class": _codex_live_failure_class(None, reason),
            "verification_path": path.as_posix(),
        }
    if payload.get("visible_window_detected") is not False:
        reason = "codex_no_window_probe_detected_visible_window"
        return {
            "ready": False,
            "reason": reason,
            "failure_class": _codex_live_failure_class(payload, reason),
            "verification": payload,
            "verification_path": path.as_posix(),
            "visible_window_detected": payload.get("visible_window_detected"),
        }
    result = str(payload.get("result") or "").strip().lower()
    if result not in {"pass", "passed", "clean"}:
        reason = "codex_no_window_probe_not_passing"
        return {
            "ready": False,
            "reason": reason,
            "failure_class": _codex_live_failure_class(payload, reason),
            "verification": payload,
            "verification_path": path.as_posix(),
            "visible_window_detected": payload.get("visible_window_detected"),
        }
    now = dt.datetime.now(dt.UTC)
    expires_at = _parse_utc_timestamp(payload.get("expires_at"))
    if expires_at is not None:
        if expires_at <= now:
            reason = "codex_no_window_verification_expired"
            return {
                "ready": False,
                "reason": reason,
                "failure_class": _codex_live_failure_class(payload, reason),
                "verification": payload,
                "verification_path": path.as_posix(),
            }
        return {
            "ready": True,
            "reason": "codex_no_window_verification_current",
            "verification": payload,
            "verification_path": path.as_posix(),
            "visible_window_detected": payload.get("visible_window_detected"),
        }
    verified_at = _parse_utc_timestamp(payload.get("verified_at"))
    if verified_at is None:
        reason = "codex_no_window_verification_missing_timestamp"
        return {
            "ready": False,
            "reason": reason,
            "failure_class": _codex_live_failure_class(payload, reason),
            "verification": payload,
            "verification_path": path.as_posix(),
        }
    age_seconds = (now - verified_at).total_seconds()
    if age_seconds > CODEX_NO_WINDOW_VERIFICATION_MAX_AGE_SECONDS:
        reason = "codex_no_window_verification_stale"
        return {
            "ready": False,
            "reason": reason,
            "failure_class": _codex_live_failure_class(payload, reason),
            "verification": payload,
            "verification_path": path.as_posix(),
        }
    return {
        "ready": True,
        "reason": "codex_no_window_verification_current",
        "verification": payload,
        "verification_path": path.as_posix(),
        "visible_window_detected": payload.get("visible_window_detected"),
    }


def evaluate_readiness(
    *,
    project_root: Path,
    recipient: str = HARNESS_ID,
    require_executable: bool = True,
    executable_resolver: Callable[[str], str | None] | None = None,
    acl_checker: Callable[[Path], dict[str, Any]] | None = None,
    repair_acl: bool = False,
) -> dict[str, Any]:
    record = _load_harness_record(project_root, recipient)
    if record.get("harness_type") != HARNESS_TYPE:
        raise VerificationError(f"recipient {recipient} is not {HARNESS_TYPE}: {record.get('harness_type')!r}")

    argv = _headless_argv(record)
    resolver = executable_resolver or shutil.which
    resolved_executable = resolver(argv[0]) if argv else None
    executable_ok = bool(resolved_executable) if require_executable else True
    model_ok = _has_flag_value(argv, "--model", REQUIRED_MODEL)
    approval_policy_ok = _has_config(argv, REQUIRED_APPROVAL_CONFIG)
    reasoning_effort_ok = _has_config(argv, REQUIRED_REASONING_CONFIG)
    sandbox_mode = _flag_value(argv, "--sandbox")
    sandbox_forbidden = sandbox_mode in FORBIDDEN_SANDBOX_MODES
    sandbox_ok = sandbox_mode == REQUIRED_SANDBOX_MODE and not sandbox_forbidden
    project_root_selector = _flag_value(argv, "--cd")
    project_root_selector_ok = project_root_selector in {"{{PROJECT_ROOT}}", str(project_root)}
    add_dir_values = _flag_values(argv, "--add-dir")
    codex_helper_add_dir = next(
        (value for value in add_dir_values if _is_codex_helper_add_dir(value, project_root)),
        None,
    )
    codex_helper_add_dir_ok = codex_helper_add_dir is not None
    forbidden_flags_present = sorted(flag for flag in FORBIDDEN_FLAGS if flag in argv)
    try:
        if acl_checker is not None:
            acl_check = acl_checker(project_root)
        else:
            acl_check = _check_codex_dotdir_acl(project_root, repair=repair_acl)
    except Exception as exc:  # pragma: no cover - defensive fail-closed guard
        acl_check = {"ok": False, "error": str(exc)}
    codex_dotdir_acl = _normalize_acl_check(acl_check)
    codex_dotdir_acl_ok = bool(codex_dotdir_acl["ok"])
    static_ok = (
        bool(argv)
        and executable_ok
        and model_ok
        and approval_policy_ok
        and reasoning_effort_ok
        and sandbox_ok
        and project_root_selector_ok
        and codex_helper_add_dir_ok
        and codex_dotdir_acl_ok
        and not forbidden_flags_present
    )
    dispatchable = (
        static_ok
        and record.get("status") == "active"
        and bool(record.get("can_receive_dispatch"))
        and HARNESS_NAME in {str(record.get("harness_name")), str(record.get("harness_type"))}
    )
    live_headless = evaluate_live_headless_readiness(project_root)
    return {
        "can_receive_dispatch": bool(record.get("can_receive_dispatch")),
        "codex_dotdir_acl": codex_dotdir_acl,
        "codex_dotdir_acl_ok": codex_dotdir_acl_ok,
        "codex_helper_add_dir": codex_helper_add_dir,
        "codex_helper_add_dir_ok": codex_helper_add_dir_ok,
        "dispatchable": dispatchable,
        "live_headless_failure_class": live_headless.get("failure_class"),
        "live_headless_ready": live_headless.get("ready"),
        "live_headless_reason": live_headless.get("reason"),
        "live_headless_verification": live_headless.get("verification"),
        "live_headless_verification_path": live_headless.get("verification_path"),
        "approval_policy_ok": approval_policy_ok,
        "executable_ok": executable_ok,
        "forbidden_flags_present": forbidden_flags_present,
        "harness_id": recipient,
        "harness_name": record.get("harness_name"),
        "headless_argv": argv,
        "model_ok": model_ok,
        "project_root_selector": project_root_selector,
        "project_root_selector_ok": project_root_selector_ok,
        "require_executable": require_executable,
        "reasoning_effort_ok": reasoning_effort_ok,
        "resolved_executable": resolved_executable,
        "required_model": REQUIRED_MODEL,
        "required_sandbox_mode": REQUIRED_SANDBOX_MODE,
        "sandbox_forbidden": sandbox_forbidden,
        "sandbox_mode": sandbox_mode,
        "sandbox_ok": sandbox_ok,
        "static_dispatchable": dispatchable,
        "static_ok": static_ok,
        "status": record.get("status"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipient", default=HARNESS_ID)
    parser.add_argument("--project-root", default=PROJECT_ROOT, type=Path)
    parser.add_argument("--no-require-executable", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--repair-acl",
        action="store_true",
        help="Escalate a .codex ACL Check to Apply (idempotent auto-repair) when risky-Deny ACEs are found (WI-5065).",
    )
    args = parser.parse_args(argv)

    try:
        result = evaluate_readiness(
            project_root=args.project_root.resolve(),
            recipient=args.recipient,
            require_executable=not args.no_require_executable,
            repair_acl=args.repair_acl,
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
        print(f"resolved_executable={result['resolved_executable']}")
    return 0 if result["static_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
