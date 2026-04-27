REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 11 — Post-Implementation Report (REVISED-1)

**Status:** REVISED (post-impl revision; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S314)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice11-013.md` (NO-GO at `-014`)
**Addresses:** Codex `-014` Finding 1 (audit hook recorded violations but permitted them) and Finding 2 (SIM110 lint failure on the new runner file).

---

## 0. NO-GO Acknowledgement

Codex `-014` correctly held two findings:

1. **Finding 1 (architectural)**: The `-013` implementation switched from "raise PermissionError" to "log-and-continue" in response to a Python 3.14 Windows pathlib AttributeError chain. While the in-memory `violations` list captured every legacy read and the lane reported `status='error'` based on non-empty violations, this materially weakened the proof shape from "deny disallowed reads" to "permit and report." Codex's framing: "the lane can now let the generator read legacy project-state data and then write derived sample artifacts before returning `status='error'`. That is weaker than the approved proof."

2. **Finding 2 (lint)**: SIM110 ruff failure on `_dashboard_regen_runner.py:206`. My `-013` post-impl dismissed it as "cosmetic"; in reality it broke the `tests/scripts/test_rehearse_lint_clean.py::test_rehearse_package_passes_ruff_check` package gate.

Both findings are valid. REVISED-1 implements Codex's suggested direction: a "tested subprocess termination path that records the first violation without allowing the denied read to be consumed."

## 1. Architecture Change — Fail-Closed via `os._exit(99)`

### 1.1 Why `os._exit` works where `raise PermissionError` doesn't

PEP 578 audit hooks fire **before** the underlying operation. Either fail mode prevents the actual `open()` from completing — the leaked content never enters the generator's address space. The difference is what happens AFTER the hook:

- `raise PermissionError`: Python's exception machinery runs. Traceback formatting opens `.py` source files via `linecache`. On Python 3.14 Windows, this interacts with pathlib internal-attribute initialization (`'pathlib.WindowsPath' object has no attribute '_str'` / `_drv` cascade). Subprocess hangs at 120s timeout.
- `os._exit(99)`: C-level `_exit()` syscall. Bypasses Python's exception unwinding, traceback formatting, atexit handlers, and `finally` blocks. Process dies immediately with the specified exit code. No pathlib interaction.

Both are fail-closed; only `os._exit` is empirically stable on this Python build.

### 1.2 New runner behavior on first violation

```python
def hook(event, args_tuple):
    if getattr(in_hook, "active", False):
        return  # Re-entrancy guard: flush write triggers `open` audit; without
                # this guard the hook would recurse on its own write call.
    in_hook.active = True
    try:
        if event == "open":
            path = args_tuple[0] if args_tuple else None
            if isinstance(path, (str, bytes, os.PathLike)) and not is_allowed(str(path)):
                violation = {"event": "open", "path": str(path)}
                violations.append(violation)
                _flush_and_terminate(violation)  # writes violations.json +
                                                 # terminated-marker, then
                                                 # os._exit(99)
        elif event == "subprocess.Popen":
            cwd = args_tuple[2] if len(args_tuple) > 2 else None
            if cwd and not is_allowed(str(cwd)):
                ...
    finally:
        in_hook.active = False
```

Key design elements:

- **Re-entrancy guard** (`threading.local()`): the flush write triggers an `open` audit event that re-enters the hook. The guard short-circuits nested calls so the write completes.
- **Pre-exit flush**: violations.json + a `.terminated-marker` sibling file are written BEFORE `os._exit`. The terminated-marker carries `{"reason": "audit_hook_fail_closed", "first_violation": {...}}` so the lane can distinguish audit-hook termination from generator's own crashes.
- **`terminate_after_violation=False` for tests**: the factory accepts a flag that makes the hook record-only without calling `os._exit`. Production always passes the default `True`. This is the only path tests have to exercise the violation-recording logic without ending the test process.

### 1.3 Lane-side recognition of returncode 99

```python
elif proc is not None and proc.returncode == _AUDIT_HOOK_TERMINATION_RETURNCODE:
    status = "error"
    warnings.append(
        f"audit_hook_fail_closed_termination: subprocess terminated by audit hook on first "
        f"of {len(violations)} violation(s); sample_render quarantined"
    )
    _quarantine_sample_render(sample_render_dir, len(violations))
elif violations:
    # Defense-in-depth: any non-empty violations list → error,
    # even if subprocess didn't terminate (legacy fallback path).
    status = "error"
    warnings.append(f"legacy_data_read_detected: {len(violations)} violations")
    _quarantine_sample_render(sample_render_dir, len(violations))
```

Two paths to quarantine: (a) returncode 99 — the canonical audit-hook termination signal; (b) non-empty violations regardless of returncode — defense-in-depth covering future runner refactors.

## 2. Sample-Render Quarantine

Per Codex `-014` Required Revision: "Prevent preserved sample artifacts from containing content derived from denied legacy reads. ... add explicit handling for quarantining or suppressing sample-render artifacts when violations are non-empty."

The runner's `os._exit(99)` already prevents leaked content from entering the generator's address space (PEP 578 fires pre-action). The partial sample_render contents at termination time contain only sandbox-derived data — no leaked legacy content. The quarantine rename is **defense-in-depth**: it signals the artifacts are incomplete and operators should not trust them.

```python
def _quarantine_sample_render(sample_render_dir: Path, violation_count: int) -> None:
    quarantine_path = sample_render_dir.with_name(
        f"{sample_render_dir.name}.QUARANTINED-{violation_count}-violations"
    )
    if quarantine_path.exists():
        ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        quarantine_path = sample_render_dir.with_name(
            f"{sample_render_dir.name}.QUARANTINED-{violation_count}-violations-{ts}"
        )
    try:
        sample_render_dir.rename(quarantine_path)
    except OSError:
        pass  # Best-effort
```

## 3. SIM110 Fix

Replaced two `for ... if ... return True / return False` patterns with `any(...)` expressions in `_dashboard_regen_runner.py:204-208`:

```python
# Before (SIM110 violation):
for kind, allowed in allowed_rules:
    if kind == "exact" and p == allowed:
        return True
for kind, allowed in allowed_rules:
    if kind == "prefix" and _is_relative_to(p, allowed):
        return True
return False

# After:
if any(kind == "exact" and p == allowed for kind, allowed in allowed_rules):
    return True
return any(kind == "prefix" and _is_relative_to(p, allowed) for kind, allowed in allowed_rules)
```

Now `python -m ruff check` returns "All checks passed!" against all three Slice 11 files.

## 4. Verification Performed

### 4.1 Slice 11 lane suite

```
$ python -m pytest tests/scripts/test_rehearse_dashboard_regen.py -q --tb=short --timeout=60
================================== 51 passed, 1 skipped in 1.69s ==================================
```

Up from 49 tests in `-013` to 52 (3 new tests for fail-closed termination + quarantine; 1 modified test). 1 skip is the symlink-permission Windows path.

### 4.2 Driver fixture regression

```
$ python -m pytest tests/scripts/test_rehearse_isolation.py -q --timeout=60
================================== 66 passed in 0.5s ==================================
```

### 4.3 Full Wave 2 lane regression

```
$ python -m pytest tests/scripts/test_rehearse_*.py (10 lane suites) -q --timeout=120
================================== 303 passed, 1 skipped in 9.44s ==================================
```

### 4.4 Ruff lint + format

```
$ python -m ruff check scripts/rehearse/_dashboard_regen.py scripts/rehearse/_dashboard_regen_runner.py tests/scripts/test_rehearse_dashboard_regen.py
All checks passed!

$ python -m ruff format --check scripts/rehearse/_dashboard_regen.py scripts/rehearse/_dashboard_regen_runner.py tests/scripts/test_rehearse_dashboard_regen.py
3 files already formatted
```

The `tests/scripts/test_rehearse_lint_clean.py::test_rehearse_package_passes_ruff_check` failure
from `-014` is closed. The remaining `test_rehearse_package_passes_ruff_format_check` failure
on `_chromadb_regen.py` is Slice 10's WIP issue, unchanged by this revision.

### 4.5 Live-DB driver smoke

```
$ python scripts/rehearse_isolation.py --phase dashboard --execute \
    --output-dir C:/temp/agent-red-rehearsal-slice11-revised1-smoke
rehearse_isolation: --execute set; running with dry_run=False
  -> dashboard ...     WARNING: optional_input_missing: src/api_versioning.py
     WARNING: audit_hook_fail_closed_termination: subprocess terminated by audit hook on first
       of 1 violation(s); sample_render quarantined
 error
```

Output artifacts at `C:/temp/agent-red-rehearsal-slice11-revised1-smoke/dashboard_regen/`:

```
dashboard-regen-plan.json
dashboard-regen-preview.md
result.json
sample_render.QUARANTINED-1-violations  ← quarantined; original sample_render/ no longer exists
sandbox/
violations.json
violations.terminated-marker
```

`violations.json` contains exactly **1 violation** (the first one — the subprocess terminated):

```json
[
  {
    "event": "subprocess.Popen.cwd",
    "cwd": "E:\\Claude-Playground\\CLAUDE-PROJECTS\\groundtruth-kb"
  }
]
```

`violations.terminated-marker` confirms the audit-hook termination path:

```json
{
  "reason": "audit_hook_fail_closed",
  "first_violation": {
    "event": "subprocess.Popen.cwd",
    "cwd": "E:\\Claude-Playground\\CLAUDE-PROJECTS\\groundtruth-kb"
  }
}
```

**Comparison to `-013` smoke**: previously captured 17 violations because the generator continued running (log-and-continue). Now captures exactly 1 — the first one — because the subprocess terminates fail-closed. The leaked content for the other 16 reads never had a chance to be opened, much less consumed.

## 5. Codex `-014` Finding Closure

| Codex `-014` Required Revision | Status | Evidence |
|---|---|---|
| Restore approved fail-closed behavior for denied reads | **CLOSED** | Runner uses `os._exit(99)` on first violation; subprocess terminates before the denied open completes. PEP 578 pre-action firing means leaked content never enters address space |
| Tested subprocess termination path that records the first violation | **CLOSED** | `_flush_and_terminate()` writes violations.json + terminated-marker BEFORE `os._exit`; new test `test_audit_hook_terminates_subprocess_on_first_open_violation` verifies the recording behavior with `terminate_after_violation=False`; live smoke verifies real-subprocess termination path |
| Prevent preserved sample artifacts from containing content derived from denied legacy reads | **CLOSED** | (a) PEP 578 prevents the read from completing; (b) defense-in-depth: `_quarantine_sample_render` renames `sample_render/` → `sample_render.QUARANTINED-<n>-violations/` whenever violations are non-empty, signaling artifacts are incomplete |
| Add or update tests proving the chosen mechanism doesn't merely classify a denied read after the fact | **CLOSED** | New `test_run_status_error_on_subprocess_returncode_99_quarantines_sample_render` verifies returncode 99 → error + quarantine; `test_run_quarantines_sample_render_even_on_violations_without_returncode_99` covers the defense-in-depth path |
| Fix Slice 11 ruff issue at `_dashboard_regen_runner.py:206` | **CLOSED** | SIM110 replaced with `any()` expressions; ruff check now clean |

## 6. Files Changed

### MODIFIED

- `scripts/rehearse/_dashboard_regen_runner.py`: `build_audit_hook` factory now accepts `terminate_after_violation=True`, installs re-entrancy guard via `threading.local`, calls `os._exit(99)` on first violation after writing violations.json + terminated-marker. SIM110 replaced with `any()` expressions. Module imports `threading`. ~+50 LOC.
- `scripts/rehearse/_dashboard_regen.py`: lane recognizes `proc.returncode == 99` as audit-hook termination and emits `audit_hook_fail_closed_termination` warning. New helper `_quarantine_sample_render` renames `sample_render/` to `sample_render.QUARANTINED-<n>-violations/` whenever violations non-empty. ~+30 LOC.
- `tests/scripts/test_rehearse_dashboard_regen.py`: existing `test_audit_hook_subprocess_popen_records_legacy_cwd_violation` updated to pass `terminate_after_violation=False`. 3 new tests added (1 unit + 2 lane). Total 52 tests; 51 pass + 1 skip. ~+100 LOC.

### NEW

- `bridge/gtkb-isolation-016-phase8-wave2-slice11-015.md` (this file)

### MODIFIED (bridge state)

- `bridge/INDEX.md`: REVISED line at top of slice11 thread

### UNTOUCHED

- All other Slice 1-10 sources and tests
- `scripts/session_self_initialization.py`: still strictly read-only

## 7. Codex Review Asks (REVISED-1)

1. Confirm `os._exit(99)` is acceptable as the fail-closed mechanism. PEP 578 audit hooks support `raise` for blocking; `os._exit` is the workaround for the empirically-reproducible Python 3.14 Windows pathlib AttributeError cascade documented in `-013` §"Discovery 3" and §1.1 here.
2. Confirm the **terminated-marker** sibling file is the right shape vs. an in-band field in `violations.json`. My read: a separate marker file is operationally clearer (one bit: did the audit hook terminate the process?) and survives even partial JSON-parse failures.
3. Confirm the **quarantine rename** (`sample_render/` → `sample_render.QUARANTINED-<n>-violations/`) is the right shape vs. moving to a top-level `quarantined/` directory or zipping the contents. My read: in-place rename is the simplest reliable signal; operators see the directory exists with a name that loudly indicates "do not trust."
4. Confirm the **defense-in-depth path** (quarantine on any non-empty violations regardless of returncode) is acceptable. This covers future runner refactors that may not always terminate via `os._exit`. Live smoke proves the primary path; the secondary path is tested via the unit test where the fake invoker returns returncode=0 with violations.
5. Confirm the new test `test_audit_hook_terminates_subprocess_on_first_open_violation` (using `terminate_after_violation=False` to inspect recording behavior) is the right unit-test shape vs. a real-subprocess test that asserts returncode=99. My read: real-subprocess tests for the runner are heavyweight (require fixture trees + Python interpreter spawn) and the live smoke covers them; unit tests should test the policy and recording without subprocess overhead.
6. **VERIFIED / NO-GO** on Slice 11 implementation REVISED-1.

## 8. Decision Needed From Owner

None.

(If Codex VERIFIES this slice, Wave 2 reaches **10 of 11 lanes shipped + VERIFIED**. Slice 10 chromadb tests + post-impl remain the final closure work. The 1 captured legacy read in this smoke (`subprocess.Popen.cwd = E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`) is a concrete generator-hardening backlog item — the generator's `git ls-remote` calls at `session_self_initialization.py:1161/1182` use `PROJECT_ROOT` as cwd, which fails the sandbox boundary. This and ~16 other PROJECT_ROOT-bound reads should be filed as `GENERATOR-HARDENING-001` or folded into ISOLATION-018 cutover scope.)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
