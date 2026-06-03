REVISED
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: keep-working-2026-06-03-adoption-doctor-requirement-sufficiency-refresh
author_model: GPT-5 Codex
author_model_version: 2026-06-03 runtime
author_model_configuration: Codex Desktop automation keep-working
author_metadata_source: explicit Codex revision metadata

# Implementation Proposal - Governance-Adoption Doctor Check - Requirement Sufficiency Refresh

bridge_kind: implementation_proposal
Document: gtkb-governance-adoption-doctor-check
Version: 005 (REVISED)
Author: Prime Builder (Codex, harness A)
Date: 2026-06-03 UTC
Responds-To: bridge/gtkb-governance-adoption-doctor-check-004.md
Supersedes: bridge/gtkb-governance-adoption-doctor-check-003.md
Recommended commit type: feat:
Project Authorization: PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH
Project: PROJECT-GTKB-ADOPTER-EXPERIENCE
Work Item: GTKB-GOV-003
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_doctor_adoption_drift.py"]

## Revision Claim

This is a compatibility refresh for the already-GO'd governance-adoption doctor check proposal. It does not broaden implementation scope, change target paths, or alter the accepted managed-artifact registry design from bridge/gtkb-governance-adoption-doctor-check-003.md.

The latest Loyal Opposition verdict at bridge/gtkb-governance-adoption-doctor-check-004.md is GO, but the current implementation-start gate rejects that approved proposal with: Approved proposal is missing ## Requirement Sufficiency.

This revision preserves the approved proposal and adds a parser-recognized ## Requirement Sufficiency section so Prime Builder can create an implementation-start packet before touching the approved source/test targets.

## Requirement Sufficiency

Existing requirements sufficient.

The existing owner-approved requirements and prior GO remain sufficient for this bounded managed-artifact doctor-check slice. No new or revised requirement is needed before implementation because this revision only makes the proposal compatible with the current implementation-start parser.

## Scope Preservation

Implementation remains limited to the two target paths listed above. New registry APIs, parallel manifests, unrelated doctor rewrites, deployment, push, force-push, production release action, and changes outside E:\GT-KB remain out of scope.

## Specification Links

- GOV-GTKB-ADOPTION-ENFORCEMENT-001
- GOV-RELEASE-READINESS-GOVERNED-TESTING-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-STANDING-BACKLOG-001
- .claude/rules/file-bridge-protocol.md
- .claude/rules/codex-review-gate.md
- .claude/rules/project-root-boundary.md

## Prior Deliberations

- DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS - owner approval for the adopter-experience batch containing GTKB-GOV-003.
- DELIB-1242, DELIB-1243, and DELIB-1244 - prior Tier A adoption and managed-artifact context surfaced by the original review.
- DELIB-1074 - prior Agent Red governance-adoption drift and release-readiness context.
- DELIB-0758 and DELIB-1207 - mass-adoption readiness context.
- bridge/gtkb-governance-adoption-doctor-check-004.md - Loyal Opposition GO approving the managed-registry based design.

## Owner Decisions / Input

- S350 owner batch authorization, captured as DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS, covers GTKB-GOV-003.
- Project authorization PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH remains active owner approval evidence.

No new owner decision is required for this metadata refresh.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Use governed bridge text and doctor/test code only; do not include credentials. | Bridge helper credential scan and staged secret scan before implementation report. | |
| CQ-PATHS-001 | Yes | Keep implementation under the two declared target paths and inside E:\GT-KB. | Implementation authorization packet and git diff path review. | |
| CQ-COMPLEXITY-001 | Yes | Extend current doctor managed-registry checks without creating a parallel registry. | Source review and focused doctor tests. | |
| CQ-CONSTANTS-001 | Yes | Reuse existing doctor ToolCheck status values and managed-registry terms. | Ruff and source review. | |
| CQ-SECURITY-001 | Yes | Doctor drift reporting must inspect local artifacts without executing untrusted content. | Focused tests and source review. | |
| CQ-DOCS-001 | Yes | Post-implementation report documents changed files, commands, and observed results. | Loyal Opposition bridge verification. | |
| CQ-TESTS-001 | Yes | Add or update the focused doctor adoption-drift tests. | Focused pytest command in implementation report. | |
| CQ-LOGGING-001 | N/A | | | Metadata refresh does not add runtime logging. |
| CQ-VERIFICATION-001 | Yes | Run focused tests plus ruff check and ruff format check on changed Python files. | Commands and observed results in implementation report. | |

## Spec-to-Test Mapping

- Managed-artifact adoption drift is surfaced by doctor: verify with focused doctor adoption-drift tests.
- Missing or broken managed-registry load is visible instead of silently skipped: verify with focused failure-path tests.
- All live paths remain under E:\GT-KB: verify with git diff checks and changed-path review.
- Proposal remains bridge-governed and implementation-start compatible: verify that implementation_authorization begin succeeds after GO on this revision.
- Python code-quality gates remain separate: run ruff check and ruff format --check on changed Python files before the post-implementation report.

## Acceptance Criteria

- Loyal Opposition records GO on this revision.
- implementation_authorization begin --bridge-id gtkb-governance-adoption-doctor-check --no-write can create an authorization packet from the refreshed proposal.
- Future implementation remains limited to the two target paths listed above.
- Post-implementation report carries forward the specification links and executed test evidence.

## Risk / Rollback

Risk is limited to bridge queue churn. If Loyal Opposition rejects this compatibility refresh, no source or test files are affected. Rollback is to leave latest GO at -004 and address any new findings in the next revision.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
