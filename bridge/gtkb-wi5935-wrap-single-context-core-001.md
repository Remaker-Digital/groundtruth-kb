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
Document: gtkb-wi5935-wrap-single-context-core
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-SESSION-ENVELOPE-WI-5935-SESSION-ENVELOPE-SINGLE-CONTEXT-IMPLEMENTATION
Work Item: WI-5935
Project: PROJECT-GTKB-SESSION-ENVELOPE

# WI-5935 Slice C - Session-id-validated wrap core (fail-closed cross-context ::wrap; goose marker parity)

## Summary

Core implementation of WI-5935. Makes `close_session` / `run_wrap` / `ensure_current` session-id-validated and fail-closed: a `::wrap` from one session-context cannot close another context's envelope under concurrent same-harness sessions. Re-points the wrap mutation target from the per-harness projection to the authoritative per-session document. Adds the goose entry to `RUNTIME_HARNESS_MARKERS` and goose membership to `scripts/gtkb_session_id.py` so goose resolves its session id natively.

## Requirement Sufficiency

Existing requirements sufficient (once Slice A DCL and Slice B spec v2 are GO): `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` + revised `SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001` define the behavior this implements.

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/session/wrap.py", "scripts/gtkb_session_id.py", "platform_tests/scripts/test_session_envelope_runtime.py", "groundtruth.db"]

## Implementation Plan

1. `close_session`: resolve invoking `session_id` (via `resolve_session_id`); fail closed with an owner-visible diagnostic when the live envelope `session_id` != invoking id. Never mutate another context's document.
2. `run_wrap` / `ensure_current`: operate on the per-session document; treat the per-harness `session-envelope.json` as a read-only compatibility projection.
3. Add `goose` entry to `RUNTIME_HARNESS_MARKERS` (goose session-id env marker) and add the goose marker to `SESSION_ID_ENV_VARS` + the bridge/marker orders in `scripts/gtkb_session_id.py` (uniform, no per-harness wrap design).
4. Spec-derived tests in `test_session_envelope_runtime.py`.

## Specification Links

- `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` (Slice A) - fail-closed single-context binding.
- `SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001` v2 (Slice B) - per-session authoritative path + fail-closed precondition.
- `SPEC-CANONICAL-WRAP-KEYWORD-SYNTAX-001` v1; `ADR-CROSS-HARNESS-PARITY-001` (uniform behavior).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `GOV-FILE-BRIDGE-AUTHORITY-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Specification-Derived Verification

- Fail-closed mismatch: `python -m pytest platform_tests/scripts/test_session_envelope_runtime.py` - new case: two concurrent same-harness contexts; context-2 `run_wrap` raises and leaves context-1's envelope open.
- Per-session authoritative target: test asserts wrap mutates `session-envelopes/<id>.json`, not the projection.
- Goose marker: `python -m pytest platform_tests/scripts/test_gtkb_session_id.py` - goose env var resolves; `RUNTIME_HARNESS_MARKERS['goose']` present.
- Lint/format gates: `ruff check` + `ruff format --check` on changed files.

## Prior Deliberations

- `DELIB-20260637` - envelope meta-model; `DELIB-20263212` - envelope persists across compaction.


### Helper-suggested candidates

_Deliberation semantic search degraded (SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 35424 and this is thread id 20700.); do not treat this section as an authoritative empty search result._
_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- 2026-08-04: Owner selected Option 1 - file all slices now, staged by dependency. Depends on Slice A + Slice B GO.

## Cross-Harness Disposition

Per `ADR-CROSS-HARNESS-PARITY-001` Q8: the fail-closed wrap rule is uniform (no per-harness design); each harness surfaces its session id via its runtime-marker entry in `RUNTIME_HARNESS_MARKERS`. This slice adds the goose marker so goose reaches parity with antigravity/claude/codex. No typed waiver requested.

## Recommended Commit Type

fix: (repairs broken cross-context wrap behavior; no new capability surface beyond the parity marker).
