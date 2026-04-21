# Verification Review: S291 Test Artifact Integrity Investigation

Verdict: VERIFIED

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input:
- `bridge/test-artifact-integrity-investigation-001.md`
- `bridge/test-artifact-integrity-investigation-002.md`
- `bridge/test-artifact-integrity-investigation-003.md`
- `bridge/test-artifact-integrity-investigation-004.md`
- `bridge/test-artifact-integrity-investigation-005.md`
Artifacts inspected:
- `independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md`
- `groundtruth.db` opened read-only via SQLite
- `tests/multi_tenant/test_log_retention.py`

## Prior Deliberations

The applicable context remains `DELIB-0045` and `DELIB-0046` anti-phantom-evidence
guidance, plus `bridge/s291-prioritization-request-002.md`, which authorized the
broadened read-only investigation. This final check verifies only the evidence gap left
by `bridge/test-artifact-integrity-investigation-004.md`.

## Claim

The revised report satisfies the remaining NO-GO condition. It now contains a fresh
current-state rerun section with pre-hash, read-only connection string, SQL/query outputs,
post-hash, and an explicit statement that the section is the independently verifiable
read-only bracket. The corrected SPEC-1837 baseline remains intact.

## Evidence

Report section checks:

```text
S291-test-artifact-integrity-investigation.md:232  Historical: Investigation era (2026-04-14)
S291-test-artifact-integrity-investigation.md:234  original pre-hash not captured; historical counts retained as non-verifiable context
S291-test-artifact-integrity-investigation.md:236  Fresh Current-State Rerun (2026-04-15, Prime Builder - S295)
S291-test-artifact-integrity-investigation.md:242  Pre-hash  141AC9FD8761D243BB89CCE775063B71AC28AB5DF7554D1349D475B045694914
S291-test-artifact-integrity-investigation.md:243  Post-hash 141AC9FD8761D243BB89CCE775063B71AC28AB5DF7554D1349D475B045694914
S291-test-artifact-integrity-investigation.md:244  Hash unchanged True
S291-test-artifact-integrity-investigation.md:246  sqlite3.connect('file:groundtruth.db?mode=ro', uri=True)
S291-test-artifact-integrity-investigation.md:296  fresh rerun section constitutes the independently verifiable read-only bracket
```

Codex read-only rerun:

```text
multi_historical_spec_ids 1978
blank_current_after_historical_nonempty 254
blank_current_last_result_counts {'stale': 254}
current_passing_no_test_file 943
total_test_rows 22121
distinct_test_ids 11075
spec1837_total 35
spec1837_pass_file_backed 32
spec1837_non_file_backed 3
pre_hash  141AC9FD8761D243BB89CCE775063B71AC28AB5DF7554D1349D475B045694914
post_hash 141AC9FD8761D243BB89CCE775063B71AC28AB5DF7554D1349D475B045694914
hash_unchanged True
```

The `SPEC-1837` baseline remains the corrected one:

```text
35 current rows total
32 file-backed passing rows
3 current non-file-backed stale/pre-implementation rows
```

The headline table still marks the 22,112 / 11,066 counts as investigation-era values and
points to the DB hash bracket for current state, which addresses the historical/current
count distinction.

## Risk/Impact

The remaining audit-evidence gap is closed. The report now separates historical context
from independently verifiable current-state evidence, and future remediation can rely on
the corrected SPEC-1837 preservation baseline without treating the three non-file-backed
rows as real passing evidence.

## Recommended Action

Use this report as the baseline for the follow-on phantom-passing test audit and any
schema/hook proposal around test ID semantic drift. Preserve the fresh-hash-bracket pattern
for future forensic reports.

## Decision Needed From Owner

None.
