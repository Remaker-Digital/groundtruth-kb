NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop, GPT-5, Prime Builder, dispatcher release-health hardening

# Implementation Proposal - Dispatcher diagnose reports DEGRADED for healthy work-intent and unselected recipients

bridge_kind: prime_proposal
Document: gtkb-wi4931-dispatcher-diagnose-health-alignment
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4931-DIAGNOSE-HEALTH
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4931

target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Fix a release-health diagnostic mismatch where dispatcher_runtime.py --diagnose reports DEGRADED despite canonical bridge dispatch health PASS after soft reset.

Work item description: After a governed soft reset, gt bridge dispatch health --json reports PASS while python scripts\dispatcher_runtime.py --diagnose reports DEGRADED. The renderer treats expected work_intent_already_held suppression and active dispatchable harnesses with no state recorded on the current tick as unrecognized states. Release-health surfaces must agree: diagnose should stay HEALTHY when canonical dispatch health is PASS and recipients are idle, suppressed by work intent, or simply not selected/recorded for that tick.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4931` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/dispatcher_runtime.py`, `platform_tests/scripts/test_dispatcher_runtime.py`.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - auto-linked governing or work-item specification.
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
- `ADR-DISPATCHER-ARCHITECTURE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20266505` - Authorize dispatcher diagnostic health release fix
- `DELIB-20266343` - Loyal Opposition Review - WI-4894 Restore pythonw-safe reaper output
- `DELIB-20266177` - Spec-to-Test Mapping
- `DELIB-20266081` - Bridge Review — gtkb-wi4789-dispatch-health-perrole-fail-boundary-003
- `DELIB-20266178` - Separation Check

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4931-DIAGNOSE-HEALTH` - active project authorization covering `WI-4931`.

## Proposed Scope

- Treat expected work_intent_already_held suppression as healthy in dispatcher_runtime.py --diagnose liveness rendering.
- Do not mark active dispatchable harnesses with no current recipient state as DEGRADED when the canonical dispatch health state is otherwise PASS/no-pending; render them as not evaluated or idle instead.
- Add focused regression coverage in platform_tests/scripts/test_dispatcher_runtime.py for the healthy mixed state observed on 2026-06-30.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Add/adjust unit coverage proving diagnose health output aligns with canonical dispatch health for work-intent suppression and unrecorded non-selected recipients. |
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
| `ADR-DISPATCHER-ARCHITECTURE-001` | Run focused dispatcher runtime tests plus live daemon health/status checks to verify daemon-backed dispatch remains PASS with no routing-policy change. |

## Acceptance Criteria

- python scripts\\dispatcher_runtime.py --diagnose reports HEALTHY and no DEGRADED after current daemon soft-reset/idle state.
- gt bridge dispatch health --json remains PASS after the change.
- Focused dispatcher runtime pytest covering diagnose/work-intent states passes.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

## Recommended Commit Type

`feat`
