# Verification Review: S291 Test Artifact Integrity Investigation

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input:
- `bridge/test-artifact-integrity-investigation-001.md`
- `bridge/test-artifact-integrity-investigation-002.md`
- `bridge/test-artifact-integrity-investigation-003.md`
Artifacts inspected:
- `independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md`
- `groundtruth.db` opened read-only via SQLite
- `tests/multi_tenant/test_log_retention.py`

## Prior Deliberations

The investigation remains tied to `DELIB-0045` and `DELIB-0046` anti-phantom-evidence
guidance and to `bridge/s291-prioritization-request-002.md`, which authorized the
broadened test artifact integrity investigation.

## Claim

The revised report fixes the SPEC-1837 factual error and keeps the four integrity checks
reproducible. It still cannot be marked VERIFIED because the report does not contain the
real pre/post DB hash bracket required by the prior NO-GO. Instead, it explicitly states
that no original pre-hash was captured and that the no-mutation claim cannot be independently
proved from the artifact.

## Positive Evidence

The SPEC-1837 baseline is now correctly characterized in the report, and read-only DB
verification agrees:

```text
spec1837_current_rows 35
spec1837_last_result_counts {None: 3, 'pass': 32}
spec1837_file_backed_passing 32
spec1837_non_file_backed 3
```

The three non-file-backed current rows are exactly the stale/pre-implementation rows
named in the revised report:

```text
TEST-10452 v2 last_result=None test_file=None test_function=None changed_by=S200
  Stale: pre-implementation spec, replaced by implementation-matching tests
TEST-10453 v2 last_result=None test_file=None test_function=None changed_by=S200
  Stale: pre-implementation spec, replaced by implementation-matching tests
TEST-10454 v3 last_result=None test_file=None test_function=None changed_by=S200
  Stale: referenced non-existent LogRetentionService API
```

The test file exists at `tests/multi_tenant/test_log_retention.py`.

The four requested integrity checks remain reproducible against the current DB:

```text
multi_historical_spec_ids 1978
blank_current_after_historical_nonempty 254
blank_current_last_result_counts {'stale': 254}
current_passing_no_test_file 943
total_test_rows 22121
distinct_test_ids 11075
```

Codex's own verification run was read-only and hash-stable:

```text
pre_hash_this_verification  141AC9FD8761D243BB89CCE775063B71AC28AB5DF7554D1349D475B045694914
post_hash_this_verification 141AC9FD8761D243BB89CCE775063B71AC28AB5DF7554D1349D475B045694914
hash_unchanged_this_verification True
```

## Finding

### 1. The report still lacks the required real pre/post hash bracket

Severity: High

`bridge/test-artifact-integrity-investigation-002.md` required the revised artifact to
include an actual pre/post `groundtruth.db` hash bracket, or to state the original pre-hash
was not captured and rerun the investigation read-only with a fresh hash bracket.

The revised report does not do that. It states:

```text
Investigation era (2026-04-14): Not captured
Codex verification run (2026-04-15): 141AC9FD8761D243BB89CCE775063B71AC28AB5DF7554D1349D475B045694914
Because no pre-hash was captured, this bracket cannot independently prove zero mutation during the investigation window.
```

That is honest, but it is still not the requested evidence. The report also keeps
investigation-era headline counts while current counts have moved from 22,112/11,066 to
22,121/11,075. The historical labeling is helpful, but without a hash for the historical
state or a fresh rerun section with pre/post hashes, reviewers cannot tie the reported
historical counts to a concrete DB artifact.

Risk/impact:

- The investigation's substantive findings are credible, but the audit trail still cannot
  prove no mutation during the investigation run.
- Future forensic reports may normalize "method says read-only" as a substitute for a
  hash bracket, which is exactly the evidence gap this NO-GO was meant to close.

Required action:

1. Add a fresh current-state rerun section to the report with:
   - pre-hash captured before the rerun,
   - the rerun command/query bundle,
   - current count outputs,
   - post-hash captured after the rerun,
   - explicit statement that the fresh rerun is the independently verifiable read-only bracket.
2. Keep the investigation-era counts only as historical context, or attach them to a concrete
   historical DB copy/hash if one exists.
3. Preserve the corrected SPEC-1837 baseline exactly: 35 current rows, 32 current passing
   file-backed rows, and 3 current non-file-backed stale/pre-implementation rows.

## Decision Needed From Owner

None. This is an audit-evidence NO-GO, not a disagreement with the corrected SPEC-1837
substance.
