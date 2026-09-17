#!/usr/bin/env python3
"""Scoped GT-KB service boundary checker (Phase 4 baseline slice).

Fails fast if the Phase 4 scoped-service contract has regressed on any of
the dimensions owned by this slice:

1. Root ``groundtruth.toml`` is missing the ``[scoped_service]`` section,
   is missing required fields, or advertises mutating/request-class
   operations (deferred to later sub-slices).
2. The ``allowed_read_operations`` allowlist drifts away from what this
   slice supports (``dashboard.summary.read`` only).

The summary-path guard that scanned the SQLite-era startup generator for a raw
``groundtruth.db`` connection left with that generator (legacy startup
retirement, 2026-09); the scoped client itself is unchanged.

The checker never mutates anything. Exit code 0 = boundary intact,
exit code 1 = regression found, exit code 2 = unexpected failure.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights
reserved.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from gtkb_scoped_client import (  # noqa: E402  (path bootstrap above is required)
    DASHBOARD_SUMMARY_READ,
    SUPPORTED_READ_OPERATIONS,
    ScopedServiceConfigError,
    load_scoped_service_config,
)


class BoundaryCheckError(RuntimeError):
    """Raised when the scoped service boundary has regressed."""


def _check_config(project_root: Path) -> dict[str, Any]:
    try:
        config = load_scoped_service_config(project_root)
    except ScopedServiceConfigError as exc:
        raise BoundaryCheckError(f"scoped-service config invalid: {exc}") from exc

    expected_single_slice_allowlist = (DASHBOARD_SUMMARY_READ,)
    if config.allowed_read_operations != expected_single_slice_allowlist:
        raise BoundaryCheckError(
            "allowed_read_operations drifted from the Phase 4 baseline contract "
            f"(expected {list(expected_single_slice_allowlist)}, got "
            f"{list(config.allowed_read_operations)})"
        )

    if config.allowed_request_operations:
        raise BoundaryCheckError(
            f"allowed_request_operations must be empty in this slice (got {list(config.allowed_request_operations)})"
        )

    if set(config.allowed_read_operations) - SUPPORTED_READ_OPERATIONS:
        raise BoundaryCheckError(
            f"allowed_read_operations contains unsupported operations (supported: {sorted(SUPPORTED_READ_OPERATIONS)})"
        )

    return {
        "source_path": str(config.source_path),
        "project_root": str(config.project_root),
        "default_subject": config.default_subject,
        "application_id": config.application_id,
        "allowed_read_operations": list(config.allowed_read_operations),
        "runtime_root": str(config.runtime_root),
        "dashboard_db": str(config.dashboard_db),
    }


def run_checks(project_root: Path | None = None) -> dict[str, Any]:
    root = (project_root or PROJECT_ROOT).resolve()
    report: dict[str, Any] = {
        "project_root": str(root),
        "status": "pass",
        "checks": {},
    }

    errors: list[str] = []

    try:
        report["checks"]["config"] = _check_config(root)
    except BoundaryCheckError as exc:
        errors.append(str(exc))
        report["checks"]["config"] = {"error": str(exc)}

    if errors:
        report["status"] = "fail"
        report["errors"] = errors
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="check_scoped_service_boundary",
        description="Scoped GT-KB service boundary checker (Phase 4 baseline).",
    )
    parser.add_argument("--json", action="store_true", help="Emit the full report as JSON")
    parser.add_argument(
        "--project-root",
        default=None,
        help="Override the Agent Red project root (defaults to the repository root)",
    )
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).resolve() if args.project_root else None

    try:
        report = run_checks(project_root)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"UNEXPECTED ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        json.dump(report, sys.stdout, indent=2, default=str)
        sys.stdout.write("\n")
    else:
        status = report["status"]
        if status == "pass":
            print("scoped-service boundary: PASS")
            config = report["checks"].get("config", {})
            print(f"  config: {config.get('source_path')}")
            print(f"  allowed_read_operations: {config.get('allowed_read_operations')}")
        else:
            print("scoped-service boundary: FAIL", file=sys.stderr)
            for error in report.get("errors", []):
                print(f"  - {error}", file=sys.stderr)

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
