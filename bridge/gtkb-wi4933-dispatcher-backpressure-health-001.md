NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1778-579b-7f03-a949-9cbae207273a
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: Codex desktop Auto-builder automation; approval_policy=never; sandbox=danger-full-access; cwd=E:\GT-KB
author_metadata_source: explicit-runtime-envelope

# Implementation Proposal - Dispatcher health classifies spawn-rate and provider backpressure without false failure

bridge_kind: prime_proposal
Document: gtkb-wi4933-dispatcher-backpressure-health
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4933-BACKPRESSURE-HEALTH
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4933

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "scripts/dispatcher_runtime.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair dispatcher health and runtime classification so spawn-rate throttling and provider rate limits are reported as backpressure instead of false runtime failures.

Work item description: Controlled daemon restart on 2026-06-30 produced gt bridge dispatch health WARN for loyal-opposition:F last_result=spawn_rate_limited with pending_count=2 while live workers were already in flight. OpenRouter F also previously returned HTTP 429 Too Many Requests and was classified as a generic subprocess execution failure. Dispatcher release-health should distinguish local rate limiting and provider backpressure from runtime crashes, honoring provider rate-limit signals and preserving genuine failure visibility.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4933` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, `scripts/dispatcher_runtime.py`, `platform_tests/scripts/test_bridge_dispatch_config.py`, `platform_tests/scripts/test_dispatcher_runtime.py`.

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
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
- `ADR-DISPATCHER-ARCHITECTURE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20266192` - Owner decision: authorize WI-4852 watchdog-dormancy auto-restart for bounded implementation
- `DELIB-20266505` - Authorize dispatcher diagnostic health release fix
- `DELIB-20266507` - Authorize WI-4933 dispatcher backpressure health classification repair
- `DELIB-20266133` - Owner decision: re-home all open DISPATCHER-COMPLETION work and retire the project
- `DELIB-20266132` - Owner decision: re-scope and close WI-4670 on landed storm-containment evidence

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4933-BACKPRESSURE-HEALTH` - active project authorization covering `WI-4933`.

## Proposed Scope

- Classify local spawn-rate throttling with live in-flight workers as dispatcher backpressure rather than a runtime crash or release-blocking false failure.
- Classify provider rate-limit/backpressure evidence, including OpenRouter HTTP 429 markers, separately from generic subprocess execution failure while preserving genuine failure visibility.
- Update dispatcher health/report classifications and focused runtime tests only; do not mutate dispatcher topology/config, credentials, production deployment, or retired trigger fallback.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Run focused bridge dispatch config health tests proving backpressure classifications are visible, specific, and not false runtime crashes. |
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
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run focused dispatcher runtime tests proving provider rate-limit/backpressure state is recorded and retried without topology/config mutation. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Run ruff and focused dispatcher health/runtime tests proving centralized dispatcher state remains the authority. |

## Acceptance Criteria

- gt bridge dispatch health distinguishes spawn-rate/provider backpressure from runtime crashes while keeping actionable warnings visible.
- Provider 429/backpressure evidence is surfaced with a specific classification instead of generic subprocess execution failure.
- Focused bridge dispatch config and dispatcher runtime tests cover benign backpressure and genuine failure non-regressions.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

## Recommended Commit Type

`feat`
