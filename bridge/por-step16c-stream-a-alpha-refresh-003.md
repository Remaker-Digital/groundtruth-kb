# POR Step 16.C Stream A — α' Test Refresh (Revised)

**Status:** REVISED (addressing NO-GO -002 findings)
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-16
**Session:** S297
**Bridge thread:** por-step16c-stream-a-alpha-refresh
**Prior versions:** -001 (NEW), -002 (NO-GO)

## NO-GO -002 Findings Addressed

| Finding | Severity | Resolution |
|---------|----------|------------|
| F1: A3 relink would attach unrelated current-row tests | High | A3 remediation derives test identity from the **historical row** where `tests.id=reassigned_id AND spec_id=original_spec_id`, NOT from the current v3 row (§ A3 Method, revised) |
| F2: `last_run_at` is not a DB field | Medium | Replaced with `last_executed_at` throughout (§ Field Mapping) |
| F3: A1 missing `test_function` and multi-row specs | Medium | Added nodeid construction rules for function/class/file-level rows and per-row outcome aggregation for multi-row specs (§ A1 Nodeid Construction) |

## Prior Deliberations (unchanged from -001)

- `DELIB-0711` / `DELIB-0712` / `DELIB-0713`
- Umbrella GO at `bridge/por-step16c-implemented-untested-remediation-002.md`

## Understanding the A3 Pattern (corrected)

The -002 NO-GO clarified what "test-ID reassignment" really means in the
current DB. Example TEST-1481 (linked to SPEC-0159):

| Version | spec_id | test_file | test_function | last_result |
|---------|---------|-----------|---------------|-------------|
| v1 | SPEC-0159 | tests/regression/test_migration_compat.py | test_has_pending_changes_false_for_old_tenant | None |
| v2 | SPEC-0159 | tests/regression/test_migration_compat.py | test_has_pending_changes_false_for_old_tenant | fail |
| v3 | '' | tests/visual/test_widget_structure.py | test_input_textarea_exists[chromium] | stale |

This is **test-ID recycling**: the same `TEST-1481` ID was reused for a
completely different test. The v3 row's `spec_id=''` makes it appear
"unowned," but it belongs to some other spec conceptually — just not this
one. Stream A must not relink the v3 row; it must use **the last version
where `spec_id=original_spec_id`** (v2 in this example) as the source of
truth for what test historically proved this spec.

## Objective (unchanged)

Restore "tested" status for the 151 α' specs by refreshing their test
evidence, using correct per-subcase methodology.

## Scope — Exact Spec ID Sets (pulled from inventory at runtime)

**Filter**: `classification.category == 'alpha_prime'` from
`independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json`.

**Partition** into A1 and A3 via inventory signal
`signals.test_id_reassignments`:
- A1 (114 specs): `len(test_id_reassignments) == 0` AND `current_stale_rows > 0`
- A3 (37 specs): `len(test_id_reassignments) > 0`

Spec-ID lists will be embedded verbatim in the post-impl report (not manually
copied into this proposal) per the F3-equivalent from Stream D's NO-GO.

## A1 Method — Straight Refresh (revised)

### A1 Nodeid Construction (addresses F3)

For each A1 stale row, build the pytest nodeid based on what fields are
populated:

```python
def build_nodeid(test_file: str, test_class: str | None, test_function: str | None) -> str:
    if test_function:
        if test_class:
            return f"{test_file}::{test_class}::{test_function}"
        return f"{test_file}::{test_function}"
    if test_class:
        return f"{test_file}::{test_class}"
    return test_file  # file-level: pytest runs all tests in file
```

**Handling of 12 file-level A1 rows** (empirical from DB):
Examples: TEST-2686 (`test_admin_features_batch.py` for SPEC-1509), TEST-2932
(`test_dashboard_display_values.py` for SPEC-1613). For these, pytest runs
the entire file and the row's outcome is aggregated from all tests in that
file (see "Outcome Aggregation" below).

### A1 Multi-Row Specs (addresses F3)

Two A1 specs have multiple current stale rows: SPEC-1580 (2 rows), SPEC-1613
(8 rows). For multi-row specs, each row is refreshed independently. The
spec's overall bucket is aggregated:

- **All rows pass** → `refreshed_pass`
- **Any row fails** → `refreshed_fail_escalated_to_c` (Stream C gets
  per-row detail for repair)
- **All rows skip** → `refreshed_skip` (test exists but doesn't run; spec
  stays implemented-untested; not an escalation)
- **Mixed pass+skip (no fail)** → `refreshed_partial` (spec gains some
  test evidence; not a full refresh but not a failure)

Per-row outcomes are recorded in the post-impl report for every multi-row
spec.

### A1 Per-Row Outcome Rules

Running `pytest {nodeid}` produces one of:

- **pass** → `db.update_test(id=test_id, version=current+1, last_result='pass', last_executed_at=now_utc)`
- **fail** → `db.update_test(id=test_id, version=current+1, last_result='fail', last_executed_at=now_utc)` + escalate to C with failure output
- **skip** → `db.update_test(id=test_id, version=current+1, last_result='skip', last_executed_at=now_utc)` — keeps row current but spec stays untested
- **collection error / file missing** → ESCALATE to C (code anomaly)

For file-level rows, pytest aggregates: if ANY test in the file fails, the
row is `fail` (escalate). If all pass, `pass`. If all skip or skip+pass, use
the majority with a note.

## A3 Method — Historical-Row-Based Refresh (corrected)

### A3 Identity Resolution (addresses F1)

For each A3 spec `S` with reassigned test_id set
`T = {t1, t2, ...}`:

1. For each `t` in T, query the **historical row where the test still
   belonged to `S`**:
   ```python
   historical = conn.execute("""
       SELECT id, version, test_file, test_class, test_function,
              last_result, last_executed_at
       FROM tests
       WHERE id = ? AND spec_id = ?
       ORDER BY version DESC LIMIT 1
   """, (test_id, original_spec_id)).fetchone()
   ```
2. If `historical` is None → ESCALATE to D (no historical evidence for
   this spec/test pair; it's effectively phantom).
3. If `historical.test_file` doesn't exist on disk → ESCALATE to C (broken
   path, similar to β').
4. Otherwise, build the nodeid from `historical` and run pytest.

### A3 Outcome → New Row

A3 remediation does **not** touch the current v3 row (which belongs to
some other test conceptually, with `spec_id=''`). Instead:

- **pass** → Allocate a new `test_id` (next sequential `TEST-NNNN` after
  max). Call `db.insert_test()` with `spec_id=original_spec_id`,
  `test_file=historical.test_file`, `test_function=historical.test_function`,
  `last_result='pass'`, `last_executed_at=now_utc`. This creates fresh
  evidence for the spec without perturbing the recycled ID.
- **fail** → Create the new row with `last_result='fail'` (so evidence
  exists in the KB), then ESCALATE to C for repair.
- **skip / collection error** → No new row; ESCALATE to C.

**Why allocate a new test_id**: the original `TEST-NNNN` now has a v3
pointing elsewhere. Creating a new version for the original spec under
the same ID would silently overwrite that v3. A fresh ID preserves the
audit trail.

### A3 Edge Case — Historical Row Already Failed

Per Codex evidence, historical A3 rows have `hist_result_counts: {None: 49,
fail: 2, pass: 24, skip: 4}`. Many have None (never executed historically)
or fail. Running them now is still informative:

- Historical `None` → Run fresh; outcome determines bucket.
- Historical `fail` → Run fresh; may pass now (bug was fixed) or still
  fail (escalate).
- Historical `pass` → Run fresh; should still pass (regression if not).

## Field Mapping (addresses F2)

All DB writes use `last_executed_at` (the actual column name per
`groundtruth_kb/db.py:2397-2422`), not `last_run_at`.

```python
# CORRECT:
db.update_test(id=tid, version=new_version, last_result='pass',
               last_executed_at=datetime.now(UTC).isoformat())

# WRONG (was in -001):
db.update_test(id=tid, last_run_at=...)  # ignored by update_test()
```

The post-impl report will sample several new test rows to prove
`last_executed_at` was refreshed with the session's timestamp range.

## Reconciliation Invariant (unchanged)

Every α' spec `S` (151 total) must receive exactly one terminal bucket:

| Bucket | Subcase sources | Reports in |
|--------|-----------------|------------|
| `refreshed_pass` | A1 all-pass, A3 pass | Stream A post-impl |
| `refreshed_fail_escalated_to_c` | A1 any-fail, A3 fail | Stream A + Stream C |
| `refreshed_skip` | A1 all-skip, A3 skip | Stream A post-impl |
| `refreshed_partial` | A1 mixed pass+skip | Stream A post-impl |
| `escalated_to_c_broken_path` | A3 file missing on disk | Stream A + Stream C |
| `escalated_to_d_no_historical` | A3 no historical row with original spec_id | Stream A + Stream D |

Sum across buckets must equal **151**. Post-impl fails loudly if any α'
spec is unaccounted.

## Implementation Plan (revised)

1. **Load inventory**, partition A1 (114) and A3 (37). Fail-fast if count != 151.
2. **DB hash bracket open**.
3. **A1 loop** (114 specs, each may have 1-8 current stale rows):
   - For each stale row, build nodeid per rules above.
   - Batch by file path to minimize pytest overhead.
   - Run pytest, classify outcome per-row.
   - `db.update_test()` with `last_executed_at=now_utc`.
   - Aggregate per-spec bucket.
4. **A3 loop** (37 specs):
   - For each reassigned test_id, resolve historical row (WHERE spec_id=original).
   - If historical exists and file present → run → insert new test_id row with fresh spec_id binding.
   - Classify outcome.
5. **DB hash bracket close** + assert only `tests` table mutated (new rows
   appended via `insert_test`, new versions via `update_test`; NO spec-status
   mutations).
6. **Verify invariant**: every α' spec has a terminal bucket; sum == 151.
7. **Classifier re-run**: confirm α' population shrinks by exactly the
   `refreshed_pass` count.

## Files Changed (unchanged)

| File | Change Type | Description |
|------|------------|-------------|
| `groundtruth.db` | Write | New `tests` rows (A3) and new test versions (A1). No spec-status changes |
| `independent-progress-assessments/spec-hygiene/scripts/stream_a_alpha_refresh.py` | New | Implementation script |

No source code changes. No test authoring. We run existing tests.

## Risks (updated)

- **Medium:** Bit-rotted A1/A3 tests reveal real regressions. Mitigation:
  each failure is a Stream C handoff with file:line evidence.
- **Low:** A3 new-test-ID allocation is deterministic (sequential from max).
  Collision impossible given sequential allocation.
- **Low:** Multi-row spec aggregation is testable via per-row outcome logs.
- **Medium:** Pytest runs for 47 unique test files may take 10-30 minutes
  total (depends on e2e/integration content). Script runs in background-
  agent-friendly batches.

## Exit Criteria (sharpened)

1. All 151 α' specs have a terminal bucket assignment (sum == 151).
2. No Stream A spec silently remains in α' without escalation explanation.
3. DB hash bracket documents exactly the expected mutations:
   - A1: new `tests` versions with `last_result` ∈ {pass, fail, skip} and fresh `last_executed_at`
   - A3: new `tests` rows (new `id` allocated) with fresh binding and outcome
4. Post-impl report lists:
   - Per-spec bucket (114 A1 + 37 A3 = 151 entries)
   - Per-row outcomes for multi-row specs (SPEC-1580, SPEC-1613, etc.)
   - Full escalation lists for Stream C and Stream D with reasons
   - Sample of new test rows proving `last_executed_at` freshness
5. Classifier re-run confirms α' count reduction matches reported
   `refreshed_pass` + `refreshed_partial` count.

## Reconciliation Against Umbrella

Umbrella condition: "Stream A must address the alpha-prime subcase risk."
This revision:
- Separates A1 (114) and A3 (37) ✓
- Handles A3 without relinking to unrelated current rows ✓
- Addresses A1 nodeid edge cases ✓
- Uses correct field names ✓
- Provides explicit multi-row aggregation rules ✓

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
