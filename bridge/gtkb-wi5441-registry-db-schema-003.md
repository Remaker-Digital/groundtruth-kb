NEW
::init gtkb lo
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 87ea6b9f-89d5-4e90-a637-a7f9fe8cb561
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb
author_metadata_source: explicit current-session Claude bridge filing metadata

# WI-5441 Artifact Registry Phase 1B: DB Schema And Migrations — Implementation Report

Document: gtkb-wi5441-registry-db-schema
Version: 003
Responds to: bridge/gtkb-wi5441-registry-db-schema-002.md
bridge_kind: implementation_report
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-DB-SCHEMA-20260722
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441
target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/tests/test_registry_db_schema.py"]

## Implementation Claim

Phase 1B (DB schema and migrations) is implemented exactly within the GO'd scope
(`bridge/gtkb-wi5441-registry-db-schema-002.md`), bounded to
`groundtruth-kb/src/groundtruth_kb/db.py` and the new
`groundtruth-kb/tests/test_registry_db_schema.py`. The change is additive storage
substrate only — no CLI, loader validation, hook, sweep, quarantine, expiry, or
coverage-mode backfill behavior was added (GO invariant 5, "no premature feature
mutation").

Implemented in `db.py`:

1. **`coverage_mode TEXT`** added to the `sot_artifacts` `CREATE TABLE` in `SCHEMA_SQL`
   (nullable, **no** default), plus a guarded `PRAGMA table_info(sot_artifacts)` +
   `ALTER TABLE sot_artifacts ADD COLUMN coverage_mode TEXT` migration ("Migration 6b")
   in `_migrate_schema` for pre-existing databases. Placed last in the `CREATE TABLE`
   so fresh and ALTER-migrated column order match. No default per
   `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v3 (no silent recursive-retention default).
2. **`sot_artifact_revisions`** (append-only observed-revision ledger) with the nine
   DCL-required fields: `entry_id`, `canonical_relative_path`, `object_kind`,
   `content_digest`, `size_bytes`, `observed_at`, `actor_session`, `operation`,
   `predecessor_revision_id` (+ `revision_id`, audit columns, indexes).
3. **`sot_registry_transaction_journal`** with intent + completion columns for
   deterministic recovery: `operation`, `entry_id`, `intent_recorded_at`,
   `declaration_digest`, `prior_revision_id`, `current_revision_id`, `filesystem_result`,
   `projection_transaction`, `receipt_digest`, `journal_state`, `completed_at`,
   `actor_session`.
4. **`sot_quarantine_receipts`** binding every field
   `DCL-QUARANTINE-RETENTION-EXPIRY-001` requires (`original_relative_path`,
   `object_kind`, `source_stat_evidence`, `payload_path`, `content_digest`,
   `logical_size`, `registry_declaration_digest`, `observed_revision_cutoff`,
   `inventory_digest`, `sweep_plan_digest`, `actor_session`) plus immutable
   `quarantined_at`/`expires_at` and `restore_pending`.

New tables are created via `CREATE TABLE IF NOT EXISTS` in `SCHEMA_SQL`, which
`_ensure_schema` executes on every DB open, so they land on both fresh and existing
databases without a bespoke migration.

## Specification Links

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` — controlling owner decision.
- `bridge/gtkb-artifact-registry-authoritative-hygiene-sweep-002.md` — independent architecture GO.
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` (v3) — coverage-mode locator semantics; no silent default.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` (v2) — declaration vs observed-revision split; revisions do not grant membership.
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` (v1) — transaction journal / recoverable transactions.
- `DCL-QUARANTINE-RETENTION-EXPIRY-001` (v1) — quarantine receipt binding fields; immutable 30-day retention.
- `ADR-REGISTRY-AUTHORITATIVE-ARTIFACT-LIFECYCLE-001` (v1) — compound declaration/revision-ledger architecture.
- `GOV-PLATFORM-SOT-REGISTRY-001` (v2) — registry as platform artifact-membership authority.
- `GOV-WORK-TREE-HYGIENE-001` (v2) — registry-authoritative sweep and quarantine model.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — active bounded PAUTH + operation-time freshness.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact approval governance (no formal-artifact mutation in this slice).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` / `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec linkage and spec-derived testing.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — numbered-file bridge authority and independent review.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — in-root placement; no `applications/<child>` touched.

## Requirement Sufficiency

Existing requirements sufficient. The Phase 1A-formalized specifications define the
target schema semantics; this slice implements only the additive storage substrate.
No new or revised requirement was required before implementation.

## Owner Decisions / Input

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` — owner authorization of
  the artifact-registry / quarantine / 30-day-expiry program, cited by the active PAUTH.
- Owner mandate (2026-07-22 transcript) — directs Prime Builder to carry WI-5441 through
  bounded per-slice proposals with independent GO/VERIFIED.
- **Owner AUQ (2026-07-23, this session)** — after a session restart dropped the interactive
  Prime Builder role (resolver fell back to loyal-opposition despite the recorded
  `::init gtkb pb`), the owner selected "Re-assert programmatically." Prime Builder role for
  session `87ea6b9f…` was restored via the canonical `ensure_worker_session`
  (role_source `transcript_init_keyword`) before the implementation claim. This did not
  weaken review independence (independence is keyed on session context, not role); the LO
  verifier must still be an unrelated session.

## Prior Deliberations

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` — controlling owner decision.
- `bridge/gtkb-artifact-registry-authoritative-hygiene-sweep-001.md` / `-002.md` — architecture governance review and independent GO (defines the Registry Data Model this schema realizes).
- `bridge/gtkb-wi5441-artifact-registry-governance-formalization-execution-004.md` — Phase 1A VERIFIED verdict (the nine specs realized here are `specified`).
- `bridge/gtkb-wi5441-registry-db-schema-002.md` — the independent GO this report responds to (antigravity/C, session `e47005c5…`).

## Spec-to-Test Mapping (DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001)

All tests in `groundtruth-kb/tests/test_registry_db_schema.py`; all executed, all PASS.

| Governing spec clause | Test node | Result |
| --- | --- | --- |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v3 — coverage_mode nullable, no default | `test_coverage_mode_present_nullable_no_default` | PASS |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v3 — migration adds column, preserves rows at NULL | `test_migration_adds_coverage_mode_and_preserves_rows` | PASS |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` v1 + `DCL-QUARANTINE-RETENTION-EXPIRY-001` v1 — required journal/receipt/revision columns present | `test_registry_tables_present_with_required_columns` | PASS |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` v2 — observed revisions do not grant membership | `test_observed_revision_does_not_change_membership` | PASS |
| GO invariant 3 — idempotent migration (re-run `_ensure_schema`/`_migrate_schema` no-op) | `test_schema_migration_idempotent` | PASS |
| GO invariant 4 + `GOV-PLATFORM-SOT-REGISTRY-001` v2 — parity preserved | `gt registry validate` (below) | PASS 50/50 |

## Commands Executed

- `python -m pytest groundtruth-kb/tests/test_registry_db_schema.py -q` → **5 passed**.
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/tests/test_registry_db_schema.py` → **All checks passed!**
- `python -m ruff format --check <both files>` → **2 files already formatted** (test file was `ruff format`-normalized before this).
- `gt registry validate --json` → `{"in_sync": true, "toml_count": 50, "projection_count": 50, ... "field_divergences": []}` — **50/50 parity preserved** after the additive migration applied to the live DB.
- Regression suites (existing consumers of `sot_artifacts`/projection reader):
  `python -m pytest groundtruth-kb/tests/test_sot_registry.py groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py platform_tests/unit/test_knowledge_db_artifacts.py platform_tests/scripts/test_check_sot_registry_completeness.py -q`
  → **97 passed, 2 failed** (the 2 failures are pre-existing and out of scope — see below).

## Live-DB Migration Note (transparency)

Opening the live `groundtruth.db` (via `gt registry validate` and the tests) applies the
additive migration automatically — this is inherent `_ensure_schema` behavior on any DB
open, not a deliberate KB record mutation. The migration adds the nullable `coverage_mode`
column (existing rows → `NULL`) and the three empty tables. It is additive, idempotent, and
parity-preserving (`gt registry validate` 50/50, zero field divergences). No KB
record/data/membership mutation occurred. `groundtruth.db` is left unstaged; this slice
performs no `git add`/commit/push/release/deploy.

## Pre-Existing Out-of-Scope Test Failures (full disclosure)

`platform_tests/unit/test_knowledge_db_artifacts.py::TestSchemaExists::test_all_tables_exist`
and `::test_all_views_exist` fail. **These were already red on HEAD, independent of this
slice**, and the file is **outside this GO's `target_paths`**. Evidence:

- Both tests assert the live schema equals a hardcoded expected list.
- The actual schema contains **five `dispatch_lane*` tables** (`dispatch_lanes`,
  `dispatch_lane_projection_snapshots`, `dispatch_lane_score_dimensions`,
  `dispatch_lane_score_snapshots`, `dispatch_lane_scoring_evidence`) plus the
  `current_dispatch_lane_projection_snapshots` view — none added by this slice and none in
  the expected lists. The enumeration lists are stale from prior dispatch-lane work, so the
  tests were failing before Phase 1B.
- This slice's three new tables extend the pre-existing `test_all_tables_exist` delta but do
  not take a green test to red.

Handling: the stale-enumeration test is captured as a separate backlog item
(`gt backlog add`, origin hygiene). It is not remediated here because
`platform_tests/unit/test_knowledge_db_artifacts.py` is not in this slice's `target_paths`
and remediation is a distinct maintenance concern (per the WI-5441 mandate: bound each slice
to its exact targets; record tooling defects separately).

## Recommended Commit Type

`feat:` — net-new registry storage substrate (one column, three tables, one migration) plus
a new focused test module. Diff is additive net-new capability, not a repair or maintenance
touch.

## Verification Requested

Independent LO verification that: (a) the four DCL-required column sets are complete;
(b) coverage_mode is nullable with no default; (c) the migration is idempotent and
row-preserving; (d) projection parity remains 50/50; (e) no premature feature/behavior was
added. Reviewer session context MUST differ from author `87ea6b9f…`.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
