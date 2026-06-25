NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: abf38f9d-9205-44ac-a4c4-92490c175d3e
author_model: claude-opus-4-8
author_model_version: opus-4-8
author_model_configuration: Interactive Prime Builder session (::init gtkb pb); workspace E:/GT-KB; envelope-disposition drive

# Implementation Proposal — WI-4685 Single-Active Activity-Envelope Invariant (source/test)

bridge_kind: prime_proposal
Document: gtkb-wi4685-single-active-envelope-invariant
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4685

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/session/topic_router.py", ".codex/gtkb-hooks/session_wrapup_trigger_dispatch.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_session_wrapup_trigger_dispatch.py"]

## Summary

Implements the single-active activity-envelope invariant (WI-4685) in the runtime, now that the governing specs are ratified to v3. At most ONE topic envelope is open at a time across all types: `::open <type>` closes the current envelope (if any) then opens the new one; bare `::close` and `::close <type>` close the current envelope; bare `::close` with nothing open is an idempotent no-op. Supersedes the prior one-topic-per-type runtime behavior (`open_topic` currently rejects same-type re-open and appends, permitting multiple concurrent envelopes of different types).

## Specification Links

- `SPEC-TOPIC-ENVELOPE-ROUTER-001` v3 — single-active invariant; bare `::close` recognized (close current); `::open <type>` closes current then opens. (Owner-ratified 2026-06-25, DELIB-20265891.)
- `DCL-TOPIC-ENVELOPE-ROUTING-001` v3 — close grammar `^::close( (ops|deliberation|build|test|spec|project))?$` (bare + typed); clause 3 close triggers; assertion 2. (Owner-ratified 2026-06-25.)
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge numbered-file-chain authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below; tests derive from the v3 specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project/Work Item/PAUTH headers present.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths are in-root under `E:\GT-KB`; no out-of-root or Agent Red mutation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — covered by PAUTH rowid-299 (source/test_addition/hook_upgrade classes include this work).
- `GOV-STANDING-BACKLOG-001` — WI-4685 is an active member of the cited project.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-TOPIC-ENVELOPE-ROUTER-001` v3 and `DCL-TOPIC-ENVELOPE-ROUTING-001` v3 (both owner-ratified 2026-06-25 via AUQ; DELIB-20265891) fully specify the single-active behavior. No new or revised requirement is required before implementation.

## Implementation Plan

1. `groundtruth-kb/src/groundtruth_kb/session/envelope.py`:
   - `open_topic`: before opening, close any currently-open topic (auto-close with `close_outcome="auto_closed_by_open_supplant"`), enforcing single-active. Remove the same-type-already-open rejection (single-active makes it moot).
   - Add `close_current_topic(project_root, *, harness_name, harness_id, close_outcome="closed")`: closes the single currently-open topic (idempotent no-op returning `None` when none open).
   - `close_topic(type)`: assert the currently-open topic is `<type>`; on mismatch raise `EnvelopeError` (guidance error) rather than silently scanning for a same-type topic.
2. `groundtruth-kb/src/groundtruth_kb/session/topic_router.py`:
   - `TOPIC_COMMAND_RE`: accept bare `::close` via optional type group — `^::open (<types>)$|^::close( (<types>))?$` (open still requires a type).
   - `parse_topic_command`: return `topic_type=None` for bare `::close`.
   - `handle_topic_command`: bare close → `close_current_topic`; `::close <type>` → `close_topic(type)`; `::open <type>` → `open_topic` (which now closes-current-first).
3. `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py`: handle a `TopicCommand` whose `topic_type` is `None` (bare close) when it dispatches on close — route to close-current rather than dereferencing a `None` type.
4. Tests in `platform_tests/scripts/test_session_envelope_runtime.py` and `platform_tests/scripts/test_session_wrapup_trigger_dispatch.py` (below).

## Spec-Derived Verification Plan (spec-to-test mapping)

| Specification (clause) | Test / verification | Command |
|---|---|---|
| `SPEC-TOPIC-ENVELOPE-ROUTER-001` v3 — single-active (`::open <type>` closes current) | `test_open_closes_current_topic` (open A, open B → only B open; A `close_outcome=auto_closed_by_open_supplant`) | `python -m pytest platform_tests/scripts/test_session_envelope_runtime.py` |
| `SPEC-...-ROUTER-001` v3 — bare `::close` closes current | `test_bare_close_closes_current_topic` | same |
| `SPEC-...-ROUTER-001` v3 — bare `::close` no-op when none open | `test_bare_close_idempotent_noop` | same |
| `DCL-TOPIC-ENVELOPE-ROUTING-001` v3 — close grammar (bare + typed) | `test_parse_bare_close` / `test_parse_typed_close` (parser accepts both) | same |
| `DCL-...-ROUTING-001` v3 — `::close <type>` type mismatch is a guidance error | `test_typed_close_type_mismatch_errors` | same |
| Codex hook parity (bare close) | `test_hook_parse_bare_close` | `python -m pytest platform_tests/scripts/test_session_wrapup_trigger_dispatch.py` |

Code-quality gates on touched files: `python -m ruff check <files>` and `python -m ruff format --check <files>`.

## Prior Deliberations

- `DELIB-20260621` (DEC-4) — locks the six-member activity vocabulary; the explicit-hint up-to-5 concurrency clause originates and is superseded here.
- `DELIB-20260638` — standing envelope-program content goal; original topic-envelope concurrency lineage.
- `DELIB-20265287` — re-admit `ops`; activity-vocabulary defect classification.
- `DELIB-20265891` — this drive's owner decision (resolve WI-4683/4684; inline-formal-drive) + the WI-4685 v3 spec-amendment AUQ ratification (2026-06-25).
- No prior deliberation conflicts with the single-active model (deliberation search 2026-06-25 returned no opposing decision).


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- AUQ 2026-06-25 (DELIB-20265891): owner chose "Drive formal work inline; AUQ each" for the remaining envelope-disposition WIs, authorizing this source/test bridge after the formal spec amendment.
- AUQ 2026-06-25 (`AUQ-2026-06-25-wi4685-single-active`): owner approved both v3 spec amendments (`SPEC-TOPIC-ENVELOPE-ROUTER-001` v3 + `DCL-TOPIC-ENVELOPE-ROUTING-001` v3), which are the requirements this implementation satisfies.

## Risk / Rollback

- Risk: behavioral change to the envelope state machine could affect callers relying on multiple concurrent topics. Mitigation: `grep` confirms the only callers are `topic_router.handle_topic_command`, `cli_session_handoff` (typed path, unaffected), and the session-wrap auto-close (already iterates all open topics). `cli_session_handoff` keeps the typed `close_topic` path and is not modified.
- Rollback: revert the three source files + tests; the v3 specs remain (they are owner-ratified requirements). No data migration; envelope state is per-session local JSON.
