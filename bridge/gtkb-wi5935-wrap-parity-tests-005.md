REVISED
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
Version: 005
Project Authorization: PAUTH-PROJECT-GTKB-SESSION-ENVELOPE-WI-5935-SESSION-ENVELOPE-SINGLE-CONTEXT-IMPLEMENTATION
Project: PROJECT-GTKB-SESSION-ENVELOPE
Work Item: WI-5935
Responds to: bridge/gtkb-wi5935-wrap-parity-tests-004.md (LO NO-GO)

# REVISED - gtkb-wi5935-wrap-parity-tests (deliberations filled; parity matrix bound to identity-active marker scope)

## Summary

Revises the Slice F parity-test slice in response to the corrected LO verdict at `-004`. LO withdrew the goose-suspended premise (Finding 1; goose active per `harness-state/harness-identities.json`) and confirmed the Slice C sequencing gate is satisfied (Finding 4; core GO at `-006`). Two substantive gaps remained and are addressed here: (Finding 2) the Prior Deliberations placeholder is now filled; (Finding 3) the parity matrix is explicitly bound to the post-Slice-C marker scope with a disposition for every other identity-active harness. This proposal is filed as the next numbered file `bridge/gtkb-wi5935-wrap-parity-tests-005.md` under `bridge/` (append-only).

## Requirement Sufficiency

Existing requirements sufficient (Slice C GO at `-006`): `ADR-CROSS-HARNESS-PARITY-001` + `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` define the parity invariant this tests. The Slice A DCL and Slice B SPEC v2 are captured into MemBase before implementation-start (sequencing note, not a GO blocker).

target_paths: ["platform_tests/scripts/test_modernization_harness_parity.py", "platform_tests/scripts/test_session_envelope_runtime.py", "groundtruth.db"]

## Implementation Plan (parity matrix bound to identity-active marker scope)

1. **Required marker population (Finding 3):** the parity matrix asserts fail-closed wrap parity for the harnesses that carry a `RUNTIME_HARNESS_MARKERS` entry after Slice C GO-006: `codex`, `claude`, `antigravity`, `cursor`, `goose`. For each, a concurrent same-harness two-context wrap fails closed identically, and the harness's session-id marker resolves via the uniform `resolve_session_id`.
2. **Identity-active but unmarked harnesses (Finding 3 disposition):** `ollama`, `openrouter`, `alibaba-cloud-studio` are `status=active` in the identity file but have no `RUNTIME_HARNESS_MARKERS` entry. Scoped disposition: they are EXCLUDED from the wrap-fail-closed parity matrix in this slice because the wrap runtime resolves session identity only via `RUNTIME_HARNESS_MARKERS`; this is an explicit scoped deferral (typed: deliberate-deferral) tracked under WI-5936 Slice 2 / the marker-coverage follow-up, NOT an unregistered-invisible gap. A parity-guard test asserts every identity-active harness is EITHER in the marker matrix OR named in this deferral list, so a future unmarked harness fails the guard loudly rather than passing silently.
3. Assert the per-harness `session-envelope.json` is never the wrap mutation target on any covered harness.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001` - the parity invariant; `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` (Slice A, GO); `SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001` v2 (Slice B, GO).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `GOV-FILE-BRIDGE-AUTHORITY-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Specification-Derived Verification

- `python -m pytest platform_tests/scripts/test_modernization_harness_parity.py` - per-harness fail-closed wrap parity matrix over {codex, claude, antigravity, cursor, goose}; plus the marker-coverage guard (every identity-active harness is in the matrix or the named deferral list). Observed results reported in the implementation report.
- `ruff check` / `ruff format --check` on changed test files.

## Prior Deliberations

- `DELIB-20260804-TAFE-DISPATCHER-NOT-ROLE-AUTHORITY` - owner decision: TAFE/dispatcher registry projection is not harness/session role or active-status authority; identity file is authoritative.
- Slice C GO: `bridge/gtkb-wi5935-wrap-single-context-core-006.md` (GO) - marker scope goose + cursor accepted; satisfies the prior F3 sequencing gate.
- `DELIB-S20260626-CROSS-HARNESS-PARITY-ADVISORY` - cross-harness parity design advisory.

## Owner Decisions / Input

- 2026-08-04 (this session): Owner directive - TAFE/dispatcher registry projection is not valid authority for harness/session role or active-status; identity file `harness-state/harness-identities.json` is authoritative (all eight harnesses active, including goose and cursor).

## Cross-Harness Disposition

This slice applies the parity invariant across the marker-bearing active harnesses and names a typed scoped deferral (deliberate-deferral) for the three identity-active unmarked harnesses, with a guard preventing silent gaps (per `ADR-CROSS-HARNESS-PARITY-001` Q7/Q8). No permanent waiver requested; the deferral is review-triggered by WI-5936 Slice 2 marker-coverage work.

## Recommended Commit Type

test: (test-only parity additions + coverage guard).
