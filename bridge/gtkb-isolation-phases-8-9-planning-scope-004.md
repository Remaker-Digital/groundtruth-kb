GO

# GTKB-ISOLATION Phases 8 and 9 Planning Scope Review

**Status:** GO
**Date:** 2026-04-23
**Reviewed proposal:** `bridge/gtkb-isolation-phases-8-9-planning-scope-003.md`

## Verdict

GO.

Revision 1 resolves the two blocking findings from `-002`. The Phase 8 and
Phase 9 scope outlines are now explicitly bound to the recorded backlog basis,
the inventory plan requirements, and the live GT-KB product entrypoints the
follow-on planning work must cover.

## Rationale

1. Phase 8 now restates the required coverage and exit criteria recorded in
   the inventory plan, then adds an explicit per-surface treatment requirement
   for the mixed-state paths that previously remained implicit.
2. Phase 9 now restores the required GT-KB productization surfaces
   (`gt project init`, `gt project upgrade`, doctor/preflight, registry
   changes, clean-adopter tests, docs, examples) instead of drifting to a new
   scaffold-specific concept.
3. The requested authorization remains correctly limited to producing two plan
   documents, updating `memory/work_list.md`, and filing the two follow-on
   plan-review bridge threads. It does not authorize migration execution or
   adopter-tooling delivery.

## Findings

### No blocking findings

Revision 1 is consistent with the currently recorded scope basis for
`GTKB-ISOLATION-008` and `GTKB-ISOLATION-009`.

### Informational note

The explicit mixed-state surface list includes
`.claude/hooks/workstream-focus.py` as a retired Phase 7 item. A read-only
path check in the current Agent Red workspace returned `False` for that file
while the other cited mixed-state surfaces still exist. That does not block
approval; it means the detailed Phase 8 plan should record it as already
retired/absent rather than as an active migration target.

## Evidence

- `bridge/gtkb-isolation-phases-8-9-planning-scope-003.md:45-56` replaces the
  earlier Phase 9 drift with the approved `gt project init` /
  `gt project upgrade` basis and withdraws the standalone scaffold entrypoint.
- `bridge/gtkb-isolation-phases-8-9-planning-scope-003.md:72-119` now matches
  the inventory's recorded Phase 8 coverage and exit criteria, then requires
  explicit handling for 16 mixed-state surfaces.
- `bridge/gtkb-isolation-phases-8-9-planning-scope-003.md:142-178` now matches
  the inventory's recorded Phase 9 coverage and exit criteria and binds the
  plan to the GT-KB product surfaces already in use.
- `memory/work_list.md:327-345` records the required outcomes for
  `GTKB-ISOLATION-008` and `GTKB-ISOLATION-009`, including dashboard/DB path
  handling, bridge/backlog split, `gt project init`, `gt project upgrade`,
  doctor/preflight checks, clean-adopter tests, docs, and examples.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md:228-243`
  defines the mixed-state surface inventory the revised Phase 8 scope now
  enumerates explicitly.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md:648-684`
  records the Phase 8 and Phase 9 required coverage and exit criteria that the
  revised proposal now mirrors.
- Read-only path check on 2026-04-23 in Agent Red confirmed these cited Phase 8
  surfaces exist: `groundtruth.toml`, `tools/knowledge-db/groundtruth.toml`,
  `groundtruth.db`, `.groundtruth/formal-artifact-approvals/`,
  `.groundtruth-chroma/`, `.claude/hooks/`, `.claude/rules/`,
  `.claude/skills/`, `.claude/settings.json`, `.codex/hooks.json`,
  `scripts/workstream_focus.py`, `.claude/hooks/formal-artifact-approval-gate.py`,
  `bridge/INDEX.md`, `memory/work_list.md`, `memory/release-readiness.md`, and
  `docs/gtkb-dashboard/`; `.claude/hooks/workstream-focus.py` is absent.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\README.md:55-60,122-124,183-184`
  shows the live GT-KB product surfaces the Phase 9 plan must address:
  `gt project init`, `gt project doctor`, and `gt project upgrade`.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\CHANGELOG.md:46-49,72-81,583-587`
  shows registry-driven upgrade behavior and continuing product investment in
  `gt project init`, `gt project doctor`, `gt project upgrade`, and
  adopter-tree ownership surfaces such as `groundtruth.toml`, `groundtruth.db`,
  `bridge/**/*.md`, and `memory/**/*.md`.

## Required Action Items Or Conditions

None.

## Decision Needed From Owner

None.
