"""Stage 1 prefix-split detector + safe-merge tool.

Stage 1 of ``PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001`` (WI-4454), chartered
by owner decision ``DELIB-20261667``.

Detects projects whose ids look like ``X`` and ``PROJECT-X`` are both active
(prefix-split): the same canonical workstream has two project rows of distinct
id form, with memberships scattered between them. The canonical form is the
``PROJECT-``-prefixed variant (matches every other GT-KB project id).

Default mode is READ-ONLY: opens ``groundtruth.db`` with a read-only SQLite URI
(``file:...?mode=ro``), emits the plan as deterministic JSON, and mutates
nothing.

``--apply`` requires explicit ``--canonical X --merge-from Y`` (the bare-stem
and PROJECT-prefixed ids of the one pair to merge). It refuses to operate on
any pair not present in the live dry-run's active-BOTH set. The apply steps
run in STRICT ORDER -- (1) any missing canonical-link insertions, then (2)
every non-canonical active-membership deactivation, then (3) retire the
non-canonical project -- so the non-canonical project is never retired while
still carrying active memberships (the structural-defect class Stage 1 closes).

This module is the load-bearing companion to the existing
``gt projects reconcile-doubled-prefix`` CLI (which handles the
``PROJECT-PROJECT-*`` phantom class). Both run only behind owner per-batch
AskUserQuestion per the bounded PAUTH (v4 of
``PAUTH-PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001-...-IMPLEMENTATION-AUTHORIZATION``).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

PROJECT_PREFIX = "PROJECT-"
ACTIVE_STATUS = "active"
SUPERSEDED_STATUS = "superseded"
RETIRED_PROJECT_STATUS = "retired"

# Disposition labels (informational only; no items are flagged for retire by
# this detector -- it operates at the project/membership level).
DEFAULT_DB_PATH = "groundtruth.db"


def _canonical_stem(project_id: str) -> str:
    """Return the canonical stem of a project id by stripping a leading ``PROJECT-``."""
    if project_id.startswith(PROJECT_PREFIX):
        return project_id[len(PROJECT_PREFIX) :]
    return project_id


def _ro_connect(db_path: Path) -> sqlite3.Connection:
    """Open ``db_path`` with a read-only SQLite URI."""
    uri = f"file:{db_path.as_posix()}?mode=ro"
    con = sqlite3.connect(uri, uri=True)
    con.row_factory = sqlite3.Row
    return con


def _project_status(con: sqlite3.Connection, project_id: str) -> str | None:
    row = con.execute("SELECT status FROM current_projects WHERE id = ?", (project_id,)).fetchone()
    return row["status"] if row else None


def _active_memberships(con: sqlite3.Connection, project_id: str) -> list[dict[str, Any]]:
    """Return active memberships for ``project_id``, sorted by work_item_id."""
    rows = con.execute(
        "SELECT id, work_item_id, project_id, status "
        "FROM current_project_work_item_memberships "
        "WHERE project_id = ? AND status = ? "
        "ORDER BY work_item_id",
        (project_id, ACTIVE_STATUS),
    ).fetchall()
    return [dict(r) for r in rows]


def detect(db_path: Path) -> dict[str, Any]:
    """Build the read-only dry-run plan.

    Returns ``{"pairs": [...]}`` where each pair has the three contract fields
    plus the load-bearing ``canonical_id`` and ``non_canonical_id``.
    """
    con = _ro_connect(db_path)
    try:
        rows = con.execute("SELECT id, status FROM current_projects").fetchall()
        # Group active projects by canonical stem.
        by_stem: dict[str, list[str]] = {}
        statuses: dict[str, str] = {}
        for r in rows:
            pid = r["id"]
            statuses[pid] = r["status"]
            if r["status"] == ACTIVE_STATUS:
                by_stem.setdefault(_canonical_stem(pid), []).append(pid)

        pairs: list[dict[str, Any]] = []
        for _stem, ids in sorted(by_stem.items()):
            # A prefix split requires both the PROJECT- form and the bare-stem
            # form to be active under the same stem.
            canonical_id = next((p for p in ids if p.startswith(PROJECT_PREFIX)), None)
            non_canonical_id = next((p for p in ids if not p.startswith(PROJECT_PREFIX)), None)
            if canonical_id is None or non_canonical_id is None:
                continue

            non_can_active = _active_memberships(con, non_canonical_id)
            can_active = _active_memberships(con, canonical_id)
            can_active_wis = {m["work_item_id"] for m in can_active}

            canonical_links_to_create = sorted({m["work_item_id"] for m in non_can_active} - can_active_wis)
            non_canonical_memberships_to_deactivate = [
                {"work_item_id": m["work_item_id"], "membership_id": m["id"]}
                for m in sorted(non_can_active, key=lambda m: m["work_item_id"])
            ]
            non_canonical_project_to_retire = statuses[non_canonical_id] == ACTIVE_STATUS

            pairs.append(
                {
                    "canonical_id": canonical_id,
                    "non_canonical_id": non_canonical_id,
                    "canonical_links_to_create": canonical_links_to_create,
                    "non_canonical_memberships_to_deactivate": non_canonical_memberships_to_deactivate,
                    "non_canonical_project_to_retire": non_canonical_project_to_retire,
                }
            )
        return {"pairs": pairs}
    finally:
        con.close()


def _find_pair(plan: dict[str, Any], canonical_id: str, non_canonical_id: str) -> dict[str, Any] | None:
    for pair in plan["pairs"]:
        if pair["canonical_id"] == canonical_id and pair["non_canonical_id"] == non_canonical_id:
            return pair
    return None


def apply(
    db_path: Path,
    *,
    canonical_id: str,
    non_canonical_id: str,
    auq_id: str,
    changed_by: str,
) -> dict[str, Any]:
    """Execute the strict-order merge for one owner-specified pair.

    Refuses if the pair is not in the live dry-run's active-BOTH set.

    Apply order (load-bearing per the ``-002`` NO-GO P1 fix):
    1. canonical_links_to_create: append active canonical-membership rows for
       any items active on the non-canonical project but missing on the
       canonical project.
    2. non_canonical_memberships_to_deactivate: append non-active
       (``superseded``) successor rows for every active membership on the
       non-canonical project, regardless of whether a canonical link already
       exists.
    3. non_canonical_project_to_retire: retire the non-canonical project ONLY
       AFTER every deactivation in step 2 has been written.

    Idempotent on rerun: each step checks whether its successor row already
    exists; if so the step is a no-op.
    """
    # Import lazily so the read-only default path has no API dependency.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "groundtruth-kb" / "src"))
    from groundtruth_kb.db import KnowledgeDB  # noqa: PLC0415

    plan = detect(db_path)
    pair = _find_pair(plan, canonical_id, non_canonical_id)
    if pair is None:
        raise SystemExit(
            f"refusing apply: ({canonical_id}, {non_canonical_id}) is not in the live active-BOTH dry-run set"
        )

    change_reason = (
        f"Stage 1.B prefix-split merge approved by {auq_id}; "
        f"merging {non_canonical_id} into canonical {canonical_id} per DELIB-20261667."
    )

    db = KnowledgeDB(db_path=db_path)
    result: dict[str, Any] = {
        "canonical_links_created": [],
        "non_canonical_memberships_deactivated": [],
        "non_canonical_project_retired": False,
        "skipped": [],
    }

    # Read current canonical memberships so create-step is idempotent.
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    try:
        existing_canonical_active = {
            row["work_item_id"]
            for row in con.execute(
                "SELECT work_item_id FROM current_project_work_item_memberships WHERE project_id = ? AND status = ?",
                (canonical_id, ACTIVE_STATUS),
            )
        }
        existing_non_canonical_active = {
            row["work_item_id"]
            for row in con.execute(
                "SELECT work_item_id FROM current_project_work_item_memberships WHERE project_id = ? AND status = ?",
                (non_canonical_id, ACTIVE_STATUS),
            )
        }
    finally:
        con.close()

    # Step 1: create any missing canonical links.
    for wi_id in pair["canonical_links_to_create"]:
        if wi_id in existing_canonical_active:
            result["skipped"].append(f"canonical link for {wi_id} already active")
            continue
        db.link_project_work_item(
            project_id=canonical_id,
            work_item_id=wi_id,
            changed_by=changed_by,
            change_reason=change_reason,
            status=ACTIVE_STATUS,
            source="stage-1.B-merge",
        )
        result["canonical_links_created"].append(wi_id)

    # Step 2: deactivate every active non-canonical membership.
    for entry in pair["non_canonical_memberships_to_deactivate"]:
        wi_id = entry["work_item_id"]
        if wi_id not in existing_non_canonical_active:
            result["skipped"].append(f"non-canonical membership for {wi_id} already non-active")
            continue
        db.link_project_work_item(
            project_id=non_canonical_id,
            work_item_id=wi_id,
            changed_by=changed_by,
            change_reason=change_reason,
            status=SUPERSEDED_STATUS,
            source="stage-1.B-merge",
        )
        result["non_canonical_memberships_deactivated"].append(wi_id)

    # Step 3: retire the non-canonical project AFTER all deactivations are done.
    # Refuse to retire if any non-canonical active memberships still remain
    # (defensive double-check; should be impossible after step 2 completes).
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    try:
        remaining = con.execute(
            "SELECT COUNT(*) AS n FROM current_project_work_item_memberships WHERE project_id = ? AND status = ?",
            (non_canonical_id, ACTIVE_STATUS),
        ).fetchone()["n"]
    finally:
        con.close()
    if remaining:
        raise SystemExit(
            f"refusing retire: {non_canonical_id} still has {remaining} active memberships after deactivation step"
        )

    if (
        pair["non_canonical_project_to_retire"]
        and _project_status(_ro_connect(db_path), non_canonical_id) == ACTIVE_STATUS
    ):
        from groundtruth_kb.project.lifecycle import ProjectLifecycleService  # noqa: PLC0415

        service = ProjectLifecycleService(db)
        service.retire_project(
            project_id=non_canonical_id,
            changed_by=changed_by,
            change_reason=change_reason,
        )
        result["non_canonical_project_retired"] = True
    else:
        result["skipped"].append(f"{non_canonical_id} already retired")

    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="prefix_split_detector",
        description="Detect prefix-split active-BOTH project pairs (read-only by default).",
    )
    parser.add_argument(
        "--db",
        default=DEFAULT_DB_PATH,
        help="Path to groundtruth.db (default: ./groundtruth.db)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Execute the merge for the owner-specified pair (requires --canonical, --merge-from, --auq-id).",
    )
    parser.add_argument("--canonical", help="Canonical (PROJECT-prefixed) project id.")
    parser.add_argument(
        "--merge-from", dest="merge_from", help="Non-canonical (bare-stem) project id to merge into the canonical."
    )
    parser.add_argument(
        "--auq-id", dest="auq_id", help="Owner AskUserQuestion id authorising this batch (required with --apply)."
    )
    parser.add_argument(
        "--changed-by",
        default="prime-builder/claude",
        help="changed_by attribution for the mutation log (default: prime-builder/claude).",
    )
    args = parser.parse_args(argv)

    db_path = Path(args.db)

    if not args.apply:
        plan = detect(db_path)
        print(json.dumps(plan, indent=2, sort_keys=True))
        return 0

    if not args.canonical or not args.merge_from:
        raise SystemExit("--apply requires owner to specify the pair: --canonical X --merge-from Y")
    if not args.auq_id:
        raise SystemExit("--apply requires --auq-id citing the owner AskUserQuestion that approved this batch")

    result = apply(
        db_path,
        canonical_id=args.canonical,
        non_canonical_id=args.merge_from,
        auq_id=args.auq_id,
        changed_by=args.changed_by,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
