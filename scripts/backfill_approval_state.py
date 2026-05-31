#!/usr/bin/env python3
"""Backfill approval_state on current MemBase work items."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from groundtruth_kb.backlog.approval_state import classify_initial_state  # noqa: E402
from groundtruth_kb.db import KnowledgeDB  # noqa: E402

STATUS_RE = re.compile(r"^(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY):\s+bridge/")


def bridge_statuses(index_path: Path) -> dict[str, str]:
    statuses: dict[str, str] = {}
    current: str | None = None
    for line in index_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Document: "):
            current = line.split(":", 1)[1].strip()
            continue
        if current and (match := STATUS_RE.match(line.strip())):
            statuses.setdefault(current, match.group(1))
            current = None
    return statuses


def rows_needing_backfill(db: KnowledgeDB) -> list[dict[str, Any]]:
    return [
        row
        for row in db.list_work_items()
        if not str(row.get("approval_state") or "").strip()
        and str(row.get("resolution_status") or "")
        not in {"verified", "resolved", "retired", "wont_fix", "not_a_defect"}
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = args.project_root.resolve()
    db = KnowledgeDB(root / "groundtruth.db")
    statuses = bridge_statuses(root / "bridge" / "INDEX.md")
    planned = []
    for row in rows_needing_backfill(db):
        state = classify_initial_state(row, bridge_statuses=statuses)
        planned.append({"id": row["id"], "approval_state": state})
        if args.apply:
            db.update_work_item(
                row["id"],
                changed_by="prime-builder/codex/A",
                change_reason="WI-3271 Slice 1 approval-state backfill (deterministic classifier per bridge/gtkb-backlog-approval-state-taxonomy-slice-1-003.md)",
                approval_state=state,
            )
    counts = Counter(item["approval_state"] for item in planned)
    payload = {
        "apply": args.apply,
        "count": len(planned),
        "state_counts": dict(sorted(counts.items())),
        "items": planned,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"{'Applied' if args.apply else 'Dry-run'} approval_state backfill for {len(planned)} work item(s)")
        for state, count in sorted(counts.items()):
            print(f"{state}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
