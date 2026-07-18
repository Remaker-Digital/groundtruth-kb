#!/usr/bin/env python3
"""Verify headless Antigravity dispatch substrate without role/topology mutation."""

from __future__ import annotations

import argparse
import datetime as dt
import importlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import uuid
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_EVIDENCE_ROOT = PROJECT_ROOT / ".gtkb-state" / "antigravity-onboarding" / "dispatch-verification"
DEFAULT_LIVE_PROMPT = "Reply READY only."
DEFAULT_TIMEOUT_SECONDS = 60.0
DISPATCH_ROLES = frozenset({"loyal-opposition", "prime-builder"})
CREDENTIAL_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*([A-Za-z0-9._~+/=-]{8,})"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
)
AGY_EXECUTABLE_NAMES = ("agy", "agy.exe", "agy.cmd", "agy.ps1")
AGY_RESPONSE_STEP_TYPE = 15
AGY_RECOVERY_LOOKBACK_SECONDS = 10.0
PRINTABLE_BYTES_RE = re.compile(rb"[ -~]{4,}")
VERDICT_ANCHOR_HELPER_PATHS = (
    ".codex/skills/verify/helpers/write_verdict.py",
    ".claude/skills/verify/helpers/write_verdict.py",
)
VERDICT_ANCHOR_VALIDATOR_PATH = "scripts/verdict_evidence_anchor_preflight.py"
VERDICT_ANCHOR_GUARD_TOKENS = ("validate_verdict_evidence_anchors", "_assert_verdict_evidence_anchors")


class VerificationError(RuntimeError):
    """Raised when the dispatch substrate cannot be verified."""


def _module_source_path(module: ModuleType) -> Path | None:
    raw_path = getattr(module, "__file__", None)
    if not isinstance(raw_path, str) or not raw_path.strip():
        return None
    try:
        return Path(raw_path).resolve()
    except OSError:
        return None


def resolve_loaded_project_module(
    *,
    project_root: Path,
    expected_source_path: Path,
    import_name: str,
    required_attributes: tuple[str, ...],
) -> ModuleType:
    """Reuse one exact loaded project module or import its canonical package name."""

    try:
        canonical_root = project_root.resolve(strict=True)
        expected_source = expected_source_path.resolve(strict=True)
        expected_source.relative_to(canonical_root)
    except (OSError, ValueError) as exc:
        raise VerificationError(
            f"expected project module source is missing or outside the project root: {expected_source_path}"
        ) from exc

    matches: dict[int, tuple[ModuleType, list[str]]] = {}
    for module_name, candidate in tuple(sys.modules.items()):
        if not isinstance(candidate, ModuleType) or _module_source_path(candidate) != expected_source:
            continue
        entry = matches.setdefault(id(candidate), (candidate, []))
        entry[1].append(module_name)

    if len(matches) > 1:
        names = sorted(name for _, module_names in matches.values() for name in module_names)
        raise VerificationError(f"multiple loaded module objects resolve to {expected_source}: {', '.join(names)}")

    if matches:
        module = next(iter(matches.values()))[0]
    else:
        module = importlib.import_module(import_name)
        resolved_source = _module_source_path(module)
        if resolved_source != expected_source:
            raise VerificationError(f"import {import_name!r} resolved to {resolved_source}, expected {expected_source}")

    missing = [name for name in required_attributes if not hasattr(module, name)]
    if missing:
        raise VerificationError(
            f"project module {expected_source} is missing required attributes: {', '.join(missing)}"
        )
    return module


_dispatcher_runtime = resolve_loaded_project_module(
    project_root=PROJECT_ROOT,
    expected_source_path=PROJECT_ROOT / "scripts" / "dispatcher_runtime.py",
    import_name="scripts.dispatcher_runtime",
    required_attributes=("DispatchTarget", "_harness_command"),
)
DispatchTarget = _dispatcher_runtime.DispatchTarget
_harness_command = _dispatcher_runtime._harness_command

_harness_projection_reader = resolve_loaded_project_module(
    project_root=PROJECT_ROOT,
    expected_source_path=PROJECT_ROOT / "scripts" / "harness_projection_reader.py",
    import_name="scripts.harness_projection_reader",
    required_attributes=("load_harness_projection",),
)
load_harness_projection = _harness_projection_reader.load_harness_projection


def sanitize_capture(text: str) -> str:
    """Redact credential-shaped values from captured process output."""

    sanitized = text
    for pattern in CREDENTIAL_PATTERNS:
        sanitized = pattern.sub(
            lambda match: match.group(0).replace(match.group(2), "[REDACTED]") if match.groups() else "[REDACTED]",
            sanitized,
        )
    return sanitized


def load_harness_record(project_root: Path, recipient: str) -> dict[str, Any]:
    """Load one harness record from the generated registry projection."""

    registry = load_harness_projection(project_root)
    for record in registry.get("harnesses", []):
        if isinstance(record, dict) and str(record.get("id")) == recipient:
            return record
    raise VerificationError(f"recipient harness not found in registry: {recipient}")


def build_dispatch_command(project_root: Path, recipient: str, prompt: str) -> list[str]:
    """Render the registry-projected headless argv for a recipient harness."""

    record = load_harness_record(project_root, recipient)
    if record.get("harness_type") != "antigravity":
        raise VerificationError(f"recipient {recipient} is not antigravity: {record.get('harness_type')!r}")
    if record.get("status") not in {"registered", "active"}:
        raise VerificationError(f"recipient {recipient} has unsupported status: {record.get('status')!r}")
    surfaces = record.get("invocation_surfaces")
    target = DispatchTarget(
        needed_role_label="loyal-opposition",
        harness_id=recipient,
        command_handle=str(record.get("harness_name") or record.get("harness_type")),
        canonical_mode="lo",
        invocation_surfaces=surfaces if isinstance(surfaces, dict) else None,
    )
    command = _harness_command(target, prompt, project_root)
    if command is None:
        raise VerificationError(f"recipient {recipient} has no valid headless argv template")
    return command


def _resolve_executable_for_host(command: list[str]) -> list[str]:
    """Return ``command`` with element 0 resolved for the current host.

    ``shutil.which`` remains the first lookup so ambient PATH wins. On Windows,
    the official Antigravity installer places ``agy.exe`` under
    ``%LOCALAPPDATA%\agy\bin`` and the current long-lived process may not inherit
    the updated user PATH, so this helper also checks that installer-owned path
    for ``agy`` only. The registry-projected canonical argv is preserved in the
    evidence payload; only the OS-launch boundary uses the resolved form.
    """

    if not command:
        return command
    resolved = shutil.which(command[0])
    if resolved:
        return [resolved] + list(command[1:])
    if os.name == "nt" and Path(command[0]).name.lower() in AGY_EXECUTABLE_NAMES:
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            candidate = Path(local_app_data) / "agy" / "bin" / "agy.exe"
            if candidate.is_file():
                return [str(candidate)] + list(command[1:])
    return command


def _timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _hidden_process_kwargs() -> dict[str, int]:
    if sys.platform.startswith("win"):
        return {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)}
    return {}


def _role_tokens(record: dict[str, Any]) -> set[str]:
    raw = record.get("role")
    if isinstance(raw, str):
        return {raw}
    if isinstance(raw, list):
        return {item for item in raw if isinstance(item, str)}
    return set()


def inspect_verdict_anchor_guard(project_root: Path) -> dict[str, Any]:
    """Return audit evidence that hook-less verdict paths have helper guard coverage."""

    validator = project_root / VERDICT_ANCHOR_VALIDATOR_PATH
    helpers: list[dict[str, Any]] = []
    for rel_path in VERDICT_ANCHOR_HELPER_PATHS:
        helper = project_root / rel_path
        try:
            text = helper.read_text(encoding="utf-8")
        except OSError as exc:
            helpers.append(
                {
                    "path": rel_path,
                    "exists": helper.is_file(),
                    "guarded": False,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
            continue
        missing_tokens = [token for token in VERDICT_ANCHOR_GUARD_TOKENS if token not in text]
        helpers.append(
            {
                "path": rel_path,
                "exists": True,
                "guarded": not missing_tokens,
                "missing_tokens": missing_tokens,
            }
        )
    guarded_helpers = [helper["path"] for helper in helpers if helper.get("guarded")]
    return {
        "ok": validator.is_file() and bool(guarded_helpers),
        "validator": {"path": VERDICT_ANCHOR_VALIDATOR_PATH, "exists": validator.is_file()},
        "helpers": helpers,
        "guarded_helpers": guarded_helpers,
        "required_tokens": list(VERDICT_ANCHOR_GUARD_TOKENS),
    }


def _first_failed_detail(checks: list[dict[str, Any]]) -> str:
    for check in checks:
        if not check.get("passed"):
            return f"{check.get('name')}: {check.get('detail') or 'failed'}"
    return ""


def _command_head_name(command: list[str]) -> str:
    if not command:
        return ""
    return Path(command[0]).name.lower()


def _is_agy_command(command: list[str]) -> bool:
    return _command_head_name(command) in AGY_EXECUTABLE_NAMES


def _is_legacy_gemini_command(command: list[str]) -> bool:
    return "gemini" in _command_head_name(command)


def _antigravity_conversations_dir() -> Path:
    return Path.home() / ".gemini" / "antigravity-cli" / "conversations"


def _sentinel_live_prompt(prompt: str, sentinel: str) -> str:
    base = prompt.strip()
    if not base or base == DEFAULT_LIVE_PROMPT:
        return f"Reply with exactly: READY {sentinel}"
    return f"{base}\n\nFor this readiness probe, include this exact final line: READY {sentinel}"


def _printable_blob_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return "\n".join(match.decode("utf-8", errors="ignore") for match in PRINTABLE_BYTES_RE.findall(value))
    return str(value)


def _recover_agy_print_response(
    *,
    sentinel: str,
    started_at: float,
    conversations_dir: Path | None = None,
) -> dict[str, Any] | None:
    """Recover agy print-mode output from Antigravity's local response store.

    Current Windows agy builds can complete successfully while writing no
    stdout, even though the model response is persisted in the conversation DB.
    This recovery path is intentionally narrow: it only accepts recent bot
    response steps containing the run-unique sentinel.
    """

    root = conversations_dir or _antigravity_conversations_dir()
    if not root.is_dir():
        return None
    threshold = started_at - AGY_RECOVERY_LOOKBACK_SECONDS
    try:
        db_paths = sorted(
            (path for path in root.glob("*.db") if path.stat().st_mtime >= threshold),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
    except OSError:
        return None
    checked = 0
    for db_path in db_paths:
        checked += 1
        try:
            uri = db_path.resolve().as_uri() + "?mode=ro"
            with sqlite3.connect(uri, uri=True, timeout=1.0) as connection:
                rows = connection.execute(
                    """
                    SELECT idx, step_type, metadata, error_details, task_details, render_info, step_payload
                    FROM steps
                    ORDER BY idx DESC
                    LIMIT 80
                    """
                ).fetchall()
        except (OSError, sqlite3.DatabaseError):
            continue
        for idx, step_type, *blobs in rows:
            if step_type != AGY_RESPONSE_STEP_TYPE:
                continue
            text = sanitize_capture("\n".join(part for value in blobs if (part := _printable_blob_text(value))))
            if sentinel in text and "READY" in text:
                return {
                    "checked_databases": checked,
                    "source": str(db_path),
                    "step_idx": idx,
                    "stdout": f"READY {sentinel}\n",
                }
    return None


def _run_live_probe(
    command: list[str],
    *,
    project_root: Path,
    sentinel: str | None,
    timeout: float,
    runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
) -> dict[str, Any]:
    started_at = time.time()
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
    stdout = sanitize_capture(completed.stdout or "")
    stderr = sanitize_capture(completed.stderr or "")
    recovery = None
    if completed.returncode == 0 and not stdout.strip() and sentinel:
        recovery = _recover_agy_print_response(sentinel=sentinel, started_at=started_at)
        if recovery:
            stdout = recovery["stdout"]
    return {
        "command": command,
        "ok": completed.returncode == 0 and bool(stdout.strip()),
        "output_recovered": bool(recovery),
        "recovery": recovery,
        "returncode": completed.returncode,
        "stderr_bytes": len(stderr.encode("utf-8")),
        "stdout_bytes": len(stdout.encode("utf-8")),
    }


def evaluate_readiness(
    *,
    project_root: Path,
    recipient: str,
    require_live: bool = False,
    live_prompt: str = DEFAULT_LIVE_PROMPT,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    live_runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
) -> dict[str, Any]:
    """Return fail-closed Antigravity dispatch readiness evidence."""

    checks: list[dict[str, Any]] = []

    def add_check(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})

    record = load_harness_record(project_root, recipient)
    record_ok = record.get("harness_name") == "antigravity" and record.get("harness_type") == "antigravity"
    add_check(
        "registry antigravity record",
        record_ok,
        f"name={record.get('harness_name')!r}; type={record.get('harness_type')!r}",
    )

    live_sentinel = f"GTKB_AGY_READY_{uuid.uuid4().hex}" if require_live else None
    dispatch_prompt = _sentinel_live_prompt(live_prompt, live_sentinel) if live_sentinel else live_prompt

    command: list[str] = []
    command_ok = False
    command_detail = ""
    if record_ok:
        try:
            command = build_dispatch_command(project_root, recipient, dispatch_prompt)
            command_ok = bool(command)
            if _is_legacy_gemini_command(command):
                command_ok = False
                command_detail = "registry still points at legacy Gemini CLI"
            elif not _is_agy_command(command):
                command_ok = False
                command_detail = f"registry command is not agy: {command[0] if command else '<missing>'}"
            else:
                command_detail = " ".join(command)
        except VerificationError as exc:
            command_detail = str(exc)
    add_check("registry agy headless argv", command_ok, command_detail)

    resolved_command = _resolve_executable_for_host(command) if command else []
    resolution_applied = bool(command and resolved_command and resolved_command[0] != command[0])
    executable_ok = bool(resolved_command) and (
        resolution_applied or shutil.which(resolved_command[0]) is not None or Path(resolved_command[0]).is_file()
    )
    add_check(
        "headless Antigravity agy CLI",
        executable_ok,
        resolved_command[0] if resolved_command else "missing command",
    )

    live_probe: dict[str, Any] | None = None
    live_ok = True
    if require_live and command_ok and executable_ok:
        try:
            live_probe = _run_live_probe(
                resolved_command,
                project_root=project_root,
                sentinel=live_sentinel,
                timeout=timeout,
                runner=live_runner,
            )
            live_ok = bool(live_probe["ok"])
            detail = f"returncode={live_probe['returncode']}; stdout_bytes={live_probe['stdout_bytes']}"
        except (OSError, subprocess.SubprocessError, subprocess.TimeoutExpired) as exc:
            live_probe = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
            live_ok = False
            detail = live_probe["error"]
        add_check("live agy prompt probe", live_ok, detail)

    roles = _role_tokens(record)
    ready = record_ok and command_ok and executable_ok and live_ok
    dispatchable_now = (
        ready
        and record.get("status") == "active"
        and bool(record.get("can_receive_dispatch"))
        and bool(roles & DISPATCH_ROLES)
    )
    return {
        "checks": checks,
        "command": command,
        "dispatchable_now": dispatchable_now,
        "first_failed_check": _first_failed_detail(checks),
        "harness_id": recipient,
        "live_probe": live_probe,
        "ready": ready,
        "recipient": recipient,
        "resolved_command": resolved_command,
        "role": sorted(roles),
        "status": record.get("status"),
        "can_receive_dispatch": bool(record.get("can_receive_dispatch")),
        "verdict_anchor_guard": inspect_verdict_anchor_guard(project_root),
    }


def run_verification(
    *,
    project_root: Path,
    recipient: str,
    prompt_fixture: Path,
    timeout: float,
    evidence_root: Path = DEFAULT_EVIDENCE_ROOT,
) -> dict[str, Any]:
    """Run the headless dispatch verification and write evidence files."""

    prompt_path = prompt_fixture if prompt_fixture.is_absolute() else project_root / prompt_fixture
    try:
        prompt = prompt_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise VerificationError(f"prompt fixture unreadable: {prompt_path}: {exc}") from exc

    command = build_dispatch_command(project_root, recipient, prompt)
    resolved_command = _resolve_executable_for_host(command)
    evidence_dir = evidence_root / _timestamp()
    evidence_dir.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    # Use temp files for stdout/stderr instead of subprocess pipes. On Windows,
    # .cmd wrappers (e.g., npm-installed CLIs like gemini.CMD) spawn child
    # node.exe processes that hold inherited pipe handles even after the
    # wrapper exits. Python's subprocess.run with capture_output=True blocks
    # in communicate() waiting for those pipes to close, which can hang
    # indefinitely. Redirecting to OS-managed files avoids the drain hazard
    # because Python never has to read from pipes -- the OS writes directly.
    with (
        tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8", delete=False, suffix=".stdout") as stdout_tf,
        tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8", delete=False, suffix=".stderr") as stderr_tf,
    ):
        stdout_path = Path(stdout_tf.name)
        stderr_path = Path(stderr_tf.name)
    try:
        # stdin=subprocess.DEVNULL ensures the launched process doesn't block
        # reading stdin (gemini.cmd and similar wrappers may otherwise block).
        # The substrate-verification objective is launch success, not stdin
        # interaction.
        with stdout_path.open("w", encoding="utf-8") as so, stderr_path.open("w", encoding="utf-8") as se:
            completed = subprocess.run(
                resolved_command,
                cwd=project_root,
                stdin=subprocess.DEVNULL,
                stdout=so,
                stderr=se,
                timeout=timeout,
                check=False,
                **_hidden_process_kwargs(),
            )
        elapsed = time.monotonic() - started
        stdout = sanitize_capture(stdout_path.read_text(encoding="utf-8", errors="replace"))
        stderr = sanitize_capture(stderr_path.read_text(encoding="utf-8", errors="replace"))
        substrate_ok = True
        error = None
        returncode = completed.returncode
    except subprocess.TimeoutExpired as exc:
        # The subprocess WAS launched but did not complete within the timeout.
        # The substrate (process launch) is therefore verified; the timeout
        # reflects program-level slowness or interactivity, not substrate
        # failure. Per proposal -003 § Verification Limitations Anticipated,
        # "the Gemini CLI exit code is not normative for the substrate test.
        # Subprocess launch success is the substrate criterion."
        elapsed = time.monotonic() - started
        # Read whatever the process wrote to the temp files before timeout.
        try:
            stdout = sanitize_capture(stdout_path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            stdout = ""
        try:
            stderr = sanitize_capture(stderr_path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            stderr = ""
        substrate_ok = True
        error = {
            "type": "TimeoutExpired",
            "message": str(exc),
            "note": "subprocess launched successfully but did not complete within timeout; substrate verified",
        }
        returncode = None
    except (OSError, subprocess.SubprocessError) as exc:
        # OSError (incl. FileNotFoundError / WinError 2) means the subprocess
        # could not be launched -- this IS a substrate failure.
        elapsed = time.monotonic() - started
        stdout = ""
        stderr = sanitize_capture(str(exc))
        substrate_ok = False
        error = {"type": type(exc).__name__, "message": str(exc)}
        returncode = None
    finally:
        # Best-effort cleanup of the OS-temp files (the subprocess captures
        # were copied above to the durable evidence files written below).
        for tmp_path in (stdout_path, stderr_path):
            try:
                tmp_path.unlink()
            except OSError:
                pass

    argv_payload = {
        "argv": command,
        "recipient": recipient,
        "resolved_argv": resolved_command,
        "resolution_applied": resolved_command != command,
    }
    result_payload = {
        "elapsed_seconds": round(elapsed, 3),
        "error": error,
        "recipient": recipient,
        "resolution_applied": resolved_command != command,
        "resolved_argv": resolved_command,
        "returncode": returncode,
        "stderr_bytes": len(stderr.encode("utf-8")),
        "stdout_bytes": len(stdout.encode("utf-8")),
        "substrate_ok": substrate_ok,
        "timestamp": dt.datetime.now(dt.UTC).isoformat(),
        "verdict_anchor_guard": inspect_verdict_anchor_guard(project_root),
    }
    _write_text(evidence_dir / "argv.json", json.dumps(argv_payload, indent=2, sort_keys=True) + "\n")
    _write_text(evidence_dir / "result.json", json.dumps(result_payload, indent=2, sort_keys=True) + "\n")
    _write_text(evidence_dir / "stdout.txt", stdout)
    _write_text(evidence_dir / "stderr.txt", stderr)
    result_payload["evidence_dir"] = str(evidence_dir)
    result_payload["argv"] = command
    return result_payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipient", required=True, help="Harness ID to verify, expected C for Antigravity.")
    parser.add_argument("--prompt-fixture", type=Path)
    parser.add_argument("--live", action="store_true", help="Run a live non-mutating agy prompt probe.")
    parser.add_argument("--prompt", default=DEFAULT_LIVE_PROMPT)
    parser.add_argument("--timeout", default=DEFAULT_TIMEOUT_SECONDS, type=float)
    parser.add_argument("--project-root", default=PROJECT_ROOT, type=Path)
    parser.add_argument("--evidence-root", default=DEFAULT_EVIDENCE_ROOT, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        if args.live or args.prompt_fixture is None:
            result = evaluate_readiness(
                project_root=args.project_root.resolve(),
                recipient=args.recipient,
                require_live=args.live,
                live_prompt=args.prompt,
                timeout=args.timeout,
            )
        else:
            result = run_verification(
                project_root=args.project_root.resolve(),
                recipient=args.recipient,
                prompt_fixture=args.prompt_fixture,
                timeout=args.timeout,
                evidence_root=args.evidence_root
                if args.evidence_root.is_absolute()
                else args.project_root / args.evidence_root,
            )
    except VerificationError as exc:
        payload = {"error": str(exc), "recipient": args.recipient, "ready": False, "substrate_ok": False}
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif "ready" in result:
        print(f"ready={result['ready']}")
        print(f"dispatchable_now={result['dispatchable_now']}")
        print(f"first_failed_check={result['first_failed_check']}")
    else:
        print(f"evidence_dir={result['evidence_dir']}")
        print(f"returncode={result['returncode']}")
        print(f"substrate_ok={result['substrate_ok']}")
    if "ready" in result:
        return 0 if result["ready"] else 1
    return 0 if result["substrate_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
