"""Implementation for the governed ``gt backlog status`` command.

Authority: bridge/gtkb-discoverability-cli-slice-2-implementation-003.md
(REVISED-1), Codex GO at -004. Source work item: WI-3262 (a member of
PROJECT-GTKB-DETERMINISTIC-SERVICES-001 / -DISCOVERABILITY sub-project).

``gt backlog status`` consolidates the project + work-item rollup that Prime
Builder currently reconstructs by hand with ad-hoc Python every time a session
asks "what is the backlog state?" Per DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE
that recurring reconstruction is the defect this slice removes.

The command is read-only:

* No MemBase writes. Opens ``KnowledgeDB`` for reads only and closes it
  before returning.
* No bridge artifact mutation.
* No schema migration.

Per the GO'd proposal, the base output (no flags) deliberately reports raw
``resolution_status`` counts instead of inventing a terminal/non-terminal
definition. Scanner-backed behaviors are gated behind explicit opt-in flags
(``--with-retire-ready`` and ``--with-verified-coverage``) and carry a
``scanner_caveat`` field that points at the CANONICAL VERIFIED scanner-fix
thread (``gtkb-project-completion-scanner-addressing-thread-fix``), NOT the
withdrawn ``-implementation`` duplicate.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB

# The scanner module lives under ``scripts/`` at the project root, which is
# not on ``sys.path`` when ``groundtruth_kb`` is imported as an installed
# package. Make ``scripts.project_verified_completion_scanner`` importable by
# adding the project root (three parents up from
# ``groundtruth-kb/src/groundtruth_kb/``). The import itself happens lazily
# inside ``build_backlog_status`` only when a scanner-backed flag is set, so
# the base command (no flags) has zero scanner import dependency (proposal
# acceptance test 10).
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


# Canonical scanner-fix thread reference for the ``scanner_caveat`` field.
# Must remain the canonical thread name (NOT the withdrawn ``-implementation``
# duplicate) per the GO'd proposal's F1 correction. Test 7 asserts both that
# the canonical slug is present AND that the withdrawn ``-implementation``
# slug is absent.
_SCANNER_FIX_CANONICAL_THREAD = "gtkb-project-completion-scanner-addressing-thread-fix"
_SCANNER_FIX_VERIFIED_FILE = f"bridge/{_SCANNER_FIX_CANONICAL_THREAD}-017.md"
SCANNER_CAVEAT = (
    "VERIFIED-coverage uses scripts/project_verified_completion_scanner.py, "
    "whose D3+D4 over-broad-citation fix is VERIFIED at bridge thread "
    f"{_SCANNER_FIX_CANONICAL_THREAD} (canonical thread; verdict at "
    f"{_SCANNER_FIX_VERIFIED_FILE}). Coverage is project-scoped and counts "
    "only Work Items covered by that project's implements-linked VERIFIED "
    "threads."
)


@dataclass(frozen=True)
class BacklogStatusRequest:
    """Validated request for one ``gt backlog status`` invocation.

    The dataclass is frozen so the request is a pure value object — callers
    cannot mutate it between the CLI wrapper and the service.
    """

    project: str | None = None
    with_orphans: bool = False
    with_retire_ready: bool = False
    with_verified_coverage: bool = False


def _doubled_prefix_flag(project_id: str) -> bool:
    """Return True iff ``project_id`` matches the phantom doubled-prefix pattern.

    The phantom ids are an artifact of the pre-fix ``_project_id_from_names``
    derivation (WI-3411 / WI-3355). Surfacing them as a flag lets the operator
    see drift without inventing a separate workflow.
    """
    return project_id.startswith("PROJECT-PROJECT-")


def _project_row(db: KnowledgeDB, project: dict[str, Any]) -> dict[str, Any]:
    """Build one project's status row from active memberships."""
    project_id = str(project["id"])
    memberships = db.list_project_work_items(project_id, include_inactive=False)
    breakdown: Counter[str] = Counter()
    work_item_ids: list[str] = []
    for member in memberships:
        wi_id = str(member.get("work_item_id") or "")
        if not wi_id:
            continue
        work_item_ids.append(wi_id)
        breakdown[str(member.get("resolution_status") or "unknown")] += 1

    return {
        "id": project_id,
        "name": str(project.get("name") or ""),
        "status": str(project.get("status") or ""),
        "work_item_count": len(work_item_ids),
        "resolution_status_breakdown": dict(sorted(breakdown.items())),
        "doubled_prefix_flag": _doubled_prefix_flag(project_id),
    }


def _list_orphan_work_items(db: KnowledgeDB) -> list[dict[str, Any]]:
    """Return work items with NO active membership row, across all resolution_status."""
    rows = (
        db._get_conn()
        .execute(
            """
            SELECT w.id           AS id,
                   w.title        AS title,
                   w.resolution_status AS resolution_status,
                   w.project_name AS project_name
              FROM current_work_items w
             WHERE NOT EXISTS (
                       SELECT 1
                         FROM current_project_work_item_memberships m
                        WHERE m.work_item_id = w.id
                          AND lower(m.status) = 'active'
                   )
             ORDER BY w.id
            """
        )
        .fetchall()
    )
    return [
        {
            "id": str(row["id"]),
            "title": str(row["title"] or ""),
            "resolution_status": str(row["resolution_status"] or ""),
            "project_name": str(row["project_name"] or "") if row["project_name"] is not None else None,
        }
        for row in rows
    ]


def _annotate_verified_coverage(
    db: KnowledgeDB,
    project_rows: list[dict[str, Any]],
    verified_by_project: dict[str, set[str]],
) -> None:
    """In-place: add ``verified_bridge_covered`` mapping to each project row."""
    for project_row in project_rows:
        project_id = project_row["id"]
        verified_ids = verified_by_project.get(project_id, set())
        memberships = db.list_project_work_items(project_id, include_inactive=False)
        coverage: dict[str, bool] = {}
        for member in memberships:
            wi_id = str(member.get("work_item_id") or "")
            if not wi_id:
                continue
            coverage[wi_id] = wi_id in verified_ids
        project_row["verified_bridge_covered"] = coverage


def build_backlog_status(config: GTConfig, request: BacklogStatusRequest) -> dict[str, Any]:
    """Build the backlog-status report for one CLI invocation.

    Read-only: opens MemBase, performs only reads, closes it before returning.
    The scanner-backed behaviors lazy-import
    ``scripts.project_verified_completion_scanner`` only when at least one of
    the corresponding flags is set.
    """
    db = KnowledgeDB(config.db_path)
    try:
        all_projects = db.list_projects(include_terminal=True)
        projects = [p for p in all_projects if request.project is None or str(p.get("id")) == request.project]

        project_rows = [_project_row(db, p) for p in projects]

        result: dict[str, Any] = {
            "projects": project_rows,
            "summary": {
                "project_count": len(project_rows),
                "doubled_prefix_project_count": sum(1 for r in project_rows if r["doubled_prefix_flag"]),
                "total_active_memberships": sum(r["work_item_count"] for r in project_rows),
            },
        }

        if request.with_orphans:
            result["orphan_work_items"] = _list_orphan_work_items(db)

        if request.with_retire_ready or request.with_verified_coverage:
            # Lazy-import the scanner ONLY when needed. The base command path
            # (no scanner flags) must not depend on scripts.* — test 10 of the
            # spec-derived verification matrix asserts this contract.
            from scripts.project_verified_completion_scanner import (  # type: ignore  # noqa: PLC0415
                completion_ready,
                verified_work_items_by_project,
            )

            project_root = config.project_root

            if request.with_retire_ready:
                ready = completion_ready(project_root)
                result["retire_ready"] = [r.as_dict() for r in ready]

            if request.with_verified_coverage:
                verified_by_project = verified_work_items_by_project(project_root)
                _annotate_verified_coverage(db, project_rows, verified_by_project)

            result["scanner_caveat"] = SCANNER_CAVEAT
    finally:
        db.close()

    return result
