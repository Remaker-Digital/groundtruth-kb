NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f17c3-3df4-7141-a6bd-43a6356ae28e
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop Auto-builder automation; approval_policy=never; sandbox=danger-full-access

# Implementation Proposal - Windows push governance preflight command and wrapper

bridge_kind: prime_proposal
Document: gtkb-wi4257-windows-push-preflight
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE
Work Item: WI-4257

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/governance/push_preflight.py", ".githooks/pre-push.cmd", ".githooks/pre-push.ps1", "platform_tests/groundtruth_kb/governance/test_push_preflight.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implement WI-4257 by adding a Windows-native push preflight command plus native pre-push wrappers that mirror the existing read-only .githooks/pre-push redacted range secret scan behavior.

Work item description: Add a canonical gt push preflight command and native Windows Git pre-push wrapper path that compute and run the same redacted range secret scan requirements currently encoded in .githooks/pre-push.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4257` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/cli.py`, `groundtruth-kb/src/groundtruth_kb/governance/push_preflight.py`, `.githooks/pre-push.cmd`, `.githooks/pre-push.ps1`, `platform_tests/groundtruth_kb/governance/test_push_preflight.py`.

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
- `SPEC-SEC-HOOK-PORTABILITY-001` - auto-linked governing or work-item specification.
- `SPEC-SEC-SCANNER-CLI-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20266429` - Separation Check
- `DELIB-20266430` - Separation Check
- `DELIB-20266416` - Separation Check
- `DELIB-20266067` - Separation Check
- `DELIB-20266404` - Separation Check

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE-BOUNDED-IMPLEMENTATION-2026-06-23` - active project authorization covering `WI-4257`.

## Proposed Scope

- Add a canonical gt push preflight command that accepts Git pre-push stdin tuples and computes the same safe ranges as the tracked Bash .githooks/pre-push hook.
- Add native Windows pre-push wrappers that prefer the project venv, set PYTHONPATH to groundtruth-kb/src, and delegate to the canonical gt push preflight command without duplicating scan logic.
- Keep the preflight read-only: no fetch, push, tag, rewrite, credential edit, remote mutation, or credential lifecycle action.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run bridge applicability and ADR/DCL clause preflights before filing and after implementation reporting. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Focused tests cover native Windows wrapper command strings and project venv precedence. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-SEC-HOOK-PORTABILITY-001` | Focused tests assert tracked Windows pre-push wrappers delegate to gt push preflight and do not duplicate direct scanner logic. |
| `SPEC-SEC-SCANNER-CLI-001` | Focused tests assert push preflight invokes groundtruth_kb secrets scan --range <computed> --redacted --fail-on verified-provider for existing and new refs. |

## Acceptance Criteria

- Existing-branch updates run a redacted verified-provider range scan for remote_sha..local_sha.
- New-branch pushes discover a safe upstream/origin/main/origin/develop/main/develop base or fail closed with reviewed-scan guidance.
- Deleted refs are skipped, and Windows wrappers delegate to the canonical command while preferring the project venv.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/governance/push_preflight.py`
- `.githooks/pre-push.cmd`
- `.githooks/pre-push.ps1`
- `platform_tests/groundtruth_kb/governance/test_push_preflight.py`

## Recommended Commit Type

`feat`
