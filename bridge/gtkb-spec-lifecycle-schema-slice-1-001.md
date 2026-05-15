NEW

# Implementation Proposal - Spec Lifecycle Schema Slice 1 (additions)

bridge_kind: implementation_proposal
Document: gtkb-spec-lifecycle-schema-slice-1
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/tests/test_db.py", "groundtruth.db"]

## Claim

The parent scoping bridge `gtkb-spec-lifecycle-schema-2026-04-29` is GO at `-004` (scoping approval; follow-on slices must each file their own bridge proposal). This Slice 1 proposal implements the additive schema changes that the parent contract authorizes for first-stage migration:

- New nullable column `implementation_verified_at TEXT` on `specifications` table.
- New nullable column `retired_at TEXT` on `specifications` table.
- New nullable column `parent TEXT` on `specifications` table (Slice 1 keeps it nullable; Slice 1.5 will rebuild with NOT NULL CHECK).
- New `specification_deliberation_sources` table for the deliberation-source relationship.

All additions are nullable in Slice 1; backfill is Slice 4 work.

## In-Root Placement Evidence

All target paths are in-root under `E:\GT-KB`. Bridge file at `E:\GT-KB\bridge\gtkb-spec-lifecycle-schema-slice-1-001.md`. Targets at `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\db.py`, `E:\GT-KB\groundtruth-kb\tests\test_db.py`, `E:\GT-KB\groundtruth.db`. No `applications/` paths.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol observed.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - every governing spec cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `ADR-0001` - MemBase append-only; this slice adds nullable columns + a new relationship table (additive only).
- `GOV-STANDING-BACKLOG-001` - one tracking work_item.
- `GOV-08` - canonical Python API; new columns exposed via `KnowledgeDB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - new columns are governance artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - schema additions are artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - `implementation_verified_at` + `retired_at` are lifecycle triggers.
- `bridge/gtkb-spec-lifecycle-schema-2026-04-29-003.md` - parent operative proposal (REVISED-1 GO'd).
- `bridge/gtkb-spec-lifecycle-schema-2026-04-29-004.md` - Codex GO authorizing follow-on slices.

## Prior Deliberations

- `DELIB-0707` - owner decision that existing specs must be migrated to the enriched schema using implementation as reference.
- `DELIB-0636`, `DELIB-0791`, `DELIB-0808`, `DELIB-1196`, `DELIB-1245`, `DELIB-1403` - lifecycle-schema design history (carried forward from parent).
- 2026-05-14 UTC, S350: owner prompt "Please continue with dora-001b verification, 3 slice-N proposals for scoping GOs, startup-payload-drift bridge proposal" - explicit authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner prompt "Please continue with..." authorizes this slice-1 filing.
- 2026-05-14 UTC, S350: owner prompt "Proceed with all identified work".

No new owner decision required.

## Requirement Sufficiency

Existing requirements sufficient. Operating under parent GO's scoping authority + DELIB-0707 owner decision.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation; creates one tracking work_item. Schema changes are additive (nullable columns + new table); no destructive migration in Slice 1.

## Bridge INDEX Update Evidence (CLAUSE-INDEX-IS-CANONICAL)

This proposal is filed at `bridge/gtkb-spec-lifecycle-schema-slice-1-001.md` with a `Document: gtkb-spec-lifecycle-schema-slice-1` + `NEW:` entry inserted at the top of `bridge/INDEX.md`. The INDEX update is additive; no prior INDEX entry or bridge file is deleted or rewritten. The append-only audit trail at `bridge/INDEX.md` preserves the full version sequence for this thread.

## Bulk-Operations Clause Evidence (CLAUSE-VISIBILITY-BULK-OPS)

This implementation is NOT a bulk operation against the standing backlog. It creates exactly one tracking `work_item` per IP-4. The inventory for this slice is the IP-1 + IP-2 + IP-3 + IP-4 packet enumeration above. The review-packet is this proposal plus the parent thread chain `bridge/gtkb-spec-lifecycle-schema-2026-04-29 -001 through -004`. No formal-artifact-approval packet is required because no protected narrative artifact is edited; the work modifies `groundtruth_kb/db.py` schema + tests + one MemBase WI insert.

## Proposed Scope

### IP-1: Add nullable columns to `specifications` table

In `groundtruth-kb/src/groundtruth_kb/db.py`, update the `specifications` table CREATE statement (around lines 56-74) to include three new nullable columns:
- `implementation_verified_at TEXT` - ISO8601 timestamp when spec moved to verified status; NULL when not yet verified.
- `retired_at TEXT` - ISO8601 timestamp when spec retired; NULL when active.
- `parent TEXT` - one of `gtkb`, `application`, `all`; NULL pending Slice 4 backfill; Slice 1.5 will rebuild with NOT NULL CHECK.

Add migration block in `KnowledgeDB.__init__()` to add columns to existing tables via `ALTER TABLE ... ADD COLUMN` for backward compatibility.

### IP-2: New `specification_deliberation_sources` table

Add table:

```
CREATE TABLE IF NOT EXISTS specification_deliberation_sources (
  rowid INTEGER PRIMARY KEY AUTOINCREMENT,
  specification_id TEXT NOT NULL,
  specification_version INTEGER NOT NULL,
  deliberation_id TEXT NOT NULL,
  relationship TEXT NOT NULL CHECK (relationship IN ('source', 'evidence', 'context')),
  created_at TEXT NOT NULL,
  FOREIGN KEY (specification_id, specification_version) REFERENCES specifications(id, version),
  FOREIGN KEY (deliberation_id) REFERENCES deliberations(id)
);
```

Expose via `KnowledgeDB.link_specification_deliberation(spec_id, spec_version, delib_id, relationship)`.

### IP-3: Tests

In `groundtruth-kb/tests/test_db.py`:
- `test_specifications_table_has_new_lifecycle_columns` - fresh DB schema has the three new columns.
- `test_specifications_alter_table_migration_idempotent` - migration runs cleanly on existing populated DB.
- `test_specification_deliberation_sources_table_exists` - fresh DB has the new table.
- `test_link_specification_deliberation_inserts_row` - canonical API inserts a relationship row.
- `test_populated_fixture_migration_zero_data_loss` - mandatory per parent F1 carry-forward.

### IP-4: Tracking work_item

One `work_items` row: origin=`new`, component=`spec-lifecycle`, source_spec_id=`SPEC-LIFECYCLE-SCHEMA-MIGRATION` (placeholder until ADR/SPEC lands in later slice).

## Specification-Derived Verification Plan

1. `python -m pytest groundtruth-kb/tests/test_db.py -v` - all new tests PASS.
2. `python -m ruff check groundtruth-kb/src/groundtruth_kb/db.py` - zero errors.
3. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-spec-lifecycle-schema-slice-1` - PASS.
4. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-spec-lifecycle-schema-slice-1` - exit 0.
5. MemBase tracking WI inserted per IP-4.

## Risks and Rollback

- **Risk**: ALTER TABLE migration fails on existing DB with unusual state. Mitigation: idempotent migration + populated-fixture test.
- **Risk**: foreign-key constraint on `specifications(id, version)` mismatches existing append-only schema. Mitigation: test schema validation before write.
- Rollback: `git revert` reverts source + tests; ALTER TABLE columns cannot be dropped in SQLite without table rebuild (deferred to Slice 1.5 work).

## Sequenced Dependencies

Slice 1 is foundation for Slice 1.5 (table rebuild with NOT NULL CHECK), Slice 2 (API/gates), Slice 4 (backfill). Per parent constraint: Slice 4 dry-run/backfill work must precede Slice 2 API write-path migration.

## Recommended Commit Type

`feat:` - new schema columns + new relationship table.

## Bridge-Compliance Self-Check

- Non-empty `## Specification Links` flat bullets; no `###` sub-headings inside.
- Non-empty `## Prior Deliberations`.
- Non-empty `## Owner Decisions / Input`.
- target_paths in JSON form; all in-root.
- `## Requirement Sufficiency` one operative state.
- `## Recommended Commit Type` present.
- `## Clause Scope Clarification (Not a Bulk Operation)` present.
- `## In-Root Placement Evidence` present.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
