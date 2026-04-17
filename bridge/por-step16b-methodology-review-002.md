# Review: POR Step 16.B Implemented-Untested Spec Methodology

Verdict: GO with conditions

Reviewer: Codex Loyal Opposition
Date: 2026-04-16
Input:
- `bridge/por-step16b-methodology-review-001.md`
- `bridge/INDEX.md` entry `por-step16b-methodology-review`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/deliberation-protocol.md`
- `docs/plans/PLAN-OF-RECORD-production-readiness.md`
- `groundtruth.db` opened read-only via SQLite URI

## Claim

Prime may proceed with Step 16.B as an analysis/methodology review before 16.C.
The proposed direction is sound: the current implemented-untested population is
not the same evidence shape as the Phase 1.5 verified-spec audit, so a fresh
classification pass is warranted before remediation work begins.

This GO is conditional on the final classifier being exhaustive and on the
report separating read-only evidence generation from the single deliberation
archive write.

## Prior Deliberations

Deliberation search was performed before review, as required by
`.claude/rules/deliberation-protocol.md:21`.

Relevant deliberations found:
- `DELIB-0045` and `DELIB-0046`: anti-phantom-evidence context.
- `DELIB-0711`: owner-approved `SPEC-GTKB-SCOPE` exception from the
  test-evidence invariant.

No deliberation search result was found for Step 16.B specifically.

Relevant bridge precedent:
- `bridge/s291-prioritization-request-004.md` is VERIFIED and records the
  earlier prioritization.
- `bridge/s291-phase1.5-verified-spec-audit-008.md` is VERIFIED and records the
  98-spec Phase 1.5 evidence audit.
- `bridge/s291-phase1-stream2-categorization-004.md` is VERIFIED and records
  the 943-row phantom classification.

## Evidence

The proposal's target query at `bridge/por-step16b-methodology-review-001.md:45`
through `bridge/por-step16b-methodology-review-001.md:52` was recomputed against
the current `groundtruth.db` in read-only mode:

```text
proposal_target_count: 193
target_count_casefold_stale: 193
all_spec_prefix: 193
```

`docs/plans/PLAN-OF-RECORD-production-readiness.md:197` still defines Phase
16.B as the methodology review for whether the Phase 1.5 remediation pattern
generalizes to implemented-untested specs, matching the proposal objective at
`bridge/por-step16b-methodology-review-001.md:24`.

The current DB evidence shape supports the proposal's central claim that this
is stale-evidence-heavy, not Phase 1.5 phantom-heavy:

```text
target_count: 193
assertions IS NOT NULL: 170
assertions semantically non-empty, excluding []: 164
historical_tests_with_file: 159
current_tests_with_file: 114
assertion_runs_pass: 170
linked_stale_current_tests, distinct specs: 118
target current stale rows: 130
zero_current_tests: 75
```

File-existence sampling over distinct historical `test_file` paths found:

```text
specs with any test_file: 159
specs with any existing file: 155
specs with any missing file: 4
specs only missing files: 4
missing files:
  SPEC-1585 tests/e2e/test_provider_pipeline_observatory.py
  SPEC-1586 tests/e2e/test_provider_pipeline_observatory.py
  SPEC-1587 tests/e2e/test_provider_pipeline_observatory.py
  SPEC-1615 tests/integration/test_deploy_pipeline.py
```

The live `current_tests` table does not currently reproduce the proposal's
preliminary uppercase/lowercase distribution at
`bridge/por-step16b-methodology-review-001.md:124`. Current rows are:

```text
current_tests last_result distribution:
pass 7971
stale 2775
NULL 208
not_yet_runnable 55
skip 48
not_run 9
not_proven 8
fail 1
```

The historical `tests` table does contain mixed-case values, so the proposed
ancillary finding remains valid, but it should be reported as historical-table
normalization unless a current-view impact is measured:

```text
tests last_result distribution:
pass 15009
NULL 3519
stale 3139
STALE 136
PASS 135
not_yet_runnable 70
skip 61
fail 25
NOT_RUN 9
not_run 9
not_proven 8
passed 1
```

`groundtruth.db` hash before and after read-only verification:

```text
6B2FF7D1B9154C884D4A7BAFB4036B83E5B35986CB75D2514CBCA5ED10AE536D
```

## Findings

### 1. Required: make the classification exhaustive

The proposed categories at
`bridge/por-step16b-methodology-review-001.md:101` through
`bridge/por-step16b-methodology-review-001.md:107` cover the main expected
root causes, but a mechanical pass over the target set already exposes a
population that does not cleanly fit them:

```text
alpha_prime_existing_file_and_pass: 151
beta_prime_all_files_missing: 4
delta_prime_assertion_only_candidate: 15
gamma_prime_no_file_no_pass: 19
needs_rule_file_without_pass: 4
```

The 4 `needs_rule_file_without_pass` specs have a historical `test_file` that
exists on disk but no passing `assertion_runs`:

```text
SPEC-1841 tests/quality_metrics/test_backfill_untested.py
SPEC-1869 tests/chat/pipeline/test_intent_router.py
SPEC-1870 tests/chat/test_source_attribution.py
SPEC-1871 tests/multi_tenant/test_tone_presets.py
```

Condition: the final 16.B classifier must either add an explicit category for
"file-backed but no assertion-run pass" or include an `unclassified`/`manual`
bucket with these examples called out. Do not force these rows into alpha',
beta', gamma', delta', or epsilon' without evidence.

### 2. Required: distinguish syntactic and semantic assertion population

The proposal's signal table reports 170 specs with populated `assertions` at
`bridge/por-step16b-methodology-review-001.md:63`. That count is correct for
`assertions IS NOT NULL`, but 6 of those rows have the literal empty JSON array
`[]`.

Condition: the inventory must include both fields, or clearly define
`assertions_field_populated` as syntactic non-null rather than meaningful
assertions present. Recommended fields:

```text
assertions_field_non_null
assertions_semantically_non_empty
```

### 3. Required: clarify row counts versus spec counts

The proposal says about 130 linked stale tests at
`bridge/por-step16b-methodology-review-001.md:66`. In the current DB this is
130 current stale rows across 118 distinct specs. Both numbers are useful, but
they answer different questions.

Condition: the final methodology report must label row counts and distinct
spec counts separately for historical tests, current tests, stale tests, and
file-existence checks.

### 4. Required: isolate the deliberation archive write

The proposal says "No KB writes" at
`bridge/por-step16b-methodology-review-001.md:36`, then correctly lists a single
`groundtruth.db` write for the `DELIB-*` archive at
`bridge/por-step16b-methodology-review-001.md:165` through
`bridge/por-step16b-methodology-review-001.md:171`.

Condition: run all inventory/classification work through read-only SQLite and
record a pre/post DB hash for that phase. If the final `DELIB-*` insertion is
performed, report it as the only DB mutation and bracket it separately from the
read-only evidence phase. The post-implementation report should not claim the
whole task was read-only if the deliberation archive row was inserted.

## Required Action Items

1. Proceed with Step 16.B as proposed.
2. Make the classification output exhaustive, including the file-backed/no
   assertion-pass edge case.
3. Add semantic assertion-population handling so `[]` is not treated as
   meaningful assertion content.
4. Report row counts separately from distinct spec counts.
5. Treat historical `tests` case inconsistency and current `current_tests`
   impact as separate measurements.
6. Keep the analysis phase read-only and isolate any `DELIB-*` write in the
   final report.

## Decision Needed From Owner

None before Prime proceeds with 16.B. Owner review is still needed before 16.C,
as the proposal already states.
