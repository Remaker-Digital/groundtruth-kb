# Proposal Review: POR Step 16.C Implemented-Untested Remediation

Verdict: GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-16
Input:
- `bridge/por-step16c-implemented-untested-remediation-001.md`
- `bridge/INDEX.md` entry `por-step16c-implemented-untested-remediation`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/deliberation-protocol.md`
- `bridge/por-step16b-methodology-review-006.md`
- `bridge/por-step16a-verified-spec-closure-010.md`
- `bridge/spec-hygiene-untested-verified-008.md`
- `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json`
- `independent-progress-assessments/spec-hygiene/S297-phase16b-methodology-review.md`
- `independent-progress-assessments/spec-hygiene/scripts/classify_16b_candidates.py`
- `docs/plans/PLAN-OF-RECORD-production-readiness.md`
- `groundtruth.db` opened read-only for deliberation/evidence queries

## Claim

Prime's umbrella proposal is approved as the coordination wrapper for POR Step
16.C, subject to the downstream conditions below.

The proposal's scope and counts are anchored in the VERIFIED Step 16.B
methodology result, owner decision `DELIB-0713`, and the generated 16.B target
inventory. The four-stream structure correctly reflects the owner-approved
change from five streams to four: `delta_prime` is folded into Stream D rather
than treated as assertion-only verified evidence.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, I searched current
deliberations before review.

Relevant read-only DB results:

```text
TERM 16.C COUNT 2
  DELIB-0712 | methodology_review | owner_decision_pending | S297 | POR Step 16.B methodology review: Phase 1.5 pattern does not generalize; 5-stream multi-remediation scope for 16.C | bridge/por-step16b-methodology-review-002.md
  DELIB-0713 | owner_conversation | owner_decision | S297 | Owner Decisions: POR 16.C Scope and Stream Configuration | bridge/por-step16b-methodology-review-006.md

TERM DELIB-0713 COUNT 1
  DELIB-0713 | owner_conversation | owner_decision | S297 | Owner Decisions: POR 16.C Scope and Stream Configuration | bridge/por-step16b-methodology-review-006.md
```

`DELIB-0713` records three owner decisions: accept Option B multi-stream
remediation, reject assertion-only verification for the 15 `delta_prime` specs
and roll them into Stream D, and run Streams A/B/C/D in parallel.

## Evidence Verified

The safe classifier check still reproduces the Step 16.B counts without
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

The same counts are present in the generated inventory:
- `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json:7`
  reports `target_count: 193`.
- `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json:8`
  through `:13` report category counts `151/4/15/19/4`.
- `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json:23`
  through `:25` report reassignment split `alpha_prime: 37`,
  `zeta_prime: 4`.
- `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json:34`
  reports `db_mutated: false`.

Independent JSON reconciliation matched the proposal's stream totals:

```text
items_count 193
summary_target_count 193
summary_category_counts {'alpha_prime': 151, 'beta_prime': 4, 'delta_prime': 15, 'gamma_prime': 19, 'zeta_prime': 4}
computed_category_counts {'alpha_prime': 151, 'beta_prime': 4, 'delta_prime': 15, 'gamma_prime': 19, 'zeta_prime': 4}
stream_d_count 34
alpha_existing_files_all True
beta_all_missing True
zeta_count_reassign 4
```

Step 16.B was already verified as the governing methodology source:
- `bridge/por-step16b-methodology-review-006.md:3` records `Verdict:
  VERIFIED`.
- `bridge/por-step16b-methodology-review-006.md:29` through `:30` state that
  the 193 requirements are exhaustively partitioned and Option B remains the
  supported 16.C recommendation.
- `bridge/por-step16b-methodology-review-006.md:44` through `:52` reproduce
  the target count, category counts, reassignment counts, and DB hash check.

The umbrella proposal correctly captures the owner-approved stream mapping:
- `bridge/por-step16c-implemented-untested-remediation-001.md:37` through
  `:44` map `alpha_prime`, `beta_prime`, `gamma_prime`, `delta_prime`, and
  `zeta_prime` to Streams A/C/D/D/B, with Stream D totaling 34 specs.
- `bridge/por-step16c-implemented-untested-remediation-001.md:116` through
  `:126` require all four sub-streams to be VERIFIED and reconciled.
- `bridge/por-step16c-implemented-untested-remediation-001.md:132` through
  `:140` require final count reconciliation and coverage of all 193 original
  specs.
- `bridge/por-step16c-implemented-untested-remediation-001.md:142` through
  `:154` define the sub-stream bridge and umbrella update flow.

Current POR tracking still leaves 16.B/16.C open, so this proposal is aligned
with the repo-visible plan state:
- `docs/plans/PLAN-OF-RECORD-production-readiness.md:197` lists the Phase 16.B
  methodology review as still pending in the plan text.
- `docs/plans/PLAN-OF-RECORD-production-readiness.md:201` through `:202` list
  Phase 16.B and 16.C as follow-on phases.

## Findings

### Finding 1: Stream structure and counts reconcile

Severity: none.

The four-stream umbrella is consistent with the verified classifier output and
`DELIB-0713`: Stream A covers 151 `alpha_prime`; Stream B covers 4
`zeta_prime`; Stream C covers 4 `beta_prime`; Stream D covers 19
`gamma_prime` plus 15 `delta_prime`, for 34 total.

Risk/impact: low. The umbrella is a coordination artifact; each sub-stream
still gets its own GO/VERIFY cycle.

Required action: none beyond the conditions below.

### Finding 2: Stream A must not assume all alpha-prime specs have current stale rows

Severity: medium if missed downstream; non-blocking for umbrella GO.

The umbrella says Stream A should re-run tests and "update the test row's
`last_result` from `stale` to `pass`" (`bridge/por-step16c-implemented-untested-remediation-001.md:52`
through `:56`). That is directionally right, but the alpha-prime population is
not uniform at the current-row level.

Independent inventory analysis found:

```text
alpha_prime 151
current_test_rows total 122
current_stale_rows total 122
specs current_test_rows>0 114
specs current_stale_rows>0 114
hist_rows total 307
hist_files total per spec 159
reassign specs 37
examples hist no current stale: SPEC-0159, SPEC-0169, SPEC-0212, SPEC-0231, SPEC-0256
```

This matches the inventory's reassignment signal:
`independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json:23`
through `:25` show 37 `alpha_prime` specs with reassignment signals.

Risk/impact: a blind implementation that only updates current stale rows would
leave some alpha-prime specs unresolved or could mutate the wrong historical
row shape.

Required action: the Stream A proposal must split or explicitly handle
alpha-prime subcases:
- specs with current stale rows that can be refreshed by rerunning linked
  tests and writing new passing evidence;
- specs with historical file-backed evidence but no current stale row;
- alpha-prime specs with reassignment signals.

For each subcase, the Stream A post-implementation report must reconcile the
151-spec population into refreshed, escalated-to-C, retired, or otherwise
terminally explained buckets.

### Finding 3: Verification gates are strong enough if sub-streams preserve exact spec lists

Severity: low.

The proposal's umbrella exit criteria are adequate, but they rely on each
sub-stream carrying exact spec IDs from the classifier inventory. Without exact
lists, reconciliation could pass by aggregate count while missing an individual
spec.

Risk/impact: low to medium. Aggregate-only reporting would weaken the audit
trail that Step 16 is meant to repair.

Required action: each sub-stream proposal and post-implementation report must
include or cite its exact spec-id set from
`S297-phase16b-target-inventory.json`, plus any moved/escalated IDs.

## GO Conditions

1. Sub-stream proposals may proceed under the four-stream structure defined in
   this umbrella.
2. Stream A must address the alpha-prime subcase risk called out in Finding 2.
3. Stream D must create exactly 34 hygiene WIs, one per `gamma_prime` or
   `delta_prime` spec, with `origin=hygiene` and a durable source-spec link.
4. No sub-stream may claim umbrella completion until all four sub-streams are
   VERIFIED and the umbrella post-implementation report reconciles all 193
   original spec IDs.
5. The umbrella post-implementation report must cite the final DELIB archive
   entry and the POR update marking Phase 16.C complete.

## Required Action Items

Prime may proceed to the sub-stream bridge proposals. The first downstream
proposal that needs extra scrutiny is Stream A, because its remediation method
must distinguish current stale rows from historical-only/reassigned alpha-prime
evidence.

## Decision Needed From Owner

None for this umbrella GO. Owner decisions required for 16.C scope are already
archived in `DELIB-0713`.
