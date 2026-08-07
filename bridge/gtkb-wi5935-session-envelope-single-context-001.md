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
Document: gtkb-wi5935-session-envelope-single-context
Version: 001
Work Item: WI-5935
Project: PROJECT-GTKB-SESSION-ENVELOPE

# WI-5935 Slice A - Session-Envelope Single-Context Design Constraint (DCL) + Sequenced Breakdown

## Summary

WI-5935 (owner-identified design flaw, P1 defect) holds that the session envelope must be constrained to exactly one session-context and that `::wrap` must never close an envelope belonging to a different session-context. The flaw is confirmed and is structural: `close_session`/`run_wrap` load the per-harness projection `harness-state/<harness>/session-envelope.json` with no session-id validation, so under concurrent same-harness sessions one context's `::wrap` can close another's envelope.

This is Slice A (the design-gate slice). It records the single governing owner design decision as a new DCL - `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` - which supersedes the per-harness authority model in `DCL-SESSION-ENVELOPE-DURABILITY-001`, and it fixes the sequenced work-item breakdown for the dependent implementation slices (B-F). No source, hook, or configuration is mutated by this slice; the deliverable is the DCL record plus this approved decomposition.

## Why a design DCL is the required first step

The captured requirements collide with live specifications. Both `DCL-SESSION-ENVELOPE-DURABILITY-001` (v1) and `SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001` (v1) mandate per-harness authoritative envelope state. The bridge Mandatory Specification Linkage Gate requires every implementation proposal to cite its governing specs; any implementation slice filed against the per-harness model while WI-5935 demands a per-context model is internally contradictory and would be NO-GO. The contradiction must be resolved at the design layer first.

## Design decision being recorded (DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001)

1. A session envelope is bound to exactly one session-context, identified by `session_id`.
2. `::wrap` (and any session close path) MUST fail closed when the live envelope's `session_id` does not equal the invoking session-context's `session_id`.
3. The constraint is uniform across all harnesses: no per-harness design. Harness differences are confined to how a harness surfaces its session id (runtime markers), never to the envelope-binding rule.
4. The per-harness `harness-state/<harness>/session-envelope.json` is reclassified from authoritative state to a non-authoritative compatibility projection (authoritative state is the per-session document `harness-state/<harness>/session-envelopes/<session_id>.json`, which the code already maintains).
5. Mechanical enforcement is required (fail-closed precondition + tests), not convention alone.
6. `::wrap` harvests that session-context's output and updates the Source of Truth (MemBase/Deliberation Archive) for that context only.
7. Every interactive-session and bridge artifact carries a closing instruction (e.g. `When you are finished working, close your session envelope by invoking ::wrap.`).

Supersedes: `DCL-SESSION-ENVELOPE-DURABILITY-001` v1 (per-harness authoritative state).

## Sequenced work-item breakdown (approved by this slice)

All slices are tracked under WI-5935 / PROJECT-GTKB-SESSION-ENVELOPE. Dependency-ordered:

- **Slice A (this proposal).** Design DCL + breakdown. Gate for all other slices.
- **Slice B.** Revise `SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001`: re-point the authoritative path to the per-session document, add the fail-closed session-id precondition to the wrap trigger, and add the closing-instruction contract. Depends on A.
- **Slice C.** Core fix: session-id-validated `close_session` / `run_wrap` / `ensure_current`; add the goose runtime-marker entry to `RUNTIME_HARNESS_MARKERS` and goose membership to `scripts/gtkb_session_id.py`; fail-closed cross-context wrap. Depends on A + B.
- **Slice D.** Simple, intuitive wrap CLI ergonomics (`gt session wrap`). Depends on C.
- **Slice E.** Closing-instruction footer, uniform across interactive and bridge artifact surfaces. Depends on A; parallel to C/D.
- **Slice F.** Cross-harness parity tests + `Cross-Harness Disposition` per `ADR-CROSS-HARNESS-PARITY-001`. Depends on C.

## Specification Links

- `DCL-SESSION-ENVELOPE-DURABILITY-001` v1 - superseded by the DCL this slice records (per-harness authoritative state).
- `SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001` v1 - revised by Slice B (per-harness authoritative path + 4-tier procedure).
- `SPEC-CANONICAL-WRAP-KEYWORD-SYNTAX-001` v1 - the `::wrap` trigger surface this work preserves.
- `ADR-ENVELOPE-META-MODEL-001` / `DCL-ENVELOPE-META-MODEL-001` - envelope three-part anatomy + containment conformance.
- `ADR-CROSS-HARNESS-PARITY-001` (accepted) - cross-harness behavioral parity invariant; drives the uniform-across-harnesses requirement and Slice F.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - specification-linkage mandate this proposal satisfies.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - VERIFIED conditional on spec-derived tests; governs Slice C/F verification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - file-bridge authority model governing these proposals and verdicts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - lifecycle states (superseded) for the DCL this slice records.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - artifact-oriented governance for recording the design decision durably.

## Prior Deliberations

<!-- Pre-populated by helper; review and prune. -->
- `DELIB-20260637` - Envelope meta-model refinement: 3-part anatomy + dispatch-session-topic containment.
- `DELIB-20263212` - Owner requirement: `::init gtkb` envelope persists for model-context lifetime (survives compaction/resume).
- `DELIB-20265897` - WI-4729 `::wrap`/`::close` mechanical harvest model.
- `DELIB-S20260626-CROSS-HARNESS-PARITY-ADVISORY` - cross-harness parity design advisory.
- `DELIB-2238` / `DELIB-2500` - session/work envelope convention origins.


### Helper-suggested candidates

_Deliberation semantic search degraded (SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 25256 and this is thread id 9576.); do not treat this section as an authoritative empty search result._
_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- 2026-08-04 (this session): Owner selected Option 1 - record Slice A as a new DCL and file all slices now, staged by dependency.

## Specification-Derived Verification

Each linked specification maps to spec-derived verification in the dependent implementation slice that enforces it. This design slice (A) mutates no code; its verification is the recorded DCL plus the applicability/clause preflight evidence below. Slice-level spec-to-test mapping (each slice's own proposal carries the concrete `test_*.py` and commands):

- `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` (this slice) -> Slice C adds `python -m pytest platform_tests/scripts/test_session_envelope_runtime.py` cases: wrap fail-closed when live envelope `session_id` != invoking session id; concurrent same-harness two-context wrap isolation.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` (superseded) -> Slice C adds a projection-not-authoritative regression test asserting `session-envelope.json` is never the wrap mutation target.
- `SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001` (revised by Slice B) -> Slice C/D execute the wrap 4-tier procedure tests with `python -m pytest`.
- `SPEC-CANONICAL-WRAP-KEYWORD-SYNTAX-001` -> Slice D CLI test: `^::wrap$` triggers the fail-closed wrap (`python -m pytest`).
- `ADR-CROSS-HARNESS-PARITY-001` -> Slice F cross-harness parity tests (`python -m pytest platform_tests/scripts/test_modernization_harness_parity.py`) assert identical fail-closed behavior on every harness.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` -> each implementation slice carries a `Specification-Derived Verification` section with `python -m pytest` / `ruff` command evidence and observed results.

Self-check evidence: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5935-session-envelope-single-context-001` reported `preflight_passed: true` (packet_hash sha256:53a067cb15b9d1118aa66fe08a673e7a6884decc1881b6ef375854fec69bd149).

## Recommended Commit Type

docs: (governance design record + decomposition; no code change).
