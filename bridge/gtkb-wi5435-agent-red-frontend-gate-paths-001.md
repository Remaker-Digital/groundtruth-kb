NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Prime Builder
author_metadata_source: same-session .gtkb-state bridge proposal draft metadata

# Implementation Proposal - Restore missing WI-5366 Agent Red frontend gate path repair

bridge_kind: prime_proposal
Document: gtkb-wi5435-agent-red-frontend-gate-paths
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5435

target_paths: ["scripts/release_candidate_gate.py", "platform_tests/scripts/test_release_candidate_gate.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Restore the independently reviewed Agent Red frontend gate path intent while leaving application-owned build-surface creation to WI-5381.

Work item description: Current HEAD 42a252ab still runs npm --prefix widget test and root admin builds from scripts/release_candidate_gate.py, producing ENOENT for E:/GT-KB/widget/package.json. WI-5366 was auto-resolved from terminal review evidence, but scripts/release_candidate_gate.py and platform_tests/scripts/test_release_candidate_gate.py are both clean and retain the pre-repair paths. Reapply the independently reviewed path-only intent against the current baseline so every frontend command targets applications/Agent_Red/widget or applications/Agent_Red/admin subpackages. Preserve missing node_modules as an explicit environment prerequisite, do not recreate root packages, and do not absorb WI-5381 Python/build self-containment work.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5435` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/release_candidate_gate.py`, `platform_tests/scripts/test_release_candidate_gate.py`.

## Specification Links

- `ADR-APPLICATION-ISOLATION-CONTRACT-001` - auto-linked governing or work-item specification.
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

- `DELIB-202666507` - Loyal Opposition Corrected GO Verdict - WI-5318 Failed VERIFIED Finalization Repair
- `DELIB-0308` - S251 deploy_ui widget gate re-verification: NO-GO
- `DELIB-0369` - S252: Comprehensive Widget & Chat Improvement Proposal - deep review (revised)
- `DELIB-0309` - S251 deploy_ui widget gate fix re-verification — NO-GO
- `DELIB-202665565` - WI-4702 Dispatcher Reset Recipient State Directory Alignment — Loyal Opposition Review Verdict: GO

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5435`.

## Proposed Scope

- Define the Agent Red application root once in _frontend_gates and make widget test/build plus all three admin build prefixes resolve beneath applications/Agent_Red.
- Point the admin environment-sync command at applications/Agent_Red/scripts/sync-admin-env.ps1, whose application-owned implementation remains WI-5381 scope; do not recreate root widget/admin packages or modify either sync script in this slice.
- Update the release-gate unit test to assert exact application-rooted npm prefixes, one application-rooted sync invocation, and unchanged npm_config_ignore_scripts=true behavior for all admin builds.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-APPLICATION-ISOLATION-CONTRACT-001` | groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_release_candidate_gate.py -q --tb=short |
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

- No frontend npm or PowerShell command emitted by _frontend_gates targets root widget/, root admin/, or root scripts/sync-admin-env.ps1.
- The focused release-candidate gate unit tests pass with exact platform-neutral os.path.join expectations.
- Only the two declared target files change; WI-5381 retains ownership of the missing application dependency/build/sync surface and foreign dirt is excluded.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/release_candidate_gate.py`
- `platform_tests/scripts/test_release_candidate_gate.py`

## Recommended Commit Type

`feat`
