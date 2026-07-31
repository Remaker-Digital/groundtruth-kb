NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-restart-sessionstart-hardening-20260630T0315Z
author_model: GPT-5 Codex
author_model_version: 2026-06
author_model_configuration: Codex Desktop Prime Builder interactive restart; hooks manually disabled in UI for diagnosis; cwd=E:\GT-KB

# Implementation Proposal - Expand no-window process-spawn audit to every harness launcher, verifier, benchmark runner, and recurring worker

bridge_kind: prime_proposal
Document: gtkb-wi4905-sessionstart-dispatch-marker-hardening
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4905

target_paths: ["scripts/session_start_dispatch_core.py", "platform_tests/scripts/test_codex_session_start_dispatcher.py", "platform_tests/scripts/test_claude_session_start_dispatcher.py", "platform_tests/scripts/test_codex_hook_parity.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Harden SessionStart bridge-dispatch detection so an inherited or test leaked GTKB_BRIDGE_POLLER_RUN_ID cannot make an interactive Codex restart behave as an auto-dispatched worker.

Work item description: WI-4896 resolved dispatcher-owned background console flashes, but Phase 2 needs full coverage. Extend the static/runtime no-window spawn audit to all Python and PowerShell launch surfaces for harness adapters, readiness verifiers, benchmark runners, recurring evaluators, dispatcher helpers, and provider wrappers, including scripts such as verify_antigravity_dispatch.py that are outside the current release-runtime allowlist.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4905` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/session_start_dispatch_core.py`, `platform_tests/scripts/test_codex_session_start_dispatcher.py`, `platform_tests/scripts/test_claude_session_start_dispatcher.py`, `platform_tests/scripts/test_codex_hook_parity.py`.

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
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` - auto-linked governing or work-item specification.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20266423` - Separation Check
- `DELIB-20266353` - GO - gtkb-wi4896-startup-console-residual - Boot-time and Minute-cadence Windows console/focus-steal fix
- `DELIB-20266349` - Separation Check
- `DELIB-20266107` - Owner decision: reconcile dispatch can_receive_dispatch drift to Honest-ON (WI-4821)
- `DELIB-20266413` - Separation Check

## Owner Decisions / Input

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` - active project authorization covering `WI-4905`.

## Proposed Scope

- Change env-var-only GTKB_BRIDGE_POLLER_RUN_ID handling from auto-dispatch to normal startup fallback while keeping the LEGACY_FALLBACK enum value for diagnostic compatibility.
- Require the canonical GTKB_BRIDGE_DISPATCH_KEYWORD side channel for the SessionStart bridge-auto-dispatch context.
- Update Codex and Claude SessionStart tests plus Codex hook parity coverage so regression tests cannot pollute live hook breadcrumbs or treat run-id-only state as dispatch authority.

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
| `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` | python -m pytest platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_claude_session_start_dispatcher.py -q --tb=short |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | python -m pytest platform_tests/scripts/test_codex_hook_parity.py -q --tb=short |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | python -m py_compile scripts/session_start_dispatch_core.py |

## Acceptance Criteria

- Interactive SessionStart with only GTKB_BRIDGE_POLLER_RUN_ID present emits a normal startup/degraded startup payload, not Bridge Auto-Dispatch Session.
- True daemon-dispatched SessionStart with both GTKB_BRIDGE_POLLER_RUN_ID and GTKB_BRIDGE_DISPATCH_KEYWORD still emits Bridge Auto-Dispatch Session.
- Focused Codex and Claude SessionStart tests pass and no live last-session-start breadcrumb is left with the test-run-002 auto-dispatch context.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/session_start_dispatch_core.py`
- `platform_tests/scripts/test_codex_session_start_dispatcher.py`
- `platform_tests/scripts/test_claude_session_start_dispatcher.py`
- `platform_tests/scripts/test_codex_hook_parity.py`

## Recommended Commit Type

`feat`
