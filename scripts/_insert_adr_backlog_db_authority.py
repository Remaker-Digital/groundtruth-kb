# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""One-shot insert of ADR-STANDING-BACKLOG-DB-AUTHORITY-001 with formal-artifact-approval packet.

Slice 1 of GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH per Codex GO at
bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-006.md.
Owner approval recorded via AskUserQuestion in S327; this script writes the
packet that gates the KB insert per GOV-ARTIFACT-APPROVAL-001.

Run: python scripts/_insert_adr_backlog_db_authority.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402

ARTIFACT_ID = "ADR-STANDING-BACKLOG-DB-AUTHORITY-001"
ARTIFACT_TITLE = "DB-Backed Standing Backlog Authority"

DESCRIPTION = """## Context

DELIB-0838 established the standing backlog as a governed cross-session work authority. That authority was formalized in `GOV-STANDING-BACKLOG-001`, `PB-STANDING-BACKLOG-CONTINUITY-001`, `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001`, and `DCL-STANDING-BACKLOG-SCHEMA-001`. The physical implementation chosen at the time was `memory/work_list.md` (a hand-maintained markdown table).

S327 owner observation identified four failure modes of the markdown implementation: (1) priority overloading ("TOP" used inconsistently across ~10 historical entries; file-wide caveat acknowledges only the 5-row header is trustworthy), (2) drift risk from hand-edits with prose-encoded relations, (3) no structured spec/deliberation linkage, (4) loss-prone (no append-only invariant). The empirical drift accumulated across 30+ sessions; see `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT` for the broader fragmentation finding.

## Decision

The standing backlog is physically implemented as the `backlog_items` table in `groundtruth.db` (MemBase). Specifically:

1. **Schema:** 24 owner-specified columns (id, version, backlog_item_name, subproject_name, implementation_order, status, created_at, updated_at, created_by, updated_by, description, source_owner_directive, source_deliberation_query, related_deliberation_ids, related_spec_ids_at_creation, related_bridge_threads, depends_on_backlog_items, blocks_backlog_items, acceptance_summary, regression_visibility, completion_evidence, supersedes, superseded_by, change_reason). Schema details in sibling `DCL-STANDING-BACKLOG-DB-SCHEMA-001`.

2. **Append-only enforcement:** SQLite `BEFORE UPDATE` and `BEFORE DELETE` triggers with `RAISE(ABORT, ...)` reject raw SQL mutations. Append style works because INSERT remains allowed.

3. **Current state surface:** `current_backlog_items` view (max-version-per-id) provides the canonical "what is the backlog right now" query. Service-layer reorder operations use atomic transactions; current-row uniqueness on `implementation_order` is enforced via service-layer SELECT-validation against the view, not base-table UNIQUE.

4. **Authority preservation:** Authority semantics from `DELIB-0838`, `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001`, `GOV-STANDING-BACKLOG-001`, and `PB-STANDING-BACKLOG-CONTINUITY-001` are preserved. This ADR changes the physical store, not the authority.

5. **Markdown view:** `memory/work_list.md` becomes a generated read-only view of `current_backlog_items` rendered by `gt backlog render-markdown`. Doctor check `_check_backlog_authoritative` (Slice 5) flags drift when the file diverges from DB state.

6. **Spec snapshot semantics (key design constraint):** `related_spec_ids_at_creation` is historical capture only. Implementation proposals derived from a backlog item must run fresh `db.list_specs(...)` and `db.search_deliberations(...)` at proposal time, enforced by the bridge-compliance-gate hook (Slice 5 extension).

7. **Authority relationship to `work_items`:** `work_items` retains work-record authority (lifecycle, origin, component, stage). `backlog_items` references work items indirectly via `related_bridge_threads`. A backlog item may exist before any work item is decomposed; "done" is acceptance_summary satisfaction, typically aligned with bridge VERIFIED.

## Consequences

**Positive:**
- Queryable backlog state via SQL/CLI (`gt backlog list/show ...`).
- Append-only history per CLAUDE.md "Artifacts and Change Control" convention.
- Structured spec/deliberation/bridge-thread linkage replaces prose citations.
- Doctor-checkable authority: `_check_backlog_authoritative` flags drift between markdown render and DB state.
- Aligns with `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — markdown maintenance becomes deterministic generation.
- Fragmentation prevention: backlog state lives in one authoritative store, not spread across markdown prose, bridge files, and dashboard reports.

**Negative:**
- One-time migration cost (Slice 4) — ~26 active markdown rows + completed section + standing-governance items must be converted to DB rows with stable BL-IDs.
- Requires new CLI tooling (`gt backlog ...`) for any backlog mutation (Slices 2-3).
- Successor governance docs (this ADR + sibling DCL + updated GOV) require formal-artifact-approval packets per `GOV-ARTIFACT-APPROVAL-001`.
- SQLite triggers must persist through `gt db snapshot` / `VACUUM INTO`; verified by T6b in Slice 2.

## Failed approaches

- **Hand-maintained markdown table** (`memory/work_list.md` current state). Failed because: priority overloading, drift across sessions, no structured relations, no append-only invariant. Empirical evidence: file-wide caveat lines 63-67 acknowledges "TOP" overloaded across ~10 entries; only the 5-row header is trustworthy. Source: S327 owner observation.
- **Markdown-linter approach** (`GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1`, never shipped). Failed because: lints validate format but cannot address the underlying physical-store problem; structural fragmentation persists regardless of formatting consistency. Superseded by this ADR per S327 owner directive.

## Rejected alternatives

- **Extend `work_items` table with backlog scheduling fields.** Rejected because: conflates work-record authority with scheduling/provenance authority. `work_items` lifecycle is mature (origin/component/stage); adding queue ordering, supersession chains, and DA-query provenance would expand its surface and make either concern harder to reason about. See sibling scoping bridge §"Authority Model" (`bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-005.md`).
- **JSON arrays for all relational columns.** Rejected directionally per Codex `-002.md` F1 (JSON arrays lose queryability without `json_each()` virtual tables). This ADR ships JSON arrays for `related_*` columns as Phase 1; flags join-table evolution as a future enhancement when query patterns demand it. The 24-column owner-specified schema is the canonical baseline; future extensions add columns/tables, never remove.
- **Strict total-order priority with `UNIQUE(implementation_order)` at base-table level.** Rejected per Codex `-004.md` F3: incompatible with append-only versioning (historical rows would collide with current rows after reprioritization). Replaced with view-level uniqueness + service-layer enforcement.

## Related specs

- `DELIB-0838` — parent owner decision establishing standing backlog as governed work authority. Preserved.
- `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` — prior authority decision. Preserved authority semantics; superseded only on physical-store choice.
- `GOV-STANDING-BACKLOG-001` — governance contract. Updated by sibling artifact in this Slice 1 to point at DB-backed authority.
- `PB-STANDING-BACKLOG-CONTINUITY-001` — Prime Builder continuity contract. Preserved.
- `DCL-STANDING-BACKLOG-SCHEMA-001` — prior markdown-grounded schema constraint. Replaced by sibling `DCL-STANDING-BACKLOG-DB-SCHEMA-001` filed in this Slice 1.
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` — successor machine-checkable schema constraint (sibling artifact, this Slice 1).
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval contract under which this ADR is filed.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` — direct motivation; archival pending Slice 1 close.
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-006.md` — Codex GO authorizing this Slice 1.
"""

PACKET_PATH = (
    REPO_ROOT
    / ".groundtruth"
    / "formal-artifact-approvals"
    / "2026-05-02-backlog-slice1-adr.json"
)


def main() -> int:
    sha = hashlib.sha256(DESCRIPTION.encode("utf-8")).hexdigest()

    packet = {
        "artifact_type": "architecture_decision",
        "artifact_id": ARTIFACT_ID,
        "action": "insert",
        "source_ref": "owner_conversation:2026-05-02-S327-backlog-slice1-adr-approved",
        "full_content": DESCRIPTION,
        "full_content_sha256": sha,
        "approval_mode": "approve",
        "presented_to_user": True,
        "transcript_captured": True,
        "explicit_change_request": (
            "Owner approved ADR-STANDING-BACKLOG-DB-AUTHORITY-001 as drafted via "
            "AskUserQuestion at S327. Owner answer: 'Approve as drafted (Recommended)'."
        ),
        "changed_by": "prime-builder/claude-code",
        "change_reason": (
            "Slice 1 of GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH per bridge "
            "gtkb-gov-backlog-source-of-truth-2026-05-02-006.md (Codex GO); "
            "codify DB-backed standing backlog authority decision."
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
            "gtkb-gov-backlog-source-of-truth-2026-05-02-006.md (Codex GO)."
        ),
        type="architecture_decision",
        description=DESCRIPTION,
        tags=[
            "gtkb-gov-backlog-source-of-truth",
            "slice1",
            "S327",
            "standing-backlog",
            "db-authority",
        ],
    )
    print(f"insert_spec result: {result}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
