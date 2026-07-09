NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5
author_model_version: codex-desktop
author_model_configuration: Codex Desktop Prime Builder session

# Implementation Proposal - Expand no-window process-spawn audit to every harness launcher, verifier, benchmark runner, and recurring worker

bridge_kind: prime_proposal
Document: gtkb-wi4905-dispatch-topology-flex-release-gate
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4905

target_paths: ["harness-state/harness-registry.json", "config/dispatcher/rules.toml", "platform_tests/scripts/test_cross_harness_protocol_parity.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Supplement WI-4905 to flex the dispatcher topology for release: active harnesses become dispatch-receivable, Codex/Cursor are event sources, and the protocol parity gate reflects the no-waiver owner directive.

Work item description: WI-4896 resolved dispatcher-owned background console flashes, but Phase 2 needs full coverage. Extend the static/runtime no-window spawn audit to all Python and PowerShell launch surfaces for harness adapters, readiness verifiers, benchmark runners, recurring evaluators, dispatcher helpers, and provider wrappers, including scripts such as verify_antigravity_dispatch.py that are outside the current release-runtime allowlist.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4905` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `harness-state/harness-registry.json`, `config/dispatcher/rules.toml`, `platform_tests/scripts/test_cross_harness_protocol_parity.py`.

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
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `ADR-CROSS-HARNESS-PARITY-001` - auto-linked governing or work-item specification.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20266423` - Separation Check
- `DELIB-20266349` - Separation Check
- `DELIB-20266413` - Separation Check
- `DELIB-20266353` - GO - gtkb-wi4896-startup-console-residual - Boot-time and Minute-cadence Windows console/focus-steal fix
- `DELIB-20266470` - Separation Check

## Owner Decisions / Input

- `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` - active project authorization covering `WI-4905`.

## Proposed Scope

- Align active harness dispatch topology with the owner directive that no harness is waived: every active harness record must be dispatch-receivable unless a concrete failing health gate disables it.
- Restore event-source capability flags for hook-capable desktop harnesses A/Codex and E/Cursor while preserving daemon-owned dispatch and excluding retired hook-triggered workers.
- Keep the change to registry/config/test surfaces only; do not change harness command implementations or revive cross-harness trigger paths.

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
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Run focused cross-harness protocol parity tests and dispatcher health/status checks. |
| `ADR-CROSS-HARNESS-PARITY-001` | Verify active harness topology is represented in both durable harness registry and dispatcher rules without adding waivers. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Confirm no cross_harness_bridge_trigger.py, single_harness_bridge_automation.py, dispatcher-daemon.cmd, or gtkb_dispatcher_daemon.py hook registration is introduced. |

## Acceptance Criteria

- Focused cross-harness protocol parity tests pass.
- gt bridge dispatch health/status reflect the updated topology without retired hook-triggered dispatch registrations.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `harness-state/harness-registry.json`
- `config/dispatcher/rules.toml`
- `platform_tests/scripts/test_cross_harness_protocol_parity.py`

## Recommended Commit Type

`feat`
