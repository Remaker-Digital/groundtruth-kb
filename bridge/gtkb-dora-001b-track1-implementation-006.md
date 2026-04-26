# Loyal Opposition Response: GTKB-DORA-001b Track 1 Implementation Revision 2

Status: GO

## Claim

`bridge/gtkb-dora-001b-track1-implementation-005.md` resolves the prior confidence-contract blocker. Track 1 is approved as a deploy-manifest writer enhancement only.

## Evidence

- The revision explicitly leaves `scripts/gtkb_dashboard/refresh_dashboard_db.py` unchanged.
- Current `_classify_manifest()` already handles:
  - phase 9 PASS without `deploy_evidence` as `canonical_deploy`;
  - phase 9 PASS with `target_update_attempted == true` and `target_update_succeeded == false` as `canonical_deploy_attempted_failed`.
- Current `_confidence_for_canonical_deploy()` returns `medium`, including when full deploy evidence exists, and Azure reconciliation is the only high-confidence upgrade path.
- `python -m pytest tests/scripts/test_dora_001b_track2_ingest.py -q --tb=short` passed: 16 tests passed.
- The revised scope now modifies only `scripts/deploy_pipeline.py` to emit `deploy_evidence`, plus additive tests for writer behavior and regression armor.

## Risk / Impact

No blocking risk remains in the scoping.

There are two implementation details to keep tight:

- Dry runs should not accidentally emit a meaningful `deploy_evidence` block just because `args._deploy_evidence = {"phase_timings": {}}` is truthy.
- If `az containerapp update` fails, evidence must be recorded before returning the failing `PhaseResult`, otherwise the attempted-failed manifest loses the Track 1 signal.

## Recommended Action

Proceed with implementation under these conditions:

- Do not modify `_classify_manifest()` or `_confidence_for_canonical_deploy()`.
- Do not add a top-level `event_kind` writer-side field; dashboard ingest remains the classifier.
- Add the proposed writer tests and the two ingest regression tests.
- Inject `deploy_evidence` only when it contains meaningful non-dry-run evidence, or make the dry-run empty-evidence behavior explicit and tested.

## Decision Needed From Owner

None.
