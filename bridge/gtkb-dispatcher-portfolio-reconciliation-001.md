NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: codex-20260702-ops-dispatcher-synthesis
author_model: GPT-5
author_model_version: 2026-07-02
author_model_configuration: Codex desktop; E:/GT-KB; danger-full-access; approval-policy never; interactive role Prime Builder via ::init gtkb pb

# Dispatcher Portfolio Reconciliation

bridge_kind: prime_proposal
Document: gtkb-dispatcher-portfolio-reconciliation
Version: 001
Date: 2026-07-02 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-PORTFOLIO-RECONCILIATION-WI-4960
Project: PROJECT-GTKB-DISPATCHER-PORTFOLIO-RECONCILIATION
Work Item: WI-4960

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_projects_reconcile.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py", "groundtruth-kb/src/groundtruth_kb/project", "scripts/inventory_project_membership_reconciliation.py", "scripts/project_verified_completion_scanner.py", "scripts/gtkb_dispatcher_daemon.py", "scripts/dispatcher_runtime.py", "config/dispatcher", "harness-state/harness-registry.json", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX", "platform_tests/scripts", "platform_tests/groundtruth_kb", "groundtruth-kb/tests"]

implementation_scope: source+formal-artifact+project-metadata+backlog-metadata+spec-metadata+tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

## Summary

Add a Wave 1 portfolio-reconciliation lane to the `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION` umbrella. This proposal inventories, classifies, and reconciles outstanding dispatcher-overlapping projects, work items, bridge/advisory artifacts, and specifications so stale or contradictory work does not compete with the OPS lifecycle, lane-scoring, and AUQ/headless implementation proposals.

This proposal folds in the owner directive that this is the most expansive umbrella program initiated so far. It treats portfolio reconciliation as part of the program foundation, not as optional cleanup.

## Claim

Prime Builder proposes to create and execute a governed dispatcher portfolio reconciliation pass before or alongside Wave 1 implementation. The pass must produce a deterministic inventory and explicit disposition for every overlapping candidate: fold into the umbrella, update/rehome, retire, supersede, leave scoped elsewhere with rationale, or defer with reason.

## Requirement Sufficiency

Existing requirements sufficient.

Existing dispatcher, backlog, project lifecycle, and bridge-governance requirements are sufficient for proposal filing and implementation-start authorization. This slice still permits bounded formal-artifact/spec updates when the reconciliation finds contradictory or obsolete authority that must be amended, superseded, or retired through governed paths.

## In-Root Placement Evidence

All implementation outputs, reports, metadata updates, tests, and formalization side effects for this proposal remain under the GT-KB project root `E:/GT-KB`. The status-bearing bridge proposal is filed under `E:/GT-KB/bridge/gtkb-dispatcher-portfolio-reconciliation-001.md`. No Agent Red application source or external archive path is in scope.

## OPS Consolidation Integration

`OPS-LIFECYCLE-DISPATCHER-MODEL-CONSOLIDATION-2026-07-02.md` remains the parent model for the program. This reconciliation lane makes that model operationally safe by finding existing dispatcher artifacts that may already cover, contradict, or obsolete parts of the new umbrella.

The reconciliation must specifically account for:

- Current Wave 1 children: `WI-4957`, `WI-4958`, `WI-4959`, and this `WI-4960`.
- Release dispatcher work such as `WI-4943` and `WI-4944`.
- Recently captured stale dispatcher work such as `WI-4721`, `WI-4725`, and `WI-4956`.
- TAFE and bridge-dispatch remnants, including open TAFE compatibility or live-flow items.
- Runtime-orchestration discovery overlap that may cover dispatcher routing, service authority, worker lifecycle, or management-plane design.
- Harness parity/equivalence work that informs dispatchability, skill effectiveness, and harness/model quality evidence.
- Advisory backlog placeholders generated from dispatcher reports.
- The duplicate OPS project-family backfill artifacts created when display-name `project_name` fields generated `PROJECT-GT-KB-OPS-DISPATCHER-MODERNIZATION` alongside the canonical `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION` family.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires protected source/config changes to proceed through bridge proposal, GO, implementation report, and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete governing specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires verification mapped to cited specifications.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform work inside GT-KB and out of Agent Red application source.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher owns dispatch decisions and dispatch activity records.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher control and health surfaces must remain authoritative and coherent.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher is the persistent daemon-owned control plane.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` - governs project/member retirement and terminal reconciliation.
- `GOV-STANDING-BACKLOG-001` - governs backlog preservation, disposition, and future-work capture.

## Prior Deliberations

- `DELIB-20260702-DISPATCH-OPS-UMBRELLA-PORTFOLIO-RECONCILIATION` - owner directed the umbrella to triage and reconcile all outstanding dispatcher-overlapping projects, WIs, and specs.
- `DELIB-20260702-DISPATCH-OPS-CREATE-ACTUAL-PROJECT-WIS-BRIDGE-PROPOSALS` - owner selected actual governed project, WI, and bridge proposal creation.
- `DELIB-20260702-DISPATCH-OPS-NEW-IMPLEMENTATION-PARENT-PROJECT` - owner selected a new implementation parent project.
- `DELIB-20260702-DISPATCH-OPS-PARENT-PROJECT-PARALLEL-CHILD-PROPOSALS` - owner selected one parent project with parallel child proposals.
- `DELIB-20260702-DISPATCH-OPS-FOUNDATION-FIRST-IMPLEMENTATION-WAVE` - Wave 1 starts with foundational OPS lifecycle/protocol, lane-scoring schema, and AUQ/headless hygiene.
- `DELIB-20260702-DISPATCH-OPS-WAVE1-FILE-ALL-PRIORITIZE-AUQ-HEADLESS` - file Wave 1 proposals together and prioritize AUQ/headless if GO arrives quickly.
- `DELIB-20260702-DISPATCH-LANE-SCORING-EXTENDS-OPS-LIFECYCLE-CONSOLIDATION` - lane scoring extends the OPS consolidation, rather than competing with it.
- `DELIB-20260702-DISPATCH-LIFECYCLE-FIRST-SCORING-LAST-PRECEDENCE` - OPS lifecycle eligibility precedes lane scoring.
- `DELIB-20260702-AUQ-ADJACENT-CONSOLE-WINDOWS-HEADLESS-REQUIREMENT` - owner reported AUQ-adjacent console windows that must be headless.

## Owner Decisions / Input

- `DELIB-20260702-DISPATCH-OPS-UMBRELLA-PORTFOLIO-RECONCILIATION` - owner added the portfolio-reconciliation requirement and characterized the umbrella as the most expansive program initiated so far.
- `PAUTH-PROJECT-GTKB-DISPATCHER-PORTFOLIO-RECONCILIATION-WI-4960` - active child-project authorization for this work item.

## Proposed Scope

- Build or extend deterministic inventory queries covering active/open and recently retired projects, work items, bridge/advisory artifacts, and specs whose ids, names, descriptions, components, related bridge threads, source specs, target paths, or project associations indicate dispatcher overlap.
- Produce a reconciliation report in `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/` listing candidates, evidence, overlap class, risk, and disposition.
- Reconcile duplicate first-class project-family records created by display-name `project_name` backfill during this umbrella setup, preserving canonical `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION` and child project ids.
- Update or rehome open work items that should become members of this umbrella, especially dispatcher release/unblock work, stale dispatcher defects, and harness-dispatch blockers.
- Retire, supersede, or mark stale obsolete items only when deterministic evidence and governed authority support terminal disposition.
- Identify specifications or proposal text that contradict the OPS consolidation and either file formal amendment work, supersede them, or explicitly leave them in place with boundary rationale.
- Add focused tests or CLI smoke checks proving the inventory/disposition tooling covers the intended query classes and does not mutate artifacts during report-only mode.
- Require downstream Wave 1 implementation reports to cite the reconciliation report or explain why their target scope is not affected by remaining overlaps.

## Out Of Scope

- Ad hoc retirement or status changes without deterministic inventory evidence.
- Production dispatcher topology activation or lane-scoring activation.
- Credential lifecycle changes or production deployment.
- Agent Red application source mutation.
- Broad source implementation of OPS lifecycle or lane scoring; those remain `WI-4957` and `WI-4958`.
- AUQ/headless launch implementation; that remains `WI-4959`.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Inventory includes dispatcher and dispatch-control work items/specs by id, component, source spec, related bridge thread, and text matches; dispositions do not create competing dispatcher authorities. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Reconciliation accounts for health/status/control-surface work such as release dispatcher substrate, LO dispatch unblock, stale FAIL state, and headless worker blockers. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Report classifies items that affect daemon control-plane authority, harness consumers, worker lifecycle, and runtime topology without restoring retired poller/hook automation. |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` | Any project/member retirement or terminal reconciliation uses governed project/backlog CLI paths with evidence and preserves version history. |
| `GOV-STANDING-BACKLOG-001` | Open advisory placeholders and future-work candidates are either folded in, retired/superseded with evidence, or left as standing backlog with a boundary rationale. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Preflight and target-path checks prove all reconciliation artifacts remain under `E:/GT-KB` and do not touch Agent Red application source. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report maps inventory coverage, disposition actions, and no-mutation dry-run behavior to focused tests/checks. |

Required focused checks include report-only inventory smoke tests, duplicate-project-family detection, work-item overlap query tests for dispatcher/dispatch/bridge-dispatch terms, active-project overlap query tests, advisory-placeholder classification checks, and project/backlog update dry-run or post-update verification checks for each applied disposition.

## Acceptance Criteria

- A deterministic report lists all discovered dispatcher-overlapping projects, work items, specs, bridge/advisory artifacts, and duplicate project-family records.
- Every candidate has one explicit disposition: fold into umbrella, update/rehome, retire, supersede, leave scoped elsewhere, or defer with reason.
- The report explicitly covers `WI-4943`, `WI-4944`, `WI-4721`, `WI-4725`, `WI-4956`, the TAFE/bridge-dispatch overlap class, runtime-orchestration discovery overlap, harness parity/equivalence overlap, advisory placeholders, and duplicate OPS umbrella backfill artifacts.
- Any metadata updates are applied through governed CLI paths and recorded in project/work-item/spec history.
- Obsolete or contradictory items are not left as unexamined competing authority.
- Wave 1 implementation proposals can cite the reconciliation output as portfolio context.
- Targeted tests/checks pass, with pre-existing unrelated failures explicitly scoped.

## Risks / Rollback

Risk is moderate because this lane can touch broad metadata and formal authority surfaces. The main risk is over-retiring valid work or rehoming release-blocking work into a slower umbrella path. Mitigation: deterministic inventory, explicit disposition categories, evidence per candidate, and no terminal changes without governed CLI evidence.

Rollback is append-only metadata correction: create a new project/work-item/spec version reversing the disposition, or file a superseding reconciliation report. Bridge files and MemBase history must not be deleted.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/db.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/cli_projects_reconcile.py`
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py`
- `groundtruth-kb/src/groundtruth_kb/project/`
- `scripts/inventory_project_membership_reconciliation.py`
- `scripts/project_verified_completion_scanner.py`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/`
- `platform_tests/scripts/`
- `platform_tests/groundtruth_kb/`
- `groundtruth-kb/tests/`

## Recommended Commit Type

`chore`
