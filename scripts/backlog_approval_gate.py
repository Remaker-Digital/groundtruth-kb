#!/usr/bin/env python3
"""Legacy compatibility wrapper for retired work-item approval-state checks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work_item_id")
    parser.add_argument("target_state")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    _ = args.project_root.resolve()
    reason = (
        "retired compatibility command; work-item approval metadata does not grant or block implementation authority"
    )
    payload = {
        "allowed": True,
        "deprecated": True,
        "reason": reason,
        "target_state": args.target_state,
        "work_item_id": args.work_item_id,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"NO-OP: {reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
