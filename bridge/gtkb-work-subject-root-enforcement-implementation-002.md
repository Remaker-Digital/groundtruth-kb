NO-GO

# GTKB Work Subject And Root Enforcement - Foundation Review

**Status:** NO-GO
**Date:** 2026-04-23
**Reviewed proposal:** `bridge/gtkb-work-subject-root-enforcement-implementation-001.md`

## Verdict

NO-GO on the proposal as written.

The first-slice boundary is directionally correct, and the distinction between
application product paths, current-repo bridge/governance paths, and GT-KB
product paths is the right problem to solve first. The blocker is the proposed
canonical state location: this slice moves ordinary runtime work-subject state
into `.groundtruth/`, which this repository already uses for governed artifacts
and approval evidence, but the proposal does not include a matching
ignore/durability contract.

## Prior Deliberations

- `DELIB-0876` recorded the owner directive for a durable session work-subject.
- `DELIB-0877` and `DELIB-0879` are the current GTKB/application-separation and
  root-topology planning records directly related to this slice.
- `DELIB-0244`, `DELIB-0216`, and `DELIB-0229` are older related work-subject /
  session-mode review records surfaced by the read-only `search_deliberations()`
  pass.
- No exact prior deliberation for `.groundtruth/session/work-subject.json` as
  the canonical runtime state path was surfaced.

## Blocking Finding

### F1 - Proposed canonical runtime state collides with the governed `.groundtruth/` tree

Severity: High

Evidence:

- The proposal makes `.groundtruth/session/work-subject.json` the new canonical
  state path: `bridge/gtkb-work-subject-root-enforcement-implementation-001.md:114-118`.
- The same proposal describes that file as lazily written runtime state during a
  migration window, not as a governed approval/spec artifact:
  `bridge/gtkb-work-subject-root-enforcement-implementation-001.md:135-143`.
- The current implementation stores this class of state under
  `.claude/hooks/.workstream-focus-state.json`:
  `scripts/workstream_focus.py:17`.
- `.gitignore` currently contains `.groundtruth-chroma/` but no
  `.groundtruth/session/` ignore rule:
  `rg -n "^\\.groundtruth/session/|^\\.groundtruth/|^\\.groundtruth-chroma/" .gitignore`
  -> only `.groundtruth-chroma/` at `.gitignore:113`.
- The repository already stores governed approval evidence under `.groundtruth/`,
  including
  `.groundtruth/formal-artifact-approvals/2026-04-22-artifact-oriented-governance.json`
  and
  `.groundtruth/formal-artifact-approvals/2026-04-22-core-spec-intake-phase0.json`.

Risk/impact:

As written, the first slice would place ephemeral operator/runtime state inside
the same top-level tree that already carries governed approval evidence and
other durable records. Without an explicit ignore rule or a stronger durability
contract, that creates immediate artifact confusion: the path looks governed,
but the proposal describes it as routine mutable runtime state.

Required action:

Revise the proposal so the canonical work-subject state either:

1. lives under an explicitly runtime-only ignored root, or
2. includes an explicit `.gitignore` carve-out and a clear contract explaining
   why `.groundtruth/session/` is safe for mutable runtime state while the rest
   of `.groundtruth/` remains governed/durable.

The revision should then restate the migration, startup, and guard behavior
against that corrected storage boundary.

## Non-Blocking Observations

- The proposed root classification split is otherwise sensible for a first slice.
- Preserving legacy aliases for one migration window is reasonable once the
  canonical storage boundary is corrected.

## Owner Decision Needed

None for this NO-GO.
