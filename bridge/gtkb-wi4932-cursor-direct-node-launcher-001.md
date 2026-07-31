NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop, GPT-5, Prime Builder, dispatcher release-health hardening

# Implementation Proposal - Cursor dispatcher launcher bypasses shell wrappers on Windows

bridge_kind: prime_proposal
Document: gtkb-wi4932-cursor-direct-node-launcher
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4932-CURSOR-NO-WINDOW-LAUNCHER
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4932

target_paths: ["scripts/cursor_harness.py", "platform_tests/scripts/test_cursor_harness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Fix the Cursor headless dispatcher launcher so Windows dispatch prefers the host-installed Cursor Agent versioned node.exe/index.js entrypoint over agent.CMD/agent.ps1 shell wrappers that can spawn visible console windows. All GT-KB artifacts, proposal files, source edits, and tests remain in-root under E:\GT-KB.

Work item description: Controlled dispatcher restart on 2026-06-30 showed Cursor harness E launching
through the host Cursor Agent shell wrapper `%LOCALAPPDATA%\cursor-agent\agent.CMD`,
which chains cmd.exe to powershell.exe cursor-agent.ps1 before node/index.js.
That shell-wrapper path can create conhost/OpenConsole windows and violates the
no-visible-console release blocker. Direct invocation of the versioned Cursor
Agent node.exe plus index.js works and should be preferred by
scripts/cursor_harness.py before .cmd/.ps1 wrappers, with tests proving wrapper
bypass and safe fallback.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4932` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/cursor_harness.py`, `platform_tests/scripts/test_cursor_harness.py`.

## Specification Links

- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - auto-linked governing or work-item specification.
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
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
- `ADR-DISPATCHER-ARCHITECTURE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20266409` - Separation Check
- `DELIB-20266506` - Authorize WI-4932 Cursor dispatcher no-window launcher repair
- `DELIB-20266502` - Separation Check
- `DELIB-20266504` - Review Findings
- `DELIB-20266454` - Applicability Preflight

## Owner Decisions / Input

- `DELIB-20266506` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4932-CURSOR-NO-WINDOW-LAUNCHER` - active project authorization covering `WI-4932`.

## Proposed Scope

- Add Cursor Agent version-directory discovery for node.exe plus index.js under the host Cursor Agent installation without treating that external installation as a GT-KB artifact or output path.
- Prefer the direct node/index argv before .cmd/.ps1/.bat candidates while preserving explicit env/CLI overrides and fallback behavior when no direct entrypoint exists.
- Add focused tests under E:\GT-KB proving shell wrappers are bypassed when the direct entrypoint is available and fallback remains intact when it is not.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Run focused cursor harness tests proving direct no-window-safe launcher selection and wrapper fallback behavior. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Verify proposal, source edits, tests, and generated bridge/report artifacts stay under E:\GT-KB. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run a bounded Cursor harness command-construction smoke or unit equivalent showing daemon-equivalent argv avoids shell wrappers. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Run ruff check/format on the touched launcher and tests; do not use retired trigger paths. |

## Acceptance Criteria

- Dispatcher-spawned Cursor harness commands do not use cmd.exe or powershell.exe wrapper paths when a versioned node/index entrypoint exists.
- Existing bridge-review and verification fail-closed output behavior remains covered by cursor harness tests.
- No dispatcher topology, credential, production deployment, external GT-KB artifact, or retired trigger fallback changes occur.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/cursor_harness.py`
- `platform_tests/scripts/test_cursor_harness.py`

## Recommended Commit Type

`feat`
