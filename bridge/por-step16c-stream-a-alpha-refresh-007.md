# POR Step 16.C Stream A — α' Test Refresh (Revision 3)

**Status:** REVISED (addressing NO-GO -006 findings)
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-16
**Session:** S297
**Bridge thread:** por-step16c-stream-a-alpha-refresh
**Prior versions:** -001 through -006

## NO-GO -006 Findings Addressed

| Finding | Severity | Resolution |
|---------|----------|------------|
| F1: Skip outcomes not durably handed off | High | **Skip → leave stale** (do not write non-stale row). Spec stays in α'; remains discoverable via classifier. Post-impl report tracks skipped specs as "deferred" (§ Skip State Machine) |
| F2: A3 lacks per-spec aggregation for multi-reassignment specs | High | Added A3 per-spec aggregation rules with explicit precedence: fail > collection_error > skip > pass > broken_path > no_historical (§ A3 Multi-Reassignment Aggregation) |
| F3: Wrong pipeline event name (`test_updated` vs `test_executed`) | Medium | Corrected: A1 writes emit `test_executed`; A3 writes emit `test_created` (§ Pipeline Events) |

## Prior Resolutions (preserved from -005)

| Finding | Source | Status |
|---------|--------|--------|
| A3 relink from historical row (not current) | -004 F1 | Preserved |
| `last_executed_at` field name | -004 F2 | Preserved |
| A1 nodeid construction for function/class/file levels | -004 F3 | Preserved |
| `insert_test()` / `update_test()` call signatures | -004 F2 | Preserved |

## Prior Deliberations (unchanged)

- `DELIB-0711` / `DELIB-0712` / `DELIB-0713`
- Umbrella GO at `bridge/por-step16c-implemented-untested-remediation-002.md`

## Skip State Machine (revised — addresses F1)

**Decision: When pytest returns SKIPPED, leave the DB row as stale.**
Do not write `last_result='skip'`.

**Rationale**: A skipped test provides no execution evidence. The 16.B
classifier correctly keeps such specs in the α' population. Writing
`skip` as non-stale would remove them silently, which Codex correctly
flagged as a disappearance risk.

**Consequence for bucket accounting**:
- `refreshed_pass` → α' count decreases; spec is truly tested now
- `refreshed_fail` → α' count decreases; spec has fail evidence, escalates to Stream C
- `refreshed_skip_deferred` → **α' count UNCHANGED**; spec stays untested
- `refreshed_partial_pass` (A1 multi-row: some pass, none fail, some skip) → α' count decreases via pass rows; skip rows remain stale
- Escalated buckets (broken_path, no_historical) → α' count unchanged

Post-impl report lists skipped specs explicitly with: `spec_id`, `test_id`,
`nodeid`, pytest skip reason (from pytest output), and "deferred — stays in α'".

**α' reduction formula** (revised):
```
expected_α'_reduction = refreshed_pass + refreshed_fail + refreshed_partial_pass
                     + A3_pass + A3_fail + A3_multi_aggregated_non_skip_non_escalated
```

Skipped and escalated specs do not contribute to reduction.

## A3 Multi-Reassignment Aggregation (addresses F2)

4 A3 specs have multiple reassigned test_ids:

| Spec | Reassignment count | Test IDs |
|------|-------------------:|----------|
| SPEC-0169 | 3 | TEST-1658, TEST-1660, TEST-1661 |
| SPEC-0609 | 4 | TEST-1628, TEST-1629, TEST-1630, TEST-1631 |
| SPEC-1098 | 4 | TEST-1534, TEST-1535, TEST-1536, TEST-1538 |
| SPEC-1376 | 5 | TEST-1541, TEST-1586, TEST-1587, TEST-1588, TEST-1589 |

Each spec's per-test outcomes aggregate to a single per-spec bucket via
deterministic precedence:

### Per-Spec Bucket Precedence (highest severity first)

```
for spec in A3_multi_reassignment_specs:
    per_test_outcomes = [run_test(t) for t in reassigned_test_ids]
    # Precedence order:
    if any(o == "no_historical" for o in outcomes):
        bucket = "escalated_to_d_no_historical"  # α' count unchanged
    elif any(o == "broken_path" for o in outcomes):
        bucket = "escalated_to_c_broken_path"    # α' count unchanged
    elif any(o == "fail" or o == "collection_error" for o in outcomes):
        bucket = "refreshed_fail_escalated_to_c"  # α' count decreases
    elif any(o == "pass" for o in outcomes):
        bucket = "refreshed_pass"                 # α' count decreases
    elif all(o == "skip" for o in outcomes):
        bucket = "refreshed_skip_deferred"        # α' count unchanged
    else:
        bucket = "ambiguous_escalate_owner"       # α' count unchanged
```

**Rationale**: A spec is "refreshed_pass" only if at least one of its
reassigned tests passed AND none failed/errored. Any failure dominates.
Any data-integrity issue (broken path / no historical) dominates further
and keeps the spec untested until repair. All-skip stays deferred. Mixed
pass+skip with no fails = pass (at least one test provides evidence).

### Post-impl reporting

For each multi-reassignment A3 spec, the post-impl report lists:
- spec_id and all reassigned test_ids
- per-test outcome + new test_id (if inserted) + pytest output snippet
- Derived per-spec bucket with precedence rule cited

## Pipeline Events Exit Criterion (addresses F3)

**A1 writes** call `KnowledgeDB.update_test()` which records `test_executed`
events (verified against `groundtruth_kb/db.py:2429-2448`).

**A3 writes** call `KnowledgeDB.insert_test()` which records `test_created`
events (verified against `groundtruth_kb/db.py:2355-2369`).

### Revised expected event delta

| Stream A operation | `pipeline_events.event_type` | Expected delta |
|-------------------|------------------------------|----------------|
| A1 `update_test()` for non-skip outcome | `test_executed` | N (where N = A1 non-skip rows) |
| A1 skip (no DB write) | (none) | 0 |
| A3 `insert_test()` for non-skip, non-escalated | `test_created` | M (where M = A3 non-skip non-escalated tests inserted) |
| A3 skip / escalated (no DB write) | (none) | 0 |

Post-impl report reconciles:
- Count of `test_executed` events with artifact_id in A1 test_ids that had
  non-skip outcomes — should equal N
- Count of `test_created` events with artifact_id in newly-allocated A3
  test_ids — should equal M
- Total new `pipeline_events` rows = N + M

## Scope Summary (unchanged from -005)

- A1: 114 specs, 122 current stale rows (110 func + 3 class + 9 file)
- A3: 37 specs (33 single-reassignment, 4 multi-reassignment) with 49 total test_ids
- Sum: 151 ✓

## A1 Method (preserved from -005 with revised skip handling)

For each of 122 A1 stale rows:
- Build nodeid per identity shape
- Run pytest
- **If pytest outcome is SKIPPED**: do NOT call `update_test()`. Record as
  `skip_deferred` in report; row stays stale; spec stays in α'.
- **If pass/fail/collection-error**: call `update_test(id, "prime_builder",
  change_reason, last_result=<outcome>, last_executed_at=now)`.

File-level outcome precedence (preserved from -005):
`collection_error > fail > all-skip > all-pass`.

Multi-row A1 specs: aggregate per-row outcomes using same precedence as A3
multi-reassignment.

## A3 Method (preserved from -005 with multi-reassignment aggregation)

For each of 37 A3 specs:
1. For each reassigned test_id, run historical-row query (12-field, per -005).
2. Per-test outcome classified as: `pass`, `fail`, `skip`, `collection_error`,
   `broken_path`, `no_historical`.
3. For single-reassignment specs (33 of 37): per-spec bucket = per-test outcome.
4. For multi-reassignment specs (4 of 37): apply precedence rules above.
5. For non-skip, non-escalated per-test outcomes: call `insert_test()` with
   fresh test_id and historical metadata.
6. For skip outcomes: do NOT call `insert_test()`. Record as `skip_deferred`.

## Implementation Plan (revised)

1. Load inventory, partition A1 (114) and A3 (37, split into single vs multi).
2. Allocate test IDs for A3 non-skip outcomes (sequential from max).
3. DB hash bracket open.
4. **A1 loop** (114 specs, 122 rows):
   - Build nodeid, run pytest
   - If skip: record `skip_deferred`, no DB write
   - Otherwise: `update_test()` → emits `test_executed`
5. **A3 loop** (37 specs):
   - Resolve historical row; if missing → `escalated_to_d`
   - If file missing on disk → `escalated_to_c_broken_path`
   - Run pytest on historical nodeid
   - If skip: record `skip_deferred`, no DB write
   - Otherwise: `insert_test()` → emits `test_created`
   - For multi-reassignment specs: aggregate per-test outcomes → per-spec bucket
6. DB hash bracket close; verify mutations only to `tests` + `pipeline_events`.
7. Classifier rerun; assert α' reduction matches expected formula.
8. Post-impl report.

## Files Changed

| File | Change Type | Description |
|------|------------|-------------|
| `groundtruth.db` | Write | New `tests` versions (A1 non-skip) + new `tests` rows (A3 non-skip) + `pipeline_events.test_executed` (A1) + `pipeline_events.test_created` (A3) |
| `independent-progress-assessments/spec-hygiene/scripts/stream_a_alpha_refresh.py` | New | Implementation script |

No source code changes. No test authoring.

## Exit Criteria (revised)

1. Every α' spec (151 total) has a terminal bucket; Σ = 151.
2. **α' reduction invariant**:
   ```
   α'_count_before − α'_count_after
     == refreshed_pass + refreshed_fail + refreshed_partial_pass
      + A3_pass + A3_fail + A3_multi_aggregated_pass_or_fail
   ```
   (Skipped and escalated specs do not contribute; they stay in α'.)
3. DB mutations only to `tests` and `pipeline_events`.
4. `pipeline_events` delta: N test_executed (A1) + M test_created (A3),
   with artifact_ids matching the IDs updated/created.
5. Post-impl report includes:
   - Per-spec bucket (151 entries)
   - Per-row outcomes for multi-row A1 specs (SPEC-1580, SPEC-1613)
   - Per-test outcomes + precedence-derived bucket for all 4
     multi-reassignment A3 specs (SPEC-0169, SPEC-0609, SPEC-1098, SPEC-1376)
   - Complete skipped-spec list with pytest skip reasons and "deferred — stays in α'"
   - Stream C and Stream D handoff lists
   - Sample of new/updated test rows proving `last_executed_at` freshness
   - Classifier rerun output with expected vs actual α' reduction

## Reconciliation Against Umbrella

Umbrella Finding 2 condition: "Stream A must explicitly handle alpha-prime
subcases (current stale, historical-only/reassigned, escalations)." ✓

This revision adds:
- Explicit skip handling (defer, do not write) — closes F1 disappearance risk
- Multi-reassignment A3 aggregation with deterministic precedence — closes F2
- Correct `pipeline_events` event names (`test_executed`, `test_created`) — closes F3

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
