# Loyal Opposition Response: GTKB-DORA-001b Track 1 Implementation Revision 1

Status: NO-GO

## Claim

`bridge/gtkb-dora-001b-track1-implementation-003.md` fixes the prior pre-Track-1 classification regression, but it introduces a new confidence-contract conflict. It is not approved as written.

## Evidence

- The revision correctly restores the key classification rule: phase 9 PASS without `deploy_evidence` remains `canonical_deploy`.
- The current implementation in `scripts/gtkb_dashboard/refresh_dashboard_db.py` already preserves that rule and also already maps phase 9 PASS with `deploy_evidence.target_update_attempted == true` and `target_update_succeeded == false` to `canonical_deploy_attempted_failed`.
- `python -m pytest tests/scripts/test_dora_001b_track2_ingest.py -q --tb=short` passed: 16 tests passed.
- Existing test `test_t13_ingest_emits_medium_then_reconcile_upgrades_to_high` proves the current confidence contract:
  - ingest emits `_confidence='medium'` even with full deploy evidence;
  - Azure revision reconciliation upgrades matching rows to `_confidence='high'`.
- The revision conflicts with that contract:
  - Section 1 lists phase 9 PASS plus `deploy_evidence.target_update_succeeded == true` with high confidence.
  - Section 5 says `canonical_deploy` from a manifest with `deploy_evidence.target_update_succeeded == true` becomes `_confidence='high'`.
  - Section 5 also says `canonical_deploy_attempted_failed` becomes `_confidence='low'`, while the current ingest path assigns it `medium`.

## Risk / Impact

Approving this text would weaken the already-approved Source A / Source C split. Source A manifest evidence can establish a canonical deploy row, but high confidence is supposed to require Azure revision reconciliation. Granting high confidence at ingest would remove that independent production-target confirmation step.

The attempted-failed confidence mismatch is also an implementation ambiguity: current code assigns `medium`, while the proposal says `low`.

## Recommended Action

Revise the Track 1 bridge again:

- Keep phase 9 PASS without `deploy_evidence` as `canonical_deploy`.
- Keep phase 9 PASS plus `target_update_succeeded == false` as `canonical_deploy_attempted_failed`.
- State explicitly that ingest continues to emit `_confidence='medium'` for `canonical_deploy`, including full Track 1 evidence.
- State that `_confidence='high'` is only assigned after Azure revision reconciliation confirms the manifest image/revision.
- Align attempted-failed confidence with the intended code contract, either by preserving current `medium` or proposing a deliberate, separately justified change to `low`.

## Decision Needed From Owner

None.
