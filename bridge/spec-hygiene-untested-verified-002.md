NO-GO

# Review: Spec Hygiene Verified-but-Untested Subset

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input: `bridge/spec-hygiene-untested-verified-001.md`
Companion report: `independent-progress-assessments/spec-hygiene/S291-untested-verified-specs.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`

## Claim

The proposal is not safe to implement as drafted. The high-level problem is
real: there are currently verified specs with zero linked current test artifacts.
But the proposed remediation rests on two incorrect premises:

1. `specifications.authority` is available for evidence pointers.
2. The 19 non-governance verified specs have no test references anywhere in the
   KB.

Both are false under direct inspection.

## Prior Deliberations

No prior deliberations found for `untested verified specs`, `spec hygiene`,
`GOV-08 spec authority`, `SPA Control Plane verification`,
`authority field convention`, or `verified-but-untested`.

Read-only deliberation archive query result:

```text
TERM untested verified specs matches 0
TERM spec hygiene matches 0
TERM GOV-08 spec authority matches 0
TERM SPA Control Plane verification matches 0
TERM authority field convention matches 0
TERM verified-but-untested matches 0
```

## Evidence

- The proposal says 118 specs have zero rows in `tests` by `spec_id`, 22 are
  verified, and 19 have no test references anywhere in the tests table at
  `bridge/spec-hygiene-untested-verified-001.md:22` through
  `bridge/spec-hygiene-untested-verified-001.md:24`.
- The companion report classifies those 19 as "Wrongly promoted (no test
  references anywhere in KB)" at
  `independent-progress-assessments/spec-hygiene/S291-untested-verified-specs.md:28`.
- The proposal's key decision would store file paths, URLs, document refs,
  assertion refs, or UAT log refs in `specifications.authority` at
  `bridge/spec-hygiene-untested-verified-001.md:37` through
  `bridge/spec-hygiene-untested-verified-001.md:49`.
- GroundTruth KB defines `authority` as the spec provenance enum
  `stated`, `inferred`, `provisional`, `inherited`, or `unknown` at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:509`.
  It validates that enum at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:531`
  through
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:534`.
- GroundTruth KB user docs describe `authority` as provenance:
  `stated`, `inferred`, and `provisional` at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\docs\user-journey.md:163`.
- The session-start untested-spec report checks only `current_specifications`
  and `current_tests`; it has no `authority` exception at
  `.claude/hooks/assertion-check.py:384` through
  `.claude/hooks/assertion-check.py:400`.
- Agent Red governance says Tests verify Specifications at `CLAUDE.md:82`,
  and GOV-08 keeps project knowledge in the KB at `CLAUDE.md:101`.

## Direct Database Checks

All database checks were read-only against `groundtruth.db`.

The verified-but-zero-current-test slice is real:

```text
ZERO_LINKED_ANY_CURRENT_TEST_VERIFIED_INCLUDE_GOV
22 ['GOV-14', 'GOV-15', 'GOV-16', 'SPEC-0439', 'SPEC-0604',
'SPEC-0661', 'SPEC-0811', 'SPEC-1076', 'SPEC-1078', 'SPEC-1097',
'SPEC-1138', 'SPEC-1165', 'SPEC-1816', 'SPEC-1818', 'SPEC-1819',
'SPEC-1820', 'SPEC-1821', 'SPEC-1822', 'SPEC-1823', 'SPEC-1824',
'SPEC-1826', 'SPEC-1827']
```

But the 19 non-governance specs are not "no test references anywhere." They
have 53 historical linked test rows and zero current linked test rows:

```text
historical_linked_total 53
current_linked_total 0
```

Representative examples:

```text
TEST-1482
v2 spec_id='SPEC-0439' last_result='pass'
v3 spec_id='' last_result='stale'

TEST-1681
v2 spec_id='SPEC-1165' last_result='pass'
v4 spec_id='' last_result='stale'

TEST-10481
v1 spec_id='SPEC-1816' last_result='pass'
v2 spec_id='SPEC-1837' last_result='pass'
```

For the SPA cluster, latest rows show apparent test-ID reuse or reassignment:

```text
SPEC-1816 hist_ids 3 latest_sample TEST-10481->'SPEC-1837'/pass; TEST-10482->'SPEC-1837'/pass; TEST-10483->'SPEC-1837'/pass
SPEC-1818 hist_ids 2 latest_sample TEST-10484->'SPEC-1837'/pass; TEST-10485->'SPEC-1837'/pass
SPEC-1827 hist_ids 2 latest_sample TEST-10505->'SPEC-1837'/pass; TEST-10506->'SPEC-1837'/pass
```

The three governance specs do have passing assertion-run history:

```text
GOV-14 total=79 passed=79 latest=2026-04-06T20:31:02+00:00
GOV-15 total=79 passed=79 latest=2026-04-06T20:31:02+00:00
GOV-16 total=79 passed=79 latest=2026-04-06T20:31:02+00:00
```

The proposed `authority` values would fail current API validation:

```text
python -c "from groundtruth_kb.db import _validate_authority; _validate_authority('tests/foo.py:1-10')"
ValueError: Invalid authority: 'tests/foo.py:1-10'. Must be one of ['inferred', 'inherited', 'provisional', 'stated', 'unknown']
```

`memory/MEMORY.md` is not present in this checkout:

```text
Test-Path memory/MEMORY.md
False
```

Current work-item origins do not include `governance`:

```text
new 1273
defect 567
hygiene 9
regression 8
improvement 2
```

GroundTruth KB's API docstring lists valid work-item origins as
`regression`, `defect`, `new`, or `hygiene` at
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:2842`.

## Findings

### Finding 1 - Proposed `authority` convention conflicts with schema semantics

Severity: Blocker

`specifications.authority` is not an open evidence-reference field. It is a
validated provenance enum used by GroundTruth KB reconciliation and impact
logic. The proposed values such as `apps/...:1-120`,
`https://github.com/...@sha#L1-L120`, `DOC-141#section-3`, or
`assertion:GOV-14...` will fail through the API and would corrupt semantics if
written by direct SQL.

Risk/impact:

- Implementation via `KnowledgeDB.update_spec()` fails immediately.
- Direct SQL would poison authority-conflict and provisional-expiration logic.
- The owner would lose the F1 provenance semantics before the field has even
  been populated in Agent Red.

Required action:

- Do not overload `specifications.authority`.
- Use existing Test artifacts where evidence is executable or inspectable.
- If off-KB evidence needs first-class representation, submit a separate schema
  proposal for a distinct field/table such as `verification_evidence`,
  `evidence_ref`, or a document/test linkage model, including validation,
  CLI/API support, and assertion-hook semantics.

### Finding 2 - Classification ignores historical linked tests and misses likely test-artifact corruption

Severity: Blocker

The proposal says the 19 non-governance specs have no test references anywhere
in the tests table. Read-only DB checks found 53 historical linked test rows for
those specs. The reason they are "untested" in current-state queries is that
the latest version of those test IDs no longer points at those specs. Some are
blank/stale; SPA-cluster examples have been reassigned to `SPEC-1837`.

Risk/impact:

- Reverting specs or adding evidence annotations treats the symptom, not the
  root cause.
- It can destroy useful audit history about existing or formerly existing tests.
- It can hide a more serious KB integrity issue: test artifact IDs appear to
  have been reused or overwritten across unrelated specs.

Required action:

- Redo the classification with both `current_tests` and full `tests` history.
- Produce a per-spec table with historical test IDs, latest current test row,
  current `spec_id`, `last_result`, `test_file`, and `test_function`.
- Investigate how `TEST-10481` through related SPA IDs became current tests for
  `SPEC-1837`, and how older backend/widget test IDs became blank/stale.
- Choose remediation per spec after that audit: restore/link valid Test
  artifacts, create new Test artifacts, create WIs for missing tests, or only
  then downgrade status if no valid evidence exists.

### Finding 3 - Proposed verification condition will not satisfy the current session-start hook

Severity: High

The proposal's verification condition says no verified spec should remain with
both zero tests and empty `authority`. The current hook does not implement that
rule. It reports implemented/verified specs that lack non-stale `current_tests`
and does not check `authority`.

Risk/impact:

- Prime could implement the proposal and still leave the session-start hygiene
  report red.
- The bridge could mark a metadata workaround as verified while the active
  automation still treats the specs as untested.

Required action:

- Either keep `current_tests` as the authoritative coverage mechanism for this
  remediation, or include an explicit hook/gate update in a separate reviewed
  proposal after the evidence model is approved.

### Finding 4 - `origin=governance` is not an established work-item origin

Severity: Medium

The proposal uses or considers `origin=governance` for new WIs, but the current
KB contains `new`, `defect`, `hygiene`, `regression`, and `improvement`, and the
GroundTruth KB API docstring lists `regression`, `defect`, `new`, or `hygiene`.

Risk/impact:

- New work items could bypass expectations tied to the existing origin taxonomy.
- Reporting and backlog summaries would get a new category without an explicit
  taxonomy decision.

Required action:

- Use `hygiene` for KB metadata cleanup WIs unless the owner approves a separate
  origin-taxonomy migration.
- Use `defect` only when a specific product behavior or verification artifact is
  proven wrong, not for the general hygiene backlog.

### Finding 5 - `memory/MEMORY.md` is not a valid repo path

Severity: Medium

The proposal and companion report require updating `memory/MEMORY.md`, but that
path does not exist in this checkout.

Risk/impact:

- Implementation can either fail or modify an off-repo Claude memory location
  that is not covered by this bridge proposal.

Required action:

- Identify the actual memory artifact path before including it in scope, or
  remove MEMORY.md editing from this bridge item.

## Required Revision

Submit a revised proposal that:

1. Drops the `authority` evidence-pointer convention, or replaces it with a
   separate reviewed schema/evidence model.
2. Reclassifies the 22 specs using both current and historical test rows.
3. Treats apparent test-ID reuse/reassignment as a first-class KB integrity
   issue.
4. Keeps the session-start hook and verification condition aligned.
5. Uses valid work-item origins.
6. Names a real memory path, or removes that edit from scope.

## Decision Needed From Owner

Owner decision is only needed if Prime wants to introduce a new evidence field,
new evidence table, or new work-item origin. No owner decision is needed to
revise this proposal around existing Test artifacts and the current origin
taxonomy.
