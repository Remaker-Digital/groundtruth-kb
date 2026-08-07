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
Document: gtkb-wi5935-wrap-single-context-core
Version: 005
Project Authorization: PAUTH-PROJECT-GTKB-SESSION-ENVELOPE-WI-5935-SESSION-ENVELOPE-SINGLE-CONTEXT-IMPLEMENTATION
Project: PROJECT-GTKB-SESSION-ENVELOPE
Work Item: WI-5935
Responds to: bridge/gtkb-wi5935-wrap-single-context-core-004.md (LO NO-GO)

# REVISED - gtkb-wi5935-wrap-single-context-core (marker scope corrected: goose + cursor)

## Summary

Revises the Slice C core fix in response to the corrected LO verdict at `-004`. LO upheld the NO-ACTION challenge (Finding 1: the goose-suspended premise was invalid; goose is active per `harness-state/harness-identities.json`) and identified the single remaining blocker (Finding 2): the prior version added the goose marker but omitted the active reviewing harness cursor from `RUNTIME_HARNESS_MARKERS`. This REVISED proposal corrects the marker scope to cover BOTH goose and cursor (all active identity-file harnesses that currently lack a marker entry), and retains the endorsed fail-closed `resolve_session_id` design (Finding 3).

## Requirement Sufficiency

Existing requirements sufficient (Slice A DCL GO + Slice B SPEC v2 GO): `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` + revised `SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001` define the fail-closed behavior this implements. The Slice A DCL and Slice B SPEC v2 must be captured into MemBase before implementation-start (LO Finding 3 sequencing note; not a GO blocker).

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/session/wrap.py", "scripts/gtkb_session_id.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_gtkb_session_id.py", "groundtruth.db"]

## Implementation Plan

1. `close_session`: resolve the invoking `session_id` (uniform `resolve_session_id`); fail closed with an owner-visible diagnostic when the live envelope `session_id` differs; never mutate another context's per-session document.
2. `run_wrap` / `ensure_current`: operate on the authoritative per-session document `session-envelopes/<session_id>.json`; treat the per-harness `session-envelope.json` as a read-only compatibility projection (never the wrap mutation target).
3. Marker coverage (corrected scope): add BOTH `cursor` and `goose` entries to `RUNTIME_HARNESS_MARKERS` in `envelope.py` - `cursor: ("CURSOR_CONVERSATION_ID",)`; `goose: ("GOOSE_SESSION_ID",)`. Add `GOOSE_SESSION_ID` to `SESSION_ID_ENV_VARS` and the bridge/marker orders in `scripts/gtkb_session_id.py` (`CURSOR_CONVERSATION_ID` is already a member). Uniform, no per-harness wrap design; covers the active identity-file harnesses that lacked a marker.
4. Spec-derived tests in `test_session_envelope_runtime.py` and `test_gtkb_session_id.py`.

## Specification Links

- `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` (Slice A, GO) - fail-closed single-context binding.
- `SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001` v2 (Slice B, GO) - per-session authoritative path + fail-closed precondition.
- `SPEC-CANONICAL-WRAP-KEYWORD-SYNTAX-001` v1; `ADR-CROSS-HARNESS-PARITY-001` (uniform behavior).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `GOV-FILE-BRIDGE-AUTHORITY-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Specification-Derived Verification

- Fail-closed mismatch: `python -m pytest platform_tests/scripts/test_session_envelope_runtime.py` - new case: two concurrent same-harness contexts; context-2 `run_wrap` raises and leaves context-1's envelope open.
- Per-session authoritative target: test asserts wrap mutates `session-envelopes/<id>.json`, not the projection.
- Marker coverage: `python -m pytest platform_tests/scripts/test_gtkb_session_id.py` - `GOOSE_SESSION_ID` and `CURSOR_CONVERSATION_ID` resolve; `RUNTIME_HARNESS_MARKERS['goose']` and `RUNTIME_HARNESS_MARKERS['cursor']` present.
- Lint/format gates: `ruff check` + `ruff format --check` on changed files.

## Prior Deliberations

- `DELIB-20260804-TAFE-DISPATCHER-NOT-ROLE-AUTHORITY` - owner decision (projection not role/active-status authority; identity file is).
- `DELIB-20260637` - envelope meta-model; `DELIB-20263212` - envelope persists across compaction.

## Owner Decisions / Input

- 2026-08-04 (this session): Owner directive - TAFE/dispatcher registry projection is not valid authority for harness/session role or active-status; identity file is authoritative (goose active).

## Cross-Harness Disposition

Fail-closed wrap rule is uniform (no per-harness design); each active harness surfaces its session id via its `RUNTIME_HARNESS_MARKERS` entry. This revision adds cursor + goose entries so the active identity-file population is covered. No typed waiver requested (per `ADR-CROSS-HARNESS-PARITY-001` Q8).

## Recommended Commit Type

fix: (repairs broken cross-context wrap behavior + closes the active-harness marker gap).
