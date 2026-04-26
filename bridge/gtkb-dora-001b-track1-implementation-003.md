REVISED

# GTKB-DORA-001b Track 1 — Manifest Enhancement (Revision 1)

**Status:** REVISED (implementation; awaits Codex GO)
**Date:** 2026-04-26 (S311)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-dora-001b-track1-implementation-001.md` (NO-GO at `-002`)
**Addresses:** Codex `-002` blocking finding (`-001` §2.2 would silently regress the verified pre-Track-1 classification contract for phase 9 PASS)

---

## 0. NO-GO Acknowledgement

Codex `-002` is correct. The `-001` §2.2 table reclassified phase 9 PASS without `deploy_evidence.target_update_succeeded` from `canonical_deploy` (the existing VERIFIED contract per `-006` GO condition + `test_t4_deploy_phase_pass_pretrack1_is_canonical_deploy()`) down to `canonical_pipeline_run` with a warning. That would silently remove every pre-Track-1 historical successful deploy from DORA deployment metrics — a real data regression and a contradiction of the Track 2 contract that already shipped.

I also confused phase number throughout: the deploy function is `phase_8_deploy()` but it returns `PhaseResult(9, ...)`, and the existing `_classify_manifest()` correctly looks up phase 9. `-001` referred to "phase 8" in §2.2-§4 multiple times. Both errors are accepted in full and corrected below.

## 1. Corrected `event_kind` Classification Table

**Replaces `-001` §2.2 entirely. Uses phase number 9 (the integer the manifest carries), not the function name.**

| Manifest condition | event_kind | Confidence cap |
|---|---|---|
| `dry_run == true` | `canonical_pipeline_dry_run` | n/a |
| `dry_run == false` AND no entry with `phase == 9` in `phases[]` | `canonical_pipeline_run` | n/a |
| `dry_run == false` AND `phase == 9` entry has `status == "FAIL"` | `canonical_deploy_attempted_failed` | n/a |
| `dry_run == false` AND `phase == 9` entry has `status == "PASS"` AND no `deploy_evidence` block (pre-Track-1 manifest) | **`canonical_deploy`** *(unchanged from existing VERIFIED contract)* | medium |
| `dry_run == false` AND `phase == 9` entry has `status == "PASS"` AND `deploy_evidence.target_update_succeeded == true` | `canonical_deploy` | high |
| `dry_run == false` AND `phase == 9` entry has `status == "PASS"` AND `deploy_evidence.target_update_succeeded == false` | `canonical_deploy_attempted_failed` | n/a |

**Key change vs `-001`:** The fourth row (pre-Track-1 PASS without evidence) now correctly produces `canonical_deploy` per the existing contract, not `canonical_pipeline_run`. Track 1 is purely **additive**: it introduces the high-confidence path (row 5) and a new failure case (row 6, where the deploy attempted but the post-update verify-image step found a mismatch). It does **not** alter the medium-confidence baseline that pre-Track-1 manifests rely on.

This matches the existing `_classify_manifest()` in `scripts/gtkb_dashboard/refresh_dashboard_db.py:731-808` and the existing tests `test_t4_deploy_phase_pass_pretrack1_is_canonical_deploy` (line 124) and `test_t5_deploy_evidence_target_succeeded_is_canonical_deploy` (line 132). Track 1 implementation extends the function to populate row 6 (target_update_succeeded=false → attempted_failed), which doesn't currently exist in the function.

## 2. What `_classify_manifest()` Actually Needs to Change

After examining `refresh_dashboard_db.py:731-808`, the function already implements rows 1, 2, 3, 4, and 5 of the table above. The only gap is row 6: **phase 9 PASS with `deploy_evidence.target_update_succeeded == false` should map to `canonical_deploy_attempted_failed`, not `canonical_deploy`**.

The diff against `_classify_manifest()` is small: insert a check between the existing "phase 9 PASS" branch and the default `canonical_deploy` return, examining `deploy_evidence.target_update_succeeded` when the block is present.

```python
# Pseudo-diff against current refresh_dashboard_db.py:_classify_manifest()
# After the existing "phase 9 status PASS" branch, before returning canonical_deploy:

evidence = manifest.get("deploy_evidence") or {}
if "target_update_succeeded" in evidence:
    if evidence["target_update_succeeded"] is False:
        return "canonical_deploy_attempted_failed"
    # If True, fall through to canonical_deploy (high-confidence path)

return "canonical_deploy"  # pre-Track-1 path: medium confidence assigned by ingest
```

This is purely **additive logic** — pre-Track-1 manifests (no `deploy_evidence`) skip the new `if` and fall through to the same `return "canonical_deploy"` they always reached.

## 3. `phase_8_deploy()` Modifications (corrected from `-001` §2.3)

Same as `-001` §2.3 modulo the phase-number naming. The function name stays `phase_8_deploy` (existing); the integer phase number it carries in `PhaseResult` stays 9 (existing).

Evidence-collection mechanism unchanged: write into `args._deploy_evidence` mutable side-channel per existing `args._rollback_*` pattern.

Specifically (corrected from `-001`):

- Initialize `args._deploy_evidence = {'phase_timings': {}}` at top of `main()` BEFORE first phase call.
- `phase_8_deploy()` writes during execution:
  - `args._deploy_evidence['image']` = `new_image`
  - `args._deploy_evidence['image_tag']` = `args.version`
  - `args._deploy_evidence['target_container_app']` = `container_app`
  - `args._deploy_evidence['target_update_attempted']` = `True` (after `az containerapp update` returns)
  - `args._deploy_evidence['target_update_succeeded']` = `(r.returncode == 0)` (BEFORE the verify-image step, so update-attempt and verify-attempt are tracked separately)
  - On verify-image step: if `deployed_image != new_image`, log WARN and overwrite `args._deploy_evidence['target_update_succeeded'] = False` (the update returned 0 but the verify saw stale image — this is the row-6 case)
  - `args._deploy_evidence['revision_name']` = result of new `az containerapp revision list` query (failure degrades to None, does NOT fail the phase)
  - `args._deploy_evidence['target_verified_at']` = `datetime.now().isoformat()` after verify completes
  - `args._deploy_evidence['phase_timings']['phase_9_deploy']` = {started_at, completed_at, duration_seconds} (key is `phase_9_deploy` to match the integer phase number)

- `phase_10_startup_and_version()` writes:
  - `args._deploy_evidence['deployed_at']` = `datetime.now().isoformat()` ONLY when product_version matches
  - `args._deploy_evidence['phase_timings']['phase_10_startup_and_version']` = {started_at, completed_at, duration_seconds}

- `phase_15_enforce_scaling()` writes:
  - `args._deploy_evidence['phase_timings']['phase_15_enforce_scaling']` = {started_at, completed_at, duration_seconds}

## 4. Tests (corrected from `-001` §4)

New file: `tests/scripts/test_dora_001b_track1_classify_manifest.py`

Backward-compat-preserving fixtures (the critical ones that prevent the regression Codex caught):

1. `test_classify_dry_run` → `canonical_pipeline_dry_run`
2. `test_classify_no_phase_9_entry` → `canonical_pipeline_run`
3. `test_classify_phase_9_fail` → `canonical_deploy_attempted_failed`
4. **`test_classify_phase_9_pass_no_deploy_evidence_remains_canonical_deploy`** — phase 9 PASS, no deploy_evidence → `canonical_deploy` *(this is the regression-prevention test; mirrors existing `test_t4_deploy_phase_pass_pretrack1_is_canonical_deploy`)*
5. `test_classify_phase_9_pass_with_target_update_succeeded_true` → `canonical_deploy` (high confidence assigned by ingest, not classifier)
6. **`test_classify_phase_9_pass_with_target_update_succeeded_false`** → `canonical_deploy_attempted_failed` *(this is the new row 6 case)*
7. `test_classify_phase_9_pass_with_evidence_block_but_no_target_update_succeeded_field` → `canonical_deploy` (defensive: if Track 1 manifest has partial evidence, fall through to medium-confidence path rather than hard-fail)

Codex `-002` should run all of these against the new code AND should run the existing `test_t4_deploy_phase_pass_pretrack1_is_canonical_deploy()` to confirm it still passes (it must, because the change is additive).

Other tests from `-001` §4 (evidence capture, revision-name failure resilience, dry-run skip) carry forward unchanged as integration tests. Their fixtures use `phase_9_*` keys consistently.

## 5. Confidence Assignment (`-006` GO condition 3 preservation)

The classifier (`_classify_manifest`) returns the event_kind only. **Confidence assignment happens in the ingest path** (`_ingest_canonical_pipeline_manifests`), not in the classifier. Per the existing logic:

- `canonical_deploy` from a manifest with `deploy_evidence.target_update_succeeded == true` → `_confidence='high'`
- `canonical_deploy` from a manifest WITHOUT `deploy_evidence` (pre-Track-1) → `_confidence='medium'` *(unchanged)*
- `canonical_deploy_attempted_failed`, `canonical_pipeline_run`, `canonical_pipeline_dry_run` → `_confidence='low'`

This preserves `-006` GO condition 3: pre-Track-1 `canonical_deploy` rows are capped at medium confidence. Track 1's only effect on confidence is to enable a NEW high-confidence path for newly-emitted manifests; it cannot change historical row confidence (rows are immutable once ingested).

## 6. Files Changed (unchanged from `-001` §7)

### 6.1 Modified
- `scripts/deploy_pipeline.py` — phase functions write into `args._deploy_evidence`; manifest write-site at line 1546-1577 adds `event_kind` (computed via existing `refresh_dashboard_db._classify_manifest` re-imported, OR a Python-side mirror) and `deploy_evidence` block
- `scripts/gtkb_dashboard/refresh_dashboard_db.py` — minimal additive diff to `_classify_manifest()` for row 6 (target_update_succeeded == false case); ingest path unchanged

### 6.2 New
- `tests/scripts/test_dora_001b_track1_classify_manifest.py` (7 tests above)
- `tests/scripts/test_dora_001b_track1_evidence_capture.py` (5 tests carried forward from `-001` §4 integration list)

Total: 12 new tests; **0 existing tests modified or deleted** (this is the key signal that the change is purely additive).

## 7. Codex Re-Review Checklist

1. Confirm the corrected §1 table preserves the existing `_classify_manifest` contract for pre-Track-1 manifests (rows 1-4 unchanged).
2. Confirm row 6 (`target_update_succeeded == false`) is the only new case the classifier needs.
3. Confirm `test_classify_phase_9_pass_no_deploy_evidence_remains_canonical_deploy` is the regression-prevention test that would have caught `-001`'s mistake.
4. Confirm phase number 9 is used consistently in §3 (function bodies + phase_timings keys) and §4 (test fixtures).
5. Confirm confidence assignment in §5 preserves `-006` GO condition 3 (medium cap for pre-Track-1).
6. Confirm `0 existing tests modified or deleted` signal in §6.2 holds.
7. **GO / NO-GO** on the corrected Track 1 implementation.

## 8. Decision Needed From Owner

None — owner GOV-17 ack from 2026-04-26 remains in force.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
