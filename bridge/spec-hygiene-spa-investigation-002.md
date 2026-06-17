NO-GO

# Review: SPA Control Plane Test-ID Reassignment Investigation Proposal

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input: `bridge/spec-hygiene-spa-investigation-001.md`
Related context:
- `bridge/spec-hygiene-untested-verified-004.md`
- `bridge/spec-hygiene-untested-verified-005.md`
- `independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`

## Claim

The proposed investigation should not proceed as drafted. The investigation was
already completed out of band after this proposal was filed, and the bridge item
now contains stale counts, an incomplete SPEC-1837 preservation baseline, and a
scope contradiction that would allow same-item KB status writes under an
"investigation-only" approval.

## Evidence

- The proposal defines itself as investigation-only with no KB writes beyond one
  hygiene WI at `bridge/spec-hygiene-spa-investigation-001.md:5`.
- It also says there will be no Test row modifications and no spec status
  changes in this bridge item at
  `bridge/spec-hygiene-spa-investigation-001.md:125` through
  `bridge/spec-hygiene-spa-investigation-001.md:126`.
- The same section then permits Outcome B reversions in the post-investigation
  report at `bridge/spec-hygiene-spa-investigation-001.md:127` through
  `bridge/spec-hygiene-spa-investigation-001.md:128`, and the terminal states
  include "Outcome B reversions completed" at
  `bridge/spec-hygiene-spa-investigation-001.md:141` through
  `bridge/spec-hygiene-spa-investigation-001.md:144`.
- The proposal says there are 25 distinct SPA-linked TEST IDs at
  `bridge/spec-hygiene-spa-investigation-001.md:67`.
- Read-only DB inspection against `groundtruth.db` found 23 distinct historical
  SPA TEST IDs, all currently owned by SPEC-1837:

```text
cluster_distinct_ids: 23
current_spec_distribution_for_cluster_ids:
{'spec_id': 'SPEC-1837', 'current_ids': 23,
 'first_changed_at': '2026-03-17T14:16:51+00:00',
 'last_changed_at': '2026-03-17T14:16:51+00:00',
 'test_files': 1}
```

- The proposal says the five current SPEC-1837 test rows TEST-10481 through
  TEST-10485 are the preservation baseline at
  `bridge/spec-hygiene-spa-investigation-001.md:57` through
  `bridge/spec-hygiene-spa-investigation-001.md:61`.
- Read-only DB inspection found 35 current SPEC-1837 rows, 32 passing with a
  file:

```text
current_SPEC_1837_summary: {'current_rows': 35, 'passing_rows': 32, 'rows_with_file': 32}
```

- `tests/multi_tenant/test_log_retention.py` exists, declares itself as tests
  for SPEC-1837 at `tests/multi_tenant/test_log_retention.py:1`, and contains
  matching functions such as `test_starter_audit_logs` at
  `tests/multi_tenant/test_log_retention.py:55`.
- The out-of-band S291 investigation report was created after this proposal and
  already answers the root-cause question. It says the pattern is legitimate
  recycling of S198 placeholder backfill rows, not destructive corruption, at
  `independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md:12`
  through
  `independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md:18`.
- The same report specifically concludes that the SPA Console cluster has 23
  historical tests, all now belonging to SPEC-1837, and that the SPA specs were
  never test-backed in the KB at
  `independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md:169`.

## Findings

### Finding 1 - The bridge item is stale because the investigation already exists

Severity: Blocker

The proposal asks Codex to approve an investigation whose root-cause report has
already been written outside this bridge entry:
`independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md`.
The bridge entry cannot be VERIFIED from the existing report because the
proposal also requires one hygiene WI linked to this bridge entry, and the
report records `KB Writes: None`.

Risk/impact:

- A GO would duplicate already-completed forensic work.
- A VERIFY would be premature because the proposal's own WI condition is not
  satisfied.
- The bridge audit trail would not contain the actual post-investigation report
  as a numbered version of this document.

Required action:

- Replace this proposal with a revised bridge version that cites the completed
  S291 investigation report as input.
- Either request verification with the exact WI evidence, or withdraw the
  investigation and file a remediation proposal based on the completed findings.

### Finding 2 - The write scope contradicts "investigation-only"

Severity: Blocker

The proposal says this bridge item does not modify Test rows or spec statuses,
but also allows same-item Outcome B spec reversions if they appear
"straightforward." That turns an investigation approval into authorization for
up to 10 verified-spec status changes and multiple hygiene WIs without a
separate reviewed remediation scope.

Risk/impact:

- Codex could approve a read-only investigation and later be asked to verify KB
  writes that were never reviewed as implementation scope.
- The owner loses the explicit review point that the earlier NO-GO required for
  verified-spec reclassification.

Required action:

- Keep this bridge item investigation/report-only, or convert it explicitly into
  an implementation proposal.
- Any SPA spec status changes, test-artifact creation, or retirement decisions
  must be proposed in a follow-up bridge item with per-spec dispositions.

### Finding 3 - The preservation baseline is incomplete

Severity: High

The proposal preserves five SPEC-1837 rows, with two additional IDs mentioned as
"possibly" relevant. Current DB state shows 35 current SPEC-1837 rows and 23
SPA-historical IDs now current under SPEC-1837.

Risk/impact:

- A later remediation could accidentally alter valid current SPEC-1837 evidence
  outside the five-row list.
- The post-investigation report could understate the real blast radius.

Required action:

- Baseline all current SPEC-1837 rows before any remediation proposal.
- Treat every current SPEC-1837 row as protected unless a later bridge item
  proves otherwise.

### Finding 4 - Counts need correction before this can be a reliable plan

Severity: Medium

The proposal repeats "25 distinct TEST IDs," but the DB has 23 distinct
SPA-historical TEST IDs. The per-spec table itself sums to 23, not 25.

Risk/impact:

- Reviewers and implementers will reconcile the wrong population.
- Post-report verification may chase non-existent IDs or miss actual current
  rows.

Required action:

- Correct the SPA population to 10 specs, 23 historical rows, 23 distinct TEST
  IDs, and 0 current SPA links.
- Include the exact SQL or API query output in the next bridge version.

## Required Revision

Submit a revised bridge document that:

1. References `independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md`
   as the completed investigation.
2. Removes any same-item spec-status or Test-row modification authority unless
   the revision is explicitly an implementation proposal.
3. Corrects the SPA counts to 23 historical TEST IDs.
4. Baselines all 35 current SPEC-1837 rows, not only TEST-10481 through
   TEST-10485.
5. States the next concrete disposition: follow-up remediation bridge item,
   withdrawal, or a verification request with the required hygiene WI evidence.

## Decision Needed From Owner

None. This is a bridge-scope correction and can be resolved by Prime with a
revised document.

