# Review: Spec Hygiene Verified-but-Untested Revision 2

Verdict: GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input:
- `bridge/spec-hygiene-untested-verified-001.md`
- `bridge/spec-hygiene-untested-verified-002.md`
- `bridge/spec-hygiene-untested-verified-003.md`
- `bridge/spec-hygiene-untested-verified-004.md`
- `bridge/spec-hygiene-untested-verified-005.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`

## Claim

Revision 2 is approved for the narrowed Tracks C/D/E scope only: the 9
non-governance, non-SPA verified specs with historical test rows but zero
current links.

This GO does not approve any SPA-cluster remediation. SPA work remains governed
by the separate `spec-hygiene-spa-investigation` bridge item.

## Evidence

- Revision 2 removes Track A, splits Track B out, and limits this proposal to
  Tracks C/D/E at `bridge/spec-hygiene-untested-verified-005.md:31` through
  `bridge/spec-hygiene-untested-verified-005.md:43`.
- The exact count table for the 9 in-scope specs is at
  `bridge/spec-hygiene-untested-verified-005.md:47` through
  `bridge/spec-hygiene-untested-verified-005.md:62`.
- Read-only DB inspection against `groundtruth.db` confirmed the scope:

```text
cluster_totals {'all_rows': 30, 'distinct_ids': 16}
current_state_for_historical_ids {'current_spec_id': '', 'last_result': 'stale', 'count': 16}
```

- Per-spec DB inspection confirmed all 9 current specs are still
  `status='verified'`, `type='requirement'`, and `current_links=0`.
- The GroundTruth current-test model uses the latest version per test ID:
  `current_tests` joins against `MAX(version)` at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:433`.
- `KnowledgeDB.update_test()` carries forward `last_result` when omitted at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:2366`.
- A read-only SPEC-1837 baseline query found more current rows than the five
  examples in the proposal:

```text
spec1837_summary {'current_rows': 35, 'passing_rows': 32, 'rows_with_file': 32}
```

- Prime's broader S291 investigation now attributes the C/D/E pattern to S198
  placeholder rows that were later retired: see
  `independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md:169`
  through
  `independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md:170`.

## Conditions

### Condition 1 - Restored test links must be current evidence, not stale links

Severity: High

The proposal's restore path is acceptable only if the resulting latest test row
is non-stale and backed by an inspected or re-run test. Appending a new row that
only restores `spec_id` while carrying forward `last_result='stale'` does not
satisfy terminal state (a).

Required action:

- For any restored test row, record why the test is valid for the spec and make
  the latest row non-stale only with concrete evidence.
- Prefer `last_result='pass'` only when the test was actually run or its current
  pass result is otherwise documented in the post-implementation report.
- If that evidence is not available, revert the spec to `implemented` and create
  the hygiene WI.

### Condition 2 - Preserve the full SPEC-1837 current baseline

Severity: Medium

Revision 2 correctly says to query current SPEC-1837 rows before writes, but its
post-check examples assert only TEST-10481 through TEST-10485. The current
baseline is 35 current SPEC-1837 rows, 32 of them passing with a file.

Required action:

- Baseline all current SPEC-1837 rows before any write.
- Post-check every baseline TEST ID, not only TEST-10481 through TEST-10485.
- Do not modify any current SPEC-1837 row under this C/D/E proposal.

### Condition 3 - Post-report must include executable verification

Severity: Medium

The verification section still includes pseudocode and an "adjust to actual API"
comment at `bridge/spec-hygiene-untested-verified-005.md:188` through
`bridge/spec-hygiene-untested-verified-005.md:205`.

Required action:

- The post-implementation report must include the actual read-only command(s)
  run, plus output proving that each of the 9 specs is either no longer
  `verified` or has at least one non-stale current test row.
- If any spec is reverted, include the WI ID and the exact `change_reason`.
- Include the full SPEC-1837 preservation query output.

## Out Of Scope

This GO does not resolve the larger S291 findings that 57 non-retired specs have
historical-only evidence and 943 current passing tests lack `test_file`; those
remain separate hygiene streams per
`independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md:189`
through
`independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md:199`.

## Decision Needed From Owner

None for this narrowed C/D/E remediation.

