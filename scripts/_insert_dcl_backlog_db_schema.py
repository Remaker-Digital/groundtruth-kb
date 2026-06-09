# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""One-shot insert of DCL-STANDING-BACKLOG-DB-SCHEMA-001 with formal-artifact-approval packet.

Sibling to ADR-STANDING-BACKLOG-DB-AUTHORITY-001. Slice 1 of GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH.
Owner approval recorded via AskUserQuestion in S327.

Run: python scripts/_insert_dcl_backlog_db_schema.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402

ARTIFACT_ID = "DCL-STANDING-BACKLOG-DB-SCHEMA-001"
ARTIFACT_TITLE = "Standing Backlog DB Schema Constraint"

DESCRIPTION = """## Constraint Statement

The standing backlog physical store, as decided in `ADR-STANDING-BACKLOG-DB-AUTHORITY-001`, must conform to the following schema invariants in `groundtruth.db` and its DDL definition site:

1. **Table existence.** A table named `backlog_items` exists.
2. **Composite primary key for append-only.** `PRIMARY KEY (id, version)` — no UPDATE-in-place; mutations are new version inserts.
3. **24 owner-specified columns present.** id, version, backlog_item_name, subproject_name, implementation_order, status, created_at, updated_at, created_by, updated_by, description, source_owner_directive, source_deliberation_query, related_deliberation_ids, related_spec_ids_at_creation, related_bridge_threads, depends_on_backlog_items, blocks_backlog_items, acceptance_summary, regression_visibility, completion_evidence, supersedes, superseded_by, change_reason.
4. **Append-only triggers.** `BEFORE UPDATE` trigger named `backlog_items_no_update` and `BEFORE DELETE` trigger named `backlog_items_no_delete`, each emitting `RAISE(ABORT, ...)`. INSERT remains permitted.
5. **Current-state view.** `current_backlog_items` view defined as max-version-per-id projection over `backlog_items`.
6. **NOT NULL columns.** id, version, backlog_item_name, subproject_name, implementation_order, status, created_at, updated_at, created_by, updated_by, description, change_reason are NOT NULL. Other columns are nullable.
7. **Status enum domain.** `status` values are restricted to: proposed, active, blocked, in_progress, verified, superseded, deferred. Enforced at the service layer (or via CHECK constraint when SQLite version permits).

## Rationale

This DCL captures the machine-checkable shape of `ADR-STANDING-BACKLOG-DB-AUTHORITY-001`'s decision. The ADR states the *why*; this DCL states the *what-must-be-true* in code. Together they form the GOV-20 ADR/DCL pairing.

The 10 grep assertions in the `assertions` field cover the most diagnostic invariants: table+PK (append-only foundation), both triggers (enforcement), the view (current-state surface), and 4 non-trivial owner-specified columns (`backlog_item_name`, `subproject_name`, `implementation_order`, plus the two columns Codex's NO-GOs explicitly drove — `source_deliberation_query` from `-002.md` F4 and `related_spec_ids_at_creation` from owner's snapshot-semantics directive). Other columns are not separately asserted to keep the DCL tractable; full-column coverage is verified by Slice 2's pytest suite.

## Replaces

`DCL-STANDING-BACKLOG-SCHEMA-001` (markdown-grounded predecessor; preserved historical, marked superseded after this DCL reaches `implemented`).

## Related specs

- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` — parent architecture decision (sibling, inserted v1 same Slice 1).
- `GOV-STANDING-BACKLOG-001` — governance contract (updated by sibling artifact this Slice 1).
- `DCL-STANDING-BACKLOG-SCHEMA-001` — predecessor; replaced.
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-006.md` — Codex GO authorizing this Slice 1.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval contract.

## Lifecycle Note

Assertions will fail at `specified` status (the migration hasn't shipped) and pass at `implemented` after Slice 2 lands the DDL in `groundtruth-kb/src/groundtruth_kb/db.py`. Per GOV-04 (Maturation), this is normal lifecycle behavior, not a defect.
"""

ASSERTIONS = [
    {
        "type": "grep",
        "description": "backlog_items table created in DDL",
        "pattern": "CREATE TABLE.*backlog_items",
        "file": "groundtruth-kb/src/groundtruth_kb/db.py",
    },
    {
        "type": "grep",
        "description": "Composite PK (id, version) for append-only",
        "pattern": r"PRIMARY KEY \(id, version\)",
        "file": "groundtruth-kb/src/groundtruth_kb/db.py",
    },
    {
        "type": "grep",
        "description": "backlog_items_no_update trigger defined",
        "pattern": "backlog_items_no_update",
        "file": "groundtruth-kb/src/groundtruth_kb/db.py",
    },
    {
        "type": "grep",
        "description": "backlog_items_no_delete trigger defined",
        "pattern": "backlog_items_no_delete",
        "file": "groundtruth-kb/src/groundtruth_kb/db.py",
    },
    {
        "type": "grep",
        "description": "current_backlog_items view defined",
        "pattern": "CREATE VIEW.*current_backlog_items",
        "file": "groundtruth-kb/src/groundtruth_kb/db.py",
    },
    {
        "type": "grep",
        "description": "backlog_item_name column present",
        "pattern": "backlog_item_name",
        "file": "groundtruth-kb/src/groundtruth_kb/db.py",
    },
    {
        "type": "grep",
        "description": "subproject_name column present",
        "pattern": "subproject_name",
        "file": "groundtruth-kb/src/groundtruth_kb/db.py",
    },
    {
        "type": "grep",
        "description": "implementation_order column present",
        "pattern": "implementation_order",
        "file": "groundtruth-kb/src/groundtruth_kb/db.py",
    },
    {
        "type": "grep",
        "description": "source_deliberation_query column present (Codex F4 of -002)",
        "pattern": "source_deliberation_query",
        "file": "groundtruth-kb/src/groundtruth_kb/db.py",
    },
    {
        "type": "grep",
        "description": "related_spec_ids_at_creation column present (owner snapshot-semantics directive)",
        "pattern": "related_spec_ids_at_creation",
        "file": "groundtruth-kb/src/groundtruth_kb/db.py",
    },
]

PACKET_PATH = REPO_ROOT / ".groundtruth" / "formal-artifact-approvals" / "2026-05-02-backlog-slice1-dcl.json"


def main() -> int:
    sha = hashlib.sha256(DESCRIPTION.encode("utf-8")).hexdigest()

    packet = {
        "artifact_type": "design_constraint",
        "artifact_id": ARTIFACT_ID,
        "action": "insert",
        "source_ref": "owner_conversation:2026-05-02-S327-backlog-slice1-dcl-approved",
        "full_content": DESCRIPTION,
        "full_content_sha256": sha,
        "approval_mode": "approve",
        "presented_to_user": True,
        "transcript_captured": True,
        "explicit_change_request": (
            "Owner approved DCL-STANDING-BACKLOG-DB-SCHEMA-001 as drafted via "
            "AskUserQuestion at S327. Owner answer: 'Approve as drafted (Recommended)'."
        ),
        "changed_by": "prime-builder/claude-code",
        "change_reason": (
            "Slice 1 of GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH per bridge "
            "gtkb-gov-backlog-source-of-truth-2026-05-02-006.md (Codex GO); "
            "machine-checkable DB-schema constraint sibling to "
            "ADR-STANDING-BACKLOG-DB-AUTHORITY-001."
        ),
        "approved_by": "owner",
        "acknowledged_by": "owner",
    }

    PACKET_PATH.parent.mkdir(parents=True, exist_ok=True)
    PACKET_PATH.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(f"Packet written: {PACKET_PATH}", flush=True)
    print(f"  SHA256: {sha}", flush=True)

    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")
    result = db.insert_spec(
        id=ARTIFACT_ID,
        title=ARTIFACT_TITLE,
        status="specified",
        changed_by="prime-builder/claude-code",
        change_reason=(
            "Slice 1 of GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH per bridge "
            "gtkb-gov-backlog-source-of-truth-2026-05-02-006.md (Codex GO); "
            "machine-checkable DB-schema constraint."
        ),
        type="design_constraint",
        description=DESCRIPTION,
        assertions=ASSERTIONS,
        validate_assertions=False,
        tags=[
            "gtkb-gov-backlog-source-of-truth",
            "slice1",
            "S327",
            "standing-backlog",
            "db-schema",
        ],
    )
    print(f"insert_spec id={result.get('id')} version={result.get('version')} rowid={result.get('rowid')}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
