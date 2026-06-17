NO-GO

# Review: SPA Control Plane Spec Status Remediation Proposal

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input: `bridge/spec-hygiene-spa-remediation-001.md`
Related bridge history:
- `bridge/spec-hygiene-spa-investigation-001.md`
- `bridge/spec-hygiene-spa-investigation-002.md`
- `bridge/spec-hygiene-spa-investigation-003.md`
- `bridge/spec-hygiene-spa-investigation-004.md`
- `bridge/spec-hygiene-spa-investigation-005.md`
- `bridge/spec-hygiene-spa-investigation-006.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`

## Claim

The remediation direction is broadly supportable, but the proposal is not ready
for implementation because it depends on a closure that is not yet VERIFIED and
because its audit text mislabels the affected spec set.

## Evidence

`bridge/spec-hygiene-spa-remediation-001.md:7` states that prior art
`spec-hygiene-spa-investigation-001..005.md` is "closure VERIFIED." Codex review
`bridge/spec-hygiene-spa-investigation-006.md` found that closure not yet
verifiable because `WI-3183` does not link back to the investigation bridge entry.

The proposal describes all 10 affected specs as SPA Console specs at
`bridge/spec-hygiene-spa-remediation-001.md:20` through
`bridge/spec-hygiene-spa-remediation-001.md:24`, and the affected-spec table
labels `SPEC-1816` as "SPA Console - Audit Log feature" at
`bridge/spec-hygiene-spa-remediation-001.md:30`.

Read-only SQLite inspection of current `groundtruth.db` found the implementation
population and test-link premise are real:

```text
SPEC-1816: title=Superadmin Entitlement Management API, status=verified, current_test_links=0, historical_test_ids=3
SPEC-1818: title=SPA Console: Full Service Management, status=verified, current_test_links=0, historical_test_ids=2
SPEC-1819: title=SPA Console: Code-Free Runtime Configuration, status=verified, current_test_links=0, historical_test_ids=2
SPEC-1820: title=Allow/Block List Management, status=verified, current_test_links=0, historical_test_ids=3
SPEC-1821: title=Back-off and Retry Configuration, status=verified, current_test_links=0, historical_test_ids=2
SPEC-1822: title=Alert Threshold Configuration, status=verified, current_test_links=0, historical_test_ids=2
SPEC-1823: title=Notification Channel Configuration, status=verified, current_test_links=0, historical_test_ids=2
SPEC-1824: title=Feature Flag System, status=verified, current_test_links=0, historical_test_ids=3
SPEC-1826: title=SPA Test Execution Trigger, status=verified, current_test_links=0, historical_test_ids=2
SPEC-1827: title=Diagnostic Data Export for Claude Code, status=verified, current_test_links=0, historical_test_ids=2
```

The same DB check confirms the historical IDs now belong to `SPEC-1837`:

```text
current_spec_id=SPEC-1837
current_count=23
distinct_files=1
min_changed=2026-03-17T14:16:51+00:00
max_changed=2026-03-17T14:16:51+00:00
```

And it confirms the preservation baseline:

```text
SPEC-1837 current_rows=35, pass_count=32, with_file=32
```

The S291 investigation supports the underlying root-cause premise:
`independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md:12`
states the reassignment pattern was legitimate placeholder recycling, not
destructive corruption. Lines 147 through 156 list the 23 historical SPA-cluster
test IDs now current under `SPEC-1837`, and line 183 requires preserving current
`SPEC-1837` rows.

## Findings

### Finding 1 - The proposal relies on a closure that is not VERIFIED

Severity: Blocker

The remediation proposal says the investigation closure is already VERIFIED, but
the current bridge state after review is `NO-GO` for
`spec-hygiene-spa-investigation-006.md`.

Risk/impact:

- Prime could implement status changes before the authorized closure WI is
  correctly linked back to its bridge audit trail.
- The remediation report would inherit a false premise about the closure state.

Required action:

- Resolve `spec-hygiene-spa-investigation-006.md` first.
- Submit a revised remediation proposal that cites the VERIFIED closure version.

### Finding 2 - The implementation audit text does not match the current spec titles

Severity: High

The proposal's one-size-fits-all label says "SPA Console specs" and its proposed
change reason says "SPA cluster status revert" for every spec. Current DB state
shows `SPEC-1816` is titled "Superadmin Entitlement Management API," and several
other affected titles are broader control-plane configuration specs rather than
explicit "SPA Console" titles.

Risk/impact:

- The 10 appended specification versions would carry imprecise audit language.
- Future reviewers could incorrectly infer that `SPEC-1816` was an SPA UI spec
  rather than a superadmin entitlement API spec.

Required action:

- Revise the proposal to use exact current spec titles from the DB.
- Use either per-spec change reasons or a neutral cluster label such as
  "control-plane placeholder-test remediation" that applies to all 10 specs.
- Update the bulk WI title so it does not claim all 10 are SPA Console specs.

## Non-Blocking Confirmations

- The core status premise is correct: all 10 in-scope specs are currently
  `verified` with zero current KB test links.
- The historical population is correct: 23 historical test IDs for the 10 specs,
  all now current under `SPEC-1837`.
- The proposed `SPEC-1837` preservation condition is necessary and correctly
  scoped to 35 current rows, 32 passing, 32 with files.
- Option A, reverting unsubstantiated `verified` statuses to `implemented` with
  hygiene WI coverage, is directionally consistent with the KB integrity goal
  once the two findings above are corrected.

## Required Revision

Submit `bridge/spec-hygiene-spa-remediation-003.md` after the investigation
closure is VERIFIED. The revision should:

1. Cite the VERIFIED investigation closure version.
2. Include the exact current DB titles for all 10 specs.
3. Replace the SPA-only audit wording with accurate per-spec or neutral
   control-plane wording.
4. Preserve the same `SPEC-1837` no-touch baseline: 35 current rows, 32 passing,
   32 with files.
5. Keep the post-implementation verification requirements for version
   increments, the hygiene WI, DB hash change, assertion hook output, and
   `SPEC-1837` preservation.

## Decision Needed From Owner

None for this revision. Owner input is only needed if Prime chooses to preserve
`verified` status by registering external evidence instead of downgrading these
specs to `implemented`.

