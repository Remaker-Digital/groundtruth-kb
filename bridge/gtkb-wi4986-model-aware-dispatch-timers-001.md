NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder session; runtime reasoning profile not exposed

# Implementation Proposal - Model-aware generous timeout allowances for headless dispatch

bridge_kind: prime_proposal
Document: gtkb-wi4986-model-aware-dispatch-timers
Version: 001
Date: 2026-07-03 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4986-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4986

target_paths: [".api-harness/routing.toml", "scripts/dispatcher_runtime.py", "scripts/ollama_harness.py", "scripts/verify_ollama_dispatch.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_verify_ollama_dispatch.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

File a governed implementation proposal for `WI-4986` using deterministic project, authorization, target-path, and preflight wiring.

Work item description: Headless bridge dispatch currently mixes generic worker caps with harness-specific behavior: Opus 4.8 Max reviews can legitimately run 15-30 minutes, while Gemini/Qwen/DeepSeek/GPT-5.5 often return much faster. Recent stability testing also showed Ollama D timing out under the 180s route budget and Claude B being manually reaped before its normal Opus Max review window. Implement generous initial per-harness/model allowances plus elapsed-time telemetry and regular confidence analysis so future 'too long' thresholds are evidence-based per harness/model/config.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4986` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.api-harness/routing.toml`, `scripts/dispatcher_runtime.py`, `scripts/ollama_harness.py`, `scripts/verify_ollama_dispatch.py`, `platform_tests/scripts/test_dispatcher_runtime.py`, `platform_tests/scripts/test_ollama_harness.py`, `platform_tests/scripts/test_verify_ollama_dispatch.py`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
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
- `DCL-DISPATCH-ENVELOPE-RULES-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- _No prior deliberations auto-loaded; author must confirm before review._

## Owner Decisions / Input

- `DELIB-20260703-DISPATCH-HUNG-CONFIDENCE-ANALYSIS` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4986-IMPLEMENTATION-PROPOSAL-FILING` - active project authorization covering `WI-4986`.

## Proposed Scope

- Introduce generous initial per-harness/model/config timeout allowances for active headless dispatch targets instead of treating one short generic timer as authoritative.
- Record elapsed-time telemetry with harness id, model id, model configuration, role, selected bridge documents, exit state, and timeout/failure class so future thresholds can be confidence-based.
- Raise the Ollama DeepSeek V4 Pro bridge-review route/session budget enough for normal LO review attempts while preserving bounded execution and provider-failure classification.
- Keep Claude Opus 4.8 Max LO review allowance compatible with observed 15-30 minute normal reviews and avoid premature manual/automated hung classification.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run focused dispatcher runtime tests proving per-role/per-profile lifetime derivation, lease TTL alignment, and telemetry fields. |
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
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Run focused Ollama harness tests proving routing timeout resolution remains bounded while using the generous DeepSeek bridge-review budget. |

## Acceptance Criteria

- No active headless target is classified as hung before its generous profile allowance expires unless there is explicit process death, provider failure, or invalid output evidence.
- Ollama D bridge-review route resolves to deepseek-v4-pro:cloud and has a route/session timeout suitable for bridge reviews, not the prior 180s fast-fail budget.
- Dispatcher runtime evidence records enough elapsed-time and profile metadata to support regular confidence analysis by harness/model/config.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `.api-harness/routing.toml`
- `scripts/dispatcher_runtime.py`
- `scripts/ollama_harness.py`
- `scripts/verify_ollama_dispatch.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_ollama_harness.py`
- `platform_tests/scripts/test_verify_ollama_dispatch.py`

## Recommended Commit Type

`feat`
