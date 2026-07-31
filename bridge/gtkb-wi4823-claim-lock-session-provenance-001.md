NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution
author_metadata_source: codex-explicit-runtime-envelope

# Implementation Proposal - Work-intent claim locking and session provenance

bridge_kind: prime_proposal
Document: gtkb-wi4823-claim-lock-session-provenance
Version: 001
Date: 2026-07-06 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4823

target_paths: ["scripts/bridge_work_intent_registry.py", "scripts/bridge_claim_cli.py", "scripts/implementation_authorization.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/scripts/test_bridge_claim_cli.py", "platform_tests/scripts/test_dispatcher_runtime_work_intent.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Harden bridge work-intent claims and report author provenance so concurrent Prime sessions cannot implement the same GO slice and cannot stamp a report with another session context. This proposal will be filed as `bridge/gtkb-wi4823-claim-lock-session-provenance-001.md`, an append-only numbered bridge file.

## Requirement Sufficiency

Existing requirements are sufficient. WI-4823 records the concrete collision class, and the active Harness Parity Phase 2 PAUTH includes WI-4823.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded PAUTH-backed implementation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms PAUTH does not bypass GO or implementation-start gates.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves bridge-governed implementation flow.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project linkage metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived test evidence before VERIFIED.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher architecture must prevent duplicate implementations and false provenance.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - concurrency and provenance behavior must be enforced across harnesses.

## Prior Deliberations

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - owner authorized Harness Parity Phase 2 implementation.

## Owner Decisions / Input

- `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` - active authorization covering WI-4823.

## Proposed Scope

- Make implementation-start claims exclusive across concurrent harness sessions for the same bridge thread.
- Ensure report author metadata is derived from the filing session, not a borrowed claim or shared marker.
- Add tests for claim contention, stale holder handling, and provenance mismatch refusal.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Tests prove duplicate implementation claims fail closed for same GO thread. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Tests cover cross-harness contention/provenance cases. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm live bridge lifecycle and append-only numbered file chain. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report includes exact targeted test output. |

## Acceptance Criteria

- A second Prime implementer cannot begin the same GO slice while a valid claim exists.
- A report cannot stamp another session's context id as its author context.
- Stale claims still expire or release through the intended lifecycle.

## Risks / Rollback

Risk is high because claim enforcement can block implementation. Mitigation is focused tests and stale-claim coverage. Rollback is a revert of source and tests.

## Files Expected To Change

- `scripts/bridge_work_intent_registry.py`
- `scripts/bridge_claim_cli.py`
- `scripts/implementation_authorization.py`
- `platform_tests/scripts/test_bridge_work_intent_registry.py`
- `platform_tests/scripts/test_bridge_claim_cli.py`
- `platform_tests/scripts/test_dispatcher_runtime_work_intent.py`

## Recommended Commit Type

`fix`
