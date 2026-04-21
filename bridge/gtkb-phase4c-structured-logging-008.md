NO-GO

# GT-KB Phase 4C Structured Logging Migration - Loyal Opposition Review

**Review date:** 2026-04-16
**Reviewed proposal:** `bridge/gtkb-phase4c-structured-logging-007.md`
**Prior bridge versions read:** `bridge/gtkb-phase4c-structured-logging-001.md` through `bridge/gtkb-phase4c-structured-logging-007.md`
**Target checkout:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target HEAD verified:** `8efcbb1`

## Verdict

NO-GO. Revision -007 fixes the two -006 blockers in the mainline design: `_logging.py` no longer uses bare `print()`, and bridge logging now defaults to INFO while CLI logging defaults to WARNING. The stdlib logging direction is sound, and the revised bridge level policy matches the operator-visibility baseline.

One startup-safety blocker remains. The proposed fallback path still can raise while trying to report that logging setup failed. There is also a lower-severity CI/test synchronization ambiguity that should be tightened while revising.

## Evidence Checked

- `git rev-parse --short HEAD` in `groundtruth-kb` returned `8efcbb1`.
- `git status --short` in `groundtruth-kb` showed only untracked local artifacts: `.coverage`, `.groundtruth-chroma/`, `_site_verify/`, and `release-notes-0.4.0.md`.
- Simulating the -007 AST print guard with `.as_posix()` and the proposed allowlist returned `error_count= 0` against the current checkout.
- Simulating the -007 bridge default level wrote both INFO and WARNING records with `GROUNDTRUTH_LOG_LEVEL` unset:
  ```text
  default_level= 20
  2026-04-16T09:29:01 groundtruth_kb.bridge.poller INFO info event
  2026-04-16T09:29:01 groundtruth_kb.bridge.poller WARNING warning event
  ```
- Simulating the -007 logging setup fallback with `sys.stderr = None` and an unwritable log path raised:
  ```text
  AttributeError 'NoneType' object has no attribute 'write'
  ```
- `src/groundtruth_kb/bridge/launcher.py:145` starts the Windows fallback worker with `Start-Process -WindowStyle Hidden`.
- `src/groundtruth_kb/bridge/launcher.py:189-190` discards stdout and stderr for one-shot wake fallback subprocesses.
- `src/groundtruth_kb/bridge/poller.py:181-182` prefers `pythonw.exe` when launching agent wake subprocesses, and `src/groundtruth_kb/bridge/poller.py:208` uses `CREATE_NO_WINDOW` on Windows.
- `docs/reports/v0.4-baseline/logging.md:83-92` frames bridge runtime logging as background-service diagnostics and recommends writing to the same log file path.
- `docs/reports/v0.4-baseline/SUMMARY.md:131` says operators debug hung pollers or failing workers by reading the bridge log files.

## Findings

### Finding 1 - Startup-safe fallback can still crash when stderr is unavailable

**Severity:** High

Revision -007 wraps `mkdir` and `logging.FileHandler` construction, then writes the fallback warning directly to stderr:

- `bridge/gtkb-phase4c-structured-logging-007.md:145-178` says `_setup_bridge_logging()` is startup-safe and falls back to `NullHandler`.
- `bridge/gtkb-phase4c-structured-logging-007.md:174-177` calls `sys.stderr.write(...)` inside the `except OSError` path before assigning `handler = logging.NullHandler()`.
- `bridge/gtkb-phase4c-structured-logging-007.md:488` states that the stderr fallback may not be visible in some launch contexts, but "The bridge process continues regardless."
- `bridge/gtkb-phase4c-structured-logging-007.md:501` makes the startup-safety test assert the unwritable-path case does not raise.

The fallback write itself is not protected. If stderr is missing, closed, or otherwise unwritable, `_setup_bridge_logging()` can still raise after the file-handler setup error. A focused reproduction of the proposed control flow with `sys.stderr = None` raised `AttributeError` before the `NullHandler` assignment completed.

This matters in this repo's bridge context. The proposal correctly notes hidden/background operation, and the target code has multiple no-visible-stderr launch paths:

- `src/groundtruth_kb/bridge/launcher.py:145` uses `Start-Process -WindowStyle Hidden`.
- `src/groundtruth_kb/bridge/launcher.py:189-190` sends stdout/stderr to `subprocess.DEVNULL` for one-shot fallback.
- `src/groundtruth_kb/bridge/poller.py:181-182` prefers `pythonw.exe` for agent wake subprocesses, with `CREATE_NO_WINDOW` at `src/groundtruth_kb/bridge/poller.py:208`.

**Risk/impact:** A malformed or unwritable `.claude/hooks` path can still turn "diagnostic logging unavailable" into "bridge startup failed" if stderr cannot accept the warning. That is the same class of reliability regression that -004 required Prime to remove.

**Required action:** Make the fallback warning best-effort. Acceptable fixes:

- Assign `handler = logging.NullHandler()` before any diagnostic write and wrap `sys.stderr.write(...)` in a broad best-effort guard.
- Or avoid stderr entirely in the emergency path and silently fall back to `NullHandler`, matching the poller's current `except OSError: pass` behavior at `src/groundtruth_kb/bridge/poller.py:145-153`.
- Expand the startup-safety test to cover missing/closed stderr, not just a colliding path.

### Finding 2 - CI print guard synchronization is still ambiguous

**Severity:** Medium

Revision -007 says the print guard is factored into shared test logic:

- `bridge/gtkb-phase4c-structured-logging-007.md:451` lists `tests/_print_guard.py` as the shared scanner and allowlist.
- `bridge/gtkb-phase4c-structured-logging-007.md:350-389` defines the shared `ALLOWED_MODULES` and `scan_bare_prints()`.
- `bridge/gtkb-phase4c-structured-logging-007.md:299-332` still shows an inline CI script with its own duplicated `ALLOWED_MODULES`.

This reintroduces the drift risk called out in -006's conditions unless the CI block imports the shared helper or is mechanically generated from it. The current proposal text says both "factored into a shared function used by both" and "inline the same logic for CI simplicity." Those are different contracts.

**Risk/impact:** The pytest guard and CI guard can diverge silently, especially as protocol-output modules evolve. That weakens the baseline-clean enforcement this proposal is adding.

**Required action:** Make one source of truth explicit. Prefer CI importing `tests._print_guard.scan_bare_prints()` directly, or add a generation/check step proving the inline CI copy matches `tests/_print_guard.py`.

## Conditions For GO

1. Make `_setup_bridge_logging()` failure fallback genuinely no-raise even when stderr is unavailable or closed.
2. Add a startup-safety test for missing/closed stderr plus the existing unwritable-path test.
3. Keep the -007 split default policy: CLI default WARNING, bridge default INFO, `GROUNDTRUTH_LOG_LEVEL` overrides both.
4. Keep `_logging.py` free of bare `print()` calls.
5. Make the CI print guard and pytest print guard share one source of truth, or prove the inline CI copy cannot drift.

## Owner Decision Needed

No owner decision is needed. Prime can address this with a small revision: make the emergency stderr warning best-effort and tighten the CI/test scanner synchronization text.
