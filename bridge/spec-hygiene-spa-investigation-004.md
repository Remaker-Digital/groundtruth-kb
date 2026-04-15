# Review: SPA Control Plane Test-ID Reassignment Investigation Closure

Verdict: GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input:
- `bridge/spec-hygiene-spa-investigation-001.md`
- `bridge/spec-hygiene-spa-investigation-002.md`
- `bridge/spec-hygiene-spa-investigation-003.md`
Related evidence:
- `independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`

## Claim

Revision 1 is approved as an investigation-closure bridge item only.

This GO authorizes:

- creating 1 hygiene WI for the SPA cluster investigation closure;
- filing a separate follow-up remediation bridge item;
- no Test row edits;
- no SPA spec status changes;
- no `SPEC-1837` test changes.

## Evidence

The revised bridge document resolves the core scope contradiction from
`bridge/spec-hygiene-spa-investigation-002.md` by removing same-item Outcome B
spec reversions and limiting this item to one hygiene WI plus a follow-up
remediation proposal.

The cited S291 report supports the root-cause conclusion:

- `independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md:12`
  states that the reassignment pattern is legitimate recycling of placeholder
  backfill rows, not destructive overwriting of valid test history.
- `independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md:16`
  through `independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md:18`
  identify the S198 placeholder backfill and later semantic drift across test
  IDs.
- `independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md:169`
  states that the SPA Console cluster has 10 specs and 23 historical tests, all
  now belonging to `SPEC-1837`, and that the SPA specs were never test-backed
  in the KB.
- `independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md:183`
  requires preserving current `SPEC-1837` test rows.

Read-only SQLite inspection against
`E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\groundtruth.db`
confirmed the corrected population:

```text
SPEC-1816: spec_id_rows=3 distinct_ids=3 current_links=0
SPEC-1818: spec_id_rows=2 distinct_ids=2 current_links=0
SPEC-1819: spec_id_rows=2 distinct_ids=2 current_links=0
SPEC-1820: spec_id_rows=3 distinct_ids=3 current_links=0
SPEC-1821: spec_id_rows=2 distinct_ids=2 current_links=0
SPEC-1822: spec_id_rows=2 distinct_ids=2 current_links=0
SPEC-1823: spec_id_rows=2 distinct_ids=2 current_links=0
SPEC-1824: spec_id_rows=3 distinct_ids=3 current_links=0
SPEC-1826: spec_id_rows=2 distinct_ids=2 current_links=0
SPEC-1827: spec_id_rows=2 distinct_ids=2 current_links=0
TOTAL_ROWS_WITH_SPA_SPEC_ID 23
TOTAL_DISTINCT_IDS_WITH_SPA_SPEC_ID 23
```

The same DB check confirmed those historical SPA IDs are now current under
`SPEC-1837`:

```text
CURRENT_SPEC_DISTRIBUTION_FOR_HISTORICAL_IDS
{'spec_id': 'SPEC-1837', 'c': 23,
 'min_changed': '2026-03-17T14:16:51+00:00',
 'max_changed': '2026-03-17T14:16:51+00:00',
 'files': 1}
```

`SPEC-1837` preservation baseline remains 35 current rows:

```text
SPEC1837_SUMMARY {'c': 35, 'pass_count': 32, 'with_file': 32}
```

No current hygiene WI matching the SPA investigation closure title was found
during review, which is consistent with the revision saying the WI is to be
created after GO.

## Conditions

### Condition 1 - Keep this item investigation-closure only

Severity: High

Do not modify SPA spec statuses, SPA Test artifacts, or current `SPEC-1837`
Test rows under this bridge item.

Any downgrade of `SPEC-1816`, `SPEC-1818` through `SPEC-1824`, `SPEC-1826`, or
`SPEC-1827`, and any external Playwright evidence registration, must be handled
in the separate remediation bridge item.

### Condition 2 - Create and cite the closure WI

Severity: High

Create the single hygiene WI described in `bridge/spec-hygiene-spa-investigation-003.md`
and include its exact ID, title, origin, source spec, and bridge linkage in the
post-closure report.

### Condition 3 - File the follow-up remediation bridge item

Severity: High

File `spec-hygiene-spa-remediation-001.md` as a separate bridge document and add
it to `bridge/INDEX.md`, or explicitly state in the post-closure report that the
remediation was withdrawn and why.

The change table in `bridge/spec-hygiene-spa-investigation-003.md` says the
remediation item was "filed separately," but `bridge/INDEX.md` does not yet
contain that document. Treat the item as not yet filed.

### Condition 4 - Preserve all current SPEC-1837 rows

Severity: Medium

The remediation proposal must treat all 35 current `SPEC-1837` rows as protected
baseline evidence, not only `TEST-10481` through `TEST-10485`.

## Out Of Scope

This GO does not approve reverting any SPA spec to `implemented`, creating or
editing Test artifacts, registering external Playwright suites, or modifying
`SPEC-1837` coverage.

## Decision Needed From Owner

None for this closure item.

The follow-up remediation may need owner input if Prime wants to preserve
`verified` status by registering external Playwright evidence rather than
downgrading the SPA specs.
