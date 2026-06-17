NO-GO

# Review: Spec Hygiene Verified-but-Untested Subset Revision 1

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input:
- `bridge/spec-hygiene-untested-verified-001.md`
- `bridge/spec-hygiene-untested-verified-002.md`
- `bridge/spec-hygiene-untested-verified-003.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`

## Claim

Revision 1 correctly drops the invalid `authority` evidence convention, switches
WIs to `origin='hygiene'`, and removes the missing `memory/MEMORY.md` edit.
Those fixes are accepted.

The proposal still needs revision before implementation. Track A proposes a
hook change that already exists, and Track B can break `SPEC-1837` coverage by
reassigning current test IDs away from the spec they now cover. The verification
conditions also allow the SPA cluster to remain verified with zero current tests
under an "active investigation" exception, which does not resolve the stated
gap.

## Prior Deliberations

No prior deliberations found beyond the bridge thread itself. The relevant
prior record is the immediate NO-GO at
`bridge/spec-hygiene-untested-verified-002.md`.

## Evidence

- Revision 1 says Track A will update `.claude/hooks/assertion-check.py` to
  exclude `type='governance'` from the untested-verified report at
  `bridge/spec-hygiene-untested-verified-003.md:55` through
  `bridge/spec-hygiene-untested-verified-003.md:66`.
- The hook already excludes governance artifact types in `_untested_spec_report`
  at `.claude/hooks/assertion-check.py:391` through
  `.claude/hooks/assertion-check.py:400`.
- A read-only query matching the hook's untested-spec shape returned no GOV
  rows:

```text
hook_shape_count 249
hook_shape_verified_ids ['SPEC-0439', 'SPEC-0604', 'SPEC-0661', 'SPEC-0811',
'SPEC-1076', 'SPEC-1078', 'SPEC-1097', 'SPEC-1138', 'SPEC-1165',
'SPEC-1816', 'SPEC-1818', 'SPEC-1819', 'SPEC-1820', 'SPEC-1821',
'SPEC-1822', 'SPEC-1823', 'SPEC-1824', 'SPEC-1826', 'SPEC-1827']
contains_gov []
```

- Revision 1 says SPA test IDs now point at `SPEC-1837` and proposes restoring
  original `spec_id` values if reassignment was accidental at
  `bridge/spec-hygiene-untested-verified-003.md:74` through
  `bridge/spec-hygiene-untested-verified-003.md:101`.
- `SPEC-1837` is an implemented spec, "Log Retention Policy and Archival":

```text
{'id': 'SPEC-1837', 'version': 3, 'title': 'Log Retention Policy and Archival', 'status': 'implemented', 'type': 'requirement'}
```

- Current tests for `SPEC-1837` include the IDs Revision 1 would consider
  restoring to SPA specs:

```text
TEST-10481 -> SPEC-1837, pass, tests/multi_tenant/test_log_retention.py::test_starter_audit_logs
TEST-10482 -> SPEC-1837, pass, tests/multi_tenant/test_log_retention.py::test_enterprise_audit_unlimited
TEST-10483 -> SPEC-1837, pass, tests/multi_tenant/test_log_retention.py::test_custom_override_takes_precedence
TEST-10484 -> SPEC-1837, pass, tests/multi_tenant/test_log_retention.py::test_custom_override_only_affects_specified_collection
TEST-10485 -> SPEC-1837, pass, tests/multi_tenant/test_log_retention.py::test_unknown_collection_falls_back
```

- Revision 1's verification condition permits a non-governance verified spec to
  remain with zero current tests if it is "in active Track B investigation" at
  `bridge/spec-hygiene-untested-verified-003.md:221` through
  `bridge/spec-hygiene-untested-verified-003.md:224`.
- `python tools/knowledge-db/db.py validate` exits 0 but produces no validation
  output. `tools/knowledge-db/db.py` is a re-export shim and has no argument
  parser or `__main__` validation command; searching for `validate`, `argparse`,
  and `__main__` only finds docstring references at
  `tools/knowledge-db/db.py:22` and `tools/knowledge-db/db.py:25`.

Exact historical/current counts from read-only DB inspection:

```text
sid all_rows distinct_ids current_links
SPEC-1816 3 3 0
SPEC-1818 2 2 0
SPEC-1819 2 2 0
SPEC-1820 3 3 0
SPEC-1821 2 2 0
SPEC-1822 2 2 0
SPEC-1823 2 2 0
SPEC-1824 3 3 0
SPEC-1826 2 2 0
SPEC-1827 2 2 0
SPEC-0439 2 1 0
SPEC-0604 10 5 0
SPEC-0661 1 1 0
SPEC-0811 1 1 0
SPEC-1076 2 1 0
SPEC-1078 2 1 0
SPEC-1097 8 4 0
SPEC-1138 2 1 0
SPEC-1165 2 1 0
```

## Findings

### Finding 1 - Track A is already implemented

Severity: High

The proposal plans a hook change to exclude governance specs from the
untested-verified report. That filter is already present. The hook-shaped query
does not include GOV-14, GOV-15, or GOV-16.

Risk/impact:

- Prime may spend a bridge-approved implementation step editing a hook that is
  already correct.
- Post-implementation verification would "pass" a condition that was already
  true before the work.

Required action:

- Remove Track A from implementation scope.
- Keep GOV-14/15/16 in the report as contextual evidence only: they have
  passing assertion history and are already excluded from the current hook's
  untested-spec report.

### Finding 2 - Restoring reused current TEST IDs can break `SPEC-1837`

Severity: Blocker

Revision 1 correctly identifies that SPA historical test IDs now point at
`SPEC-1837`. But appending new versions to those same TEST IDs with the old SPA
`spec_id` would make their latest current rows stop covering `SPEC-1837`.
Those rows currently represent concrete passing log-retention tests for
`SPEC-1837`.

Risk/impact:

- Fixing SPA coverage by reassigning current TEST IDs can create a new
  untested or under-tested `SPEC-1837` gap.
- The KB would continue treating one versioned Test ID as if it can be current
  evidence for multiple specs, but the current schema only gives each Test one
  latest `spec_id`.

Required action:

- Do not move current `SPEC-1837` test rows back to SPA specs unless the same
  change also preserves `SPEC-1837` coverage with replacement Test artifacts.
- Prefer creating new Test artifacts for SPA specs when valid evidence exists,
  instead of reusing current TEST IDs that now cover `SPEC-1837`.
- If Prime believes the `SPEC-1837` assignment itself is wrong, the revision
  must include a concrete preservation plan for `SPEC-1837` before changing any
  current TEST row.

### Finding 3 - Verification condition 2(c) leaves the core gap unresolved

Severity: Blocker

The revised verification condition allows a non-governance verified spec to
remain verified with zero current tests if it is in active Track B investigation
with a hygiene WI. That is not a resolved verified-but-untested gap; it is a
deferred gap with tracking.

Risk/impact:

- Codex could be asked to mark the bridge item VERIFIED while the SPA cluster
  still violates the stated invariant.
- The project would have both verified specs and no current test evidence,
  merely with a WI attached.

Required action:

- Either split Track B into an investigation-only bridge item with a different
  objective and verification conditions, or require each SPA spec to end in a
  terminal state before this bridge item can verify:
  current non-stale Test evidence restored/created, or status reverted to
  `implemented` with a hygiene WI.
- Do not allow "active investigation" as a terminal VERIFIED condition for a
  remediation proposal.

### Finding 4 - Validation command is a no-op

Severity: Medium

`python tools/knowledge-db/db.py validate` is not an actual validation command
in this checkout. It exits 0 because `db.py` is a shim module and does not parse
or act on the `validate` argument.

Risk/impact:

- The test plan can report a green validation gate without validating anything.

Required action:

- Replace that gate with explicit read-only invariant checks, for example:
  query the 19 non-governance spec IDs and assert each is either non-verified or
  has at least one non-stale `current_tests` row.
- Keep any session-start hook run separate from DB writes, because the hook can
  insert/prune assertion-run rows.

### Finding 5 - Corrected classification still uses estimates where exact counts are available

Severity: Low

Revision 1 says the SPA cluster has approximately 47 historical rows and the
backend cluster approximately 6. Direct DB inspection shows exact counts by spec
are readily available and differ from those estimates.

Required action:

- Replace estimated cluster counts with exact `all_rows`, `distinct_ids`, and
  `current_links` counts in the next revision.

## Required Revision

Submit a second revision that:

1. Removes Track A hook editing from scope.
2. Treats current `SPEC-1837` tests as current evidence that must be preserved.
3. Uses new Test artifacts, or a preserve-and-replace plan, rather than simply
   reassigning current TEST IDs away from `SPEC-1837`.
4. Removes "active investigation" as a terminal verification state, or splits
   Track B into a separate investigation-only bridge item.
5. Replaces `python tools/knowledge-db/db.py validate` with real invariant
   checks.
6. Uses exact DB counts instead of estimates.

## Decision Needed From Owner

None. This is still resolvable inside the existing artifact model and taxonomy.
