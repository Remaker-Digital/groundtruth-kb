NEW

# Implementation Proposal - GTKB-DORA-001b Authoritative Deployment Source Implementation

bridge_kind: prime_proposal
Document: gtkb-dora-001b-implementation
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
target_paths: ["scripts/deploy_pipeline.py", "scripts/gtkb_dashboard/schema.sql", "scripts/gtkb_dashboard/refresh_dashboard_db.py", "platform_tests/scripts/test_dora_001b_classify_manifest.py", "platform_tests/scripts/test_dora_001b_dora_kpi_exclusion.py", "platform_tests/scripts/test_dora_001b_pre_track_1_confidence_cap.py", "platform_tests/scripts/test_dora_001b_refresh_runs_reconciliation.py", "groundtruth.db"]

## Claim

The parent thread `gtkb-dora-001b-authoritative-deployment-source` is GO at `-008` (scoping addendum at `-007` approved under the implementation contract at `-006`). The substantive implementation has NOT yet landed. This proposal implements the four Implementation Conditions from the `-006` GO:

1. `_classify_manifest()` with fixtures for dry-run, no-deploy-phase, deploy-fail, pre-Track-1-deploy-pass, and enhanced-deploy-evidence cases.
2. DORA KPI queries excluding `canonical_pipeline_run` and `canonical_pipeline_dry_run` from deployment frequency.
3. Pre-Track-1 `canonical_deploy` rows capped at `_confidence='medium'`.
4. Azure reconciliation failures degrade affected rows to unknown consistency without failing `refresh_runs.status`.

## In-Root Placement Evidence

All target paths are in-root under `E:\GT-KB`. Bridge file at `E:\GT-KB\bridge\gtkb-dora-001b-implementation-001.md`. Targets at `E:\GT-KB\scripts\deploy_pipeline.py`, `E:\GT-KB\scripts\gtkb_dashboard\schema.sql`, `E:\GT-KB\scripts\gtkb_dashboard\refresh_dashboard_db.py`, `E:\GT-KB\platform_tests\scripts\test_dora_001b_*.py`, `E:\GT-KB\groundtruth.db`. No `applications/` paths.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol observed.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths in-root under `E:\GT-KB`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - every governing spec cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - DORA KPIs feed release-readiness evidence.
- `GOV-STANDING-BACKLOG-001` - tracking work_item per slice.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - canonical_deploy + canonical_pipeline_run rows are governance artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - manifest-classifier output is a tracked artifact.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - canonical_deploy lifecycle tied to deploy phase outcome.
- `bridge/gtkb-dora-001b-authoritative-deployment-source-006.md` - parent implementation contract (GO'd).
- `bridge/gtkb-dora-001b-authoritative-deployment-source-007.md` - scoping addendum.
- `bridge/gtkb-dora-001b-authoritative-deployment-source-008.md` - Codex GO authorizing this implementation.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - DORA classification belongs in a deterministic service.
- 2026-05-14 UTC, S350: owner prompt "Please continue with dora-001b verification, 3 slice-N proposals for scoping GOs, startup-payload-drift bridge proposal" - explicit authorization.
- 2026-05-14 UTC, S350: owner prompt "Proceed with all identified work" - broader queue authorization.
- bridge/gtkb-dora-001b-authoritative-deployment-source -001 through -008 - parent chain.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner prompt "Please continue with dora-001b verification, 3 slice-N proposals for scoping GOs, startup-payload-drift bridge proposal" - explicit authorization.
- 2026-05-14 UTC, S350: owner prompt "Proceed with all identified work".

No new owner decision required.

## Requirement Sufficiency

Existing requirements sufficient. Implementation operates under the parent GO's contract.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation; creates one tracking work_item.

## Bridge INDEX Update Evidence (CLAUSE-INDEX-IS-CANONICAL)

This proposal is filed at `bridge/gtkb-dora-001b-implementation-001.md` with a `Document: gtkb-dora-001b-implementation` + `NEW:` entry inserted at the top of `bridge/INDEX.md`. The INDEX update is additive; no prior INDEX entry or bridge file is deleted or rewritten. The append-only audit trail at `bridge/INDEX.md` preserves the full version sequence for this thread.

## Bulk-Operations Clause Evidence (CLAUSE-VISIBILITY-BULK-OPS)

This implementation is NOT a bulk operation against the standing backlog. It creates exactly one tracking `work_item` (per IP-6) identical in shape to other single-slice tracking entries (e.g., WI-3310 from gtkb-implementation-gate-friction-hygiene). The inventory for this slice is the 4 Implementation Conditions enumerated in proposed scope IP-1 through IP-4. The review-packet is this proposal plus the parent thread chain `bridge/gtkb-dora-001b-authoritative-deployment-source -001 through -008`. No formal-artifact-approval packet is required because no protected narrative artifact is edited; the work creates Python implementation + SQL schema migration + tests + one MemBase WI insert.

## Proposed Scope

### IP-1: `_classify_manifest()` implementation

In `scripts/deploy_pipeline.py`, add `_classify_manifest(manifest)` returning one of:
- `canonical_pipeline_dry_run` when `manifest.dry_run == True`.
- `canonical_pipeline_run` when no deploy phase exists in manifest.
- `canonical_deploy_attempted_failed` when deploy phase exists but `outcome != "pass"`.
- `canonical_deploy` when deploy phase exists and `outcome == "pass"` on a non-dry-run manifest.

### IP-2: DORA KPI query exclusion

In `scripts/gtkb_dashboard/refresh_dashboard_db.py`, update DORA deployment-frequency queries to filter on `event_kind = 'canonical_deploy'` only; explicit `WHERE event_kind NOT IN ('canonical_pipeline_run', 'canonical_pipeline_dry_run')`.

### IP-3: Pre-Track-1 medium-confidence cap

In `scripts/deploy_pipeline.py` `_classify_manifest()`, when the manifest lacks Track-1 evidence (`target_update_succeeded`, `revision_name`, `_deployed_at`), the resulting `canonical_deploy` row's `_confidence` field is capped at `medium`. With Track-1 evidence present, `_confidence` may be `high`.

### IP-4: refresh_runs.status preservation under Azure reconciliation failure

In `scripts/gtkb_dashboard/refresh_dashboard_db.py`, Azure reconciliation step must catch reconciliation failures, degrade affected rows' `_consistency` to `unknown`, emit warning evidence, and NOT set `refresh_runs.status = 'failed'`.

### IP-5: Regression tests

Four test files, each ~5-8 tests:
- `test_dora_001b_classify_manifest.py`: 5 fixture-driven tests for the four event kinds + pre-Track-1.
- `test_dora_001b_dora_kpi_exclusion.py`: tests that DORA deployment-frequency excludes pipeline_run + pipeline_dry_run.
- `test_dora_001b_pre_track_1_confidence_cap.py`: tests that pre-Track-1 canonical_deploy rows cap at medium.
- `test_dora_001b_refresh_runs_reconciliation.py`: tests that reconciliation failure doesn't fail refresh_runs.status.

### IP-6: Tracking work_item

One `work_items` row: origin=`new`, component=`dora-kpi`, source_spec_id=`GOV-RELEASE-READINESS-GOVERNED-TESTING-001`, title carries the implementation summary.

## Specification-Derived Verification Plan

1. `python -m pytest platform_tests/scripts/test_dora_001b_*.py -v` - all new tests PASS.
2. `python -m ruff check scripts/deploy_pipeline.py scripts/gtkb_dashboard/` - zero errors.
3. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dora-001b-implementation` - `preflight_passed: true`.
4. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-dora-001b-implementation` - exit 0, zero blocking gaps.
5. End-to-end smoke: feed a known dry-run manifest fixture through `_classify_manifest` and verify the four event-kind branches.
6. MemBase tracking WI inserted per IP-6.

## Risks and Rollback

- **Risk**: classifier misclassifies edge cases (e.g., deploy phase with `outcome` field missing). Mitigation: fail-safe default to `canonical_pipeline_run`. Rollback: revert classifier.
- **Risk**: DORA KPI query exclusion breaks existing dashboard panels. Mitigation: 5 regression tests against fixture rows; visual smoke test before commit.
- General rollback: `git revert <commit-sha>` reverts source + tests. WI append-only retire.

## Sequenced Dependencies

Independent of friction-hygiene, benchmark-suite, and other current threads. Sister thread `GTKB-DORA-001c` (future) covers GitHub Actions out-of-band detection.

## Recommended Commit Type

`feat:` - new manifest-classifier surface + DORA query exclusion + confidence cap + reconciliation degradation logic.

## Bridge-Compliance Self-Check

- Non-empty `## Specification Links` with flat bullets; no `###` sub-headings inside.
- Non-empty `## Prior Deliberations`.
- Non-empty `## Owner Decisions / Input`.
- target_paths in JSON form; all in-root under `E:\GT-KB`.
- `## Requirement Sufficiency` exactly one operative state.
- `## Recommended Commit Type` present.
- `## Clause Scope Clarification (Not a Bulk Operation)` present.
- `## In-Root Placement Evidence` present.
- Proposed Scope enumerates IP-1 through IP-6.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
