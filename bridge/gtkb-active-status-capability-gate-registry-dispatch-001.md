NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-gtkb-pb-2026-06-02
author_model: GPT-5 Codex
author_model_version: 2026-06-02
author_model_configuration: reasoning=high

bridge_kind: prime_proposal
Document: gtkb-active-status-capability-gate-registry-dispatch
Project Authorization: PAUTH-WI-4213-ACTIVE-STATUS-CAPABILITY-GATE
Project: PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH
Work Item: WI-4213
target_paths: ["scripts/cross_harness_bridge_trigger.py", "groundtruth-kb/src/groundtruth_kb/harness_projection.py", "groundtruth-kb/src/groundtruth_kb/harness_ops.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/groundtruth_kb/test_mode_switch_invariants.py", "groundtruth.db", "harness-state/harness-registry.json"]

# Implementation Proposal: Active-Status Capability Gate Registry and Dispatch

## Summary

Complete the implementation half of WI-4213 after the verified formalization slice. The live registry/projection still cannot represent Antigravity C as role-retaining but non-event-capable: C is currently \`role=[]\`, and the dispatch resolver only gates on \`status == "active"\` rather than bridge-event reception capability.

Implement the formalized active-status capability gate by projecting an \`event_driven_hooks\` capability flag, excluding non-event-capable harnesses from dispatch target resolution, allowing inactive/non-active role retention in the active role-partition invariant, and appending a canonical C harness row that retains \`prime-builder\` role while remaining non-dispatchable.

## Prior Deliberations

- \`bridge/gtkb-active-status-capability-gate-formalization-004.md\` VERIFIED the formal authority: active dispatch requires bridge-event reception capability, and WI-3513 remains the separate write-contention fix.
- \`bridge/gtkb-active-status-capability-gate-formalization-content-drafts-004.md\` VERIFIED the formal draft inputs consumed by the formalization.
- \`bridge/gtkb-implementation-start-requirement-sufficiency-owner-direction-phrase-006.md\` VERIFIED the start-gate phrase fix needed to begin the formalization thread.
- WI-4213 records the S384 correction: C can retain Prime Builder role while inactive/non-event-capable; the resolver must exclude non-event-capable harnesses; WI-3513 remains separate.
- DELIB-2813 records the owner directive to continue until the listed items are completed under the active project authorization.

## Owner Decisions / Input

No new owner decision is required. The formal authority for this implementation is now live in ADR-ROLE-STATUS-ORTHOGONALITY-001 v2, DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001 v2, and REQ-HARNESS-REGISTRY-001 v3.

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

Existing requirements sufficient.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Source/tests/registry rows contain no secrets or environment values. | Helper credential scan and diff review. | |
| CQ-PATHS-001 | Yes | Mutate only resolver, projection, invariant, tests, DB harness row, and generated projection listed in target_paths. | \`git diff --name-only -- <target paths>\`. | |
| CQ-COMPLEXITY-001 | Yes | Add a small boolean capability gate instead of redesigning dispatch. | Targeted resolver tests. | |
| CQ-CONSTANTS-001 | Yes | Centralize projected capability semantics in harness_projection and gate semantics in the resolver. | Source review and tests. | |
| CQ-SECURITY-001 | Yes | Missing/false event capability fails closed and is non-dispatchable. | Resolver tests for false and missing \`event_driven_hooks\`. | |
| CQ-DOCS-001 | Yes | Update docstrings/comments that currently say inactive harnesses cannot retain roles. | Source review. | |
| CQ-TESTS-001 | Yes | Add tests for event capability dispatch exclusion and inactive role retention. | Targeted pytest commands. | |
| CQ-LOGGING-001 | Yes | Preserve existing \`no_active_target_for_role\` dispatch-failure audit; refine note wording to mention event-capable active target. | Resolver zero-target test. | |
| CQ-VERIFICATION-001 | Yes | Run targeted pytest, ruff check, ruff format-check, DB/projection readback. | Commands listed in report. | |

## Scope

In scope:

- Add \`event_driven_hooks\` to the generated harness registry projection, true for hook-capable Codex/Claude harness types and false for Antigravity.
- Update \`_resolve_dispatch_target\` so dispatch candidates require role match, \`status == "active"\`, and \`event_driven_hooks is true\`; missing/false/unknown event capability is non-dispatchable.
- Update single-harness topology detection if necessary so non-event-capable rows cannot activate event-driven dispatch.
- Relax the active role-partition invariant so non-active harnesses may retain roles while only active harnesses are counted for PB/LO partition validity.
- Append a governed C harness row in \`groundtruth.db\` with \`role=["prime-builder"]\`, non-active status, and regenerate \`harness-state/harness-registry.json\` showing \`event_driven_hooks: false\` for C.
- Add targeted tests covering the resolver, missing/false capability fail-closed behavior, and inactive role retention.

Out of scope:

- Bridge writer serialization or INDEX write-contention behavior; WI-3513 remains the durable fix.
- Multi-active dispatch redesign.
- Production deployment or external credential changes.
- Changing session-stated role override semantics.

## Acceptance Criteria

- \`harness-state/harness-registry.json\` represents Antigravity C with \`role=["prime-builder"]\`, non-active status, and \`event_driven_hooks=false\`.
- \`_resolve_dispatch_target("prime-builder", ...)\` ignores active or role-retaining rows whose \`event_driven_hooks\` is false or missing.
- If the only role-retaining rows are non-event-capable or non-active, the resolver returns the existing \`None\` sentinel and writes the existing \`no_active_target_for_role\` audit record when a state dir is supplied.
- Inactive/non-active role retention no longer fails the active role-partition invariant; active PB/LO uniqueness still holds.
- Targeted pytest, ruff check, and ruff format-check pass.
- WI-3513 remains open/separate and is not implemented by this slice.

## Specification-Derived Verification Plan

- ADR-ROLE-STATUS-ORTHOGONALITY-001 v2: DB/projection readback shows role/status/capability orthogonality for C.
- DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001 v2: resolver tests prove role+active+event capability are all required for dispatch.
- REQ-HARNESS-REGISTRY-001 v3: registry readback shows C role retention while non-event-capable, and invariant tests allow non-active role retention.
- GOV-FILE-BRIDGE-AUTHORITY-001: file proposal/report through bridge helpers and preserve bridge/INDEX.md ordering.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001: include spec-to-test mapping and observed command results in the implementation report.

## Pre-Filing Preflight

Manual preflight before filing: the formal authority slice is VERIFIED, all target paths are in-root, this proposal does not implement WI-3513, and the resolver behavior remains fail-closed for missing capability flags.

## Risk And Rollback

Risk: relaxing role retention could accidentally weaken active PB/LO uniqueness. Mitigation: keep uniqueness checks scoped to active event-capable dispatch targets and add regression tests for active duplicates. Rollback restores the prior resolver/projection/invariant behavior and appends a superseding harness row; bridge audit files remain append-only.
