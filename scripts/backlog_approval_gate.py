#!/usr/bin/env python3
"""Check deterministic work-item approval-state transitions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from groundtruth_kb.backlog.approval_state import validate_transition  # noqa: E402
from groundtruth_kb.db import KnowledgeDB  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work_item_id")
    parser.add_argument("target_state")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = args.project_root.resolve()
    db = KnowledgeDB(root / "groundtruth.db")
    item = db.get_work_item(args.work_item_id)
    if item is None:
        raise SystemExit(f"work item not found: {args.work_item_id}")
    ok, reason = validate_transition(
        work_item_id=args.work_item_id,
        current_state=item.get("approval_state"),
        target_state=args.target_state,
        pending_owner_decisions_path=root / "memory" / "pending-owner-decisions.md",
        bridge_state_path=root / "bridge",
        project_root=root,
    )
    payload = {"allowed": ok, "reason": reason, "work_item_id": args.work_item_id}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(("ALLOW" if ok else "BLOCK") + f": {reason}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
