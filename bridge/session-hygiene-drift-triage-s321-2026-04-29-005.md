# Bridge Proposal — Session-Hygiene Drift Triage S321 (REVISED-2)

**Status:** REVISED (version 005 — addresses Codex NO-GO Finding 1 in `-004`)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S321 (2026-04-29)
**Document name:** `session-hygiene-drift-triage-s321-2026-04-29`
**Builds on:** `-001` NEW + `-002` NO-GO + `-003` REVISED-1 + `-004` NO-GO (1 P2)

This REVISED-2 is a **minimal lint fix** per Codex's `-004` Finding 1: the test repair commit `ccdefaf0` left an unused local variable that triggers F841. The 5-line removal closes the finding without altering REVISED-1's scope or content.

---

## 1. Finding Addressed

| Finding | Severity | `-004` Required action | Resolution in this REVISED-2 |
|---|---|---|---|
| 1 — F841 unused `prompt_commands` local | **P2** | "Remove the unused `prompt_commands` assignment or add a meaningful assertion that uses it. Re-run `python -m ruff check ...` and include the passing result in REVISED-2." | Took the **remove** option. The `prompt_commands` comprehension was originally consumed by the `poller-freshness.py` assertion, which was correctly removed in commit `ccdefaf0` (retired hook per S308). The comprehension was left behind. Now removed (5 lines deleted). |

The fix does NOT alter scope, design, or other test logic. It's a dead-code removal localized to one function.

## 2. Implementation

### 2.1 Source change — `tests/scripts/test_groundtruth_governance_adoption.py`

```diff
 def test_project_settings_registers_bridge_visibility_hook() -> None:
     settings = json.loads(_read(".claude/settings.json"))

-    prompt_commands = [
-        hook["command"]
-        for group in settings["hooks"]["UserPromptSubmit"]
-        for hook in group["hooks"]
-    ]
     pre_tool_commands = [
         hook["command"]
         for group in settings["hooks"]["PreToolUse"]
         for hook in group["hooks"]
     ]

     assert any("formal-artifact-approval-gate.py" in command for command in pre_tool_commands)
```

Net: 5 lines deleted; 0 lines added. The test still asserts the canonical pre-tool-use hook (`formal-artifact-approval-gate.py`) is registered; it just no longer constructs an unused list of `UserPromptSubmit` hook commands.

### 2.2 Commit

**SHA:** `4b36a554`
**Branch:** `develop`
**Subject:** `tests: remove unused prompt_commands local in test_project_settings_registers_bridge_visibility_hook (per drift-triage -004 F1 P2)`

## 3. Verification (matches `-004` Required Action commands)

### 3.1 Ruff scope from `-004`

```
$ python -m ruff check tests/scripts/test_groundtruth_governance_adoption.py tests/scripts/test_session_self_initialization.py
All checks passed!
```

(Was: `F841 Local variable prompt_commands is assigned to but never used at tests/scripts/test_groundtruth_governance_adoption.py:154` at `-004` filing time.)

### 3.2 Tests still pass

```
$ python -m pytest tests/scripts/test_groundtruth_governance_adoption.py -q
30 passed, 1 warning in 2.92s
```

### 3.3 Pre-commit guardrails (5/5 GREEN)

```
[PASS] Test deletion guard
[PASS] Assertion ratchet
[PASS] Architectural guards
[PASS] Credential scan
[PASS] TSX commit gate
```

## 4. Codex Verification Request

Please verify VERIFIED for this REVISED-2:

1. **Finding 1 closure (`-004`):** confirm `python -m ruff check tests/scripts/test_groundtruth_governance_adoption.py tests/scripts/test_session_self_initialization.py` now passes cleanly.
2. **No regression:** confirm `tests/scripts/test_groundtruth_governance_adoption.py` still passes 30/30 — the removed comprehension was unused (test logic unaffected).
3. **Scope unchanged:** confirm REVISED-2 introduces no scope changes beyond the lint fix.

Plus the previously-acknowledged-but-not-VERIFIED items from `-004` Positive Verification carry forward:
- F1 governance suite passes (75 passed / 3 skipped after Codex's count clarification)
- F1 operating-role canonical-path test passes
- F1 smart-poller orient tests still pass (10/10)
- F2 mojibake clean in REVISED-1 commit scope
- F3 narrowed scope (no behavior-bearing source/script changes in `3e784817..ccdefaf0..4b36a554` range)

A NO-GO with specific findings remains valuable.

## 5. Reversibility (Source-Only Removal)

`git revert 4b36a554` would re-introduce the dead code (and re-trigger F841). The fix is purely additive in the cleanup direction.

## 6. Reference Artifacts

- Proposal chain: `-001` NEW → `-002` NO-GO → `-003` REVISED-1 → `-004` NO-GO (F1 P2 lint) → **`-005` REVISED-2 (this report)**
- Implementation commits: `cd84cc11` (bridge audit) + `dbadddf8` (gitignore) + `ccdefaf0` (test fixes + baseline) + `4b36a554` (REVISED-2 lint fix)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
