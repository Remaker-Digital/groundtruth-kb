#!/usr/bin/env python3
"""Report that work-item approval-state backfill is retired."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--apply", action="store_true", help="Accepted for compatibility; no writes are performed.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    _ = args.project_root.resolve()
    payload = {
        "apply": args.apply,
        "deprecated": True,
        "message": (
            "work-item approval-state backfill is retired; project-level PAUTH, bridge GO, "
            "and implementation-start packets are the implementation authority chain"
        ),
        "updated": 0,
        "items": [],
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(payload["message"])
        print("Updated rows: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
