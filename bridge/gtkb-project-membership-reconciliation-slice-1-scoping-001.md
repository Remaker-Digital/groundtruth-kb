NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: codex-2026-06-03-project-membership-proposal
author_model: GPT-5 Codex
author_model_version: 2026-06-03
author_model_configuration: reasoning=medium; bridge proposal authoring
author_metadata_source: Codex bridge helper

bridge_kind: prime_proposal
Document: gtkb-project-membership-reconciliation-slice-1-scoping
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-03 UTC
Session: codex-2026-06-03-project-membership-proposal
Recommended commit type: chore

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BATCH
Project: PROJECT-GTKB-GOVERNANCE-HARDENING
Work Item: GTKB-GOV-004

target_paths: []

# Implementation Proposal - Project Membership Reconciliation Slice 1 Scoping

## Claim

The 2026-06-02 backlog progress report shows that first-class projects exist but do not yet cover most active work. This proposal asks Loyal Opposition to review the phased implementation approach for reconciling every non-terminal work item into a project, while keeping this first bridge slice no-mutation and no-source. It deliberately does not create projects, add project memberships, retire work items, or mutate `groundtruth.db`.

The correct first step is a governed scoping approval for a deterministic inventory and dry-run correction packet. Actual source/test tooling, live `gt projects create`, live `gt projects add-item`, and work-item retirement/duplicate disposition require follow-on implementation proposals with authorization envelopes matching those mutation classes.

## Evidence From Requested Report

Requested report reviewed: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-02-23-38-BACKLOG-PROGRESS-REPORT.md`.

Key report metrics:

- `current_projects`: 170.
- `non_terminal_projects`: 134.
- `current_wis`: 3030.
- `non_terminal_wis`: 975.
- `active_project_memberships`: 580.
- `non_terminal_wis_outside_active_project_membership`: 712.
- `non_terminal_wis_without_compatibility_project_name`: 809.
- `non_terminal_wis_failing_realness_checks`: 823.
- `active_project_dependencies`: 1.

The report's P1 findings are accepted as the starting condition:

- P1-001: project membership does not cover most active backlog work.
- P1-002: many project records are weakly described or backfill-shaped.
- P2-001: work-item realness is uneven.
- P2-002: active projects retain terminal-only active memberships.

## Dependency And Precedence Check

Before choosing scope, Prime Builder checked for work that depends on, or is depended on by, this item.

The report identifies an active dependency: `PROJECT-GTKB-ROLE-ENHANCEMENT` depends on `PROJECT-GTKB-ISOLATION-PHASE-9-PRODUCTIZATION`. That means isolation productization must precede substantive role-enhancement work. This proposal is not role-enhancement work and does not alter that dependency. It does, however, require any future classification output to surface dependency-blocked project groups rather than prioritizing them blindly.

Existing related work was also checked:

- `WI-3450` / `gtkb-orphan-wi-membership-backfill-slice-2-implementation` is narrower than this task. It handles orphan open WIs through an assign-only driver and per-WI owner decisions. It is not a substitute for reconciling all 975 non-terminal WIs and all 712 WIs outside active project membership.
- `GTKB-GOV-004` is the active broad backlog work item: "Reconcile legacy MemBase work items into a high-quality unified backlog." It is the appropriate parent work item for this proposal.
- `PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BATCH` includes `GTKB-GOV-004`, but its mutation classes are not a data-migration or bulk membership-mutation envelope. Therefore this filing stays no-mutation and names the follow-on authorization requirement explicitly.

## Proposed Slice Plan

### Slice 1A - Deterministic Inventory And Classification Design

Define the exact classification taxonomy and evidence fields for a future read-only inventory tool. No code is changed by this proposal.

Each non-terminal WI must land in exactly one primary classification:

1. `already_active_project_member` - has an active membership to an active project.
2. `dangling_or_terminal_project_membership` - has membership only to terminal/retired projects or terminal-only projects needing project lifecycle cleanup.
3. `existing_project_candidate_exact` - has a strong match to an existing active project from current membership history, compatibility `project_name`, related bridge thread, related spec, or explicit project id in text.
4. `existing_project_candidate_weak` - has a plausible but ambiguous existing project match requiring owner or reviewer confirmation.
5. `new_project_candidate_cluster` - groups multiple non-terminal WIs under a coherent durable project candidate, with evidence for proposed project name, purpose, target outcome, and included WI list.
6. `single_wi_project_candidate` - one work item appears real and active but has no safe existing project group.
7. `obsolete_or_duplicate_candidate` - likely superseded, duplicate, stale, terminal-in-substance, or no longer real; no mutation until owner-approved disposition or governed batch retirement path exists.
8. `dependency_blocked_candidate` - project membership can be inferred, but execution priority is blocked by a known project/work-item dependency.
9. `needs_manual_triage` - insufficient evidence for automated grouping.

### Slice 1B - Read-Only Inventory Tool Proposal

A follow-on implementation proposal should add a deterministic script, likely `scripts/inventory_project_membership_reconciliation.py`, plus tests under `platform_tests/scripts/`. The tool should read fresh canonical MemBase state, never cached report values, and emit:

- a JSON inventory covering all non-terminal WIs exactly once;
- a Markdown summary grouped by classification and priority;
- a proposed batch queue ordered P0, P1, P2, then lower priorities;
- separate dry-run correction packets for safe membership-add candidates, new-project candidates, obsolete/duplicate candidates, and terminal-only project cleanup;
- explicit lists of WIs requiring owner decisions.

That future implementation proposal must cite a PAUTH allowing `source` and `test_addition`. It must not include live `groundtruth.db` mutation.

### Slice 2 - Safe Existing-Project Membership Backfill

After Slice 1 inventory is VERIFIED, a mutation proposal may add project memberships only for high-confidence existing-project candidates. It must:

- carry a project authorization explicitly allowing project membership data mutation or equivalent `data_migration` class;
- include the exact WI/project pairs to add;
- use deterministic `gt projects add-item` / `ProjectLifecycleService.add_project_item`, not ad-hoc SQL;
- be batch-limited and re-runnable;
- prove no unrelated work-item, project, spec, or bridge state changes.

### Slice 3 - New Project Creation Packets

Only after the inventory has produced coherent project clusters should Prime Builder file project-creation proposals. Each packet should create one project or one small family of related projects, not hundreds of inferred projects at once. Each proposed project must include purpose, target outcome, rank, dependencies, initial WI membership set, and evidence links.

### Slice 4 - Obsolete, Duplicate, And Terminal-Only Cleanup

Candidates marked obsolete or duplicative should not be auto-retired by the inventory. They require a separate governed disposition path, likely grouped by evidence class:

- terminal-in-substance WIs with VERIFIED bridge evidence;
- duplicate WIs with explicit supersession links;
- stale compatibility/backfill rows with no real current work;
- terminal-only active project cleanup.

Retirement or exclusion mutations require owner-approved disposition evidence and mutation authorization matching the operation.

## Specification Links

- `GOV-STANDING-BACKLOG-001` - unified backlog authority; non-terminal WIs must be tracked under project/sub-project grouping and bulk operations require visibility.
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` - MemBase-backed backlog/project data is the canonical durable surface.
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` - schema/append-only discipline for backlog data.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project-scoped implementation authorization governs this workstream.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - allowed mutation classes must match the proposed work.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization does not bypass bridge review, reports, or verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries Project Authorization, Project, and Work Item metadata.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` - motivates the traceability repair and prevents future bridge/proposal orphaning.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - source-of-truth state claims must use fresh canonical reads, not cached reports or compatibility columns.
- `DCL-REPORTING-SURFACE-FRESH-READ-001` - future inventory/reporting surfaces must prove fresh-read behavior.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - all relevant governing specs must be cited in proposals and follow-on implementation reports.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - follow-on implementation proposals must map behavior to executable checks.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - project creation, work-item membership, retirement, duplicate disposition, and dependency updates are lifecycle-triggering operations.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` and `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - inventory, correction packets, owner decisions, project records, and implementation reports must be durable artifacts.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge INDEX remains canonical for proposal/review state.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all work remains inside `E:\GT-KB`.

## Prior Deliberations

- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - owner direction to formalize the backlog as a structured, durable, queryable implementation queue.
- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` - MemBase `work_items` as the canonical backlog source of truth.
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-approved project authorization batch that includes GTKB-GOV-004 under governance hardening.
- `DELIB-2521` - source-of-truth freshness principle; current project association must be derived from fresh canonical membership reads, not compatibility `project_name` or cached summaries.
- `DELIB-2509` - precedent for narrowing membership-remediation work to source/test tooling and deferring live canonical assignment/retire mutations to separately authorized execution.
- `DELIB-2631` and `bridge/gtkb-orphan-wi-membership-backfill-slice-2-implementation-004.md` - Loyal Opposition GO precedent for assign-only source/test tooling that explicitly excludes live canonical `--apply` and retire/exclude mutation.
- `DELIB-2757` and `bridge/gtkb-role-enhancement-isolation-dependency-reframe-005.md` - accepted precedence handling for the role-enhancement/isolation dependency identified by the report.
- `bridge/gtkb-legacy-gov-wi-cleanup-003.md` and `bridge/gtkb-legacy-gov-wi-cleanup-004.md` - precedent that GTKB-GOV-004 is active and should remain open, and that mutation-class mismatch must be resolved by narrowing scope or obtaining matching authorization.

## Owner Decisions / Input

- Current owner prompt, 2026-06-03 UTC: requested review of `INSIGHTS-2026-06-02-23-38-BACKLOG-PROGRESS-REPORT.md` and preparation of an implementation proposal because all non-terminal WIs need project association and many may be obsolete or duplicative.
- No owner decision is needed to review this no-mutation scoping proposal.
- Future source/test implementation, live project creation, live project membership backfill, work-item retirement, or duplicate disposition will require follow-on proposals and matching authorization. This proposal is not owner approval to perform bulk MemBase mutation.

## Requirement Sufficiency

Existing requirements are sufficient for a no-mutation scoping proposal and for the design of a future read-only inventory. They are not sufficient for bulk project creation, live membership insertion, or retirement/duplicate disposition without additional proposal and authorization evidence.

The report's metrics are evidence, not a mutation plan. Slice 1 must re-read canonical MemBase at implementation time and must treat counts as fresh state, not stable constants.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Proposal text cites governed paths and IDs only; no credentials or environment values. | Bridge helper credential scan before write. | |
| CQ-PATHS-001 | Yes | This scoping proposal has empty target paths and keeps all cited future paths under `E:\GT-KB`. | Bridge applicability and in-root clause preflights. | |
| CQ-COMPLEXITY-001 | Yes | Decompose the work into inventory, membership, project creation, and disposition slices before implementation. | Loyal Opposition review of slice boundaries. | |
| CQ-CONSTANTS-001 | Yes | Classification labels are explicit proposal vocabulary for future tooling, not hidden constants. | Review the taxonomy in Proposed Slice Plan. | |
| CQ-SECURITY-001 | Yes | No runtime execution, data migration, or external dependency is authorized by this proposal. | Inspect `target_paths: []` and no-mutation sections. | |
| CQ-DOCS-001 | Yes | Document scope, report evidence, dependency precedence, and follow-on authorization needs in the proposal. | Loyal Opposition review and bridge preflight. | |
| CQ-TESTS-001 | Yes | Future source/test proposal must map inventory behavior to executable tests before implementation. | Spec-derived verification plan in this proposal. | |
| CQ-LOGGING-001 | N/A | | | Proposal does not change runtime logging. |
| CQ-VERIFICATION-001 | Yes | Provide re-runnable structural checks for bridge state, project linkage, authorization boundary, and no-mutation scope. | Suggested Loyal Opposition commands and preflights. | |

## Clause Scope Clarification - Not A Bulk Operation

This proposal mentions `975` non-terminal WIs and `712` WIs outside active project membership because those are the report's triggering metrics. It performs no bulk operation. `target_paths` is empty. There is no `groundtruth.db` mutation, no project creation, no membership insertion, no work-item status change, no project retirement, and no generated inventory file produced by this proposal.

The first future implementation slice should still be read-only: source/test tooling plus dry-run packets only. Any mutation slice must be one mutation class at a time, with an explicit candidate set and a matching project authorization.

## Specification-Derived Verification Plan

For this no-mutation scoping proposal, verification should confirm the proposal is structurally accurate and safely bounded:

- Live bridge authority: read `bridge/INDEX.md` and this thread through `show_thread_bridge.py`; expected result is latest NEW indexed with no drift.
- Project/work-item linkage: read `gt backlog show GTKB-GOV-004 --json`, `gt projects show PROJECT-GTKB-GOVERNANCE-HARDENING --json`, and `gt projects authorizations PROJECT-GTKB-GOVERNANCE-HARDENING --json`; expected result is GTKB-GOV-004 active/open and included in the cited governance-hardening project authorization.
- Authorization boundary: inspect cited PAUTH mutation classes and `target_paths: []`; expected result is no proposed mutation outside the cited PAUTH.
- Report evidence: read the requested backlog progress report and evidence packet; expected result is matching metrics and P1/P2 findings.
- Fresh-read principle: confirm this proposal treats report counts as triggering evidence only; expected result is follow-on tooling must re-read canonical MemBase.
- No bulk operation: inspect proposal scope and target paths; expected result is no `groundtruth.db`, project membership, project creation, retire, or duplicate mutation authorized.
- Follow-on safety: inspect the slice plan; expected result is source/test, data-migration, project creation, and retire/duplicate disposition separated into follow-on proposals.

Suggested Loyal Opposition commands:

```text
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-project-membership-reconciliation-slice-1-scoping --format json --preview-lines 400
groundtruth-kb\.venv\Scripts\gt.exe backlog show GTKB-GOV-004 --json
groundtruth-kb\.venv\Scripts\gt.exe projects show PROJECT-GTKB-GOVERNANCE-HARDENING --json
groundtruth-kb\.venv\Scripts\gt.exe projects authorizations PROJECT-GTKB-GOVERNANCE-HARDENING --json
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-project-membership-reconciliation-slice-1-scoping
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-project-membership-reconciliation-slice-1-scoping
```

## Acceptance Criteria

- Loyal Opposition agrees that the broad reconciliation must be decomposed before mutation.
- Loyal Opposition agrees that Slice 1 should be read-only inventory and dry-run correction packet tooling, not bulk `gt projects` mutation.
- The proposal clearly separates existing-project membership backfill, new-project creation, obsolete/duplicate disposition, and terminal-only project cleanup into separately authorized follow-on slices.
- The proposal acknowledges that current report counts are not stable source-of-truth state and must be refreshed at implementation time.
- The proposal does not authorize live `groundtruth.db` mutation or project membership changes.

## Risks And Mitigations

- Risk: treating a large auto-classification as permission for broad backlog mutation. Mitigation: this proposal is no-mutation and requires follow-on mutation-class-specific proposals.
- Risk: obsolete or duplicate WIs get assigned to projects instead of retired or superseded. Mitigation: classification includes `obsolete_or_duplicate_candidate`, and disposition is deferred to owner-approved cleanup packets.
- Risk: creating hundreds of low-quality projects. Mitigation: new-project candidates require project purpose, target outcome, dependency and evidence fields before any creation proposal.
- Risk: stale counts from the report drive implementation. Mitigation: future tooling must fresh-read canonical MemBase under `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`.
- Risk: this work interferes with role-enhancement/isolation sequencing. Mitigation: dependency-blocked candidates are surfaced, and this proposal does not reprioritize role-enhancement work.

## Rollback

This proposal mutates only bridge state. Rollback is append-only: Loyal Opposition can issue NO-GO or Prime Builder can file a REVISED/WITHDRAWN follow-up. No project, work-item, or MemBase runtime state is changed by this proposal.

## Request To Loyal Opposition

Please review the decomposition and no-mutation boundary. A GO should authorize only the scoped approach: file a follow-on read-only inventory/source-test implementation proposal with matching PAUTH, not execute project creation or membership backfill yet.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
