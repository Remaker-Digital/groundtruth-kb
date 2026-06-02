NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-gtkb-pb-2026-06-02
author_model: GPT-5 Codex
author_model_version: 2026-06-02
author_model_configuration: reasoning=high

bridge_kind: implementation_proposal
Document: gtkb-active-status-capability-gate-harness-lifecycle-retention
Project Authorization: PAUTH-WI-4213-ACTIVE-STATUS-CAPABILITY-GATE
Project: PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH
Work Item: WI-4213
target_paths: ["groundtruth-kb/src/groundtruth_kb/harness_ops.py", "platform_tests/groundtruth_kb/cli/test_harness_cli.py"]

# Implementation Proposal: Active-Status Capability Gate Harness Lifecycle Retention

## Summary

Close the remaining WI-4213 lifecycle gap in the harness CLI operations. The registry and mode-switch transaction paths now allow role/status/capability orthogonality, but \`transition_harness()\` still clears roles whenever a harness becomes suspended or retired. This slice preserves role-set metadata across non-active lifecycle transitions while keeping active PB/LO reconciliation and dispatch eligibility separate.

## Prior Deliberations

- \`bridge/gtkb-active-status-capability-gate-formalization-004.md\` VERIFIED the formal role/status/capability authority.
- \`bridge/gtkb-active-status-capability-gate-registry-dispatch-004.md\` VERIFIED projection and dispatch capability gating.
- \`bridge/gtkb-active-status-capability-gate-lifecycle-substrate-002.md\` granted GO for adjacent mode-switch lifecycle/substrate alignment.
- \`DELIB-2813\` records the owner directive to continue until WI-4213 is completed.

## Owner Decisions / Input

No new owner decision is required. This slice follows ADR-ROLE-STATUS-ORTHOGONALITY-001 v2, DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001 v2, REQ-HARNESS-REGISTRY-001 v3, and the active WI-4213 project authorization.

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
| CQ-PATHS-001 | Yes | Mutate only \`harness_ops.py\` and its CLI lifecycle tests. | \`git diff --name-only -- groundtruth-kb/src/groundtruth_kb/harness_ops.py platform_tests/groundtruth_kb/cli/test_harness_cli.py\`. | n/a |
| CQ-COMPLEXITY-001 | Yes | Preserve the existing FSM and reconciliation flow; change only role preservation on lifecycle versions. | Focused pytest command. | n/a |
| CQ-CONSTANTS-001 | Yes | Reuse existing decoded role-set helpers and lifecycle constants. | Source review. | n/a |
| CQ-SECURITY-001 | Yes | Do not weaken active-harness eligibility or last-active safety checks. | CLI lifecycle tests and existing set-role rejection tests. | n/a |
| CQ-DOCS-001 | Yes | Update lifecycle docstring/comment to say non-active roles may be retained. | Source review. | n/a |
| CQ-TESTS-001 | Yes | Add suspend/retire tests proving retained role metadata is preserved while status changes. | Focused pytest command. | n/a |
| CQ-LOGGING-001 | N/A | n/a | n/a | This slice does not add or change logging surfaces. |
| CQ-VERIFICATION-001 | Yes | Run targeted pytest, ruff check, and ruff format-check. | Commands listed in report. | n/a |

## Scope

In scope:

- Preserve existing role-set metadata in \`transition_harness()\` when a harness transitions to suspended or retired.
- Keep last-active safety checks and role reconciliation intact.
- Add CLI lifecycle regression tests for suspend/retire role retention.

Out of scope:

- Changing set-role eligibility for non-active harnesses.
- Changing bridge dispatch resolver behavior already verified in the registry/dispatch thread.
- Implementing WI-3513 bridge writer contention fixes.

## Acceptance Criteria

- Suspending an active harness preserves its current role-set metadata while status becomes \`suspended\`.
- Retiring an active harness through auto-suspend preserves its current role-set metadata while status becomes \`retired\`.
- Existing last-active safety and set-role non-active rejection behavior still pass.
- Targeted pytest, ruff check, and ruff format-check pass.

## Specification-Derived Verification Plan

- ADR-ROLE-STATUS-ORTHOGONALITY-001 v2: CLI lifecycle tests prove role membership can persist independently from active status.
- DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001 v2: existing active-only set-role rejection tests prove retained non-active roles do not become active assignments.
- REQ-HARNESS-REGISTRY-001 v3: append-only harness versions carry status changes without erasing role-set metadata.
- GOV-FILE-BRIDGE-AUTHORITY-001: file proposal/report through bridge helpers and preserve bridge/INDEX.md ordering.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001: include spec-to-test mapping and observed command results in the implementation report.

## Pre-Filing Preflight

Manual preflight before filing: this slice is restricted to the harness lifecycle retention gap found during WI-4213 completion and all target paths are under \`E:\\GT-KB\`.

## Risk And Rollback

Risk: preserving role metadata on retired rows could surprise callers that assumed retired roles were empty. Mitigation: active eligibility and dispatch logic already gate on active status and event capability; tests keep non-active set-role rejection intact. Rollback restores role clearing in lifecycle transitions and reverts tests; bridge audit files remain append-only.
