# Proposal Review: POR Step 16.C Stream A Alpha-Prime Refresh Revision 3

Verdict: GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-16
Input:
- `bridge/INDEX.md` entry `por-step16c-stream-a-alpha-refresh`
- `bridge/por-step16c-stream-a-alpha-refresh-001.md`
- `bridge/por-step16c-stream-a-alpha-refresh-002.md`
- `bridge/por-step16c-stream-a-alpha-refresh-003.md`
- `bridge/por-step16c-stream-a-alpha-refresh-004.md`
- `bridge/por-step16c-stream-a-alpha-refresh-005.md`
- `bridge/por-step16c-stream-a-alpha-refresh-006.md`
- `bridge/por-step16c-stream-a-alpha-refresh-007.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/deliberation-protocol.md`
- `bridge/por-step16c-implemented-untested-remediation-002.md`
- `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json`
- `independent-progress-assessments/spec-hygiene/scripts/classify_16b_candidates.py`
- `groundtruth.db` opened read-only for evidence queries
- `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py`

## Claim

Revision 3 closes the blockers from the -006 NO-GO. The proposal now keeps
skipped tests stale instead of writing non-stale `skip` evidence, adds
per-spec aggregation for the four multi-reassignment A3 specs, and corrects
the expected pipeline event names to `test_executed` for A1 updates and
`test_created` for A3 inserts.

Prime may proceed to implementation under the GO conditions below. The
conditions are implementation constraints, not a request for another proposal
revision.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, I searched current
deliberations before review.

```text
TERM 16.C COUNT 2
  DELIB-0712 | methodology_review | owner_decision_pending | S297 | POR Step 16.B methodology review: Phase 1.5 pattern does not generalize; 5-stream multi-remediation scope for 16.C | bridge/por-step16b-methodology-review-002.md
  DELIB-0713 | owner_conversation | owner_decision | S297 | Owner Decisions: POR 16.C Scope and Stream Configuration | bridge/por-step16b-methodology-review-006.md
TERM alpha-prime COUNT 0
TERM alpha_prime COUNT 0
TERM DELIB-0713 COUNT 0
```

`DELIB-0713` remains the governing owner decision for Step 16.C multi-stream
remediation.

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

The classifier target query removes a spec from the implemented-untested
population only when a current test row has `last_result IS NULL OR
last_result != 'stale'`
(`independent-progress-assessments/spec-hygiene/scripts/classify_16b_candidates.py:86`
through `:100`). Revision 3's skip decision therefore matches the classifier:
skipped rows receive no DB write and remain discoverable
(`bridge/por-step16c-stream-a-alpha-refresh-007.md:32` through `:58`).

Read-only inventory reconciliation matched Revision 3's scope:

```text
alpha 151 a1 114 a3 37 sum 151
a1_stale_rows 122 shape {'class+func': 110, 'class_only': 3, 'file_only': 9} multi {'SPEC-1580': 2, 'SPEC-1613': 8}
a3_reassignment_rows 49 multi {'SPEC-0169': 3, 'SPEC-0609': 4, 'SPEC-1098': 4, 'SPEC-1376': 5}
a3_missing_hist 0 []
a3_missing_required_or_file 0 []
a3_missing_files 0 []
a3_hist_shapes {'class+func': 49} hist_results {'fail': 2, 'pass': 24, None: 19, 'skip': 4}
```

The four multi-reassignment A3 specs in the proposal match the inventory
(`bridge/por-step16c-stream-a-alpha-refresh-007.md:60` through `:105`).
The current DB also has no missing A3 historical rows, required insert
metadata, or historical test files, so the A3 historical-row replacement plan
is executable against the current checkout.

The installed GroundTruth KB API supports the revised event expectations:

- `insert_test()` records `test_created`
  (`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:2300`
  through `:2375`).
- `update_test()` records `test_executed` when `last_result` or
  `last_executed_at` changes
  (`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:2377`
  through `:2450`).
- Revision 3's event criterion now expects those event names
  (`bridge/por-step16c-stream-a-alpha-refresh-007.md:107` through `:129`,
  `:194` through `:215`).

## Findings

### Finding 1: Prior skip disappearance risk is closed

Severity: none.

Revision 3 explicitly says a pytest SKIPPED outcome leaves the DB row stale,
with no `last_result='skip'` write
(`bridge/por-step16c-stream-a-alpha-refresh-007.md:32` through `:58`,
`:137` through `:145`, and `:153` through `:163`). That closes the -006
blocker: skipped specs remain visible to the classifier and must be listed in
the post-implementation report with skip reasons.

Risk/impact: acceptable. Skipped specs do not falsely disappear from the
implemented-untested target population.

Required action: none beyond the GO conditions.

### Finding 2: A3 multi-reassignment aggregation is now reviewable

Severity: none.

Revision 3 names all four known multi-reassignment A3 specs and defines a
single per-spec bucket using deterministic precedence
(`bridge/por-step16c-stream-a-alpha-refresh-007.md:60` through `:105`). This
addresses the -006 concern that 49 reassigned test IDs could otherwise break
the 37-spec A3 reconciliation.

Risk/impact: acceptable, provided implementation reports both per-test
outcomes and the derived per-spec bucket for those four specs.

Required action: none beyond the GO conditions.

### Finding 3: Event-name exit criteria now match the installed API

Severity: none.

Revision 3 corrects the prior impossible `test_updated` expectation. A1
non-skip `update_test()` writes should reconcile to `test_executed` events,
and A3 inserted replacement rows should reconcile to `test_created` events
(`bridge/por-step16c-stream-a-alpha-refresh-007.md:107` through `:129`).
This matches the installed API behavior in `groundtruth_kb/db.py`.

Risk/impact: acceptable.

Required action: none beyond the GO conditions.

## GO Conditions

1. For A3 pytest outcomes, insert replacement rows for `pass`, `fail`, and
   collection-error-as-fail outcomes. Do not interpret the phrase
   "non-skip, non-escalated" at
   `bridge/por-step16c-stream-a-alpha-refresh-007.md:121` or `:161` as
   excluding failing tests that are handed off to Stream C. Only `skip`,
   `broken_path`, and `no_historical` produce no A3 DB write.
2. Normalize collection errors to DB `last_result='fail'` while preserving
   the raw pytest collection-error evidence in the post-implementation report.
   Do not create a new ad hoc `last_result='collection_error'` value unless
   owner approval is obtained.
3. Use the detailed A3 precedence block at
   `bridge/por-step16c-stream-a-alpha-refresh-007.md:76` through `:91` as the
   controlling aggregation rule. If the summary wording at
   `bridge/por-step16c-stream-a-alpha-refresh-007.md:15` is read as a
   different order, the detailed block controls.
4. Post-implementation verification must reconcile both per-spec buckets and
   DB-visible effects:
   - all 151 alpha-prime specs have exactly one terminal bucket;
   - alpha-prime reduction equals the count of specs receiving non-stale
     pass/fail evidence;
   - skipped and broken/no-historical specs remain in alpha-prime and appear
     in the handoff/deferred lists;
   - `pipeline_events` delta equals A1 `test_executed` events plus A3
     `test_created` events for rows actually written.

## Required Action Items

Prime may proceed with `independent-progress-assessments/spec-hygiene/scripts/stream_a_alpha_refresh.py`
and the controlled `groundtruth.db` mutation described in Revision 3, subject
to the GO conditions above.

## Decision Needed From Owner

None.
