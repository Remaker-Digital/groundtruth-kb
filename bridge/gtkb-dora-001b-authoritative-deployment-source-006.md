GO

# GTKB-DORA-001b - Authoritative Deployment Source Scoping Review

**Status:** GO
**Date:** 2026-04-25
**Reviewer:** Codex (Loyal Opposition)
**Reviewed proposal:** `bridge/gtkb-dora-001b-authoritative-deployment-source-005.md`

## Verdict

GO.

The revised scoping proposal now addresses the remaining blocker from `-004`. It defines a manifest-ingest classification contract that prevents dry-runs, validation failures, and other non-deployment pipeline runs from becoming `canonical_deploy` rows.

## Review Findings

### 1. Manifest classification contract is sufficient

Section 5.5 correctly separates the four cases Codex required:

- `dry_run == true` maps to `canonical_pipeline_dry_run`, not `canonical_deploy`.
- No deploy phase maps to `canonical_pipeline_run`, not `canonical_deploy`.
- Deploy phase failure maps to `canonical_deploy_attempted_failed`.
- Deploy phase PASS on a non-dry-run manifest maps to `canonical_deploy`, with confidence capped before Track 1 adds explicit evidence booleans.

That fixes the telemetry poisoning risk identified in `-004`.

### 2. Event-kind taxonomy is acceptable for scoping

The four-way split is the right shape:

- `canonical_deploy`
- `canonical_deploy_attempted_failed`
- `canonical_pipeline_run`
- `canonical_pipeline_dry_run`

The proposal also correctly states that deployment-frequency math must count only `canonical_deploy`. The implementation proposal should make that exclusion testable when DORA KPI queries land.

### 3. `refresh_runs.status` wording is corrected

Section 5.4 now matches the current refresh table behavior: reconciliation failures should not turn the overall refresh into a failed run. They should degrade affected rows to unknown consistency and emit warning evidence.

### 4. Pre-Track-1 medium confidence is acceptable

Pre-enhancement manifests do not contain `target_update_succeeded`, `revision_name`, or `_deployed_at` evidence. Capping those rows at `_confidence='medium'` is a reasonable interim contract, provided the implementation does not promote them to high confidence without either Track 1 evidence or Azure revision confirmation.

## Implementation Conditions

The implementation bridge should preserve these constraints:

1. `_classify_manifest()` must be covered with fixtures for dry-run, no deploy phase, deploy phase FAIL, deploy phase PASS pre-Track-1, and enhanced deploy-evidence cases.
2. DORA KPI queries must explicitly exclude `canonical_pipeline_run` and `canonical_pipeline_dry_run` from deployment frequency.
3. Pre-Track-1 `canonical_deploy` rows must not exceed medium confidence.
4. Azure reconciliation failures must not fail `refresh_runs.status`.

These are implementation review points, not blockers to the scoping GO.

## Decision Needed From Owner

None for this scoping proposal. Track 1 implementation still requires owner GOV-17 acknowledgement because it modifies `scripts/deploy_pipeline.py`.
