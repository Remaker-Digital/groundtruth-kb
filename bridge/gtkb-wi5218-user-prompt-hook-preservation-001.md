NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5474-93a6-7f70-8e54-d6d8b0a31bb4
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex desktop interactive Prime Builder; build activity; full GT-KB governance

# Implementation Proposal - Preserve provider prompts across UserPromptSubmit enrichment-hook failures

bridge_kind: prime_proposal
Document: gtkb-wi5218-user-prompt-hook-preservation
Version: 001
Date: 2026-07-12 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5218-USER-PROMPT-HOOK-20260712
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5218

target_paths: ["scripts/cloud_harness_base.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_alibaba_cloud_studio_harness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Genuine Alibaba H dispatch `2026-07-12T22-56-18Z-loyal-opposition-H-65b019` never reached a provider turn. The native-full `UserPromptSubmit` hook `glossary-expansion.py` exceeded its registered timeout, and shared `invoke_native_hooks` aborted the complete review even though this event provides prompt enrichment and its output is not a mutating-tool authorization decision.

Add event-specific fail-soft execution semantics for `UserPromptSubmit`: timeout, nonzero exit, empty output, malformed informational JSON, and non-object informational output preserve the original provider prompt and continue to later registered hooks. Explicit policy blocks remain fail-closed. `PreToolUse` and the guard-adapter floor remain unchanged and fail-closed. SessionStart, PostToolUse, and Stop retain their existing separately governed semantics.

## Claim

Prime Builder proposes a bounded shared-native-hook lifecycle correction and focused tests only. It neither raises nor lowers any hook/provider/worker timeout and does not change dispatcher, routing, registry, credentials, or bridge publication authority.

## Requirement Sufficiency

Existing requirements are sufficient. `DELIB-202666173` authorizes correction of every defect found during genuine six-harness proof; WI-5218 and TEST-11372 define the live failure and exact preservation contract.

## In-Root Placement Evidence

All three targets are under `E:\GT-KB`. No settings registration, dispatcher runtime/config, lease, registry, or external dependency is in scope.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - H must reach and complete genuine assigned-role provider work.
- `ADR-CLOUD-HARNESS-TEMPLATE-001` - lifecycle semantics belong in the shared native-full cloud runtime.
- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` - H is the native-full adopter that exposed the defect.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - publication remains exclusively governed after the prompt survives.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - original dispatcher session/model provenance remains intact.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - all 600/900/28800/29400/29700 allowances remain unchanged.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - guard-adapter and PreToolUse fail-closed behavior is not weakened.
- `ADR-CROSS-HARNESS-PARITY-001` - lifecycle maintenance failures must not erase valid provider work.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - tests distinguish enrichment from authorization events.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requirements are linked before mutation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification executes the mapped lifecycle tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - exact project, work item, PAUTH, and targets are declared.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the live hook failure has a durable defect lifecycle.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - dispatch, test, proposal, report, and verdict remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the observed blocker triggers governed correction.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - this is GT-KB platform harness work.

## Prior Deliberations

- `DELIB-202666173` - complete six-harness governed proof and correct every discovered defect.
- `DELIB-20260711-WI5198-BOUNDED-IMPLEMENTATION-AUTHORIZATION` - native-hook empty-output predecessor.
- `bridge/gtkb-wi5204-h-stop-hook-completion-preservation-004.md` - VERIFIED Stop event-specific preservation.
- `bridge/gtkb-wi5213-posttooluse-completion-preservation-004.md` - VERIFIED PostToolUse event-specific preservation.

## Owner Decisions / Input

- `DELIB-202666173` supplies owner authority for this discovered-defect correction.
- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5218-USER-PROMPT-HOOK-20260712` forbids PreToolUse/guard weakening, dispatcher/routing changes, allowance reduction, direct runtime/lease mutation, and unrelated work.

## Proposed Scope

- Identify `UserPromptSubmit` as a non-mutating prompt-enrichment event inside the existing native hook executor.
- Continue to later registered UserPromptSubmit hooks after execution timeout, nonzero exit, empty output, malformed JSON, or non-object informational output; the original `messages` user prompt remains byte-for-byte present.
- Preserve valid informational object handling and fail closed when valid output carries an explicit block reason.
- Keep malformed settings, unsupported event/type, invalid registration, and invalid timeout configuration fail-closed because those are configuration-contract defects, not hook execution outcomes.
- Leave PreToolUse, guard adapter, SessionStart, PostToolUse, and Stop behavior unchanged.
- Re-run shared, Alibaba, OpenRouter, and hook parity suites, then require fresh H dispatcher proof.

## Specification-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001`, H adoption ADR | Fresh H work reaches provider turns and publishes a substantive canonical verdict. |
| `ADR-CLOUD-HARNESS-TEMPLATE-001` | Shared-base parameterized tests cover timeout, nonzero, empty, malformed, non-object, valid informational, and explicit block outcomes. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, provenance carrier | Existing publisher tests prove no publication or metadata authority changes. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | PreToolUse and guard timeout/nonzero/malformed/deny regressions remain fail-closed. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Existing runtime tests prove 600/900/28800/29400/29700 values unchanged. |
| Cross-harness parity carriers | OpenRouter and Alibaba shared-base suites prove only native-full UserPromptSubmit execution outcomes change. |
| Verification/lifecycle carriers | Candidate/live applicability and clause preflights pass, Ruff passes, exact diff is clean, and unrelated dirty paths remain excluded. |

## Acceptance Criteria

- UserPromptSubmit timeout/nonzero/empty/malformed/non-object informational output cannot discard, replace, or suppress the original provider prompt.
- A later valid UserPromptSubmit hook still executes after an earlier maintenance failure.
- Valid explicit block output remains fail-closed and prevents provider invocation.
- PreToolUse and guard failures remain fail-closed; PostToolUse and Stop retain their independently verified semantics.
- All generous turn/operation/session/worker/lease limits remain unchanged.
- Fresh genuine H work produces a substantive canonical verdict or another separately governed defect.
- Independent LO returns VERIFIED and creates one focused commit containing only the three approved source/test paths and this bridge chain.

## Risks / Rollback

Risk is over-broad fail-open behavior. The implementation is restricted to execution outcomes of the non-mutating UserPromptSubmit event; configuration defects and explicit policy blocks still fail closed. Rollback reverts the three targets while retaining append-only evidence.

## Files Expected To Change

- `scripts/cloud_harness_base.py`
- `platform_tests/scripts/test_cloud_harness_base.py`
- `platform_tests/scripts/test_alibaba_cloud_studio_harness.py`

## Recommended Commit Type

`fix`
