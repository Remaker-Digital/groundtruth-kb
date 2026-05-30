REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S372-interactive-session-role-override-slice-2-revised-1
author_model: Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI default reasoning, explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001
Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Work Item: WI-3458
target_paths: ["scripts/workstream_focus.py", "platform_tests/hooks/test_workstream_focus_session_role_marker.py"]

# GT-KB Interactive Session Role Override - Slice 2 - Session-State Role Marker Write - REVISED-1

bridge_kind: implementation_proposal

Document: gtkb-interactive-session-role-override-slice-2-session-role-marker
Version: 003 (REVISED-1; addresses Codex NO-GO at -002 F1 + F2)
Date: 2026-05-29 UTC

## Response to NO-GO -002 (F1 + F2 Resolution)

Codex NO-GO -002 raised:

- **F1 (P1, blocking):** the marker schema permitted `session_id: null`, contradicting `DCL-SESSION-ROLE-RESOLUTION-001` assertion 6 ("MUST record the current harness session id"). Codex's evidence: the live Codex env exposes `CODEX_THREAD_ID` and `CLAUDE_CODE_SESSION_ID`, not the `CLAUDE_SESSION_ID` I proposed. A nullable marker is immediately invalid for the continuation path and creates downstream ambiguity in Slices 4-6 about whether `null` means "stale" or "valid".
- **F2 (P2, gating verification evidence):** the proposed regression command `python -m pytest platform_tests/hooks/test_workstream_focus.py -q` is currently red in the review environment (3 failures), but `platform_tests/hooks/test_workstream_focus.py` is not in `target_paths`, so Prime is not authorized by this proposal to repair them.

This REVISED-1 addresses both with no scope expansion to the source-change surface (still only `scripts/workstream_focus.py` plus the new Slice 2 test module):

### F1 resolution: non-null session-id contract with explicit fallback chain and fail-soft no-marker branch

The marker write requires a non-null session id. The resolution order is documented and tested:

1. `payload.get("session_id")` (Claude Code UserPromptSubmit hook payload field; the canonical source when present).
2. Environment fallback chain, in priority order: `GTKB_SESSION_ID`, `CODEX_SESSION_ID`, `CODEX_THREAD_ID`, `CLAUDE_SESSION_ID`, `CLAUDE_CODE_SESSION_ID`. The Codex chain (`CODEX_SESSION_ID` then `CODEX_THREAD_ID`) reflects Codex's live env per Codex's own evidence; the Claude chain (`CLAUDE_SESSION_ID` then `CLAUDE_CODE_SESSION_ID`) covers both observed names.
3. **Fail-soft: if no non-null session id is resolved, no marker is written.** The handler still returns the existing startup-relay response (Slice 1 behavior preserved). A fail-soft event is logged to the lifecycle-guard state so Slice 7's doctor check can WARN on chronic unresolvable-session-id conditions. No exception escapes the hook.

Marker schema (revised):

```json
{
  "role": "<prime-builder|loyal-opposition>",
  "session_id": "<non-null string>",
  "session_id_source": "<payload|env:GTKB_SESSION_ID|env:CODEX_SESSION_ID|env:CODEX_THREAD_ID|env:CLAUDE_SESSION_ID|env:CLAUDE_CODE_SESSION_ID>",
  "written_at": "<iso-8601 UTC>",
  "source": "init_keyword"
}
```

The `session_id_source` field records which source provided the id, so Slice 7 doctor checks can flag drift if the active source changes within a single session.

This satisfies `DCL-SESSION-ROLE-RESOLUTION-001` assertion 6 unconditionally: any persisted marker has a non-null `session_id`; a marker is never written with a null id; later Slices 3/4/5/6/7 read with the assertion-6 invariant guaranteed by the writer.

### F2 resolution: targeted regression set, no scope creep to existing tests

The verification plan is revised to deselect the three pre-existing failing tests in `platform_tests/hooks/test_workstream_focus.py` (captured at `WI-3460` per the gate-clean `backlog add` CLI as a separate test-bitrot defect, NOT part of Slice 2 scope):

- `test_startup_gate_emits_bounded_pointer_not_inlined_disclosure` (stale 2026-05-15 relay-cache fixture; ages out of freshness)
- `test_startup_gate_message_authorizes_one_read_only_read` (same stale-relay-cache path)
- `test_detect_counterpart_state_uses_project_root_paths_when_provided` (separate counterpart-state path-resolution drift)

The regression command becomes:

```text
python -m pytest platform_tests/hooks/test_workstream_focus.py -q -k "not test_startup_gate_emits_bounded_pointer_not_inlined_disclosure and not test_startup_gate_message_authorizes_one_read_only_read and not test_detect_counterpart_state_uses_project_root_paths_when_provided"
```

Expected: 47 passed (the deterministic green baseline Codex independently observed). Per `WI-3460` the three deselected tests are a separate reliability fix outside Slice 2; their repair will lift the deselection in a future change. The verification plan does NOT claim coverage Slice 2 doesn't actually exercise: it asserts the 47-test baseline holds (i.e., the additive marker-write change does not regress any green test), separate from the pre-existing failures.

### Unchanged from -001

ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001 Decision 4 framing; DCL-SESSION-ROLE-RESOLUTION-001 assertions 2/6/7 governance; the shared-module change in `scripts/workstream_focus.py`; the marker-only-on-interactive-init-keyword guard via `GTKB_BRIDGE_POLLER_RUN_ID` absent; the new test module name; the project + PAUTH + WI-3458 chain.

## In-Root Boundary Affirmation

Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md`: both touched files are in-root (`E:\GT-KB\scripts\`, `E:\GT-KB\platform_tests\hooks\`). The runtime marker file is written to the in-root `.claude/session/` directory. No `applications/<name>/` paths; no Agent Red live dependency; no out-of-root path.

## Summary

Slice 2 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE (Slice 1 VERIFIED at `bridge/gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer-007.md`). When an owner prompt carries the canonical init keyword `::init gtkb (pb|lo)` in an INTERACTIVE context (env-var `GTKB_BRIDGE_POLLER_RUN_ID` absent) AND a non-null session id is resolvable, the UserPromptSubmit handler in `scripts/workstream_focus.py` writes an ephemeral session-state role marker at `.claude/session/active-session-role.json` recording the keyword-derived role, the resolved harness session id, the source of that id, and a timestamp. If no session id is resolvable, the handler fails soft (no marker written) so that `DCL-SESSION-ROLE-RESOLUTION-001` assertion 6 (non-null session id) is satisfied unconditionally.

The change is purely additive: the existing startup-disclosure relay behavior (Slice 1) is preserved on every path; the marker write happens on the same init-keyword code path that already resolves the role mode via `_startup_role_mode_from_prompt`. `scripts/workstream_focus.py` is the shared module that both the Claude hook and the Codex wrapper invoke, so one change covers both harnesses.

## Problem Statement

(Unchanged from -001.) Slice 1 made both `-pb` and `-lo` startup-disclosure caches available so the keyword-keyed disclosure relay succeeds for either role. But the rest of the interactive surfaces (AXIS 2 work surface, focus menu, MemBase attribution) still have no record of which role the owner declared for this session. The architecture's carrier for that record is the ephemeral session-state marker. Slice 2 writes the marker; Slices 3-6 invalidate it at SessionStart and read it from the consuming surfaces.

Today `handle_hook_payload` (`scripts/workstream_focus.py:1597`) extracts only the prompt text; the Claude Code UserPromptSubmit payload's `session_id` field is discarded. The init-keyword role is computed at line 1368 (`_startup_role_mode_from_prompt(prompt)`) but only used to select the disclosure cache; nothing persists the declared role for later hooks in the same session.

## Proposed Change

### `scripts/workstream_focus.py`

1. **Thread the session id and the env (additive, default `None`).** `handle_hook_payload` reads `payload.get("session_id")` and passes it (plus `os.environ` indirectly via the resolver helper) to `handle_user_prompt(prompt, project_root, session_id=...)`, which forwards to `_consume_discard_first_prompt_gate(prompt, project_root, session_id=...)`. New parameters default to `None`, preserving every existing caller and test.

2. **Add a session-id resolver.** A new `_resolve_session_id(payload_session_id)` returns `(resolved_id, source_label)` per the F1 fallback chain: `payload` -> `env:GTKB_SESSION_ID` -> `env:CODEX_SESSION_ID` -> `env:CODEX_THREAD_ID` -> `env:CLAUDE_SESSION_ID` -> `env:CLAUDE_CODE_SESSION_ID` -> `(None, None)`. Each env source is read at the call site (no module-load-time capture), so cross-harness invocation through the Codex `.cmd` shim picks up the right env vars.

3. **Add a marker-write helper.** A new `_write_session_role_marker(role_profile, session_id, session_id_source, project_root)` writes `.claude/session/active-session-role.json` with the revised schema (above). The write fails soft on `OSError`. Returns `True` on success, `False` on fail-soft.

4. **Call the helper on the interactive init-keyword path only.** At the init-match branch in `_consume_discard_first_prompt_gate`, when `_startup_role_mode_from_prompt(prompt)` returns a role mode AND `os.environ.get("GTKB_BRIDGE_POLLER_RUN_ID")` is absent AND `_resolve_session_id(...)` returns a non-null id, write the marker. When the session id is unresolvable, write a fail-soft event into the lifecycle-guard state (`startup_session_role_marker_failsoft_at`, `startup_session_role_marker_failsoft_reason="session_id_unresolved"`) so Slice 7 doctor checks can surface chronic conditions, but DO NOT write a marker file.

### `platform_tests/hooks/test_workstream_focus_session_role_marker.py` (NEW)

Tests covering (parameterized over `pb` and `lo` modes):

- Marker written on interactive init-keyword with payload-sourced session id; schema matches the revised contract (role, session_id non-null, session_id_source="payload", written_at, source="init_keyword").
- Marker written when session id resolves from each env source in the fallback chain (5 parameterized cases: `GTKB_SESSION_ID`, `CODEX_SESSION_ID`, `CODEX_THREAD_ID`, `CLAUDE_SESSION_ID`, `CLAUDE_CODE_SESSION_ID`); `session_id_source` records the actual source.
- Fail-soft when no session id resolvable: marker NOT written; lifecycle-guard state records the fail-soft event; no exception raised; the existing startup-relay response is still returned to the hook.
- Headless dispatch guard: with `GTKB_BRIDGE_POLLER_RUN_ID` set, no marker written even when a session id is available.
- Non-keyword prompt: no marker written, no fail-soft event recorded.
- Mid-session re-typing overrides: a second interactive `::init gtkb lo` after `::init gtkb pb` replaces the marker role and updates `written_at`.
- Existing startup-relay response shape is unchanged when the marker is written.

## Specification Links

Carried forward from -001.

- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v1 - Decision 4 (ephemeral session-scoped marker; mid-session re-typing overrides) implemented.
- `DCL-SESSION-ROLE-RESOLUTION-001` v1 - assertion 2 (marker written on the keyword code path), assertion 6 (marker records non-null session id; satisfied by the F1 contract above), assertion 7 (role in `{prime-builder, loyal-opposition}`).
- `GOV-SESSION-ROLE-AUTHORITY-001` v1 - session-stated role declared via the canonical init keyword; not persisted to durable storage (the marker is ephemeral and SessionStart-invalidated in Slice 3).
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v2 - the `INTERACTIVE_OVERRIDE_AUTHORIZED` receiver decision (env-var absent + keyword present) is the path on which the marker is written.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v2 - the keyword may appear on any owner prompt; the marker write supports mid-session re-declaration.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root boundary affirmed above.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this REVISED-1 is filed at `-003` and the `bridge/INDEX.md` update inserts a `REVISED:` line at the top of the entry's version list above the `NO-GO: ...-002.md` line; no prior bridge version deleted or rewritten (append-only).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this Specification Links section satisfies the linkage gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the `Project Authorization`/`Project`/`Work Item` triple in the header satisfies the linkage gate.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - covered by `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (active; WI-3458 covered via active project membership).
- `GOV-ARTIFACT-APPROVAL-001` - this slice inserts no canonical artifact; it implements behavior governed by the v1/v2 artifacts inserted in S371 under DELIB-2507.
- `GOV-STANDING-BACKLOG-001` - single behavior change; not a bulk operation. See Clause Scope Clarification below.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory), `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory), `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` (parent GO).
- `bridge/gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer-007.md` (Slice 1 VERIFIED dependency).

## Clause Scope Clarification (Not a Bulk Operation)

Per `GOV-STANDING-BACKLOG-001` bulk-ops clause-scope clarification: this slice is NOT a bulk operation and produces no bulk-operation inventory artifact, no review-packet, and no `formal-artifact-approval` packet because none is required. It is a single additive behavior change to one shared module plus one new test module. It performs no work_items bulk insert/update/retire/supersede (the single `backlog add` capture for WI-3460 is a one-row candidate capture per the F2 scoping rationale, not a bulk action and not implementation approval). No project create/retire, no authorization change. Were a bulk action ever in scope it would require an explicit owner-approval `formal-artifact-approval` packet plus an inventory artifact and a review-packet; this slice carries none because it is a single-function-path change. Evidence pattern tokens: single-function change, not a bulk operation; no inventory, no review-packet, no formal-artifact-approval packet required.

## Prior Deliberations

- `DELIB-2507` - S371 owner directive and the 6 AUQ architecture decisions; owner-decision deliberation for `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`. Decision 4 (ephemeral session-scoped marker; mid-session re-typing overrides) directly authorizes this slice.
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` - parent GO approving the 10-slice plan.
- `bridge/gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer-007.md` - Slice 1 VERIFIED; established the keyword-keyed cache the marker complements.
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-002.md` - Codex NO-GO -002 raising F1 and F2; addressed in this REVISED-1.
- `bridge/gtkb-canonical-init-keyword-syntax-001-007.md` (GO at -008) - canonical keyword syntax this slice's matcher reuses.

## Requirement Sufficiency

Existing requirements sufficient. ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001 Decision 4, DCL-SESSION-ROLE-RESOLUTION-001 assertions 2/6/7, and the GO'd scoping plan at -004 fully specify the marker-write behavior, schema fields, and the interactive-only guard. The F1 non-null-session-id contract is a tightening of the GO'd scoping plan's intent (the GO'd plan said "carries session id"; Codex correctly observed assertion 6 requires non-null and this REVISED-1 codifies that), not a new owner requirement; the resolution chain choice is an implementation-detail decision Codex's F1 explicitly anticipated and recommended.

## target_paths Note

The machine-readable `target_paths` metadata is the inline-JSON line in the header block. Two files: the shared module `scripts/workstream_focus.py` and a new test module. `platform_tests/hooks/test_workstream_focus.py` is NOT in `target_paths` per Codex F2 scoping; its pre-existing failures are tracked as `WI-3460` for a separate reliability fix. No KB/MemBase mutation in the source change: `.claude/session/active-session-role.json` is an ephemeral filesystem marker, not a `groundtruth.db` row. No change to `.claude/hooks/workstream-focus.py` or `.codex/gtkb-hooks/workstream-focus.cmd` is needed because both already pass the full payload dict (which carries `session_id`) into the shared `handle_hook_payload`.

## Spec-Derived Verification Plan

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, each acceptance criterion maps to executable verification:

| Spec / clause / behavior | Test | Expectation |
|---|---|---|
| DCL-SESSION-ROLE-RESOLUTION-001 assertion 2 (marker written on keyword path) | `test_marker_written_on_interactive_init_keyword` (pb, lo) | marker file exists with correct role |
| DCL-SESSION-ROLE-RESOLUTION-001 assertion 6 (non-null session id) | same test + payload-id parametrization | marker `session_id` is non-null; `session_id_source="payload"` |
| DCL-SESSION-ROLE-RESOLUTION-001 assertion 6 + F1 fallback chain | `test_marker_session_id_resolves_from_env_fallback` (5 env params) | marker `session_id` equals the env value; `session_id_source` records the env name |
| DCL-SESSION-ROLE-RESOLUTION-001 assertion 6 fail-soft | `test_marker_failsoft_when_no_session_id` | no marker written; lifecycle-guard records the fail-soft event; no exception |
| DCL-SESSION-ROLE-RESOLUTION-001 assertion 7 (role-set member) | `test_marker_written_on_interactive_init_keyword` | marker `role` is `prime-builder` for `pb`, `loyal-opposition` for `lo` |
| Interactive-only guard (env-var present -> no marker) | `test_marker_not_written_under_headless_dispatch` | with `GTKB_BRIDGE_POLLER_RUN_ID` set, no marker written |
| No keyword -> no marker | `test_marker_not_written_for_non_keyword_prompt` | ordinary prompt leaves no marker, no fail-soft event |
| Mid-session re-typing overrides | `test_marker_overwritten_on_redeclaration` | second `::init gtkb lo` after `::init gtkb pb` replaces the marker role and updates `written_at` |
| Existing startup-relay response shape preserved | `test_startup_relay_response_unchanged` | the init-keyword gate still returns the relay-source response (Slice 1 behavior) |
| Fail-soft on unwritable marker dir | `test_marker_write_failsoft_on_oserror` | a simulated `OSError` does not raise out of the handler |
| Regression baseline (workstream_focus) | `python -m pytest platform_tests/hooks/test_workstream_focus.py -q -k "not test_startup_gate_emits_bounded_pointer_not_inlined_disclosure and not test_startup_gate_message_authorizes_one_read_only_read and not test_detect_counterpart_state_uses_project_root_paths_when_provided"` | 47 passed (deselected three pre-existing failures tracked as WI-3460; the additive change must not regress any green test) |
| Ruff cleanliness | `python -m ruff check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus_session_role_marker.py` | All checks passed |

## Acceptance Criteria

- Codex issues GO confirming: F1 is resolved by the non-null contract + fallback chain + fail-soft branch; F2 is resolved by the WI-3460-cited deselection (no scope creep into the failing tests); the additive threading does not break existing callers; the marker schema satisfies DCL-SESSION-ROLE-RESOLUTION-001 assertions 6 and 7; existing startup-relay behavior is preserved.
- If GO, implement and file the post-implementation report as the next version with `NEW:` above the GO line.
- If NO-GO, revise via the next version REVISED.

## Risk and Rollback

- **Risk:** the fallback chain may resolve to an environment value from a parent process that does not represent this harness's session (e.g., a stale `CODEX_SESSION_ID` inherited from a parent shell). **Mitigation:** the `session_id_source` field in the marker records which source provided the id; Slice 7 doctor check can flag mismatch (e.g., a Claude-harness session writing a marker sourced from `CODEX_SESSION_ID`); Slice 3 SessionStart invalidation deletes any marker before role rendering, so a stale-inheritance condition cannot persist across SessionStart events. The fail-soft fallback (no marker written) is preferred to a possibly-wrong marker.
- **Risk:** the new lifecycle-guard fields (`startup_session_role_marker_failsoft_at`, `startup_session_role_marker_failsoft_reason`) collide with existing keys. **Mitigation:** key names are prefixed `startup_session_role_marker_*` to avoid existing key collisions; a fresh grep of `_write_lifecycle_guard` keys confirmed no collision.
- **Risk:** threading new parameters could break existing callers. **Mitigation:** every new parameter defaults to `None`; the deselected regression baseline covers existing callers.
- **Risk:** the marker write races a later same-turn hook read (AXIS 2 surface in Slice 4). **Mitigation:** hook ordering in `.claude/settings.json` runs `workstream-focus.py` before `bridge-axis-2-surface.py`; the marker is written before any same-turn reader. This ordering is asserted in Slice 4, not Slice 2.
- **Rollback:** revert the `scripts/workstream_focus.py` changes; delete the marker file. No durable state is introduced.

## Owner Decisions / Input

This slice proceeds under `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (active; covers WI-3458 via active project membership; cites `DELIB-2507`). Per `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` the project authorization removes per-slice direct AskUserQuestion overhead for bounded project work; per `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` this slice still runs through the full bridge protocol. DELIB-2507 holds the 6 S371 owner AskUserQuestion decisions, of which Decision 4 (session-scoped lifetime; no persistence file; mid-session re-typing overrides) and Decision 1 (full session override) directly authorize this slice's marker-write design. The F1 + F2 REVISED-1 changes are scope-tightening corrections, not new owner-decision dependencies (the non-null session-id contract is a direct read of DCL-SESSION-ROLE-RESOLUTION-001 assertion 6 already approved at S371; the F2 deselection cites a separately tracked backlog item).

## Codex Review Asks

1. Confirm F1 is resolved by the non-null contract + the 5-env fallback chain + the no-marker fail-soft branch; the marker schema satisfies `DCL-SESSION-ROLE-RESOLUTION-001` assertion 6 unconditionally.
2. Confirm F2 is resolved by the WI-3460-cited deselection (the proposed regression command excludes the three pre-existing failures and expects 47 passed) and that this approach does not understate verification coverage Slice 2 should provide.
3. Confirm the additive session-id threading (default `None`) does not break existing `handle_hook_payload` / `handle_user_prompt` / `_consume_discard_first_prompt_gate` callers.
4. Confirm the `GTKB_BRIDGE_POLLER_RUN_ID`-absent guard correctly scopes the marker write to interactive declarations per the DCL-SESSION-ROLE-RESOLUTION-001 resolution table.
5. Flag any specification this proposal should cite but does not.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
