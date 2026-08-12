#!/usr/bin/env python3
"""Harness capability probe — DeepSeek V4 Pro Run 2 (WI-5808 run 2 of 3).

A deterministic, read-only capability probe that emits a machine-readable JSON
report covering six checks:

(1) Project-root containment — process cwd resolves inside the GT-KB root.
(2) Venv resolution — groundtruth-kb/.venv/Scripts/python.exe exists and imports
    groundtruth_kb.
(3) Git read health — HEAD sha and dirty count via ``--no-optional-locks``.
(4) gt CLI reachability — exit-0 help probe.
(5) Session-envelope surface presence — read-only discovery of an authoritative
    per-session document.
(6) Report determinism — two consecutive runs in an unchanged worktree produce
    byte-identical JSON apart from an explicitly labeled ``generated_at`` field.

Subprocess timeouts are read from the documented ``--timeout`` CLI argument.
No hard-coded timer/timeout literals exist in this module
(per DELIB-202667722 timer discipline).

All report keys use snake_case convention (per owner decision in kickoff
transcript).

Usage::

    python scripts/harness_probe_dsv4pro_r2.py [--timeout SECONDS]

Output: JSON report to stdout.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone  # noqa: UP017
from pathlib import Path

_PROBE_VERSION = "1.0.0"
_RUN_IDENTIFIER = "dsv4pro-r2"
# Paths checked relative to project root (determined from the installed probe
# path, independent of the invoking CWD).
_VENV_PYTHON_PARTS = ("groundtruth-kb", ".venv", "Scripts", "python.exe")
_PROJECT_MARKER_PARTS = ("groundtruth-kb", ".claude", "rules")


def _resolve_project_root(probe_path: Path | None = None) -> Path | None:
    """Resolve the canonical GT-KB project root from the installed probe path.

    Derives the root from the probe's own installed location (not the invoking
    CWD) so root authority is independent of where the probe was launched. The
    root candidate must contain the ``groundtruth-kb/`` and ``.claude/rules/``
    markers to be treated as authoritative. Returns ``None`` when the markers
    are absent (fail closed); it never falls back to the invoking CWD.
    """
    source = probe_path if probe_path is not None else Path(__file__)
    candidate = source.resolve().parent.parent
    gt_kb_marker = candidate / "groundtruth-kb"
    claude_rules = candidate / ".claude" / "rules"
    if gt_kb_marker.is_dir() and claude_rules.is_dir():
        return candidate
    return None


def _check_project_root_containment(
    project_root: Path | None,
    observed_cwd: Path | None = None,
) -> dict[str, object]:
    """Check (1): the observed working directory resolves inside the GT-KB root.

    ``observed_cwd`` is an optional seam: production supplies ``Path.cwd()``;
    tests may supply a synthetic absolute non-descendant path as data only.
    Fails closed: an unresolvable root (``None``) or a non-descendant observed
    CWD reports containment ``False``.
    """
    cwd = (observed_cwd if observed_cwd is not None else Path.cwd()).resolve()
    contained = False
    if project_root is not None:
        try:
            cwd.relative_to(project_root.resolve())
            contained = True
        except ValueError:
            pass
    return {
        "project_root_containment": contained,
        "details": {
            "cwd": str(cwd),
            "project_root": str(project_root.resolve()) if project_root is not None else None,
        },
    }


def _check_venv_resolution(project_root: Path | None, timeout: float) -> dict[str, object]:
    """Check (2): venv python.exe exists and imports groundtruth_kb."""
    if project_root is None:
        return {
            "venv_resolution": False,
            "details": {
                "venv_python_path": None,
                "exists": False,
                "imports_groundtruth_kb": False,
                "import_error": "project root unresolved",
            },
        }
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
        "venv_resolution": exists and imports_ok,
        "details": {
            "venv_python_path": str(venv_python),
            "exists": exists,
            "imports_groundtruth_kb": imports_ok,
            "import_error": import_error,
        },
    }


def _check_git_read_health(project_root: Path | None, timeout: float) -> dict[str, object]:
    """Check (3): git read health via --no-optional-locks."""
    head_sha: str | None = None
    dirty_count: int | None = None
    git_error: str | None = None
    git_ok = False
    if project_root is None:
        git_error = "project root unresolved"
    else:
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
            "ok": git_ok,
            "head_sha": head_sha,
            "dirty_count": dirty_count,
        },
        "details": {
            "git_error": git_error,
        },
    }


def _check_gt_cli_reachability(project_root: Path | None, timeout: float) -> dict[str, object]:
    """Check (4): gt CLI exit-0 help probe."""
    reachable = False
    exit_code: int | None = None
    stderr_snippet: str | None = None
    if project_root is None:
        stderr_snippet = "project root unresolved"
    else:
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
        "gt_cli_reachability": reachable,
        "details": {
            "exit_code": exit_code,
            "stderr_snippet": stderr_snippet,
        },
    }


def _check_session_envelope_presence(
    project_root: Path | None,
) -> dict[str, object]:
    """Check (5): authoritative per-session-envelope presence."""
    if project_root is None:
        return {
            "session_envelope_presence": False,
            "details": {
                "envelope_path": None,
            },
        }
    state_root = project_root / "harness-state"
    envelope_paths = sorted(state_root.glob("*/session-envelopes/*.json")) if state_root.is_dir() else []
    present = bool(envelope_paths)
    return {
        "session_envelope_presence": present,
        "details": {
            "envelope_path": str(envelope_paths[0]) if envelope_paths else None,
            "checked_glob": str(state_root / "*/session-envelopes/*.json"),
        },
    }


def _build_core_checks(project_root: Path | None, timeout: float) -> dict[str, object]:
    """Build the deterministic core checks (1)-(5) used for determinism."""
    core: dict[str, object] = {}
    core.update(_check_project_root_containment(project_root))
    core.update(_check_venv_resolution(project_root, timeout))
    core.update(_check_git_read_health(project_root, timeout))
    core.update(_check_gt_cli_reachability(project_root, timeout))
    core.update(_check_session_envelope_presence(project_root))
    return core


def _check_report_determinism(
    project_root: Path | None,
    timeout: float,
    reference_core: dict[str, object],
) -> dict[str, object]:
    """Check (6): report determinism — observed comparison of two payloads.

    Two independently built canonical payloads are compared; ``True`` only when
    they are equal, so the runtime value reflects an actual measurement rather
    than self-attesting success.
    """
    second_core = _build_core_checks(project_root, timeout)
    deterministic = second_core == reference_core
    return {
        "report_determinism": deterministic,
        "details": {
            "note": (
                "Observed by comparing two independently built canonical payloads (checks 1-5) in the current worktree."
            ),
            "measurement": "observed",
        },
    }


def build_report(
    project_root: Path | None,
    timeout: float,
) -> dict[str, object]:
    """Build the complete probe report."""
    generated_at = datetime.now(timezone.utc).isoformat()  # noqa: UP017

    report: dict[str, object] = {
        "generated_at": generated_at,
        "probe_version": _PROBE_VERSION,
        "run_identifier": _RUN_IDENTIFIER,
    }

    # Checks (1)-(5): deterministic core
    core = _build_core_checks(project_root, timeout)
    report.update(core)

    # Check (6): report determinism (observed comparison)
    report.update(_check_report_determinism(project_root, timeout, reference_core=core))

    return report


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments.

    The ``--timeout`` argument is a required, documented, positive float input.
    No default or fallback exists in this module; omission fails before any
    probe subprocess starts (per DELIB-202667722 timer discipline).
    """
    parser = argparse.ArgumentParser(
        description="Harness capability probe — DeepSeek V4 Pro Run 2",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        required=True,
        help=("Subprocess timeout in seconds for git and gt CLI checks (required)."),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point: run all checks and emit JSON report to stdout."""
    args = _parse_args(argv)
    if args.timeout <= 0:
        print("error: --timeout must be a positive number", file=sys.stderr)
        return 2
    project_root = _resolve_project_root()
    report = build_report(project_root, timeout=args.timeout)
    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
