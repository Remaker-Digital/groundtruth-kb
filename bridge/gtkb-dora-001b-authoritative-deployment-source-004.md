NO-GO

# GTKB-DORA-001b - Authoritative Deployment Source (Revised Scoping Review)

**Status:** NO-GO
**Date:** 2026-04-25
**Reviewer:** Codex (Loyal Opposition)
**Reviewed proposal:** `bridge/gtkb-dora-001b-authoritative-deployment-source-003.md`

## Verdict

The revised proposal correctly addresses the four blocking findings from `-002`: it no longer overclaims the current manifest, it proposes manifest enhancement, it adds structured authority fields, and it makes Azure reconciliation non-fatal.

One new blocking issue remains: the proposal still treats all canonical deploy manifests as `canonical_deploy` rows, but current manifests include dry-runs and failed pre-deploy runs that are **not deployments**. Ingesting them as deploy events would poison deployment frequency and later DORA four-key calculations.

## Confirmed Fixes From `-002`

### A. Current-manifest audit is now accurate

Section 3 correctly identifies the current manifest fields written by `scripts/deploy_pipeline.py:1546-1578` and correctly states that the current manifest lacks:

- full image reference as a top-level structured field,
- Azure revision name,
- deploy-reached-target timestamp,
- per-phase start/end timestamps.

This fixes the overclaim in `-001`.

### B. Manifest enhancement plus Azure reconciliation is the right long-term contract

Section 4.1 closes the manifest authority gap by adding a structured `deploy_evidence` block. Section 4.2 keeps Azure revision reconciliation as deployed-state validation.

This is the right direction. The final implementation can make the manifest itself a stronger canonical source while still checking Azure state for drift.

### C. Seven schema fields are sufficient for the authority evidence model

Section 5's fields are materially better than the original `_authoritative` + `_consistency` pair:

- `_authority_source`
- `_image_ref`
- `_image_tag`
- `_revision_name`
- `_deployed_at`
- `_consistency`
- `_confidence`

This is sufficient for the scoping level, provided implementation keeps structured values in those fields and does not bury authority data in `notes`.

### D. Graceful degradation contract is sufficient

Section 6's requirement that Azure CLI failures degrade to unknown consistency without failing dashboard refresh is correct.

Implementation note: the proposal says `refresh_runs` records `result='success'`; the current table uses a `status` field with values such as `completed` / `failed`. That is a wording bug, not a design blocker.

## Blocking Issue: Dry-Runs And Failed Pre-Deploy Manifests Must Not Become Deployments

Section 4.2 says `_ingest_canonical_pipeline_manifests()` walks `logs/deploy-result-{env}-*.json` and emits `delivery_timeline_events` rows with `event_kind='canonical_deploy'`.

Section 7 then says Track 2 can land first using the existing manifest, with rows such as:

- `_authority_source='canonical_manifest'`
- `_image_ref=''`
- `_revision_name=''`
- `_deployed_at=''`
- `_confidence='medium'`

That is unsafe as written because existing deploy-result manifests are not all actual deployments.

Evidence:

- `scripts/deploy_pipeline.py:1546-1578` writes a manifest for every pipeline run after summary generation, regardless of whether deployment reached the target.
- The manifest includes `dry_run`.
- The manifest includes `status`.
- The manifest includes per-phase status/duration/detail rows.
- A current sample manifest in `logs/deploy-result-production-1775695786.json` is `dry_run: true`, `status: "FAILED"`, and stopped at phase 0 validation. It is a canonical pipeline run, but it is not a deployment.

Impact:

If Track 2 ingests every manifest as `canonical_deploy`, DORA deployment frequency will count:

- dry-run rehearsals,
- validation failures,
- build failures,
- protected-behavior gate failures,
- any other pipeline run that never reached `phase_8_deploy`.

That would recreate the same class of telemetry defect this work is meant to remove: a structured but false deployment signal.

## Required Correction

The revised scope must define a row classification contract for manifest ingest before GO.

Minimum acceptable contract:

1. **Dry-runs are not deployments.** If `dry_run == true`, the row must not be emitted as `event_kind='canonical_deploy'`. It may be skipped or emitted as a separate non-DORA deployment event kind such as `canonical_pipeline_run`, but it must not feed deployment-frequency math.
2. **Failed pre-deploy runs are not deployments.** A manifest with no actual deploy phase attempt must not become `canonical_deploy`.
3. **Deploy-attempt failures are distinct from successful deploys.** A manifest where `phase_8_deploy` attempted a real target update but failed may be represented as a deploy attempt or failed deploy, but the contract must state how later DORA metrics will include or exclude it.
4. **Successful deploy rows require target evidence.** For Track 2 before manifest enhancement, a successful `canonical_deploy` row must at minimum require:
   - `dry_run == false`,
   - deploy phase present,
   - deploy phase status PASS,
   - version/image evidence derivable from existing fields,
   - `_confidence` no higher than `medium` until `_deployed_at` and `_revision_name` are populated.
5. **Track 1 should make this explicit.** The enhanced `deploy_evidence` block should include a boolean or enum such as `target_update_attempted`, `target_update_succeeded`, and `target_verified_at`, so dashboard ingest does not infer deployment status from free-text phase names.

## Review Ask Responses

1. Finding A: **confirmed fixed** by the audit table and manifest-extension plan.
2. Finding B: **directionally confirmed**, but Track 2's intermediate state needs the dry-run / failed-run contract above.
3. Finding C: **confirmed sufficient** at scoping level, subject to the corrected row classification contract.
4. Finding D: **confirmed sufficient**.
5. Sequencing: **not confirmed as written**. Track 2 can still go first, but only after the proposal states that existing manifests are filtered/classified so non-deploy pipeline runs do not become `canonical_deploy`.
6. Status: **NO-GO** on `-003` as written.

## Required Next Prime Action

File a revised proposal that adds the manifest-ingest classification contract for:

- dry-run pipeline runs,
- failed pre-deploy runs,
- failed deploy attempts,
- successful target-reaching deployments,
- confidence levels before and after manifest enhancement.

Once that is explicit, the revised A-primary / C-reconciliation design is likely GO-able.
