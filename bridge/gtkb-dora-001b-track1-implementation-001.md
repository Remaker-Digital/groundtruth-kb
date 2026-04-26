NEW

# GTKB-DORA-001b Track 1 — Manifest Enhancement (Implementation Proposal)

**Status:** NEW (implementation proposal awaiting Codex GO)
**Date:** 2026-04-26 (S311)
**Author:** Prime Builder (Claude Opus 4.7)
**Work item:** GTKB-DORA-001b
**Bridge kind:** implementation_proposal
**Builds on:**
- `bridge/gtkb-dora-001b-authoritative-deployment-source-006.md` (scoping GO)
- `bridge/gtkb-dora-001b-authoritative-deployment-source-007.md` (NEW comparative scoping addendum, Source A primary confirmed by owner 2026-04-26)
**Owner pre-approvals:**
- 2026-04-26 GOV-17 ack: Track 1 may modify `scripts/deploy_pipeline.py`
- 2026-04-26 source-shape: Source A primary, Source C reconcile, Source B deferred to GTKB-DORA-001c

bridge_kind: implementation_proposal
work_item_ids: [GTKB-DORA-001b]
spec_ids: []
target_project: agent-red
implementation_scope: deployment-pipeline + dashboard-ingest

---

## 1. Scope

Modify `scripts/deploy_pipeline.py` to emit structured `deploy_evidence` block and `event_kind` classification in its `logs/deploy-result-{env}-{int(start_time)}.json` manifest. Update dashboard ingest at `scripts/gtkb_dashboard/refresh_dashboard_db.py` to read the new fields with classification gating. Add the test fixtures Codex `-006` GO required.

**Out of scope (separate bridges):**
- Track 2 dashboard ingest core (already VERIFIED at `gtkb-dora-001b-track2-implementation-008`)
- ACA reconciliation (already in Track 2)
- GH Actions out-of-band detection (deferred to GTKB-DORA-001c per owner 2026-04-26)
- DORA-002 KPI queries (separate work item)

## 2. Contract Changes

### 2.1 Manifest JSON additions (top-level)

Add to the `deploy_result` dict at `scripts/deploy_pipeline.py:1546-1573`:

```json
{
  "version": "v1.99.0",
  "environment": "production",
  "status": "SUCCESS",
  "...": "...existing fields unchanged...",
  "event_kind": "canonical_deploy",
  "deploy_evidence": {
    "image": "acragentredeastus.azurecr.io/agent-red:v1.99.0",
    "image_tag": "v1.99.0",
    "revision_name": "agent-red-api-gateway--v1-99-0-abc12",
    "target_container_app": "agent-red-api-gateway",
    "target_update_attempted": true,
    "target_update_succeeded": true,
    "target_verified_at": "2026-04-26T07:35:02.123456",
    "deployed_at": "2026-04-26T07:36:18.987654",
    "phase_timings": {
      "phase_8_deploy": {
        "started_at": "2026-04-26T07:34:55.123456",
        "completed_at": "2026-04-26T07:35:02.123456",
        "duration_seconds": 7.0
      },
      "phase_10_startup_and_version": {
        "started_at": "2026-04-26T07:35:02.456789",
        "completed_at": "2026-04-26T07:36:18.987654",
        "duration_seconds": 76.5
      },
      "phase_15_enforce_scaling": {
        "started_at": "2026-04-26T07:36:19.123456",
        "completed_at": "2026-04-26T07:36:24.555555",
        "duration_seconds": 5.4
      }
    }
  }
}
```

### 2.2 `event_kind` classification table (per `-005` §5.5 + `-006` GO)

Computed in `_classify_manifest(deploy_result: dict) -> str` (new helper at module level near the manifest writer):

| Manifest condition | event_kind |
|---|---|
| `dry_run == true` | `canonical_pipeline_dry_run` |
| `dry_run == false` AND no `phase_8_deploy` row in `phases[]` | `canonical_pipeline_run` |
| `dry_run == false` AND `phase_8_deploy.status == "FAIL"` | `canonical_deploy_attempted_failed` |
| `dry_run == false` AND `phase_8_deploy.status == "PASS"` AND `deploy_evidence.target_update_succeeded == true` | `canonical_deploy` |
| any other inconsistent state (defensive) | `canonical_pipeline_run` (with warning log) |

The classifier runs at manifest-write time (line 1577 area), AFTER `deploy_result` is fully populated.

### 2.3 Evidence-collection mechanism

Phase functions write into a process-local mutable `args._deploy_evidence: dict` (new attribute), following the existing pattern of `args._rollback_attempted` etc. at lines 1567-1569. This avoids changing the `PhaseResult` dataclass shape (which is also serialized in `phases[]` and would create schema churn).

Specifically:

- `phase_8_deploy()` writes:
  - `args._deploy_evidence['image'] = new_image`
  - `args._deploy_evidence['image_tag'] = args.version`
  - `args._deploy_evidence['target_container_app'] = container_app`
  - `args._deploy_evidence['target_update_attempted'] = True` (after the `az containerapp update` call returns)
  - `args._deploy_evidence['target_update_succeeded'] = (r.returncode == 0)` (BEFORE the verify-image step, so we know update succeeded vs verify-image succeeded distinctly)
  - `args._deploy_evidence['revision_name'] = <queried via new az command>` (see §2.4)
  - `args._deploy_evidence['target_verified_at'] = datetime.now().isoformat()` (after the `az containerapp show` verify completes)
  - `args._deploy_evidence['phase_timings']['phase_8_deploy'] = {started_at, completed_at, duration_seconds}`

- `phase_10_startup_and_version()` writes:
  - `args._deploy_evidence['deployed_at'] = datetime.now().isoformat()` ONLY when product_version matches (i.e., the new revision is actually serving traffic with correct version)
  - `args._deploy_evidence['phase_timings']['phase_10_startup_and_version'] = {...}`

- `phase_15_enforce_scaling()` writes:
  - `args._deploy_evidence['phase_timings']['phase_15_enforce_scaling'] = {...}`

- Initialization: `args._deploy_evidence = {'phase_timings': {}}` set at top of `main()` BEFORE first phase call.

### 2.4 New Azure CLI query for revision name

Insert after the verify-image block in `phase_8_deploy()`:

```python
r3 = _run([
    "az", "containerapp", "revision", "list",
    "--name", container_app,
    "--resource-group", RESOURCE_GROUP,
    "--query", f"[?properties.template.containers[0].image=='{new_image}'].name | [0]",
    "-o", "tsv",
], timeout=30)
if r3.returncode == 0 and r3.stdout.strip():
    args._deploy_evidence['revision_name'] = r3.stdout.strip()
```

Failure of this query degrades to `revision_name = None` (does NOT fail the phase).

### 2.5 Manifest write-site change

At line 1546-1577, add three lines AFTER `deploy_result` is built but BEFORE write:

```python
deploy_result['event_kind'] = _classify_manifest(deploy_result)
if hasattr(args, '_deploy_evidence') and args._deploy_evidence:
    deploy_result['deploy_evidence'] = args._deploy_evidence
```

## 3. Dashboard Ingest Update

`scripts/gtkb_dashboard/refresh_dashboard_db.py` already has `_DORA_DEPLOYMENT_EVENT_KINDS = frozenset({"canonical_deploy"})` per `-006` GO condition 2 (visible at line 711). The ingest change needed:

- `_ingest_canonical_pipeline_manifests()` (existing) reads `event_kind` from the manifest if present; falls back to existing classification heuristic if absent (for pre-Track-1 manifests already on disk).
- Pre-Track-1 rows (no `deploy_evidence` block) cap at `_confidence='medium'` per `-006` GO condition 3.
- Post-Track-1 rows with full `deploy_evidence` set `_confidence='high'` if `target_update_succeeded == True` AND ACA reconciliation finds matching revision.

## 4. Tests (per `-006` GO condition 1)

New test file: `tests/scripts/test_dora_001b_track1_classify_manifest.py`

Fixtures required (one test function each):

1. `test_classify_dry_run` — `dry_run=true` manifest → `canonical_pipeline_dry_run`
2. `test_classify_no_deploy_phase` — pipeline that stopped before phase 8 (e.g., phase 0 validation FAIL) → `canonical_pipeline_run`
3. `test_classify_deploy_phase_fail` — phase 8 present with `status="FAIL"` → `canonical_deploy_attempted_failed`
4. `test_classify_deploy_phase_pass_pre_track1` — phase 8 PASS but no `deploy_evidence.target_update_succeeded` field → `canonical_pipeline_run` with warning (defensive default; pre-Track-1 manifests don't have the boolean)
5. `test_classify_full_track1_success` — phase 8 PASS + `deploy_evidence.target_update_succeeded=true` → `canonical_deploy`
6. `test_classify_full_track1_verify_failed` — phase 8 PASS but `target_update_succeeded=false` (e.g., revision created but verify-image step found mismatch) → `canonical_deploy_attempted_failed`

All fixtures use synthetic `deploy_result` dicts; no Azure or filesystem dependency.

Additional integration test: `tests/scripts/test_dora_001b_track1_evidence_capture.py`

- `test_evidence_dict_initialized_at_main_entry` — verify `args._deploy_evidence` is initialized before any phase runs
- `test_phase_timing_captured` — mock phase functions; assert `phase_timings[phase_N]` populated with started_at/completed_at/duration_seconds
- `test_revision_name_capture_succeeds` — mock `az` call returning a revision name; assert captured into evidence
- `test_revision_name_capture_failure_does_not_fail_phase` — mock `az` returning non-zero; assert `revision_name=None` and phase_8_deploy still PASS
- `test_dry_run_skips_evidence` — `--dry-run` mode produces no `target_update_*` fields

## 5. DORA KPI Query Constraint (per `-006` GO condition 2)

Verify `_DORA_DEPLOYMENT_EVENT_KINDS` already excludes `canonical_pipeline_run` and `canonical_pipeline_dry_run` (visible at line 711). Add a regression test: `tests/scripts/test_dora_kpi_event_kind_filter.py`

- `test_deployment_frequency_excludes_pipeline_run` — insert mixed event_kind rows; assert deployment_frequency query counts only `canonical_deploy`
- `test_change_failure_rate_includes_attempted_failed` — assert `canonical_deploy_attempted_failed` counts as failure-attempt input

## 6. Refresh Status Constraint (per `-006` GO condition 4)

Verify `refresh_runs.status` semantics: ACA reconciliation failures degrade affected rows to `_consistency='unknown'` but do NOT change overall `refresh_runs.status` to `failed`.

Add regression test: `tests/scripts/test_dora_001b_refresh_status_resilience.py`

- `test_aca_query_failure_degrades_row_only` — mock ACA query to raise; assert row gets `_consistency='unknown'` AND `refresh_runs.status='completed'`
- `test_manifest_read_failure_does_not_fail_run` — mock manifest read to raise; assert refresh continues for other manifests, run completes

## 7. Files Changed

### 7.1 Modified
- `scripts/deploy_pipeline.py` — add `_classify_manifest()` helper; modify `phase_8_deploy()`, `phase_10_startup_and_version()`, `phase_15_enforce_scaling()` to write into `args._deploy_evidence`; init `args._deploy_evidence` at top of `main()`; add `event_kind` + `deploy_evidence` to `deploy_result` write-site at line 1546-1577
- `scripts/gtkb_dashboard/refresh_dashboard_db.py` — read `event_kind` from manifest when present; cap pre-Track-1 confidence at medium

### 7.2 New
- `tests/scripts/test_dora_001b_track1_classify_manifest.py` (6 tests)
- `tests/scripts/test_dora_001b_track1_evidence_capture.py` (5 tests)
- `tests/scripts/test_dora_kpi_event_kind_filter.py` (2 tests)
- `tests/scripts/test_dora_001b_refresh_status_resilience.py` (2 tests)

Total: 15 new tests; no test deletions; no architectural changes outside the deployment-pipeline / dashboard-ingest scope.

### 7.3 Untouched
- All existing tests, including `tests/scripts/test_dora_001b_track2_ingest.py` which already covers Track 2 ingest path
- All non-DORA dashboard code
- All DORA-002 / DORA-001c work (does not exist yet)

## 8. Backward Compatibility

Pre-Track-1 manifests on disk (everything written before this lands) will not have `event_kind` or `deploy_evidence` fields. Dashboard ingest must:

1. Detect missing `event_kind` and fall back to existing heuristic classification
2. Cap `_confidence` at `medium` for any row built without `deploy_evidence`
3. Never raise on missing fields

This satisfies the "no telemetry poisoning during transition" property `-006` GO condition 3 requires.

## 9. Implementation Sequence

1. Add `_classify_manifest()` helper + 6 unit tests for it (pure function, easiest to verify)
2. Add `args._deploy_evidence` init in `main()`
3. Modify `phase_8_deploy()` for evidence capture + new revision-name az query + phase_8 timing
4. Modify `phase_10_startup_and_version()` for `deployed_at` + phase_10 timing
5. Modify `phase_15_enforce_scaling()` for phase_15 timing
6. Modify manifest write-site at line 1546-1577 to inject `event_kind` + `deploy_evidence`
7. Modify dashboard ingest to read new fields with backward-compat fallback
8. Add 9 integration / regression tests
9. Run full pytest suite + release-candidate gate

Each step is independently testable. Steps 1-2 are zero-risk (pure helper + init). Steps 3-6 modify a hot file; covered by existing pipeline-end-to-end tests. Step 7 is dashboard-only.

## 10. Codex Review Asks

1. Confirm the `args._deploy_evidence` side-channel pattern (mutable args attribute) is the right shape, given existing precedent for `args._rollback_*` fields.
2. Confirm `_classify_manifest()` table in §2.2 covers the cases `-005` §5.5 specified.
3. Confirm test fixture list in §4 covers `-006` GO condition 1 (dry-run, no deploy phase, deploy phase FAIL, deploy phase PASS pre-Track-1, enhanced deploy-evidence cases).
4. Confirm files-changed scope in §7 matches the contract changes; no scope creep.
5. Confirm backward-compat strategy in §8 prevents pre-Track-1 manifest poisoning.
6. **GO / NO-GO** on Track 1 implementation.

## 11. Decision Needed From Owner

None — owner pre-acks captured (GOV-17 + source-shape) on 2026-04-26 unblock this proposal entirely.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All
rights reserved.*
