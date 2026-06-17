NO-GO

# Review: POR Step 16.A Verified Spec Hygiene Closure

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-16
Input:
- `bridge/por-step16a-verified-spec-closure-001.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`

## Claim

The proposed closure is not ready for implementation because its main exit
criterion is false against the current `groundtruth.db`.

The S291 remediation threads are substantially supported by prior Codex
verification, and the named hygiene WIs `WI-3178` through `WI-3184` are open.
However, the proposal now broadens the closure invariant to all verified
requirement-type specs, and that broader invariant currently has an unhandled
exception: `SPEC-GTKB-SCOPE`.

## Evidence

The proposal states the closure objective as:

- `bridge/por-step16a-verified-spec-closure-001.md:21` through
  `bridge/por-step16a-verified-spec-closure-001.md:23`: no `verified` spec in
  the KB without current, non-stale test evidence.
- `bridge/por-step16a-verified-spec-closure-001.md:57` through
  `bridge/por-step16a-verified-spec-closure-001.md:59`: expected query result
  is zero, excluding governance-type specs.
- `bridge/por-step16a-verified-spec-closure-001.md:73`: exit criterion is
  zero verified requirement-type specs with zero non-stale test links.

Read-only SQLite inspection of:

`E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\groundtruth.db`

Current database SHA-256 observed during review:

```text
50D4BBA56EC3CE0F497378CC4A9FF2042B6331C5EEBE02E811D9079EF686B5C9
```

Invariant query used:

```sql
SELECT s.id, s.status, COALESCE(s.type, 'requirement') AS type, s.title
FROM current_specifications s
WHERE s.status='verified'
  AND COALESCE(s.type, 'requirement')='requirement'
  AND NOT EXISTS (
      SELECT 1 FROM current_tests t
      WHERE t.spec_id=s.id AND (t.last_result IS NULL OR t.last_result != 'stale')
  )
ORDER BY s.id;
```

Result:

```text
count 1
SPEC-GTKB-SCOPE status=verified type=requirement title=GroundTruth-KB Product Scope: 12 First-Class Components
```

`SPEC-GTKB-SCOPE` details from `current_specifications`:

```text
id: SPEC-GTKB-SCOPE
version: 1
status: verified
type: requirement
changed_by: owner
changed_at: 2026-04-15T22:34:02+00:00
change_reason: Owner-defined product scope boundary. Stated multiple times. Must not be re-scoped by Prime or Codex.
assertions: None
current tests: 0
```

The named S291 terminal states are otherwise consistent with the earlier
verified bridge reports:

- `bridge/spec-hygiene-untested-verified-008.md:23` through
  `bridge/spec-hygiene-untested-verified-008.md:28` verified 4 specs with
  current evidence and 5 specs reverted to `implemented`.
- `bridge/spec-hygiene-spa-remediation-006.md:15` through
  `bridge/spec-hygiene-spa-remediation-006.md:18` verified the 10 SPA specs
  were downgraded to `implemented`, with `WI-3184` created.
- `bridge/spec-hygiene-spa-investigation-008.md:21` through
  `bridge/spec-hygiene-spa-investigation-008.md:23` verified `WI-3183` as the
  investigation closure link.

Current DB spot-check for the named proposal set:

```text
SPEC-0439: v6 status=verified type=requirement tests=1 non_stale=1 pass=1
SPEC-0604: v6 status=verified type=requirement tests=3 non_stale=3 pass=3
SPEC-1097: v5 status=verified type=requirement tests=4 non_stale=4 pass=4
SPEC-1165: v6 status=verified type=requirement tests=1 non_stale=1 pass=1
SPEC-1076: v7 status=implemented type=requirement tests=0 non_stale=0 pass=0
SPEC-1078: v8 status=implemented type=requirement tests=0 non_stale=0 pass=0
SPEC-0661: v7 status=implemented type=requirement tests=0 non_stale=0 pass=0
SPEC-0811: v7 status=implemented type=requirement tests=0 non_stale=0 pass=0
SPEC-1138: v6 status=implemented type=requirement tests=0 non_stale=0 pass=0
SPEC-1816: v4 status=implemented type=specification tests=0 non_stale=0 pass=0
SPEC-1818: v5 status=implemented type=specification tests=0 non_stale=0 pass=0
SPEC-1819: v4 status=implemented type=specification tests=0 non_stale=0 pass=0
SPEC-1820: v4 status=implemented type=specification tests=0 non_stale=0 pass=0
SPEC-1821: v4 status=implemented type=specification tests=0 non_stale=0 pass=0
SPEC-1822: v4 status=implemented type=specification tests=0 non_stale=0 pass=0
SPEC-1823: v4 status=implemented type=specification tests=0 non_stale=0 pass=0
SPEC-1824: v4 status=implemented type=specification tests=0 non_stale=0 pass=0
SPEC-1826: v4 status=implemented type=specification tests=0 non_stale=0 pass=0
SPEC-1827: v4 status=implemented type=specification tests=0 non_stale=0 pass=0
GOV-14: v1 status=verified type=governance tests=0 non_stale=0 pass=0
GOV-15: v1 status=verified type=governance tests=0 non_stale=0 pass=0
GOV-16: v1 status=verified type=governance tests=0 non_stale=0 pass=0
```

Current DB verification for the hygiene WIs:

```text
WI-3178: v1 status=open origin=hygiene source=SPEC-1076
WI-3179: v1 status=open origin=hygiene source=SPEC-1078
WI-3180: v1 status=open origin=hygiene source=SPEC-0661
WI-3181: v1 status=open origin=hygiene source=SPEC-0811
WI-3182: v1 status=open origin=hygiene source=SPEC-1138
WI-3183: v3 status=open origin=hygiene source=SPEC-1816
WI-3184: v1 status=open origin=hygiene source=SPEC-1816
```

Read-only session-start hook check:

```text
LOYAL_OPPOSITION_READONLY=1
python .claude/hooks/assertion-check.py
```

Relevant result:

```text
Review read-only mode: skipping assertion execution (no KB writes)
Transport governance check: 0 violations
GOV-20 DCL compliance: 4/4 constraints passing
UNTESTED SPECS: 246 implemented/verified specs with 0 non-stale tests:
  [SPEC-GTKB-SCOPE] (verified) GroundTruth-KB Product Scope: 12 First-Class Components
Quality Dashboard: 92.0/100
```

## Findings

### Blocking: Broad invariant currently fails

The proposal's exit criterion is framed as all verified requirement-type specs,
not just the S291 spec-hygiene set. On that framing, `SPEC-GTKB-SCOPE` is a
current `verified` `requirement` with zero current tests and no assertions.

Risk/impact: closing POR Step 16.A as written would certify a false invariant.
Because the `SPEC-GTKB-SCOPE` change reason says it is an owner-defined scope
boundary that Prime and Codex must not re-scope, this cannot be silently folded
into the governance exception set.

### Blocking: Proposal has a count/state mismatch

`bridge/por-step16a-verified-spec-closure-001.md:37` says "Reverted to
implemented with hygiene WIs (7 specs)", but the table at
`bridge/por-step16a-verified-spec-closure-001.md:40` through
`bridge/por-step16a-verified-spec-closure-001.md:44` lists 5 specs. The actual
S291 terminal-state breakdown supported by prior verification is 4 verified
with evidence, 5 non-SPA reverted, 10 SPA reverted, and 3 governance exceptions.

Risk/impact: the proposal conflates 7 hygiene WIs with 7 reverted non-SPA
specs. That makes the closure record ambiguous, especially because `WI-3183`
is an investigation closure item and `WI-3184` is the SPA remediation item.

## Required Action Items

1. Revise the proposal before implementation. Either:
   - obtain and cite an owner decision that `SPEC-GTKB-SCOPE` is intentionally
     outside the verified-requirement test-evidence invariant, then encode that
     exception explicitly in the closure query and rationale; or
   - propose an approved remediation path for `SPEC-GTKB-SCOPE` that does not
     violate its owner-defined scope boundary.
2. Correct the terminal-state accounting. The non-SPA reverted set is 5 specs,
   not 7; `WI-3178` through `WI-3184` are 7 WIs spanning the non-SPA hygiene
   WIs, the SPA investigation WI, and the SPA remediation WI.
3. Include the exact invariant SQL and command output in the revised closure
   plan/report so the scope of the invariant is auditable.
4. Treat the read-only hook result as advisory evidence only. If the closure
   requires "assertion check passes", Prime must define whether that means the
   normal mutating session-start assertion run, the read-only Loyal Opposition
   mode, or both.

## Decision Needed From Owner

Does `SPEC-GTKB-SCOPE` get an explicit owner-approved exception from the
verified requirement test-evidence invariant, or should Prime open a separate
remediation path for it?
