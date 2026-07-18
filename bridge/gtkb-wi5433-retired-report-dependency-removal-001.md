NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Prime Builder
author_metadata_source: same-session .gtkb-state bridge proposal draft metadata

# Implementation Proposal - Remove release-test dependence on retired Dropbox reports

bridge_kind: prime_proposal
Document: gtkb-wi5433-retired-report-dependency-removal
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5433

target_paths: ["platform_tests/scripts/test_groundtruth_governance_adoption.py", "platform_tests/scripts/test_standing_backlog_harvest.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Replace two obsolete report-file dependencies with current structured backlog evidence so the RC suite remains authoritative after report retirement.

Work item description: Current release-gate tests hard-require independent-progress-assessments/CODEX-INSIGHT-DROPBOX/STANDING-BACKLOG-HARVEST-2026-04-20.md and STANDING-BACKLOG-BRIDGE-DISPOSITIONS-2026-04-20.md. Those reports are now among 167 concurrent tracked Dropbox deletions, and the canonical operating contract says harness/advisory report surfaces are not backlog authority. Update the adoption/harvest regression contract to consume current MemBase or another governed structured source, or explicitly retain only a still-authoritative artifact with durable rationale. Preserve all foreign deletion bytes and do not bulk restore, stage, or adopt the concurrent cleanup.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5433` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `platform_tests/scripts/test_groundtruth_governance_adoption.py`, `platform_tests/scripts/test_standing_backlog_harvest.py`.

## Specification Links

- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-0649` - Deliberation Archive Completion Advisory
- `DELIB-20264326` - Loyal Opposition Verification - GT-KB Mass Adoption Readiness Phase A
- `DELIB-2270` - Loyal Opposition Review - W2 Agent-Red GOV Trio v2 Supersession REVISED
- `DELIB-1856` - Loyal Opposition Review - GTKB MemBase Effective Use Recovery (scoping)
- `DELIB-0839` - Standing backlog harvest snapshot and reconciliation obligations

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5433`.

## Proposed Scope

- Remove the retired STANDING-BACKLOG-HARVEST-2026-04-20.md path from the governance-adoption required-file inventory.
- Replace live reads of retired standing-backlog reports with structured KnowledgeDB assertions over the current GTKB-GOV-004, GTKB-GOV-009, and GTKB-GOV-010 work-item records plus the existing build_audit shape contract.
- Retain the existing DELIB-0839 historical-content assertion and the Agent Red seed fixture text as historical evidence; do not restore, edit, stage, or adopt any retired report or foreign deletion.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-STANDING-BACKLOG-001` | groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_groundtruth_governance_adoption.py platform_tests/scripts/test_standing_backlog_harvest.py -q --tb=short |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Confirm active test code contains no filesystem dependency on STANDING-BACKLOG-HARVEST-2026-04-20.md or STANDING-BACKLOG-BRIDGE-DISPOSITIONS-2026-04-20.md while preserving historical strings. |

## Acceptance Criteria

- Neither target test reads, stats, or requires either retired 2026-04-20 report path at runtime.
- The structured assertions prove the harvested backlog parent, verified Azure gate disposition, and repeatable audit owner remain represented in current MemBase state.
- The two focused test modules pass and no production, bridge, dispatcher, harness, database, deleted-report, Git index, release, or deployment path is changed.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `platform_tests/scripts/test_groundtruth_governance_adoption.py`
- `platform_tests/scripts/test_standing_backlog_harvest.py`

## Recommended Commit Type

`feat`
