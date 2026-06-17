NO-GO

# Proposal Review: POR Step 16.C Stream A Alpha-Prime Refresh

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-16
Input:
- `bridge/INDEX.md` entry `por-step16c-stream-a-alpha-refresh`
- `bridge/por-step16c-stream-a-alpha-refresh-001.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/deliberation-protocol.md`
- `bridge/por-step16c-implemented-untested-remediation-002.md`
- `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json`
- `independent-progress-assessments/spec-hygiene/scripts/classify_16b_candidates.py`
- `groundtruth.db` opened read-only for evidence queries
- `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py`

## Claim

The Stream A proposal correctly partitions the 151 alpha-prime specs into 114
A1 specs and 37 A3 specs, but it is not safe to implement as written.

The blocker is A3. The proposal treats `now_owned_by=''` as evidence that the
current test row can be relinked with the current `test_file`
(`bridge/por-step16c-stream-a-alpha-refresh-001.md:101` through `:104`).
Read-only DB inspection shows the opposite: for all 49 reassigned A3 test IDs,
the latest current row has `spec_id=''` and a current `test_file` that differs
from the historical file path that originally backed the spec. Relinking those
current rows would attach unrelated tests to the original specs.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, I searched deliberations before
reviewing.

```text
TERM 16.C COUNT 2
  DELIB-0712 | methodology_review | owner_decision_pending | S297 | POR Step 16.B methodology review: Phase 1.5 pattern does not generalize; 5-stream multi-remediation scope for 16.C | bridge/por-step16b-methodology-review-002.md
  DELIB-0713 | owner_conversation | owner_decision | S297 | Owner Decisions: POR 16.C Scope and Stream Configuration | bridge/por-step16b-methodology-review-006.md
```

`DELIB-0713` remains the governing scope decision. The umbrella GO also
requires Stream A to explicitly split current stale rows from historical-only
or reassigned alpha-prime evidence
(`bridge/por-step16c-implemented-untested-remediation-002.md:140` through
`:180`).

## Evidence Verified

The safe classifier still reproduces the Step 16.B inventory without mutating
the DB:

```text
python independent-progress-assessments/spec-hygiene/scripts/classify_16b_candidates.py --check

--check mode: no files written
target_count: 193
category_counts: {'alpha_prime': 151, 'beta_prime': 4, 'delta_prime': 15, 'gamma_prime': 19, 'zeta_prime': 4}
with_any_test_id_reassignment (total specs): 41
with_any_test_id_reassignment_by_category: {'alpha_prime': 37, 'zeta_prime': 4}
DB hash pre==post: True
```

Independent JSON reconciliation matched the proposal's top-level counts:

```text
alpha_count 151
a1_count 114
a3_count 37
a1_current_stale_rows_total 122
a3_current_rows_total 0
a3_current_stale_rows_total 0
a1_plus_a3 151
alpha_unique_paths 47
alpha_missing_paths 0 []
a3_reassignment_rows 49
a3_now_owned_by_counts {'': 49}
```

The A3 current-row drift check is the blocker:

```text
a3_reassigned_rows 49
current_file_matches_inventory 0
current_file_differs_from_inventory 49
SPEC-0159 TEST-1481 orig= ['tests/regression/test_migration_compat.py'] current= tests/visual/test_widget_structure.py func= test_input_textarea_exists[chromium] match= False
SPEC-0169 TEST-1658 orig= ['tests/unit/test_avatar_upload.py'] current= tests/ops/test_pre_flight_specs.py func= test_skip_helper match= False
SPEC-0212 TEST-1522 orig= ['tests/security/test_config_pipeline_live.py'] current= tests/test_forgot_password.py func= test_different_tokens_unique match= False
```

The historical rows for those original specs still have executable identities:

```text
a3_historical_rows_for_original_spec 79
missing_hist_file 0
missing_hist_function 0
hist_file_exists_false 0
hist_result_counts {None: 49, 'fail': 2, 'pass': 24, 'skip': 4}
```

A1 also has execution-identity edge cases not covered by the proposal's
`pytest {test_file}::{test_name}` method:

```text
a1_current_rows 122
a1_rows_missing_file 0
a1_rows_missing_function 12
a1_rows_nonstale 0
a1_specs_with_multi_stale 2
a1_multi_sample [('SPEC-1580', 2), ('SPEC-1613', 8)]
```

Finally, the proposed timestamp field does not match the DB API. The proposal
calls for a fresh `last_run_at`
(`bridge/por-step16c-stream-a-alpha-refresh-001.md:40` through `:41`), but
`KnowledgeDB.update_test()` carries forward or updates `last_executed_at`
(`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:2397`
through `:2398`) and writes `last_executed_at` into the new test version
(`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:2407`
through `:2422`).

## Findings

### Finding 1: A3 relink would attach the wrong current files

Severity: high.

The proposal's A3b method says null/empty reassignment means the test "still
exists on disk and covers the original spec" and should be relinked using the
current `test_file`
(`bridge/por-step16c-stream-a-alpha-refresh-001.md:101` through `:104`).
Read-only DB inspection found 49 of 49 A3 reassigned current rows have
`spec_id=''`, but none of those current rows point to the original historical
file path. Example: `TEST-1481` historically linked `SPEC-0159` to
`tests/regression/test_migration_compat.py`, while its current row points at
`tests/visual/test_widget_structure.py::test_input_textarea_exists[chromium]`.

Risk/impact: relinking current rows would manufacture false test evidence and
could mark alpha-prime specs tested using unrelated widget, ops, health, or
evaluation tests.

Required action: revise A3 to derive the candidate executable identity from
the latest historical row where `tests.id = reassigned_id` and
`tests.spec_id = original_spec_id`, including `test_file`, `test_class`, and
`test_function`. Do not use the latest current row's `test_file` unless it
matches that historical identity and the semantic coverage has been verified.
Each A3 post-impl row must report the source historical version used, nodeid
run, outcome, and whether it was relinked, escalated to C, or escalated to D.

### Finding 2: `last_run_at` will not refresh execution freshness

Severity: medium.

The proposal specifies `db.update_test(..., last_result='pass', last_run_at=...)`.
The actual API/schema field is `last_executed_at`; unrecognized keyword fields
are ignored by `update_test()` because the method only reads known keys from
`**fields`.

Risk/impact: implementation could change `last_result` to `pass` while leaving
the stale execution timestamp intact, weakening the audit trail and lifecycle
event evidence.

Required action: replace `last_run_at` with `last_executed_at` everywhere in
the implementation plan and post-implementation verification. The post-impl
report should sample or summarize new test versions proving both
`last_result='pass'` and fresh `last_executed_at`.

### Finding 3: A1 needs explicit file/class-level handling and mixed-outcome rules

Severity: medium.

The A1 method assumes every stale row has a function-level pytest nodeid
(`bridge/por-step16c-stream-a-alpha-refresh-001.md:36` through `:44`). In the
current DB, 12 A1 stale rows have no `test_function`. Some are class-level rows
and others are file-level aggregate rows. Two specs also have multiple stale
rows, including `SPEC-1613` with eight current stale rows.

Risk/impact: a script that only constructs `test_file::test_function` nodeids
will either skip those rows accidentally or fail to prove their outcome. A
single per-spec bucket also becomes ambiguous when a multi-row spec has mixed
pass/fail/skip outcomes.

Required action: define nodeid construction for function-level, class-level,
and file-level rows. Define per-spec precedence for mixed outcomes, and include
per-test-row outcomes in the post-impl report for any spec with more than one
current stale row.

## Required Action Items

1. Revise A3 so relink candidates are built from the historical row tied to
   the original spec, not from the current reassigned row.
2. Use `last_executed_at`, not `last_run_at`, in all DB updates and evidence
   freshness checks.
3. Add explicit A1 handling for missing `test_function` rows and multi-row
   mixed outcomes.
4. Keep the existing reconciliation invariant: all 151 alpha-prime specs must
   receive terminal bucket assignments, and the post-impl report must list the
   exact 114 A1 and 37 A3 spec IDs.

## Decision Needed From Owner

None. This is a proposal correction request for Prime before Stream A can
proceed.
