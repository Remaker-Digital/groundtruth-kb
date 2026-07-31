NEW

# GT-KB Bridge Implementation Report - gtkb-wi5071-claude-hook-headless-parity - 003

bridge_kind: implementation_report
Document: gtkb-wi5071-claude-hook-headless-parity
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5071-claude-hook-headless-parity-002.md
Approved proposal: bridge/gtkb-wi5071-claude-hook-headless-parity-001.md

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: fea7dd14-2033-476e-8618-748d76c6fda2
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive session; resolved_role=prime-builder (session-stated ::init gtkb pb)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5071

Recommended commit type: fix:

## Implementation Claim

The dominant Claude-worker console-window source is fixed: every hook command in `.claude/settings.json` now launches through the no-console `pythonw` interpreter instead of bare `python`, bringing the Claude hook-launch surface to headless parity with the Codex surface (`.codex/hooks.json` already uses `pythonw`). The change is interpreter-only — hook logic, arguments, stdin/stdout JSON contract, ordering, and matchers are unchanged. All 46 registered hook commands (across PreToolUse, PostToolUse, SessionStart, Stop, UserPromptSubmit) were converted; 0 bare-`python` launches remain. A reintroduction-guard test was added so the regression cannot silently return.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`

## Owner Decisions / Input

- **Owner directive:** stop the console-window spawns at the source, guard against reintroduction, and never block manual window/GUI launches. Authorizes this source-level interpreter fix + CI-test guard. `detected_via: owner_directive`.
- **Owner AUQ (proceed):** "Proceed now with the real fix" -> authorizes driving this primary Claude-hook parity fix. `detected_via: ask_user_question`.
- **Owner AUQ (this session, 2026-07-09):** re-prioritized this WI-5071 A fix ahead of the cloud-harness slices to restore dispatch review throughput. `detected_via: ask_user_question`.

Project-scope owner-approval evidence is `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (covers WI-5071 by active project membership).

**Acceptance-criterion note (owner directive 2026-07-09):** the "120-consecutive-minute clean interval" text that appears in the approved proposal is NOT carried as an acceptance criterion here. Per the owner's live directive, a DELIB is historical/informational only and carries no requirements, acceptance criteria, or gates; the real acceptance for this slice is the deterministic evidence below. Whether visible windows are gone on dispatch is an operational observation for after dispatch is re-enabled, not a gate on this report's VERIFIED.

## Prior Deliberations

(Historical/informational context only — not requirement sources.)

- `bridge/gtkb-wi5071-claude-hook-headless-parity-001.md` - approved proposal.
- `bridge/gtkb-wi5071-claude-hook-headless-parity-002.md` - LO GO (Antigravity, session `6147bb18`).
- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS`, `DELIB-20260702-AUQ-ADJACENT-CONSOLE-WINDOWS-HEADLESS-REQUIREMENT` - the owner directives motivating headless hook children.
- `DELIB-20266297` (WI-4896) - the prior slice that gave the `.codex` hook surface its `pythonw` treatment; this brings `.claude` to parity.
- `bridge/gtkb-wi5052-dispatcher-codex-no-window-containment-004.md` (WI-5052 VERIFIED) - made the worker launch headless; this makes the worker's hook children headless.

## Specification-Derived Verification Plan

Interpreter: the project venv (`groundtruth-kb/.venv/Scripts/python.exe`).

| Linked spec | Derived evidence | Result |
|---|---|---|
| `DELIB-20260707` + `DELIB-20260702` + `ADR-CROSS-HARNESS-PARITY-001` (Claude hook children run headless) | the new `platform_tests/hooks/test_claude_settings_hook_no_window.py` parses `.claude/settings.json` and asserts every hook command launches via `pythonw` and none via bare `python` | **3 passed** (46 commands, 0 bare-python, 46 pythonw) |
| Interpreter parity (pythonw resolves to the same install as python) | `Get-Command python` -> `C:\Python314\python.exe`; `Get-Command pythonw` -> `C:\Python314\pythonw.exe` (same install; only the console subsystem differs) | **confirmed same install** |
| Non-regression of the hook decision contract | a spanning sample of hooks (`sot-read-discipline`, `kb-not-markdown`, `spec-before-code`, `credential-scan`) run under both `python` and `pythonw` with identical read-only payloads | **byte-identical stdout + returncode for all 4** |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` / code quality | `ruff check` AND `ruff format --check` on the new test file | **both pass** |
| JSON well-formedness | `.claude/settings.json` parses and every hook command is well-formed | **valid** |

## Commands Run

- `groundtruth-kb/.venv/Scripts/python.exe .gtkb-state/drivers/validate_claude_settings.py` (JSON valid; 46 commands; 0 bare-python; 46 pythonw)
- `Get-Command python` / `Get-Command pythonw` (interpreter parity)
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_claude_settings_hook_no_window.py -q --tb=short`
- `groundtruth-kb/.venv/Scripts/python.exe .gtkb-state/drivers/span_sample_hooks.py` (python-vs-pythonw identical-decision sample)
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check` / `ruff format --check` on the new test file

## Observed Results

- Guard test: **3 passed**.
- `.claude/settings.json`: JSON OK; 46 hook commands; **0 bare-python; 46 pythonw**.
- Interpreter parity: `python` and `pythonw` both resolve to `C:\Python314\` (same install).
- Spanning sample: **ALL_IDENTICAL: True** (4/4 hooks byte-identical stdout + returncode under `python` vs `pythonw`).
- ruff check: **All checks passed!**; ruff format --check: **1 file already formatted**.

## Files Changed

- `.claude/settings.json`
- `platform_tests/hooks/test_claude_settings_hook_no_window.py`

## Cross-Harness Disposition

Harness-surface file touched: `.claude/settings.json`. Disposition: **full behavioral parity; no waiver requested.**

- **Codex harness:** already headless (`.codex/hooks.json` launches its identical governance hooks via `pythonw`). No change; this brings Claude UP TO the existing Codex behavior.
- **Claude harness:** hook interpreter changes `python` -> `pythonw` (no-console). Logic, arguments, stdin/stdout contract, ordering unchanged; interactive session unaffected (verified — identical decisions); dispatched headless workers stop popping per-hook consoles.
- **Antigravity harness:** no hook event surface (`.antigravity/config.toml`); does not apply. Its dispatched-worker window source (the `gemini` CLI) is a separate concern (WI-5113).
- **Parity enforcement:** the new test asserts the Claude hook-launch surface stays headless, matching the Codex surface's `pythonw` discipline.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Justification: repairs a reliability regression (dispatched Claude workers spawning visible console windows) and adds the CI test that prevents its recurrence.

## Acceptance Criteria Status

- [x] Every `.claude/settings.json` hook command launches via `pythonw` (46/46); 0 bare-python.
- [x] `.claude/settings.json` remains valid JSON.
- [x] The reintroduction-guard test passes and fails on any bare-`python` reintroduction.
- [x] Interpreter parity confirmed: `pythonw` resolves to the same install as `python`.
- [x] Spanning sample: identical decisions under `python` vs `pythonw`.
- [x] `ruff check` and `ruff format --check` clean on the new test file.

## Risk And Rollback

Blast radius: `.claude/settings.json` hook interpreter (this session's own governance-hook config) + one new CI test. Interpreter-only change; the `.codex` surface already proves the identical hooks run correctly under `pythonw`, and the spanning sample confirms byte-identical decisions. The guard is a CI pytest — no local pre-commit hook, no runtime window suppression — so it never blocks the owner's local commits or manual window/GUI launches. Rollback: restore the `python` interpreter (returns prior behavior exactly; no data, no state).

## Loyal Opposition Asks

1. Confirm all 46 hook commands launch via `pythonw` and the guard test fails on any bare-`python` reintroduction.
2. Confirm the interpreter-parity evidence (same `C:\Python314` install) and the byte-identical spanning-sample decisions.
3. Return VERIFIED if satisfied, committing `.claude/settings.json` + the new test + the bridge chain; otherwise NO-GO with findings.
