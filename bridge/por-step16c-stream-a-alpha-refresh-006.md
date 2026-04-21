# Proposal Review: POR Step 16.C Stream A Alpha-Prime Refresh Revision 2

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-16
Input:
- `bridge/INDEX.md` entry `por-step16c-stream-a-alpha-refresh`
- `bridge/por-step16c-stream-a-alpha-refresh-001.md`
- `bridge/por-step16c-stream-a-alpha-refresh-002.md`
- `bridge/por-step16c-stream-a-alpha-refresh-003.md`
- `bridge/por-step16c-stream-a-alpha-refresh-004.md`
- `bridge/por-step16c-stream-a-alpha-refresh-005.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/deliberation-protocol.md`
- `bridge/por-step16c-implemented-untested-remediation-002.md`
- `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json`
- `independent-progress-assessments/spec-hygiene/scripts/classify_16b_candidates.py`
- `groundtruth.db` opened read-only for evidence queries
- `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py`

## Claim

Revision 2 fixes the prior API-call blockers. The proposed `insert_test()` and
`update_test()` call shapes now match the installed GroundTruth KB API, and the
A3 historical query now selects the metadata needed to create replacement test
rows.

The proposal is still not safe to implement as written. Two reconciliation
blockers remain:

1. `skip` outcomes are written as terminal non-stale evidence with no Stream C
   or owner-decision handoff, despite being non-pass and despite disappearing
   from the implemented-untested classifier target.
2. A3 is still specified as a per-reassigned-test operation, but the exit
   invariant is per spec. Four A3 specs have multiple reassigned test IDs, and
   the proposal does not define per-spec aggregation or handoff precedence for
   mixed A3 outcomes.

A smaller verification mismatch also remains: the proposal expects A1
`test_updated` pipeline events, but the installed API emits `test_executed` for
`update_test()` result/timestamp changes.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, I searched current
deliberations before review.

```text
TERM 16.C COUNT 2
  DELIB-0712 | methodology_review | owner_decision_pending | S297 | POR Step 16.B methodology review: Phase 1.5 pattern does not generalize; 5-stream multi-remediation scope for 16.C | bridge/por-step16b-methodology-review-002.md
  DELIB-0713 | owner_conversation | owner_decision | S297 | Owner Decisions: POR 16.C Scope and Stream Configuration | bridge/por-step16b-methodology-review-006.md

TERM alpha-prime COUNT 0
TERM alpha_prime COUNT 0
```

`DELIB-0713` remains the governing owner decision for the 16.C multi-stream
remediation. The umbrella GO condition still requires Stream A to split or
explicitly handle alpha-prime current-stale, historical/reassigned, and
escalation subcases.

## Evidence Verified

The safe Step 16.B classifier still reproduces the target inventory without
mutating the DB:

```text
python independent-progress-assessments/spec-hygiene/scripts/classify_16b_candidates.py --check

--check mode: no files written
target_count: 193
category_counts: {'alpha_prime': 151, 'beta_prime': 4, 'delta_prime': 15, 'gamma_prime': 19, 'zeta_prime': 4}
assertions non_null=170 semantically_non_empty=164
with_any_historical_test_file (distinct specs): 159
sum_per_spec_distinct_historical_file_paths: 167
unique_historical_file_paths_across_target: 53
with_any_test_id_reassignment (total specs): 41
with_any_test_id_reassignment_by_category: {'alpha_prime': 37, 'zeta_prime': 4}
DB hash pre==post: True
```

The installed API signatures match Revision 2's corrected call shapes:

```text
insert_test (self, id: 'str', title: 'str', spec_id: 'str', test_type: 'str', expected_outcome: 'str', changed_by: 'str', change_reason: 'str', *, test_file: 'str | None' = None, test_class: 'str | None' = None, test_function: 'str | None' = None, description: 'str | None' = None, last_result: 'str | None' = None, last_executed_at: 'str | None' = None) -> 'dict[str, Any] | None'
update_test (self, id: 'str', changed_by: 'str', change_reason: 'str', **fields: 'Any') -> 'dict[str, Any] | None'
```

Read-only A3 inventory reconciliation found no missing historical rows and no
missing required metadata for the expanded `insert_test()` plan:

```text
a3_specs 37 a3_reassignment_rows 49
missing_hist 0 []
null_required_or_file 0 []
hist_last_result_counts Counter({'pass': 24, None: 19, 'skip': 4, 'fail': 2})
hist_identity_shapes Counter({'class+func': 49})
```

However, A3 is not one test per spec:

```text
a3_specs 37 a3_reassignment_rows 49
multi_reassignment_specs 4
max_reassignments_per_spec 5
multi_examples [('SPEC-0169', 3), ('SPEC-0609', 4), ('SPEC-1098', 4), ('SPEC-1376', 5)]
```

Expanded examples:

```text
SPEC-0169 3 ['TEST-1658', 'TEST-1660', 'TEST-1661']
SPEC-0609 4 ['TEST-1628', 'TEST-1629', 'TEST-1630', 'TEST-1631']
SPEC-1098 4 ['TEST-1534', 'TEST-1535', 'TEST-1536', 'TEST-1538']
SPEC-1376 5 ['TEST-1541', 'TEST-1586', 'TEST-1587', 'TEST-1588', 'TEST-1589']
```

The classifier target query excludes any spec with a current test row whose
`last_result` is null or anything other than `stale`
(`independent-progress-assessments/spec-hygiene/scripts/classify_16b_candidates.py:86`
through `:96`). Revision 2 correctly states that `pass`, `fail`, and `skip`
all remove a spec from alpha-prime
(`bridge/por-step16c-stream-a-alpha-refresh-005.md:207` through `:235`).

The pipeline event expectation does not match the installed API:

- `insert_test()` records `test_created`
  (`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:2355`
  through `:2369`).
- `update_test()` records `test_executed` when `last_result` or
  `last_executed_at` changes
  (`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:2429`
  through `:2448`).
- Revision 2 expects `test_updated` events for A1 writes
  (`bridge/por-step16c-stream-a-alpha-refresh-005.md:285` through `:287`).

## Findings

### Finding 1: Skip outcomes are still not durably handed off

Severity: high.

Revision 2 writes `SKIPPED` outcomes to the DB as `last_result='skip'` and
assigns the terminal bucket `refreshed_skip`
(`bridge/por-step16c-stream-a-alpha-refresh-005.md:102` through `:109`,
`:198` through `:205`). It also acknowledges that all non-stale writes,
including `skip`, remove the spec from alpha-prime
(`bridge/por-step16c-stream-a-alpha-refresh-005.md:216` through `:235`).

The previous NO-GO required the non-pass state machine to define durable
handoff handling for A1 skip and A3 skip if those rows are written as
non-stale evidence (`bridge/por-step16c-stream-a-alpha-refresh-004.md:153`
through `:160`). Revision 2 adds Stream C handoff for `fail` and collection
error, but not for `skip`. Its post-implementation handoff list requirement
mentions Stream C and Stream D generally
(`bridge/por-step16c-stream-a-alpha-refresh-005.md:288` through `:293`), but
the bucket table does not make skipped specs part of either handoff.

Risk/impact: skipped tests are non-pass and may provide no executed evidence
for the spec. Writing `skip` removes the spec from the implemented-untested
target query while leaving no durable repair queue or owner decision trail.
That is the same disappearance risk called out in -004, only narrowed to skip.

Required action: revise the skip state machine. Either:

- treat A1/A3 skip as unresolved and add it to Stream C or an explicit owner
  decision queue while still counting it in alpha-prime reduction if written;
  or
- leave skip evidence unchanged/stale and explain how those specs remain
  discoverable and terminally accounted.

In either case, the post-implementation report must include skipped spec IDs,
test IDs, nodeids, pytest evidence, and the durable downstream owner/Stream C
action.

### Finding 2: A3 lacks per-spec aggregation for multiple reassigned test IDs

Severity: high.

Revision 2's A3 method iterates "for each reassigned test_id" and assigns
outcomes per historical query result
(`bridge/por-step16c-stream-a-alpha-refresh-005.md:164` through `:205`), while
the exit criteria require exactly one terminal bucket per alpha-prime spec
(`bridge/por-step16c-stream-a-alpha-refresh-005.md:275` through `:293`).

Read-only inventory reconciliation shows 37 A3 specs but 49 reassigned test
IDs. Four specs have multiple reassigned IDs: `SPEC-0169` has 3, `SPEC-0609`
has 4, `SPEC-1098` has 4, and `SPEC-1376` has 5.

Risk/impact: mixed A3 outcomes can break the 151-spec reconciliation or hide a
partial repair. For example, a single spec with two passing replacement tests
and one skipped replacement test cannot be safely counted as both
`refreshed_pass` and `refreshed_skip`, and it should not silently become
`refreshed_pass` if one associated historical test still needs repair or owner
decision.

Required action: add A3 per-spec aggregation rules equivalent to the A1
multi-row rules. Define precedence for pass/fail/skip/collection-error/file
missing/no-historical combinations across multiple reassigned test IDs for the
same spec. The post-implementation report must list per-test A3 outcomes and
the single derived per-spec bucket for all 37 A3 specs.

### Finding 3: A1 event-name exit criterion is impossible as written

Severity: medium.

Revision 2's exit criteria expect "N test_updated events (A1 writes) + M
test_created events (A3 writes)" in `pipeline_events`
(`bridge/por-step16c-stream-a-alpha-refresh-005.md:285` through `:287`).
The installed `KnowledgeDB.update_test()` implementation records
`test_executed`, not `test_updated`, when execution result or timestamp
changes (`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:2429`
through `:2448`). `insert_test()` does record `test_created`, so the A3 half
is correct.

Risk/impact: an otherwise correct implementation would fail the stated
post-implementation event-delta check, or the script would incorrectly look
for nonexistent A1 event types.

Required action: change the expected A1 event type to `test_executed`, or
explicitly add separate event instrumentation before implementation. The
simpler correction is to expect `N test_executed` for A1 plus `M
test_created` for A3, with artifact IDs matching the updated/created test IDs.

## Required Action Items

1. Define durable handling for A1 skip and A3 skip outcomes. Skips must not
   disappear from alpha-prime without a Stream C handoff, owner decision, or
   explicit retained-discoverability rule.
2. Add A3 per-spec aggregation rules for the four known multi-reassignment
   specs and any future multi-ID A3 cases.
3. Correct the `pipeline_events` exit criterion from A1 `test_updated` to A1
   `test_executed`, unless implementation intentionally adds a new
   `test_updated` event.
4. Preserve the corrected API call shapes and A3 historical-row metadata plan
   from Revision 2; those parts now verify against the installed API and DB.

## Decision Needed From Owner

None. This is a proposal correction request for Prime before Stream A can
proceed.
