NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S372-interactive-session-role-override-slice-2
author_model: Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI default reasoning, explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001
Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Work Item: WI-3458
target_paths: ["scripts/workstream_focus.py", "platform_tests/hooks/test_workstream_focus_session_role_marker.py"]

# GT-KB Interactive Session Role Override - Slice 2 - Session-State Role Marker Write

bridge_kind: prime_proposal

Document: gtkb-interactive-session-role-override-slice-2-session-role-marker
Version: 001 (NEW)
Date: 2026-05-29 UTC

## Summary

Slice 2 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE (Slice 1 VERIFIED at `bridge/gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer-007.md`). When an owner prompt carries the canonical init keyword `::init gtkb (pb|lo)` in an INTERACTIVE context (env-var `GTKB_BRIDGE_POLLER_RUN_ID` absent), the UserPromptSubmit handler in `scripts/workstream_focus.py` writes an ephemeral session-state role marker at `.claude/session/active-session-role.json` recording the keyword-derived role, the harness session id, and a timestamp. The marker is the carrier that later slices (AXIS 2 surface, workstream focus, attribution) read to resolve the session-stated role.

The change is purely additive: the existing startup-disclosure relay behavior (Slice 1) is preserved; the marker write happens on the same init-keyword code path that already resolves the role mode via `_startup_role_mode_from_prompt`. `scripts/workstream_focus.py` is the shared module that both the Claude hook (`.claude/hooks/workstream-focus.py`) and the Codex wrapper (`.codex/gtkb-hooks/workstream-focus.cmd`) invoke, so one change covers both harnesses.

This implements `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` Decision 4 (session-stated role held in an ephemeral session-scoped marker; mid-session re-typing overrides) and `DCL-SESSION-ROLE-RESOLUTION-001` assertions 2, 6, 7.

## In-Root Boundary Affirmation

Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md`: both touched files are in-root (`E:\GT-KB\scripts\`, `E:\GT-KB\platform_tests\hooks\`). The runtime marker file is written to the in-root `.claude/session/` directory (the same directory as the existing `work-subject.json`). No `applications/<name>/` paths; no Agent Red live dependency; no out-of-root path.

## Problem Statement

Slice 1 made both `-pb` and `-lo` startup-disclosure caches available so the keyword-keyed disclosure relay succeeds for either role. But the rest of the interactive surfaces (AXIS 2 work surface, focus menu, MemBase attribution) still have no record of which role the owner declared for this session. The architecture's carrier for that record is the ephemeral session-state marker (`ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` Decision 4). Slice 2 writes the marker; Slices 3-6 invalidate it at SessionStart and read it from the consuming surfaces.

Today `handle_hook_payload` (`scripts/workstream_focus.py:1597`) extracts only the prompt text and passes it to `handle_user_prompt`; the Claude Code UserPromptSubmit payload's `session_id` field is discarded. The init-keyword role is computed at line 1368 (`_startup_role_mode_from_prompt(prompt)`) but only used to select the disclosure cache; nothing persists the declared role for later hooks in the same session.

## Proposed Change

### `scripts/workstream_focus.py`

1. **Thread the session id (additive).** `handle_hook_payload` reads `payload.get("session_id")` and passes it to `handle_user_prompt(prompt, project_root, session_id=...)`, which forwards it to `_consume_discard_first_prompt_gate(prompt, project_root, session_id=...)`. All new parameters default to `None`, preserving every existing caller and test.

2. **Add a marker-write helper.** A new `_write_session_role_marker(role_profile, session_id, project_root)` writes `.claude/session/active-session-role.json` with:

```json
{
  "role": "<prime-builder|loyal-opposition>",
  "session_id": "<harness session id or null>",
  "written_at": "<iso-8601 UTC>",
  "source": "init_keyword"
}
```

   The `role` value is the canonical role profile mapped from the keyword mode (`pb` -> `prime-builder`, `lo` -> `loyal-opposition`) per `DCL-SESSION-ROLE-RESOLUTION-001` assertion 7. The write fails soft (an `OSError` does not break the hook).

3. **Call the helper on the interactive init-keyword path only.** At the init-match branch (`_consume_discard_first_prompt_gate`, around line 1353-1368), when `_startup_role_mode_from_prompt(prompt)` returns a role mode AND `os.environ.get("GTKB_BRIDGE_POLLER_RUN_ID")` is absent, write the marker. The `GTKB_BRIDGE_POLLER_RUN_ID`-absent guard scopes the write to interactive owner-typed declarations per the `DCL-SESSION-ROLE-RESOLUTION-001` resolution table (the "Interactive declaration" row requires the env-var absent); headless dispatch sessions (env-var present) never write the marker.

### `platform_tests/hooks/test_workstream_focus_session_role_marker.py` (NEW)

A test module asserting the marker is written on an interactive init-keyword prompt, is NOT written when the env-var is present (headless), is NOT written for a non-keyword prompt, carries the session id, and maps the keyword mode to the canonical role profile. Parameterized over the `pb` and `lo` modes; the shared-module change covers both harnesses through the single code path.

## Specification Links

- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v1 - Decision 4 (ephemeral session-scoped marker; mid-session re-typing overrides) implemented.
- `DCL-SESSION-ROLE-RESOLUTION-001` v1 - assertion 2 (marker written on the keyword code path), assertion 6 (marker carries session id), assertion 7 (role in `{prime-builder, loyal-opposition}`).
- `GOV-SESSION-ROLE-AUTHORITY-001` v1 - session-stated role declared via the canonical init keyword; not persisted to durable storage (the marker is ephemeral and SessionStart-invalidated in Slice 3).
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v2 - the `INTERACTIVE_OVERRIDE_AUTHORIZED` receiver decision (env-var absent + keyword present) is the path on which the marker is written.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v2 - the keyword may appear on any owner prompt; the marker write supports mid-session re-declaration.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root boundary affirmed above.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is filed at `-001` and the `bridge/INDEX.md` update inserts a `NEW:` line at the top of a fresh entry; no prior bridge version deleted or rewritten (append-only).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this Specification Links section satisfies the linkage gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the `Project Authorization`/`Project`/`Work Item` triple in the header satisfies the linkage gate.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - covered by `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (active; WI-3458 covered via active project membership).
- `GOV-ARTIFACT-APPROVAL-001` - this slice inserts no canonical artifact; it implements behavior governed by the v1/v2 artifacts inserted in S371 under DELIB-2507.
- `GOV-STANDING-BACKLOG-001` - single behavior change; not a bulk operation. See Clause Scope Clarification below.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory), `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory), `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` (parent GO).
- `bridge/gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer-007.md` (Slice 1 VERIFIED; the dependency this slice builds on).

## Clause Scope Clarification (Not a Bulk Operation)

Per `GOV-STANDING-BACKLOG-001` bulk-ops clause-scope clarification: this slice is NOT a bulk operation and produces no bulk-operation inventory artifact, no review-packet, and no `formal-artifact-approval` packet because none is required. It is a single additive behavior change to one shared module plus one new test module. It performs no work_items bulk insert/update/retire/supersede, no project create/retire, no authorization change. Were a bulk action ever in scope it would require an explicit owner-approval `formal-artifact-approval` packet plus an inventory artifact and a review-packet; this slice carries none because it is a single-function-path change. Evidence pattern tokens: single-function change, not a bulk operation; no inventory, no review-packet, no formal-artifact-approval packet required.

## Prior Deliberations

- `DELIB-2507` - S371 owner directive and the 6 AUQ architecture decisions; owner-decision deliberation for PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001. Decision 4 (ephemeral session-scoped marker, no durable persistence, mid-session re-typing overrides) is the direct authority for this slice.
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` - parent GO approving the 10-slice plan; Slice 2 is the marker-write slice.
- `bridge/gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer-007.md` - Slice 1 VERIFIED; established the keyword-keyed cache the marker complements.
- `bridge/gtkb-canonical-init-keyword-syntax-001-007.md` (GO at -008) - canonical keyword syntax this slice's matcher reuses.
- No prior deliberation has introduced a session-state role marker; this is the first artifact to write `.claude/session/active-session-role.json`.

## Requirement Sufficiency

Existing requirements sufficient. ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001 Decision 4, DCL-SESSION-ROLE-RESOLUTION-001 assertions 2/6/7, and the GO'd scoping plan at -004 fully specify the marker-write behavior, schema fields, and the interactive-only guard. No new owner clarification required for Slice 2. One implementation-detail question (the Codex-side session-id source) is raised as a Codex Review Ask but does not require new owner requirement capture.

## target_paths Note

The machine-readable `target_paths` metadata is the inline-JSON line in the header block. Two files: the shared module `scripts/workstream_focus.py` and a new test module. No KB/MemBase mutation in the source change: `.claude/session/active-session-role.json` is an ephemeral filesystem marker, not a `groundtruth.db` row. No change to `.claude/hooks/workstream-focus.py` or `.codex/gtkb-hooks/workstream-focus.cmd` is needed because both already pass the full payload dict (which carries `session_id`) into the shared `handle_hook_payload`.

## Spec-Derived Verification Plan

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, each acceptance criterion maps to an executable test:

| Spec / clause | Test | Expectation |
|---|---|---|
| DCL-SESSION-ROLE-RESOLUTION-001 assertion 2 (marker written on keyword path) | `test_marker_written_on_interactive_init_keyword` (pb, lo) | marker file exists with correct role after an interactive `::init gtkb <mode>` prompt |
| DCL-SESSION-ROLE-RESOLUTION-001 assertion 7 (role-set member) | same test | marker `role` is `prime-builder` for `pb`, `loyal-opposition` for `lo` |
| DCL-SESSION-ROLE-RESOLUTION-001 assertion 6 (carries session id) | `test_marker_records_session_id` | marker `session_id` equals the payload `session_id` |
| Interactive-only guard (env-var present -> no marker) | `test_marker_not_written_under_headless_dispatch` | with `GTKB_BRIDGE_POLLER_RUN_ID` set, no marker written |
| No keyword -> no marker | `test_marker_not_written_for_non_keyword_prompt` | ordinary prompt leaves no marker |
| Mid-session re-typing overrides | `test_marker_overwritten_on_redeclaration` | a second `::init gtkb lo` after `::init gtkb pb` replaces the marker role |
| Existing startup-relay behavior preserved | `test_startup_relay_response_unchanged` | the init-keyword gate still returns the relay-source response (Slice 1 behavior) |
| Fail-soft on unwritable marker dir | `test_marker_write_failsoft` | a simulated `OSError` does not raise out of the handler |

Commands at implementation time: `python -m pytest platform_tests/hooks/test_workstream_focus_session_role_marker.py -v` and `python -m pytest platform_tests/hooks/test_workstream_focus.py -q` (regression on the existing shared-module tests), plus `ruff check scripts/workstream_focus.py <new test>`.

## Acceptance Criteria

- Codex issues GO confirming: the threading is additive (no existing caller/test breaks); the interactive-only env-var guard is correct; the marker schema satisfies DCL-SESSION-ROLE-RESOLUTION-001 assertions 6/7; the existing startup-relay behavior is preserved.
- If GO, implement and file the post-implementation report as the next version with `NEW:` above the GO line.
- If NO-GO, revise via the next version REVISED (no in-place edit of `-001`).

## Risk and Rollback

- **Risk:** the Codex UserPromptSubmit payload may not include a `session_id` field, so the Codex-side marker would record `session_id: null`. **Mitigation / Codex Review Ask:** I propose writing `session_id` from `payload.get("session_id")` with a documented fallback to `os.environ.get("CLAUDE_SESSION_ID")` then `None`; readers (Slice 3 invalidation, Slice 4-6 consumers) treat a `null`/mismatched session id per `DCL-SESSION-ROLE-RESOLUTION-001` assertion 6 (stale marker invalid). I ask Codex to confirm the canonical Codex session-id source or accept the documented fallback.
- **Risk:** threading new parameters could break existing callers. **Mitigation:** every new parameter defaults to `None`; `test_workstream_focus.py` regression covers existing callers.
- **Risk:** the marker write races a later same-turn hook read (AXIS 2 surface in Slice 4). **Mitigation:** hook ordering in `.claude/settings.json` runs `workstream-focus.py` before `bridge-axis-2-surface.py`; the marker is written before any same-turn reader. This ordering is asserted in Slice 4, not Slice 2.
- **Rollback:** revert the `scripts/workstream_focus.py` changes; delete the marker file. No durable state is introduced (the marker is ephemeral and not yet read by any consumer until Slices 4-6).

## Owner Decisions / Input

This slice proceeds under `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (active; covers WI-3458 via active project membership; cites `DELIB-2507`). Per `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` the project authorization removes per-slice direct AskUserQuestion overhead for bounded project work; per `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` this slice still runs through the full bridge protocol (this NEW -> Codex GO -> implement -> post-implementation report -> VERIFIED). DELIB-2507 holds the 6 S371 owner AskUserQuestion decisions, of which Decision 4 (session-scoped lifetime; no persistence file; mid-session re-typing overrides) and Decision 1 (full session override) directly authorize this slice's marker-write design. No new owner decision is required.

## Codex Review Asks

1. Confirm the additive session-id threading (default `None`) does not break existing `handle_hook_payload` / `handle_user_prompt` / `_consume_discard_first_prompt_gate` callers or `test_workstream_focus.py`.
2. Confirm the `GTKB_BRIDGE_POLLER_RUN_ID`-absent guard correctly scopes the marker write to interactive declarations per the DCL-SESSION-ROLE-RESOLUTION-001 resolution table.
3. Confirm or correct the Codex-side session-id source (see Risk #1): accept the `payload.get("session_id")` -> `CLAUDE_SESSION_ID` -> `None` fallback, or name the canonical Codex session token.
4. Confirm the marker schema satisfies DCL-SESSION-ROLE-RESOLUTION-001 assertions 6 and 7.
5. Flag any specification this proposal should cite but does not.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
