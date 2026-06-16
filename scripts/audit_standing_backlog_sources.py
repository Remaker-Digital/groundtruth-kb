#!/usr/bin/env python3
"""Audit pre-existing sources that feed the Agent Red standing backlog."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
ACTIONABLE_BRIDGE_STATUSES = {"NEW", "REVISED", "GO", "NO-GO"}
NON_TERMINAL_WORK_ITEM_STATUSES = {
    "blocked",
    "created",
    "deferred",
    "in_progress",
    "new",
    "open",
    "specified",
    "unresolved",
}


def latest_bridge_entries(project_root: Path) -> list[dict[str, str]]:
    """Return one latest status row per numbered bridge document."""
    from groundtruth_kb.bridge.versioned_files import scan_expected_documents, status_from_bridge_file

    entries: list[dict[str, str]] = []
    for document in scan_expected_documents(project_root).values():
        rel_path = document.files[-1]
        status = status_from_bridge_file(project_root / rel_path)
        if not status:
            continue
        entries.append(
            {
                "document": document.slug,
                "status": status,
                "path": rel_path,
            }
        )
    return sorted(entries, key=lambda entry: entry["path"])


def bridge_summary(project_root: Path) -> dict[str, Any]:
    entries = latest_bridge_entries(project_root)
    status_counts = Counter(entry["status"] for entry in entries)
    actionable = [entry for entry in entries if entry["status"] in ACTIONABLE_BRIDGE_STATUSES]
    return {
        "status_counts": dict(sorted(status_counts.items())),
        "actionable": actionable,
    }


def work_item_summary(project_root: Path) -> dict[str, Any]:
    db_path = project_root / "groundtruth.db"
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    try:
        active_authorized_work_item_ids: set[str] = set()
        for row in connection.execute(
            "SELECT included_work_item_ids FROM current_project_authorizations WHERE status = 'active'"
        ):
            raw_ids = row["included_work_item_ids"]
            if not raw_ids:
                continue
            try:
                parsed_ids = json.loads(raw_ids)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed_ids, list):
                active_authorized_work_item_ids.update(str(item_id) for item_id in parsed_ids)

        status_counts = {
            row["resolution_status"]: row["count"]
            for row in connection.execute(
                "SELECT resolution_status, count(*) AS count "
                "FROM current_work_items GROUP BY resolution_status ORDER BY resolution_status"
            )
        }
        non_terminal_rows = [
            dict(row)
            for row in connection.execute(
                "SELECT id, resolution_status, priority, component, project_name, source_spec_id, title "
                "FROM current_work_items "
                "WHERE resolution_status IN ({}) "
                "ORDER BY CASE priority WHEN 'P0' THEN 0 WHEN 'P1' THEN 1 WHEN 'P2' THEN 2 ELSE 9 END, id".format(
                    ",".join("?" for _ in NON_TERMINAL_WORK_ITEM_STATUSES)
                ),
                sorted(NON_TERMINAL_WORK_ITEM_STATUSES),
            )
        ]
        authorization_status_counts = Counter(
            "covered_by_active_authorization"
            if row["id"] in active_authorized_work_item_ids
            else "not_in_active_authorization"
            for row in non_terminal_rows
        )
        priority_counts = {
            f"{row['priority'] or 'none'}:{row['resolution_status']}": row["count"]
            for row in connection.execute(
                "SELECT priority, resolution_status, count(*) AS count "
                "FROM current_work_items "
                "WHERE resolution_status IN ({}) "
                "GROUP BY priority, resolution_status "
                "ORDER BY priority, resolution_status".format(",".join("?" for _ in NON_TERMINAL_WORK_ITEM_STATUSES)),
                sorted(NON_TERMINAL_WORK_ITEM_STATUSES),
            )
        }
    finally:
        connection.close()

    return {
        "status_counts": status_counts,
        "authorization_status_counts": dict(sorted(authorization_status_counts.items())),
        "priority_status_counts": priority_counts,
        "top_non_terminal": non_terminal_rows[:25],
    }


def release_blocker_summary(project_root: Path) -> list[str]:
    text = (project_root / "memory" / "release-readiness.md").read_text(encoding="utf-8")
    in_section = False
    blockers: list[str] = []
    current_blocker: list[str] = []

    def flush_blocker() -> None:
        if current_blocker:
            blockers.append(" ".join(current_blocker).strip())
            current_blocker.clear()

    for line in text.splitlines():
        if line.startswith("## Remaining Release Blockers"):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            flush_blocker()
            break
        if in_section and line.startswith("- "):
            flush_blocker()
            current_blocker.append(line[2:].strip())
            continue
        if in_section and current_blocker and line.startswith("  "):
            current_blocker.append(line.strip())
    else:
        flush_blocker()
    return blockers


def build_audit(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    return {
        "bridge": bridge_summary(project_root),
        "work_items": work_item_summary(project_root),
        "release_blockers": release_blocker_summary(project_root),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(argv)

    audit = build_audit(args.project_root.resolve())
    if args.json:
        print(json.dumps(audit, indent=2, sort_keys=True))
        return 0

    bridge = audit["bridge"]
    work_items = audit["work_items"]
    print("Standing backlog source audit")
    print(f"Bridge latest status counts: {bridge['status_counts']}")
    print("Actionable bridge entries:")
    for entry in bridge["actionable"]:
        print(f"- {entry['status']}: {entry['document']} ({entry['path']})")
    print(f"Work item status counts: {work_items['status_counts']}")
    print(f"Work item authorization coverage: {work_items['authorization_status_counts']}")
    print("Release blockers:")
    for blocker in audit["release_blockers"]:
        print(f"- {blocker}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
