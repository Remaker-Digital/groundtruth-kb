NEW

# GTKB-ISOLATION Phases 8 and 9 — Planning Scope Proposal

**Prepared by:** Prime Builder
**Date:** 2026-04-23
**Session:** S305

bridge_kind: proposal
scope: planning_scope
work_item_ids: [GTKB-ISOLATION-008, GTKB-ISOLATION-009]
target_paths: ["memory/work_list.md"]

## Requested Verdict

GO to produce two detailed phase plan documents
(`GTKB-ISOLATION-008-PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-YYYY-MM-DD.md`
and `GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-YYYY-MM-DD.md`)
in `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/` according to the
scope outlines below, matching the structure and depth established by the
Phase 1–7 plan documents (dated 2026-04-22 / 2026-04-23).

Once the plans land, separate plan-review bridges
(`gtkb-isolation-008-migration-plan-review` and
`gtkb-isolation-009-adopter-packaging-plan-review`) will follow the
established pattern for review, revision, and VERIFIED closure.

Or NO-GO with required revisions to the scope outlines below.

## Background

The GTKB-ISOLATION program (owner decision `DELIB-0877`, nine-phase plan) has
completed Phases 1–7 planning with all five planning reviews VERIFIED. Phase 3,
5, 6 baselines have landed on `main` with VERIFIED status. Phase 4 and Phase 7
implementation bridges are in flight (GO -008 and GO -012 respectively).

Phases 8 and 9 are named in the original nine-phase program but have not yet
been planned in detail. Work items `GTKB-ISOLATION-008` (migration rehearsal)
and `GTKB-ISOLATION-009` (adopter packaging and validation) exist as
placeholders in `memory/work_list.md` but have no corresponding plan
documents.

### Why file this now, with Phases 4 and 7 still in implementation

- Phase 8 (migration rehearsal) and Phase 9 (adopter packaging) are
  higher-risk than the preceding phases because they execute the full Agent
  Red cutover and make the isolation model reusable by downstream adopters.
  Late planning creates schedule risk.
- Certain Phase 8 inventory work can proceed in parallel with Phase 4 and
  Phase 7 implementation finishing — e.g., cataloguing current Agent Red
  artifact locations, enumerating deployment scripts and CI workflows, and
  mapping secrets is independent of the Phase 7 work-subject state
  contract.
- Phase 9 depends on Phase 8 completing, so front-loading Phase 9 scope
  definition reduces the risk of a serial plan-then-plan-then-execute chain
  at the end.

## Prior Deliberations (per deliberation-protocol.md)

- `DELIB-0877` — parent owner decision, nine-phase program.
- `DELIB-0878` — Phase 1 authority matrix (ownership / access model).
- `DELIB-0879` — Phase 2 root topology (target structure
  `E:\Claude-Playground\GT-KB\applications\Agent_Red` or the equivalent
  Phase 2 decision, to be confirmed in the Phase 8 plan).

No prior NO-GOs exist for Phases 8 or 9 specifically; this is the first
bridge on this scope.

## Scope Outline: Phase 8 — Agent Red Migration Rehearsal

### Purpose

Define the complete plan for migrating the existing Agent Red project from
`E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\` into
the target GTKB-ISOLATION layout (per `DELIB-0879`, e.g.,
`<GT-KB-root>\applications\Agent_Red\`), including dry-run rehearsal,
rollback, and acceptance criteria.

### Required Plan Sections

1. **Current-state inventory**
   - Exhaustive listing of Agent Red artifact classes at their current paths
   - Authority classification per the Phase 1 matrix (source, generated,
     provenance, secret, test fixture, CI config, deployment config)
   - Identification of cross-references to GT-KB infrastructure that must
     survive the move

2. **Target-state layout**
   - Concrete target path for each artifact class inside the
     `<GT-KB-root>/applications/Agent_Red/` subtree
   - GT-KB-provided services (package, scripts, hooks) referenced from the
     app subtree but not copied into it
   - Directory structure diagram

3. **Migration action classification**
   - Per artifact: `move`, `copy`, `transform`, `regenerate`, `delete`, or
     `leave-in-place` (for GT-KB-owned artifacts)
   - Transformation recipes for path rewrites inside artifacts (e.g.,
     CI config references to `Agent Red Customer Engagement` →
     `applications/Agent_Red`)

4. **Rehearsal procedure**
   - Sandboxed clone target (not the live working tree) for dry-run
   - Scripted migration tool vs. manual checklist tradeoff
   - Verification steps after dry-run: startup, tests, release gate,
     deploy scripts, dashboard generation

5. **Rollback plan**
   - Pre-migration snapshot mechanism (git tag + tar of untracked paths)
   - Criteria that trigger rollback
   - Rollback verification steps

6. **Risk register**
   - Secrets handling (credentials, `.env` files, Azure service principals)
   - CI/CD pipelines that reference absolute paths or workspace names
   - Deployment scripts with hardcoded paths
   - Test data and fixtures
   - Downstream dependencies (dashboards, release records, bridge-automation
     tasks registered with Windows Task Scheduler)
   - Concurrent-process invalidation (OS pollers, scheduled harvests,
     monitoring scripts)
   - Git LFS cache transfer vs. re-fetch tradeoff

7. **Acceptance criteria**
   - Specific test runs that must pass post-migration
   - Release-gate green on migrated tree
   - Dashboard generation succeeds against migrated paths
   - Bridge automation functional in migrated tree
   - One full Prime/LO bridge cycle successfully executed from migrated tree

8. **Owner decisions required**
   - Exact target root path confirmation (`E:\Claude-Playground\GT-KB\...`
     vs. any alternative)
   - Migration-window policy (pause all GT-KB operations during rehearsal?)
   - Post-migration handling of the legacy `Agent Red Customer Engagement`
     directory (archive / delete / repurpose)

## Scope Outline: Phase 9 — Adopter Packaging and Validation

### Purpose

Define the complete plan for making the GTKB-ISOLATION pattern reusable by
downstream GT-KB adopters. Agent Red is the reference implementation;
Phase 9 turns that reference into a repeatable template, scaffold, and
migration kit for others.

### Required Plan Sections

1. **Adopter persona and use cases**
   - New-adopter: installs GT-KB from scratch and scaffolds an application
     subdirectory
   - Existing-adopter: has an app that predates GTKB-ISOLATION and needs
     migration
   - Multi-app adopter: runs multiple applications as siblings under one
     GT-KB installation

2. **Scaffolding toolchain**
   - `gt application scaffold <name>` or equivalent CLI entrypoint
   - Application-root template (directory skeleton, starter rules, starter
     hooks, starter tests, starter bridge INDEX)
   - Authority matrix template per Phase 1
   - Topology template per Phase 2

3. **Installation and bootstrap documentation**
   - GT-KB package installation (PyPI or wheel)
   - Application-root creation under `<GT-KB-root>/applications/<name>/`
   - First-session bootstrap: operating role, bridge poller, startup report,
     dashboard scope

4. **Existing-adopter migration kit**
   - Adaptation of the Phase 8 rehearsal for generic adopters
   - Path-rewrite tool genericized beyond Agent Red
   - Migration validation suite

5. **Testing / validation matrix**
   - Scaffolded-app smoke suite (starts, runs bridge, generates dashboard)
   - Migration suite (for existing-adopter path)
   - Integration suite (app-subject operations do not touch product state;
     product-subject operations visible in app session per Phase 6 overlay)
   - Documentation-exercise suite (every documented step produces the
     described result)

6. **Release and distribution**
   - GT-KB version that ships adopter tooling
   - Documentation site / README updates
   - Backward-compatibility policy (pre-isolation GT-KB installations and
     their apps)

7. **Owner decisions required**
   - Whether GTKB-ISOLATION is the mandatory model for new adopters or an
     opt-in alternative
   - Timeline and channels for Agent Red transition publicity (if any)
   - Post-Phase-9 acceptance gate before closing the nine-phase program

## Expected Outputs

When this proposal is GO'd and the follow-on planning work lands:

1. `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-008-PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-YYYY-MM-DD.md`
2. `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-YYYY-MM-DD.md`
3. Updates to `memory/work_list.md`:
   - `GTKB-ISOLATION-008` marked DONE (planning complete)
   - `GTKB-ISOLATION-009` marked DONE (planning complete)
   - New implementation work items added for Phase 8 migration execution
     and Phase 9 adopter tooling implementation (numbers subject to
     standing-backlog hygiene)
4. New plan-review bridge threads:
   - `gtkb-isolation-008-migration-plan-review`
   - `gtkb-isolation-009-adopter-packaging-plan-review`

This proposal does **not** request authorization to execute the migration
or scaffold adopters. It only requests authorization to produce the two
plan documents. Migration execution and adopter toolchain delivery will
each require their own GO'd implementation bridges.

## Review Focus

A GO on this proposal authorizes only:
- Production of the two phase plan documents in the CODEX-INSIGHT-DROPBOX
  directory.
- Associated `memory/work_list.md` updates to reflect planning-complete
  status and to insert follow-on implementation work items.
- Filing the two plan-review bridge threads for Codex review.

A NO-GO should identify:
- Additional plan sections that should be in scope for Phase 8 or Phase 9
  beyond the outlines above.
- Sections that are out of scope and should be deferred further.
- Objection to doing Phase 8 and Phase 9 planning in parallel rather than
  serially (Phase 8 first, Phase 9 after).
- Preference for bundling Phases 8 and 9 into a single plan document
  rather than two separate documents.

## Non-Scope Reminder

This proposal does not:
- Execute the Agent Red migration.
- Produce adopter tooling.
- Make any code changes.
- Modify the live Agent Red directory structure.
- Pre-commit to the exact target root path (that is an owner decision
  inside the Phase 8 plan).
- Close out the in-flight Phase 4 and Phase 7 bridges.

## Decision Needed From Owner

None for this proposal. Phase-level target path and migration-window policy
decisions are scoped into the Phase 8 plan body itself per the "Owner
decisions required" section above.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
