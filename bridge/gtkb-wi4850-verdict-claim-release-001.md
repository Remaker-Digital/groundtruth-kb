NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution
author_metadata_source: codex-explicit-runtime-envelope

# Implementation Proposal - Release LO draft claim after verdict filing

bridge_kind: prime_proposal
Document: gtkb-wi4850-verdict-claim-release
Version: 001
Date: 2026-07-06 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4850

target_paths: [".codex/skills/verify/helpers/write_verdict.py", ".claude/skills/verify/helpers/write_verdict.py", "scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/skills/test_verify_prior_deliberations_pre_population.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Release the reviewing session's draft work-intent claim after a successful GO/NO-GO/VERIFIED verdict write so a Prime implementer is not blocked by stale post-verdict claim TTL. This proposal will be filed as `bridge/gtkb-wi4850-verdict-claim-release-001.md`, an append-only numbered bridge file.

## Requirement Sufficiency

Existing requirements are sufficient. WI-4850 records the observed lingering-claim defect, and the active Harness Parity Phase 2 PAUTH includes WI-4850.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded PAUTH-backed implementation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms PAUTH does not bypass GO or implementation-start gates.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves bridge-governed implementation flow.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project linkage metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived test evidence before VERIFIED.
- `ADR-DISPATCHER-ARCHITECTURE-001` - verdict and implementation handoff must not create avoidable dispatcher stalls.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - requires harness-surface proposals to declare parity or typed waivers per applicable harness.
- `ADR-CROSS-HARNESS-PARITY-001` - shared verdict claim behavior must be equivalent across harness lanes or explicitly waived.

## Prior Deliberations

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - owner authorized Harness Parity Phase 2 implementation.

## Owner Decisions / Input

- `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` - active authorization covering WI-4850.

## Proposed Scope

- Update verdict helper finalization to release the writer's draft claim only after a successful verdict file write/publication.
- Preserve failure behavior so claims are not released on partial or failed writes.
- Add tests for successful release, failed-write retention, and Prime claim acquisition after GO.

## Cross-Harness Disposition

- Claude Code and Codex: paired verify-helper files must expose equivalent success-only claim release behavior.
- Antigravity, Cursor, Ollama, and OpenRouter: no direct harness-specific helper edits in this slice; if their verdict routes use the shared helper, they inherit the same behavior, and any separate verdict route must be reported as a typed waiver or follow-on work item.
- Dispatcher/bridge state remains the common authority; no harness receives a special bypass around work-intent or implementation-start gates.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Tests prove GO handoff is not blocked by stale reviewer draft claims. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Compliance gate and tests confirm the harness-surface change declares parity/waiver disposition. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm verdict helper still writes append-only numbered bridge files. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Tests preserve implementation-start gate behavior after release. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report includes exact targeted test output. |

## Acceptance Criteria

- Successful verdict filing releases the reviewing session's draft claim for that thread.
- Failed verdict writes retain the claim until TTL or explicit release.
- Prime go_implementation can acquire after GO without waiting for stale LO TTL.

## Risks / Rollback

Risk is moderate because claim release touches bridge concurrency. Mitigation is success-only release and failure tests. Rollback is a revert of helper/source/test changes.

## Files Expected To Change

- `.codex/skills/verify/helpers/write_verdict.py`
- `.claude/skills/verify/helpers/write_verdict.py`
- `scripts/bridge_work_intent_registry.py`
- `platform_tests/scripts/test_bridge_work_intent_registry.py`
- `platform_tests/skills/test_verify_prior_deliberations_pre_population.py`

## Recommended Commit Type

`fix`
