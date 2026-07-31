NEW
::init gtkb lo
::open build
author_identity: claude
author_harness_id: B
author_session_context_id: d067ca16-171b-4b2e-89f5-642340e605a6
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: claude-code-interactive-prime-builder-via-init-gtkb-pb

# Implementation Proposal - Cloud-harness publisher-only recovery lacks tool_choice forcing on OpenAI-compatible dialect

bridge_kind: prime_proposal
Document: gtkb-wi5495-publisher-recovery-tool-choice-forcing
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5495

target_paths: ["scripts/cloud_harness_base.py", "scripts/ollama_harness.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_ollama_harness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Root-caused and directly reproduced (full daemon-faithful nested-process replication, exit code 1 at t+75s) the D/F Loyal Opposition dispatch livelock: bridge-verdict publisher-only-recovery mode restricts the OFFERED tool schema to PublishBridgeVerdict but only mechanically FORCES compliance for the Anthropic dialect (force_anthropic_publisher_tool_choice); the OpenAI-compatible dialect used by both F/OpenRouter (cloud_harness_base.py) and D/Ollama (ollama_harness.py, a separate duplicated implementation with NO forcing at all) has no equivalent, so a less-strictly-compliant model can keep emitting out-of-schema tool calls, exhausting the 3-attempt recovery budget and crashing the worker with an abandoned verdict-publish claim that blocks the same document for its TTL. Fix: add the standard OpenAI Chat Completions forced-function tool_choice directive to both harnesses during recovery, mirroring the existing Anthropic-only pattern. Fast-lane reliability defect; source plus test only.

Work item description: Root cause of the D/F verdict-claim livelock diagnosed via direct reproduction: the multi-turn agentic loop's publisher-only-recovery mode (entered after a stalled/failed bridge-verdict publish attempt) restricts the OFFERED tool schema to just PublishBridgeVerdict, but only cloud_harness_base.py's Anthropic-dialect branch (force_anthropic_publisher_tool_choice) actually forces the model to comply via a tool_choice directive. The OpenAI-compatible dialect branch used by F/OpenRouter has no equivalent forcing, and scripts/ollama_harness.py (a separate, duplicated implementation used by D/Ollama) has NO tool_choice forcing at all, in any mode. A non-strictly-compliant model (observed: deepseek-v4-flash on OpenRouter) can therefore keep calling out-of-schema tools (observed: Read) during recovery, exhausting MAX_BRIDGE_VERDICT_RECOVERY_TURNS (3) and crashing the worker via a hard raised error with no further diagnostic output captured, abandoning its acquired verdict-publish claim until the claim's TTL naturally expires and the next dispatched worker repeats the identical failure on the same document. Directly reproduced via a full daemon-faithful nested-process replication: exit code 1 at t+75s, stderr message literally 'bridge verdict publisher recovery exhausted after 4 attempts; last failure: publisher-only recovery rejected non-publisher tool call(s): Read'. Fix: add the OpenAI Chat Completions forced-function tool_choice ({type: function, function: {name: PublishBridgeVerdict}}) to both cloud_harness_base.py's openai-chat dialect branch during publisher-only recovery, and the equivalent payload field in ollama_harness.py's chat-turn loop, mirroring the existing (Anthropic-only) forcing pattern.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5495` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/cloud_harness_base.py`, `scripts/ollama_harness.py`, `platform_tests/scripts/test_cloud_harness_base.py`, `platform_tests/scripts/test_ollama_harness.py`.

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
- `GOV-RELIABILITY-FAST-LANE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666257` - Loyal Opposition Proposal Review - WI-5253 Ollama D Publisher Failure Recovery
- `DELIB-202666266` - Loyal Opposition Proposal Review - WI-5258 Alibaba H HTTP 400 Publisher Recovery
- `DELIB-202666227` - Loyal Opposition Verification - gtkb-wi5224-provider-verdict-completion-contract - 005
- `DELIB-202666174` - WI-5211 Proposal Review Verdict — GO
- `DELIB-202666256` - Loyal Opposition Verification Verdict - WI-5253 Ollama Publisher Recovery

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` - active project authorization covering `WI-5495`.

## Proposed Scope

- In cloud_harness_base.py's main agentic-loop turn handler, extend the existing publisher-only-recovery tool_choice forcing block (currently gated to profile.dialect == DIALECT_ANTHROPIC_MESSAGES) with a parallel branch for DIALECT_OPENAI_CHAT that sets payload['tool_choice'] = {'type': 'function', 'function': {'name': PUBLISH_BRIDGE_VERDICT_TOOL}} (the standard OpenAI Chat Completions forced-function-call directive), so OpenRouter-routed models are mechanically constrained to the offered PublishBridgeVerdict schema during recovery instead of relying on unenforced prompt-level restriction.
- In ollama_harness.py's chat-turn loop, add the same OpenAI-compatible forced-function tool_choice field to the payload dict whenever the loop is in publisher-only-recovery mode (bridge_verdict_required and bridge_recovery_turns and not bridge_verdict_published), matching the same schema shape used by the cloud_harness_base.py fix.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | pytest platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_ollama_harness.py; report pass/fail counts in the implementation report. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-RELIABILITY-FAST-LANE-001` | New/extended unit tests in test_cloud_harness_base.py and test_ollama_harness.py assert tool_choice forcing is present during publisher-only recovery for the openai-chat dialect in both harnesses; pytest both files. |

## Acceptance Criteria

- A unit test asserts that when publisher-only recovery is active and the dialect is openai-chat, the built payload includes tool_choice forcing PublishBridgeVerdict by name (test_cloud_harness_base.py).
- A unit test asserts the equivalent tool_choice field is present in ollama_harness.py's payload construction under the same recovery condition (test_ollama_harness.py).
- ruff check and ruff format --check pass on both changed source files.
- A live direct-invocation smoke test (matching the diagnostic replication in this thread) against a real bridge document completes without raising the publisher-recovery-exhausted error.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/cloud_harness_base.py`
- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_cloud_harness_base.py`
- `platform_tests/scripts/test_ollama_harness.py`

## Recommended Commit Type

`feat`
