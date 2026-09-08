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
import math
import subprocess
import sys
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _resolve_project_root() -> Path:
    """Bind the probe to the repository containing this script."""
    return PROJECT_ROOT


def _is_within(path: Path, root: Path) -> bool:
    """Return whether *path* is *root* or a descendant of it."""
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def check_project_root_containment(
    project_root: Path,
    *,
    expected_root: Path = PROJECT_ROOT,
) -> dict:
    """Check 1: root identity is canonical and cwd is inside it."""
    cwd = Path.cwd().resolve()
    root = project_root.resolve()
    canonical_root = expected_root.resolve()
    root_matches = root == canonical_root
    cwd_contained = _is_within(cwd, canonical_root)
    passed = root_matches and cwd_contained
    if not root_matches:
        detail = "supplied project root does not match the script-bound GT-KB root"
    elif not cwd_contained:
        detail = "cwd is outside the script-bound GT-KB root"
    else:
        detail = "project root is canonical and cwd is contained"
    return {
        "check": "project_root_containment",
        "passed": passed,
        "project_root": str(root),
        "expected_project_root": str(canonical_root),
        "process_cwd": str(cwd),
        "detail": detail,
    }


def check_venv_resolution(project_root: Path, timeout: float) -> dict:
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


def check_git_read_health(project_root: Path, timeout: float) -> dict:
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


def check_gt_cli_reachability(project_root: Path, timeout: float) -> dict:
    """Check 4: gt CLI reachability (exit-0 help probe)."""
    gt_executable = project_root / "groundtruth-kb" / ".venv" / "Scripts" / "gt.exe"
    if not gt_executable.is_file():
        return {
            "check": "gt_cli_reachability",
            "passed": False,
            "executable": str(gt_executable),
            "exit_code": None,
            "detail": "canonical project venv gt.exe not found",
        }
    try:
        result = subprocess.run(
            [str(gt_executable), "--help"],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        passed = result.returncode == 0
        return {
            "check": "gt_cli_reachability",
            "passed": passed,
            "executable": str(gt_executable),
            "exit_code": result.returncode,
            "detail": "canonical gt --help exit 0"
            if passed
            else f"canonical gt --help exit {result.returncode}: {result.stderr.strip()[:200]}",
        }
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {
            "check": "gt_cli_reachability",
            "passed": False,
            "executable": str(gt_executable),
            "exit_code": None,
            "detail": f"subprocess error: {exc}",
        }


def check_session_envelope_presence(project_root: Path) -> dict:
    """Check 5: authoritative per-session-envelope presence."""
    state_root = project_root / "harness-state"
    envelope_paths = sorted(state_root.glob("*/session-envelopes/*.json")) if state_root.is_dir() else []
    found = [str(p) for p in envelope_paths if p.is_file()]
    return {
        "check": "session_envelope_presence",
        "passed": len(found) > 0,
        "checked_paths": [str(p) for p in envelope_paths],
        "found": found,
        "detail": "per-session envelope found" if found else "no authoritative per-session envelope found",
    }


def _run_capability_checks(project_root: Path, timeout: float) -> list[dict]:
    """Run the five external capability checks once."""
    results = []
    checks: list[tuple[str, Callable[[], dict]]] = [
        ("project_root_containment", lambda: check_project_root_containment(project_root)),
        ("project_venv_resolution", lambda: check_venv_resolution(project_root, timeout)),
        ("git_read_health", lambda: check_git_read_health(project_root, timeout)),
        ("gt_cli_reachability", lambda: check_gt_cli_reachability(project_root, timeout)),
        ("session_envelope_presence", lambda: check_session_envelope_presence(project_root)),
    ]

    for _name, fn in checks:
        results.append(fn())
    return results


def _snapshot_bytes(project_root: Path, results: list[dict]) -> bytes:
    """Serialize the deterministic portion of one capability snapshot."""
    snapshot = {
        "probe": "harness_probe_dsv4pro-r1",
        "project_root": str(project_root.resolve()),
        "overall_passed": all(result["passed"] for result in results),
        "results": results,
    }
    return json.dumps(snapshot, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def check_report_determinism(
    project_root: Path,
    first_results: list[dict],
    second_results: list[dict],
) -> dict:
    """Check 6: compare byte serialization of two live snapshots."""
    first_bytes = _snapshot_bytes(project_root, first_results)
    second_bytes = _snapshot_bytes(project_root, second_results)
    passed = first_bytes == second_bytes
    return {
        "check": "report_determinism",
        "passed": passed,
        "detail": "two capability snapshots are byte-identical"
        if passed
        else "capability snapshots changed within one probe run",
    }


def run_all_checks(project_root: Path, timeout: float) -> dict:
    """Run all six checks and assemble the JSON report."""
    first_results = _run_capability_checks(project_root, timeout)
    second_results = _run_capability_checks(project_root, timeout)
    determinism = check_report_determinism(project_root, first_results, second_results)
    results = [*first_results, determinism]

    return {
        "probe": "harness_probe_dsv4pro-r1",
        "generated_at": datetime.now(timezone.utc).isoformat(),  # noqa: UP017
        "project_root": str(project_root),
        "overall_passed": all(result["passed"] for result in results),
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="GT-KB harness capability probe — DeepSeek V4 Pro Run 1",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        required=True,
        help="Positive subprocess timeout in seconds; supplied by the caller",
    )
    parser.add_argument(
        "--project-root",
        default=None,
        help="Root to verify against the script-bound GT-KB repository",
    )
    args = parser.parse_args()
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("--timeout must be a finite value greater than zero")

    if args.project_root:
        project_root = Path(args.project_root)
    else:
        project_root = _resolve_project_root()

    report = run_all_checks(project_root, args.timeout)
    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
