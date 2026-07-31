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
Document: gtkb-wi4933-ollama-routing-timeout-bounds
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4933-BACKPRESSURE-HEALTH
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4933

target_paths: ["scripts/ollama_harness.py", "platform_tests/scripts/test_ollama_harness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Prime Builder proposes a bounded WI-4933 follow-up after live D testing showed .api-harness/routing.toml declares a 180s Ollama timeout but scripts/ollama_harness.py still defaults to 240s per operation and 540s per session unless explicit CLI flags are supplied.

Work item description: Controlled daemon restart on 2026-06-30 produced gt bridge dispatch health WARN for loyal-opposition:F last_result=spawn_rate_limited with pending_count=2 while live workers were already in flight. OpenRouter F also previously returned HTTP 429 Too Many Requests and was classified as a generic subprocess execution failure. Dispatcher release-health should distinguish local rate limiting and provider backpressure from runtime crashes, honoring provider rate-limit signals and preserving genuine failure visibility.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4933` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/ollama_harness.py`, `platform_tests/scripts/test_ollama_harness.py`.

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
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20266466` - Separation Check
- `DELIB-20266132` - Owner decision: re-scope and close WI-4670 on landed storm-containment evidence
- `DELIB-20266508` - Authorize WI-4934 dispatcher failed-recipient LO failover repair
- `DELIB-20266192` - Owner decision: authorize WI-4852 watchdog-dormancy auto-restart for bounded implementation
- `DELIB-20266366` - Separation Check

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4933-BACKPRESSURE-HEALTH` - active project authorization covering `WI-4933`.

## Proposed Scope

- Bind [routing.ollama].timeout_seconds from .api-harness/routing.toml into the Ollama harness runtime when CLI timeout flags are not explicitly supplied.
- Derive a bounded default session timeout from the configured route timeout so unattended D dispatch cannot silently exceed the configured route budget by several minutes.
- Preserve explicit CLI --timeout and --session-timeout overrides for tests and manual diagnostics.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Failure messages remain concise OllamaHarnessError diagnostics suitable for dispatcher report classification. |
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
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Focused Ollama harness tests prove routing timeout values govern default execution budgets and session timeout derivation. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | No retired trigger, hook, poller, or alternate runtime path is added; fix stays inside the dispatcher-owned harness path. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | No launch-window behavior changes; subprocess calls continue using CREATE_NO_WINDOW/pythonw-managed dispatcher wrappers. |

## Acceptance Criteria

- Ollama D dispatch uses the configured route timeout by default for /api/tags, chat turns, guard calls, and tool subprocess caps.
- The default session timeout is deterministically bounded from routing config and fails with concise OllamaHarnessError evidence instead of hanging silently.
- Existing explicit CLI timeout behavior remains backward compatible.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_ollama_harness.py`

## Recommended Commit Type

`feat`
