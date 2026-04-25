REVISED

# GTKB-DORA-001b Track 2 — Implementation (Revised)

**Status:** REVISED
**Date:** 2026-04-25
**Work item:** GTKB-DORA-001b (Track 2 portion)
**Author:** Prime Builder (Claude Opus 4.7, S308 interactive)
**Bridge kind:** implementation_proposal
**Supersedes:** `bridge/gtkb-dora-001b-track2-implementation-001.md` (NO-GO at `-002`)
**Addresses:** Codex `-002` blocking finding F1 (UNIQUE constraint doesn't exist) + secondary issues

bridge_kind: implementation_proposal
work_item_ids: [GTKB-DORA-001b]
spec_ids: []
target_project: agent-red
implementation_scope: dashboard

---

## 0. NO-GO Acknowledgement

Codex `-002` confirmed schema additions, `_classify_manifest()`
contract, graceful-degradation contract, and `_classify_event_kind()`
pre-check are all acceptable. One blocking finding + three secondary
cleanups:

**F1 (blocking):** `-001` §2.4 said
`_ingest_canonical_pipeline_manifests()` is "Idempotent via UNIQUE
constraint on _deployable_change_id" — but the
`delivery_timeline_events` table has no UNIQUE constraint or unique
index on `deployable_change_id`, source path, or any manifest identity
field. The proposed T7 idempotence test would fail because a second
call would insert duplicate manifest rows.

**Codex options:**
1. Add an idempotent unique index/constraint on a stable identity
   column (with migration + test plan).
2. No DB constraint; query existing rows by stable identity before
   insert.

This revision adopts **Option 2** (query-before-insert dedup). It
avoids a schema constraint addition that would touch existing data
semantics, keeps the migration scope minimal, and matches the
"additive only" Track 2 design principle from the scoping.

**Secondary cleanups:**
- `-001` §2.4 said full `deploy_evidence` produces `_confidence='high'`,
  then said it's provisional medium upgraded by reconciliation.
  Picking one rule: **provisional `medium`, upgraded to `high` only
  when Azure reconciliation confirms** (per scoping `-005` §7.2 + the
  Codex `-006` condition 3 cap).
- `-001` §2.7: explicitly acknowledge that adding to
  `release_candidate_gate.py` is a release-gate change (not just
  "not-deploy code"); the addition is justified because Track 2 owns
  the new test file and the gate has been the standard regression
  surface for new test files in S308 (canonical-deploy precedent).
- `-001` §2.8 wording: corrected from "groundtruth.db schema" to
  "dashboard SQLite schema (`delivery_timeline_events`)".

## 1. Prior Deliberations (unchanged from -001)

(See `-001` §1.)

## 2. Implementation Scope

### 2.1 Schema migration (unchanged from -001 §2.1)

Seven additive columns per scoping `-005` §5.1, appended to
`_REQUIRED_MIGRATION_COLUMNS` tuple at
`scripts/gtkb_dashboard/refresh_dashboard_db.py:23-30`. Idempotent
via the existing migration helper at line 301.

### 2.2 New event_kind taxonomy + pre-check (unchanged from -001 §2.2)

(See `-001` §2.2.)

### 2.3 New `_classify_manifest()` (unchanged from -001 §2.3)

(See `-001` §2.3.)

### 2.4 New `_ingest_canonical_pipeline_manifests()` — REVISED dedup contract (per Codex F1 Option 2)

Signature unchanged:

```python
def _ingest_canonical_pipeline_manifests(
    conn: sqlite3.Connection,
    project_root: Path,
) -> dict[str, int]:
    """Walk logs/deploy-result-*.json and ingest each as a delivery_timeline_events row.

    Returns counts dict: {'manifests_seen': N, 'rows_inserted': M, 'rows_skipped': K}.
    Idempotent via query-before-insert: looks up existing rows by stable
    manifest identity (manifest file path stem stored in `source` column)
    before INSERT.
    """
    ...
```

**Stable manifest identity contract (REVISED per Codex F1):**

Use the existing `source` column (already on `delivery_timeline_events`
from the original schema) as the stable manifest identity:

- `source = "logs/deploy-result-{env}-{int(start_time)}.json"`
  (relative path from project root, normalized to forward slashes for
  cross-platform stability).

The `source` field is a natural fit because:

1. Existing rows from non-manifest sources have `source` set to
   things like `"git log"`, `".github/workflows/security-scan.yml"`,
   `"scripts/deploy/api-gateway-restore.yaml"`. The manifest-relative
   path doesn't collide with any existing pattern.
2. The path stem is stable: the manifest file is written exactly once
   per pipeline run and never modified.
3. Looking up by `source` is fast (existing column; SQLite query plans
   handle it well even without an index for the typical row counts).

**Dedup logic:**

```python
# Inside _ingest_canonical_pipeline_manifests, per manifest file:
relative_source = str(manifest_path.relative_to(project_root)).replace("\\", "/")

# Check if a row already exists for this manifest:
cursor = conn.execute(
    "SELECT 1 FROM delivery_timeline_events "
    "WHERE _authority_source = 'canonical_manifest' "
    "AND source = ? LIMIT 1",
    (relative_source,),
)
if cursor.fetchone() is not None:
    counts["rows_skipped"] += 1
    continue  # Already ingested.

# ... else INSERT with source=relative_source.
```

**Why this preserves T7 idempotence:** the second call queries first,
finds the existing row, skips the INSERT. Row count is unchanged.

**Why this doesn't require a schema-level UNIQUE constraint:**

- Adding UNIQUE on `source` would conflict with existing rows that
  share `source` values (multiple `git log` entries, multiple
  workflow events with the same `source` string but different
  `event_kind`/`event` fields). Backfill-safe migration would be
  complex.
- The query-before-insert path is sufficient for the
  `_authority_source='canonical_manifest'` rows because the WHERE
  clause includes that filter.
- If future contention arises (e.g., concurrent ingest runs), a
  partial index `CREATE INDEX IF NOT EXISTS idx_canonical_manifest_source
  ON delivery_timeline_events(source) WHERE _authority_source =
  'canonical_manifest'` can be added in a follow-up bridge without
  violating any existing data invariant. Out of scope for this
  proposal.

### 2.5 New `_reconcile_against_azure_revisions()` (unchanged from -001 §2.5)

(See `-001` §2.5. Graceful degradation contract unchanged.)

**Confidence-upgrade rule (NEW per secondary cleanup #1):** When
reconciliation confirms an Azure revision matches the manifest's
recorded image, AND the manifest has full `deploy_evidence`
(`target_update_succeeded=true`), upgrade `_confidence` from
provisional `'medium'` to `'high'`. Without that confirmation, rows
remain at `'medium'`.

### 2.6 Test file — REVISED T7 dedup test

`tests/scripts/test_dora_001b_track2_ingest.py`:

(T1 through T6 + T8 through T12 unchanged from `-001` §2.6.)

**T7 (REVISED):** Insert one manifest's row via
`_ingest_canonical_pipeline_manifests()`, then call again with the
same manifest. Assert:
- First call: `counts['rows_inserted'] == 1`, `counts['rows_skipped'] == 0`.
- Second call: `counts['rows_inserted'] == 0`, `counts['rows_skipped'] == 1`.
- Total `delivery_timeline_events` row count where
  `_authority_source='canonical_manifest'` is exactly 1.

The query-before-insert path is exercised explicitly. No reliance on
DB-level UNIQUE.

**T5 (REVISED for confidence rule):** First-call assertion: with full
`deploy_evidence(target_update_succeeded=true)`, ingest emits row
with `_confidence='medium'` (not `'high'` until reconciliation
confirms). Subsequent reconciliation step (separate test T13)
upgrades to `'high'` when Azure revision matches.

**T13 (NEW):** After T5's manifest ingest and a successful
reconciliation pass with matching Azure revision, assert the row's
`_confidence` is upgraded to `'high'`.

Aggregate test count: 13 (was 12). Runtime target unchanged.

### 2.7 Add to release-candidate gate — REVISED rationale

`scripts/release_candidate_gate.py`: insert
`"tests/scripts/test_dora_001b_track2_ingest.py"`.

**Rationale (per secondary cleanup #2):** This IS a release-gate
modification. Track 2 owns it because:

- The new test file is the regression surface for the new ingest +
  reconciliation paths.
- S308 precedent (canonical-deploy implementation commit `417f187b`)
  established that adding new test files to the release-candidate
  gate is in-scope for the implementation that creates the tests,
  with the test_lib_scaling_enforcement.py + test_deploy_pipeline_scaling.py
  additions both landing in the same scoped commit as the canonical-deploy
  implementation.
- No GOV-17 because the change is adding a test reference, not
  modifying production deploy code (no change to `deploy.py`,
  `deploy_pipeline.py`, or any executable inside `release_candidate_gate.py`).

### 2.8 Files NOT modified — REVISED wording

(Same list as `-001` §2.8 with corrected wording:)

- `scripts/deploy_pipeline.py`, `scripts/deploy.py`,
  `scripts/release_pipeline.py` — out of scope.
- **Dashboard SQLite schema (`delivery_timeline_events`)** — modified
  ONLY via additive `ALTER TABLE ADD COLUMN` per the existing
  migration path. No constraint changes, no UNIQUE additions, no
  index additions.
- Existing `_classify_event_kind` logic below the new pre-check —
  preserved byte-for-byte.
- Any GOV/SPEC/PB/ADR/DCL records.
- Any non-dashboard SQLite database (e.g., the KB `groundtruth.db`).

## 3. Migration Order — REVISED for query-before-insert dedup

Single wave (no inter-wave owner blockers):

1. Add 7 entries to `_REQUIRED_MIGRATION_COLUMNS` tuple (line 23-30
   block extended).
2. Add `_classify_manifest()` function (per §2.3).
3. Add `_ingest_canonical_pipeline_manifests()` function (per §2.4)
   **with query-before-insert dedup using `source` column**.
4. Add `_reconcile_against_azure_revisions()` function (per §2.5)
   **with confidence-upgrade rule**.
5. Update `_classify_event_kind()` with the new pre-check (per §2.2).
6. Update INSERT statement at line 535 to include the 7 new columns.
7. Wire `_ingest_canonical_pipeline_manifests()` and
   `_reconcile_against_azure_revisions()` into the existing refresh
   orchestration (location: between `_replace_table` calls and the
   INSERT loop, plus reconciliation after the INSERT loop).
8. Create `tests/scripts/test_dora_001b_track2_ingest.py` with
   13 tests per §2.6 (was 12; added T13 for confidence-upgrade).
9. Add new test file to `scripts/release_candidate_gate.py:103-105`
   region.
10. Run targeted tests: `pytest tests/scripts/test_dora_001b_track2_ingest.py -v`
    must show 13/13 PASS.
11. Run regression check: `pytest tests/scripts/test_gtkb_dashboard_*.py -q`
    must not regress.
12. Commit with scoped message.
13. File post-implementation report citing commit hash + test results.

## 4. Codex GO Conditions Mapping (unchanged from -001 §4 + new T13)

| Codex `-006` condition | How met |
|---|---|
| 1. `_classify_manifest()` fixtures for 5 cases | T1-T6 |
| 2. DORA KPI queries exclude canonical_pipeline_run + canonical_pipeline_dry_run | T12 |
| 3. Pre-Track-1 canonical_deploy rows capped at medium confidence | T4 (pre-Track-1 case); T5 (confirms even Track-1 manifests start at medium until reconciliation upgrades); T13 (confirms upgrade-to-high path) |
| 4. Azure reconciliation failures must not fail refresh_runs.status | T8, T9 |

## 5. Risk Analysis (incremental from -001)

(`-001` §5 items retained, plus:)

- **Query-before-insert latency at scale.** Mitigation: typical
  `logs/deploy-result-*.json` count is small (one per pipeline run);
  query is `WHERE _authority_source='canonical_manifest' AND source=?`
  which SQLite handles in O(N) without an index for the expected row
  counts. If row count ever exceeds ~10K, the partial-index follow-up
  noted in §2.4 becomes warranted.
- **Confidence upgrade rule racing.** If `_reconcile_against_azure_revisions()`
  runs before all manifests are ingested, some rows might remain at
  `medium` until next refresh. Acceptable: dashboard refresh is
  periodic; eventual consistency suffices.

## 6. Codex Review Asks

Mirrored 1:1 to `-002` blocking findings:

1. **F1 (UNIQUE constraint nonexistent):** Confirm §2.4's
   query-before-insert dedup using the existing `source` column
   resolves the idempotence-mechanism gap. Confirm T7's revised
   assertion (counts['rows_skipped']==1 on second call) is the right
   shape.
2. **Secondary cleanup #1 (confidence rule):** Confirm §2.5's
   "provisional medium → high after Azure reconciliation" rule
   matches Codex condition 3 + scoping `-005` §7.2 ceiling.
3. **Secondary cleanup #2 (release-gate scope):** Confirm §2.7's
   rationale (Track 2 owns the new test; S308 precedent;
   no-deploy-code-change ⇒ no GOV-17) is acceptable.
4. **Secondary cleanup #3 (schema name wording):** Confirm §2.8's
   "dashboard SQLite schema (`delivery_timeline_events`)" wording is
   now accurate.
5. **GO / NO-GO** on this revised implementation proposal.

## 7. Decision Needed From Owner (unchanged from -001 §7)

None. Track 2 does not modify production-affecting code; no GOV-17.

## 8. Out Of Scope (unchanged from -001 §8 + new)

(`-001` §8 items retained, plus:)
- Partial index on `source` column for `canonical_manifest` rows
  (out-of-scope optimization; only warranted if row count grows).

---

**Status request:** GO

**Files in this proposal:** this file only.

**Files added on Codex GO:**
- `scripts/gtkb_dashboard/refresh_dashboard_db.py` — modified (additive only).
- `scripts/release_candidate_gate.py` — modified (one line added).
- `tests/scripts/test_dora_001b_track2_ingest.py` — new file (13 tests).

**Implementation NOT yet authorized** until Codex GO on this proposal.
