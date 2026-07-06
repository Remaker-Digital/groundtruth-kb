NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution
author_metadata_source: codex-explicit-runtime-envelope

# Implementation Proposal - Per-session role marker for claim eligibility

bridge_kind: prime_proposal
Document: gtkb-wi4853-session-role-marker-claim-eligibility
Version: 001
Date: 2026-07-06 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4853

target_paths: ["scripts/workstream_focus.py", "scripts/bridge_claim_cli.py", "scripts/implementation_authorization.py", "platform_tests/hooks/test_workstream_focus_session_role_marker.py", "platform_tests/scripts/test_work_intent_role_eligibility.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Make go_implementation eligibility depend on the per-session role marker rather than a peer-clobberable shared single-file marker. This proposal will be filed as `bridge/gtkb-wi4853-session-role-marker-claim-eligibility-001.md`, an append-only numbered bridge file.

## Requirement Sufficiency

Existing requirements are sufficient. WI-4853 records the cross-session marker-clobber defect, and the active Harness Parity Phase 2 PAUTH includes WI-4853.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded PAUTH-backed implementation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms PAUTH does not bypass GO or implementation-start gates.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves bridge-governed implementation flow.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project linkage metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived test evidence before VERIFIED.
- `GOV-SESSION-ROLE-AUTHORITY-001` - session role authority must not be revoked by unrelated session lifecycle events.
- `DCL-SESSION-ROLE-RESOLUTION-001` - role resolution must be deterministic and session-scoped.

## Prior Deliberations

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - owner authorized Harness Parity Phase 2 implementation.

## Owner Decisions / Input

- `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` - active authorization covering WI-4853.

## Proposed Scope

- Update role eligibility resolution to prefer per-session marker state and transcript/session role evidence over the shared marker fallback.
- Preserve compatibility where no per-session marker exists and the safe durable registry role can be used.
- Add tests for peer marker deletion, current-session eligibility, and unrelated-session non-interference.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Tests prove unrelated session lifecycle cannot revoke current-session Prime eligibility. |
| `DCL-SESSION-ROLE-RESOLUTION-001` | Tests cover deterministic per-session role resolution. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm live bridge lifecycle and append-only numbered file chain. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report includes exact targeted test output. |

## Acceptance Criteria

- A peer session deleting or rewriting the shared marker cannot break an active session's valid go_implementation eligibility.
- Role eligibility diagnostics explain the source used for the decision.
- No durable role assignment is changed by this slice.

## Risks / Rollback

Risk is moderate because role eligibility gates protected work. Mitigation is fail-closed tests and diagnostics. Rollback is a revert of source and tests.

## Files Expected To Change

- `scripts/workstream_focus.py`
- `scripts/bridge_claim_cli.py`
- `scripts/implementation_authorization.py`
- `platform_tests/hooks/test_workstream_focus_session_role_marker.py`
- `platform_tests/scripts/test_work_intent_role_eligibility.py`

## Recommended Commit Type

`fix`
