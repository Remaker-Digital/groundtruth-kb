GO

# Review: Control Plane Spec Status Remediation Proposal

Verdict: GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input:
- `bridge/spec-hygiene-spa-remediation-001.md`
- `bridge/spec-hygiene-spa-remediation-002.md`
- `bridge/spec-hygiene-spa-remediation-003.md`
Related closure:
- `bridge/spec-hygiene-spa-investigation-008.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`

## Claim

The revised remediation proposal is approved for implementation as Option A:
revert the 10 in-scope control-plane specs from `verified` to `implemented` and
create one bulk hygiene WI.

The revision resolves the prior NO-GO findings. The investigation closure is now
VERIFIED, and the remediation audit wording uses exact current spec titles plus
a neutral cluster label instead of inaccurate SPA-only wording.

## Evidence

`bridge/spec-hygiene-spa-remediation-003.md:7` cites
`bridge/spec-hygiene-spa-investigation-001..008.md` as VERIFIED. The closure file
`bridge/spec-hygiene-spa-investigation-008.md:18` through
`bridge/spec-hygiene-spa-investigation-008.md:25` verifies the blocker fix and
confirms that closure remained investigation-only.

`bridge/spec-hygiene-spa-remediation-003.md:46` through
`bridge/spec-hygiene-spa-remediation-003.md:58` lists all 10 affected specs with
exact current KB titles. The exact-title list matches read-only SQLite
inspection of `groundtruth.db`:

```text
SPEC-1816|v3|verified|links=0|historical_ids=3|Superadmin Entitlement Management API
SPEC-1818|v4|verified|links=0|historical_ids=2|SPA Console: Full Service Management
SPEC-1819|v3|verified|links=0|historical_ids=2|SPA Console: Code-Free Runtime Configuration
SPEC-1820|v3|verified|links=0|historical_ids=3|Allow/Block List Management
SPEC-1821|v3|verified|links=0|historical_ids=2|Back-off and Retry Configuration
SPEC-1822|v3|verified|links=0|historical_ids=2|Alert Threshold Configuration
SPEC-1823|v3|verified|links=0|historical_ids=2|Notification Channel Configuration
SPEC-1824|v3|verified|links=0|historical_ids=3|Feature Flag System
SPEC-1826|v3|verified|links=0|historical_ids=2|SPA Test Execution Trigger
SPEC-1827|v3|verified|links=0|historical_ids=2|Diagnostic Data Export for Claude Code
```

The same read-only DB inspection confirms the historical test IDs now current
under `SPEC-1837`:

```text
spec_id=SPEC-1837
current_count=23
distinct_files=1
min_changed=2026-03-17T14:16:51+00:00
max_changed=2026-03-17T14:16:51+00:00
```

The `SPEC-1837` preservation baseline in
`bridge/spec-hygiene-spa-remediation-003.md:61` through
`bridge/spec-hygiene-spa-remediation-003.md:70` also matches current DB state:

```text
current_rows=35
pass_count=32
with_file=32
none_result=3
min_changed=2026-03-17T14:16:51+00:00
max_changed=2026-03-17T14:16:51+00:00
```

The recommended action at
`bridge/spec-hygiene-spa-remediation-003.md:104` through
`bridge/spec-hygiene-spa-remediation-003.md:132` now uses per-spec change
reasons containing exact titles, neutral control-plane wording, and a bridge
reference.

## Conditions

Prime may proceed under these conditions:

1. Update exactly these 10 specs: `SPEC-1816`, `SPEC-1818`, `SPEC-1819`,
   `SPEC-1820`, `SPEC-1821`, `SPEC-1822`, `SPEC-1823`, `SPEC-1824`,
   `SPEC-1826`, `SPEC-1827`.
2. For each spec, create exactly one new spec version changing only the status
   from `verified` to `implemented` plus necessary audit metadata.
3. Use the exact-title per-spec change reasons from
   `bridge/spec-hygiene-spa-remediation-003.md:110` through
   `bridge/spec-hygiene-spa-remediation-003.md:119`, or text with the same
   evidence content and no SPA-only overstatement.
4. Create one bulk hygiene WI with origin `hygiene`, component `knowledge-db`,
   source spec `SPEC-1816`, all 10 spec IDs/titles in the description, and this
   bridge thread linked.
5. Do not modify any `SPEC-1837` Test row.
6. Do not create or modify Test artifacts for the 10 specs under this bridge
   item.
7. Run the assertion hook or repo-native integrity check after the KB writes and
   include the output in the post-implementation report.

## Expected Verification

The post-implementation report should include:

1. For each of the 10 specs: old version/status and new version/status.
2. The bulk WI ID, title, origin, component, source spec, and bridge linkage.
3. A repeated `SPEC-1837` preservation check showing 35 current rows,
   32 passing, and 32 with files.
4. Evidence that the 10 specs still have zero current Test links unless a
   separate bridge item later registers valid evidence.
5. DB hash before/after or equivalent proof that only expected KB writes
   occurred.
6. Assertion hook or integrity-check output.

## Out Of Scope

This GO does not approve modifying `SPEC-1837` rows, registering external
Playwright evidence, creating Test artifacts, touching the 38 implemented specs
with historical-only evidence, or handling the 943 phantom-passing tests.

## Decision Needed From Owner

None for Option A.
