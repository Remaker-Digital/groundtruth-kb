# Implementation Proposal - First-Class Project Artifacts And Subject Workflow Model

**Document:** `gtkb-first-class-project-artifacts`
**Status:** `NEW`
**Version:** 001
**Date:** 2026-05-12
**Author:** Prime Builder (Codex, harness A)
**Bridge kind:** implementation_proposal
**Active workspace:** `E:\GT-KB`
**Recommended commit type:** `feat:`

## Claim

GT-KB currently uses `project` as an important operating-model term, but it does not implement projects as first-class lifecycle artifacts. The backlog is represented primarily by MemBase `work_items` / `current_work_items`, with project identity stored as denormalized `project_name` and `subproject_name` fields. This makes the owner's intended workflow harder to express: a subject is evolved through one or more projects, projects are stack-ranked in the backlog, and work items may participate in multiple projects because of sequencing, interoperability, or dependency relationships.

This proposal requests Loyal Opposition review for a phased implementation that introduces first-class project artifacts, formalizes the subject/project/work-item vocabulary, and migrates backlog reporting away from string-grouped project names while preserving compatibility for existing work-item data.

## Specification Links

This proposal is governed by, and should be reviewed against, the following active or planned authority surfaces:

- `.claude/rules/operating-model.md` - current canonical operating-model artifact, including definitions for application, project, sub-project, work item, backlog, specification, implementation proposal, implementation report, verification, release, MemBase, Deliberation Archive, and dashboard.
- `.claude/rules/canonical-terminology.md` - active terminology rule used by startup and validation.
- `config/agent-control/system-interface-map.toml` - declares authoritative backlog interfaces and currently points backlog authority to MemBase `current_work_items`.
- `groundtruth-kb/src/groundtruth_kb/db.py` - current MemBase schema implementation; `work_items` include `project_name`, `subproject_name`, dependency fields, bridge links, and deliberation links, but no first-class `projects` or `subjects` tables.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge review is the implementation handoff authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation proposals require explicit specification linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation must include spec-derived verification where applicable.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - concrete work planning should preserve durable artifacts when it crosses from brainstorming into decisions, plans, requirements, or accepted future work.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - artifact-oriented development is the governing implementation posture.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - lifecycle-trigger criteria apply when owner input becomes formal work.
- `GOV-STANDING-BACKLOG-001`, `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001`, `PB-STANDING-BACKLOG-CONTINUITY-001` - the standing backlog is governed cross-session work authority.
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001`, `DCL-STANDING-BACKLOG-DB-SCHEMA-001`, `DCL-STANDING-BACKLOG-SCHEMA-001` - current and planned backlog database authority that this proposal must reconcile with, not bypass.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - subject/project terminology must not collapse the GT-KB platform, hosted applications, demo applications, or Agent Red into one filesystem or release lifecycle.
- `GOV-ARTIFACT-APPROVAL-001`, `PB-ARTIFACT-APPROVAL-001` - formal artifact mutations remain subject to approval-gated governance.

## Prior Deliberations

Deliberation archive search was performed on 2026-05-12 using MemBase queries for first-class projects, backlog DB authority, project lifecycle artifacts, and work-item membership/dependencies. Relevant prior records:

- `DELIB-1791` - Loyal Opposition review of the GTKB backlog source-of-truth scoping proposal. Relevant because it critiques backlog authority and project/work-list source-of-truth claims.
- `DELIB-1790` - Loyal Opposition review of the revised backlog source-of-truth scoping proposal. Relevant because this proposal extends the same backlog authority line rather than creating an unrelated planning surface.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - owner directive for formal backlog DB schema work. Relevant because first-class projects must be integrated with, or deliberately supersede part of, the existing backlog DB schema direction.
- `DELIB-0838` - owner decision on standing backlog governed cross-session work authority. Relevant because project artifacts become a first-class organizing layer for that authority.
- `DELIB-0839` - standing backlog harvest snapshot and reconciliation obligations. Relevant because migration must preserve existing backlog items and avoid orphaned work.
- `DELIB-0874` - owner decision on artifact-oriented development governance. Relevant because subject/project/work-item terms are lifecycle artifacts, not only labels.
- `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE` - owner directive about backlog-consideration implementation. Relevant because implementation must distinguish future-work candidates from implementation-approved work.
- `DELIB-1583` - Loyal Opposition review of the backlog work-list retirement directive. Relevant because this proposal should not revive retired file-backed backlog authority.

## Owner Decisions And Input

The owner has stated the following working model in chat on 2026-05-12:

- A `Subject` is the conceptual thing being implemented and evolved using software artifacts, such as GT-KB, Agent Red, or another application.
- A subject is implemented, evolved, and maintained through one or more time-oriented `Projects`.
- Projects are part of the stack-ranked `Backlog`.
- The backlog may contain multiple projects; each project may contain multiple work items or sub-projects.
- Work items may be members of multiple projects to reflect build order and interoperation dependencies.
- Bridge threads and deliberations are approved evidence/control artifacts associated with implementation and planning work.
- The owner suspects GT-KB does not currently handle projects as first-class artifacts and asked Prime Builder to create an implementation proposal and begin planning implementation.

This chat input is sufficient owner direction to create this bridge proposal. It is not treated as formal approval for GOV, ADR, DCL, SPEC, rule, or schema mutations that require explicit approval evidence. Those mutations remain gated by the applicable artifact-approval and bridge-review rules.

## Bulk-Operation Visibility And Deferred Decisions

This proposal is the review packet for a project/backlog model change that may require bulk migration of existing `project_name` and `subproject_name` data. Slice 1 must produce an inventory artifact before backfill, covering distinct current project strings, subproject strings, implied project candidates, existing work-item dependencies, existing bridge links, and existing deliberation links.

DECISION DEFERRED: the implementation must not bulk-convert backlog records, retire compatibility fields, or mutate formal GOV/ADR/DCL/SPEC/rule artifacts until the applicable slice produces its inventory artifact, migration review packet, and formal-artifact-approval evidence where required.

## Current-State Evidence

- `work_items` and `current_work_items` are the active MemBase backlog surfaces. They contain `project_name` and `subproject_name`, but do not model project identity, lifecycle state, ownership, rank, dependencies, or artifact links as first-class rows.
- `config/agent-control/system-interface-map.toml` declares `current_work_items` as the authoritative backlog read interface and marks `memory/work_list.md` compatibility-only.
- `.claude/rules/operating-model.md` already defines `project` as a named grouping of related known work in the standing backlog, but the implementation does not provide a corresponding project table or current-project view.
- `.claude/rules/canonical-terminology.md` contains a useful but inconsistent hierarchy: `backlog -> projects -> sub-projects -> work items`, while also stating that all backlog items are work items. The first-class project model should resolve that ambiguity.
- Existing backlog DB authority work is specified or proposed, but it still centers backlog storage on work items/backlog items. It does not fully express subjects, project lifecycle, many-to-many work-item membership, cross-project dependencies, or project-to-artifact evidence links.

## Proposed Canonical Model

Introduce these normalized concepts:

- `Subject`: the owner-facing conceptual target that GT-KB helps build, evolve, or maintain. A subject may correspond to the platform, a hosted application, a demo application, or a separately governed application. `Subject` should be mapped carefully to the existing `application` term rather than replacing it blindly.
- `Project`: a first-class, time-oriented lifecycle container that advances one subject or a bounded cross-subject initiative. Projects have rank, status, purpose, subject association, start/target dates when known, and explicit dependencies.
- `Sub-project` or `milestone`: a project-local planning subdivision. This should remain optional and subordinate to project identity.
- `Work item`: an atomic or near-atomic unit of governed work. A work item can belong to zero, one, or many projects through a membership table.
- `Backlog entry`: the rankable queue representation. Backlog entries may rank projects and work items, but the implementation must make clear whether the primary stack rank is project-level, work-item-level, or both.
- `Bridge thread`: implementation-review control artifact linked to one or more projects/work items. It is not itself the work item.
- `Deliberation`: planning or decision evidence linked to subjects, projects, or work items. It is not itself the work item unless an explicit work item is created to act on it.

## Proposed Schema Direction

Implement append-friendly MemBase tables and current views consistent with existing DB patterns:

- `subjects`
  - Stable subject identity, name, type, status, description, repository/root hints, created/updated metadata.
  - `current_subjects` view selecting the latest active row per subject.
- `projects`
  - Stable project identity, subject identity, project name, status, rank, purpose, target outcome, lifecycle dates, owner notes, created/updated metadata.
  - `current_projects` view selecting the latest active row per project.
- `project_work_item_memberships`
  - Many-to-many membership between projects and work items, with role such as `primary`, `dependency`, `enabler`, `followup`, or `blocked_by_context`.
  - Membership status and ordering so a work item can be intentionally shared across projects without duplicating the work item.
- `project_dependencies`
  - Project-to-project dependencies with type, rationale, blocking status, and optional linked work item.
- `project_artifact_links`
  - Links from projects to bridge documents, deliberations, specs, ADRs, DCLs, implementation reports, verification runs, and release blockers.
- Compatibility migration fields/views
  - Preserve existing `work_items.project_name` and `work_items.subproject_name` as non-authoritative compatibility fields until consumers are migrated.
  - Add views or migration helpers that derive project memberships from existing project strings without data loss.

The implementation should decide during detailed design whether `backlog_items` becomes a rankable queue table over `projects` and `work_items`, or whether `projects.rank` plus `project_work_item_memberships.order_index` is sufficient. That decision must reconcile with `DCL-STANDING-BACKLOG-DB-SCHEMA-001` and the existing backlog DB direction.

## Proposed Implementation Plan

### Slice 1 - Model Foundation And Compatibility

- Add schema definitions for subjects, projects, project memberships, project dependencies, project artifact links, and current views.
- Add deterministic migration/backfill logic from existing `current_work_items.project_name` and `subproject_name` values.
- Preserve existing work-item reads and writes while introducing new project-aware APIs.
- Add tests for schema creation, current views, migration idempotence, many-to-many membership, and compatibility reads.

### Slice 2 - CLI And Reporting Surface

- Add project-aware commands or command options for listing projects, showing a project, listing project work items, and showing dependencies/artifact links.
- Update backlog reporting so project grouping comes from `current_projects` and membership views instead of string grouping on `current_work_items.project_name`.
- Update startup/current-state reporting to distinguish active projects, project statuses, project ranks, and project-blocking dependencies.

### Slice 3 - Governance And Glossary Alignment

- Update canonical terminology and operating-model text after owner/governance approval to make `Subject`, `Project`, `Work item`, `Backlog entry`, `Bridge thread`, and `Deliberation` unambiguous.
- Update `config/agent-control/system-interface-map.toml` to name authoritative project/backlog read and write interfaces.
- If needed, add or update GOV/ADR/DCL/SPEC records through the formal approval path instead of embedding durable policy only in markdown prose.

### Slice 4 - Dashboard And Release Integration

- Update dashboards and release-readiness reports to show project-level backlog, cross-project dependencies, linked bridge state, linked deliberation/spec evidence, and project-level blockers.
- Add assertions that prevent orphaned project memberships, unknown subject references, stale project string authority, and unlinked implementation proposals for project-affecting work.

## Acceptance Criteria

- Projects are represented by stable first-class MemBase rows and current views, not only by `project_name` strings on work items.
- A work item can belong to multiple projects without duplication or ambiguity.
- Cross-project dependencies are queryable independently of work-item dependencies.
- Bridge threads and deliberations can be linked to projects as evidence/control artifacts without being mislabeled as work items.
- Existing backlog consumers continue to work during migration, and compatibility fields are explicitly documented as non-authoritative.
- Backlog reports can group and prioritize by first-class project identity and surface cross-project dependencies.
- Canonical terminology no longer conflicts over whether backlog contains projects, work items, or both.
- Tests cover schema creation, migration/backfill, current views, many-to-many memberships, dependency queries, and reporting behavior.

## Risk And Mitigation

- **Risk:** This change touches both governance vocabulary and database structure, creating a high chance of partial migration.
  **Mitigation:** Implement in slices with compatibility views and explicit preflight/test coverage before retiring old string-grouping behavior.

- **Risk:** Introducing `Subject` may conflict with the existing `application` term and platform/application isolation rules.
  **Mitigation:** Define `Subject` as an owner-facing conceptual planning target and map it to existing application/platform terms, rather than replacing `application` in deployment/release contexts.

- **Risk:** Existing backlog DB schema direction may conflict with the proposed project model.
  **Mitigation:** Treat the project model as a reconciliation layer over standing backlog DB authority and update or supersede narrower backlog-schema records only through formal approval.

- **Risk:** Many-to-many project membership could make ranking ambiguous.
  **Mitigation:** Separate project-level rank, membership ordering, and work-item dependency/blocking relationships, then expose each explicitly in CLI/reporting.

## Out Of Scope

- Retiring `memory/work_list.md` beyond its current compatibility status.
- Treating Agent Red repository files as live GT-KB artifacts.
- Replacing the existing `application` term in release/deployment governance.
- Mutating formal GOV, ADR, DCL, SPEC, or rule artifacts without the required approval evidence.
- Implementing production deployment or release changes.

## Verification Plan

- Run bridge applicability preflight for this proposal after filing.
- Run ADR/DCL clause preflight for this proposal after filing.
- For implementation slices, run targeted MemBase schema/unit tests and project-aware reporting tests.
- Run repo-native checks appropriate to touched files, expected minimum:
  - `python -m pytest -q --tb=short`
  - `python -m ruff check .`
  - `python -m ruff format --check .`
- Add migration-specific tests proving existing `current_work_items.project_name` data is preserved and mapped into project memberships.

## Decision Requested From Loyal Opposition

Return `GO` if this phased proposal is sufficiently scoped and specification-linked to begin implementation planning and Slice 1 design. Return `NO-GO` with required corrections if the proposal needs a narrower scope, additional specification linkage, formal owner approval evidence, or a different boundary between subject, application, project, backlog entry, and work item.
