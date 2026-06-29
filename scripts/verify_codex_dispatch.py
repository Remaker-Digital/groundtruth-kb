#!/usr/bin/env python3
"""Deterministic Codex dispatch readiness probe."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.harness_projection_reader import load_harness_projection  # noqa: E402

HARNESS_ID = "A"
HARNESS_NAME = "codex"
HARNESS_TYPE = "codex"


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


def evaluate_readiness(
    *,
    project_root: Path,
    recipient: str = HARNESS_ID,
    require_executable: bool = True,
    executable_resolver: Callable[[str], str | None] | None = None,
) -> dict[str, Any]:
    record = _load_harness_record(project_root, recipient)
    if record.get("harness_type") != HARNESS_TYPE:
        raise VerificationError(f"recipient {recipient} is not {HARNESS_TYPE}: {record.get('harness_type')!r}")

    argv = _headless_argv(record)
    resolver = executable_resolver or shutil.which
    resolved_executable = resolver(argv[0]) if argv else None
    executable_ok = bool(resolved_executable) if require_executable else True
    static_ok = bool(argv) and executable_ok
    dispatchable = (
        static_ok
        and record.get("status") == "active"
        and bool(record.get("can_receive_dispatch"))
        and HARNESS_NAME in {str(record.get("harness_name")), str(record.get("harness_type"))}
    )
    return {
        "can_receive_dispatch": bool(record.get("can_receive_dispatch")),
        "dispatchable": dispatchable,
        "executable_ok": executable_ok,
        "harness_id": recipient,
        "harness_name": record.get("harness_name"),
        "headless_argv": argv,
        "require_executable": require_executable,
        "resolved_executable": resolved_executable,
        "static_ok": static_ok,
        "status": record.get("status"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipient", default=HARNESS_ID)
    parser.add_argument("--project-root", default=PROJECT_ROOT, type=Path)
    parser.add_argument("--no-require-executable", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        result = evaluate_readiness(
            project_root=args.project_root.resolve(),
            recipient=args.recipient,
            require_executable=not args.no_require_executable,
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
