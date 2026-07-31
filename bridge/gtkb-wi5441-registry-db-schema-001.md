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

# WI-5441 Artifact Registry Phase 1B: DB Schema And Migrations

bridge_kind: prime_proposal
Document: gtkb-wi5441-registry-db-schema
Version: 001
Date: 2026-07-23 UTC
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-DB-SCHEMA-20260722
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441
target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/tests/test_registry_db_schema.py"]

## Claim

This is the Phase 1B (DB schema and migrations) slice of the WI-5441 artifact-registry
program, implementing the schema portion of the architecture's Implementation
Decomposition item 1. Phase 1A (governance formalization: nine approval packets and nine
append-only specification records) is already independently VERIFIED at
`bridge/gtkb-wi5441-artifact-registry-governance-formalization-execution-004.md`.

This slice adds only the additive MemBase storage substrate that later phases build on. It:

1. Adds a **nullable** `coverage_mode TEXT` column to `sot_artifacts` (base DDL plus a
   guarded `ALTER TABLE ... ADD COLUMN` in `_migrate_schema` for existing databases). The
   column is nullable with **no** `NOT NULL` default, because `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`
   v3 forbids silently turning a broad directory row into recursive retention via a default.
   Coverage-mode value assignment for existing declarations is deferred to the Phase 2 CLI
   register/amend surface.
2. Creates append-only `sot_artifact_revisions` (observed-revision ledger): entry id,
   canonical relative path, object kind, content/Merkle digest, size, observed_at,
   actor/session, operation, predecessor revision id. Per
   `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` v2, revision rows are automatically-maintained
   observed state and **do not grant membership**.
3. Creates `sot_registry_transaction_journal`: intent and completion records (operation,
   entry id, declaration digest, prior/current observed revision, filesystem result,
   projection transaction, receipt digest, journal state) enabling deterministic recovery
   after partial failure per `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` v1.
4. Creates `sot_quarantine_receipts`: binds original relative path, object kind, source stat
   evidence, payload path, content/Merkle digest, logical size, registry declaration digest,
   observed-revision cutoff, inventory digest, sweep plan digest, actor/session, immutable
   `quarantined_at` and `expires_at`, and `restore_pending`, per
   `DCL-QUARANTINE-RETENTION-EXPIRY-001` v1.

New tables are created via `CREATE TABLE IF NOT EXISTS` in the base DDL block, which covers
both fresh and existing databases; the coverage-mode column uses the established guarded
`PRAGMA table_info` + `ALTER TABLE ADD COLUMN` migration pattern already used in
`_migrate_schema`.

**Explicitly out of scope for this slice** (deferred to later phases): coverage_mode value
backfill, any `config/registry/sot-artifacts.toml` edit, loader/schema validation
enforcement, the `gt registry` register/amend/observe/transition CLI, hooks, doctor/commit
/release gates, sweep planning, quarantine execution, and expiry. No behavior, no
enforcement, no Git/release/deployment/dispatcher/credential mutation.

## Specification Links

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` — controlling owner decision.
- `bridge/gtkb-artifact-registry-authoritative-hygiene-sweep-002.md` — independent architecture GO.
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` (v3) — coverage-mode locator semantics this slice stores.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` (v2) — declaration vs observed-revision split; revisions do not grant membership.
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` (v1) — transaction journal / recoverable transactions.
- `DCL-QUARANTINE-RETENTION-EXPIRY-001` (v1) — quarantine receipt binding fields and immutable 30-day retention.
- `ADR-REGISTRY-AUTHORITATIVE-ARTIFACT-LIFECYCLE-001` (v1) — compound declaration/revision-ledger architecture.
- `GOV-PLATFORM-SOT-REGISTRY-001` (v2) — registry as platform artifact-membership authority.
- `GOV-WORK-TREE-HYGIENE-001` (v2) — registry-authoritative sweep and quarantine model.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implementation requires an active bounded PAUTH.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — operation-time authorization freshness.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact approval governance (no formal-artifact mutation in this slice).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification maps each clause to executed tests.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — numbered-file bridge authority and independent review.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — in-root placement; no `applications/<child>` touched.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable artifact traceability; revisions/quarantine are lifecycle events.

## Requirement Sufficiency

Existing requirements sufficient. The Phase 1A-formalized specifications listed above define
the target schema semantics; this slice implements only the additive storage substrate for
them. No new or revised requirement is required before implementation.

## Owner Decisions / Input

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` — owner authorization of the
  artifact-registry / quarantine / 30-day-expiry program, cited by the active PAUTH.
- Owner mandate (2026-07-22 transcript) — directs Prime Builder to carry WI-5441 through
  bounded per-slice proposals with independent GO/VERIFIED; "establish a new bounded PAUTH …
  per slice."
- Owner AUQ (2026-07-22) — session Prime Builder provenance correction ("I correct my session
  doc") and per-slice PAUTH lifecycle ("revoke each completed slice PAUTH"); the Phase 1A
  governance PAUTH was accordingly revoked after its VERIFIED slice so exactly one active
  WI-5441 PAUTH (`…-DB-SCHEMA-20260722`) governs this slice.

## Prior Deliberations

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` — controlling owner decision.
- `bridge/gtkb-artifact-registry-authoritative-hygiene-sweep-001.md` / `-002.md` — architecture governance review and independent GO (defines the Registry Data Model this schema realizes).
- `bridge/gtkb-wi5441-artifact-registry-governance-formalization-execution-004.md` — Phase 1A VERIFIED verdict (the nine specs realized here are `specified`).
- `DELIB-20260701-GTKB-ARTIFACT-ESSENTIALITY-EMERGENCY` — registry-first cleanup guardrails; Git is not essentiality authority.
- `DELIB-20260710-GTKB-MODERNIZATION-ARTIFACT-DECONTAMINATION-CHARTER` — prior bounded cleanup charter (superseded only where "No unbounded purge" conflicts with the closed registry-authoritative sweep).

## Implementation Scope

- `groundtruth-kb/src/groundtruth_kb/db.py`
  - Add `coverage_mode TEXT` (nullable, no default) to the `sot_artifacts` `CREATE TABLE` DDL.
  - Add the same column via a guarded `PRAGMA table_info(sot_artifacts)` + `ALTER TABLE sot_artifacts ADD COLUMN coverage_mode TEXT` migration in `_migrate_schema` (idempotent; no backfill).
  - Add `CREATE TABLE IF NOT EXISTS sot_artifact_revisions (…)` with the observed-revision columns and an append-only shape (no UPDATE/DELETE), plus supporting indexes.
  - Add `CREATE TABLE IF NOT EXISTS sot_registry_transaction_journal (…)` with intent + completion columns and a journal-state column.
  - Add `CREATE TABLE IF NOT EXISTS sot_quarantine_receipts (…)` with the receipt-binding columns, immutable `quarantined_at`/`expires_at`, and `restore_pending`.
- `groundtruth-kb/tests/test_registry_db_schema.py` (new) — focused schema tests (see verification plan).

No other file is modified. `current_sot_artifacts` view semantics are preserved. `select *`-based
projection continues to function; the Phase-2 projection reader will begin surfacing
`coverage_mode` in a later slice.

## Spec-Derived Verification Plan

| Governing spec | Executed test evidence |
| --- | --- |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v3 | Test asserts `sot_artifacts` has a nullable `coverage_mode` column with no default on both a fresh DB and a DB migrated from a pre-column baseline; pre-existing rows retain `NULL`. |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` v2 | Test asserts `sot_artifact_revisions` exists, is insert-only in shape, and that inserting a revision row does not change `current_sot_artifacts`/membership; `gt registry validate` remains `in_sync` at 50/50. |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` v1 | Test asserts `sot_registry_transaction_journal` carries the intent + completion columns (operation, entry id, declaration digest, prior/current revision, filesystem result, projection transaction, receipt digest, state). |
| `DCL-QUARANTINE-RETENTION-EXPIRY-001` v1 | Test asserts `sot_quarantine_receipts` carries all required binding columns including immutable `quarantined_at`/`expires_at` and `restore_pending`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Every schema clause above maps to an executed `pytest` node; an idempotency test (repeat `_ensure_schema`/`_migrate_schema` is a no-op) and a data-preservation test (existing `sot_artifacts` rows unchanged) are included and run. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target paths are under `E:\GT-KB`; no `applications/<child>` path is created or modified. |

Exact commands to be reported in the post-implementation report: `ruff check <changed.py>`,
`ruff format --check <changed.py>`, and the focused `pytest` node ids for
`groundtruth-kb/tests/test_registry_db_schema.py`, plus `gt registry validate --json`.

## Acceptance Criteria

1. `sot_artifacts` has a nullable `coverage_mode` column on fresh and migrated databases; existing 50 rows retain `NULL`; no `NOT NULL` default is introduced.
2. `sot_artifact_revisions`, `sot_registry_transaction_journal`, and `sot_quarantine_receipts` exist with the specified columns on fresh and existing databases.
3. Migration is idempotent and preserves all existing `sot_artifacts` rows and `current_sot_artifacts` view semantics.
4. `gt registry validate` still reports `in_sync` with 50 TOML / 50 projection rows and zero divergence.
5. No coverage_mode value assignment, no TOML edit, no loader validation, and no CLI/hook/enforcement change occur in this slice.

## Risk And Rollback

- **Risk:** an accidental `NOT NULL`/default on `coverage_mode` would silently classify existing rows. **Mitigation:** the column is nullable with no default; a dedicated test asserts this and that existing rows are `NULL`.
- **Risk:** a non-idempotent migration could double-apply on existing DBs. **Mitigation:** guarded `PRAGMA table_info` check + `CREATE TABLE IF NOT EXISTS`; idempotency test.
- **Risk:** schema change disturbs projection parity. **Mitigation:** additive columns/tables only; `gt registry validate` 50/50 asserted post-migration.
- **Rollback:** additive-only DDL; rollback is a normal-bridge-path code revert. No data is migrated, moved, or deleted; no Git/release action is requested by this proposal (the PAUTH forbids `git_commit`, `git_push`, `release`, `destructive_cleanup`, and `dispatcher_mutation`).

## Preflight

Applicability preflight and ADR/DCL clause preflight both returned `0` (PASS, no missing
required specs, no blocking clause gaps) when the governed generator composed this exact
proposal content (`gt bridge file-implementation-proposal --dry-run`) on 2026-07-23; the
generator auto-selected `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-DB-SCHEMA-20260722`
as the sole `exact_singleton` candidate for WI-5441. This proposal is filed as a plain numbered
bridge file (not the dispatchable filer) per `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN`; review
is by independent manual/timer-driven Loyal Opposition operation.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
