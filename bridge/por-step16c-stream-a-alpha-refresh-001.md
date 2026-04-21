# POR Step 16.C Stream A — α' Test Refresh (151 specs)

**Status:** NEW (proposal for Codex review)
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-16
**Session:** S297
**Repo:** Agent Red Customer Engagement (groundtruth.db)
**Bridge thread:** por-step16c-stream-a-alpha-refresh
**Umbrella:** `bridge/por-step16c-implemented-untested-remediation-002.md` (GO)

## Prior Deliberations

- `DELIB-0713` (S297): Owner decisions on 16.C scope — Option B multi-stream.
- `DELIB-0712` (S297): Methodology review — α' remediation is test refresh,
  not phantom-evidence WI creation.
- Umbrella GO at `bridge/por-step16c-implemented-untested-remediation-002.md`
  includes **Finding 2** requiring Stream A to explicitly handle α' subcases.

## Objective

Restore "tested" status for the 151 α' specs — specs whose tests exist (files
on disk) but whose DB test-row evidence has gone stale or drifted. Stream A
has two internal subcases (per umbrella Finding 2):

- **A1 (114 specs)**: current test rows marked `stale`. Straight refresh.
- **A3 (37 specs)**: test rows exist but their `spec_id` was reassigned
  elsewhere in a later test version (drift). Per-spec triage.

All 47 unique historical test file paths referenced by α' specs **exist on
disk** — the files themselves are not the problem.

## Subcase A1 — Straight refresh (114 specs)

### Method

For each A1 spec:
1. Identify the spec's current_tests rows with `last_result='stale'`.
2. For each row, look up `test_file` and the test's function name.
3. Run the test via pytest: `pytest {test_file}::{test_name} --no-cov`.
4. If pass → update the test row via `db.update_test()` with `last_result='pass'`
   and fresh `last_run_at`.
5. If fail → ESCALATE to Stream C (bit-rotted test, needs repair). Record in
   post-impl report.
6. If skip → report as skipped; test row stays stale, spec stays implemented-untested.

### Expected breakdown

Best case: all 114 specs refresh cleanly → 114 specs move from
implemented-untested to implemented-tested.

Realistic case: some tests fail (bit-rot), some skip. Post-impl reports
counts:
- A1-pass: N specs refreshed
- A1-fail-escalated-to-C: M specs (Stream C picks up)
- A1-skip: K specs (no progress; stay untested)
- Total: N + M + K = 114

### A1 spec list

114 spec IDs stored in:
`independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json`
filter: `classification.category='alpha_prime' AND signals.test_id_reassignments is empty AND signals.current_stale_rows > 0`

Canonical extraction command (provided in impl script):
```python
[s['spec_id'] for s in inv['specs']
  if s['classification']['category'] == 'alpha_prime'
  and len(s['signals']['test_id_reassignments']) == 0
  and s['signals']['current_stale_rows'] > 0]
```

Post-impl report will embed the full 114-ID list.

## Subcase A3 — Reassignment triage (37 specs)

### The drift pattern

37 α' specs have test rows whose `spec_id` field was rewritten to point
elsewhere (or to empty string) in a later version. Example from inventory:

```json
"test_id_reassignments": [
  {"test_id": "TEST-1481", "now_owned_by": ""}
]
```

This means TEST-1481 used to link to spec X, but the test's latest version
has `spec_id=''`. The spec looks "untested" because `current_tests` no longer
associates TEST-1481 with it.

### Method

For each A3 spec:
1. Retrieve the list of reassigned test_ids from the inventory signal.
2. For each reassigned test, inspect its version history via
   `SELECT id, version, spec_id, test_file, last_result FROM tests WHERE id=? ORDER BY version`.
3. Classify:
   - **(a) Legitimate refactor**: test was moved to cover a different spec
     that's now verified+tested. Original spec truly needs a new test.
     → ESCALATE to Stream D (create hygiene WI).
   - **(b) Null/empty reassignment (data corruption)**: `now_owned_by=''`.
     Test still exists on disk and covers the original spec. Re-link:
     create new test row with the original `spec_id` and current `test_file`.
     Run it and verify pass.
   - **(c) Still valid linkage in some version**: the spec has at least one
     non-reassigned historical test row. Run that test and refresh (same as A1).

### A3 spec list

37 spec IDs filtered where `classification.category='alpha_prime' AND
len(signals.test_id_reassignments) > 0`.

Canonical extraction command embedded in impl script; full list in post-impl report.

### Expected breakdown

- A3a-escalated-to-D: specs where tests truly moved elsewhere
- A3b-relinked: specs where reassignment was null/corruption; relinked
  and tests pass
- A3c-refreshed: specs with alternate valid test rows refreshable like A1

## Coverage Check — Reconciliation Invariant

For every α' spec `S` (151 total), at Stream A exit the post-impl report
records exactly one of:
- `refreshed_pass` (A1 or A3c)
- `refreshed_fail_escalated_to_c`
- `skipped`
- `relinked` (A3b)
- `escalated_to_d` (A3a — should be rare; if significant, may warrant
  reopening methodology review)

Sum of buckets must equal **151**. Post-impl will fail loudly if any spec
is unaccounted.

## Implementation Plan

1. **Load inventory** and partition into A1/A3 subcase sets.
2. **DB hash bracket open**.
3. **A1 loop**: for each of 114 specs, run pytest on its stale test(s);
   update `last_result` on pass, record failure for escalation.
4. **A3 loop**: for each of 37 specs, inspect reassignment history and
   route to one of (a), (b), (c) paths.
5. **DB hash bracket close** + assert only expected tables mutated
   (`tests` table versions appended, no spec status changes).
6. **Verify invariant**: re-run the 16.B classifier to confirm A1+A3
   specs moved out of α' (into "tested" population or into Stream C/D
   queues).

## Files Changed

| File | Change Type | Description |
|------|------------|-------------|
| `groundtruth.db` | Write | New `tests` rows appended (version bumps); no spec-status mutations |
| `independent-progress-assessments/spec-hygiene/scripts/stream_a_alpha_refresh.py` | New | Implementation script |
| Post-impl report | New | Full per-spec bucket assignment + escalation lists |

No source code changes. No test changes (we run existing tests; we don't
author or modify them).

## Risks

- **Medium:** Running 114+ pytest invocations takes time. Mitigation: batch
  by file path (47 unique test files across 151 specs) to run each file once
  and map results back to specs.
- **Medium:** Bit-rotted tests may fail, revealing real regressions. Each
  is a new finding — escalated to Stream C for repair. The post-impl report
  flags each with file:line evidence so Stream C has everything it needs.
- **Low:** A3 relink (subcase b) creates new test row versions. This is a
  normal KB mutation pattern used throughout the project; rollback is via
  `db.update_test(version=N-1)` equivalent.
- **Medium:** If A3a escalations are large (>10), it suggests the methodology
  review missed a pattern. Mitigation: post-impl report flags high
  escalation counts and requests owner review before Stream D consumes them.

## Exit Criteria

1. All 151 α' specs have a terminal bucket assignment (151 = sum of buckets).
2. DB hash bracket documents exactly the expected mutations (test-row
   appends, no status mutations on spec rows).
3. Classifier re-run confirms α' population reduction matches reported
   bucket counts.
4. Post-impl report lists:
   - 114 A1 specs with bucket assignments
   - 37 A3 specs with bucket assignments + per-spec triage decision
   - Any escalations to Stream C or Stream D with source-spec IDs
5. No Stream A spec silently stays in α' — absence of terminal state is a fail.

## Reconciliation Against Umbrella

Umbrella exit criteria require Stream A to "refresh 151 α' specs OR
escalate to Stream C (moved count reported)." This proposal's coverage
invariant enforces exactly that: every α' spec has a terminal bucket.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
