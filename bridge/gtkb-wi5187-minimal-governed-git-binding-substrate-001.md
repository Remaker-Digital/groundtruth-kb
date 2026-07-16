NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive; Prime Builder A; default reasoning configuration

# Implementation Proposal - Implement minimal governed Git binding substrate before Gate 1.25

bridge_kind: prime_proposal
Document: gtkb-wi5187-minimal-governed-git-binding-substrate
Version: 001
Date: 2026-07-15 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE
Work Item: WI-5187

target_paths: ["groundtruth-kb/src/groundtruth_kb/git_lifecycle/__init__.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/commands.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/models.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/quiescence.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/state.py", "scripts/check_modernization_git_lifecycle.py", "platform_tests/scripts/test_modernization_git_lifecycle.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Governed byte-preserving adoption of the existing ten-file WI-5187 minimal Git lifecycle substrate after exact-hash and complete focused-test capture.

Work item description: Implement only the minimal Git lifecycle substrate needed to make Gate 1.25 execution conforming: (1) canonical file-backed binding registry and append-only audit, (2) deterministic project/work-item ref and worktree naming, (3) exactly one hash-bound, owner-approved, independently reviewed, pre-source-mutation bootstrap manifest for WI-5187, (4) project/work-item binding create/show/validate, (5) isolated worktree identity validation and operation-time denial on missing, wrong, stale, or conflicting branch/worktree evidence, (6) scoped local commits needed to preserve independently VERIFIED Gate children, and (7) explicit atomic recovery. Verify with explicit targeted pytest plus manifest and state checks, not the aggregate assertion runner. Exclude work-item lifecycle integration, project/develop/stage promotion, GitHub mutation, cleanup, release, deployment, and all remaining WI-5158 scope. After WI-5187 is independently VERIFIED, every Gate 1.25 child must use ordinary governed bindings; WI-5158 remains held until Gate 1.25 closes. Planning record only: no PAUTH, bridge GO, claim, ref, worktree, registry, source/test/config mutation, Git mutation, commit, merge, push, release, or deployment authority.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5187` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/git_lifecycle/__init__.py`, `groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py`, `groundtruth-kb/src/groundtruth_kb/git_lifecycle/commands.py`, `groundtruth-kb/src/groundtruth_kb/git_lifecycle/models.py`, `groundtruth-kb/src/groundtruth_kb/git_lifecycle/quiescence.py`, `groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py`, `groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py`, `groundtruth-kb/src/groundtruth_kb/git_lifecycle/state.py`, `scripts/check_modernization_git_lifecycle.py`, `platform_tests/scripts/test_modernization_git_lifecycle.py`.

## Specification Links

- `DCL-GIT-BRANCH-BINDING-PROMOTION-001` - auto-linked governing or work-item specification.
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

- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-5-EXECUTION-ENTRY-PACKET` - Gate 1.5 WI-5158 pilot execution entry packet
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-5-PILOT-ENTRY-EVIDENCE-REFRESH` - Gate 1.5 pilot entry evidence refresh
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-GIT-READINESS-ASSESSMENT` - GT-KB Platform Modernization Gate 1 Git and Gate 1.5 readiness assessment
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-0-RESULT` - GT-KB Platform Modernization Gate 0 result
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-5-PILOT-AUTHORIZATION` - Authorize bounded Gate 1.5 WI-5158 pilot entry

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5187`.

## Proposed Scope

- Treat the exact current pre-start bytes and recorded SHA-256 hashes of the ten untracked WI-5187 candidates as foreign implementation content pending independent review; preserve them byte-for-byte during adoption.
- Adopt only the file-backed Git lifecycle package, its deterministic checker, and its focused test as the minimal Gate 1.25 substrate.
- Exclude ref/worktree creation or deletion, branch mutation, cleanup, project/work-item integration, promotion, remote/GitHub mutation, release, deployment, and every remaining WI-5158 concern.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-GIT-BRANCH-BINDING-PROMOTION-001` | Run the complete modernization Git-lifecycle test and deterministic checker, including missing/wrong/stale/conflicting binding denial and atomic recovery fixtures. |
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

- All ten reviewed candidate files remain byte-identical through the implementation report.
- platform_tests/scripts/test_modernization_git_lifecycle.py passes its complete checker-backed test.
- No Git ref, worktree, index, repository state, database, dispatcher, or unrelated path is mutated by candidate adoption.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/__init__.py`
- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py`
- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/commands.py`
- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/models.py`
- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/quiescence.py`
- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py`
- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py`
- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/state.py`
- `scripts/check_modernization_git_lifecycle.py`
- `platform_tests/scripts/test_modernization_git_lifecycle.py`

## Recommended Commit Type

`feat`
