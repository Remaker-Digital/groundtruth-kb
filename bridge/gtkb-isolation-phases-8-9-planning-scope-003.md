REVISED

# GTKB-ISOLATION Phases 8 and 9 — Planning Scope Proposal Revision 1

**Status:** REVISED
**Prepared by:** Prime Builder
**Date:** 2026-04-23
**Supersedes:** `bridge/gtkb-isolation-phases-8-9-planning-scope-001.md`
**Addresses:** `bridge/gtkb-isolation-phases-8-9-planning-scope-002.md` (NO-GO)

bridge_kind: prime_proposal
scope: planning_scope
work_item_ids: [GTKB-ISOLATION-008, GTKB-ISOLATION-009]
target_paths: ["memory/work_list.md"]

## Requested Verdict

GO to produce two detailed phase plan documents
(`GTKB-ISOLATION-008-PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-YYYY-MM-DD.md`
and `GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-YYYY-MM-DD.md`)
in `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/` according to the
scope outlines below, which are aligned verbatim with the already-recorded
required coverage in
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md:645-684`.

Or NO-GO with required revisions.

## Change From Revision 0 (-001)

Revision 0 was NO-GO'd in `-002` for two blocking findings:

- **F1**: my Phase 9 outline replaced the approved scope
  (`gt project init`, `gt project upgrade`, managed artifact registry changes,
  doctor/preflight checks, clean-adopter tests, documentation, examples) with
  a broader `gt application scaffold`-centered concept, which would have
  allowed the Phase 9 plan to close without binding to the real GT-KB product
  surfaces already recorded as required follow-on work.
- **F2**: my Phase 8 outline talked about path rewrites in generic terms but
  did not explicitly require treatment of the mixed-state surfaces the
  inventory identified as the core separation work (`groundtruth.toml`,
  `tools/knowledge-db/groundtruth.toml`, `groundtruth.db`,
  MemBase specs/work items, `.groundtruth-chroma/`, `bridge/INDEX.md`,
  `memory/work_list.md`, `docs/gtkb-dashboard/`).

Revision 1 resolves both findings by:

1. Replacing the Phase 9 scope outline with the inventory's verbatim required
   coverage list and exit criteria.
2. Replacing the Phase 8 scope outline with the inventory's verbatim required
   coverage list and exit criteria, plus an explicit enumeration of every
   mixed-state surface from the Interdependency Classification table (inventory
   lines 228-243) that the Phase 8 detailed plan must treat individually.
3. Removing the prior `gt application scaffold <name>` reference. Phase 9
   planning will use the approved `gt project init` / `gt project upgrade`
   entrypoints. If a future `gt application scaffold` alias or wrapper is
   desired, it is a separate proposal and review outside this bridge.

## Prior Deliberations (per deliberation-protocol.md)

- `DELIB-0877` — parent owner decision, nine-phase program.
- `DELIB-0878` — Phase 1 authority matrix.
- `DELIB-0879` — Phase 2 root topology.
- NO-GO at `-002` is the direct prior for this thread.

## Scope Outline: Phase 8 — Agent Red Migration Rehearsal

### Purpose

Plan the safe extraction of Agent Red from the legacy mixed root. (Inventory
plan `:646`.)

### Required Coverage (verbatim from inventory `:648-656`)

The detailed Phase 8 plan must cover:

- dry-run copy/move inventory
- import/path rewrites
- CI/test command rewrites
- dashboard and MemBase path rewrites
- bridge/backlog split
- production deployment effects
- rollback plan

### Required Exit Criteria (verbatim from inventory `:658-663`)

- exact migration script strategy
- zero-destructive dry-run output
- verification matrix for application behavior and GT-KB conformance
- explicit list of artifacts that must not move

### Explicit Mixed-State Surface Coverage (resolving `-002` F2)

The detailed plan must treat **every** surface below individually, with a
named action (move / copy / split / stay / regenerate / deprecate),
authority classification per the Phase 1 matrix, and rationale. Source:
inventory Interdependency Classification table, lines 228-243.

| # | Surface | Inventory classification |
|---|---------|--------------------------|
| 1 | `groundtruth.toml` | C with B extensions |
| 2 | `tools/knowledge-db/groundtruth.toml` | B plus C |
| 3 | `groundtruth.db` | Split B/C |
| 4 | Deliberation Archive records in `groundtruth.db` | B/C |
| 5 | MemBase specs/work items in `groundtruth.db` | B/C |
| 6 | `.groundtruth/formal-artifact-approvals/` | C |
| 7 | `.groundtruth-chroma/` | D (cache/overlay) |
| 8 | `.claude/hooks/`, `.claude/rules/`, `.claude/skills/` | B/C/D hybrid |
| 9 | `.claude/settings.json`, `.codex/hooks.json` | C |
| 10 | `scripts/workstream_focus.py` | B/C transition |
| 11 | `.claude/hooks/workstream-focus.py` | B/C transition (retired S304/S305 per Phase 7) |
| 12 | `.claude/hooks/formal-artifact-approval-gate.py` | B/C transition |
| 13 | `bridge/INDEX.md` and `bridge/*.md` | C for app bridge, A/B for GT-KB bridge (bridge/backlog split) |
| 14 | `memory/work_list.md` | Split B/C (backlog split) |
| 15 | `memory/release-readiness.md` | C for app, A/B for GT-KB |
| 16 | `docs/gtkb-dashboard/` | B/D (service URL + overlay snapshots) |

For each surface the detailed plan must state: current location, target
location (or target service/overlay), migration action, transformation recipe
if applicable, rollback behavior, and post-migration verification.

### Additional Plan Sections (non-substitute for the above)

The detailed plan may extend beyond the required coverage with:

- Production deployment / CI pipeline concrete rewrites (Azure credentials,
  workspace names, hardcoded paths, deploy scripts)
- Windows Task Scheduler registrations (bridge-automation tasks, scheduled
  harvests) that reference the legacy path
- Git LFS cache transfer vs re-fetch tradeoff
- Secrets handling checklist (`.env`, Azure service principals, PyPI tokens)
- Owner decisions: exact target root path confirmation; migration-window
  policy; post-migration disposition of the legacy
  `Agent Red Customer Engagement` directory

## Scope Outline: Phase 9 — Adopter Packaging and Validation

### Purpose

Ensure the isolation model becomes a GT-KB product capability, not an Agent
Red-only workaround. (Inventory plan `:667-668`.)

### Required Coverage (verbatim from inventory `:670-677`)

The detailed Phase 9 plan must cover:

- `gt project init` and `gt project upgrade`
- managed artifact registry changes
- doctor/preflight checks
- clean-adopter tests
- documentation for normal users
- examples using application-only project roots

### Required Exit Criteria (verbatim from inventory `:679-684`)

- clean-adopter project defaults to application subject
- GT-KB product artifacts are unavailable for mutation from app-only roots
- app-local governed state still works
- service/overlay behavior is documented and tested

### Additional Plan Sections (non-substitute for the above)

The detailed plan may extend beyond the required coverage with:

- Adopter persona and use cases (new-adopter, existing-adopter,
  multi-app adopter) as context for documentation and examples
- Existing-adopter migration kit (a generalization of the Phase 8 rehearsal)
- Release and distribution strategy (which GT-KB version ships adopter
  tooling; backward-compatibility policy for pre-isolation installations)
- Owner decisions: mandatory vs opt-in isolation model; publicity and
  transition channels; post-Phase-9 acceptance gate

### Entrypoint Clarification (resolving `-002` F1 item 2)

The approved Phase 9 entrypoints are `gt project init` and `gt project
upgrade`. Revision 0's reference to a standalone `gt application scaffold
<name>` entrypoint is **withdrawn**. If such an alias or wrapper is later
desired, it will be a separate proposal with its own review; it is not part
of the Phase 9 scope approved by this bridge.

## Expected Outputs

When this proposal is GO'd and the follow-on planning work lands:

1. `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-008-PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-YYYY-MM-DD.md`
2. `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-YYYY-MM-DD.md`
3. Updates to `memory/work_list.md`:
   - `GTKB-ISOLATION-008` marked DONE (planning complete)
   - `GTKB-ISOLATION-009` marked DONE (planning complete)
   - New implementation work items added for Phase 8 migration execution
     and Phase 9 adopter tooling implementation
4. New plan-review bridge threads:
   - `gtkb-isolation-008-migration-plan-review`
   - `gtkb-isolation-009-adopter-packaging-plan-review`

This proposal does not request authorization to execute migration, scaffold
adopters, or modify GT-KB product source. Each of those requires its own
GO'd implementation bridge after the corresponding plan-review lands
VERIFIED.

## Review Focus

A GO on this revision authorizes only:
- Production of the two plan documents according to the required coverage,
  required exit criteria, and (for Phase 8) the 16 explicit mixed-state
  surface entries above.
- Associated `memory/work_list.md` updates.
- Filing the two plan-review bridge threads.

A NO-GO should identify:
- Additional surfaces or required-coverage items missed in the outlines
  above beyond what the inventory already enumerates.
- Scope items that remain inadequately bound to the inventory's recorded
  requirements.
- Objection to parallel Phase 8 + Phase 9 planning (preference for
  Phase 8 first, Phase 9 after).

## Non-Scope Reminder

Unchanged from `-001`. This proposal does not execute migration, produce
adopter tooling, change code, modify the live Agent Red directory, or
pre-commit to the exact target root path.

## Decision Needed From Owner

None. The Phase 9 entrypoint clarification (drop `gt application scaffold`
alias; use approved `gt project init` / `gt project upgrade`) is a
self-correction aligned with the already-approved Phase 9 basis. No new
owner decision is required for this revision.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
