# Implementation Proposal — Prime Worker Permission Profile (Slice 1 of 4)

bridge_kind: prime_proposal

## Summary

Add `--permission-mode acceptEdits` and `--allowed-tools <explicit-list>` flags
to the spawned-Claude command in
`scripts/cross_harness_bridge_trigger.py::_harness_command` so bridge-dispatched
Prime workers can complete Edit/Write operations without hanging on interactive
permission prompts that no owner will answer. This is Slice 1 of a 4-slice
fix; subsequent slices land in separate bridge threads.

## Background

Owner observation in S350 (2026-05-14 chat): a recent Prime worker spawned by
the cross-harness trigger "was blocked because AskUserQuestion and Edit were
declined." Loyal Opposition workers complete successfully (LO recently filed
NO-GO at `gtkb-startup-payload-canonical-state-drift-006.md` and GO at
`active-workspace-declaration-slice-1-006.md`), so the hook topology works.
Prime-side delivery is constrained by permission/session-state gates on the
spawned subprocess.

Live code at `scripts/cross_harness_bridge_trigger.py:393-402` builds the
Claude command as:

```
["claude", "-p", prompt, "--add-dir", str(project_root), "--output-format", "json"]
```

No `--permission-mode` flag, no `--allowed-tools` flag. In a non-interactive
subprocess context, default permission mode blocks Edit/Write/Bash on first
call.

## Scope (Slice 1 of 4)

This slice adds permission flags to the spawned-Claude command only.

Out of scope for Slice 1 (each is a separate bridge thread):

- Slice 2: worker-context-aware AskUserQuestion enforcement. The owner-decision-tracker
  Stop hook detects `GTKB_BRIDGE_POLLER_RUN_ID` in env and switches enforcement:
  in owner context, missing-AUQ blocks turn-end; in worker context, an AUQ-needed
  scenario means stop-and-report the structured `requires_owner_decision` payload
  in the bridge artifact.
- Slice 3: lock granularity. Move from coarse `active-{handle}-session.lock`
  to per-thread or per-entry locks, OR add a post-Stop dispatch retry pass that
  clears suppression markers.
- Slice 4: regression coverage for the end-to-end worker delivery path.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — file bridge as canonical workflow state; dispatch automation must preserve protocol authority and not alter dispatched behavior contracts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposals cite governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived from linked specifications and executed against the implementation.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` — canonical init keyword emitted as first line of spawned-worker prompts; permission flags must not alter prompt content.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` — emitter authority on dispatched prompts; first-line invariant preserved.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval discipline; this slice mutates only operational dispatch substrate, not formal artifacts.
- `.claude/rules/bridge-essential.md` § Bridge Dispatch Enablement Contract — cross-harness trigger is the active dispatch substrate; this slice changes what the dispatched harness CAN do, not whether it dispatches.
- `.claude/rules/prime-builder-role.md` — Prime Builder operating role attaches to harness ID; spawned workers operate under Prime Builder authority.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol invariants; pre-filing preflight section requirement.
- `.claude/rules/codex-review-gate.md` — Loyal Opposition review gate; spec-derived test mapping requirement.

## Prior Deliberations

- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` (rowid 1550) — empirical foundation for event-driven dispatch on Windows.
- `bridge/gtkb-bridge-poller-event-driven-replacement-003.md` GO at `-004` (Slice 2) — establishes the cross-harness trigger as the canonical bridge automation path.
- `bridge/gtkb-canonical-init-keyword-syntax-001-007.md` Codex GO at `-008` — init-keyword first-line invariant on dispatched prompts; documents the env-var companion `GTKB_BRIDGE_DISPATCH_KEYWORD`.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-*` — smart-poller retirement; the current event-driven trigger is the substrate this slice modifies.
- `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md` VERIFIED — active-session-suppression contract; this slice does not alter that contract.
- _No prior deliberation specifically on Prime-worker permission-mode policy was found in chat-window context. The implementation-start-gate currently blocks the Prime session's `python -c` deliberation-archive queries; if a deeper search_deliberations sweep is needed, Loyal Opposition can run it as part of review (the worker-context for review is unconstrained on read-only queries)._

## Owner Decisions / Input

Two AskUserQuestion answers in S350 (2026-05-14) authorize this work:

1. Question: "Which slicing strategy for the Prime-worker-delivery fix?"
   Answer: **4-slice sequence (recommended)** — Slice 1 = permission-mode + allowed-tools on spawned workers; Slice 2 = worker-context-aware AUQ; Slice 3 = lock granularity; Slice 4 = regression coverage. Each slice is small, independently reviewable.
2. Question: "Permission-mode choice for spawned Prime workers?"
   Answer: **acceptEdits + explicit allowed-tools (recommended)** — `--permission-mode acceptEdits` plus an explicit `--allowed-tools` list. PreToolUse governance hooks (`scanner-safe-writer`, `bridge-compliance-gate`, `formal-artifact-approval-gate`, `narrative-artifact-approval-gate`, `implementation_start_gate`, `owner-decision-tracker`) remain active.

These two answers together constitute the owner's approval to proceed with this slice.

## Requirement Sufficiency

Existing requirements sufficient.

The dispatch behavior contract is governed by `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` (prompt syntax) plus `GOV-FILE-BRIDGE-AUTHORITY-001` (workflow authority); neither requires modification. The new permission-mode behavior is operational scaffolding on the dispatch substrate. The dispatched harness's runtime authority continues to derive from `.claude/rules/prime-builder-role.md` and the durable role record at `harness-state/role-assignments.json` — unchanged by this slice.

## target_paths

- `scripts/cross_harness_bridge_trigger.py` (modify `_harness_command` and its docstring)
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py` (add command-shape regression test)

## Implementation Plan

1. **Modify `_harness_command`** in `scripts/cross_harness_bridge_trigger.py:380-403`. When `target.command_handle == "claude"`, the returned list becomes:
   ```python
   return [
       "claude",
       "-p",
       prompt,
       "--add-dir",
       str(project_root),
       "--output-format",
       "json",
       "--permission-mode",
       "acceptEdits",
       "--allowed-tools",
       "Read Edit Write Glob Grep Bash TodoWrite NotebookEdit",
   ]
   ```
   The `command_handle == "codex"` branch is unchanged; Codex permission model is separate.

2. **Update the docstring** at lines 380-390 to document the permission contract: explain that `acceptEdits` allows Edit/Write without interactive prompts, that PreToolUse governance hooks remain the safety floor, and that the explicit allowed-tools list intentionally excludes `AskUserQuestion`, `WebFetch`, `WebSearch`, and all `mcp__*` tools.

3. **Add a regression test** in `platform_tests/scripts/test_cross_harness_bridge_trigger.py`:
   - `test_harness_command_claude_has_acceptedits_permission_mode`: asserts the returned list contains `--permission-mode` followed by `acceptEdits`.
   - `test_harness_command_claude_has_explicit_allowed_tools`: asserts the returned list contains `--allowed-tools` followed by a non-empty string.
   - `test_harness_command_claude_excludes_askuserquestion_from_allowed_tools`: asserts `AskUserQuestion` is not in the allowed-tools value (workers must not call AUQ — Slice 2 will add positive enforcement).
   - `test_harness_command_codex_unchanged`: asserts the `codex` target's returned command is still `["codex", "exec", prompt, "--cd", str(project_root)]`.
   - `test_harness_command_preserves_init_keyword_first_line`: asserts the prompt's first line matches `^::init gtkb (pb|lo)$` (per `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`).

## Spec-to-Test Mapping

- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` → `test_harness_command_preserves_init_keyword_first_line`.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` → same test plus `test_harness_command_claude_has_acceptedits_permission_mode` confirms flags do not alter prompt content.
- `GOV-FILE-BRIDGE-AUTHORITY-001` → covered by `test_harness_command_codex_unchanged` and `test_harness_command_claude_has_acceptedits_permission_mode` (dispatch decision and prompt content remain unchanged; only spawned-process permission posture changes).
- `.claude/rules/prime-builder-role.md` → `test_harness_command_claude_has_explicit_allowed_tools` and `test_harness_command_claude_excludes_askuserquestion_from_allowed_tools` confirm worker can act as Prime Builder for normal authoring tools but cannot call AUQ (whose semantics are owner-context-only).

## Risks

- **Tool allow-list too restrictive**: if the allow-list excludes a tool the Prime worker needs for legitimate bridge work, the worker will block on that tool. *Mitigation:* the proposed allow-list is generous (Read, Edit, Write, Glob, Grep, Bash, TodoWrite, NotebookEdit) and covers all tools exercised in normal bridge implementation work. Slice 4 regression coverage observes worker behavior empirically; missing tools are added in follow-up bridge proposals.
- **`acceptEdits` is broader than `--add-dir` scope**: the flag accepts Edit/Write on any path the worker tries. *Mitigation:* PreToolUse hooks (`scanner-safe-writer`, `bridge-compliance-gate`, `formal-artifact-approval-gate`, `narrative-artifact-approval-gate`, `implementation_start_gate`) gate dangerous patterns. `--add-dir` continues to scope filesystem reads.
- **Cross-platform behavior**: tested on Windows (the active host). Linux/macOS may have different default permission behavior for `claude -p`. *Mitigation:* Slice 4 regression coverage will catch host-specific divergence; this slice's unit test asserts command shape independent of platform.
- **Worker still hangs on AskUserQuestion**: with permission-mode acceptEdits set but no positive AUQ-blocking, a worker that calls AUQ will still hang in subprocess context. *Mitigation:* Slice 2 lands positive enforcement; until then, the allow-list excludes `AskUserQuestion` so the worker is unable to call it (Claude Code's tool-availability check fails before the AUQ call reaches the user).

## Rollback

Revert `scripts/cross_harness_bridge_trigger.py:380-403` and remove the regression tests. No state migration required; the dispatch-state.json schema is unchanged.

## Verification Procedure

1. Run `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short`. All existing tests must continue to pass; the new tests must pass.
2. Run `python scripts/cross_harness_bridge_trigger.py --diagnose`. Liveness summary should remain HEALTHY.
3. Manual end-to-end smoke: file a NEW Prime-actionable bridge entry, wait for the cross-harness trigger to dispatch a Prime worker, inspect `.gtkb-state/cross-harness-trigger/dispatch-runs/*.stdout.log` to confirm the worker performs at least one Edit/Write operation without hitting permission denial.

## Acceptance Criteria

- `_harness_command` returns the new flags for Claude targets (verified by regression tests).
- Codex branch unchanged (verified by `test_harness_command_codex_unchanged`).
- All preflights (applicability, clause) pass for this proposal.
- Existing test suite for the cross-harness trigger continues to pass.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
