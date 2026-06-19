NO-GO

bridge_kind: loyal_opposition_verdict
Document: gtkb-role-authority-interactive-persistence
Version: 002 (NO-GO)
Reviewer: Loyal Opposition (Codex, harness A session envelope)
Date: 2026-06-18 UTC
Responds-To: bridge/gtkb-role-authority-interactive-persistence-001.md
Work Item: WI-4668
Project: PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH

# Loyal Opposition Verdict: Role-Authority Interactive Persistence

## Verdict

NO-GO.

The proposal correctly captures the owner's new invariant, and the preflight
shape is clean. The implementation scope is not sufficient because it leaves
live, currently-specified artifacts and startup guidance carrying the opposite
rule: session role is invalidated at SessionStart / does not survive compaction
or resume. A new peer ADR/DCL plus a pointer is not enough while those older
governing artifacts remain unamended.

## Blocking Finding

### P1 - Current specified role-resolution artifacts directly contradict the proposed invariant

The owner's directive is that the transcript defines the interactive session
envelope and the designated role survives compaction, resume, and contiguous
SessionStart-like boundaries unless the owner explicitly changes it.

The proposal says it will add a peer ADR/DCL and retire `SPEC-INTAKE-a3cdef`,
but it does not amend or explicitly supersede the existing artifacts that say
the opposite:

- `GOV-SESSION-ROLE-AUTHORITY-001` currently says session-stated role persists
  in an ephemeral marker and is "lost across SessionStart events".
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` decision item 4 currently says
  "compaction or session resume reverts to durable until owner re-declares".
- `DCL-SESSION-ROLE-RESOLUTION-001` v2 currently has an explicit
  "Interactive resume after compaction" row resolving to durable when no marker
  is present, plus assertion 6 requiring the marker not survive SessionStart.

Those rows are not just stale prose; they are specified MemBase artifacts with
machine-checkable assertions. Leaving them in force while adding a peer DCL
creates two live specification authorities with incompatible behavior.

## Narrative-Surface Evidence

The proposed implementation only targets `.claude/rules/operating-role.md` with
a pointer. But current active guidance contains contradictory instructions:

- `CLAUDE.md:7` says the override lives in `.claude/session/active-session-role.json`
  and is invalidated by the next SessionStart.
- `AGENTS.md:91` says the same, and this file is active Codex guidance.
- `.claude/rules/operating-role.md:164` through `.claude/rules/operating-role.md:167`
  says the session-stated role is invalidated at next SessionStart and does not
  survive compaction or resume.
- `.claude/rules/canonical-terminology.md:786` through
  `.claude/rules/canonical-terminology.md:787` carries the same old definition.

Appending a pointer in only `.claude/rules/operating-role.md` would not make
"every agent" default to the corrected interpretation.

## Checks Run

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-role-authority-interactive-persistence --content-file bridge/gtkb-role-authority-interactive-persistence-001.md --json`
  - Result: pass; `preflight_passed: true`, `missing_required_specs: []`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-role-authority-interactive-persistence --content-file bridge/gtkb-role-authority-interactive-persistence-001.md`
  - Result: pass; 4 must-apply clauses, 0 blocking gaps.
- `python scripts/proposal_target_paths_coverage_preflight.py --content-file bridge/gtkb-role-authority-interactive-persistence-001.md --json --strict`
  - Result: clean; all implied paths covered for the proposal as written.
- `gt deliberations search "role authority interactive session persistence session envelope dispatcher registry hint" --limit 10`
  - Result: found the anchoring owner decision `DELIB-20265226` plus prior role-authority deliberations.
- Read-only MemBase query of `current_specifications` for
  `GOV-SESSION-ROLE-AUTHORITY-001`,
  `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`,
  `DCL-SESSION-ROLE-RESOLUTION-001`, and `SPEC-INTAKE-a3cdef`.
  - Result: the first three are currently `specified` and carry the old
    SessionStart/compaction fallback semantics; `SPEC-INTAKE-a3cdef` is
    currently `specified` with `description = null`.

## Required Revision

Revise the proposal so the implementation does one of these explicitly:

1. Amend the existing governing artifacts that contradict the new owner
   directive:
   - `GOV-SESSION-ROLE-AUTHORITY-001`
   - `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`
   - `DCL-SESSION-ROLE-RESOLUTION-001`

2. Or create the new ADR/DCL as explicit successors/superseders and retire or
   supersede the conflicting clauses in the older artifacts in the same
   governed ceremony.

The revised target paths must include the active narrative surfaces that will
otherwise continue to mislead agents:

- `CLAUDE.md`
- `AGENTS.md`
- `.claude/rules/operating-role.md`
- `.claude/rules/canonical-terminology.md`

The revised scope should replace the contradictory text, not merely append a
pointer.

## Non-Blocking Notes

- The dispatcher split itself is correct: registry role remains the source of
  truth for dispatch routing, while the interactive agent treats registry role
  only as fallback/hint when the transcript lacks explicit owner direction.
- The active PAUTH permits formal artifact mutation, spec retirement, and
  narrative artifact mutation, so the required revision appears authorization
  compatible.
- Retiring `SPEC-INTAKE-a3cdef` remains appropriate, but should happen only
  alongside the contradiction cleanup above.

## Dispatcher State Observed During Review

`gt bridge dispatch health --json` currently reports WARN, not PASS:

- `loyal-opposition:F last_result=unchanged with pending_count=30`
- malformed-status quarantine remains active for
  `gtkb-wi4232-bridge-index-drift-pb-classification`

`.gtkb-state/bridge-poller/dispatch-state.json` also shows current
`loyal-opposition:D` launch attempts failing due to `concurrency_cap_reached`.
That is not a blocker for this proposal verdict, but it remains dispatcher
drift to monitor.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
