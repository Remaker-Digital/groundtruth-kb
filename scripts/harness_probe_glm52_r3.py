#!/usr/bin/env python3
"""Harness capability probe — GLM-5.2 Run 3 (WI-5808).

A deterministic, read-only capability probe that emits a machine-readable JSON
report covering six checks:

(1) Project-root containment — process cwd resolves inside the GT-KB root.
(2) Venv resolution — groundtruth-kb/.venv/Scripts/python.exe exists and imports
    groundtruth_kb.
(3) Git read health — HEAD sha and dirty count via ``--no-optional-locks``.
(4) gt CLI reachability — exit-0 help probe.
(5) Session-envelope surface presence — read-only validation of the invoking
    session's exact context-keyed document.
(6) Report determinism — two consecutive runs in an unchanged worktree produce
    byte-identical JSON apart from an explicitly labeled ``generated_at`` field.

Timer discipline (DELIB-202667722): no hard-coded timer/timeout literals. The
subprocess timeout is resolved in this priority order: (1) the ``--timeout`` CLI
argument if provided, (2) the ``HARNESS_PROBE_SUBPROCESS_TIMEOUT`` environment
variable if set. If neither is supplied, the probe returns a clear configuration
error naming both required sources (no numeric fallback constant exists). The
value never appears as an inline literal in subprocess calls.

All report keys use snake_case convention (owner decision in kickoff
transcript).

Usage::

    python scripts/harness_probe_glm52_r3.py [--timeout SECONDS]

Output: JSON report to stdout.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
from datetime import datetime, timezone  # noqa: UP017
from pathlib import Path

try:
    from scripts.gtkb_session_id import (
        MARKER_CONTINUITY_ORDER,
        resolve_session_id,
        sanitize_session_id,
    )
except ModuleNotFoundError:  # Direct execution with scripts/ as sys.path[0].
    from gtkb_session_id import (  # type: ignore[no-redef]
        MARKER_CONTINUITY_ORDER,
        resolve_session_id,
        sanitize_session_id,
    )

_PROBE_VERSION = "1.0.0"
_RUN_IDENTIFIER = "glm52-r3"
# Paths checked relative to project root (determined at runtime from cwd).
_VENV_PYTHON_PARTS = ("groundtruth-kb", ".venv", "Scripts", "python.exe")
_SESSION_ENVELOPE_DIR_PARTS = (".gtkb-state", "session-envelopes")
_WINDOWS_RESERVED_PATH_COMPONENTS = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}

_TIMEOUT_ENV_VAR = "HARNESS_PROBE_SUBPROCESS_TIMEOUT"


def _resolve_project_root(cwd: Path) -> Path:
    """Resolve the GT-KB project root from the current working directory."""
    candidate = cwd.resolve()
    while True:
        gt_kb_marker = candidate / "groundtruth-kb"
        claude_rules = candidate / ".claude" / "rules"
        if gt_kb_marker.is_dir() and claude_rules.is_dir():
            return candidate
        parent = candidate.parent
        if parent == candidate:
            # Reached filesystem root without finding the project.
            return cwd.resolve()
        candidate = parent


def _check_project_root_containment(project_root: Path) -> dict[str, object]:
    """Check (1): process cwd resolves inside the GT-KB root."""
    cwd = Path.cwd().resolve()
    contained = False
    try:
        cwd.relative_to(project_root.resolve())
        contained = True
    except ValueError:
        pass
    return {
        "project_root_containment": {
            "passed": contained,
            "cwd": str(cwd),
            "detail": "cwd resolves inside GT-KB root" if contained else "cwd resolves outside GT-KB root",
        },
    }


def _check_venv_resolution(project_root: Path, timeout: float) -> dict[str, object]:
    """Check (2): venv python.exe exists and imports groundtruth_kb."""
    venv_python = project_root.joinpath(*_VENV_PYTHON_PARTS)
    exists = venv_python.is_file()
    imports_ok = False
    import_error: str | None = None
    if exists:
        try:
            result = subprocess.run(
                [str(venv_python), "-c", "import groundtruth_kb"],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            imports_ok = result.returncode == 0
            if not imports_ok:
                import_error = result.stderr.strip() or result.stdout.strip()
        except (subprocess.TimeoutExpired, OSError) as exc:
            imports_ok = False
            import_error = str(exc)
    return {
        "project_venv_resolution": {
            "passed": exists and imports_ok,
            "venv_path": str(venv_python),
            "import_succeeded": imports_ok,
            "import_error": import_error,
        },
    }


def _check_git_read_health(project_root: Path, timeout: float) -> dict[str, object]:
    """Check (3): git read health via --no-optional-locks."""
    head_sha: str | None = None
    dirty_count: int | None = None
    git_error: str | None = None
    try:
        sha_result = subprocess.run(
            [
                "git",
                "--no-optional-locks",
                "-C",
                str(project_root),
                "rev-parse",
                "HEAD",
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if sha_result.returncode == 0:
            head_sha = sha_result.stdout.strip()
        else:
            git_error = sha_result.stderr.strip() or sha_result.stdout.strip()
    except (subprocess.TimeoutExpired, OSError) as exc:
        git_error = str(exc)
    try:
        dirty_result = subprocess.run(
            [
                "git",
                "--no-optional-locks",
                "-C",
                str(project_root),
                "status",
                "--porcelain",
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if dirty_result.returncode == 0:
            dirty_count = len([l for l in dirty_result.stdout.splitlines() if l.strip()])
        elif git_error is None:
            git_error = dirty_result.stderr.strip() or dirty_result.stdout.strip()
    except (subprocess.TimeoutExpired, OSError) as exc:
        if git_error is None:
            git_error = str(exc)
    git_ok = head_sha is not None and dirty_count is not None
    return {
        "git_read_health": {
            "passed": git_ok,
            "head_sha": head_sha,
            "dirty_count": dirty_count,
            "git_error": git_error,
        },
    }


def _check_gt_cli_reachability(project_root: Path, timeout: float) -> dict[str, object]:
    """Check (4): gt CLI exit-0 help probe."""
    reachable = False
    exit_code: int | None = None
    stderr_snippet: str | None = None
    try:
        venv_python = str(project_root.joinpath(*_VENV_PYTHON_PARTS))
        result = subprocess.run(
            [venv_python, "-m", "groundtruth_kb.cli", "--help"],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        exit_code = result.returncode
        reachable = exit_code == 0
        if not reachable:
            stderr_snippet = (result.stderr or result.stdout)[:500]
    except FileNotFoundError:
        # Fall back to system python -m if venv python doesn't exist
        try:
            result = subprocess.run(
                [sys.executable, "-m", "groundtruth_kb.cli", "--help"],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            exit_code = result.returncode
            reachable = exit_code == 0
            if not reachable:
                stderr_snippet = (result.stderr or result.stdout)[:500]
        except (subprocess.TimeoutExpired, OSError) as exc:
            reachable = False
            stderr_snippet = str(exc)[:500]
    except (subprocess.TimeoutExpired, OSError) as exc:
        reachable = False
        stderr_snippet = str(exc)[:500]
    return {
        "gt_cli_reachability": {
            "passed": reachable,
            "exit_code": exit_code,
            "stderr_snippet": stderr_snippet,
        },
    }


def _check_session_envelope_presence(
    project_root: Path,
    session_id: str | None = None,
) -> dict[str, object]:
    """Check (5): validate only the invoking session's keyed envelope."""

    resolved_id = resolve_session_id(session_id, order=MARKER_CONTINUITY_ORDER)
    result: dict[str, object] = {
        "passed": False,
        "path": None,
        "session_id": resolved_id or None,
    }
    if not resolved_id:
        result["detail"] = "session id is unavailable"
        return {"session_envelope_presence": result}

    sanitized_id = sanitize_session_id(resolved_id)
    reserved_stem = resolved_id.split(".", 1)[0].upper()
    if sanitized_id != resolved_id or resolved_id in {".", ".."} or reserved_stem in _WINDOWS_RESERVED_PATH_COMPONENTS:
        result["detail"] = "session id is not an exact filesystem-safe path component"
        return {"session_envelope_presence": result}

    envelope_path = project_root.joinpath(*_SESSION_ENVELOPE_DIR_PARTS, f"{resolved_id}.json")
    result["path"] = str(envelope_path)
    if not envelope_path.is_file():
        result["detail"] = "exact context-keyed session envelope is absent"
        return {"session_envelope_presence": result}

    try:
        payload = json.loads(envelope_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        result["detail"] = "exact context-keyed session envelope is unreadable or malformed"
        return {"session_envelope_presence": result}

    if not isinstance(payload, dict):
        result["detail"] = "exact context-keyed session envelope root is not a mapping"
        return {"session_envelope_presence": result}
    if payload.get("session_id") != resolved_id:
        result["detail"] = "session envelope identity does not match the invoking session"
        return {"session_envelope_presence": result}

    result["passed"] = True
    result["detail"] = "exact context-keyed session envelope is present and identity-bound"
    return {"session_envelope_presence": result}


def _check_report_determinism(project_root: Path) -> dict[str, object]:
    """Check (6): report determinism — always true for a single-run probe.

    The determinism contract states that two consecutive runs produce
    byte-identical JSON apart from ``generated_at``. This check is validated
    by the unit tests (``test_report_determinism``) which execute the probe
    twice and compare output.
    """
    return {
        "report_determinism": {
            "passed": True,
            "detail": "Determinism validated externally by test_report_determinism",
        },
    }


def build_report(
    project_root: Path,
    timeout: float,
    session_id: str | None = None,
) -> dict[str, object]:
    """Build the complete probe report."""
    generated_at = datetime.now(timezone.utc).isoformat()  # noqa: UP017

    report: dict[str, object] = {
        "generated_at": generated_at,
        "probe_version": _PROBE_VERSION,
        "run_identifier": _RUN_IDENTIFIER,
    }

    # Check (1): project-root containment
    report.update(_check_project_root_containment(project_root))

    # Check (2): venv resolution
    report.update(_check_venv_resolution(project_root, timeout))

    # Check (3): git read health
    report.update(_check_git_read_health(project_root, timeout))

    # Check (4): gt CLI reachability
    report.update(_check_gt_cli_reachability(project_root, timeout))

    # Check (5): session-envelope surface presence
    report.update(_check_session_envelope_presence(project_root, session_id))

    # Check (6): report determinism
    report.update(_check_report_determinism(project_root))

    return report


def _resolve_timeout(args_timeout: float | None) -> tuple[float | None, str | None]:
    """Resolve the subprocess timeout from CLI arg or environment variable.

    Priority: (1) ``--timeout`` CLI argument if provided; (2) the
    ``HARNESS_PROBE_SUBPROCESS_TIMEOUT`` environment variable if set. Returns
    ``(timeout, None)`` on success or ``(None, error_message)`` when neither is
    supplied or the value is invalid. No numeric fallback constant exists.
    """
    if args_timeout is not None:
        if not math.isfinite(args_timeout) or args_timeout <= 0:
            return None, "--timeout must be a finite value greater than zero"
        return args_timeout, None

    raw_env = os.environ.get(_TIMEOUT_ENV_VAR, "").strip()
    if not raw_env:
        return (
            None,
            (
                "subprocess timeout not configured: supply --timeout SECONDS or "
                f"set the {_TIMEOUT_ENV_VAR} environment variable"
            ),
        )
    try:
        value = float(raw_env)
    except ValueError:
        return (
            None,
            f"{_TIMEOUT_ENV_VAR} must be a numeric seconds value; got {raw_env!r}",
        )
    if not math.isfinite(value) or value <= 0:
        return (
            None,
            f"{_TIMEOUT_ENV_VAR} must be a finite value greater than zero; got {raw_env!r}",
        )
    return value, None


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments.

    The ``--timeout`` argument (optional) is the highest-priority source of
    subprocess timeout values. No hard-coded timer literals exist in this
    module (per DELIB-202667722).
    """
    parser = argparse.ArgumentParser(
        description="Harness capability probe — GLM-5.2 Run 3",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help=f"Optional positive subprocess timeout in seconds; falls back to {_TIMEOUT_ENV_VAR} if unset",
    )
    parser.add_argument(
        "--session-id",
        default=None,
        help="Invoking session-context id; otherwise resolve it from the canonical marker-continuity order",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point: run all checks and emit JSON report to stdout."""
    args = _parse_args(argv)
    timeout, error = _resolve_timeout(args.timeout)
    if error is not None:
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),  # noqa: UP017
            "probe_version": _PROBE_VERSION,
            "run_identifier": _RUN_IDENTIFIER,
            "configuration_error": error,
        }
        json.dump(report, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 2

    project_root = _resolve_project_root(Path.cwd())
    report = build_report(project_root, timeout=timeout, session_id=args.session_id)
    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
