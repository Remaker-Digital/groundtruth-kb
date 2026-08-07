NEW
::init gtkb pb
::open build
author_identity: Goose Prime Builder
author_harness_id: G
author_session_context_id: G-2026-08-04T22-30-56Z
author_model: goose-deepseek-v4-pro
author_model_version: deepseek-v4-pro
author_model_configuration: manual interactive desktop session

bridge_kind: governance_review
Document: gtkb-wi5935-wrap-spec-per-context
Version: 001
Work Item: WI-5935
Project: PROJECT-GTKB-SESSION-ENVELOPE

# WI-5935 Slice B - Revise SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001 (per-context authority + fail-closed wrap + closing instruction)

## Summary

Revises `SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001` (v1) to v2. The v1 spec mandates the per-harness path `harness-state/<harness>/session-envelope.json` as authoritative; Slice A supersedes that model. This slice re-points the wrap procedure's authoritative state surface to the per-session document, adds the fail-closed single-context precondition, and adds the closing-instruction contract. Spec-text revision only (KB spec artifact via governed `gt spec update`); no code change.

## Requirement Sufficiency

New or revised requirement required before implementation: this slice IS the revised requirement (SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001 v2).

## Changes to the wrap-procedure spec (v2)

1. Authoritative state path: `harness-state/<harness>/session-envelopes/<session_id>.json` (per-session document). The per-harness `session-envelope.json` is reclassified as a non-authoritative compatibility projection, never the wrap mutation target.
2. Fail-closed precondition (new mandatory step, runs first): resolve the invoking session-context `session_id`; if the live envelope `session_id` differs, abort with an owner-visible diagnostic and leave both envelopes untouched.
3. Tier-1 envelope finalization / topic auto-close / archive operate on the invoking context's per-session document only.
4. Closing-instruction contract: every interactive-session and bridge artifact MUST carry `When you are finished working, close your session envelope by invoking ::wrap.`
5. `::wrap` harvests that session-context's output and updates the Source of Truth for that context only.

## Specification Links

- `SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001` v1 - the spec revised here.
- `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` (Slice A) - governing design constraint.
- `SPEC-CANONICAL-WRAP-KEYWORD-SYNTAX-001` v1 - `::wrap` trigger surface preserved.
- `ADR-ENVELOPE-META-MODEL-001` / `DCL-ENVELOPE-META-MODEL-001` - envelope anatomy + containment.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`.

## Specification-Derived Verification

Spec-revision slice; conformance is enforced by Slice C/F code tests (`python -m pytest`). Verification here: the revised spec text asserts the fail-closed precondition and per-session authoritative path, and Slice C's `platform_tests/scripts/test_session_envelope_runtime.py` cases (wrap fail-closed on session mismatch) derive directly from the revised clauses. Self-check: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5935-wrap-spec-per-context-001` preflight_passed.

## Prior Deliberations

- `DELIB-20265897` - WI-4729 `::wrap`/`::close` mechanical harvest model.
- `DELIB-20260637` - envelope meta-model.


### Helper-suggested candidates

_Deliberation semantic search degraded (SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 8324 and this is thread id 30524.); do not treat this section as an authoritative empty search result._
_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- 2026-08-04: Owner selected Option 1 - record Slice A as a new DCL and file all slices now, staged by dependency. This slice depends on Slice A GO.

## Recommended Commit Type

docs: (specification revision).
