REVISED

# GTKB-DORA-001b Track 1 — Manifest Writer Enhancement (Revision 2)

**Status:** REVISED (implementation; awaits Codex GO)
**Date:** 2026-04-26 (S311)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-dora-001b-track1-implementation-003.md` (NO-GO at `-004`)
**Addresses:** Codex `-004` blocking finding (`-003` §1 + §5 introduced a confidence-contract conflict by saying ingest assigns `_confidence='high'` when full evidence present; existing contract is that ingest ALWAYS emits `medium`, and only Azure reconciliation upgrades to `high`)

---

## 0. NO-GO Acknowledgement + Scope Correction

Codex `-004` is correct. The `-003` §5 confidence rules contradicted the existing VERIFIED contract in two places:

1. Said full deploy_evidence at ingest → `_confidence='high'`. Actual contract per `_confidence_for_canonical_deploy()` at `scripts/gtkb_dashboard/refresh_dashboard_db.py:781-789`: returns `medium` ALWAYS, including with full evidence. Test `test_t13_ingest_emits_medium_then_reconcile_upgrades_to_high` asserts this.
2. Said `canonical_deploy_attempted_failed` → `_confidence='low'`. Actual contract: code assigns `medium` (and there was no separate justification for changing it).

**Bigger insight from re-reading the source code (`refresh_dashboard_db.py:731-778`) more carefully:** the existing `_classify_manifest()` already implements **every row of the §1 table** in `-003`, including the row 6 case (PASS with `target_update_succeeded=false` → `canonical_deploy_attempted_failed`). It does this at lines 761-773. **Track 1 needs zero changes to `_classify_manifest()` and zero changes to confidence assignment.**

The only thing Track 1 actually needs to change is the **manifest writer** in `scripts/deploy_pipeline.py`: today it produces manifests WITHOUT a `deploy_evidence` block; Track 1 enhances the writer to populate the block so the classifier can use the high-fidelity branch instead of the pre-Track-1 fallback.

This revision corrects the scope: Track 1 is a **writer enhancement only**, not a classifier change.

## 1. Classification + Confidence Contract (NO CHANGE)

The existing classifier and confidence function already implement the right contract. Quoting them verbatim for the audit trail:

```python
# scripts/gtkb_dashboard/refresh_dashboard_db.py:761-773
if status == "PASS":
    # Track 1 enhanced manifest: prefer the explicit booleans.
    evidence = manifest.get("deploy_evidence", {}) or {}
    if evidence.get("target_update_attempted") is True:
        if evidence.get("target_update_succeeded") is True:
            return "canonical_deploy"
        return "canonical_deploy_attempted_failed"
    # Pre-Track-1 manifest: phase-8 PASS without evidence block.
    return "canonical_deploy"
```

```python
# scripts/gtkb_dashboard/refresh_dashboard_db.py:781-789
def _confidence_for_canonical_deploy(manifest: dict[str, Any]) -> str:
    """Per Codex -006 condition 3: pre-Track-1 deploy rows must not exceed
    'medium'. Even with full deploy_evidence, ingest emits provisional
    'medium'; reconciliation upgrades to 'high' only when Azure revision
    matches (per `_reconcile_against_azure_revisions` confidence-upgrade rule).
    """
    return "medium"
```

**Track 1 makes ZERO modifications to either function.** Both already handle Track 1 manifests correctly. The Source A → Source C reconciliation contract from the GO'd `-007` addendum (where `_confidence='high'` is reserved for Azure-revision-confirmed rows) is preserved exactly.

`canonical_deploy_attempted_failed` confidence stays at whatever the existing code assigns (Codex notes `medium`); Track 1 makes no change there either.

## 2. What Track 1 Actually Modifies — `scripts/deploy_pipeline.py` Only

The single goal of Track 1: produce manifests with a `deploy_evidence` block so the classifier exercises the Track-1-aware branch (lines 763-767) instead of the pre-Track-1 fallback (line 773).

### 2.1 Initialize evidence dict at top of `main()`

```python
# Top of main() in scripts/deploy_pipeline.py, BEFORE first phase call:
args._deploy_evidence = {"phase_timings": {}}
```

This follows the existing pattern of `args._rollback_*` attributes already used at lines 1567-1569.

### 2.2 `phase_8_deploy()` populates evidence during execution

(The function name stays `phase_8_deploy()`; the integer phase number it reports stays 9.)

After `args = ENVIRONMENTS[args.env]; container_app = env_config["container_app"]; new_image = ...`:

```python
# Add to args._deploy_evidence as the function progresses:
args._deploy_evidence["image"] = new_image
args._deploy_evidence["image_tag"] = args.version
args._deploy_evidence["target_container_app"] = container_app
phase_t0 = time.time()
# ... existing dry_run check unchanged ...

# After `r = _run([...az containerapp update...])`:
args._deploy_evidence["target_update_attempted"] = True
args._deploy_evidence["target_update_succeeded"] = (r.returncode == 0)

# After verify-image step (existing code), if deployed_image != new_image:
args._deploy_evidence["target_update_succeeded"] = False  # downgrade

# New: query revision name (failure non-fatal):
r3 = _run([
    "az", "containerapp", "revision", "list",
    "--name", container_app,
    "--resource-group", RESOURCE_GROUP,
    "--query", f"[?properties.template.containers[0].image=='{new_image}'].name | [0]",
    "-o", "tsv",
], timeout=30)
if r3.returncode == 0 and r3.stdout.strip():
    args._deploy_evidence["revision_name"] = r3.stdout.strip()
args._deploy_evidence["target_verified_at"] = datetime.now().isoformat()
args._deploy_evidence["phase_timings"]["phase_9_deploy"] = {
    "started_at": datetime.fromtimestamp(phase_t0).isoformat(),
    "completed_at": datetime.now().isoformat(),
    "duration_seconds": round(time.time() - phase_t0, 1),
}
```

### 2.3 `phase_10_startup_and_version()` records `deployed_at`

In the existing successful-version-match branch (where it currently returns PASS), add:

```python
if hasattr(args, "_deploy_evidence"):
    args._deploy_evidence["deployed_at"] = datetime.now().isoformat()
    args._deploy_evidence["phase_timings"]["phase_10_startup_and_version"] = {
        "started_at": datetime.fromtimestamp(phase_t0).isoformat(),
        "completed_at": datetime.now().isoformat(),
        "duration_seconds": round(time.time() - phase_t0, 1),
    }
```

### 2.4 `phase_15_enforce_scaling()` records phase timing only

```python
if hasattr(args, "_deploy_evidence"):
    args._deploy_evidence["phase_timings"]["phase_15_enforce_scaling"] = {...}
```

### 2.5 Manifest write site at line 1546-1573 — add `deploy_evidence`

Existing `deploy_result` dict construction continues unchanged. After it's built, before `result_path.write_text(json.dumps(deploy_result, indent=2))`:

```python
if hasattr(args, "_deploy_evidence") and args._deploy_evidence:
    deploy_result["deploy_evidence"] = args._deploy_evidence
```

**Note:** I am NOT computing `event_kind` at deploy_pipeline.py side. The existing dashboard ingest path already classifies manifests via `_classify_manifest()` at ingest time; doing it again at write time would duplicate logic without benefit. (This drops the `event_kind` top-level field I had in `-003` §2.5; that field was redundant.)

## 3. Tests

### 3.1 `tests/scripts/test_dora_001b_track1_writer.py` (new)

Focused on the WRITER side — does `deploy_pipeline.py` populate the evidence dict correctly?

1. `test_evidence_dict_initialized_in_main` — after `main()` start, `args._deploy_evidence` exists with `phase_timings={}` empty dict
2. `test_phase_8_populates_image_and_tag` — mock `phase_8_deploy()` execution; assert `args._deploy_evidence['image']` and `image_tag` set
3. `test_phase_8_populates_target_update_attempted_after_az_update` — mock az returncode 0; assert `target_update_attempted=True` and `target_update_succeeded=True`
4. `test_phase_8_target_update_succeeded_false_when_az_returncode_nonzero` — mock az returncode 1; assert `target_update_attempted=True` and `target_update_succeeded=False`
5. `test_phase_8_target_update_succeeded_downgraded_on_image_mismatch` — mock az succeeds but verify-image returns different image; assert `target_update_succeeded=False`
6. `test_phase_8_revision_name_captured_when_az_query_succeeds` — mock revision-list returns name; assert `revision_name` populated
7. `test_phase_8_revision_name_failure_does_not_fail_phase` — mock revision-list returns nonzero; assert `revision_name` not in evidence AND phase still returns PASS PhaseResult
8. `test_phase_8_phase_timings_captured` — assert `phase_timings.phase_9_deploy` has started_at/completed_at/duration_seconds
9. `test_phase_10_records_deployed_at_on_version_match` — mock health endpoint returns matching version; assert `deployed_at` set
10. `test_phase_10_does_not_record_deployed_at_on_version_mismatch` — mock health returns mismatched version; assert `deployed_at` NOT set
11. `test_phase_15_records_phase_timing` — assert phase_timings.phase_15_enforce_scaling populated
12. `test_main_emits_manifest_with_deploy_evidence_block` — full main() with mocked az; resulting manifest JSON contains `deploy_evidence` key
13. `test_dry_run_does_not_populate_evidence` — `--dry-run` mode produces manifest WITHOUT `deploy_evidence` (or with empty)

### 3.2 Backward-compat regression test (in existing test file)

Add to `tests/scripts/test_dora_001b_track2_ingest.py`:

14. `test_pre_track1_manifest_still_classified_as_canonical_deploy` — synthesize an old-style manifest (PASS phase 9, NO `deploy_evidence`); assert `_classify_manifest()` returns `canonical_deploy` AND ingest assigns `_confidence='medium'`. This is regression armor.
15. `test_track1_manifest_with_full_evidence_still_capped_at_medium_until_reconcile` — synthesize a Track 1 manifest with `target_update_succeeded=true`; assert ingest emits `_confidence='medium'` (NOT `high`). High only after Azure reconciliation upgrades. This is the regression armor for the very mistake -003 made.

Tests 1-13 are new; tests 14-15 add to existing file. Total new tests: 15. **Existing tests modified or deleted: 0.**

## 4. Files Changed

### 4.1 Modified
- `scripts/deploy_pipeline.py` — initialize `args._deploy_evidence` in `main()`; populate during phase_8/10/15; inject into `deploy_result` at write site

### 4.2 New
- `tests/scripts/test_dora_001b_track1_writer.py` (13 tests)

### 4.3 Modified (additions only)
- `tests/scripts/test_dora_001b_track2_ingest.py` (+2 regression tests for backward-compat assertions)

### 4.4 Untouched
- `scripts/gtkb_dashboard/refresh_dashboard_db.py` (`_classify_manifest()` and `_confidence_for_canonical_deploy()` are unchanged — they already handle Track 1 manifests correctly)
- All existing tests
- DORA-002 KPI query work (separate work item)

## 5. Confidence Contract Re-Statement (per Codex `-004` ask)

For absolute clarity, the confidence contract Track 1 preserves exactly:

| Source manifest | Ingest emits | After Azure reconcile | Reason |
|---|---|---|---|
| Pre-Track-1 (PASS, no evidence) | `_confidence='medium'` | `medium` (no upgrade path; no revision_name to match) | Per `-006` GO condition 3 cap |
| Track 1 (PASS, target_update_succeeded=true, revision_name set) | `_confidence='medium'` | `medium` if no Azure match; **`high` if revision_name matches Azure revision** | Per `_007 §4.2 Source C reconciliation contract |
| Track 1 (PASS, target_update_succeeded=false) | `canonical_deploy_attempted_failed` row, current `_confidence` (medium per existing code) | unchanged | Track 1 makes no change to attempted_failed confidence |
| Phase 9 FAIL or no phase 9 | `canonical_deploy_attempted_failed` or `canonical_pipeline_run` | unchanged | Existing logic |

Track 1's only effect on the dashboard data: **manifests written by post-Track-1 deploys will have `revision_name` populated, which enables Azure reconciliation to match and upgrade to high. Pre-Track-1 manifests (already on disk) remain at medium forever, which is the intended behavior — they did not capture the revision_name needed for reconciliation.**

## 6. Codex Re-Review Checklist

1. Confirm §2 modifications are limited to `scripts/deploy_pipeline.py` (writer side only).
2. Confirm `_classify_manifest()` and `_confidence_for_canonical_deploy()` are NOT modified.
3. Confirm the confidence contract table in §5 matches the existing code behavior + the GO'd Source A/C reconciliation contract from `-007`.
4. Confirm tests 14-15 in §3.2 are appropriately scoped as regression armor against the kind of mistake `-003` made.
5. Confirm 0 existing tests modified or deleted (additive change only).
6. **GO / NO-GO** on the corrected Track 1 implementation scope.

## 7. Decision Needed From Owner

None — owner GOV-17 ack from 2026-04-26 remains in force.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
