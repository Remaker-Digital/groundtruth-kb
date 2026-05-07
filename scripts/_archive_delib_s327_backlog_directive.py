# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Archive DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE per Slice 1 of
GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH. Links to ADR/DCL/GOV-update inserted same Slice 1.

Run: python scripts/_archive_delib_s327_backlog_directive.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from scripts._kb_attribution import resolve_changed_by  # noqa: E402

DELIB_ID = "DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE"

CONTENT = """## Owner directive (S327, first turn) — verbatim:

> The "backlog" is not adequately formal. The backlog should be implemented as a source-of-truth database table, with a defined schema that contains information about: the unique name of the backlog item, the unique name of the sub-project it belongs to, the date/time it was created, the date/time it was last updated, the long-form textual description of the work item's relevance and intent, the related deliberations (deliberation archive query), the related specifications (those known at the time the backlog item was created, not necessarily all the specifications which apply when the implementation proposal is created/reviewed), implementation order priority (all backlog items are implemented sequentially, so the priority is the presumed sequential position of the implementation in the continuing series that is the backlog), and any other attributes which GTKB requires (you decide).
>
> Please propose a new backlog item to clarify and enhance the backlog with a schema update and simplified, track-able use of the backlog that prevents fragmentation or loss of backlog items over time.

## Owner refinement (S327, second turn) — verbatim:

> Proposed new backlog item:
>
> GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH
> Status: proposed; owner-directed; not yet filed as bridge implementation proposal
>
> Priority / implementation order: high, immediately after the current GTKB-ISOLATION critical path unless owner promotes it above isolation. This should supersede the current markdown-linter direction in GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1, not create a parallel backlog-governance track.
>
> Intent: Replace memory/work_list.md as the canonical backlog source of truth with a structured, append-only/versioned MemBase-backed backlog table. Markdown backlog views may remain, but only as generated views or temporary compatibility surfaces. The backlog must become a durable, queryable, ordered implementation queue so items cannot fragment across markdown prose, bridge files, MemBase work items, snapshots, and dashboard reports.
>
> Required schema direction: Add a canonical backlog_items table with at least: id, version, backlog_item_name, subproject_name, implementation_order, status, created_at, updated_at, created_by, updated_by, description, source_owner_directive, source_deliberation_query, related_deliberation_ids, related_spec_ids_at_creation, related_bridge_threads, depends_on_backlog_items, blocks_backlog_items, acceptance_summary, regression_visibility, completion_evidence, supersedes, superseded_by, change_reason.
>
> Key design constraint: related_spec_ids_at_creation is a historical capture field, not an exhaustive applicability claim. Implementation proposals and reviews must still perform fresh spec/deliberation discovery when the item is actually worked.
>
> Required outcome: Implement backlog creation, update, reorder, list, and generated-view commands in GT-KB; migrate current actionable memory/work_list.md rows into the new table; update startup, dashboard, bridge citation checks, harvest audits, and doctor checks to read from the table; make manual markdown backlog edits non-authoritative or flagged as drift.
>
> Regression visibility: Tests must prove unique backlog names, unique subproject names where applicable, stable append-only version history, deterministic implementation ordering, no duplicate active item names, no lost migrated rows, generated markdown parity, dashboard visibility, and doctor failure when backlog state exists only in markdown.
>
> Next step: File bridge proposal bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-001.md with this item as the scope, explicitly superseding or absorbing the existing backlog-discipline linter work.

## Resolution

Owner-approved Slice 1 governance artifacts (formal-artifact-approval packets at `.groundtruth/formal-artifact-approvals/2026-05-02-backlog-slice1-{adr,dcl,gov-update}.json`):

- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v1 (status=specified) — physical-store decision: backlog_items table in groundtruth.db with append-only triggers + current_backlog_items view.
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v1 (status=specified, 10 grep assertions) — machine-checkable schema constraint sibling.
- `GOV-STANDING-BACKLOG-001` v2 (status=verified) — adds Physical Store section pointing at new ADR/DCL; replaces v1 prose-field list with structured 24-column reference; adds spec-snapshot-discipline clause.

Approval cycle: scoping bridge `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-001.md` (NEW) → `-002` (NO-GO) → `-003` (REVISED-1) → `-004` (NO-GO) → `-005` (REVISED-2) → `-006` (Codex GO authorizing Slice 1). Each AskUserQuestion approval recorded in S327 transcript.

## Sequencing

Slice 1 (this DELIB + ADR + DCL + GOV update) closes pre-implementation governance work. Slices 2-7 implement DB migration, CLI, render generator, migration tooling, and integration touch-points per the scoping proposal §"Sequencing" (`bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-005.md`).

## Sibling DELIBs (S327 same session)

- `DELIB-S327-TERM-PRIMER-STARTUP-OWNER-DIRECTIVE` (parallel sibling; pending archival via primer Slice 1 close).
- `DELIB-S327-TERM-DISAMBIGUATION-MECHANICAL-OWNER-DIRECTIVE` (parallel sibling; pending archival via disambiguation Slice 1 close).
"""

SUMMARY = (
    "S327 owner directive (two turns) requesting standing-backlog formalization as "
    "DB-backed source-of-truth table with 24-column schema, supersession of "
    "GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1 markdown-linter direction, and key design "
    "constraint that related_spec_ids_at_creation is historical capture (fresh "
    "discovery still required at implementation time). Resolved Slice 1 via "
    "ADR-STANDING-BACKLOG-DB-AUTHORITY-001 v1 + DCL-STANDING-BACKLOG-DB-SCHEMA-001 v1 + "
    "GOV-STANDING-BACKLOG-001 v2 update."
)


def main() -> int:
    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")

    result = db.insert_deliberation(
        id=DELIB_ID,
        source_type="owner_conversation",
        title="S327 owner directive: formalize standing backlog as DB-backed source-of-truth",
        summary=SUMMARY,
        content=CONTENT,
        changed_by=resolve_changed_by(),
        change_reason=(
            "Archive S327 owner directive driving GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH. "
            "Slice 1 governance artifacts inserted same session: ADR/DCL/GOV-update."
        ),
        outcome="owner_decision",
        session_id="S327",
        source_ref="owner_conversation:2026-05-02-S327-backlog-source-of-truth-directive",
    )
    delib_id = result.get('id') if result else DELIB_ID
    print(f"insert_deliberation id={delib_id} version={result.get('version') if result else '?'}", flush=True)

    # Link DELIB to the three Slice 1 specs.
    for spec_id in (
        "ADR-STANDING-BACKLOG-DB-AUTHORITY-001",
        "DCL-STANDING-BACKLOG-DB-SCHEMA-001",
        "GOV-STANDING-BACKLOG-001",
    ):
        db.link_deliberation_spec(deliberation_id=delib_id, spec_id=spec_id, role="motivation")
        print(f"  linked → {spec_id}", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
