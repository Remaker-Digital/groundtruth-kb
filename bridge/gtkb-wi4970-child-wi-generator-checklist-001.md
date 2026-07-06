NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution
author_metadata_source: codex-explicit-runtime-envelope

# Implementation Proposal - Phase 3 gap 08: deterministic child-WI generator and checklist

bridge_kind: prime_proposal
Document: gtkb-wi4970-child-wi-generator-checklist
Version: 001
Date: 2026-07-06 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI4970-BATCH-C-20260705
Project: PROJECT-HARNESS-EQUIVALENCE-PHASE-3
Work Item: WI-4970

target_paths: ["scripts/project_child_wi_checklist.py", "platform_tests/scripts/test_project_child_wi_checklist.py", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-CHILD-WI-CHECKLIST-*.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implement a deterministic dry-run checklist/helper that converts identified project gaps into governed work-item, test, and bridge-proposal skeleton recommendations without dumping full SoT payloads into model context. The helper should preserve GOV-12/GOV-13 expectations and bridge proposal linkage requirements while leaving actual backlog mutations to governed CLI workflows.

The work item scope is limited to WI-4970. It does not authorize bulk backlog mutation or direct database writes.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4970` that reduces manual child-WI setup errors while keeping MemBase and bridge authority intact.

## Requirement Sufficiency

Existing requirements are sufficient. The Batch C PAUTH allows source/test/helper and governance-evidence work; `GOV-STANDING-BACKLOG-001` and artifact-oriented governance define the output contract.

## In-Root Placement Evidence

All proposed target paths are inside `E:\GT-KB`: `scripts/project_child_wi_checklist.py`, `platform_tests/scripts/test_project_child_wi_checklist.py`, and `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-CHILD-WI-CHECKLIST-*.md`.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - confirms implementation authority is project-bounded and evidence-backed.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms PAUTH does not bypass bridge proposal review or later GO.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge status filing.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires PAUTH, project, work item, and target path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete governing spec links before implementation review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires implementation reports to map specs to executed verification.
- `GOV-STANDING-BACKLOG-001` - requires standing work to flow through MemBase work items.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - routes actionable gaps into durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - keeps child work boundaries artifact-backed.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - classifies whether a gap becomes new work, supersession, waiver, retirement, or no-op.
- `ADR-CROSS-HARNESS-PARITY-001` - supplies the Phase 3 cross-harness use case for child-WI generation.

## Prior Deliberations

- `DELIB-202665197` - authorized Harness Equivalence Phase 3 child work.
- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner-directed Batch C continuation authorization.
- `DELIB-S20260626-CROSS-HARNESS-PARITY-ENFORCEMENT-GAP` - source parity enforcement context.
- `DELIB-202665119` - compact query and oversized SoT context.
- `DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE` - precedent for child work closure and supersession discipline.

## Owner Decisions / Input

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner approved Batch C continuation.
- `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI4970-BATCH-C-20260705` - active authorization covering WI-4970.

## Proposed Scope

- Add a dry-run helper that accepts compact gap records and emits checklist rows for candidate WI, linked test, target paths, PAUTH need, bridge proposal slug, and evidence references.
- Validate required fields without reading or embedding full SoT payloads.
- Generate a compact markdown report for Harness Equivalence Phase 3 child-WI readiness.
- Add focused tests for field validation, skeleton rendering, compact evidence handling, missing-spec warnings, and no-mutation behavior.

## Cross-Harness Disposition

The helper is harness-agnostic and supports Phase 3 gap processing across harness lanes. It must output recommendations only; actual work-item creation remains governed by `gt backlog` and project authorization evidence.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Confirm implementation report cites the active WI-4970 PAUTH and stays within target paths. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Confirm no protected implementation starts before GO. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Use `gt bridge show gtkb-wi4970-child-wi-generator-checklist --json --compact` to confirm lifecycle state. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run bridge applicability preflight and confirm project linkage metadata is present. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run bridge applicability preflight and confirm `missing_required_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run targeted tests and include exact command output in the implementation report. |
| `GOV-STANDING-BACKLOG-001` | Test that output routes child work through MemBase WI/test/proposal skeletons, not alternate backlog authority. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Confirm actionable gap records become durable recommendations with evidence references. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Confirm recommended child boundaries include artifact type, owner evidence, and target path data. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Test lifecycle classifications for new work, supersession, waiver, retirement, and no-op. |
| `ADR-CROSS-HARNESS-PARITY-001` | Test Phase 3 harness-gap examples produce complete child-WI checklist rows. |

## Acceptance Criteria

- The helper runs in dry-run mode only and performs no MemBase or bridge mutation.
- The generated checklist includes candidate WI fields, linked test prompt, PAUTH need, proposal slug, target paths, and evidence references.
- The helper refuses or warns on missing required evidence, missing target paths, missing spec links, and oversized raw payloads.
- Tests cover dry-run behavior, validation, lifecycle classifications, compact evidence handling, and markdown output.

## Risks / Rollback

Risk is moderate because generated skeletons can shape future backlog work. Mitigation is dry-run-only behavior, explicit validation warnings, and no direct database writes.

Rollback is a revert of the helper, tests, and generated report. Bridge files and PAUTH records are append-only audit artifacts and must not be deleted.

## Files Expected To Change

- `scripts/project_child_wi_checklist.py`
- `platform_tests/scripts/test_project_child_wi_checklist.py`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-CHILD-WI-CHECKLIST-*.md`

## Recommended Commit Type

`feat`
