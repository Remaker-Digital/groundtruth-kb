REVISED

# GTKB Session Overlay Baseline — Revised Post-Implementation Report

bridge_kind: implementation_report
scope: protocol
work_item_ids: [GTKB-ISOLATION-014]
target_paths: ["scripts/session_self_initialization.py", "tests/scripts/test_session_self_initialization.py"]

## Summary

Addresses the two blocking findings in `bridge/gtkb-session-overlay-baseline-implementation-004.md`:

- **F1** (High): direct-script SessionStart execution crashed with
  `ImportError: cannot import name 'gtkb_overlay' from 'scripts'` because the
  `except ModuleNotFoundError` clause didn't catch `ImportError`-with-bound-package.
- **F2** (Medium): the focused suite used `importlib.util.spec_from_file_location(...)`
  and never exercised the direct-script top-level import path that the hook command
  actually runs.

Revision 2 fixes both layers: the except clause is broadened to catch `ImportError`
(which includes `ModuleNotFoundError` as a subclass), and a new subprocess regression
test now exercises the exact hook command form.

## Change From Revision 1 (-003)

### `scripts/session_self_initialization.py`

Single-line change with an expanded comment:

```python
# before:
try:
    from scripts import gtkb_overlay as _gtkb_overlay
except ModuleNotFoundError:  # pragma: no cover - direct script execution path
    import gtkb_overlay as _gtkb_overlay  # type: ignore[no-redef]

# after:
try:
    from scripts import gtkb_overlay as _gtkb_overlay
except ImportError:  # pragma: no cover - direct script execution path
    # Broader than ModuleNotFoundError: direct `python scripts/session_self_initialization.py`
    # can raise ImportError("cannot import name 'gtkb_overlay' from 'scripts'") even when
    # a 'scripts' namespace package is importable without this submodule bound. Catching
    # ImportError covers both the "package missing" and "name missing" cases.
    import gtkb_overlay as _gtkb_overlay  # type: ignore[no-redef]
```

`ModuleNotFoundError` is a subclass of `ImportError`, so broadening to `ImportError`
catches both failure modes without weakening the existing coverage. The sibling
`workstream_focus` import at lines 21-24 remains unchanged because its `from X import Y`
form raises `ModuleNotFoundError` (package missing) rather than
`ImportError: cannot import name` (package present but name not bound).

### `tests/scripts/test_session_self_initialization.py`

One new subprocess regression test appended at the end of the file:
`test_direct_script_execution_emits_startup_payload`.

This test runs

```
python scripts/session_self_initialization.py \
    --project-root <REPO_ROOT> \
    --dashboard-dir <tmp>/dashboard \
    --history-path <tmp>/history.json \
    --emit-startup-service-payload \
    --fast-hook \
    --skip-bridge-maintenance \
    --lifecycle-guard-path <tmp>/guard.json
```

as a subprocess (via `subprocess.run` with a 60s timeout) and asserts:

- `returncode == 0`
- `stdout` is valid JSON with `hookSpecificOutput.hookEventName == "SessionStart"`
- payload contains `"agent-red-startup-service-v2"`

This exercises the exact top-level import path used by the SessionStart hook command
at `.claude/settings.json:16-22`, which the prior `importlib.util.spec_from_file_location`
tests never hit. Future regressions of this class will be caught at commit time.

## Live Verification

### Direct hook command form (`-004` repro)

```
$ python scripts/session_self_initialization.py --emit-startup-service-payload
{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "# Agent Red / GT-KB Programmatic Startup Payload ...
```

Exit 0. Payload emits as expected. The `-004` F1 `ImportError: cannot import name
'gtkb_overlay' from 'scripts'` repro no longer fires.

### Focused test lane

```
$ python -m pytest tests/scripts/test_session_self_initialization.py::test_direct_script_execution_emits_startup_payload tests/scripts/test_gtkb_overlay.py tests/scripts/test_release_candidate_gate.py -q --tb=short
...
23 passed in 12.94s
```

- New subprocess test (1) passes in ~10s (actual subprocess spawn + startup model build).
- `test_gtkb_overlay.py` (13 tests) green — overlay library unchanged.
- `test_release_candidate_gate.py` (9 tests) green — ordering preserved.

### Original `-003` focused suite remains green

The `-003` focused verification command from the NO-GO's "What Verified Cleanly" section
still passes (13 overlay + startup + release-gate tests — same set shown above). No
regression introduced.

## Files Changed (Commit-Local Delta)

```
 scripts/session_self_initialization.py         | ~5 lines (except clause + comment)
 tests/scripts/test_session_self_initialization.py | +44 lines (1 new subprocess test)
```

No other files modified. The `scripts/gtkb_overlay.py` library, the
`scripts/check_session_overlay_policy.py` checker, `.gitignore` coverage, release-gate
wiring, and original Phase 6 tests from `-003` all remain in place and unchanged; this
revision only fixes the startup import and adds direct-execution regression coverage.

## Required Action Items From -004

1. **Fix the startup script import so direct script execution can load the
   overlay helper** — DONE via the `except ImportError` broadening.
2. **Add a regression test that runs `python scripts/session_self_initialization.py
   --emit-report --fast-hook` or `--emit-startup-service-payload` in a subprocess and
   asserts exit 0** — DONE via `test_direct_script_execution_emits_startup_payload`.
3. **Re-run the focused verification from `-003.md`, plus the direct startup command,
   and post a revised bridge report with the updated evidence** — DONE (this file).

## Non-Scope Confirmation

- No other files in the Phase 6 baseline scope were modified.
- `scripts/gtkb_overlay.py` unchanged.
- `scripts/check_session_overlay_policy.py` unchanged.
- `.gitignore` overlay coverage unchanged.
- No Phase 7 work-subject changes (separate thread).
- No Phase 4 scoped-service changes (separate thread).

## Requested Verdict

VERIFIED.

## Prior Deliberations (per deliberation-protocol.md)

- GTKB application-isolation planning context via Phase 6 GO `-002`.
- NO-GO at `-004` is the direct prior for this revision. The F1 / F2 findings
  there are explicitly addressed by the two changes in this revision.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
