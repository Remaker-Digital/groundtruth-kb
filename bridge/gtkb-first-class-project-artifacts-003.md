REVISED

# Implementation Proposal - First-Class Project Artifacts Without Backlog Authority Drift

**Document:** `gtkb-first-class-project-artifacts`
**Status:** `REVISED`
**Version:** 003
**Date:** 2026-05-12
**Author:** Prime Builder (Codex, harness A)
**Bridge kind:** implementation_proposal
**Active workspace:** `E:\GT-KB`
**Recommended commit type:** `feat:`

## Revision Summary

This revision addresses the three blocking findings from `bridge/gtkb-first-class-project-artifacts-002.md`.

- F1 closed: `work_items` / `current_work_items` is now explicit, non-negotiable backlog authority for this proposal. No `backlog_items` table, queue, or authority path is proposed.
- F2 closed: the owner-input section now uses the exact required heading `## Owner Decisions / Input`.
- F3 closed: `Subject` is no longer part of Slice 1 schema implementation. Slice 1 is limited to first-class `projects` and project/work-item relationships over the existing backlog authority. Any future `Subject` table or terminology mutation requires a prior terminology/governance slice and applicable approval evidence.

## Bridge INDEX Canonicalness Evidence

This revised bridge artifact is filed under `bridge/` at `bridge/gtkb-first-class-project-artifacts-003.md`. The `bridge/INDEX.md` update inserts `REVISED: bridge/gtkb-first-class-project-artifacts-003.md` at the top of the existing document entry, above `NO-GO: bridge/gtkb-first-class-project-artifacts-002.md` and `NEW: bridge/gtkb-first-class-project-artifacts-001.md`. No prior bridge version is deleted or rewritten.

## Claim

GT-KB should represent projects as first-class lifecycle artifacts because the owner wants backlog work to be organized as projects containing work items and sub-projects, with explicit project rank, dependencies, and evidence links.

The implementation must not reopen the settled backlog-authority pivot. The canonical backlog work records remain MemBase `work_items` and `current_work_items`. Projects are an organizing and planning layer over those work items, not a replacement backlog authority and not a separate `backlog_items` table.

## Specification Links

- `.claude/rules/operating-model.md` - current canonical operating-model artifact, including `application`, `project`, `sub-project`, `work item`, `backlog`, `specification`, `implementation proposal`, `implementation report`, `verification`, `release`, `MemBase`, `Deliberation Archive`, and `dashboard`.
- `.claude/rules/canonical-terminology.md` - active terminology rule, including existing `work subject` startup-payload terminology that must not be silently replaced by a schema-level `Subject` concept.
- `config/agent-control/system-interface-map.toml` - declares authoritative backlog interfaces and currently points backlog authority to MemBase `current_work_items`.
- `groundtruth-kb/src/groundtruth_kb/db.py` - current MemBase schema implementation; `work_items` and `current_work_items` are the live backlog work-record surfaces.
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v3 - canonical backlog authority is `current_work_items` backed by append-only `work_items`; v3 supersedes prior `backlog_items` table references.
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v3 - backlog metadata is represented on `work_items`; `current_work_items` is the canonical backlog query surface.
- `GOV-STANDING-BACKLOG-001` v4 - post-migration implementation surface is `work_items` / `current_work_items`; `backlog_items` never existed in MemBase.
- `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001`, `PB-STANDING-BACKLOG-CONTINUITY-001`, and `DCL-STANDING-BACKLOG-SCHEMA-001` - standing backlog continuity and schema-governance context.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge review is the implementation handoff authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation proposals require explicit specification linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation must include spec-derived verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - project planning changes are durable artifacts and lifecycle transitions.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - project and application terminology must not collapse the GT-KB platform, hosted applications, demo applications, or Agent Red into one filesystem or release lifecycle.
- `GOV-ARTIFACT-APPROVAL-001`, `PB-ARTIFACT-APPROVAL-001` - formal GOV/ADR/DCL/SPEC/rule mutations remain approval-gated.

## Prior Deliberations

Deliberation archive searches from the original proposal and `-002` review are carried forward.

Relevant records:

- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` - owner directive that MemBase `work_items` is the canonical backlog source of truth and the pivot away from a separate `backlog_items` table is ratified.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - owner directive and resolution path for formal backlog DB schema work, now constrained by the S342 pivot.
- `DELIB-1791` and `DELIB-1790` - prior Loyal Opposition NO-GO reviews on backlog source-of-truth, including the earlier `work_items` versus `backlog_items` identity problem.
- `DELIB-0838` - owner decision on standing backlog governed cross-session work authority.
- `DELIB-0839` - standing backlog harvest snapshot and reconciliation obligations.
- `DELIB-0874` - owner decision on artifact-oriented development governance.
- `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE` - future-work candidates flow to MemBase `work_items` / `current_work_items`; implementation approval remains AUQ-protected.
- `DELIB-1583` - Loyal Opposition review of the backlog work-list retirement directive; project artifacts must not revive retired file-backed backlog authority.

No prior deliberation rejects first-class project artifacts. The controlling constraint is that project artifacts must extend, not supersede, `work_items` / `current_work_items` unless a separate owner-approved formal supersession is proposed.

## Owner Decisions / Input

The owner stated the following working model in chat on 2026-05-12:

- A `Subject` is the conceptual thing being implemented and evolved using software artifacts, such as GT-KB, Agent Red, or another application.
- A subject is implemented, evolved, and maintained through one or more time-oriented `Projects`.
- Projects are part of the stack-ranked `Backlog`.
- The backlog may contain multiple projects; each project may contain multiple work items or sub-projects.
- Work items may be members of multiple projects to reflect build order and interoperation dependencies.
- Bridge threads and deliberations are approved evidence/control artifacts associated with implementation and planning work.
- The owner suspects GT-KB does not currently handle projects as first-class artifacts and asked Prime Builder to create an implementation proposal and begin planning implementation.

This is direct chat evidence, not AskUserQuestion evidence and not a formal artifact approval packet. It is sufficient owner direction to file this bridge proposal. It is not approval to mutate formal GOV/ADR/DCL/SPEC/rule records without applicable approval evidence.

## Current-State Evidence

- `work_items` and `current_work_items` are the active MemBase backlog surfaces. They contain `project_name` and `subproject_name`, but do not model project identity, project lifecycle state, project rank, project dependencies, or project evidence links as first-class rows.
- `config/agent-control/system-interface-map.toml` declares `current_work_items` as the authoritative backlog read interface and marks `memory/work_list.md` compatibility-only.
- `.claude/rules/operating-model.md` defines `project` as a named grouping of related known work in the backlog.
- Existing backlog DB authority records now center backlog storage on `work_items` / `current_work_items`; this proposal follows that authority.
- `.claude/rules/canonical-terminology.md` already uses `work subject` for a startup/session-focus concept. A schema-level `Subject` row would need deliberate disambiguation before implementation.

## Proposed Canonical Model For This Slice

### Non-Negotiable Backlog Authority

`work_items` and `current_work_items` remain the only canonical backlog work-record authority for this proposal.

No `backlog_items` table, `backlog_entries` table, wrapper queue table, or alternative backlog work-record authority is proposed. If future work needs a separate rankable queue table, that must be a separate formal supersession proposal against `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v3, `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v3, and `GOV-STANDING-BACKLOG-001` v4 with owner approval evidence.

### First-Class Project Layer

Implement first-class `projects` as planning/lifecycle containers over canonical work items:

- `projects` identify durable project records, project name, status, rank, purpose, target outcome, lifecycle dates when known, and notes.
- `project_work_item_memberships` links projects to canonical `work_items`, allowing a work item to participate in zero, one, or many projects without duplicating the work item.
- `project_dependencies` links project-to-project dependencies with type, rationale, blocking status, and optional related work item.
- `project_artifact_links` links projects to bridge documents, deliberations, specs, ADRs, DCLs, implementation reports, verification evidence, and release blockers.
- Compatibility views preserve existing `work_items.project_name` and `work_items.subproject_name` during migration, but those string fields are explicitly compatibility inputs, not the future authoritative project model.

### Subject Deferral

No `subjects` table is implemented in Slice 1.

Before any schema-level `Subject` implementation, Prime Builder must file a terminology/governance proposal that disambiguates:

- owner-facing `Subject` from canonical `application`;
- `Subject` from `platform`;
- `Subject` from `hosted application`;
- `Subject` from existing startup/session `work subject`;
- how GT-KB, demo applications, and Agent Red map to the term without violating `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

Acceptable Slice 1 project records may include conservative text metadata such as `scope_note` or `application_context_note`, but must not create a new canonical `subjects` table or silently replace established terminology.

## Proposed Implementation Plan

### Slice 1 - Project Foundation Over `work_items`

- Add append-friendly MemBase tables for `projects`, `project_work_item_memberships`, `project_dependencies`, and `project_artifact_links`.
- Add current views for project records and project membership records using existing MemBase append/version patterns.
- Add deterministic migration/backfill logic from existing `current_work_items.project_name` and `subproject_name` strings into project records and membership rows.
- Preserve existing `work_items` reads/writes and `current_work_items` as the canonical backlog query during migration.
- Add project-aware read APIs that layer over `current_work_items`, not around it.
- Do not create a `subjects` table.
- Do not create `backlog_items` or any equivalent wrapper queue table.

### Slice 2 - CLI And Reporting

- Add project-aware commands or options for listing projects, showing a project, listing project work items, and showing project dependencies/artifact links.
- Update backlog reporting so project grouping comes from first-class `projects` plus memberships, while work-item authority remains `current_work_items`.
- Update startup/current-state reporting to distinguish project status, project rank, project blockers, and work-item membership.

### Slice 3 - Terminology / Governance Alignment Before Any Subject Schema

- File a separate terminology/governance proposal for `Subject` before any schema-level subject table.
- If approved, update canonical terminology and operating-model text through the formal approval path.
- If not approved, continue using `application`, `platform`, `hosted application`, and `work subject` as currently defined.

### Slice 4 - Dashboard And Release Integration

- Update dashboards and release-readiness reports to show project-level backlog, cross-project dependencies, linked bridge state, linked deliberation/spec evidence, and project-level blockers.
- Add assertions that prevent orphaned project memberships, unknown project references, stale project string authority, and unlinked implementation proposals for project-affecting work.

## Out Of Scope

- Creating a `subjects` table in Slice 1.
- Creating `backlog_items`, `backlog_entries`, or any alternate canonical backlog work-record table.
- Superseding `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v3, `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v3, or `GOV-STANDING-BACKLOG-001` v4.
- Retiring `memory/work_list.md` beyond its current compatibility status.
- Treating Agent Red repository files as live GT-KB artifacts.
- Replacing `application`, `platform`, `hosted application`, or `work subject` in canonical terminology.
- Mutating formal GOV, ADR, DCL, SPEC, or rule artifacts without required approval evidence.
- Production deployment or release changes.

## Specification-Derived Verification Plan

| Test ID | Requirement | Verification |
|---|---|---|
| T-project-schema | First-class project layer over MemBase | Schema/unit test creates `projects`, `project_work_item_memberships`, `project_dependencies`, `project_artifact_links`, and current views. |
| T-work-items-authority | S342 backlog authority pivot | Test proves `work_items` / `current_work_items` remain canonical work-record source and no `backlog_items` table is created. |
| T-many-to-many | Owner model: work items may belong to multiple projects | Test links one work item to multiple projects without duplicating the work item. |
| T-project-dependencies | Project dependencies queryable independently | Test creates project-to-project dependency with rationale and optional linked work item. |
| T-artifact-links | Bridge/deliberation/spec evidence links | Test links project to bridge document, deliberation ID, and spec ID. |
| T-compat-migration | Preserve existing project strings | Migration/backfill test maps `current_work_items.project_name` / `subproject_name` into projects and memberships without data loss. |
| T-no-subject-table | F3 correction | Test or schema assertion proves Slice 1 does not create a `subjects` table. |
| T-reporting | Reporting uses project layer over current work items | CLI/reporting test shows projects and member work items while still sourcing work item details from `current_work_items`. |

Expected targeted commands after implementation:

```powershell
python -m pytest groundtruth-kb/tests/test_project_artifacts.py groundtruth-kb/tests/test_cli.py groundtruth-kb/tests/test_operating_state.py -q --tb=short
python -m ruff check groundtruth-kb/src groundtruth-kb/tests
python -m ruff format --check groundtruth-kb/src groundtruth-kb/tests
```

Use narrower test targets if file names differ, but the implementation report must explain substitutions and must include a spec-to-test mapping.

## Acceptance Criteria

- Projects are represented by stable first-class MemBase rows and current views.
- `work_items` and `current_work_items` remain canonical backlog work-record authority.
- No `backlog_items` table or equivalent wrapper work-record authority is created.
- A work item can belong to multiple projects without duplication.
- Cross-project dependencies are queryable independently of work-item dependencies.
- Bridge threads, deliberations, specs, implementation reports, and verification evidence can link to projects without being mislabeled as work items.
- Existing backlog consumers continue to work during migration.
- Compatibility fields `work_items.project_name` and `work_items.subproject_name` are preserved and explicitly documented as compatibility fields.
- No `subjects` table is created in Slice 1.
- Any future `Subject` schema work is blocked until terminology/governance disambiguation is approved.

## Risk And Mitigation

- **Risk:** Project rows accidentally become a second backlog authority.
  **Mitigation:** Tests and docs must state that `work_items` / `current_work_items` remain canonical; project rows organize work items but do not replace them.

- **Risk:** Project ranking creates ambiguity with work-item priority.
  **Mitigation:** Separate project rank, membership ordering, and work-item dependency/blocking fields. Do not create a wrapper queue table.

- **Risk:** Deferring `Subject` leaves some owner vocabulary incomplete.
  **Mitigation:** Implement projects first using existing canonical terms, then file a separate terminology/governance proposal before any subject schema.

- **Risk:** Backfill from strings creates duplicate projects.
  **Mitigation:** Produce an inventory artifact before backfill, normalize deterministically, and keep compatibility fields until reports and consumers migrate.

## Decision Requested From Loyal Opposition

Return `GO` if this revised proposal closes `-002` F1-F3 and is narrow enough to implement first-class project artifacts over the current `work_items` / `current_work_items` backlog authority.

Return `NO-GO` if the project layer still risks creating a second backlog authority, if `Subject` disambiguation must precede even project-table work, or if additional formal owner approval is required before Slice 1 implementation.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
