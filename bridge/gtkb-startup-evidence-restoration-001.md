NEW

# GTKB-STARTUP-EVIDENCE-RESTORATION — `session_self_initialization.py` import resolution + UTF-8 hook output

**Status:** NEW (fix; awaits Codex GO)
**Date:** 2026-04-27 (S313)
**Author:** Prime Builder (Claude Opus 4.7)
**Triggered by:** Loyal Opposition findings (S313, owner-forwarded), P1 finding: "tests/scripts/test_session_self_initialization.py fails 33/33" + "Windows UnicodeEncodeError when emitting startup JSON".

bridge_kind: fix
work_item_ids: []
spec_ids: [GOV-SESSION-SELF-INITIALIZATION-001, PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001]
target_project: agent-red
implementation_scope: scripts/session_self_initialization.py — narrow surgical changes only

---

## Prior Deliberations

- `GOV-SESSION-SELF-INITIALIZATION-001`, `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` — establish the startup-disclosure contract this fix restores.
- `GTKB-GOV-011` (`memory/work_list.md`): the originating implementation of `session_self_initialization.py`.
- `GTKB-STARTUP-ENHANCEMENTS` P1 (S309 VERIFIED): the work that *extracted* `_atomic_write_text` to `scripts/_wrap_io.py` (commit `3caa034d` impl + `857ea71e` audit). The relocation introduced the bare `from _wrap_io` import that this fix corrects.

## 1. Scope

Narrow fix to `scripts/session_self_initialization.py` to restore startup evidence trustworthiness:

1. **Import resolution (P1, blocking):** make `from _wrap_io import _atomic_write_text` (line 3240) work under both direct script invocation AND test-loader (importlib) load.
2. **UTF-8 hook output (P1, latent):** ensure `print(json.dumps(..., ensure_ascii=False))` at line 4900 doesn't fail on Windows cp1252 stdout when the SessionStart hook runs without `PYTHONIOENCODING=utf-8`.

**Not in scope:** broader audit of `session_self_initialization.py` (5,355 lines), other startup scripts, dashboard renderer, history JSON contents.

## 2. Evidence

### 2.1 P1 import resolution — reproduced

```
$ python -m pytest tests/scripts/test_session_self_initialization.py::test_dashboard_and_report_are_written_with_time_series_kpi -q --tb=short
scripts\session_self_initialization.py:3240: in <module>
    from _wrap_io import _atomic_write_text  # noqa: E402,F401
E   ModuleNotFoundError: No module named '_wrap_io'
```

All 33 tests in `test_session_self_initialization.py` fail with the same `ModuleNotFoundError`. The test loader uses `importlib.util.spec_from_file_location()` (per `tests/scripts/test_session_self_initialization.py:19` `_load_module()`), which does not add the file's parent directory to `sys.path`. Direct script execution works because Python implicitly adds `sys.path[0] = scripts/` for direct script runs.

### 2.2 P1 UTF-8 hook output — latent

`scripts/session_self_initialization.py:4900` uses `ensure_ascii=False`:

```python
print(json.dumps({"additionalContext": text}, ensure_ascii=False))
```

On Windows with default cp1252 stdout (no `PYTHONIOENCODING=utf-8`), printing non-ASCII characters (em dashes `─`, bullet `★`, accented characters from user data) raises `UnicodeEncodeError`. This is the SessionStart hook output channel that Claude Code consumes as `additionalContext`. Failure here corrupts every fresh session's startup disclosure.

In my Bash shell `python scripts/session_self_initialization.py` ran without UnicodeEncodeError because the shell's `PYTHONIOENCODING` is UTF-8. The Codex run on a Windows powershell without that env var hit the failure. **The fix must NOT rely on environment-variable plumbing** — the script must self-correct stdout encoding at startup.

## 3. Proposed Change

### 3.1 Fix import resolution (line ~3236-3240)

**Before:**

```python
# Around line 3235-3240:
# _atomic_write_text relocated to scripts/_wrap_io.py per
# bridge/gtkb-startup-enhancements-p1-006.md (P1 VERIFIED 2026-04-25 S309).
from _wrap_io import _atomic_write_text  # noqa: E402,F401
```

**After:**

```python
# Around line 3235-3240:
# _atomic_write_text relocated to scripts/_wrap_io.py per
# bridge/gtkb-startup-enhancements-p1-006.md (P1 VERIFIED 2026-04-25 S309).
# sys.path manipulation here mirrors the established pattern in
# scripts/rehearse_isolation.py:26-27 — required so the test loader
# (importlib.util.spec_from_file_location) can resolve the bare
# `_wrap_io` module name. Direct script execution does not require
# this because Python implicitly adds sys.path[0] = scripts/.
import sys as _sys  # noqa: E402
from pathlib import Path as _Path  # noqa: E402
_sys.path.insert(0, str(_Path(__file__).resolve().parent))
from _wrap_io import _atomic_write_text  # noqa: E402,F401
```

The `_sys` and `_Path` aliases avoid colliding with any existing top-level `sys` / `Path` imports earlier in the file (line ~3240 is deep into the script, and naming collisions are documented codebase-wide failure modes).

### 3.2 Fix UTF-8 hook output (top of script, before any stdout writes)

Add stdout/stderr UTF-8 reconfiguration at the top of the script (after the docstring + standard imports), guarded by Python version + reconfiguration support:

```python
# At top of file, after standard imports, before any execution:
import sys as _sys_init
if hasattr(_sys_init.stdout, "reconfigure"):
    # Python 3.7+: reconfigure stdout/stderr to UTF-8 with replacement
    # for codepoints the legacy locale cannot encode. Prevents
    # UnicodeEncodeError on Windows cp1252 default during SessionStart
    # hook output. Mirrors the pattern in scripts/release_candidate_gate.py
    # if present, or established standalone.
    try:
        _sys_init.stdout.reconfigure(encoding="utf-8", errors="replace")
        _sys_init.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        # Best effort; if reconfigure fails (e.g., piped through a
        # non-text wrapper), fall through. The ensure_ascii=False
        # at line 4900 will then either succeed (UTF-8 sink) or fail
        # loudly, but at least we tried.
        pass
```

Alternative (smaller, less robust): change `ensure_ascii=False` to `ensure_ascii=True` at line 4900. Trade-off: hook output JSON has `\uXXXX` escapes for non-ASCII, slightly larger, but mechanically safe regardless of stdout encoding. **Recommended fallback if Codex prefers the smaller diff**, though it doesn't address other ascii-unsafe stdout writes that might exist elsewhere.

### 3.3 No other changes

- Do not refactor the import structure broadly.
- Do not change `_atomic_write_text` itself (it's already UTF-8 explicit at `_wrap_io.py:30`).
- Do not modify any non-startup script.

## 4. Test Plan

### 4.1 Reproduce-then-verify

Before-state baseline (already captured): `pytest tests/scripts/test_session_self_initialization.py -q` → **33 failed**.

Expected after-state: all 33 tests pass.

### 4.2 New regression guards

Add to `tests/scripts/test_session_self_initialization.py` (or a new test file `test_session_self_initialization_imports.py` to keep the existing test file intact):

| # | Test | Coverage |
|---|---|---|
| 1 | `test_module_loads_via_importlib_without_scripts_on_path` | Importlib load with empty sys.path entries succeeds (regression guard for P1 import resolution) |
| 2 | `test_module_loads_via_direct_python_invocation` | `python scripts/session_self_initialization.py --help` (or non-side-effecting flag) returns exit 0 |
| 3 | `test_stdout_is_reconfigured_to_utf_8_when_supported` | After module load, `sys.stdout.encoding.lower() == 'utf-8'` (or the reconfigure attempt was made) |
| 4 | `test_session_start_hook_output_succeeds_under_cp1252_stdout` | Set `sys.stdout` to a TextIO with `cp1252` encoding before module load; hook emit step does not raise UnicodeEncodeError |

Test 4 is the key Codex-finding regression guard. It must remain green even if a future change strips the §3.2 reconfigure block.

### 4.3 Acceptance gates

- All 33 existing tests in `test_session_self_initialization.py` pass.
- 4 new tests pass.
- `python -m ruff check scripts/session_self_initialization.py` clean (or no new findings).
- `python -m ruff format --check scripts/session_self_initialization.py` clean.
- Manual smoke: `python scripts/session_self_initialization.py` from `bash` and from `powershell` both run to completion.

## 5. Files Changed

### 5.1 MODIFIED
- `scripts/session_self_initialization.py` — two surgical edits per §3.1 + §3.2 (~15 lines added).
- `tests/scripts/test_session_self_initialization.py` (or new file) — 4 regression-guard tests added.

### 5.2 NEW
- `bridge/gtkb-startup-evidence-restoration-001.md` (this file).

### 5.3 UNTOUCHED
- `scripts/_wrap_io.py` (already UTF-8 correct).
- All other scripts.
- `_atomic_write_text` semantics.

## 6. Out of Scope

- Broader review of `session_self_initialization.py` (5,355 lines).
- Encoding audit of other scripts (e.g., `release_candidate_gate.py`, `migrate_root_to_gtkb.py`).
- Performance optimization of startup script.
- Test file refactor.
- Replacing the bare `from _wrap_io import` with `from scripts._wrap_io import` (would require turning `scripts/` into a package, broader change).

## 7. Codex Review Asks

1. Confirm the §3.1 sys.path insert pattern (matching `rehearse_isolation.py:26-27`) is the right convention for this project, vs. converting `scripts/` to a package + absolute imports.
2. Confirm the §3.2 `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` approach is preferred over the smaller fallback (change `ensure_ascii=False` to `ensure_ascii=True`).
3. Confirm Test 4 (cp1252 stdout regression guard) is the right shape — specifically, whether the test should be skip-on-non-Windows or run universally with a TextIOWrapper mock.
4. Confirm the `_sys` / `_Path` aliasing in §3.1 is necessary, or whether the file already imports `sys` + `Path` at top-level and the bare reuse is fine.
5. **GO / NO-GO** on this fix.

## 8. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
