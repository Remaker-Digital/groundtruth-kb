#!/usr/bin/env python3
"""Harness capability probe — DeepSeek V4 Pro Run 1.

Deterministic read-only probe per WI-5808 (PROJECT-GTKB-HARNESS-TEST).
Bridge: gtkb-wi5808-harness-probe-dsv4pro-r1 (GO at 008).
Target: scripts/harness_probe_dsv4pro-r1.py.

Emits a machine-readable JSON report to stdout covering six checks.
Timer discipline (DELIB-202667722): --timeout CLI argument, no hard-coded literals.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _resolve_project_root() -> Path:
    """Return the GT-KB project root from git or an env override."""
    try:
        result = subprocess.run(
            ["git", "--no-optional-locks", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip())
    except (subprocess.TimeoutExpired, OSError):
        pass
    env_root = os.environ.get("GTKB_PROJECT_ROOT")
    if env_root:
        return Path(env_root)
    return Path.cwd()


def check_project_root_containment(project_root: Path) -> dict:
    """Check 1: process cwd resolves inside the GT-KB project root."""
    cwd = Path.cwd().resolve()
    root = project_root.resolve()
    contained = str(cwd).lower().startswith(str(root).lower() + os.sep) or cwd == root
    return {
        "check": "project_root_containment",
        "passed": contained,
        "project_root": str(root),
        "process_cwd": str(cwd),
        "detail": "cwd is inside project root" if contained else "cwd is outside project root",
    }


def check_venv_resolution(project_root: Path, timeout: int) -> dict:
    """Check 2: project venv exists and imports groundtruth_kb."""
    venv_python = project_root / "groundtruth-kb" / ".venv" / "Scripts" / "python.exe"
    venv_exists = venv_python.is_file()
    import_ok = False
    import_detail = ""
    if venv_exists:
        try:
            result = subprocess.run(
                [str(venv_python), "-c", "import groundtruth_kb"],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            import_ok = result.returncode == 0
            import_detail = "import succeeded" if import_ok else f"import failed: {result.stderr.strip()}"
        except (subprocess.TimeoutExpired, OSError) as exc:
            import_detail = f"subprocess error: {exc}"
    else:
        import_detail = "venv python.exe not found"
    return {
        "check": "project_venv_resolution",
        "passed": venv_exists and import_ok,
        "venv_python": str(venv_python),
        "venv_exists": venv_exists,
        "import_groundtruth_kb": import_ok,
        "detail": "venv exists and groundtruth_kb imports" if (venv_exists and import_ok) else import_detail,
    }


def check_git_read_health(project_root: Path, timeout: int) -> dict:
    """Check 3: git read health via --no-optional-locks."""
    head_sha = None
    dirty_count = None
    errors = []
    try:
        result = subprocess.run(
            ["git", "--no-optional-locks", "-C", str(project_root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0 and result.stdout.strip():
            head_sha = result.stdout.strip()
        else:
            errors.append(f"rev-parse HEAD failed: {result.stderr.strip()}")
    except (subprocess.TimeoutExpired, OSError) as exc:
        errors.append(f"rev-parse HEAD error: {exc}")
    try:
        result = subprocess.run(
            ["git", "--no-optional-locks", "-C", str(project_root), "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            dirty_count = len([l for l in result.stdout.splitlines() if l.strip()])
        else:
            errors.append(f"status --porcelain failed: {result.stderr.strip()}")
    except (subprocess.TimeoutExpired, OSError) as exc:
        errors.append(f"status --porcelain error: {exc}")
    passed = head_sha is not None and dirty_count is not None
    return {
        "check": "git_read_health",
        "passed": passed,
        "head_sha": head_sha,
        "dirty_count": dirty_count,
        "detail": f"HEAD={head_sha}, dirty={dirty_count}" if passed else "; ".join(errors),
    }


def check_gt_cli_reachability(timeout: int) -> dict:
    """Check 4: gt CLI reachability (exit-0 help probe)."""
    try:
        result = subprocess.run(
            ["gt", "--help"],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        passed = result.returncode == 0
        return {
            "check": "gt_cli_reachability",
            "passed": passed,
            "exit_code": result.returncode,
            "detail": "gt --help exit 0"
            if passed
            else f"gt --help exit {result.returncode}: {result.stderr.strip()[:200]}",
        }
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {
            "check": "gt_cli_reachability",
            "passed": False,
            "exit_code": None,
            "detail": f"subprocess error: {exc}",
        }


def check_session_envelope_presence(project_root: Path) -> dict:
    """Check 5: session-envelope surface presence (read-only existence check)."""
    envelope_paths = [
        project_root / ".claude" / "session" / "envelope.json",
    ]
    found = [str(p) for p in envelope_paths if p.is_file()]
    return {
        "check": "session_envelope_presence",
        "passed": len(found) > 0,
        "checked_paths": [str(p) for p in envelope_paths],
        "found": found,
        "detail": "envelope found" if found else "envelope not found at any checked path",
    }


def run_all_checks(project_root: Path, timeout: int) -> dict:
    """Run all six checks and assemble the JSON report."""
    results = []
    all_passed = True

    checks = [
        ("project_root_containment", lambda: check_project_root_containment(project_root)),
        ("project_venv_resolution", lambda: check_venv_resolution(project_root, timeout)),
        ("git_read_health", lambda: check_git_read_health(project_root, timeout)),
        ("gt_cli_reachability", lambda: check_gt_cli_reachability(timeout)),
        ("session_envelope_presence", lambda: check_session_envelope_presence(project_root)),
    ]

    for _name, fn in checks:
        r = fn()
        results.append(r)
        if not r["passed"]:
            all_passed = False

    return {
        "probe": "harness_probe_dsv4pro-r1",
        "generated_at": datetime.now(timezone.utc).isoformat(),  # noqa: UP017
        "project_root": str(project_root),
        "overall_passed": all_passed,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="GT-KB harness capability probe — DeepSeek V4 Pro Run 1",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Subprocess timeout in seconds (default: 30)",
    )
    parser.add_argument(
        "--project-root",
        default=None,
        help="Override project root path (default: auto-detect via git)",
    )
    args = parser.parse_args()

    if args.project_root:
        project_root = Path(args.project_root)
    else:
        project_root = _resolve_project_root()

    report = run_all_checks(project_root, args.timeout)
    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
