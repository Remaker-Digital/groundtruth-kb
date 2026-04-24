NO-GO

# GTKB Session Overlay Baseline Implementation Review

**Status:** NO-GO
**Date:** 2026-04-23
**Reviewed report:** `bridge/gtkb-session-overlay-baseline-implementation-003.md`

## Verdict

NO-GO. The copy-only overlay library, policy checker, `.gitignore` coverage,
and focused tests are present, but the implementation is not yet
VERIFIED because the actual SessionStart execution path now crashes before the
startup payload can be emitted.

## What Verified Cleanly

- `scripts/gtkb_overlay.py` implements the approved first-slice boundaries:
  fixed allowlist, `authoritative: false`, copy-only overlay building, and
  no promotion/apply surface.
- `scripts/check_session_overlay_policy.py --json` exits `0` and reports
  `"pass": true` with the current tree.
- Focused verification passed:
  `python -m pytest tests/scripts/test_gtkb_overlay.py tests/scripts/test_release_candidate_gate.py::test_python_gate_runs_session_overlay_policy_before_pytest tests/scripts/test_session_self_initialization.py::test_startup_report_surfaces_session_overlay_status_as_non_authoritative -q --tb=short`
  -> `15 passed, 1 warning`.

## Blocking Findings

### 1. SessionStart startup path is broken by the new overlay import

The startup hook command executes `python "$CLAUDE_PROJECT_DIR/scripts/session_self_initialization.py" --emit-report --fast-hook`
from `.claude/settings.json:16-22`. In that direct-script mode,
`scripts/session_self_initialization.py:26-29` imports the overlay helper as:

- `from scripts import gtkb_overlay as _gtkb_overlay`
- fallback only on `ModuleNotFoundError`

That import form raises `ImportError`, not `ModuleNotFoundError`, in the live
hook execution path, so the fallback never runs. Reproduction:

```powershell
python scripts/session_self_initialization.py --emit-startup-service-payload
```

Result:

```text
ImportError: cannot import name 'gtkb_overlay' from 'scripts' (unknown location)
```

Impact:

- the requested startup visibility surface for session overlays is not actually
  available in the harness path that uses `session_self_initialization.py`
- the startup service is degraded exactly where the post-implementation report
  requests `VERIFIED`

Evidence:

- `.claude/settings.json:16-22`
- `scripts/session_self_initialization.py:26-29`
- direct command result above

### 2. Test coverage missed the real execution mode that failed

`tests/scripts/test_session_self_initialization.py:14-17` loads the script via
`importlib.util.spec_from_file_location(...)`, and the startup-service test at
`tests/scripts/test_session_self_initialization.py:730-744` calls
`module.main(...)` after import succeeds. That does not exercise the direct
`python scripts/session_self_initialization.py ...` top-level import path used
by the actual hook command, so the regression escaped despite the focused suite
passing.

Impact:

- the verification evidence in `-003.md` overstates readiness for the live
  startup path
- future startup regressions of the same class can slip through again unless a
  subprocess/direct-script test is added

Evidence:

- `tests/scripts/test_session_self_initialization.py:14-17`
- `tests/scripts/test_session_self_initialization.py:730-744`
- focused pytest command passes while the direct startup command fails

## Required Action Items

1. Fix the startup script import so direct script execution can load the
   overlay helper. Match the proven `workstream_focus` pattern or otherwise
   catch the actual direct-execution import failure mode.
2. Add a regression test that runs
   `python scripts/session_self_initialization.py --emit-report --fast-hook`
   or `--emit-startup-service-payload` in a subprocess and asserts exit `0`.
3. Re-run the focused verification from `-003.md`, plus the direct startup
   command, and post a revised bridge report with the updated evidence.

## Owner Decision Needed

None.
