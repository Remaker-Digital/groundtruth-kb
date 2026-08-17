#!/usr/bin/env python3
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-6618 census and one-current-per-project collapse.

Read-only census by default. ``--apply`` writes append-only superseded and
current authorization rows through ``KnowledgeDB.insert_project_authorization``.

Usage:
    python scripts/pauth_one_current_per_project.py --census
    python scripts/pauth_one_current_per_project.py --dry-run
    python scripts/pauth_one_current_per_project.py --apply --changed-by prime-builder/cursor
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from groundtruth_kb.project.authorization_collapse import (  # noqa: E402
    CHANGE_REASON,
    census_active_authorizations,
    collapse_all,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--census", action="store_true", help="Print the live C1/C2 census and exit.")
    parser.add_argument("--dry-run", action="store_true", help="Plan the collapse without writing.")
    parser.add_argument("--apply", action="store_true", help="Write the append-only collapse.")
    parser.add_argument("--changed-by", default="prime-builder/cursor")
    parser.add_argument("--change-reason", default=CHANGE_REASON)
    parser.add_argument("--db-path", type=Path, default=None)
    args = parser.parse_args(argv)
    if not args.census and not args.dry_run and not args.apply:
        args.census = True
    db_path = args.db_path or (PROJECT_ROOT / "groundtruth.db")
    db = KnowledgeDB(db_path)
    try:
        if args.census and not args.dry_run and not args.apply:
            payload = census_active_authorizations(db)
            payload.pop("by_project", None)
            json.dump(payload, sys.stdout, indent=2, sort_keys=True)
            sys.stdout.write("\n")
            return 0
        result = collapse_all(
            db,
            changed_by=args.changed_by,
            change_reason=args.change_reason,
            dry_run=not args.apply,
        )
        json.dump(
            {
                "dry_run": result["dry_run"],
                "before": result["before"],
                "after": result["after"],
                "errors": result["errors"],
                "left_unauthorized": result["left_unauthorized"],
                "c1_fail_closed": result["c1_fail_closed"],
                "c2_fail_closed": result["c2_fail_closed"],
                "project_count": len(result["projects"]),
            },
            sys.stdout,
            indent=2,
            sort_keys=True,
        )
        sys.stdout.write("\n")
        return 1 if result["errors"] else 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
