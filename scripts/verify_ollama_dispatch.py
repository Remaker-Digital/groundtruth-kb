#!/usr/bin/env python3
"""Native Ollama installation, routing and optional advertised-model diagnostics.

These read-only checks do not execute a model, file a bridge item, assign a role
or establish complete harness qualification. Runtime workflows are tested through
the provider and native CLI suites; mocked exercises are not a live fallback.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import quote

from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.config import GTConfig, GTConfigError

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.ollama_harness import (  # noqa: E402
    DEFAULT_ENDPOINT,
    DEFAULT_TIMEOUT_SECONDS,
    OllamaHarnessError,
    call_ollama_tags,
    load_routing_config,
    resolve_model,
)
from scripts.windows_subprocess import no_window_subprocess_kwargs  # noqa: E402

OLLAMA_HARNESS_ID = "D"
OLLAMA_HARNESS_NAME = "ollama"
OLLAMA_DISPATCH_SKILL = "bridge-review"
OLLAMA_DISPATCH_REQUIRED_TOOLS = ("Read", "Write", "Edit", "Grep", "Glob", "Bash")
OLLAMA_SHIM_RELATIVE = Path("scripts") / "ollama_harness.py"
OLLAMA_AUTOSTART_PROBE_TIMEOUT_SECONDS = 5.0


class VerificationError(RuntimeError):
    """Raised when exact native installation/configuration cannot be read."""


def load_harness_record(project_root: Path, recipient: str = OLLAMA_HARNESS_ID) -> dict[str, Any]:
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


def _as_string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str) and item]
    return []


def evaluate_ollama_autostart(
    *,
    platform: str | None = None,
    timeout: float = OLLAMA_AUTOSTART_PROBE_TIMEOUT_SECONDS,
    executable_resolver: Callable[[str], str | None] | None = None,
    command_runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
) -> dict[str, Any]:
    """Return read-only Ollama host autostart evidence.

    Autostart posture is diagnostic only and does not establish invocation,
    qualification, role or dispatch eligibility.
    """
    active_platform = platform or sys.platform
    if not active_platform.startswith("win"):
        return {
            "checked": False,
            "configured": None,
            "platform": active_platform,
            "detail": "Ollama autostart check is Windows-specific and was skipped.",
        }

    resolver = executable_resolver or shutil.which
    powershell = resolver("powershell.exe") or resolver("powershell") or resolver("pwsh.exe") or resolver("pwsh")
    if not powershell:
        return {
            "checked": True,
            "configured": False,
            "platform": active_platform,
            "scheduled_tasks": [],
            "services": [],
            "warning": "PowerShell is unavailable for the Ollama autostart probe.",
        }

    ps_script = r"""
$ErrorActionPreference = 'SilentlyContinue'
$tasks = @(Get-ScheduledTask | Where-Object {
    $_.TaskName -match 'Ollama' -or $_.TaskPath -match 'Ollama'
} | Select-Object -ExpandProperty TaskName)
$services = @(Get-Service | Where-Object {
    $_.Name -match 'Ollama' -or $_.DisplayName -match 'Ollama'
} | Select-Object -ExpandProperty Name)
[pscustomobject]@{
    scheduled_tasks = $tasks
    services = $services
} | ConvertTo-Json -Compress
"""
    runner = command_runner or subprocess.run
    no_window_kwargs = no_window_subprocess_kwargs(force_windows=command_runner is not None)
    try:
        completed = runner(
            [
                powershell,
                "-NoLogo",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                ps_script,
            ],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            **no_window_kwargs,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "checked": True,
            "configured": False,
            "platform": active_platform,
            "scheduled_tasks": [],
            "services": [],
            "warning": f"Ollama autostart probe failed: {type(exc).__name__}",
        }

    if completed.returncode != 0:
        return {
            "checked": True,
            "configured": False,
            "platform": active_platform,
            "scheduled_tasks": [],
            "services": [],
            "warning": f"Ollama autostart probe exited {completed.returncode}",
        }

    try:
        payload = json.loads((completed.stdout or "{}").strip() or "{}")
    except json.JSONDecodeError:
        return {
            "checked": True,
            "configured": False,
            "platform": active_platform,
            "scheduled_tasks": [],
            "services": [],
            "warning": "Ollama autostart probe returned invalid JSON",
        }

    if not isinstance(payload, dict):
        return {"checked": True, "configured": False, "warning": "Ollama autostart probe returned an invalid object"}
    scheduled_tasks = _as_string_list(payload.get("scheduled_tasks"))
    services = _as_string_list(payload.get("services"))
    configured = bool(scheduled_tasks or services)
    result: dict[str, Any] = {
        "checked": True,
        "configured": configured,
        "platform": active_platform,
        "scheduled_tasks": scheduled_tasks,
        "services": services,
    }
    if not configured:
        result["warning"] = "No Windows scheduled task or service matching Ollama was detected."
    return result


def _model_advertised(model_id: str, advertised_model_ids: set[str]) -> bool:
    # Ollama's API model-name contract uses :latest only when a tag is omitted.
    # An arbitrary tag with the same model prefix is not the requested model.
    def name(value):
        return value if ":" in value.rsplit("/", 1)[-1] else value + ":latest"

    return any(name(candidate) == name(model_id) for candidate in advertised_model_ids)


def evaluate_readiness(
    project_root: Path,
    *,
    endpoint: str = DEFAULT_ENDPOINT,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    recipient: str = OLLAMA_HARNESS_ID,
    require_daemon: bool = True,
) -> dict[str, Any]:
    if not math.isfinite(timeout) or timeout <= 0:
        raise VerificationError("timeout must be finite and positive")
    project_root = project_root.resolve()
    record = load_harness_record(project_root, recipient)
    checks, warnings = [], []
    result = {
        "probe_passed": False,
        "probe_scope": "installation_routing_and_advertised_model" if require_daemon else "installation_and_routing",
        "authority_source": "native_harness_record",
        "harness_qualification": "unqualified",
        "model_execution": "unqualified",
        "recipient": recipient,
        "checks": checks,
        "warnings": warnings,
    }
    argv = _headless_argv(record)
    if record.get("harness_type") != OLLAMA_HARNESS_NAME or not argv:
        checks.append(
            {"name": "native headless argv", "passed": False, "detail": "Invalid Ollama installation or argument list"}
        )
        return result
    shim = (project_root / OLLAMA_SHIM_RELATIVE).resolve()
    command = [p.replace("{{PROJECT_ROOT}}", str(project_root)) for p in argv]
    invokes_shim = any(
        (Path(p) if Path(p).is_absolute() else project_root / p).resolve() == shim
        for p in command
        if p.endswith("ollama_harness.py")
    )
    skill_positions = [i for i, p in enumerate(command) if p == "--skill"]
    skill_ok = (
        len(skill_positions) == 1
        and skill_positions[0] + 1 < len(command)
        and command[skill_positions[0] + 1] == OLLAMA_DISPATCH_SKILL
    )
    checks.append(
        {
            "name": "native headless argv",
            "passed": invokes_shim and skill_ok,
            "detail": "Exact selected-root shim and bridge-review skill",
        }
    )
    checks.append({"name": "shim present", "passed": shim.is_file(), "detail": OLLAMA_SHIM_RELATIVE.as_posix()})
    if not all(c["passed"] for c in checks):
        return result
    try:
        route = resolve_model(load_routing_config(project_root), None, skill=OLLAMA_DISPATCH_SKILL)
    except OllamaHarnessError:
        checks.append(
            {"name": "routing skill route", "passed": False, "detail": "Invalid or unavailable selected-root routing"}
        )
        return result
    missing = sorted(set(OLLAMA_DISPATCH_REQUIRED_TOOLS) - set(route.allowed_tools))
    route_ok = route.tool_calling_supported is True and not missing
    checks.append({"name": "routing skill route", "passed": route_ok, "detail": f"missing_tools={missing}"})
    result.update(model_id=route.model_id, route_key=route.key, required_tools=list(OLLAMA_DISPATCH_REQUIRED_TOOLS))
    if not route_ok:
        return result
    autostart = evaluate_ollama_autostart(timeout=min(timeout, OLLAMA_AUTOSTART_PROBE_TIMEOUT_SECONDS))
    result["autostart"] = autostart
    if autostart.get("checked") and autostart.get("warning"):
        warnings.append({"name": "ollama autostart", "detail": autostart["warning"]})
    if require_daemon:
        try:
            advertised = call_ollama_tags(endpoint, timeout)
        except OllamaHarnessError:
            checks.append({"name": "ollama /api/tags", "passed": False, "detail": "Advertised-model request failed"})
            return result
        checks.append(
            {
                "name": "ollama /api/tags",
                "passed": _model_advertised(route.model_id, set(advertised)),
                "detail": "Requested model name, including its tag",
            }
        )
    result["probe_passed"] = all(c["passed"] for c in checks)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=_PROJECT_ROOT)
    parser.add_argument("--recipient", default=OLLAMA_HARNESS_ID)
    parser.add_argument("--endpoint", default=os.environ.get("OLLAMA_ENDPOINT", DEFAULT_ENDPOINT))
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument(
        "--skip-daemon",
        action="store_true",
        help="Omit the advertised-model HTTP check; no execution qualification follows.",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = evaluate_readiness(
            args.project_root,
            endpoint=args.endpoint,
            timeout=args.timeout,
            recipient=args.recipient,
            require_daemon=not args.skip_daemon,
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
        for check in result["checks"]:
            print(f"{check['name']}: passed={check['passed']}; {check['detail']}")
        for warning in result["warnings"]:
            print(f"Warning: {warning['detail']}")
        print("harness_qualification=unqualified; model_execution=unqualified")
    return 0 if result["probe_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
