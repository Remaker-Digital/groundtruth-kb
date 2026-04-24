NEW

# GTKB-ISOLATION-008 Phase 8 Migration Rehearsal Plan Review

**Status:** NEW
**Prepared by:** Prime Builder
**Date:** 2026-04-23

bridge_kind: plan_review
scope: plan_review
work_item_ids: [GTKB-ISOLATION-008, GTKB-ISOLATION-016]
target_paths:
  - "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-008-PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-2026-04-23.md"

## Requested Verdict

GO to accept the Phase 8 migration rehearsal plan as the authoritative
planning basis for a later implementation bridge that executes the
non-destructive rehearsal (`GTKB-ISOLATION-016`).

Or NO-GO with required revisions.

## Planning Authorization

The upstream planning-scope bridge
`bridge/gtkb-isolation-phases-8-9-planning-scope-004.md` (GO, 2026-04-23)
authorized production of this plan document plus the companion Phase 9 plan
and the filing of this review thread and the companion Phase 9 review
thread. This review is the scoped follow-on required by that GO.

## Plan Under Review

`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-008-PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-2026-04-23.md`.

## Prior Deliberations (per deliberation-protocol.md)

- `bridge/gtkb-isolation-phases-8-9-planning-scope-001.md` (NEW)
- `bridge/gtkb-isolation-phases-8-9-planning-scope-002.md` (NO-GO — F1 Phase 9
  scope drift, F2 Phase 8 missing mixed-state surface enumeration)
- `bridge/gtkb-isolation-phases-8-9-planning-scope-003.md` (REVISED resolving
  both findings)
- `bridge/gtkb-isolation-phases-8-9-planning-scope-004.md` (GO)
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md`
  (inventory and phase plan)
- `DELIB-0877` — parent owner decision, nine-phase program
- `DELIB-0878` — Phase 1 authority matrix
- `DELIB-0879` — Phase 2 root topology

## Review Focus

Review the Phase 8 plan against the inventory's required coverage
(`:648-656`), required exit criteria (`:658-663`), and the 16 mixed-state
surface entries from the Interdependency Classification table (`:228-243`).
Confirm:

1. All seven required-coverage items are bound to concrete rehearsal
   artifacts (`dryrun-inventory.json`, `path-rewrite-map.json`,
   `path-rewrite-preview.diff`, `ci-command-inventory.csv`,
   `ci-rewrite-preview.md`, `bridge-split-plan.md`,
   `production-effects-map.md`, `rollback-manifest.md`).
2. All four exit criteria are bound to concrete acceptance checks.
3. Each of the 16 mixed-state surfaces in the matrix carries a named
   action, authority classification, transformation recipe, rollback
   behavior, and post-migration verification.
4. Surface 11 (`.claude/hooks/workstream-focus.py`) is recorded as
   retired/absent rather than as an active migration target.
5. The plan is planning-only and does not authorize execution of the
   rehearsal, cutover, or any production-affecting rewrite.
6. The explicit list of artifacts that must not move under exit criterion
   4 covers `groundtruth.db` as a unit, production Azure container apps,
   ACS numbers, Key Vault contents, live secrets, GT-KB product source,
   and git history at either root.
7. The regression visibility section defines tests for zero-destructive
   default, subject-scoped CI/startup/dashboard lanes, bridge/backlog
   split correctness, rollback manifest completeness, and the negative
   presence assertion for the retired hook.

A NO-GO should identify:

- Required coverage or exit-criterion items not bound to concrete
  deliverables.
- Mixed-state surfaces whose treatment is ambiguous or conflicts with
  Phase 1 authority classifications.
- Authorization scope creep (plan language that attempts to authorize
  execution rather than planning).
- Cross-phase dependency gaps (Phase 1-7 artifacts the plan assumes but
  does not reference).
- Missing open decisions the implementation bridge must surface to the
  owner before starting.

## Non-Scope

This review does not authorize the implementation bridge that will
execute the rehearsal (`GTKB-ISOLATION-016`), nor the cutover
(`GTKB-ISOLATION-018`), nor any modification of the legacy mixed root,
the GT-KB product root, or production Agent Red environments. Each of
those requires its own bridge and, where applicable, GOV-16 approval.

## Decision Needed From Owner

None for this review. The planning-scope GO at
`bridge/gtkb-isolation-phases-8-9-planning-scope-004.md` already covers
the open decisions at this level. Owner decisions about exact target
child root path, migration window, and post-rehearsal disposition of the
legacy mixed root are documented as "Open Decisions For The Implementation
Bridge" inside the plan and will surface at the implementation bridge,
not here.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
