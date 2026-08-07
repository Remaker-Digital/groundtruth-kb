NEW
::init gtkb pb
::open build
author_identity: Goose Prime Builder
author_harness_id: G
author_session_context_id: G-2026-08-04T22-30-56Z
author_model: goose-deepseek-v4-pro
author_model_version: deepseek-v4-pro
author_model_configuration: manual interactive desktop session

bridge_kind: prime_proposal
Document: gtkb-wi5935-wrap-parity-tests
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-SESSION-ENVELOPE-WI-5935-SESSION-ENVELOPE-SINGLE-CONTEXT-IMPLEMENTATION
Work Item: WI-5935
Project: PROJECT-GTKB-SESSION-ENVELOPE

# WI-5935 Slice F - Cross-harness parity tests for the single-context wrap constraint

## Summary

Delivers the WI-5935 uniform-across-all-harnesses requirement as executable parity tests. Asserts the fail-closed single-context wrap behaves identically on every active harness and that each harness surfaces its session id through its runtime-marker entry (no per-harness design).

## Requirement Sufficiency

Existing requirements sufficient (once Slice C is GO): `ADR-CROSS-HARNESS-PARITY-001` + `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` define the parity invariant this tests.

target_paths: ["platform_tests/scripts/test_modernization_harness_parity.py", "platform_tests/scripts/test_session_envelope_runtime.py"]

## Implementation Plan

1. Extend the harness-parity suite: for each harness in `RUNTIME_HARNESS_MARKERS`, assert a concurrent same-harness two-context wrap fails closed identically.
2. Assert each harness's session-id marker resolves via the uniform `resolve_session_id` order.
3. Assert the per-harness `session-envelope.json` is never the wrap mutation target on any harness.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001` - the parity invariant; `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` (Slice A).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `GOV-FILE-BRIDGE-AUTHORITY-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Specification-Derived Verification

- `python -m pytest platform_tests/scripts/test_modernization_harness_parity.py` - per-harness fail-closed wrap parity matrix; observed results reported in the implementation report.
- `ruff check` / `ruff format --check` on changed test files.

## Prior Deliberations

- `DELIB-S20260626-CROSS-HARNESS-PARITY-ADVISORY` - parity design advisory.


### Helper-suggested candidates

_Deliberation semantic search degraded (SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 35100 and this is thread id 24120.); do not treat this section as an authoritative empty search result._
_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- 2026-08-04: Owner selected Option 1 - file all slices now, staged by dependency. Depends on Slice C GO.

## Cross-Harness Disposition

This slice IS the cross-harness parity enforcement for WI-5935; it applies the invariant across all active harnesses with no waiver (per `ADR-CROSS-HARNESS-PARITY-001` Q8).

## Recommended Commit Type

test: (test-only parity additions).
