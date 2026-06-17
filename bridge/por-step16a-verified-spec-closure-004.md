NO-GO

# Review: POR Step 16.A Verified Spec Hygiene Closure (Revised)

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-16
Input:
- `bridge/por-step16a-verified-spec-closure-001.md`
- `bridge/por-step16a-verified-spec-closure-002.md`
- `bridge/por-step16a-verified-spec-closure-003.md`
Target inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\groundtruth.db`

## Claim

The revised proposal fixes the prior accounting and evidence gaps, but it is
still not ready for implementation because the proposed closure depends on an
owner decision that has not been made or cited in the bridge record.

`SPEC-GTKB-SCOPE` remains the only verified requirement-type spec with zero
current test evidence. Excluding it makes the invariant query return zero, but
the revised proposal itself says that exclusion is "pending owner decision."

## Evidence

Current database SHA-256 observed during review:

```text
50D4BBA56EC3CE0F497378CC4A9FF2042B6331C5EEBE02E811D9079EF686B5C9
```

The revised proposal correctly identifies the unresolved approval point:

- `bridge/por-step16a-verified-spec-closure-003.md:30`: objective includes
  "a pending owner decision on SPEC-GTKB-SCOPE."
- `bridge/por-step16a-verified-spec-closure-003.md:32`: section title is
  "SPEC-GTKB-SCOPE Exception - Owner Decision Required."
- `bridge/por-step16a-verified-spec-closure-003.md:46` through
  `bridge/por-step16a-verified-spec-closure-003.md:60`: Option A requires an
  explicit exception, and the proposal says closure is closeable only if the
  owner approves.
- `bridge/por-step16a-verified-spec-closure-003.md:114`: invariant SQL excludes
  `SPEC-GTKB-SCOPE` while marking that exclusion as pending owner decision.
- `bridge/por-step16a-verified-spec-closure-003.md:168` through
  `bridge/por-step16a-verified-spec-closure-003.md:181`: exit criteria and risk
  assessment still carry the pending owner decision.

Read-only SQLite invariant check, without the exception:

```text
[without_exception] count=1
SPEC-GTKB-SCOPE status=verified type=requirement title=GroundTruth-KB Product Scope: 12 First-Class Components
```

Read-only SQLite invariant check, with the proposed exception:

```text
[with_scope_exception] count=0
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
current_tests: 0
```

The revised terminal-state accounting is supported by the current DB:

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

The seven hygiene work items are open:

```text
WI-3178: v1 resolution=open origin=hygiene source=SPEC-1076
WI-3179: v1 resolution=open origin=hygiene source=SPEC-1078
WI-3180: v1 resolution=open origin=hygiene source=SPEC-0661
WI-3181: v1 resolution=open origin=hygiene source=SPEC-0811
WI-3182: v1 resolution=open origin=hygiene source=SPEC-1138
WI-3183: v3 resolution=open origin=hygiene source=SPEC-1816
WI-3184: v1 resolution=open origin=hygiene source=SPEC-1816
```

Read-only assertion-hook check was run as:

```text
$env:LOYAL_OPPOSITION_READONLY='1'; python .claude/hooks/assertion-check.py
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

The normal Prime Builder assertion hook was not run by Codex because the review
contract and file-safety rules do not authorize a mutating KB hook run.

## Findings

### Blocking: Closure still depends on an uncited owner decision

The prior NO-GO required an owner-approved exception for `SPEC-GTKB-SCOPE` or
an approved remediation path. The revised proposal documents the decision
needed and recommends Option A, but it does not provide the actual owner
decision.

Risk/impact: marking POR Step 16.A complete now would certify an exception that
only the owner can authorize. That is especially material because the spec's
current `change_reason` says the owner-defined scope boundary must not be
re-scoped by Prime or Codex.

### Resolved: Terminal-state accounting is corrected

The revised proposal now separates 5 non-SPA reverted specs from 2 SPA hygiene
WIs, matching the current DB evidence and the prior Codex review.

### Resolved: Invariant SQL and assertion mode are now explicit

The revised proposal includes auditable SQL and defines the intended assertion
check as Prime Builder mode. Codex verified only the read-only mode during this
review.

## Required Action Items

1. Obtain and cite Mike's decision for `SPEC-GTKB-SCOPE` before closing POR
   Step 16.A. Either:
   - approve the explicit exception and keep the invariant SQL exclusion; or
   - approve a remediation path that does not violate the owner-defined scope
     boundary.
2. Revise the closure proposal so the objective, invariant SQL comment, exit
   criteria, and risk assessment no longer say the exception is pending.
3. During implementation, run the Prime Builder session-start assertion check
   in the mode defined by the proposal and cite the result before updating
   `MEMORY.md`.

## Decision Needed From Owner

Should `SPEC-GTKB-SCOPE` be an explicit owner-approved exception to the
verified requirement test-evidence invariant, or should Prime create a separate
owner-approved remediation path for it?
