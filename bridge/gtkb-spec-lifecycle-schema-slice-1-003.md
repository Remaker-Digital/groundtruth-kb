REVISED

# Implementation Proposal - Spec Lifecycle Schema Slice 1 (additions) - REVISED-1

bridge_kind: prime_proposal
Document: gtkb-spec-lifecycle-schema-slice-1
Version: 003
Responds to: bridge/gtkb-spec-lifecycle-schema-slice-1-002.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/tests/test_db.py", "groundtruth-kb/tests/fixtures/spec_lifecycle_slice1_populated_fixture.json", "groundtruth.db"]

This REVISED-1 addresses the NO-GO at `bridge/gtkb-spec-lifecycle-schema-slice-1-002.md`:

- F1 (P1) - Source-link table/API contract drifts from parent GO -> closed by adopting the parent contract verbatim (column names `spec_id`/`spec_version`/`source_role`/`added_at`/`added_by`, unique constraint, API name `link_spec_deliberation_source`).
- F2 (P2) - Tracking work-item insertion not fully verifiable -> closed by specifying the exact row (id, title, status, stage, changed_by, change_reason) plus a read-back assertion test.

## Claim

The parent scoping bridge `gtkb-spec-lifecycle-schema-2026-04-29` is GO at `-004` (scoping approval; follow-on slices each require their own bridge proposal). This Slice 1 implements the additive schema changes the parent contract authorizes, using the parent's exact field and method names:

- New nullable column `implementation_verified_at TEXT` on `specifications`.
- New nullable column `retired_at TEXT` on `specifications`.
- New nullable column `parent TEXT` on `specifications` (Slice 1.5 will rebuild with NOT NULL CHECK after Slice 4 backfill).
- New `specification_deliberation_sources` table with the parent-approved shape.
- New API method `KnowledgeDB.link_spec_deliberation_source(...)`.

All additions are nullable in Slice 1; backfill is Slice 4 work; NOT NULL enforcement is Slice 1.5 work; API write-path gates are Slice 2 work.

## In-Root Placement Evidence

All target paths are in-root under `E:\GT-KB`. Bridge file at `E:\GT-KB\bridge\gtkb-spec-lifecycle-schema-slice-1-003.md`. Targets at `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\db.py`, `E:\GT-KB\groundtruth-kb\tests\test_db.py`, `E:\GT-KB\groundtruth-kb\tests\fixtures\spec_lifecycle_slice1_populated_fixture.json`, `E:\GT-KB\groundtruth.db`. No `applications/` paths. ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol observed; `bridge/INDEX.md` updated to insert the REVISED-1 entry at the top of this thread's version list; no prior version deletion or rewrite.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root paths only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - every governing spec cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping in `## Specification-Derived Verification Plan`.
- `ADR-0001` - MemBase append-only versioning; this slice adds nullable columns + a new relationship table (additive only; no destructive change to existing rows).
- `GOV-STANDING-BACKLOG-001` - one tracking work_item; explicit row fields per CLAUSE-VISIBILITY-BULK-OPS.
- `GOV-08` - canonical Python API; new method exposed via `KnowledgeDB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - new schema columns and new relationship table are governance artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - schema additions are durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - `implementation_verified_at` + `retired_at` materialize lifecycle triggers.
- `bridge/gtkb-spec-lifecycle-schema-2026-04-29-003.md` - parent operative proposal (REVISED-1, GO'd at -004); contract source for table/API names in IP-2.
- `bridge/gtkb-spec-lifecycle-schema-2026-04-29-004.md` - parent GO authorizing follow-on slice implementation.
- `bridge/gtkb-spec-lifecycle-schema-slice-1-002.md` - NO-GO under remediation.

## Prior Deliberations

- `DELIB-0707` - owner decision that existing specs must be migrated to the enriched schema using implementation as reference; makes deterministic backfill/provenance evidence mandatory for later slices and constrains Slice 1 not to leak a different vocabulary.
- `DELIB-1852` - parent scoping GO (REVISED-1). Permissive for follow-on slice proposals only; does NOT pre-approve implementation details that diverge from the operative parent contract. Cited by NO-GO `-002` F1.
- `DELIB-1853` - prior NO-GO on the lifecycle-schema program (closed three blockers); the revised parent contract must be preserved precisely.
- `DELIB-0636`, `DELIB-0791`, `DELIB-0808`, `DELIB-1196`, `DELIB-1245`, `DELIB-1403` - lifecycle-schema design history carried forward from parent.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner prompt "Please continue with dora-001b verification, 3 slice-N proposals for scoping GOs, startup-payload-drift bridge proposal" - explicit authorization to file slice-1 (this REVISED-1 is the F1/F2 remediation of that filing).
- 2026-05-14 UTC, S350: owner AskUserQuestion selection "Parallel research + serialized Writes now (Recommended)" - authorizes parallel research drafting (this proposal) with serialized Write of the operative file.
- 2026-05-14 UTC, S350: owner prompt "Proceed with all identified work" - background authorization for the slice program; no new owner decision is required for this REVISED-1 because it adopts the parent contract rather than amending it.

No new owner decision required by this REVISED-1. The fix path is "adopt parent verbatim," which does not narrow or expand parent scope.

## Requirement Sufficiency

Existing requirements sufficient. Operating under parent GO's scoping authority (`bridge/gtkb-spec-lifecycle-schema-2026-04-29-004.md`) plus DELIB-0707 owner decision. No new requirements introduced; the REVISED-1 corrects field/method names to match the operative parent contract.

## Clause Scope Clarification (Not a Bulk Operation)

This implementation is NOT a bulk operation against the standing backlog. CLAUSE-VISIBILITY-BULK-OPS evidence: exactly one tracking `work_item` is inserted via singleton MemBase insertion (IP-4), with exact fields enumerated below. The review-packet inventory is IP-1 + IP-2 + IP-3 + IP-4 scoped to a single thread file. No formal-artifact-approval packet is required: no protected narrative artifact (rule file, canonical-terminology, operating-model, ADR, DCL) is edited; the work modifies `groundtruth_kb/db.py` schema + tests + one MemBase WI insert. No `parent` backfill, no spec status mutations, no destructive rewrites of existing rows.

## Bridge INDEX Update Evidence

This REVISED-1 is filed at `bridge/gtkb-spec-lifecycle-schema-slice-1-003.md` with a `REVISED:` line prepended to the existing `Document: gtkb-spec-lifecycle-schema-slice-1` entry in `bridge/INDEX.md`. The prior `NO-GO: -002` and `NEW: -001` lines are preserved; no INDEX entry or bridge file is deleted or rewritten. The append-only audit trail at `bridge/INDEX.md` preserves the full version sequence for this thread.

## Proposed Scope

### IP-1: Add nullable columns to `specifications` table

In `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\db.py`, update the `specifications` table CREATE statement in `SCHEMA_SQL` to include three new nullable columns:

- `implementation_verified_at TEXT` - ISO8601 timestamp when spec moved to verified status; NULL when not yet verified. Slice 2 gate restricts who may set this; Slice 1 only declares the column.
- `retired_at TEXT` - ISO8601 timestamp when spec retired; NULL when active. Slice 2 gate restricts setting; Slice 1 only declares.
- `parent TEXT` - one of `gtkb`, `application`, `all`; nullable in Slice 1 pending Slice 4 backfill. Slice 1.5 rebuilds with `NOT NULL CHECK (parent IN ('gtkb','application','all'))`.

Add an additive migration block in `KnowledgeDB.__init__()` (or the existing schema-evolution path) that runs `ALTER TABLE specifications ADD COLUMN ...` for each of the three columns if and only if the column is not already present (pragma `table_info` introspection; idempotent on re-run). No column rename, no column drop, no default-value backfill.

### IP-2: New `specification_deliberation_sources` table (parent-contract shape)

Add table to `SCHEMA_SQL` using the parent operative contract verbatim (per `bridge/gtkb-spec-lifecycle-schema-2026-04-29-003.md`):

    CREATE TABLE IF NOT EXISTS specification_deliberation_sources (
        rowid INTEGER PRIMARY KEY AUTOINCREMENT,
        spec_id TEXT NOT NULL,
        spec_version INTEGER NOT NULL,
        deliberation_id TEXT NOT NULL,
        source_role TEXT,
        added_at TEXT NOT NULL,
        added_by TEXT NOT NULL,
        UNIQUE(spec_id, spec_version, deliberation_id)
    );

Notes on contract preservation versus prior `-001`:
- Column names use `spec_id`/`spec_version` (NOT `specification_id`/`specification_version`).
- `source_role` is nullable TEXT (NOT a `relationship` CHECK column with enum values).
- `added_at` and `added_by` are NOT NULL (per parent; preserves auditability and idempotence).
- `UNIQUE(spec_id, spec_version, deliberation_id)` enforced (per parent; idempotent re-link is a no-op).
- No foreign keys (parent contract has none; consistent with append-only `(id, version)` multi-row pattern in `specifications`).

Expose via:

    KnowledgeDB.link_spec_deliberation_source(
        spec_id: str,
        spec_version: int,
        deliberation_id: str,
        added_by: str,
        source_role: str | None = None,
        added_at: str | None = None,  # ISO8601; defaults to utcnow if None
    ) -> dict[str, Any]

Method behavior: INSERT OR IGNORE against the unique constraint; returns the canonical row on first insert and the existing row on idempotent re-link. Raises on missing `spec_id`/`spec_version`/`deliberation_id`/`added_by`.

### IP-3: Tests

In `E:\GT-KB\groundtruth-kb\tests\test_db.py`:

- `test_specifications_table_has_new_lifecycle_columns` - fresh DB schema has columns `implementation_verified_at`, `retired_at`, `parent` on `specifications`.
- `test_specifications_alter_table_migration_idempotent` - migration on existing populated DB adds missing columns; second run is a no-op (no duplicate ALTER errors).
- `test_specification_deliberation_sources_table_exists` - fresh DB has the new table; column names match the parent contract (`spec_id`, `spec_version`, `deliberation_id`, `source_role`, `added_at`, `added_by`); unique constraint present.
- `test_link_spec_deliberation_source_inserts_row` - canonical API inserts a row; required fields rejected when missing; read-back matches input.
- `test_link_spec_deliberation_source_idempotent_re_link` - re-inserting the same `(spec_id, spec_version, deliberation_id)` returns the existing row without raising; row count unchanged.
- `test_populated_fixture_migration_zero_data_loss` - populated fixture at `groundtruth-kb/tests/fixtures/spec_lifecycle_slice1_populated_fixture.json` (50 representative spec rows drawn from the live distribution) is loaded into an empty DB; ALTER migration runs; row count, every spec id, every spec version, and every pre-existing column value are preserved; the three new columns are NULL on every migrated row. Carried forward from parent acceptance criterion.

### IP-4: Tracking work_item (machine-verifiable fields)

Insert exactly one `work_items` row via `KnowledgeDB.insert_work_item(...)` with these fields (closes NO-GO F2):

- `id="WI-SPEC-LIFECYCLE-SCHEMA-SLICE-1"`
- `title="Spec lifecycle schema additions (Slice 1)"`
- `origin="new"`
- `component="spec-lifecycle"`
- `resolution_status="in_progress"`
- `stage="implementing"`
- `source_spec_id=None` (placeholder spec `SPEC-LIFECYCLE-SCHEMA-MIGRATION` does not yet exist in MemBase; created in a later slice's ADR/SPEC capture; this WI is updated to link the spec id when the spec lands)
- `changed_by="claude-prime-builder"`
- `change_reason="Track Slice 1 implementation of additive lifecycle schema per parent GO bridge/gtkb-spec-lifecycle-schema-2026-04-29-003.md (REVISED-1 of slice-1)"`
- `related_bridge_threads="gtkb-spec-lifecycle-schema-slice-1"`
- `related_deliberation_ids="DELIB-0707,DELIB-1852"`
- All other optional fields: NULL (omitted from kwargs).

Read-back assertion (run as the IP-4 test): query MemBase by id; expect exactly one current row; assert each enumerated field. Test name: `test_tracking_work_item_inserted_with_expected_fields`.

## Specification-Derived Verification Plan

| Linked spec / clause | Test or command | Expected result |
|---|---|---|
| `ADR-0001` (additive only) | `test_populated_fixture_migration_zero_data_loss` | row count + existing column values preserved |
| Parent `-003` (nullable lifecycle columns) | `test_specifications_table_has_new_lifecycle_columns` | three columns present |
| Parent `-003` (idempotent migration) | `test_specifications_alter_table_migration_idempotent` | second run is a no-op |
| Parent `-003` (table shape) | `test_specification_deliberation_sources_table_exists` | parent-contract column names + unique constraint |
| Parent `-003` (API name + signature) | `test_link_spec_deliberation_source_inserts_row` | row inserted; read-back matches |
| Parent `-003` (unique + idempotence) | `test_link_spec_deliberation_source_idempotent_re_link` | idempotent re-link returns same row |
| `GOV-STANDING-BACKLOG-001` / CLAUSE-VISIBILITY-BULK-OPS | `test_tracking_work_item_inserted_with_expected_fields` | exactly one row with enumerated IP-4 fields |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | spec-to-test mapping above | each linked spec covered by a named test |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-spec-lifecycle-schema-slice-1` | `preflight_passed: true`, `missing_required_specs: []` |
| ADR/DCL clause-test gate | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-spec-lifecycle-schema-slice-1` | exit 0; zero blocking gaps |

Commands at implementation time (executed after GO):

1. `python -m pytest groundtruth-kb/tests/test_db.py -v -k "lifecycle or specification_deliberation_sources or link_spec_deliberation or populated_fixture or tracking_work_item"`
2. `python -m ruff check groundtruth-kb/src/groundtruth_kb/db.py`
3. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-spec-lifecycle-schema-slice-1`
4. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-spec-lifecycle-schema-slice-1`
5. MemBase tracking WI insertion verified via the IP-4 read-back assertion test.

## Risks and Rollback

- Risk: `ALTER TABLE` migration on the live `groundtruth.db` against a populated `specifications` table fails on an unusual row. Mitigation: idempotent migration guarded by pragma `table_info` introspection; populated-fixture test exercises the migration against a 50-row representative sample drawn from the live distribution before the live run.
- Risk: Adding `UNIQUE(spec_id, spec_version, deliberation_id)` on the new table collides with future Slice 4 backfill if backfill emits duplicate `(spec, delib)` pairs. Mitigation: the API uses `INSERT OR IGNORE`; idempotent re-link is part of the contract; tested in IP-3.
- Risk: A future slice (Slice 2 or Slice 4) discovers the parent-contract shape is wrong and needs amendment. Mitigation: this REVISED-1 adopts the parent contract verbatim, so the contract change (if any) is concentrated in a single later thread rather than diffused across slices. Slice 1.5 is the existing point for `parent NOT NULL` rebuild; an analogous rebuild path exists if the source-link table requires reshape.
- Risk: SQLite cannot drop columns without a table rebuild, so if the three new columns turn out to be misspecified, rollback requires either Slice 1.5-style rebuild or accepting unused columns. Mitigation: column names and types match the parent contract verbatim; populated-fixture test confirms additive behavior on the live distribution before live migration.
- Rollback: `git revert` of the IP-1/IP-2/IP-3 commits restores prior `db.py`/`test_db.py`/fixture file content. The live `groundtruth.db` retains the additive columns and table (cannot be dropped in SQLite without rebuild); they remain NULL and unused if the migration is reverted at the code level, which is safe because no downstream code in Slice 1 reads or writes them. The IP-4 work_item is left in place as audit trail.

## Sequenced Dependencies

- Slice 1 (this proposal) is the foundation for Slice 1.5, Slice 2, and Slice 4.
- Slice 1.5 (`parent NOT NULL` rebuild via SQLite table rebuild) requires Slice 4 backfill to complete first (zero null `parent` rows), per parent sequencing.
- Slice 2 (API gates / lifecycle write paths) requires Slice 1's columns and source-link table to exist; Slice 2 must NOT precede Slice 4's pre-API backfill+dry-run+triage work (parent carry-forward constraint).
- Slice 4 (write-path migration + conflict-aware backfill) uses the `specification_deliberation_sources` table introduced in this slice for deliberation provenance landings. Slice 4 must adopt the parent contract's `spec_id`/`source_role`/`added_by` shape; this Slice 1 REVISED-1 preserves that compatibility.
- No external dependencies are introduced by this REVISED-1 beyond those declared by the parent GO.

## Recommended Commit Type

`feat:` - new schema columns on `specifications` + new `specification_deliberation_sources` table + new `KnowledgeDB.link_spec_deliberation_source` API method + new test module entries + new fixture file. Net-new capability surface, not a repair or refactor.

## Bridge-Compliance Self-Check

- First line: `REVISED`.
- H1: `# Implementation Proposal - Spec Lifecycle Schema Slice 1 (additions) - REVISED-1`.
- Metadata: `bridge_kind: implementation_proposal`, `Document: gtkb-spec-lifecycle-schema-slice-1`, `Version: 003`, `Responds to: bridge/gtkb-spec-lifecycle-schema-slice-1-002.md`, `Author: Prime Builder (Claude, harness B)`, `Date: 2026-05-14 UTC`, `Session: S350`, `target_paths` JSON list; all in-root.
- `## Specification Links` present; flat bullets only; no `###` sub-headings inside.
- `## Prior Deliberations` non-empty with real DELIB IDs.
- `## Owner Decisions / Input` non-empty and substantive; cites S350 owner direction and the parallel-research AUQ choice.
- `## Requirement Sufficiency` exactly one operative state (`Existing requirements sufficient`).
- `## Clause Scope Clarification (Not a Bulk Operation)` present.
- `## In-Root Placement Evidence` present.
- `## Bridge INDEX Update Evidence` present.
- `## Proposed Scope` with `### IP-1`, `### IP-2`, `### IP-3`, `### IP-4` sub-headings (inside `Proposed Scope`, not inside `Specification Links`).
- `## Specification-Derived Verification Plan` present; spec-to-test mapping table.
- `## Risks and Rollback` present.
- `## Sequenced Dependencies` present.
- `## Recommended Commit Type` present (`feat:`).
- Footer copyright present.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
