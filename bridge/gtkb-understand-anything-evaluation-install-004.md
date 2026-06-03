NO-GO

# Loyal Opposition Review - Understand-Anything Evaluation Install REVISED-1

bridge_kind: loyal_opposition_verdict
Document: gtkb-understand-anything-evaluation-install
Version: 004
Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-06-03 UTC
Responds to: bridge/gtkb-understand-anything-evaluation-install-003.md
Verdict: NO-GO
Work Item: WI-4280

## Verdict

NO-GO.

The revision resolves the original target-path and graph-policy intent from
NO-GO `-002`, but the proposed ignore rule is broader than the stated
platform-root evaluation policy. `-003` says per-application graph commit
policy remains future/out of scope, yet it proposes an unanchored
`.understand-anything/` ignore entry that can also affect nested application
trees.

## Review Scope

- Read live `bridge/INDEX.md`; latest status was `REVISED:
  bridge/gtkb-understand-anything-evaluation-install-003.md`.
- Read `-001`, `-002`, and the current `-003` revision.
- Ran mandatory applicability and clause preflights against `-003`.
- Checked the proposed `.gitignore` pattern against local ignore behavior using
  the existing analogous `.gtkb-state/` directory ignore.
- Used a read-only sidecar review; it independently recommended the same narrow
  NO-GO.

## Positive Confirmations

- `-003` adds `.gitignore` to `target_paths`, closing the direct F1
  implementation-start path-scope defect from `-002`.
- `-003` explicitly selects an ignored platform-root `.understand-anything/`
  policy and keeps the per-application graph policy out of Slice 1 scope.
- Applicability preflight passed with no missing required specs.
- Clause applicability preflight passed with zero blocking gaps.
- The project, PAUTH, and WI metadata are present in the header.

## Finding

### P1 - Unanchored Ignore Rule Reaches Beyond Platform-Root Policy

Observation: `-003` states the selected policy is to gitignore the
platform-root `.understand-anything/` tree during the evaluation slice, but the
exact proposed `.gitignore` line is unanchored:

```text
.understand-anything/
```

Deficiency rationale: In Git ignore syntax, an unanchored directory pattern can
match that directory name below nested paths, not only at the repository root.
That is wider than the proposal's policy language. The proposal explicitly says
the future per-application graph commit policy remains out of scope, so the
Slice 1 ignore rule should not accidentally make a per-application decision.

Evidence:

- `bridge/gtkb-understand-anything-evaluation-install-003.md` line 52 says the
  platform-root `.understand-anything/` tree is ignored and that
  per-application graph commit policy remains future/out of scope.
- `bridge/gtkb-understand-anything-evaluation-install-003.md` lines 75-81
  propose the exact `.gitignore` line `.understand-anything/`.
- `bridge/gtkb-understand-anything-evaluation-install-003.md` lines 152-164
  only verify substring presence and root `.understand-anything/` tracked-file
  absence; they do not verify root anchoring or nested application behavior.
- Local analogous evidence: existing `.gitignore` line 510 is `.gtkb-state/`;
  `git check-ignore -v --no-index .gtkb-state\sentinel.txt
  applications\example\.gtkb-state\sentinel.txt` reports both paths matched by
  `.gitignore:510:.gtkb-state/`.

Impact: A GO would authorize a `.gitignore` pattern that may suppress future
application-scoped UA graph artifacts even though that policy is explicitly
deferred. This over-implements the evaluation slice and weakens the audit
boundary between platform-root evaluation and future application adoption.

## Required Revision

File `REVISED -005` that:

1. Changes the proposed `.gitignore` line to root-anchored
   `/.understand-anything/`.
2. Updates the F1 verification command to require that exact anchored entry,
   not merely substring presence of `.understand-anything/`.
3. Keeps the existing no-tracked-root-artifact verification for F2.

No new owner decision appears necessary for this narrow correction.

## Commands Executed

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-understand-anything-evaluation-install
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-understand-anything-evaluation-install
git check-ignore -v --no-index .gtkb-state\sentinel.txt applications\example\.gtkb-state\sentinel.txt
```
