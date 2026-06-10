NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-gtkb-pb-2026-06-02
author_model: GPT-5 Codex
author_model_version: 2026-06-02
author_model_configuration: reasoning=high

bridge_kind: prime_proposal
Document: gtkb-active-status-capability-gate-lifecycle-substrate
Project Authorization: PAUTH-WI-4213-ACTIVE-STATUS-CAPABILITY-GATE
Project: PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH
Work Item: WI-4213
target_paths: ["groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/derive.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/bridge_substrate.py", "platform_tests/groundtruth_kb/test_mode_switch_transaction.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py", "platform_tests/scripts/test_cross_harness_trigger_durable_keyed_regression.py", "platform_tests/scripts/test_cross_harness_trigger_suppression.py", "platform_tests/scripts/test_governing_specs_preserved.py"]

# Implementation Proposal: Active-Status Capability Gate Lifecycle and Substrate Alignment

## Summary

Close the WI-4213 gaps surfaced during the registry/dispatch implementation review: adjacent lifecycle and mode-switch helpers still erase retained non-active roles or derive bridge substrate state without the event-driven capability axis. This companion slice aligns those upstream paths with the already-formalized role/status/capability orthogonality so a non-active or non-event-capable harness may retain role membership without becoming an active bridge-event dispatch target.

## Prior Deliberations

- \`bridge/gtkb-active-status-capability-gate-formalization-004.md\` VERIFIED the formal authority: active dispatch requires bridge-event reception capability, and WI-3513 remains the separate durable write-contention fix.
- \`bridge/gtkb-active-status-capability-gate-registry-dispatch-002.md\` granted GO for the registry/projection/dispatch half of WI-4213.
- \`DELIB-2813\` records the owner directive to continue until the listed items are completed.
- WI-4213 records the S384 correction: C can retain Prime Builder role while inactive/non-event-capable; the resolver must exclude non-event-capable harnesses; WI-3513 remains separate.

## Owner Decisions / Input

No new owner decision is required. This slice follows the live formal authority in ADR-ROLE-STATUS-ORTHOGONALITY-001 v2, DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001 v2, and REQ-HARNESS-REGISTRY-001 v3, plus the owner direction to complete WI-4213.

## Specification Links

- ADR-ROLE-STATUS-ORTHOGONALITY-001
- DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001
- REQ-HARNESS-REGISTRY-001
- GOV-HARNESS-ROLE-PORTABILITY-001
- GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- DCL-PROJECT-AUTHORIZATION-ENVELOPE-001
- PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001
- GOV-STANDING-BACKLOG-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001

## Requirement Sufficiency

Existing owner direction and WI-4213 are sufficient.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Source/tests contain no secrets or environment values. | Helper credential scan and diff review. | n/a |
| CQ-PATHS-001 | Yes | Mutate only lifecycle, topology/substrate helpers, and targeted tests listed in target_paths. | \`git diff --name-only -- <target paths>\`. | n/a |
| CQ-COMPLEXITY-001 | Yes | Preserve existing mode-switch flows; adjust only role retention and capability predicates. | Focused pytest commands. | n/a |
| CQ-CONSTANTS-001 | Yes | Reuse existing role/status/capability field names; avoid parallel state. | Source review and tests. | n/a |
| CQ-SECURITY-001 | Yes | Missing/false event capability remains fail-closed for bridge-event dispatch/substrate activation. | Tests with missing/false \`event_driven_hooks\`. | n/a |
| CQ-DOCS-001 | Yes | Update stale comments that say inactive harnesses must be cleared. | Source review. | n/a |
| CQ-TESTS-001 | Yes | Add/adjust tests for non-active role retention through transactions and event-capability-aware substrate/topology derivation. | Targeted pytest commands. | n/a |
| CQ-LOGGING-001 | N/A | n/a | n/a | This slice does not add or change runtime logging surfaces. |
| CQ-VERIFICATION-001 | Yes | Run targeted pytest, ruff check, and ruff format-check. | Commands listed in report. | n/a |

## Scope

In scope:

- Preserve retained roles for non-active harnesses during \`transition_harness\` and mode-switch transaction role assignment unless a path explicitly requires role removal.
- Update mode-switch topology derivation and bridge-substrate active Prime Builder resolution so active bridge substrate/\`applied_by\` logic ignores non-active or non-event-capable role-retaining harnesses.
- Update comments/docstrings that still encode "inactive roles are always cleared" semantics.
- Update stale tests/fixtures that omit \`event_driven_hooks\` for active dispatchable harnesses or still use legacy role-assignment files where the trigger now reads the registry projection.

Out of scope:

- Reworking bridge writer serialization or INDEX write contention; WI-3513 remains separate.
- Changing the event-driven dispatch resolver already covered by \`gtkb-active-status-capability-gate-registry-dispatch\`.
- Production deployment or credential changes.

## Acceptance Criteria

- Mode-switch transaction and harness lifecycle paths do not erase retained roles from non-active harnesses merely because the harness is non-active.
- Topology/substrate helpers require active status and \`event_driven_hooks=true\` before treating a role-retaining harness as a bridge-event-capable active participant.
- Tests that exercise event-driven dispatch fixtures include explicit capability fields, and stale role-assignment-only trigger assertions are migrated or retired.
- Targeted pytest, ruff check, and ruff format-check pass.
- WI-3513 remains open/separate and is not implemented by this slice.

## Specification-Derived Verification Plan

- ADR-ROLE-STATUS-ORTHOGONALITY-001 v2: tests prove role membership is retained independently from active status, while active dispatch/substrate eligibility remains separate.
- DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001 v2: tests prove bridge-event substrate/topology eligibility requires role + active status + event capability.
- REQ-HARNESS-REGISTRY-001 v3: tests prove mode-switch/lifecycle operations preserve the registry's role-set semantics for non-active rows.
- GOV-FILE-BRIDGE-AUTHORITY-001: file proposal/report through bridge helpers and preserve bridge/INDEX.md ordering.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001: include spec-to-test mapping and observed command results in the implementation report.

## Pre-Filing Preflight

Manual preflight before filing: this companion slice is restricted to adjacent WI-4213 lifecycle/substrate semantics, does not alter WI-3513 write-contention behavior, and all target paths are under \`E:\\GT-KB\`.

## Risk And Rollback

Risk: preserving retained roles could leave stale role metadata visible in more lifecycle states than prior tests expected. Mitigation: keep active uniqueness and dispatch/substrate predicates scoped to active event-capable rows, and add regression coverage for non-active retention. Rollback restores the previous role-clearing behavior in lifecycle/transaction helpers and reverts targeted tests; bridge audit files remain append-only.
