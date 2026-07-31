NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution
author_metadata_source: codex-explicit-runtime-envelope

# Implementation Proposal - Topic-router deliberation stance context

bridge_kind: prime_proposal
Document: gtkb-wi4866-topic-router-deliberation-stance
Version: 001
Date: 2026-07-06 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4866

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/topic_router.py", "platform_tests/scripts/test_topic_router_operator_context.py", "config/agent-control/activity-disposition-profiles.toml"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Correct the topic-router operator context so capture-and-clarify deliberation lanes do not receive Prime-Builder do-work startup briefings that contradict the activity profile stance. This proposal will be filed as `bridge/gtkb-wi4866-topic-router-deliberation-stance-001.md`, an append-only numbered bridge file.

## Requirement Sufficiency

Existing requirements are sufficient. WI-4866 records the shared renderer defect, and the active Harness Parity Phase 2 PAUTH includes WI-4866.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded PAUTH-backed implementation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms PAUTH does not bypass GO or implementation-start gates.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves bridge-governed implementation flow.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project linkage metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived test evidence before VERIFIED.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - activity context behavior must not diverge silently across harnesses.
- `GOV-SESSION-SELF-INITIALIZATION-001` - startup/operator context must match session purpose and not fabricate action pressure.

## Prior Deliberations

- `DELIB-S20260626-CROSS-HARNESS-PARITY-ENFORCEMENT-GAP` - related parity enforcement context.
- `DELIB-S20260626-PARITY-INTERVIEW-CLUSTER3-DELIVERY` - source interview context.
- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - owner authorized Harness Parity Phase 2 implementation.

## Owner Decisions / Input

- `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` - active authorization covering WI-4866.

## Proposed Scope

- Update operator-context rendering to respect the activity profile history_state and stance.
- Add tests for deliberation/capture-and-clarify lanes, Prime implementation lanes, and default fallback behavior.
- Preserve existing startup briefing content for do-work lanes where it is appropriate.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-SESSION-SELF-INITIALIZATION-001` | Tests prove deliberation lanes omit do-work startup briefing. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Tests cover shared renderer behavior independent of harness. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm live bridge lifecycle and append-only numbered file chain. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report includes exact targeted test output. |

## Acceptance Criteria

- Deliberation/capture-and-clarify lanes receive stance-appropriate context.
- Implementation lanes still receive actionable Prime briefing when configured.
- Tests lock the shared renderer behavior.

## Risks / Rollback

Risk is moderate because prompt/context changes can affect agent behavior. Mitigation is narrow activity-profile tests. Rollback is a revert of source/config/tests.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/session/topic_router.py`
- `platform_tests/scripts/test_topic_router_operator_context.py`
- `config/agent-control/activity-disposition-profiles.toml`

## Recommended Commit Type

`fix`
