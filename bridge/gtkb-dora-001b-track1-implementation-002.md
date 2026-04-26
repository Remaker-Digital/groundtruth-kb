# Loyal Opposition Response: GTKB-DORA-001b Track 1 Implementation

Status: NO-GO

## Claim

`bridge/gtkb-dora-001b-track1-implementation-001.md` is not approved as written because it would regress the already-approved and verified Track 2 classification contract for pre-Track-1 deployment manifests.

## Evidence

- `bridge/gtkb-dora-001b-authoritative-deployment-source-005.md` explicitly classifies the pre-Track-1 deploy phase PASS manifest, represented as phase number 9 and lacking `deploy_evidence`, as `canonical_deploy` with medium confidence.
- `bridge/gtkb-dora-001b-authoritative-deployment-source-006.md` approved that implementation condition and required pre-Track-1 `canonical_deploy` rows to remain capped at medium confidence.
- Current implementation in `scripts/gtkb_dashboard/refresh_dashboard_db.py` keeps `_DORA_DEPLOYMENT_EVENT_KINDS = frozenset({"canonical_deploy"})`, classifies phase 9 PASS without `deploy_evidence` as `canonical_deploy`, and assigns medium confidence to canonical deploy rows.
- Current test coverage in `tests/scripts/test_dora_001b_track2_ingest.py` includes `test_t4_deploy_phase_pass_pretrack1_is_canonical_deploy()`, which asserts that phase 9 PASS without deploy evidence remains a canonical deploy.
- The new Track 1 proposal conflicts with that verified behavior:
  - Section 2.2 says only phase 8 PASS plus `deploy_evidence.target_update_succeeded == true` becomes `canonical_deploy`.
  - Section 2.2 sends other inconsistent states to `canonical_pipeline_run`.
  - Section 4 proposes `test_classify_deploy_phase_pass_pre_track1`, expecting PASS with no `deploy_evidence.target_update_succeeded` to become `canonical_pipeline_run` with a warning.

## Risk / Impact

This would silently remove historic pre-Track-1 successful deploy-phase manifests from deployment metrics. That is a DORA data regression and contradicts the already-approved Track 2 contract.

The phase naming is also easy to misread: the deploy function is named `phase_8_deploy()`, but the current manifest phase number is 9. Existing code and tests correctly use phase number 9 for this path.

## Recommended Action

Revise the Track 1 implementation plan so it preserves the existing `_classify_manifest()` contract:

- Phase 9 PASS without `deploy_evidence` remains `canonical_deploy` with medium confidence.
- Track 1 adds enhanced `deploy_evidence` handling and tests without reclassifying historical manifests.
- New tests should include both the enhanced evidence path and the backward-compatibility path for pre-Track-1 manifests.

## Decision Needed From Owner

None.
