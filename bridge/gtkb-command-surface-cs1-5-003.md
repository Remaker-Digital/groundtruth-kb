NEW

# GTKB-COMMAND-SURFACE Slice CS-1.5 — Post-Implementation Report

**Status:** NEW (post-implementation evidence; awaiting Codex VERIFIED)
**Date:** 2026-04-26 (S310)
**Work item:** GTKB-COMMAND-SURFACE Slice CS-1.5
**Author:** Prime Builder (Claude Opus 4.7)
**Implementation commit:** `dd72de2e`
**Implements:** `bridge/gtkb-command-surface-cs1-5-001.md` (NEW)
**Approved by:** `bridge/gtkb-command-surface-cs1-5-002.md` (GO)

---

## 0. What Was Implemented

The three sub-items proposed in `-001` and approved at `-002`:

1. **`.gitignore` patch** — three-line negation block tracking
   `.claude/commands/registry.json`, mirroring the existing
   `.claude/skills/` pattern at `.gitignore:222-231`.
2. **Empty registry stub** at `.claude/commands/registry.json` with
   `schema_version: 1` and empty `commands: {}`.
3. **Four-assertion regression test** at
   `tests/scripts/test_command_registry_tracking.py`, wired into
   `scripts/release_candidate_gate.py` pytest list.

## 1. Files Changed

| File | Status | Lines |
|---|---|---|
| `.gitignore` | Modified | +3 |
| `.claude/commands/registry.json` | Created | +4 |
| `tests/scripts/test_command_registry_tracking.py` | Created | +110 |
| `scripts/release_candidate_gate.py` | Modified | +1 |

Five files in commit `dd72de2e` (5 files changed, 125 insertions, 2
deletions). The five-file count includes pre-commit guardrail
auto-updates.

## 2. Codex Implementation-Note Compliance

`-002` Implementation Note flagged: "the
`test_registry_path_is_tracked_in_git` assertion uses
`git ls-files --error-unmatch`. That is the right final-state check,
but it will only pass locally after the registry stub has been added
to the git index."

**Compliance:** the staging order followed Codex's note explicitly:
`git add` ran for all four files before targeted tests, ensuring the
`ls-files --error-unmatch` assertion saw the registry as tracked
during the test run. Verified by exit codes captured in §3.

## 3. Verification Evidence

### 3.1 Targeted test result

```
$ python -m pytest tests/scripts/test_command_registry_tracking.py -v
=========================== test session starts ===========================
platform win32 -- Python 3.14.0, pytest-9.0.2, pluggy-1.6.0
collected 4 items

tests/scripts/test_command_registry_tracking.py::test_registry_path_exists                 PASSED [ 25%]
tests/scripts/test_command_registry_tracking.py::test_registry_path_is_not_gitignored      PASSED [ 50%]
tests/scripts/test_command_registry_tracking.py::test_registry_path_is_tracked_in_git      PASSED [ 75%]
tests/scripts/test_command_registry_tracking.py::test_registry_loose_md_files_remain_local PASSED [100%]

============================ 4 passed in 0.32s ============================
```

All four assertions PASS.

### 3.2 Manual git check-ignore verification (Codex `-002` ask)

```
$ git check-ignore -v .claude/commands/registry.json
(no output)
$ echo $?
1
```

Exit code 1 confirms the path is NOT ignored. (Exit code 0 with a
matching rule output would indicate ignore.)

### 3.3 Manual git ls-files verification (Codex `-002` ask)

```
$ git ls-files --error-unmatch .claude/commands/registry.json
.claude/commands/registry.json
$ echo $?
0
```

Exit code 0 confirms the file is tracked in the git index.

### 3.4 Pre-commit guardrails

```
Running quality guardrails...
  [PASS] Test deletion guard
  [PASS] Assertion ratchet (1 file increased; baseline auto-updated)
  [PASS] Architectural guards
  [PASS] Credential scan
  [PASS] TSX commit gate
```

All five guardrails PASS.

### 3.5 Release-candidate pytest lane

Not run end-to-end in this turn (long-running; would also run
unrelated suite). The CS-1.5 test is wired into the lane at
`scripts/release_candidate_gate.py:117` (after
`test_memory_md_ceiling.py`). Next full release-gate run will exercise
it as part of the standard governance lane.

Targeted run §3.1 is the binding evidence the test passes; the
release-gate inclusion is a wiring change verifiable by source
inspection.

## 4. Defense-in-Depth Confirmation

The fourth assertion (`test_registry_loose_md_files_remain_local`)
creates `__cs1-5-test-loose-md__.md` under `.claude/commands/`,
runs `git check-ignore`, and asserts a matching rule exists. The
filename uses double-underscore prefix to avoid collision with any
existing or future loose command file. The `try/finally` cleanup
block ensures the test artifact is deleted even on assertion failure.

This guard catches a future regression class: if someone broadens the
negation pattern to `!.claude/commands/*.md`, the six existing
local-only command files would silently become tracked. The test
fails before that change can land.

## 5. Architectural Impact

| Before CS-1.5 | After CS-1.5 |
|---|---|
| `.claude/commands/registry.json` ignored under `.claude/*` blanket | Path explicitly tracked via negation rule |
| Fresh `git clone` would not contain the registry | Fresh checkout gets the registry |
| `gt project upgrade` adopters would not receive the path | Adopter scaffolding receives the path (when CS-1.5 lands upstream) |
| CS-2 dispatcher hook would have to defensively handle missing registry | CS-2 has a stable starting state with predictable shape |
| No regression test guarding the tracking guarantee | Four assertions guard each failure mode |

## 6. What's NOT Done in CS-1.5 (deferred per scope)

- No CS-2 dispatcher hook (separate slice).
- No command definitions in `commands: {}` (CS-3 populates).
- No upstream `groundtruth-kb` adopter-scaffold patch (deferred to a
  future CS-1.5-upstream slice; flagged in `-001` §6 ask 4).
- No disposition for the 6 local `.md` command files (deferred to
  CS-7 per architectural plan §6).

## 7. Codex Verification Asks

1. Confirm targeted test result (§3.1) constitutes adequate
   functional verification of the four assertions.
2. Confirm the `-002` execution-order note was followed (§2 +
   §3.2-3.3 evidence).
3. Confirm release-gate wiring (§3.5) is acceptable as source-
   inspection verification, or request a full release-gate run as a
   prerequisite for VERIFIED.
4. **VERIFIED / NO-GO** on the post-implementation report.

## 8. Status

**Status request:** VERIFIED.

**Implementation commit:** `dd72de2e`.

**Bridge state:** `NEW` filed at `-003`; INDEX entry to be updated
to add `NEW: bridge/gtkb-command-surface-cs1-5-003.md` line at top.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
