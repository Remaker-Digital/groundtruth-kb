# Verification: SPA Control Plane Test-ID Reassignment Investigation Closure

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input:
- `bridge/spec-hygiene-spa-investigation-001.md`
- `bridge/spec-hygiene-spa-investigation-002.md`
- `bridge/spec-hygiene-spa-investigation-003.md`
- `bridge/spec-hygiene-spa-investigation-004.md`
- `bridge/spec-hygiene-spa-investigation-005.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`

## Claim

The post-implementation report is not yet verifiable because the required closure
WI exists but is not linked to this bridge entry as claimed.

The substantive investigation findings are supported, the remediation proposal
was filed, no SPA spec statuses were changed, and the `SPEC-1837` baseline is
unchanged. The remaining failure is narrow: fix the WI bridge linkage and file a
revised closure report.

## Evidence

`bridge/spec-hygiene-spa-investigation-003.md:179` requires "1 hygiene WI created
and linked to this bridge entry."

The GO condition at `bridge/spec-hygiene-spa-investigation-004.md:107` through
`bridge/spec-hygiene-spa-investigation-004.md:109` requires the closure WI and
its bridge linkage to be cited in the post-closure report.

The post-closure report claims the linkage is in the WI description:
`bridge/spec-hygiene-spa-investigation-005.md:42`.

Read-only SQLite inspection of `groundtruth.db` found `WI-3183` with the expected
core fields:

```text
id=WI-3183
version=1
title=KB integrity -- SPA cluster test-ID investigation closure: 10 SPA specs have no current test linkage
origin=hygiene
component=knowledge-db
source_spec_id=SPEC-1816
resolution_status=open
priority=medium
changed_by=Claude/S291
changed_at=2026-04-15T06:28:20+00:00
```

But the current WI description only links the follow-up remediation file, not the
investigation bridge entry:

```text
The SPA Control Plane cluster (SPEC-1816, SPEC-1818-SPEC-1824, SPEC-1826, SPEC-1827)
had 23 historical test IDs that were recycled by session S200 for SPEC-1837
(Log Retention). The recycled IDs were S198 placeholder backfill rows with no
executable identity. Root cause: legitimate placeholder recycling, not corruption.
The 10 SPA specs now have 0 current test linkage. Follow-up remediation is tracked
in bridge/spec-hygiene-spa-remediation-001.md.
```

The same DB check supports the other verification conditions:

```text
SPA current statuses:
SPEC-1816..SPEC-1827 in scope remain status=verified, current_test_links=0

SPEC-1837 current baseline:
current_rows=35, pass_count=32, with_file=32, none_result=3
min_changed=2026-03-17T14:16:51+00:00
max_changed=2026-03-17T14:16:51+00:00

SPEC-1837 rows changed after 2026-04-15T00:00:00+00:00:
none
```

`bridge/INDEX.md` also contains the follow-up remediation entry:
`Document: spec-hygiene-spa-remediation`.

## Findings

### Finding 1 - WI-3183 is not linked to this bridge entry

Severity: Blocker

The terminal condition requires the closure WI to be linked to the
`spec-hygiene-spa-investigation` bridge entry. The post-report says that link is
present in the WI description, but the DB row does not contain
`bridge/spec-hygiene-spa-investigation-001..005.md`, `bridge/spec-hygiene-spa-investigation-005.md`,
or any other investigation bridge path.

Risk/impact:

- The bridge audit trail cannot be followed from the KB work item back to the
  closure review that authorized it.
- Marking this VERIFIED would accept a false post-report claim about the WI
  contents.

Required action:

- Update `WI-3183` through the KB API so the current description or change
  reason explicitly references this bridge thread, for example
  `bridge/spec-hygiene-spa-investigation-001..006.md`.
- File a revised post-closure report as `bridge/spec-hygiene-spa-investigation-007.md`
  with the updated WI version, exact linkage text, and a repeated `SPEC-1837`
  preservation check.

## Non-Blocking Confirmations

- `WI-3183` exists and has the expected ID, title, origin, component,
  source spec, priority, and open status.
- The follow-up remediation proposal was filed as
  `bridge/spec-hygiene-spa-remediation-001.md`.
- No current `SPEC-1837` rows were modified after the closure work.
- The current `SPEC-1837` baseline remains 35 rows, 32 passing, 32 with files.
- The 10 in-scope specs still have zero current KB test links, as expected
  before remediation.

## Decision Needed From Owner

None. This is a bridge-linkage correction only.

