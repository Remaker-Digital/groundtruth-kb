NO-GO

# GTKB-ISOLATION Phases 8 and 9 Planning Scope Review

**Status:** NO-GO
**Date:** 2026-04-23
**Reviewed proposal:** `bridge/gtkb-isolation-phases-8-9-planning-scope-001.md`

## Verdict

NO-GO.

The proposal is correctly bounded to planning work and it is supported by
existing backlog placeholders plus completed Phase 1 through Phase 7 planning
artifacts. However, the proposed scope cannot be approved as written because it
does not yet preserve the already-recorded required outcomes for Phase 9, and
it leaves Phase 8's highest-risk mixed-state surfaces implicit rather than
explicitly required.

## Findings

### F1 - Blocking: Phase 9 scope does not explicitly cover the required GT-KB productization surfaces

The approved planning basis for `GTKB-ISOLATION-009` requires the detailed plan
to cover existing GT-KB product entrypoints and adoption mechanisms:
`gt project init`, `gt project upgrade`, managed artifact registry changes,
doctor/preflight checks, clean-adopter tests, application-only project-root
documentation, and examples.

The proposal replaces that explicit scope with a broader scaffold/tooling
concept centered on ``gt application scaffold <name>`` or an equivalent
entrypoint. That substitution is not safe as written. It would allow the Phase
9 plan to close without proving how the isolation model lands in the actual
GT-KB surfaces already recorded as required follow-on work.

### F2 - Blocking: Phase 8 scope leaves mixed DB, bridge, backlog, and dashboard separation as inferred rather than required

The Phase 8 planning basis already says the detailed migration-rehearsal plan
must cover dashboard and MemBase path rewrites, bridge/backlog split, and
production deployment effects. The proposal mentions generic path rewrites,
dashboard generation, deploy scripts, and bridge automation, but it does not
explicitly require treatment of the mixed-state surfaces that the earlier
inventory identified as core separation work: `groundtruth.toml`,
`tools/knowledge-db/groundtruth.toml`, `groundtruth.db`, MemBase/work-item
state, `bridge/INDEX.md`, `memory/work_list.md`, and `docs/gtkb-dashboard/`.

That omission is material because those are exactly the surfaces where the
current mixed-root model still combines application-governed and GT-KB product
state.

## Evidence

- `memory/work_list.md:327-345` records `GTKB-ISOLATION-008` and
  `GTKB-ISOLATION-009` as standing work items and defines their required
  outcomes.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md:650-677`
  requires Phase 8 to cover import/path rewrites, CI/test command rewrites,
  dashboard and MemBase path rewrites, bridge/backlog split, production
  deployment effects, rollback, and requires Phase 9 to cover `gt project
  init`, `gt project upgrade`, managed artifact registry changes,
  doctor/preflight checks, clean-adopter tests, documentation, and examples.
- `bridge/gtkb-isolation-phases-8-9-planning-scope-001.md:95-129` defines the
  proposed Phase 8 sections. Those sections do not explicitly require
  `groundtruth.toml` / `groundtruth.db` / MemBase handling or bridge/backlog
  split planning.
- `bridge/gtkb-isolation-phases-8-9-planning-scope-001.md:157-187` defines the
  proposed Phase 9 sections around scaffolding, bootstrap docs, migration kit,
  validation, and release/distribution, but does not explicitly bind the plan
  to `gt project init`, `gt project upgrade`, managed artifact registry
  changes, or doctor/preflight checks.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md:228-243`
  identifies the mixed surfaces that need explicit separation treatment:
  `groundtruth.toml`, `tools/knowledge-db/groundtruth.toml`, `groundtruth.db`,
  MemBase specs/work items, `.groundtruth-chroma/`, `bridge/INDEX.md`,
  `memory/work_list.md`, and `docs/gtkb-dashboard/`.
- Read-only inspection on 2026-04-23 confirmed that the current Agent Red
  workspace contains the referenced `memory/work_list.md` and the seven Phase
  1 through Phase 7 plan documents, while the separate upstream
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` checkout does not host
  the cited `memory/` or `independent-progress-assessments/` paths. That makes
  it more important for the proposal to state the GT-KB product-facing surfaces
  explicitly when defining Phase 9 scope.

## Required Action Items

1. Revise the Phase 9 scope outline so it explicitly requires planning for
   `gt project init`, `gt project upgrade`, managed artifact registry changes,
   doctor/preflight checks, clean-adopter tests/fixtures, application-only
   project-root documentation, and examples.
2. If the plan still wants a `gt application scaffold` entrypoint, state
   whether it is merely an alias/wrapper over the approved `gt project init`
   and `gt project upgrade` surfaces or a separate future proposal requiring
   its own review.
3. Revise the Phase 8 scope outline so it explicitly requires planning for
   `groundtruth.toml`, `tools/knowledge-db/groundtruth.toml`, `groundtruth.db`,
   MemBase/work-item state, `.groundtruth-chroma/`, bridge split, backlog
   split, dashboard split, and production deployment effects.
4. Refile the planning-scope bridge after those additions are incorporated.

## Decision Needed From Owner

None.
