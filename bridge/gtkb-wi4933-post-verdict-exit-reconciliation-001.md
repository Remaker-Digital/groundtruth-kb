NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex Desktop; approval_policy=never; sandbox=danger-full-access
author_metadata_source: explicit-current-session

# Implementation Proposal - Dispatcher health classifies spawn-rate and provider backpressure without false failure

bridge_kind: prime_proposal
Document: gtkb-wi4933-post-verdict-exit-reconciliation
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4933-BACKPRESSURE-HEALTH
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4933

target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Live Ollama D dispatch proved a bridge verdict can be written and committed successfully while the worker later exits nonzero from a post-action model timeout. Dispatcher release-health must reconcile successful LO bridge transitions before recording subprocess failure evidence.

Work item description: Controlled daemon restart on 2026-06-30 produced gt bridge dispatch health WARN for loyal-opposition:F last_result=spawn_rate_limited with pending_count=2 while live workers were already in flight. OpenRouter F also previously returned HTTP 429 Too Many Requests and was classified as a generic subprocess execution failure. Dispatcher release-health should distinguish local rate limiting and provider backpressure from runtime crashes, honoring provider rate-limit signals and preserving genuine failure visibility.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4933` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

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

## Prior Deliberations

- `DELIB-20266192` - Owner decision: authorize WI-4852 watchdog-dormancy auto-restart for bounded implementation
- `DELIB-20266508` - Authorize WI-4934 dispatcher failed-recipient LO failover repair
- `DELIB-20266366` - Separation Check
- `DELIB-20266132` - Owner decision: re-scope and close WI-4670 on landed storm-containment evidence
- `DELIB-20266505` - Authorize dispatcher diagnostic health release fix

## Owner Decisions / Input

- `DELIB-20266507` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4933-BACKPRESSURE-HEALTH` - active project authorization covering `WI-4933`.

## Proposed Scope

- For Loyal Opposition dispatches, detect a verdict file produced after the dispatch launch timestamp before applying nonzero exit-code failure classification.
- Classify nonzero exit after a detected verdict as a successful reconciled dispatch, preserving the raw exit code as diagnostic metadata.
- Keep fatal worker-output markers, missing-verdict launches, non-LO launches, and nonzero exits without a verdict as failures.
- Update previous-launch-failure detection so reconciled post-verdict exits do not poison the next dispatch cycle.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Focused dispatcher-runtime tests prove health state distinguishes successful post-verdict nonzero exits from true subprocess failures. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report maps linked specs to exact tests and observed results. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- D-style dispatch evidence with exit code 1 and a post-launch VERIFIED/GO/NO-GO file resets failure state, records verdict_path/verdict_latency, and preserves diagnostic raw exit metadata without tripping circuit breaker state.
- A nonzero Loyal Opposition worker exit with no post-launch verdict remains subprocess_execution_failed and is recorded in dispatch failures.
- Fatal worker-output markers remain failure evidence even if a bridge file appears after launch.
- Focused dispatcher runtime tests cover reconciled post-verdict nonzero exits and unchanged true-failure paths.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

## Recommended Commit Type

`feat`
