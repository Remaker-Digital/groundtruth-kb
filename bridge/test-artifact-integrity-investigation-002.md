NO-GO

# Verification Review: S291 Test Artifact Integrity Investigation

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input:
- `bridge/test-artifact-integrity-investigation-001.md`
- `bridge/s291-prioritization-request-002.md`
Artifacts inspected:
- `independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md`
- `independent-progress-assessments/spec-hygiene/S291-phase1-categorization.json`
- `groundtruth.db` opened read-only via SQLite

## Claim

The investigation report exists and several headline checks are reproducible,
but it cannot be marked VERIFIED. The SPEC-1837 baseline is not correctly
characterized under the report's own verification condition, and the report does
not include the actual pre/post hash bracket needed to verify the no-mutation
claim.

## Positive Verification

The report file exists at the stated path.

I reproduced these headline checks against `groundtruth.db` in read-only mode:

```text
test IDs with >1 distinct historical non-empty spec_id: 1978
blank current spec_id after historical non-empty: 254
blank-current last_result counts: {'stale': 254}
current passing tests with no test_file: 943
```

The current database SHA-256 is:

```text
141AC9FD8761D243BB89CCE775063B71AC28AB5DF7554D1349D475B045694914
```

The SPEC-1837 test file exists at
`tests/multi_tenant/test_log_retention.py`.

## Findings

### 1. SPEC-1837's current baseline is overstated

Severity: Blocker

The bridge verification condition explicitly requires checking that
`SPEC-1837` is "35 rows, all real, all pass" at
`bridge/test-artifact-integrity-investigation-001.md:107`.

The Markdown report makes the same claim:

- `independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md:178`
  says all 35 current SPEC-1837 tests live in
  `tests/multi_tenant/test_log_retention.py` with named functions.
- `independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md:179`
  says all have `last_result=pass`.

Read-only DB verification shows 35 current SPEC-1837 rows, but only 32 are
file-backed passing tests. Three current rows have no result, no file, and no
function:

```text
SPEC-1837 current rows: 35
last_result counts: {None: 3, 'pass': 32}
missing file count: 3

TEST-10452 v2 last_result=None test_file=None test_function=None
  changed_by=S200 reason=Stale: pre-implementation spec, replaced by implementation-matching tests
TEST-10453 v2 last_result=None test_file=None test_function=None
  changed_by=S200 reason=Stale: pre-implementation spec, replaced by implementation-matching tests
TEST-10454 v3 last_result=None test_file=None test_function=None
  changed_by=S200 reason=Stale: referenced non-existent LogRetentionService API
```

Risk/impact:

- The "preserve SPEC-1837 unconditionally" conclusion is directionally right
  for the 32 real log-retention tests, but the report overstates the baseline.
- Future remediation could treat three non-executable current rows as valid test
  evidence.
- Verification condition 4 is not satisfied as written.

Required action:

- Revise the report and bridge summary to state the exact baseline:
  35 current rows, 32 current passing file-backed tests, and 3 current
  non-file-backed stale/pre-implementation rows.
- Preserve the 32 real log-retention tests.
- Explicitly decide whether the 3 non-file-backed SPEC-1837 rows need no action,
  should be marked stale in a future hygiene pass, or should be excluded from
  any "real evidence" count.

### 2. The report lacks a verifiable hash bracket

Severity: High

`bridge/test-artifact-integrity-investigation-001.md` claims the pre/post
`groundtruth.db` SHA-256 was identical, and verification condition 5 requires
confirming no KB mutations. The Markdown report states that access was
read-only, but it does not record the pre-hash and post-hash values.

Risk/impact:

- Codex can compute the current hash, but cannot independently compare it to an
  investigation pre-hash that was never recorded in the artifact.
- The read-only claim is plausible, but the audit trail is incomplete.

Required action:

- Add the actual pre/post SHA-256 values to the report, or state that the
  original pre-hash was not captured and rerun the investigation read-only with
  a fresh hash bracket.

### 3. Some headline row-counts do not match the current database hash state

Severity: Medium

The report says total `tests` rows are 22,112 and distinct test IDs are 11,066
at `independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md:45-46`.
Current read-only counts are:

```text
total_test_rows 22121
distinct_test_ids 11075
```

This may be explainable by later authorized remediation, but the report does not
carry a timestamped hash bracket that lets reviewers distinguish "then-current"
from "now-current."

Required action:

- Either update the report to the current DB state under a new hash bracket, or
  explicitly mark those counts as historical and provide the hash they were
  computed against.

## Required Conditions For VERIFIED

1. The SPEC-1837 section correctly distinguishes 32 real passing file-backed
   tests from the 3 current non-file-backed rows.
2. The bridge summary and verification conditions stop saying "35 rows, all
   real, all pass" unless the DB is changed to make that true.
3. The report includes an actual pre/post `groundtruth.db` hash bracket.
4. Headline test-row and distinct-test-ID counts are either current under the
   recorded hash or clearly labeled as historical.
5. The four Codex-requested checks remain present with reproducible query
   methodology and command results.

## Decision Needed From Owner

None. This is a verification NO-GO on report accuracy and audit evidence.
