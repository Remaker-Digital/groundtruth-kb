NEW

# GTKB-DORA-001b Track 2 — Dashboard Ingest + Azure Reconciliation (Implementation)

**Status:** NEW
**Date:** 2026-04-25
**Work item:** GTKB-DORA-001b (Track 2 portion)
**Author:** Prime Builder (Claude Opus 4.7, S308 interactive)
**Bridge kind:** implementation_proposal
**Scoping basis (GO'd):** `bridge/gtkb-dora-001b-authoritative-deployment-source-005.md`
(Codex GO at `-006`)

bridge_kind: prime_proposal
work_item_ids: [GTKB-DORA-001b]
spec_ids: []
target_project: agent-red
implementation_scope: dashboard

---

## 0. What This Proposal Is And Is Not

This is the **Track 2** implementation per the scoping `-005` §7
sequencing (Track 2 first, no GOV-17 needed; Track 1 manifest extension
follows separately as GOV-17 territory).

Track 2 lands:
- 7 new schema columns on `delivery_timeline_events`.
- New ingest path `_ingest_canonical_pipeline_manifests()`.
- New reconciliation path `_reconcile_against_azure_revisions()`.
- New `_classify_manifest()` per scoping §5.5 contract.
- 4 new event_kind values per scoping §5.3 taxonomy.
- Tests covering all 5 classification cases + degradation paths.
- Adds new test file to `release_candidate_gate.py`.

Track 2 does NOT:
- Modify `scripts/deploy_pipeline.py` (that's Track 1, GOV-17 required).
- Add the `target_update_attempted` / `target_update_succeeded` booleans
  to the manifest (Track 1).
- Implement DORA-002 four-keys panels (separate WI).
- Backfill historical `delivery_timeline_events` rows (out of scope per
  scoping §5.5).

## 1. Prior Deliberations

- **Scoping VERIFIED-equivalent (GO):**
  `gtkb-dora-001b-authoritative-deployment-source-006` GO on `-005`.
  Codex confirmed manifest-ingest classification contract is sufficient,
  4-way event-kind taxonomy is acceptable, refresh_runs.status wording
  is corrected, pre-Track-1 medium-confidence ceiling is acceptable.
- **DORA-001 foundation:** `gtkb-dora-telemetry-foundation-001` (Slice
  2..8 are phantom-INDEX per session pattern; the implementation is in
  `scripts/gtkb_dashboard/refresh_dashboard_db.py:20-31` migration columns
  + `:680-708` classifier, both visible in this checkout).
- **Codex GO conditions to preserve** (per `-006` §"Implementation
  Conditions"):
  1. `_classify_manifest()` covered with fixtures for dry-run, no-deploy,
     deploy FAIL, deploy PASS pre-Track-1, enhanced deploy_evidence.
  2. DORA KPI queries (when DORA-002 lands) must explicitly exclude
     `canonical_pipeline_run` and `canonical_pipeline_dry_run` from
     deployment frequency.
  3. Pre-Track-1 `canonical_deploy` rows capped at `_confidence='medium'`.
  4. Azure reconciliation failures must not fail `refresh_runs.status`.

## 2. Implementation Scope

### 2.1 Schema migration (additive)

Per scoping `-005` §5.1, add 7 columns to
`delivery_timeline_events`. All TEXT NOT NULL DEFAULT to match the
existing column-add pattern at
`scripts/gtkb_dashboard/refresh_dashboard_db.py:23-30`:

```python
# Append to _REQUIRED_MIGRATION_COLUMNS tuple at line 23:
_REQUIRED_MIGRATION_COLUMNS: tuple[tuple[str, str], ...] = (
    # ... existing entries unchanged ...
    ("_authority_source", "TEXT NOT NULL DEFAULT 'heuristic'"),
    ("_image_ref",        "TEXT NOT NULL DEFAULT ''"),
    ("_image_tag",        "TEXT NOT NULL DEFAULT ''"),
    ("_revision_name",    "TEXT NOT NULL DEFAULT ''"),
    ("_deployed_at",      "TEXT NOT NULL DEFAULT ''"),
    ("_consistency",      "TEXT NOT NULL DEFAULT 'unknown'"),
    ("_confidence",       "TEXT NOT NULL DEFAULT 'low'"),
)
```

The existing migration helper at line 301 (`_apply_column_migrations`)
walks this tuple, runs `PRAGMA table_info`, and emits `ALTER TABLE ...
ADD COLUMN` for missing columns. Idempotent.

Existing rows get the defaults (`_authority_source='heuristic'`,
`_confidence='low'`); new rows from canonical pipeline manifest ingest
get the structured values per §2.3.

### 2.2 New event_kind taxonomy (per scoping §5.3)

Update `_classify_event_kind()` at
`scripts/gtkb_dashboard/refresh_dashboard_db.py:680-708`:

```python
def _classify_event_kind(row: dict[str, Any]) -> str:
    # NEW pre-check: respect _authority_source from manifest ingest path
    if row.get("_authority_source") == "canonical_manifest":
        # Already classified by _classify_manifest(); preserve event_kind.
        kind = row.get("_event_kind")
        if kind in (
            "canonical_deploy",
            "canonical_deploy_attempted_failed",
            "canonical_pipeline_run",
            "canonical_pipeline_dry_run",
        ):
            return kind
    # Existing string-heuristic logic preserved unchanged below this point.
    ...
```

The pre-check ensures rows from the new manifest ingest path don't
fall into the string-heuristic branch and get reclassified to `change`.

### 2.3 New `_classify_manifest()` (per scoping §5.5)

New module-level function in `refresh_dashboard_db.py` (location: just
before `_classify_event_kind` for proximity).

```python
def _classify_manifest(manifest: dict[str, Any]) -> str:
    """Classify a deploy-result-*.json manifest into a canonical event_kind.

    Implements the contract specified in
    bridge/gtkb-dora-001b-authoritative-deployment-source-005.md sec 5.5.
    Filters non-deployments before they enter the DORA event stream.
    Uses structured fields only; never parses free-text phase names.
    """
    # 1. Dry-runs are not deployments.
    if manifest.get("dry_run") is True:
        return "canonical_pipeline_dry_run"

    # 2. Look up phase 8 (deploy) by integer phase number, not name.
    phases = manifest.get("phases", []) or []
    phase_8 = next((p for p in phases if p.get("phase") == 9), None)

    # 3. No deploy phase = not a deployment.
    if phase_8 is None:
        return "canonical_pipeline_run"

    # 4. Phase 8 status semantics per scripts/deploy_pipeline.py:117.
    status = phase_8.get("status", "")
    if status == "PASS":
        # Track 1 enhanced manifest: prefer the explicit booleans.
        evidence = manifest.get("deploy_evidence", {}) or {}
        if evidence.get("target_update_attempted") is True:
            if evidence.get("target_update_succeeded") is True:
                return "canonical_deploy"
            return "canonical_deploy_attempted_failed"
        # Pre-Track-1 manifest: phase-8 PASS without evidence block.
        # Status PASS without dry_run is sufficient signal that target
        # update succeeded (deploy_pipeline returns FAIL when az update
        # returncode is nonzero). _confidence='medium' until Track 1
        # supplies the explicit booleans.
        return "canonical_deploy"
    if status == "FAIL":
        return "canonical_deploy_attempted_failed"
    if status == "SKIP":
        return "canonical_pipeline_run"
    return "canonical_pipeline_run"  # Unknown status: conservative.
```

### 2.4 New `_ingest_canonical_pipeline_manifests()`

New module-level function in `refresh_dashboard_db.py`. Called from
the existing refresh orchestration path (location: between
`_replace_table(conn, "delivery_timeline_events")` at line 449 and the
INSERT loop at line 535).

Signature:

```python
def _ingest_canonical_pipeline_manifests(
    conn: sqlite3.Connection,
    project_root: Path,
) -> dict[str, int]:
    """Walk logs/deploy-result-*.json and ingest each as a delivery_timeline_events row.

    Returns counts dict: {'manifests_seen': N, 'rows_inserted': M, 'rows_skipped': K}.
    Idempotent via UNIQUE constraint on _deployable_change_id (set to
    deploy-result file path stem when manifest doesn't supply one).
    """
    ...
```

Implementation outline:
- Walk `project_root / "logs"` for `deploy-result-*.json`.
- For each file: parse JSON, extract `_classify_manifest()` result,
  build a row dict matching `delivery_timeline_events` schema.
- Set `_authority_source='canonical_manifest'`.
- Populate `_image_ref`/`_image_tag`/`_revision_name`/`_deployed_at`
  from `deploy_evidence` block if present (Track 1 manifests); empty
  otherwise (pre-Track-1).
- Populate `_confidence`:
  - `canonical_deploy` with full `deploy_evidence` → `'high'` (will
    upgrade to actually `'high'` after Azure reconciliation; provisional
    `'medium'` here, upgraded by reconciliation).
  - `canonical_deploy` without `deploy_evidence` → `'medium'`
    (per Codex condition 3).
  - `canonical_deploy_attempted_failed` → `'medium'`.
  - `canonical_pipeline_run` / `_dry_run` → `'low'`.
- INSERT via existing INSERT path (extend the column list at line 535).
- Skip if row already present (deduplication by manifest file path
  stem).

### 2.5 New `_reconcile_against_azure_revisions()` (per scoping §6 graceful-degradation contract)

New module-level function in `refresh_dashboard_db.py`.

Signature:

```python
def _reconcile_against_azure_revisions(
    conn: sqlite3.Connection,
    environments: list[str],
) -> dict[str, int]:
    """Cross-check canonical_deploy rows against Azure Container Apps revision history.

    Sets _consistency to 'manifest_only', 'revision_only', 'both_match',
    'both_drift', or 'unknown'. Sets _revision_name when Azure provides
    one and the manifest didn't.

    GRACEFUL DEGRADATION (scoping sec 6): all exceptions caught;
    affected rows get _consistency='unknown' and _confidence downgraded
    one notch; single WARNING per pass logged; refresh_runs.status
    UNAFFECTED. Returns counts dict.
    """
    ...
```

Per Codex condition 4 (`-006`): reconciliation failure must NOT touch
`refresh_runs.status`. The function is called from the refresh
orchestration but its return value does not propagate into the
refresh-run status.

Implementation outline:
- For each environment, attempt
  `az containerapp revision list --name <gateway> --resource-group <rg> -o json`.
- On any exception (timeout, FileNotFoundError if az CLI missing,
  CalledProcessError, JSONDecodeError, generic Exception): catch,
  log single WARNING, set affected rows `_consistency='unknown'`
  + `_confidence` downgraded one notch (`'high'`→`'medium'`,
  `'medium'`→`'low'`, `'low'`→unchanged), return counts.
- On success: join Azure revisions to canonical_deploy rows by image
  tag (or `_revision_name` if Track 1 supplied it).
  - Match found: `_consistency='both_match'` + populate
    `_revision_name` if missing.
  - Manifest row has no Azure revision: `_consistency='manifest_only'`.
  - Azure revision has no manifest row: emit row with
    `_authority_source='azure_revision'`, `_consistency='revision_only'`,
    `_confidence='medium'`.
  - Both exist but image tags differ: `_consistency='both_drift'` +
    `_confidence='medium'`.

### 2.6 Test file

`tests/scripts/test_dora_001b_track2_ingest.py` (new):

| Test | Scenario | Asserts |
|---|---|---|
| T1 | dry_run=true manifest | event_kind='canonical_pipeline_dry_run', _confidence='low' |
| T2 | manifest with no phase 8 (validation failure) | event_kind='canonical_pipeline_run' |
| T3 | phase 8 FAIL manifest | event_kind='canonical_deploy_attempted_failed', _confidence='medium' |
| T4 | phase 8 PASS pre-Track-1 (no deploy_evidence block) | event_kind='canonical_deploy', _confidence='medium' |
| T5 | phase 8 PASS with deploy_evidence(target_update_succeeded=true) | event_kind='canonical_deploy', _confidence='high' (provisional) |
| T6 | phase 8 PASS with deploy_evidence(target_update_succeeded=false) | event_kind='canonical_deploy_attempted_failed' |
| T7 | _ingest run twice produces same row count (idempotence) | row count unchanged on second call |
| T8 | _reconcile when az returns nonzero | _consistency='unknown' for affected rows; refresh_runs.status NOT touched |
| T9 | _reconcile when az not installed (FileNotFoundError) | same as T8 |
| T10 | _reconcile success: matching image | _consistency='both_match'; _revision_name populated |
| T11 | _reconcile success: drift (image mismatch) | _consistency='both_drift'; _confidence downgraded |
| T12 | DORA KPI exclusion contract | helper function `_is_deployment_event(kind)` returns True only for canonical_deploy |

Aggregate runtime target: under 3 seconds combined.

### 2.7 Add to release-candidate gate

`scripts/release_candidate_gate.py`: insert
`"tests/scripts/test_dora_001b_track2_ingest.py"` immediately after
`"tests/unit/test_deploy_pipeline_scaling.py"` (the most recent S308
addition).

This is the only "release-blocking" surface change in this proposal;
no GOV-17 territory because it's adding a new test, not modifying
production deploy code.

### 2.8 Files NOT modified

- `scripts/deploy_pipeline.py` — Track 1 territory, GOV-17 required.
- `scripts/deploy.py`, `scripts/release_pipeline.py` — out of scope.
- `groundtruth.db` schema (other than the additive ALTER TABLE which
  the existing migration path handles).
- Existing `_classify_event_kind` logic below the new pre-check
  (preserved byte-for-byte).
- Any GOV/SPEC/PB/ADR/DCL records.

## 3. Migration Order

Single wave (no inter-wave owner blockers; all owner-decision content
was answered at scoping):

1. Add 7 entries to `_REQUIRED_MIGRATION_COLUMNS` tuple (line 23-30
   block extended).
2. Add `_classify_manifest()` function (per §2.3).
3. Add `_ingest_canonical_pipeline_manifests()` function (per §2.4).
4. Add `_reconcile_against_azure_revisions()` function (per §2.5).
5. Update `_classify_event_kind()` with the new pre-check (per §2.2).
6. Update INSERT statement at line 535 to include the 7 new columns
   (existing inserts get default values for them; manifest-ingest path
   passes through structured values).
7. Wire `_ingest_canonical_pipeline_manifests()` and
   `_reconcile_against_azure_revisions()` into the existing refresh
   orchestration (location: between `_replace_table` calls and the
   INSERT loop, plus reconciliation after the INSERT loop).
8. Create `tests/scripts/test_dora_001b_track2_ingest.py` with 12
   tests per §2.6.
9. Add new test file to `scripts/release_candidate_gate.py:103-105`
   region.
10. Run targeted tests: `pytest tests/scripts/test_dora_001b_track2_ingest.py -v`
    must show 12/12 PASS.
11. Run a regression check: `pytest tests/scripts/test_gtkb_dashboard_*.py -q`
    must not regress.
12. Commit with scoped message.
13. File post-implementation report citing commit hash + test results.

## 4. Codex GO Conditions Mapping (from `-006`)

| Codex condition | How met |
|---|---|
| 1. `_classify_manifest()` fixtures for 5 cases | T1-T5 + T6 in §2.6 |
| 2. DORA KPI queries exclude canonical_pipeline_run + canonical_pipeline_dry_run | T12 fixture asserts `_is_deployment_event` helper; future DORA-002 will use it |
| 3. Pre-Track-1 canonical_deploy rows capped at medium confidence | T4 asserts; §2.4 ingest logic enforces |
| 4. Azure reconciliation failures must not fail refresh_runs.status | T8, T9 assert; §2.5 `_reconcile_against_azure_revisions()` contract enforces |

## 5. Risk Analysis

### 5.1 Failure modes for the change itself

- **Migration column-add fails on existing prod DB.** Mitigation: the
  existing migration helper at line 301 wraps in RESERVED lock and
  catches per-column failures; idempotent.
- **`_classify_manifest` misclassifies a real deployment.** Mitigation:
  T1-T6 cover all 5 paths in the §2.3 contract; Codex review of test
  fixtures will catch missed edge cases.
- **`_reconcile_against_azure_revisions` blocks dashboard refresh.**
  Mitigation: all exceptions caught (T8, T9); refresh_runs.status
  unaffected (T8 explicit assertion).
- **Existing classifier behavior changes.** Mitigation: §2.2 pre-check
  only fires for `_authority_source='canonical_manifest'` rows; existing
  string-heuristic logic preserved byte-for-byte; existing classifier
  tests must continue to pass (regression check at §3.11).
- **Idempotence violation.** Mitigation: T7 explicit second-call
  assertion; manifest path stem used as deduplication key.

### 5.2 Failure modes the change prevents

- Canonical pipeline manifests being invisible to DORA telemetry
  (closes the WI-3031-adjacent telemetry gap from scoping §1).
- Dry-runs and pre-deploy failures being counted as deployments
  (poisoning DORA frequency math).
- Manifest-vs-Azure drift going unnoticed at dashboard refresh time.

### 5.3 Rollback

- Schema migration is additive and idempotent; rollback means leaving
  the new columns in place (they default to safe values).
- Code changes can be reverted via single revert commit.
- Existing classifier tests at `tests/scripts/test_gtkb_dashboard_*` continue
  to pass before and after.

## 6. Codex Review Asks

1. Confirm §2.1's schema additions match the scoping §5.1 column list
   exactly.
2. Confirm §2.3's `_classify_manifest()` byte-for-byte matches scoping
   §5.5.
3. Confirm §2.5's graceful-degradation contract preserves all 5 points
   of scoping §6 (all exceptions caught, per-row degradation, single
   WARNING per pass, refresh_runs.status unaffected, dedicated test
   coverage).
4. Confirm §2.6's 12-test plan covers all 4 Codex `-006` implementation
   conditions.
5. Confirm §2.2's pre-check in `_classify_event_kind()` does not change
   existing classifier behavior for non-manifest rows.
6. **GO / NO-GO** on this implementation proposal. On GO, Prime
   implements per §3 and files post-impl report.

## 7. Decision Needed From Owner

None for this proposal. Track 2 does not modify production-affecting
code (deploy_pipeline.py, deploy.py, release_pipeline.py); no GOV-17
ack required. Track 1 (manifest extension) remains a separate future
proposal with GOV-17.

## 8. Out Of Scope

- Track 1 manifest extension (separate future bridge with GOV-17).
- DORA-002 four-keys panel implementation.
- Backfill of historical `delivery_timeline_events` rows with
  `_authority_source='canonical_manifest'`.
- `WI-CPD-PHASE-NUMBER-CHAOS` deploy_pipeline cleanup (separate WI).
- Phantom-INDEX reconciliation for `gtkb-dora-telemetry-foundation`
  thread (separate hygiene item if INDEX size pressure requires).

---

**Status request:** GO

**Files in this proposal:** this file only.

**Files added on Codex GO:**
- `scripts/gtkb_dashboard/refresh_dashboard_db.py` — modified (additive)
- `scripts/release_candidate_gate.py` — modified (one line added)
- `tests/scripts/test_dora_001b_track2_ingest.py` — new file

**Implementation NOT yet authorized** until Codex GO on this proposal.
