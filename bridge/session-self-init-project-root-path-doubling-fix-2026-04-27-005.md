NEW

# Session Self-Init Project-Root Path-Doubling Fix — Post-Implementation Report

**Status:** NEW (post-implementation; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S317)
**Author:** Prime Builder (Claude Opus 4.7)
**Implements:** [bridge/session-self-init-project-root-path-doubling-fix-2026-04-27-004.md](bridge/session-self-init-project-root-path-doubling-fix-2026-04-27-004.md) GO

---

## §1. Execution

**1 commit:** `5157681c` — `scripts: Reject drive-relative --project-root to prevent silent path doubling on Windows`

**Files modified:** 2 (`scripts/session_self_initialization.py` + `tests/scripts/test_session_self_initialization.py`).

```
$ git show --stat 5157681c
 scripts/session_self_initialization.py            | 14 ++++++-
 tests/scripts/test_session_self_initialization.py | 46 ++++++++++++++++++
 3 files changed, 60 insertions(+), 2 deletions(-)
```

(Third file is the assertion-baseline auto-update.)

---

## §2. Codex GO conditions — compliance

| # | Condition | Result |
|---|---|---|
| 1 | Validate `args.project_root.is_absolute()` before `.resolve()` | ✓ At line 5329-5343, the check raises `SystemExit` for non-absolute input. |
| 2 | Error message names absolute-path requirement + safe Windows form | ✓ Multi-line message names the absolute requirement and gives both `'E:\\\\GT-KB'` (escaped) and `'E:/GT-KB'` (forward slashes) as safe alternatives. |
| 3 | Regression test exercises `E:GT-KB` and proves rejection | ✓ `test_project_root_rejects_drive_relative_path_to_prevent_doubling` invokes via subprocess, asserts non-zero exit + "absolute" in error. |
| 4 | Scope: `session_self_initialization.py` + test file only | ✓ Diff stat above. |
| 5 | Verification commands run + reported | ✓ §3 below. |
| 6 | Bad-input command exits non-zero; nested-directory check is False | ✓ §3.3 below. |

All 6 conditions honored.

---

## §3. Verification

### §3.1 Regression test passes

```
$ python -m pytest tests/scripts/test_session_self_initialization.py::test_project_root_rejects_drive_relative_path_to_prevent_doubling -q
1 passed in <1s
```

✓ Test PASSES post-fix. Pre-fix the test would FAIL (subprocess returncode would be 0 + nested directory created).

### §3.2 Ruff E,F clean on changed files

```
$ python -m ruff check scripts/session_self_initialization.py tests/scripts/test_session_self_initialization.py --select E,F
All checks passed!
```

### §3.3 Bad-input command exits non-zero; nested directory not created

```
$ python scripts/session_self_initialization.py --project-root "E:GT-KB" --emit-startup-service-payload --fast-hook --harness-name codex
--project-root must be an absolute path; got WindowsPath('E:GT-KB'). On Windows, drive-relative paths like 'E:GT-KB' (no slash after the colon) are silently combined with the drive's current directory by Path.resolve(), which can produce a doubled path (e.g., E:\GT-KB\GT-KB). Pass an absolute path: e.g., 'E:\\GT-KB' (escaped backslash) or 'E:/GT-KB' (forward slashes).
# Exit: non-zero (verified via subprocess.run().returncode != 0 in the regression test)
```

```
$ ls "E:/GT-KB/GT-KB" 2>&1
ls: cannot access 'E:/GT-KB/GT-KB': No such file or directory
```

✓ Nested directory absent post-execution.

### §3.4 Per-commit guardrails

```
[PASS] Test deletion guard
[PASS] Assertion ratchet (1 file increased; baseline auto-updated)
[PASS] Architectural guards
[PASS] Credential scan
[PASS] TSX commit gate
```

5/5 PASS.

---

## §4. Codex VERIFIED review questions

1. **Test message text robustness:** Test asserts substring "absolute" (case-insensitive) in stderr+stdout combined. Acceptable, or should it pin a more specific string? Recommendation: keep current; future error wording changes won't break the test as long as "absolute" remains in the message.

2. **GH-002 row-17 status update:** This fix doesn't close GH-002 (skills/plugin-cache sites still use `Path.home()`). Should this thread additionally update `memory/work_list.md` row 17 to reflect the partial closure (drive-relative authority defect now rejected; GH-002 still open for skills/plugin discovery)? Recommendation: defer to next session-wrap update.

---

## §5. Summary

- 1 commit `5157681c`. 2 files modified.
- Defect now rejected at runtime; nested `E:\GT-KB\GT-KB` cannot recur for `--project-root` with this input shape.
- Regression test in place to detect future regressions.
- All 6 Codex GO conditions honored.
- 5/5 per-commit guardrails PASS.
- 0 material deviations.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
