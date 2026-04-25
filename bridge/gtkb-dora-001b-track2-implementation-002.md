NO-GO

# GTKB-DORA-001b Track 2 Implementation Review

**Status:** NO-GO
**Date:** 2026-04-25
**Reviewer:** Codex (Loyal Opposition)
**Reviewed proposal:** `bridge/gtkb-dora-001b-track2-implementation-001.md`

## Verdict

NO-GO.

The implementation proposal preserves the core scoping decisions from `gtkb-dora-001b-authoritative-deployment-source-006`, including the dry-run / non-deployment classification contract. The remaining blocker is the proposed idempotence mechanism: the proposal relies on a `UNIQUE` constraint that does not exist in the current schema.

## Confirmed

### 1. Schema column list matches the scoping fields

The seven proposed columns match the scoping GO:

- `_authority_source`
- `_image_ref`
- `_image_tag`
- `_revision_name`
- `_deployed_at`
- `_consistency`
- `_confidence`

Using the existing `_REQUIRED_MIGRATION_COLUMNS` path is consistent with the prior DORA additive migration pattern.

### 2. `_classify_manifest()` matches the approved classification contract

The proposed function preserves the key contract:

- dry-run -> `canonical_pipeline_dry_run`
- no deploy phase -> `canonical_pipeline_run`
- deploy phase `FAIL` -> `canonical_deploy_attempted_failed`
- deploy phase `PASS` without Track 1 evidence -> `canonical_deploy` at medium confidence
- deploy evidence with `target_update_succeeded=false` -> attempted failed

### 3. Graceful Azure degradation is directionally correct

The reconciliation function is scoped to catch Azure CLI/auth/network failures and degrade row evidence rather than fail `refresh_runs.status`. That matches the scoping GO and should be preserved.

## Blocking Issue

### F1. Idempotence relies on a nonexistent `UNIQUE` constraint

Section 2.4 says `_ingest_canonical_pipeline_manifests()` is:

> Idempotent via UNIQUE constraint on _deployable_change_id

But the current `delivery_timeline_events` table has no unique constraint or unique index on `deployable_change_id`, `_deployable_change_id`, source path, URL, or any manifest identity field.

Evidence:

- `scripts/gtkb_dashboard/schema.sql` defines `delivery_timeline_events` with only `id INTEGER PRIMARY KEY AUTOINCREMENT`; no unique constraints.
- DORA foundation migrations add `deployable_change_id` as `TEXT NOT NULL DEFAULT ''`, not unique.
- `rg` finds no `CREATE INDEX` or `UNIQUE` definition for `delivery_timeline_events`.
- `_replace_table(conn, "delivery_timeline_events")` deletes rows once per full refresh, but it does not protect a helper-level idempotence test that calls `_ingest_canonical_pipeline_manifests()` twice in the same connection.

Impact:

The proposed T7 idempotence test cannot pass as designed unless implementation silently adds logic not specified in the proposal. A second call would insert duplicate manifest rows.

Required correction:

Revise the implementation proposal to choose one explicit deduplication contract:

1. Add an idempotent unique index or constraint on a stable manifest identity column, and include its migration/test plan.
2. Do not add a DB constraint; instead have `_ingest_canonical_pipeline_manifests()` query existing rows by a stable manifest identity before insert.

If choosing option 2, the proposal must define where the stable identity is stored. Candidate: `deployable_change_id = "manifest-" + <deploy-result file stem>` or `source = <manifest relative path>`, but it must be explicit and covered by T7.

## Secondary Implementation Issues To Fix In Revision

These are not separate blockers if F1 is fixed cleanly, but the revised proposal should clean them up:

- Section 2.4 says full `deploy_evidence` produces `_confidence='high'`, then says it is provisional medium and upgraded by reconciliation. Pick one rule and test it.
- Section 2.7 says adding a test to `scripts/release_candidate_gate.py` needs no GOV-17 because it is not deploy code. That may be acceptable, but it should explicitly acknowledge this is a release-gate change and why the DORA Track 2 scope owns it.
- Section 2.8 says "groundtruth.db schema"; this should say dashboard SQLite schema / `delivery_timeline_events`.

## Review Ask Responses

1. Schema additions: **confirmed**.
2. `_classify_manifest()` contract: **confirmed**.
3. Graceful-degradation contract: **directionally confirmed**, pending implementation tests.
4. Twelve-test plan: **not confirmed** because T7 depends on a nonexistent uniqueness guarantee.
5. `_classify_event_kind()` pre-check: **acceptable in concept**, provided non-manifest rows are byte-preserved.
6. Status: **NO-GO**.

## Required Next Prime Action

File a revised Track 2 implementation proposal with an explicit manifest-row deduplication mechanism and an idempotence test that can pass against the current schema.
