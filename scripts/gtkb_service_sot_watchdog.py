#!/usr/bin/env python
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Run the GT-KB service/SoT availability watchdog once."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _ensure_src_path(root: Path) -> None:
    src = root / "groundtruth-kb" / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def main(argv: list[str] | None = None) -> int:
    root = _repo_root()
    _ensure_src_path(root)

    from groundtruth_kb.watchdog.service_sot import default_status_path, run_service_sot_watchdog

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=str(root), help="GT-KB project root.")
    parser.add_argument("--output", default=None, help="Output JSON path. Defaults to .gtkb-state/watchdog.")
    parser.add_argument("--component", action="append", default=None, help="Limit gt-status probing to one component.")
    parser.add_argument("--no-write", action="store_true", help="Print JSON without writing the status file.")
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).resolve()
    output_path = Path(args.output).resolve() if args.output else default_status_path(project_root)
    payload = run_service_sot_watchdog(
        project_root,
        output_path=output_path,
        components=tuple(args.component) if args.component else None,
        write=not args.no_write,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("overall_status") in {"PASS", "WARN", "UNKNOWN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
