NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: abf38f9d-9205-44ac-a4c4-92490c175d3e
author_model: claude-opus-4-8
author_model_version: opus-4-8
author_model_configuration: Interactive Prime Builder session (::init gtkb pb); workspace E:/GT-KB; envelope-disposition drive

# Implementation Report — WI-4685 Single-Active Activity-Envelope Invariant

bridge_kind: implementation_report
Document: gtkb-wi4685-single-active-envelope-invariant
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC
Responds-To: bridge/gtkb-wi4685-single-active-envelope-invariant-002.md (GO)

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4685

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/session/topic_router.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_session_wrapup_trigger_dispatch.py"]

## Recommended Commit Type

Recommended commit type: `feat` — adds a new command surface (bare `::close`) and replaces the one-per-type concurrency model with the single-active invariant. New runtime behavior, not a pure repair.

## Summary

Implemented the single-active activity-envelope invariant per the GO at `-002`, now that `SPEC-TOPIC-ENVELOPE-ROUTER-001` v3 and `DCL-TOPIC-ENVELOPE-ROUTING-001` v3 are owner-ratified. At most one topic envelope is open at a time across all types; `::open <type>`, bare `::close`, and `::close <type>` all close the current envelope; bare `::close` with nothing open is an idempotent no-op; `::close <type>` against a different open type is a guidance error.

## Files Changed (4 of the 5 declared target_paths)

- `groundtruth-kb/src/groundtruth_kb/session/envelope.py` — `open_topic` now auto-closes any currently-open topic (`close_outcome="auto_closed_by_open_supplant"`) before opening (single-active), replacing the same-type "already open" rejection. Added `_close_open_topic` helper and `close_current_topic` (bare close). `close_topic(type)` asserts the open topic is `type` (guidance error on mismatch) and is an idempotent no-op when nothing is open.
- `groundtruth-kb/src/groundtruth_kb/session/topic_router.py` — split `TOPIC_COMMAND_RE` into `TOPIC_OPEN_RE` (`^::open (<types>)$`) and `TOPIC_CLOSE_RE` (`^::close( (<types>))?$`, the DCL v3 assertion regex accepting bare + typed). `parse_topic_command` returns `topic_type=None` for bare close; `handle_topic_command` routes bare close to `close_current_topic`; `render_topic_context` echoes bare close without a `None` literal.
- `platform_tests/scripts/test_session_envelope_runtime.py` — replaced the one-per-type test with single-active; added supplant-on-open, bare-close, idempotent-no-op, and typed-mismatch tests; updated the parser-strictness test for bare `::close`.
- `platform_tests/scripts/test_session_wrapup_trigger_dispatch.py` — added bare-`::close` parity assertion (the hook reuses the shared parser).

**Declared-but-unmodified:** `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py` was in the proposal's `target_paths` but needed no edit — it delegates through the shared `parse_topic_command`/`handle_topic_command`, which now handle bare close. (Editing fewer than the declared `target_paths` is within the impl-start authorization.)

## Specification Links (carried forward from proposal)

- `SPEC-TOPIC-ENVELOPE-ROUTER-001` v3 — single-active invariant; bare `::close`.
- `DCL-TOPIC-ENVELOPE-ROUTING-001` v3 — close grammar (bare + typed); clause 3 triggers; assertion 2.
- `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (all paths in-root); `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `GOV-STANDING-BACKLOG-001`.

## Spec-to-Test Mapping (executed)

| Specification (clause) | Test | Result |
|---|---|---|
| `SPEC-...-ROUTER-001` v3 — `::open` closes current (single-active) | `test_open_topic_closes_current_topic_of_other_type`, `test_topic_open_close_is_strict_and_single_active` | pass |
| `SPEC-...-ROUTER-001` v3 — bare `::close` closes current | `test_bare_close_closes_current_topic` | pass |
| `SPEC-...-ROUTER-001` v3 — bare/typed close idempotent no-op | `test_bare_close_is_idempotent_noop_when_nothing_open` | pass |
| `DCL-...-ROUTING-001` v3 — close grammar accepts bare + typed (strict) | `test_wrap_and_topic_command_parsers_are_strict` | pass |
| `DCL-...-ROUTING-001` v3 — `::close <type>` mismatch is a guidance error | `test_typed_close_type_mismatch_is_guidance_error` | pass |
| Codex hook parser parity (bare close) | `test_hook_recognizes_strict_topic_commands` | pass |

## Verification Commands & Results

```text
python -m pytest platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_wrapup_trigger_dispatch.py -q
  => 19 passed

python -m ruff check <4 changed files>
  => All checks passed!

python -m ruff format --check <4 changed files>
  => 4 files already formatted
```

## Out-of-Scope Test Note (not a WI-4685 regression)

A broader regression run flagged 1 failure: `test_session_self_initialization.py::test_harness_role_assignment_map_is_startup_source_of_truth` (expects "Interactive resolved role: Loyal Opposition"; live resolves codex=prime-builder with a STALE=1 harness-parity warning). This is excluded from WI-4685 scope with evidence: (1) `scripts/session_self_initialization.py` imports none of the changed modules (`grep` for `topic_router`/`session.envelope`/`parse_topic_command`/`open_topic`/`close_topic` returns empty); (2) the assertion concerns role disclosure driven by the live harness registry/session state, not the topic-envelope runtime; (3) the test file was under concurrent edit by a parallel session during the run (an 18-line working-tree delta appeared and cleared between consecutive `git diff` calls). The WI-4685-scoped suite passes deterministically across repeated runs.

## Owner Decisions / Input

- AUQ 2026-06-25 (`DELIB-20265891`): owner chose "Drive formal work inline; AUQ each" for the remaining envelope WIs, authorizing this source/test bridge.
- AUQ 2026-06-25 (`AUQ-2026-06-25-wi4685-single-active`): owner ratified `SPEC-TOPIC-ENVELOPE-ROUTER-001` v3 + `DCL-TOPIC-ENVELOPE-ROUTING-001` v3 — the requirements this implementation satisfies.

## Prior Deliberations

- `DELIB-20260621` (DEC-4) — six-member vocabulary; supersedes the explicit-hint up-to-5 concurrency clause.
- `DELIB-20260638` — envelope-program lineage.
- `DELIB-20265287` — re-admit `ops`.
- `DELIB-20265891` — this drive's owner decision + WI-4685 v3 spec-amendment ratification.

## Risk / Rollback

Revert the four changed files; the v3 specs remain (owner-ratified requirements). No data migration — envelope state is per-session local JSON. The only behavioral coupling (`cli_session_handoff` typed `close`) is preserved for the matching-type path.
