# POR Step 16.C Stream A — α' Test Refresh (Revision 2)

**Status:** REVISED (addressing NO-GO -004 findings)
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-16
**Session:** S297
**Bridge thread:** por-step16c-stream-a-alpha-refresh
**Prior versions:** -001 (NEW), -002 (NO-GO), -003 (REVISED), -004 (NO-GO)

## NO-GO -004 Findings Addressed

| Finding | Severity | Resolution |
|---------|----------|------------|
| F1: Fail/skip writes contradict classifier definition of "implemented-untested" | High | All non-stale writes (pass/fail/skip) remove spec from α' — exit invariant rewritten to match (§ Bucket→Classifier Reconciliation) |
| F2: A3 `insert_test()` missing required fields (title, test_type, expected_outcome, etc.) | High | A3 historical query expanded to select all 7 required fields; full call shape specified (§ A3 API Calls) |
| F3: `update_test()` signature mismatch + file-level determinism gap | Medium | Correct `update_test()` signature (no explicit version); deterministic file-level precedence rules (§ A1 API Calls + § File-Level Determinism) |

## Prior NO-GO Resolutions (preserved)

| Finding | Source | Resolution |
|---------|--------|-----------|
| A3 relink would attach unrelated current-row tests | -002 F1 | Historical-row identity rule (preserved from -003) |
| `last_run_at` not a DB field | -002 F2 | `last_executed_at` throughout (preserved) |
| A1 missing `test_function`, multi-row specs | -002 F3 | Nodeid construction rules (preserved, refined below) |

## Prior Deliberations (unchanged)

- `DELIB-0711` / `DELIB-0712` / `DELIB-0713`
- Umbrella GO at `bridge/por-step16c-implemented-untested-remediation-002.md`

## Correct API Signatures (verified against installed GT-KB)

Verified via `inspect.signature` against
`groundtruth_kb.db.KnowledgeDB`:

```python
insert_test(
    id: str, title: str, spec_id: str, test_type: str, expected_outcome: str,
    changed_by: str, change_reason: str,
    *, test_file: str | None = None, test_class: str | None = None,
    test_function: str | None = None, description: str | None = None,
    last_result: str | None = None, last_executed_at: str | None = None,
) -> dict[str, Any] | None

update_test(
    id: str, changed_by: str, change_reason: str,
    **fields: Any,  # passed through; no explicit `version` accepted
) -> dict[str, Any] | None
```

## Scope — Exact Spec ID Sets (unchanged)

- A1 (114 specs): `classification.category == 'alpha_prime' AND len(signals.test_id_reassignments) == 0 AND signals.current_stale_rows > 0`
- A3 (37 specs): `classification.category == 'alpha_prime' AND len(signals.test_id_reassignments) > 0`
- Total: 151 ✓

### A1 Stale-Row Identity Distribution (empirical, addresses F3 numbers)

From DB query of 122 current stale rows across 114 A1 specs:

| Identity shape | Row count | Handling |
|----------------|----------:|----------|
| `test_class + test_function` | 110 | `{file}::{class}::{func}` nodeid |
| `test_class` only (no func) | 3 | `{file}::{class}` nodeid — runs all class methods |
| Neither (file-level aggregate) | 9 | `{file}` nodeid — runs all tests in file |

Multi-row A1 specs: SPEC-1580 (2 rows), SPEC-1613 (8 rows). Other 112
specs have 1 row each.

## A1 Method (revised API + determinism)

### A1 Nodeid Construction (unchanged)

```python
def build_nodeid(test_file, test_class, test_function):
    if test_function:
        return f"{test_file}::{test_class}::{test_function}" if test_class else f"{test_file}::{test_function}"
    if test_class:
        return f"{test_file}::{test_class}"
    return test_file  # file-level
```

### A1 update_test() Call Shape (addresses F3)

```python
db.update_test(
    id=test_id,                                   # e.g., "TEST-2686"
    changed_by="prime_builder",
    change_reason="POR Step 16.C Stream A: refresh stale test evidence per DELIB-0713",
    last_result=outcome,                          # 'pass' | 'fail' | 'skip'
    last_executed_at=datetime.now(UTC).isoformat(),
)
```

**No explicit version** — `update_test()` computes the next version
internally. `changed_by` and `change_reason` are mandatory positional args.

### A1 Per-Row Outcome Rules

Running `pytest {nodeid} --no-cov -q` produces one of:

| pytest outcome | Write to DB | Bucket assignment |
|----------------|-------------|-------------------|
| PASSED | `last_result='pass'` | `refreshed_pass` |
| FAILED | `last_result='fail'` | `refreshed_fail` (escalate to C) |
| SKIPPED | `last_result='skip'` | `refreshed_skip` |
| Collection error | `last_result='fail'` (treat as fail) | `refreshed_fail` (escalate to C) |
| XFAIL | `last_result='pass'` (expected failure) | `refreshed_pass` |
| XPASS | `last_result='pass'` (unexpected pass, test needs review) | `refreshed_pass` (flag in report) |

**All non-stale writes remove the spec from α'** (per classifier's target
query definition).

### File-Level Determinism (addresses F3)

For the 9 file-level rows, pytest runs all tests in the file. Aggregate
rule (deterministic precedence):

```python
if any_test_had_collection_error: outcome = 'fail'
elif any_test_failed:             outcome = 'fail'
elif all_collected_tests_skipped: outcome = 'skip'
elif all_collected_non_skip_tests_passed: outcome = 'pass'
else: outcome = 'fail'  # shouldn't happen; defensive
```

Ordered precedence: **collection_error > fail > skip-only > pass**.
Per-test outcomes recorded in post-impl report for every file-level row.

### A1 Multi-Row Spec Aggregation (revised — matches classifier)

For multi-row specs, each row gets its own outcome and its own DB write.
The spec's α' membership is determined solely by the classifier: as soon
as any row is non-stale, the spec is out of α'.

Bucket for multi-row specs:
- All rows `pass` → `refreshed_pass`
- Any row `fail` (even if others pass) → `refreshed_fail_mixed` (escalate to C)
- All rows `skip` → `refreshed_skip`
- Pass + skip mix (no fail) → `refreshed_partial_pass`

Per-row outcomes in post-impl report regardless of aggregate bucket.

## A3 Method (revised API, addresses F2)

### A3 Historical Query (expanded to include required insert_test fields)

```sql
SELECT id, version, spec_id, title, test_type, expected_outcome,
       test_file, test_class, test_function, description,
       last_result, last_executed_at
FROM tests
WHERE id = ? AND spec_id = ?
ORDER BY version DESC
LIMIT 1
```

All 12 fields are needed: 7 for the `insert_test()` required args
(`id`, `title`, `spec_id`, `test_type`, `expected_outcome` — `changed_by`
and `change_reason` supplied by Stream A), plus the 6 optional args used
to preserve the test identity faithfully (`test_file`, `test_class`,
`test_function`, `description`, `last_result`, `last_executed_at`).

### A3 `insert_test()` Call Shape (addresses F2)

For each A3 reassigned test_id where the historical row exists:

1. Allocate new test_id (sequential from `max(TEST-NNNN) + 1`).
2. Run pytest using the historical row's nodeid (`test_file`/`test_class`/`test_function`).
3. Call `insert_test()`:

```python
db.insert_test(
    id=new_test_id,                               # e.g., "TEST-11064"
    title=historical.title,                        # preserved from historical
    spec_id=original_spec_id,                      # NOT the blank v3 spec_id
    test_type=historical.test_type,                # preserved
    expected_outcome=historical.expected_outcome,  # preserved
    changed_by="prime_builder",
    change_reason=(
        f"POR Step 16.C Stream A A3: replacement test binding after test_id "
        f"{original_test_id} was recycled; historical row v{historical.version} "
        f"used as template per DELIB-0713"
    ),
    test_file=historical.test_file,
    test_class=historical.test_class,
    test_function=historical.test_function,
    description=historical.description,
    last_result=outcome,                           # pytest run outcome
    last_executed_at=datetime.now(UTC).isoformat(),
)
```

### A3 Outcome → Bucket

Same `pytest outcome → DB write` mapping as A1, with one extra escalation:

| Historical query result | Action | Bucket |
|-------------------------|--------|--------|
| Found + file exists + pytest pass | Insert new test row | `refreshed_pass` |
| Found + file exists + pytest fail | Insert with `last_result='fail'` | `refreshed_fail` (→ C) |
| Found + file exists + pytest skip | Insert with `last_result='skip'` | `refreshed_skip` |
| Found + file exists + collection error | Insert with `last_result='fail'` | `refreshed_fail` (→ C) |
| Found + file DOES NOT exist on disk | No DB write | `escalated_to_c_broken_path` |
| Not found (no historical row with original spec_id) | No DB write | `escalated_to_d_no_historical` |

## Bucket → Classifier Reconciliation Invariant (addresses F1)

The 16.B classifier's target query:
```sql
NOT EXISTS (SELECT 1 FROM current_tests t
  WHERE t.spec_id=s.id
    AND (t.last_result IS NULL OR t.last_result != 'stale'))
```

**Any spec with any non-stale current test row leaves the α' population.**
This includes `pass`, `fail`, `skip` — all non-stale.

Stream A's writes that cause α' reduction:
| Bucket | Writes non-stale current row? | Removes spec from α'? |
|--------|------------------------------|----------------------|
| `refreshed_pass` | Yes (pass) | Yes |
| `refreshed_fail` | Yes (fail) | Yes |
| `refreshed_fail_mixed` | Yes (fail) | Yes |
| `refreshed_skip` | Yes (skip) | Yes |
| `refreshed_partial_pass` | Yes (pass on some rows) | Yes |
| `escalated_to_c_broken_path` (A3) | No — file missing | **No, spec stays in α'** |
| `escalated_to_d_no_historical` (A3) | No — no evidence | **No, spec stays in α'** |

**Expected α' reduction** at Stream A completion:
```
α'_reduction = (refreshed_pass + refreshed_fail + refreshed_fail_mixed
                + refreshed_skip + refreshed_partial_pass)
             = 151 − (escalated_to_c_broken_path + escalated_to_d_no_historical)
```

**Key implication for umbrella reconciliation**: specs with `fail` evidence
are NO LONGER in α', but they ARE in a new state — "implemented with
failing test." The umbrella's 193-spec reconciliation covers this by
Stream C absorbing these failures and resolving them (repair test, retire
spec, or accept as known-failing with a tracking WI).

## Implementation Plan (revised)

1. Load inventory, partition A1 (114) and A3 (37). Fail-fast if sum != 151.
2. Allocate next-available test IDs for A3 usage (`max(TEST-NNNN)+1` onwards).
3. DB hash bracket open.
4. **A1 loop** (114 specs, 122 stale rows):
   - Build nodeid per identity shape.
   - Batch pytest by file path (47 unique files).
   - For each row, classify outcome and `update_test()` with the correct
     signature (no version kwarg, with changed_by/change_reason).
   - Aggregate per-spec bucket for multi-row specs.
5. **A3 loop** (37 specs):
   - For each reassigned test_id, run expanded historical query (12 fields).
   - If historical missing → escalate to D.
   - If file missing on disk → escalate to C.
   - Else run pytest on historical nodeid, classify outcome.
   - `insert_test()` with new test_id and preserved metadata.
6. DB hash bracket close. Verify mutations only to `tests` + `pipeline_events`
   (the API emits audit events; same allowance as Stream D -005).
7. **Classifier rerun**: compute α' reduction; assert it equals expected
   (all rows with non-stale writes).
8. Post-impl report.

## Files Changed

| File | Change Type | Description |
|------|------------|-------------|
| `groundtruth.db` | Write | New `tests` versions (A1) + new `tests` rows (A3); `pipeline_events` audit rows (test_updated / test_created); no spec status mutations |
| `independent-progress-assessments/spec-hygiene/scripts/stream_a_alpha_refresh.py` | New | Implementation script |

No source code changes. No test authoring.

## Exit Criteria (sharpened)

1. Every α' spec (151 total) has a terminal bucket assignment.
   Σ(buckets) = 151.
2. Classifier rerun shows α' reduction **exactly equal to** the sum of
   non-stale-writing buckets (pass + fail + skip + partial + mixed).
3. Specs still in α' after Stream A = escalated_to_c_broken_path +
   escalated_to_d_no_historical.
4. DB hash bracket documents mutations only to `tests` and
   `pipeline_events`. Other tables unchanged.
5. `pipeline_events` delta: N test_updated events (A1 writes) + M
   test_created events (A3 writes), with artifact_ids matching the
   row IDs updated/created.
6. Post-impl report includes:
   - Per-spec bucket (151 entries)
   - Per-row outcomes for multi-row specs (SPEC-1580, SPEC-1613, etc.)
   - Stream C and Stream D handoff lists
   - Sample of new/updated test rows proving `last_executed_at` freshness
   - Classifier rerun output with expected vs actual α' reduction

## Reconciliation Against Umbrella

Umbrella condition (from `por-step16c-implemented-untested-remediation-002.md:140-180`):
"Stream A must split or explicitly handle alpha-prime subcases: current
stale, historical-only/reassigned, and escalations."

This revision:
- ✓ Separates A1 (114) and A3 (37)
- ✓ A3 uses historical-row identity (not current v3 row)
- ✓ Exact-bucket coverage: 151 specs = refreshed_* + escalated_* buckets
- ✓ Classifier rerun invariant aligned with actual DB writes
- ✓ Correct `update_test()` + `insert_test()` signatures with all required fields

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
