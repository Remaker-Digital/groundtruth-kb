NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 8ae8ee16-629f-4328-a797-47cb3e7a3293
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

# Implementation Proposal - Add mechanical guard: doctor/lint for memory-labeled-authoritative, rule-shaped memory, and DELIB-sole-authority rules

bridge_kind: prime_proposal
Document: gtkb-wi5124-canonical-authority-drift-mechanical-guard
Version: 001
Date: 2026-07-09 UTC

Project Authorization: PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-EXECUTION
Project: PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION
Work Item: WI-5124

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_doctor_canonical_authority_guard.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Recurrence-prevention (deterministic-off-load fix, SPEC-INTAKE-fee587): add a doctor/lint guard for the three canonical-authority-drift shapes. Filed last; implementation sequences after the WI-5120/5121 carriers land. New tooling plus a targeted test.

Work item description: Deterministic-off-load fix (SPEC-INTAKE-fee587). Doctor/lint flagging (i) config labeling a memory/* path authoritative, (ii) memory/*.md with skill-frontmatter or imperative rule-shaped content, (iii) a rule whose sole cited Source is a DELIB with no canonical carrier.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5124` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, `groundtruth-kb/tests/test_doctor_canonical_authority_guard.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `SPEC-INTAKE-bb25be` - auto-linked governing or work-item specification.
- `SPEC-INTAKE-fee587` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20265747` - Loyal Opposition GO verdict: WI-4716 bridge-propose semantic-search doc sync
- `DELIB-20261103` - Verification Verdict - gtkb-backlog-update-title-desc-cli-001
- `DELIB-20261246` - Verification Verdict - gtkb-backlog-update-title-desc-cli-001
- `DELIB-20260999` - Loyal Opposition Review - Work-Tree Hygiene Slice A Detector
- `DELIB-20261194` - Loyal Opposition Review - Work-Tree Hygiene Slice A Detector

## Owner Decisions / Input

- `DELIB-202665930` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-EXECUTION` - active project authorization covering `WI-5124`.

## Proposed Scope

- Add a doctor check that mechanically flags the three canonical-authority-drift shapes: (i) any config field labeling a memory/* path authoritative, (ii) memory/*.md carrying skill-style frontmatter or imperative rule-shaped content, (iii) a rule whose sole cited Source is a DELIB with no canonical carrier.
- Implementation sequences after WI-5120 and WI-5121 land so the DELIB-sole-authority check does not false-positive on the orphans those work items remove.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-INTAKE-bb25be` | The check detects a reintroduced memory-authoritative label or a DELIB-sole-authority rule; a targeted test asserts each of the three detections. |
| `SPEC-INTAKE-fee587` | Source-authority is enforced mechanically (doctor), not left to worker judgment. |

## Acceptance Criteria

- A doctor check exists that flags all three drift shapes and passes on the post-remediation tree.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `groundtruth-kb/tests/test_doctor_canonical_authority_guard.py`

## Recommended Commit Type

`feat`
