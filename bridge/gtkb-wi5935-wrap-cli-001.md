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
Document: gtkb-wi5935-wrap-cli
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-SESSION-ENVELOPE-WI-5935-SESSION-ENVELOPE-SINGLE-CONTEXT-IMPLEMENTATION
Work Item: WI-5935
Project: PROJECT-GTKB-SESSION-ENVELOPE

# WI-5935 Slice D - Simple intuitive wrap CLI (gt session wrap ergonomics)

## Summary

Delivers the WI-5935 requirement for a very simple, intuitive wrap CLI. Surfaces the fail-closed wrap (Slice C) through `gt session wrap` so the invoking session-context's id is auto-resolved (no manual `--harness-name`/`--session-id` needed) and a cross-context attempt fails closed with a clear owner-visible message.

## Requirement Sufficiency

Existing requirements sufficient (once Slice C is GO): `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` + Slice C define the behavior this CLI exposes.

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "platform_tests/scripts/test_session_envelope_runtime.py", "groundtruth.db"]

## Implementation Plan

1. `gt session wrap` resolves the invoking session-context id from runtime markers / `GTKB_SESSION_ID` (uniform `resolve_session_id`), not from a per-harness flag.
2. On mismatch, print the Slice C fail-closed diagnostic and exit non-zero; never close another context's envelope.
3. Keep the `::wrap` keyword path (SPEC-CANONICAL-WRAP-KEYWORD-SYNTAX-001) routing to the same CLI.

## Specification Links

- `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` (Slice A); `SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001` v2 (Slice B); `SPEC-CANONICAL-WRAP-KEYWORD-SYNTAX-001` v1.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `GOV-FILE-BRIDGE-AUTHORITY-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Specification-Derived Verification

- `python -m pytest platform_tests/scripts/test_session_envelope_runtime.py`: `gt session wrap` auto-resolves the invoking context; cross-context invocation fails closed (non-zero exit + diagnostic).
- `ruff check` / `ruff format --check` on changed files.

## Prior Deliberations

- `DELIB-20265897` - mechanical wrap/harvest model.


### Helper-suggested candidates

_Deliberation semantic search degraded (SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 31444 and this is thread id 20700.); do not treat this section as an authoritative empty search result._
_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- 2026-08-04: Owner selected Option 1 - file all slices now, staged by dependency. Depends on Slice C GO.

## Recommended Commit Type

feat: (new CLI ergonomics surface for wrap).
