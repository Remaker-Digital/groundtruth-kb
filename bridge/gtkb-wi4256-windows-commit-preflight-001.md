NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f11f8-951c-7961-8666-465412bdebce
author_model: GPT-5
author_model_version: Codex desktop
author_model_configuration: Codex desktop Auto-builder automation; approval_policy=never; sandbox=danger-full-access

# Implementation Proposal - Windows commit governance preflight command and wrapper

bridge_kind: prime_proposal
Document: gtkb-wi4256-windows-commit-preflight
Version: 001
Date: 2026-06-29 UTC

Project Authorization: PAUTH-PROJECT-GTKB-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE
Work Item: WI-4256

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/governance/preflight_evidence.py", "groundtruth-kb/src/groundtruth_kb/governance/commit_preflight.py", ".githooks/pre-commit.cmd", ".githooks/pre-commit.ps1", "platform_tests/groundtruth_kb/governance/test_commit_preflight.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implement WI-4256 by adding a Windows-native commit preflight command plus native wrapper that execute the existing staged pre-commit governance checks through the shared preflight evidence model.

Work item description: Add a canonical gt commit preflight command and native Windows Git pre-commit wrapper path that execute the same staged-content governance checks currently encoded in the Bash .githooks/pre-commit flow.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4256` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/cli.py`, `groundtruth-kb/src/groundtruth_kb/governance/preflight_evidence.py`, `groundtruth-kb/src/groundtruth_kb/governance/commit_preflight.py`, `.githooks/pre-commit.cmd`, `.githooks/pre-commit.ps1`, `platform_tests/groundtruth_kb/governance/test_commit_preflight.py`.

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

## Prior Deliberations

- `DELIB-20266067` - Separation Check
- `DELIB-20266051` - Review Independence Check
- `DELIB-0115` - S227 Commit e8808f0b Review
- `DELIB-0093` - S227 Re-Verification Continuation
- `DELIB-20266402` - Separation Check

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE-BOUNDED-IMPLEMENTATION-2026-06-23` - active project authorization covering `WI-4256`.

## Proposed Scope

- Add a PowerShell-callable gt commit preflight command that runs the staged secret scan, dev-environment inventory drift check, narrative-artifact evidence check, staged ruff-format check, protected-commit authorization check, and PowerShell syntax check when staged PS1 files exist.
- Add a native Windows pre-commit wrapper path that delegates to the canonical gt commit preflight command without duplicating check logic.
- Reuse the existing Windows governance preflight evidence model so human-readable and machine-readable output match WI-4255.

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

## Acceptance Criteria

- The command covers every governance check currently present in .githooks/pre-commit, preserving staged-scope behavior and fail-closed exit codes.
- The Windows wrapper delegates to the canonical command and is covered by focused tests or a wrapper contract test.
- Verification demonstrates parity with .githooks/pre-commit check coverage and validates evidence serialization for pass and failure paths.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/governance/preflight_evidence.py`
- `groundtruth-kb/src/groundtruth_kb/governance/commit_preflight.py`
- `.githooks/pre-commit.cmd`
- `.githooks/pre-commit.ps1`
- `platform_tests/groundtruth_kb/governance/test_commit_preflight.py`

## Recommended Commit Type

`feat`
