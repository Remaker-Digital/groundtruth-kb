# Proposal Review: POR Step 16.C Stream B Zeta-Prime Triage

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-16
Input:
- `bridge/por-step16c-stream-b-zeta-triage-001.md`
- `bridge/INDEX.md` entry `por-step16c-stream-b-zeta-triage`
- `.claude/rules/file-bridge-protocol.md`
- `bridge/por-step16c-implemented-untested-remediation-002.md`
- `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json`
- `groundtruth.db` opened read-only for spec/test history queries
- Target test files named in the proposal

## Claim

The proposal is directionally correct for `SPEC-1869`, `SPEC-1870`, and
`SPEC-1871`, but it is not safe as written because `SPEC-1841` is not a simple
test-id reassignment case. The historical tests for `SPEC-1841` cover the old
"Untested Spec Backfill Program" meaning of that ID, while the current latest
`SPEC-1841` requirement is the deployment modal pre-fill requirement.

Relinking `tests/quality_metrics/test_backfill_untested.py` rows to current
`SPEC-1841` would create false coverage for an unrelated deployment UI
requirement.

## Evidence Verified

The umbrella GO authorizes this stream as the four-spec zeta-prime remediation
stream:
- `bridge/por-step16c-implemented-untested-remediation-002.md` records Stream B
  as the four zeta-prime specs and requires terminal decisions for the 193-spec
  reconciliation.

The proposal's own table identifies the mismatch risk for `SPEC-1841`:
- `bridge/por-step16c-stream-b-zeta-triage-001.md:25` maps current
  `SPEC-1841` "Deployment modal should pre-fill next version" to
  `tests/quality_metrics/test_backfill_untested.py`.
- `bridge/por-step16c-stream-b-zeta-triage-001.md:41` through `:43` propose
  creating new test rows with `spec_id=S.id` when the code covers `S`.

The inventory confirms the four zeta-prime targets and reassignment owners:
- `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json:5147`
  through `:5174` show `SPEC-1841`, title "Deployment modal SHOULD pre-fill...",
  historical file `tests/quality_metrics/test_backfill_untested.py`, and
  reassignment to `SPEC-1771`.
- `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json:5346`
  through `:5397` show `SPEC-1869` with seven reassignments to `SPEC-1874`.
- `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json:5403`
  through `:5442` show `SPEC-1870` with four reassignments to `SPEC-1874`.
- `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json:5448`
  through `:5499` show `SPEC-1871` with seven reassignments to `SPEC-1874`.

The test code supports the three Track B specs but not current `SPEC-1841`:
- `tests/quality_metrics/test_backfill_untested.py:1` says the module tests
  `SPEC-1841: Untested Spec Backfill Program`.
- `tests/quality_metrics/test_backfill_untested.py:22` scopes the class to
  `SPEC-1841: Risk tier classification`.
- `tests/chat/pipeline/test_intent_router.py:542` and `:547` scope the intent
  threshold tests to `SPEC-1869`.
- `tests/chat/test_source_attribution.py:1` and `:16` scope source attribution
  tests to `SPEC-1870`.
- `tests/multi_tenant/test_tone_presets.py:1` and `:36` scope tone preset tests
  to `SPEC-1871`.

Read-only SQLite inspection of `groundtruth.db` showed:
- `SPEC-1841` versions 1-3 were "Untested Spec Backfill Program"; versions 4-5
  are "Deployment modal SHOULD pre-fill recommended next version and show last
  deployed version".
- `TEST-10612` through `TEST-10621` version 1 rows pointed at the old
  backfill-file tests for `SPEC-1841`, while latest version 3 rows now point at
  `SPEC-1771` admin integration API tests.
- `TEST-11003` through `TEST-11020` had version 2 rows that correctly linked
  the Track B executable tests to `SPEC-1869`, `SPEC-1870`, or `SPEC-1871`, and
  latest version 3 rows now point at `SPEC-1874`.

Focused verification command:

```text
python -m pytest tests/quality_metrics/test_backfill_untested.py tests/chat/pipeline/test_intent_router.py tests/chat/test_source_attribution.py tests/multi_tenant/test_tone_presets.py -q --tb=short
```

Result:

```text
57 passed in 1.76s
```

## Findings

### Finding 1: `SPEC-1841` would be falsely covered by the proposed default relink

Severity: high.

The current latest `SPEC-1841` requirement is the deployment modal pre-fill
requirement. The historical test file names and exercises an untested-spec
backfill/risk-tier classifier instead. Those tests are executable and passing,
but they do not verify the current deployment modal behavior.

Risk/impact: relinking the ten backfill tests to current `SPEC-1841` would
convert a real uncovered deployment requirement into an apparently tested one,
undermining the Step 16.C reconciliation.

Required action: revise the proposal so `SPEC-1841` is not relinked to
`tests/quality_metrics/test_backfill_untested.py` unless Mike explicitly
decides the spec identity should be repaired back to the old backfill-program
meaning. Otherwise, `SPEC-1841` needs actual deployment-modal test evidence, a
new-test/WI terminal bucket, or an owner decision about spec identity repair.

### Finding 2: The triage taxonomy is missing a required terminal branch

Severity: medium.

The proposal has branches for "test covers S", "test covers now_owned_by", and
"ambiguous". `SPEC-1841` demonstrates a fourth concrete case: the historical
test covers neither the current latest spec nor the current owner. It covers a
superseded meaning of the same spec ID.

Risk/impact: without this branch, the implementation script can force a bad
choice between relink and retire, or hide the case under generic ambiguity.

Required action: add an explicit terminal outcome for "historical test covers a
superseded spec meaning / current spec still needs test evidence." Acceptable
terminal handling should be one of:
- create or locate real deployment-modal test evidence for `SPEC-1841`;
- create a follow-up WI for a missing test and reconcile it as not relinked;
- ask Mike for a spec-identity decision if Prime believes the `SPEC-1841`
  version history itself must be repaired.

### Finding 3: `SPEC-1869`, `SPEC-1870`, and `SPEC-1871` are suitable relink candidates

Severity: none, conditional.

The target files and test functions for these three specs still match the
latest spec titles and descriptions, and the focused pytest command passed.
Their current test IDs were later reused for `SPEC-1874`, so the proposal is
right to create new rows rather than mutate the current `TEST-11003` through
`TEST-11020` rows.

Risk/impact: low if fresh test IDs are used. Medium if the implementation
updates current rows in place, because that would steal legitimate
`SPEC-1874` rows.

Required action: the revised proposal should explicitly require fresh test IDs
for relinked evidence and should preserve the currently owned `SPEC-1874` test
rows.

## Required Action Items

1. Revise the Stream B method to prohibit automatic relink of
   `tests/quality_metrics/test_backfill_untested.py` to current `SPEC-1841`.
2. Add the missing "covers neither current spec nor now-owned-by" terminal
   branch and include it in the exit criteria.
3. Keep `SPEC-1869`, `SPEC-1870`, and `SPEC-1871` on the relink path, but
   require fresh test IDs and no mutation of current `SPEC-1874` rows.
4. In the post-implementation report, include before/after DB evidence showing
   per-spec terminal outcomes and test-row IDs created or intentionally not
   created.

## Decision Needed From Owner

None for this NO-GO. A Mike decision becomes necessary only if Prime wants to
repair the `SPEC-1841` identity/version history rather than treat current
`SPEC-1841` as a deployment-modal requirement needing real test evidence.
