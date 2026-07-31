NEW

# gtkb-wi5071-claude-hook-headless-parity — Route .claude/settings.json hooks headless (pythonw) so dispatched Claude workers stop spawning console windows

bridge_kind: prime_proposal
Document: gtkb-wi5071-claude-hook-headless-parity
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-07-09 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 054bb30f-56ef-436b-a5d6-ad07f7b29dd6
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive session; resolved_role=prime-builder (session-stated ::init gtkb pb)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5071

target_paths: [".claude/settings.json", "platform_tests/hooks/test_claude_settings_hook_no_window.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This is the primary window-stopper under `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` and WI-5071. Live evidence this session (owner reported windows on every dispatch of a Claude worker) pinned the dominant source: `.claude/settings.json` registers roughly twenty governance hooks, and every one launches its handler via bare `python` (e.g., `python "$CLAUDE_PROJECT_DIR/.claude/hooks/spec-before-code.py"`).

For an interactive Claude session the hook child inherits the operator's console, so no separate window appears. But a dispatched, headless Claude worker (spawned by the dispatcher through the no-window `run_with_status` wrapper) has NO console, so each bare-`python` hook child — fired on SessionStart, on every UserPromptSubmit, on every PreToolUse/PostToolUse — allocates a NEW visible console window. A single dispatched worker therefore pops dozens of consoles. This is the exact class `DELIB-20260702-AUQ-ADJACENT-CONSOLE-WINDOWS-HEADLESS-REQUIREMENT` flagged, and it is why `.codex/hooks.json` already routes its (identical) governance hooks through `pythonw.exe … run_py_no_window`, while `.claude` never received the same treatment.

Fix: bring `.claude/settings.json` to headless parity with `.codex` by launching each hook command through `pythonw` (the no-console Python interpreter) instead of `python`. This is transparent for the interactive session (hooks communicate over stdin/stdout pipes, not a console window; verified this session — `pythonw .claude/hooks/sot-read-discipline.py` on a sample PreToolUse payload returned the identical `{}` allow-decision with no window) and it eliminates the per-hook console for headless dispatched workers. It changes only the interpreter, not the hook logic, arguments, or ordering.

Reintroduction guard: add a test that fails if any `.claude/settings.json` hook `command` launches via bare `python` (must be `pythonw` or an approved no-window wrapper), so this regression cannot silently return. Because `platform_tests` runs in CI, this is self-enforcing without any local pre-commit hook or runtime window suppressor — honoring the owner constraint that nothing may block the owner's own manual window/GUI launches.

Out of scope (tracked separately): the Antigravity (harness C) dispatched-worker windows are a DIFFERENT source — Antigravity has no hooks and dispatches as the third-party `gemini` CLI (`.antigravity/config.toml`), whose own console/child handling is the `DELIB-20260707` "CLI child process handling" class. That requires separate investigation; harness C stays LO-non-dispatchable in the interim. This proposal fixes the Claude-worker half, which is GT-KB-owned and clean.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — reliability fast-lane; WI-5071's home and the authority for this bounded regression fix.
- `ADR-CROSS-HARNESS-PARITY-001` — this change brings the Claude hook-launch surface to no-window parity with the Codex hook-launch surface (`.codex/hooks.json` already uses `pythonw + run_py_no_window`).
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` — the SessionStart hook path; the change is interpreter-only and adds no measurable cost.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail and GO/NO-GO discipline governing this proposal and its verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every relevant governing spec.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project/PAUTH/WI linkage metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires spec-derived tests; the verification plan maps the fix to the parity test.
- `GOV-STANDING-BACKLOG-001` — MemBase work_items is the canonical backlog authority; WI-5071 is tracked there under PROJECT-GTKB-RELIABILITY-FIXES.

## Cross-Harness Disposition

This proposal touches a harness-surface file (`.claude/settings.json`), so per `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` (`ADR-CROSS-HARNESS-PARITY-001` Q8) the per-harness disposition is declared here. Disposition: **full behavioral parity; no waiver requested.**

- **Codex harness:** already headless — `.codex/hooks.json` launches its identical governance-hook set via `pythonw.exe .codex/gtkb-hooks/run_py_no_window …`. No change; this proposal brings Claude UP TO the existing Codex behavior.
- **Claude harness:** `.claude/settings.json` hook commands change from `python` to `pythonw` (no-console interpreter). Hook logic, arguments, stdin/stdout JSON contract, and ordering are unchanged; the interactive session is unaffected (verified) and dispatched headless workers stop popping per-hook consoles.
- **Antigravity harness:** has no hook event surface (`.antigravity/config.toml`: "Antigravity exposes no hook event surface … intentionally no hooks.json"), so this change does not apply to it; its dispatched-worker window source (the `gemini` CLI) is a separate concern tracked outside this proposal.
- **Parity enforcement:** the new test asserts the Claude hook-launch surface stays headless (no bare `python`), matching the Codex surface's existing `pythonw` discipline.

## Prior Deliberations

- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` — the governing owner directive ("no visible console windows… no exception"; 120-minute clean acceptance; dispatcher may remain quiesced during repair). WI-5071's `source_owner_directive`. This proposal removes the dominant Claude-worker window source that directive targets.
- `DELIB-20260702-AUQ-ADJACENT-CONSOLE-WINDOWS-HEADLESS-REQUIREMENT` — the owner directive that AUQ-adjacent / UserPromptSubmit hook children must be headless; explicitly names the `.cmd`/bare-`python` hook-child console-allocation class this proposal fixes for the Claude surface.
- `DELIB-20266297` (WI-4896 dispatcher console-window suppression) — made the daemon/stop-hook/bridge-launcher surfaces headless; the `.codex` hook surface got the `pythonw + run_py_no_window` treatment there. This proposal extends the same discipline to the Claude hook surface.
- `bridge/gtkb-wi5052-dispatcher-codex-no-window-containment-004.md` (WI-5052 VERIFIED) — the dispatcher_runtime Popen no-window containment; WI-5071's `related_bridge_thread`. Complementary: that made the worker LAUNCH headless; this makes the worker's own HOOK children headless.

## Owner Decisions / Input

This proposal depends on owner approval. Authorizing evidence (all this session, 2026-07-09, interactive Prime Builder, harness B):

- **Owner directive:** "I want the spawns to be stopped, at the source(s), without halting work. Find them all and fix them and find a way to stop them from being reintroduced. DO NOT block me from manually launching any window or GUI if I choose." Authorizes this source-level fix + reintroduction test and constrains the guard to exclude any local-blocking or global-suppressing mechanism. `detected_via: owner_directive`.
- **Owner AUQ (proceed):** "Windows are stopped… how do you want to proceed?" -> "Proceed now with the real fix." Authorizes filing and driving this primary Claude-hook parity fix. `detected_via: ask_user_question`.
- **Owner AUQ (scope):** the comprehensive no-window scope ("+ Consolidate inline helpers") was chosen earlier this session; this proposal is the re-prioritized primary slice of that program. `detected_via: ask_user_question`.
- **Standing directive:** `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` (owner_decision).

Project-scope owner-approval evidence is `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, which covers WI-5071 by active project membership. Implementation authority remains gated by Loyal Opposition GO plus the implementation-start authorization packet. Because automated bridge dispatch is quiesced during this repair (sanctioned by `DELIB-20260707`), the LO GO/VERIFIED for this thread are expected from an owner-engaged interactive Loyal Opposition counterpart (no dispatch, no windows), as with WI-5083 this session.

## Requirement Sufficiency

Existing requirements sufficient. This is a defect/regression fix under `GOV-RELIABILITY-FAST-LANE-001` (WI-5071) implementing the standing owner directives `DELIB-20260707` and `DELIB-20260702`. No new requirement is needed to authorize it.

## Spec-Derived Verification Plan

Interpreter: the project venv (`groundtruth-kb/.venv/Scripts/python.exe`).

Spec-to-test mapping:

- `DELIB-20260707` + `DELIB-20260702` + `ADR-CROSS-HARNESS-PARITY-001` (Claude hook children run headless) -> the new test `platform_tests/hooks/test_claude_settings_hook_no_window.py` parses `.claude/settings.json` and asserts every hook `command` launches via `pythonw` (or an approved no-window wrapper) and none via bare `python`. This both proves the fix and is the reintroduction guard.
- Interactive-session non-regression: a representative hook (`sot-read-discipline.py`) was run under `pythonw` on a sample PreToolUse payload this session and returned the identical `{}` allow-decision with no window and no error, matching `python` — evidence the interpreter change preserves the hook stdin/stdout JSON contract. The implementer confirms the `pythonw` interpreter resolution used in the hook command matches the `python` the hooks currently resolve to (venv parity), and re-runs a spanning sample of the hooks under the new command form.

Verification commands (run after implementation):

- pytest the new test (`platform_tests/hooks/test_claude_settings_hook_no_window.py`).
- ruff check and ruff format --check on the new test file (both separate gates).
- Confirm `.claude/settings.json` remains valid JSON and every hook command is well-formed.

Acceptance: the parity test passes; `.claude/settings.json` is valid and every hook launches headless; a spanning sample of hooks produces identical decisions under the new command form. The `DELIB-20260707` 120-consecutive-minute clean-interval soak is the owner-facing live acceptance after dispatch is re-enabled headless (post-implementation), not a per-slice unit test.

## Risk / Rollback

Blast radius: `.claude/settings.json` hook interpreter (this session's own governance-hook config) plus one new test. The change is interpreter-only (`python` -> `pythonw`); hook logic, arguments, stdin/stdout contract, and ordering are unchanged, and the `.codex` surface proves the identical hooks run correctly under `pythonw`. Because this edits the running session's hook config, the implementer verifies each changed command with a spanning sample BEFORE finalizing, and the change is low-risk to revert: restoring the `python` interpreter returns the prior behavior exactly (no data, no state). The reintroduction guard is a CI pytest — it never blocks the owner's local commits or manual window/GUI launches.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi5071-claude-hook-headless-parity`; append-only. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix: — repairs a reliability regression (dispatched Claude workers spawning visible console windows) and adds the test that prevents its recurrence.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
