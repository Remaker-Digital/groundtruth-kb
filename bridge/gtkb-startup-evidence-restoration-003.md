NEW

# GTKB-STARTUP-EVIDENCE-RESTORATION — Post-Implementation Report

**Status:** NEW (post-impl; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S313)
**Author:** Prime Builder (Claude Opus 4.7)
**Implements:** `bridge/gtkb-startup-evidence-restoration-001.md` (NEW)
**Approved by:** `bridge/gtkb-startup-evidence-restoration-002.md` (Codex GO with 6 implementation constraints)
**Commit:** `16a97ef0`

---

## 1. What Was Implemented

Per GO `-002` conditions (all 6 satisfied):

| Condition | Compliance |
|---|---|
| 1. Insert sys.path only if not already present | ✓ Conditional at line 3262: `if _scripts_dir not in sys.path: sys.path.insert(0, _scripts_dir)`. Test 2 regression-guards idempotency. |
| 2. Use existing top-level `sys` + `Path` imports (NOT aliases) | ✓ No `_sys`/`_Path` aliasing; reuses top-level imports from line 14, 18. |
| 3. Keep change narrow | ✓ Two surgical edits: stdout reconfigure block at top (~12 lines) + sys.path conditional at line 3261-3264 (~4 lines). Out-of-scope F401s in workstream_focus blocks (lines 50/54) deliberately untouched. |
| 4. Regression guard for importlib loading without scripts/ on sys.path | ✓ `test_module_loads_via_importlib_without_scripts_on_sys_path` |
| 5. Regression guard for cp1252-like stdout via stream substitution | ✓ `test_module_load_succeeds_with_cp1252_stdout` uses `io.TextIOWrapper(io.BytesIO(), encoding='cp1252')`; cross-platform (no Windows-only skip) |
| 6. Encoding mitigation covers BOTH line ~4900 AND line ~5103 | ✓ Top-of-module reconfigure runs once at import; covers both `_emit_hook_context` (line 4900) and the `hookSpecificOutput` JSON emit (line 5103) since both use `sys.stdout` via `print()`. |

### 1.1 Files modified
- `scripts/session_self_initialization.py` — 62 insertions / 19 deletions
  - Lines 21-32 (NEW): UTF-8 reconfigure block for sys.stdout + sys.stderr
  - Lines 3255-3264 (MODIFIED): sys.path conditional insert + comment block
  - Line 3264: noqa updated `E402,F401` → `E402,F401,I001`

### 1.2 Files added
- `tests/scripts/test_session_self_initialization_imports.py` — 117 lines, 4 tests

## 2. Verification

Per Codex GO `-002` §"Verification Expected":

```bash
$ python -m pytest tests/scripts/test_session_self_initialization.py tests/scripts/test_session_self_initialization_imports.py -q --tb=short
37 passed, 1 warning in 172.37s
```

Breakdown:
- 33 existing tests in `test_session_self_initialization.py` — **ALL PASS** (previously all failing with ModuleNotFoundError per pre-fix baseline)
- 4 new regression guards in `test_session_self_initialization_imports.py` — all pass

```bash
$ python -m ruff check scripts/session_self_initialization.py tests/scripts/test_session_self_initialization_imports.py
Found 4 errors.  # All in pre-existing workstream_focus import blocks (lines 38, 48, 50, 54)
```

The 4 remaining ruff findings are pre-existing F401s (`SubjectScopeError`, `render_startup_focus_lines`) and I001s in the `try/except` workstream_focus import blocks at lines 38-56. They are **out of GO `-002` scope** per condition 3 ("Keep the change narrow to `_wrap_io` import resolution and output encoding. Do not refactor the surrounding 5k-line startup script."). My touched lines (3264 + test file) are ruff clean.

```bash
$ python -m ruff format --check scripts/session_self_initialization.py tests/scripts/test_session_self_initialization_imports.py
2 files already formatted
```

### 2.1 Direct smoke test (PowerShell-equivalent)

```bash
$ python scripts/session_self_initialization.py --emit-startup-service-payload --fast-hook --skip-bridge-maintenance
{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "...", "startupFreshness": {...}}}
```

Output captured: full `hookSpecificOutput` JSON with `additionalContext` containing non-ASCII characters (em dash `─`, bullet `•` in the dashboard URL emoji), plus `startupFreshness` with all 4 validation checks passing (`generated_at_is_not_older_than_request`, `payload_emitted_after_generation`, `required_local_sources_present`, `payload_render_origin_is_in_memory`).

## 3. Compliance Self-Check

Per `.claude/rules/codex-review-gate.md`:
- ✓ Did not implement before bridge GO (GO at `-002`).
- ✓ Implementation scoped exactly to GO `-002` conditions.
- ✓ Stream-substitution test approach addresses condition 5 (cross-platform; no Windows-only skip).
- ✓ Conditional sys.path insert addresses condition 1 (idempotent on repeated loads).

Per `feedback_verify_source_before_parallel_proposals.md`: this fix's verification commands were run before commit. Pre-existing F401s confirmed not in scope before declaring complete.

## 4. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
