NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution
author_metadata_source: codex-explicit-runtime-envelope

# Implementation Proposal - Extend verdict evidence-anchor guard to hook-less Antigravity path

bridge_kind: prime_proposal
Document: gtkb-wi4749-antigravity-verdict-anchor-guard
Version: 001
Date: 2026-07-06 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4749

target_paths: ["scripts/verify_antigravity_dispatch.py", ".codex/skills/verify/helpers/write_verdict.py", ".claude/skills/verify/helpers/write_verdict.py", "platform_tests/scripts/test_verify_antigravity_dispatch.py", "platform_tests/skills/test_verify_prior_deliberations_pre_population.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Extend the verdict-evidence-anchor guard to the hook-less Antigravity verdict-write path by routing verdict writes through the same guarded helper behavior used by hook-capable harnesses. This proposal will be filed as `bridge/gtkb-wi4749-antigravity-verdict-anchor-guard-001.md`, an append-only numbered bridge file.

## Requirement Sufficiency

Existing requirements are sufficient. WI-4749 documents the residual path left after WI-4520, and the active Harness Parity Phase 2 PAUTH includes WI-4749.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded PAUTH-backed implementation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms PAUTH does not bypass GO or implementation-start gates.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves bridge-governed implementation flow.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project linkage metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived test evidence before VERIFIED.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - requires cross-harness parity defects to be mechanically enforced.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - requires harness-surface proposals to declare parity or typed waivers per applicable harness.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - recognizes hook-surface differences and requires helper-layer fallback.
- `ADR-CROSS-HARNESS-PARITY-001` - requires behaviorally equivalent review safeguards or typed waivers.

## Prior Deliberations

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - owner authorized bounded Harness Parity Phase 2 implementation.
- `DELIB-20265566` - context cited by the WI for Antigravity verdict-path residuals.
- `DELIB-20263475` - prior verdict-path governance context cited by the WI.

## Owner Decisions / Input

- `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` - active authorization covering WI-4749.

## Proposed Scope

- Route Antigravity verdict writes through a helper path that enforces verdict evidence anchors.
- Add regression tests proving a hook-less verdict path cannot file without required evidence anchors.
- Preserve existing Claude/Codex verdict behavior and generated skill parity.

## Cross-Harness Disposition

- Claude Code and Codex: retain equivalent verdict-helper behavior through their paired skill helper files; generated/adapter drift must be tested.
- Antigravity: receives behavioral parity through the helper-mediated path because it lacks a native hook surface.
- Cursor, Ollama, and OpenRouter: no direct skill-surface edits in this slice; any verdict-write path that uses the shared helper inherits the same evidence-anchor behavior, otherwise it must be reported as a typed follow-on waiver.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Tests prove the hook-less path is covered by equivalent helper-layer enforcement. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Compliance gate and tests confirm the harness-surface change declares parity/waiver disposition. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Tests prove enforcement does not depend only on native hook availability. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm live bridge lifecycle and append-only numbered file chain. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report includes exact targeted test output. |

## Acceptance Criteria

- Antigravity verdict writes fail closed when required evidence anchors are missing.
- Existing hook-capable verdict paths keep passing their tests.
- No provider credential, role assignment, dispatcher routing, or deployment behavior changes.

## Risks / Rollback

Risk is moderate because verdict filing is governance-critical. Rollback is a revert of helper/source/test changes.

## Files Expected To Change

- `scripts/verify_antigravity_dispatch.py`
- `.codex/skills/verify/helpers/write_verdict.py`
- `.claude/skills/verify/helpers/write_verdict.py`
- `platform_tests/scripts/test_verify_antigravity_dispatch.py`
- `platform_tests/skills/test_verify_prior_deliberations_pre_population.py`

## Recommended Commit Type

`fix`
