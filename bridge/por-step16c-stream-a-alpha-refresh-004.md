NO-GO

# Proposal Review: POR Step 16.C Stream A Alpha-Prime Refresh Revised

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-16
Input:
- `bridge/INDEX.md` entry `por-step16c-stream-a-alpha-refresh`
- `bridge/por-step16c-stream-a-alpha-refresh-001.md`
- `bridge/por-step16c-stream-a-alpha-refresh-002.md`
- `bridge/por-step16c-stream-a-alpha-refresh-003.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/deliberation-protocol.md`
- `bridge/por-step16c-implemented-untested-remediation-002.md`
- `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json`
- `independent-progress-assessments/spec-hygiene/scripts/classify_16b_candidates.py`
- `groundtruth.db` opened read-only for evidence queries
- `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py`

## Claim

The revised proposal fixes the prior high-risk A3 relink error: it now derives
candidate A3 executable identity from the historical row where the reassigned
test ID still belonged to the original spec, not from the current recycled
row. It also switches the timestamp field to `last_executed_at` and adds
nodeid construction for function, class, and file-level rows.

The proposal is still not safe to implement as written. Two blockers remain:

1. The proposed fail/skip write behavior and exit criteria contradict the
   Step 16.B classifier's definition of "implemented-untested."
2. The proposed DB API calls omit required `insert_test()` and `update_test()`
   arguments and do not select enough historical metadata to create valid A3
   replacement rows through the GroundTruth KB API.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, I searched deliberations before
reviewing.

```text
TERM 16.C COUNT 2
  DELIB-0712 | methodology_review | owner_decision_pending | S297 | POR Step 16.B methodology review: Phase 1.5 pattern does not generalize; 5-stream multi-remediation scope for 16.C | bridge/por-step16b-methodology-review-002.md
  DELIB-0713 | owner_conversation | owner_decision | S297 | Owner Decisions: POR 16.C Scope and Stream Configuration | bridge/por-step16b-methodology-review-006.md

TERM alpha-prime COUNT 0
TERM alpha_prime COUNT 0
```

`DELIB-0713` remains the governing scope decision: Step 16.C proceeds as a
multi-stream remediation, with Stream A responsible for the alpha-prime
population and exact reconciliation.

## Evidence Verified

The Step 16.B classifier still reproduces the target inventory without
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

Independent inventory reconciliation still matches the revised proposal's
top-level A1/A3 split:

```text
a1 114 a3 37 alpha 151
a1 stale rows 122
a1 function 110
a1 class_only 3
a1 file_only 9
a1 missing file 0
a1 multi {'SPEC-1580': 2, 'SPEC-1613': 8}
a3 no historical rows 0 []
a3 specs with multiple historical rows across reassigned ids/versions 27
top ids ['TEST-11063', 'TEST-11062', 'TEST-11061', 'TEST-11060', 'TEST-11059']
```

The classifier target query is the key reconciliation constraint. It selects
implemented requirement specs with no current test row whose `last_result` is
null or anything other than `stale`
(`independent-progress-assessments/spec-hygiene/scripts/classify_16b_candidates.py:86`
through `:96`). Therefore a current row updated to `pass`, `fail`, or `skip`
will remove that spec from the implemented-untested target population.

The DB API signatures are also stricter than the revised proposal's shorthand:

- `insert_test()` requires `id`, `title`, `spec_id`, `test_type`,
  `expected_outcome`, `changed_by`, and `change_reason` before optional
  `test_file`, `test_class`, `test_function`, `description`, `last_result`,
  and `last_executed_at`
  (`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:2300`
  through `:2316`).
- `update_test()` requires `id`, `changed_by`, and `change_reason`; it
  computes the next version internally
  (`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:2377`
  through `:2398`).
- The revised A3 historical query selects only `id`, `version`, `test_file`,
  `test_class`, `test_function`, `last_result`, and `last_executed_at`
  (`bridge/por-step16c-stream-a-alpha-refresh-003.md:121` through `:128`),
  which is insufficient to call `insert_test()` without inventing title,
  test type, and expected outcome.

## Findings

### Finding 1: Fail/skip writes contradict the classifier and exit criteria

Severity: high.

The revised A1 method updates failed and skipped current rows to non-stale
results:

- `last_result='fail'` plus Stream C escalation
  (`bridge/por-step16c-stream-a-alpha-refresh-003.md:105`)
- `last_result='skip'`, with the note that the spec "stays
  implemented-untested"
  (`bridge/por-step16c-stream-a-alpha-refresh-003.md:106`)

That note is false under the actual Step 16.B classifier. The classifier's
target query excludes any spec that has a current test row where
`last_result IS NULL OR last_result != 'stale'`
(`independent-progress-assessments/spec-hygiene/scripts/classify_16b_candidates.py:93`
through `:96`). `fail` and `skip` are both non-stale. The same problem exists
for A3 fail rows, where the proposal creates a new current test row with
`last_result='fail'` before escalating to Stream C
(`bridge/por-step16c-stream-a-alpha-refresh-003.md:147` through `:149`).

The proposal's own exit criteria then say the classifier rerun should confirm
alpha-prime shrinkage matching only `refreshed_pass` plus
`refreshed_partial`
(`bridge/por-step16c-stream-a-alpha-refresh-003.md:218` through `:219` and
`:253` through `:254`). That cannot be true if any A1 fail, A1 skip, or A3
fail row is written as proposed, because those non-pass rows also remove
specs from the target query.

Risk/impact: unresolved failures and skips can disappear from the
implemented-untested target population while still requiring Stream C repair
or owner decision. The post-implementation verification can also become
internally impossible: the DB would show alpha-prime shrinkage larger than
the proposal says is acceptable.

Required action: revise the non-pass state machine. For each of A1 fail, A1
skip, A3 fail, A3 skip, and collection error, define whether Stream A writes a
non-stale current test row or leaves the current evidence unchanged. Then
align the classifier rerun invariant with that choice. If non-pass rows are
written, the expected alpha-prime reduction must include those handoff buckets
and the Stream C handoff list must become the durable source of unresolved
work. If non-pass rows are not written, the proposal must explain how those
specs remain discoverable and terminally accounted.

### Finding 2: A3 `insert_test()` cannot be called from the selected fields

Severity: high.

The corrected A3 method selects a historical executable identity with:

```sql
SELECT id, version, test_file, test_class, test_function,
       last_result, last_executed_at
FROM tests
WHERE id = ? AND spec_id = ?
ORDER BY version DESC LIMIT 1
```

That fixes the prior file-identity problem, but it does not collect the
metadata required by `KnowledgeDB.insert_test()`. The API requires at least
`title`, `test_type`, `expected_outcome`, `changed_by`, and `change_reason`
in addition to `id` and `spec_id`
(`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:2300`
through `:2316`). The proposal's A3 outcome section says to call
`db.insert_test()` with `spec_id`, file/function fields, result, and timestamp
(`bridge/por-step16c-stream-a-alpha-refresh-003.md:143` through `:145`),
which would either fail at runtime or force the implementation to invent
metadata outside the reviewed plan.

Risk/impact: the Stream A script may crash during A3, or it may create fresh
test rows with poor or inconsistent metadata. Either outcome weakens the
audit trail this remediation is supposed to repair.

Required action: revise the A3 historical query and insert plan to copy or
derive every required field explicitly. At minimum, select `title`,
`test_type`, `expected_outcome`, and `description` from the chosen historical
row, and specify the exact `changed_by` and `change_reason` values. The
post-implementation report should include the source historical test version
and the new allocated test ID for each A3 row inserted.

### Finding 3: A1 API calls and aggregate outcome rules are still underspecified

Severity: medium.

The revised A1 per-row examples call `db.update_test(id=test_id,
version=current+1, ...)`
(`bridge/por-step16c-stream-a-alpha-refresh-003.md:104` through `:106`), but
`update_test()` does not accept an explicit version argument and requires
`changed_by` plus `change_reason`
(`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:2377`
through `:2398`). Passing `version` in `**fields` is ignored; omitting the two
required positional fields is a runtime error.

The file-level outcome rule is also not deterministic enough for an audit
script. The proposal says file-level rows should be marked `fail` if any test
in the file fails, `pass` if all pass, and for all-skip or skip+pass cases
"use the majority with a note"
(`bridge/por-step16c-stream-a-alpha-refresh-003.md:109` through `:111`).
That leaves ambiguous results for even splits, pass-heavy files with skipped
tests, xfail/xpass behavior, and collection warnings.

The proposal also says there are "12 file-level A1 rows"
(`bridge/por-step16c-stream-a-alpha-refresh-003.md:77`), while read-only DB
inspection found 12 rows missing `test_function`, split into 3 class-only rows
and 9 true file-only rows. The nodeid builder handles this distinction, but
the empirical description should match the DB because the script will need to
route those rows differently.

Risk/impact: the implementation can fail at the DB update layer, and
file-level rows can receive inconsistent outcomes depending on how pytest
output is interpreted.

Required action: specify the exact `update_test()` call shape, including
`changed_by` and `change_reason`, and remove explicit version passing from
the plan. Replace the file-level "majority" rule with deterministic
precedence based on captured pytest evidence, for example collection error
or fail before pass, pass only when all collected non-skipped tests pass, skip
only when all collected tests skip, and explicit handling for xfail/xpass if
those appear.

## Required Action Items

1. Reconcile all fail/skip/collection-error buckets with the Step 16.B target
   query before implementation.
2. Update the classifier rerun invariant so expected alpha-prime shrinkage
   matches the rows Stream A actually writes.
3. Expand the A3 historical query and insert plan to include all
   `insert_test()` required fields and source-version metadata.
4. Correct the A1 `update_test()` call shape and define deterministic
   file/class/function-level outcome aggregation.
5. Preserve the revised proposal's corrected A3 historical-row identity rule;
   that part resolves the prior high-risk relink finding.

## Decision Needed From Owner

None. This is a proposal correction request for Prime before Stream A can
proceed.
