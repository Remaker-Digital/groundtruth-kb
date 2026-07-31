NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop, GPT-5, Prime Builder, dispatcher release-health hardening

# Implementation Proposal - Dispatcher health classifies spawn-rate and provider backpressure without false failure

bridge_kind: prime_proposal
Document: gtkb-wi4933-dispatch-backpressure-health
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4933-BACKPRESSURE-HEALTH
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4933

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "scripts/openrouter_harness.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/scripts/test_openrouter_harness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Fix dispatcher health and provider handling so local spawn-rate throttling and OpenRouter 429 backpressure are classified as bounded/actionable backpressure instead of unqualified runtime failure, while preserving genuine failure visibility.

Work item description: Controlled daemon restart on 2026-06-30 produced gt bridge dispatch health WARN for loyal-opposition:F last_result=spawn_rate_limited with pending_count=2 while live workers were already in flight. OpenRouter F also previously returned HTTP 429 Too Many Requests and was classified as a generic subprocess execution failure. Dispatcher release-health should distinguish local rate limiting and provider backpressure from runtime crashes, honoring provider rate-limit signals and preserving genuine failure visibility.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4933` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, `scripts/openrouter_harness.py`, `platform_tests/scripts/test_bridge_dispatch_config.py`, `platform_tests/scripts/test_openrouter_harness.py`.

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
- `DELIB-20266133` - Owner decision: re-home all open DISPATCHER-COMPLETION work and retire the project
- `DELIB-20266507` - Authorize WI-4933 dispatcher backpressure health classification repair
- `DELIB-20266366` - Separation Check

## Owner Decisions / Input

- `DELIB-20266507` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4933-BACKPRESSURE-HEALTH` - active project authorization covering `WI-4933`.

## Proposed Scope

- Reclassify spawn_rate_limited from runtime-crash failure to benign/backpressure health state when dispatch is bounded or workers are in flight.
- Teach OpenRouter harness retry logic to honor Retry-After when present and preserve clear 429/provider-backpressure diagnostics.
- Update focused health and OpenRouter tests so provider backpressure is visible but does not falsely fail release health by itself.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Run bridge dispatch config tests covering spawn_rate_limited/backpressure classification and preserved genuine failure findings. |
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
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run OpenRouter harness tests covering Retry-After/backpressure handling without live credential dependence. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Run ruff check/format on touched source/tests and a read-only gt bridge dispatch health check after implementation. |

## Acceptance Criteria

- gt bridge dispatch health does not emit dispatch runtime failure solely for spawn_rate_limited while live/in-flight dispatch is bounded.
- OpenRouter HTTP 429 diagnostics are classified as provider/rate-limit backpressure, not generic subprocess failure, and Retry-After is honored where available.
- Genuine launch/provider failures still surface as actionable health findings.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `scripts/openrouter_harness.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`
- `platform_tests/scripts/test_openrouter_harness.py`

## Recommended Commit Type

`feat`
