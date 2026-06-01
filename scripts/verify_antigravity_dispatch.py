#!/usr/bin/env python3
"""Verify headless Antigravity dispatch substrate without role/topology mutation."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.cross_harness_bridge_trigger import DispatchTarget, _harness_command  # noqa: E402

DEFAULT_EVIDENCE_ROOT = PROJECT_ROOT / ".gtkb-state" / "antigravity-onboarding" / "dispatch-verification"
CREDENTIAL_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*([A-Za-z0-9._~+/=-]{8,})"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
)


class VerificationError(RuntimeError):
    """Raised when the dispatch substrate cannot be verified."""


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

    registry_path = project_root / "harness-state" / "harness-registry.json"
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise VerificationError(f"harness registry not found: {registry_path}") from exc
    except json.JSONDecodeError as exc:
        raise VerificationError(f"harness registry is invalid JSON: {registry_path}: {exc}") from exc
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
    """Return ``command`` with element 0 resolved via the host's ambient PATH.

    Resolution relies ONLY on the launching context's ambient PATH, consistent
    with the External Harness Executable Resolution Exception clause 2a in
    ``.claude/rules/project-root-boundary.md`` (the same mechanism by which the
    codex/claude harness CLIs are already dispatched). This helper performs no
    PATH enrichment: it does not compute, guess, or inject any user-profile
    executable directory. ``shutil.which`` is used because, on Windows, Python's
    ``subprocess`` does not apply PATHEXT to bare command names (e.g., ``gemini``
    would not find ``gemini.cmd``); ``shutil.which`` DOES apply PATHEXT and
    returns the absolute path of the resolved executable.

    If ambient resolution fails (the executable is not on the launching
    context's PATH), the original ``command`` is returned unchanged so
    ``subprocess`` raises its native ``FileNotFoundError`` rather than this
    helper silently masking the failure with a user-profile guess. Providing
    ``gemini`` on PATH is the launcher's responsibility per clause 2a; a future
    ``.env.local``-configured override (clause 2b, ``GOV-ENV-LOCAL-AUTHORITY-001``)
    is a named extension, not implemented here.

    The registry-projected canonical argv (``argv.json`` evidence) is preserved
    via the caller recording both the projected and resolved argv separately;
    only the OS-launch boundary uses the resolved form.
    """

    if not command:
        return command
    resolved = shutil.which(command[0])
    if resolved is None:
        return command
    return [resolved] + list(command[1:])


def _timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


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
    parser.add_argument("--prompt-fixture", required=True, type=Path)
    parser.add_argument("--timeout", default=60.0, type=float)
    parser.add_argument("--project-root", default=PROJECT_ROOT, type=Path)
    parser.add_argument("--evidence-root", default=DEFAULT_EVIDENCE_ROOT, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
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
        payload = {"error": str(exc), "recipient": args.recipient, "substrate_ok": False}
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"evidence_dir={result['evidence_dir']}")
        print(f"returncode={result['returncode']}")
        print(f"substrate_ok={result['substrate_ok']}")
    return 0 if result["substrate_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
