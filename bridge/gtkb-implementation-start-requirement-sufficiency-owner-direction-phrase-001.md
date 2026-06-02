NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-gtkb-pb-2026-06-02
author_model: GPT-5 Codex
author_model_version: 2026-06-02
author_model_configuration: reasoning=high

bridge_kind: implementation_proposal
Document: gtkb-implementation-start-requirement-sufficiency-owner-direction-phrase
Project Authorization: PAUTH-WI-4213-ACTIVE-STATUS-CAPABILITY-GATE
Project: PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH
Work Item: WI-4213
target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]

# Implementation Proposal: Implementation-Start Requirement-Sufficiency Phrase Parity

## Summary

The approved WI-4213 formalization proposal uses a concrete sufficiency statement: "Existing owner direction and WI-4213 are sufficient to formalize the active-status capability gate." The implementation-start gate currently treats that section as missing because its allow-list recognizes narrower stock phrases only. This creates a false-negative start blocker after Loyal Opposition has already approved the proposal.

Implement a narrow parser update so `scripts/implementation_authorization.py` recognizes that owner-direction/work-item sufficiency phrase while preserving the explicit-gap and unapproved-phrase rejection behavior.

## Prior Deliberations

- `bridge/gtkb-active-status-capability-gate-formalization-001.md` and `bridge/gtkb-active-status-capability-gate-formalization-002.md` provide the approved WI-4213 proposal and GO verdict whose requirement-sufficiency phrase exposed the false negative.
- WI-4213 records the active-status capability-gate correction and keeps WI-3513 as the durable bridge write-contention fix.
- DELIB-2813 records the owner directive to continue until the listed items are completed under the active project authorization.
- WI-3410 and its implementation-start-gate slice established the existing requirement-sufficiency section gate; this change preserves that gate and adds parity for an approved owner-direction phrasing.

## Owner Decisions / Input

No new owner decision is required. This is a narrow implementation-start parser parity fix inside the active WI-4213 project authorization and does not change proposal-governance approval requirements.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- ADR-CODEX-HOOK-PARITY-FALLBACK-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- DCL-PROJECT-AUTHORIZATION-ENVELOPE-001
- PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-STANDING-BACKLOG-001
- ADR-ROLE-STATUS-ORTHOGONALITY-001
- DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001
- REQ-HARNESS-REGISTRY-001

## Requirement Sufficiency

Existing requirements sufficient.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Parser/test-only change; no credentials, environment values, or secret material. | Helper credential scan and diff review. | |
| CQ-PATHS-001 | Yes | Mutate only the start-gate parser and its tests. | `git diff --name-only -- scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py`. | |
| CQ-COMPLEXITY-001 | Yes | Add one bounded phrase to the existing normalized phrase matcher. | Targeted pytest coverage. | |
| CQ-CONSTANTS-001 | Yes | Keep the phrase in the existing requirement-sufficiency phrase tuple. | Source review and tests. | |
| CQ-SECURITY-001 | Yes | Preserve explicit-gap and unapproved-phrase rejection semantics. | Targeted negative tests remain in scope. | |
| CQ-DOCS-001 | N/A | Runtime parser behavior only; no user-facing documentation changes. | N/A. | No documentation surface is changed. |
| CQ-TESTS-001 | Yes | Add regression coverage for the approved owner-direction/work-item phrasing and packet creation. | `python -m pytest platform_tests\scripts	est_implementation_authorization.py -q --tb=short`. | |
| CQ-LOGGING-001 | N/A | No logging behavior changes. | N/A. | Parser-only change. |
| CQ-VERIFICATION-001 | Yes | Run targeted pytest plus ruff check and format check. | Commands listed in the implementation report. | |

## Scope

In scope:

- Add a bounded recognized requirement-sufficiency phrase for approved owner-direction/work-item language.
- Add tests proving the phrase is accepted and the existing rejection behavior remains intact.
- Re-run the WI-4213 formalization start-gate command after the fix to confirm the original approved proposal is unblocked.

Out of scope:

- Changing bridge proposal content already approved by Loyal Opposition.
- Weakening the requirement-sufficiency gate to accept arbitrary prose.
- Changing the WI-4213 formal specs, harness registry, dispatch resolver, or bridge writer serialization.
- Any WI-3513 write-contention implementation.

## Acceptance Criteria

- `requirement_sufficiency_state` returns `sufficient` for `Existing owner direction and WI-4213 are sufficient to formalize the active-status capability gate.`
- Existing explicit-gap and unapproved-phrase tests continue to reject insufficient or vague statements.
- `create_authorization_packet` can create an implementation-start packet from a proposal using the approved owner-direction/work-item sufficiency phrase.
- `python scripts\implementation_authorization.py begin --bridge-id gtkb-active-status-capability-gate-formalization` no longer fails with `Approved proposal is missing ## Requirement Sufficiency`.

## Specification-Derived Verification Plan

- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 and DCL-PROJECT-AUTHORIZATION-ENVELOPE-001: run targeted implementation-authorization tests proving the packet gate accepts the approved phrase and preserves negative cases.
- PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001: confirm the original formalization implementation begins through `scripts\implementation_authorization.py begin`, not by bypassing the packet gate.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 and GOV-FILE-BRIDGE-AUTHORITY-001: file this proposal through the bridge helper and preserve Loyal Opposition review before source changes.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001: keep the parser/test mutation inside the helper-mediated bridge and implementation-start path.

## Pre-Filing Preflight

Manual preflight before filing: the target paths are in-root, the proposal includes project-linkage metadata, requirement sufficiency, specification links, code quality baseline, spec-derived verification, and a narrow rollback path. The change is intentionally scoped to the implementation-start parser false negative surfaced by the approved WI-4213 formalization proposal.

## Risk And Rollback

Risk: broadening phrase acceptance too far could weaken the start gate. Mitigation: add one bounded phrase rather than substring-free prose acceptance and retain explicit negative tests. Rollback removes the phrase and added tests; no bridge audit files are rewritten.
