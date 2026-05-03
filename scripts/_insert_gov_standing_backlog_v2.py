# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""One-shot update of GOV-STANDING-BACKLOG-001 to v2 with formal-artifact-approval packet.

Slice 1 of GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH. Adds DB-backed physical-store pointer
referencing the just-inserted ADR/DCL siblings; preserves v1's verified authority claim.
Owner approval recorded via AskUserQuestion in S327.

Run: python scripts/_insert_gov_standing_backlog_v2.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402

ARTIFACT_ID = "GOV-STANDING-BACKLOG-001"
ARTIFACT_TITLE = "Standing backlog is the durable cross-session work authority"

DESCRIPTION_V2 = """Agent Red and the GT-KB platform must maintain a standing backlog that persists across sessions and records outstanding governance, release-readiness, production-readiness, and GT-KB adoption work. The standing backlog is the durable cross-session queue for work that has been identified but not yet completed, explicitly rejected, superseded, or deferred by owner decision. Future sessions must inspect the standing backlog during startup before selecting new work. Items marked TOP or otherwise owner-prioritized must be considered ahead of discretionary work unless the owner explicitly redirects the session.

## Physical Store (added in v2 per Slice 1 of GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH)

The standing backlog is physically implemented as the `backlog_items` table in `groundtruth.db` (MemBase) per `ADR-STANDING-BACKLOG-DB-AUTHORITY-001`. Schema invariants are machine-checkable per `DCL-STANDING-BACKLOG-DB-SCHEMA-001`. Both sibling specs are at `status=specified` after Slice 1 (this update); they reach `status=verified` after Slice 2 lands the migration in `groundtruth-kb/src/groundtruth_kb/db.py`.

`memory/work_list.md` is retained as a generated read-only view of `current_backlog_items`, rendered by `gt backlog render-markdown` (Slice 3). Doctor check `_check_backlog_authoritative` (Slice 5) flags drift between the markdown view and DB authority. Hand-edits to `memory/work_list.md` are non-authoritative; the DB is the source of truth.

`DCL-STANDING-BACKLOG-SCHEMA-001` (the markdown-grounded predecessor) is preserved historical and marked superseded after `DCL-STANDING-BACKLOG-DB-SCHEMA-001` reaches `implemented`. Authority semantics from `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` are preserved unchanged; that ADR's physical-store choice is superseded by `ADR-STANDING-BACKLOG-DB-AUTHORITY-001`.

## Required Backlog Entry Fields (preserved + extended in v2)

Backlog entries must include enough context for a future harness to continue without relying on conversational memory. The `backlog_items` schema (per `DCL-STANDING-BACKLOG-DB-SCHEMA-001`) provides 24 columns covering:

- **Identity:** id, version, backlog_item_name, subproject_name, supersedes, superseded_by.
- **Scheduling:** implementation_order, status (proposed | active | blocked | in_progress | verified | superseded | deferred).
- **Provenance:** created_at, updated_at, created_by, updated_by, change_reason, source_owner_directive, source_deliberation_query.
- **Linkage:** related_deliberation_ids (snapshot at creation), related_spec_ids_at_creation (historical capture only — see ADR §6 for fresh-discovery semantic), related_bridge_threads, depends_on_backlog_items, blocks_backlog_items.
- **Closure:** description (long-form intent), acceptance_summary, regression_visibility, completion_evidence.

These fields supersede the v1 narrative list (identifier, title, priority, source decision/deliberation reference, required outcome, regression visibility, disposition state) by formalizing them as typed columns rather than prose conventions.

## Spec-Snapshot Discipline (key design constraint, v2)

`related_spec_ids_at_creation` and `related_deliberation_ids` capture the spec/deliberation set known at the moment the backlog item was created. They are NOT exhaustive applicability claims. Implementation proposals derived from a backlog item must run fresh `db.list_specs(...)` and `db.search_deliberations(...)` at proposal time. The bridge-compliance-gate hook (Slice 5 extension) enforces this.
"""

PACKET_PATH = (
    REPO_ROOT
    / ".groundtruth"
    / "formal-artifact-approvals"
    / "2026-05-02-backlog-slice1-gov-update.json"
)


def main() -> int:
    sha = hashlib.sha256(DESCRIPTION_V2.encode("utf-8")).hexdigest()

    packet = {
        "artifact_type": "governance",
        "artifact_id": ARTIFACT_ID,
        "action": "update-version",
        "source_ref": "owner_conversation:2026-05-02-S327-backlog-slice1-gov-update-approved",
        "full_content": DESCRIPTION_V2,
        "full_content_sha256": sha,
        "approval_mode": "approve",
        "presented_to_user": True,
        "transcript_captured": True,
        "explicit_change_request": (
            "Owner approved GOV-STANDING-BACKLOG-001 v2 update as drafted via "
            "AskUserQuestion at S327. Owner answer: 'Approve as drafted (Recommended)'. "
            "v2 preserves v1 authority claim verbatim; adds Physical Store section "
            "pointing at ADR-STANDING-BACKLOG-DB-AUTHORITY-001 and "
            "DCL-STANDING-BACKLOG-DB-SCHEMA-001 (just inserted same Slice 1)."
        ),
        "changed_by": "prime-builder/claude-code",
        "change_reason": (
            "Slice 1 of GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH per bridge "
            "gtkb-gov-backlog-source-of-truth-2026-05-02-006.md (Codex GO); "
            "add DB-backed physical-store pointer; replace prose-field list "
            "with structured 24-column reference; add spec-snapshot-discipline clause."
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
        status="verified",
        changed_by="prime-builder/claude-code",
        change_reason=(
            "v2: add Physical Store section pointing at "
            "ADR-STANDING-BACKLOG-DB-AUTHORITY-001 and "
            "DCL-STANDING-BACKLOG-DB-SCHEMA-001; replace prose-field list with "
            "structured 24-column reference; add spec-snapshot-discipline clause. "
            "Slice 1 of GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH per bridge "
            "gtkb-gov-backlog-source-of-truth-2026-05-02-006.md (Codex GO)."
        ),
        type="governance",
        description=DESCRIPTION_V2,
        tags=[
            "standing-backlog",
            "session-governance",
            "agent-red",
            "groundtruth-kb",
            "gtkb-gov-backlog-source-of-truth",
            "slice1",
            "S327",
        ],
    )
    print(f"insert_spec id={result.get('id')} version={result.get('version')} rowid={result.get('rowid')}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
