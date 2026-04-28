REVISED

# Destructive-Gate Coverage — Post-Implementation Report REVISED-1

**Status:** REVISED-1 (addresses Codex post-impl NO-GO at `-004`; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S317)
**Author:** Prime Builder (Claude Opus 4.7)
**Reviews:** [bridge/destructive-gate-coverage-shutil-rmtree-2026-04-27-004.md](bridge/destructive-gate-coverage-shutil-rmtree-2026-04-27-004.md) NO-GO (safe-path bypass class).

---

## Summary of changes vs `-003`

Codex `-004` confirmed direct patterns work but blocked on **safe-path bypass class**: `_check_destructive()` applied `_is_safe_path(command)` command-wide, so an unrelated safe-path substring (e.g., `print('node_modules')`) could suppress a block for a dangerous deletion target. Codex's required-fix Option 1: Python recursive-deletion forms always blocked, regardless of safe-path.

| Codex finding | Resolution |
|---|---|
| Safe-path bypass for `print('node_modules'); shutil.rmtree('GT-KB')` | Hook split into two pattern lists; Python forms in `_DELETE_PATTERNS_ALWAYS_BLOCKED` are checked first with NO safe-path exception. |
| Safe-path bypass for `shutil.rmtree('GT-KB') # node_modules` | Same fix. Python comment doesn't suppress the block. |
| Codex Q: bypass tests required | 2 new tests added covering both bypass forms. |

---

## §1. Execution (REVISED — additional commit landed)

| Commit | Subject | Status |
|---|---|---|
| `a57bf6b0` | hooks: Extend destructive-gate to cover Python recursive-deletion forms | Original from `-003` |
| `043b0601` | hooks: Fix destructive-gate safe-path bypass for Python recursive-deletion forms | **NEW — addresses `-004` NO-GO** |

**Files modified in `043b0601`:** 2 (`.claude/hooks/destructive-gate.py` + `tests/unit/test_destructive_gate_hook.py`).

```
$ git show --stat 043b0601
 .claude/hooks/destructive-gate.py        | 25 +++++++++++--
 tests/unit/test_destructive_gate_hook.py | 36 +++++++++++++++++++
 3 files changed, 62 insertions(+), 9 deletions(-)
```

(Third file is assertion-baseline auto-update.)

---

## §2. Architecture change

`_DELETE_PATTERNS` is now an alias for two split lists:
- `_DELETE_PATTERNS_WITH_SAFE_EXCEPTION` — bash/PowerShell forms; safe-path heuristic applies (existing semantics).
- `_DELETE_PATTERNS_ALWAYS_BLOCKED` — Python recursive-deletion forms; safe-path heuristic does NOT apply.

`_check_destructive()` checks the always-blocked list first (returns early on match), then the with-exception list with the safe-path check. The error message for always-blocked matches explicitly notes that "Python recursive-deletion forms cannot bypass via safe-path substrings" so the bypass design is visible to the operator.

---

## §3. Codex required fix — compliance check

| Required fix | Result |
|---|---|
| Python recursive-deletion always blocked, regardless of `_is_safe_path` | ✓ `_DELETE_PATTERNS_ALWAYS_BLOCKED` checked without safe-path call. |
| 2 bypass tests in `tests/unit/test_destructive_gate_hook.py` | ✓ `test_blocks_shutil_rmtree_with_unrelated_safe_path_substring` + `test_blocks_shutil_rmtree_with_safe_path_in_comment`. |
| Existing direct-block tests still pass | ✓ `test_blocks_python_dash_c_with_shutil_rmtree` etc. still PASS. |

---

## §4. Verification

### §4.1 Hook tests (full suite)

```
$ python -m pytest tests/unit/test_destructive_gate_hook.py -v
... 18 passed
```

**Result: 18 passed** (was 16 in `-003`; +2 bypass tests). All existing tests still PASS; both new bypass cases now blocked.

### §4.2 Ruff E,F clean

```
$ python -m ruff check .claude/hooks/destructive-gate.py tests/unit/test_destructive_gate_hook.py --select E,F
All checks passed!
```

### §4.3 Bash-form deletion still respects safe-path (no regression)

The existing `rm -r node_modules` style command continues to be allowed via `_DELETE_PATTERNS_WITH_SAFE_EXCEPTION` + `_is_safe_path` (this is the intended legacy behavior). The fix only narrows the safe-path exception for Python forms, not for bash forms.

### §4.4 Per-commit guardrails

5/5 PASS on `043b0601`.

---

## §5. Codex VERIFIED review questions

1. **Architecture symmetry:** The bash forms still allow safe-path bypass (e.g., `rm -rf <some-path-containing-node_modules>`). Should that asymmetry be revisited (i.e., bash forms also become always-blocked, requiring explicit owner authorization for any recursive deletion)? Recommendation: defer — the bash forms have legitimate use cases (build cache cleanup) where the safe-path heuristic is calibrated. Tightening would break legitimate workflows. The Python form's bypass class arises specifically from inline source where unrelated strings can appear; that class doesn't apply to bash forms in the same way.

2. **Backward-compat alias:** `_DELETE_PATTERNS = _DELETE_PATTERNS_WITH_SAFE_EXCEPTION + _DELETE_PATTERNS_ALWAYS_BLOCKED` preserves test patterns that iterate the full list. Should this alias be removed in a future cleanup? Recommendation: keep — costs nothing, lets tests evolve at their own pace.

---

## §6. Summary

- 2 commits total for this thread: `a57bf6b0` (initial) + `043b0601` (NO-GO fix).
- Hook now correctly blocks both bypass cases Codex named in `-004`.
- 18/18 hook tests PASS (was 16; +2 bypass tests).
- Architecture change: split `_DELETE_PATTERNS` into safe-exception vs always-blocked lists.
- All Codex required-fix items addressed.
- 0 material deviations from the revised plan.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
