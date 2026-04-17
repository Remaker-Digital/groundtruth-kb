NO-GO

# GT-KB Phase 4C Structured Logging Migration - Loyal Opposition Review

**Review date:** 2026-04-16
**Reviewed proposal:** `bridge/gtkb-phase4c-structured-logging-003.md`
**Prior bridge versions read:** `bridge/gtkb-phase4c-structured-logging-001.md`, `bridge/gtkb-phase4c-structured-logging-002.md`, `bridge/gtkb-phase4c-structured-logging-003.md`
**Target checkout:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target HEAD verified:** `8efcbb1`

## Verdict

NO-GO. Revision -003 materially addresses the prior -002 design blockers: it keeps bridge diagnostics on per-project log files, wires bridge direct entry points, corrects the scan-status boundary, and replaces the unsupported `gt project doctor` exit criterion.

Two release-blocking issues remain in the revised implementation plan:

1. The proposed AST print guard is not baseline-clean on Windows as written.
2. The proposed bridge logging setup can fail process startup before logging begins, and the risk mitigation stated in the proposal is technically inaccurate.

## Evidence Checked

- `git rev-parse --short HEAD` in `groundtruth-kb` returned `8efcbb1`.
- `git status --short` in `groundtruth-kb` showed only untracked local artifacts: `.coverage`, `.groundtruth-chroma/`, `_site_verify/`, and `release-notes-0.4.0.md`.
- `rg -n "^import logging|^from logging" src/groundtruth_kb -g "*.py"` returned `logging_import_matches=0`.
- `rg -n "^\s*print\(" src/groundtruth_kb -g "*.py"` returned `bare_print_matches=23`.
- `rg -n "def _append_log|_append_log\(" src/groundtruth_kb/bridge/poller.py src/groundtruth_kb/bridge/worker.py` returned `append_log_matches=36`.
- `docs/reports/v0.4-baseline/logging.md:78-109` confirms the Phase 4 logging target and the recommendation to keep bridge logging on the same log file path.
- `.github/workflows/ci.yml:130-158` confirms the repo already treats path separators as a cross-platform risk area, even though the full test suite currently runs on Ubuntu.

## Findings

### Finding 1 - Proposed AST print guard fails the current baseline on Windows

**Severity:** High

The revised proposal's CI guard uses forward-slash allowlist entries such as `bridge/launcher.py`, while its sample code computes module names with:

```python
rel = str(py.relative_to('src/groundtruth_kb'))
```

On this Windows workspace, that expression returns paths such as `bridge\launcher.py`, so the allowlist does not match. I simulated the revised guard with the proposal's protocol modules plus `bridge/poller.py` included in the allowlist, and it still reported all 23 current protocol prints as violations:

```text
error_count= 23
bridge\handshake.py:142
bridge\handshake.py:144
bridge\handshake.py:145
bridge\handshake.py:162
bridge\handshake.py:164
bridge\handshake.py:171
bridge\handshake.py:173
bridge\handshake.py:174
bridge\launcher.py:290
bridge\launcher.py:292
bridge\launcher.py:335
bridge\launcher.py:337
```

Running the same simulation with:

```python
rel = py.relative_to('src/groundtruth_kb').as_posix()
```

returned:

```text
error_count= 0
```

This is a proposal defect, not an implementation nit. The new `tests/test_no_bare_print.py` is intended to enforce the same policy as CI. If implemented exactly as proposed, it will fail a local Windows full-test run against the current baseline.

**Risk/impact:** The revised CI/test guard can block implementation on the owner's primary Windows environment and create a false regression signal for intentional protocol output. It also weakens trust in the print policy because the policy is not portable.

**Required action:** Normalize allowlist paths with `.as_posix()` or equivalent in both the CI script and pytest test. Keep the CI script and `tests/test_no_bare_print.py` identical or factored through a shared helper so the enforcement cannot drift. If `# print-ok` is retained as part of the proposal, the guard must actually parse/enforce that convention or the text should drop that claim.

### Finding 2 - Bridge logging setup can crash before startup, despite the stated mitigation

**Severity:** High

Revision -003 says the behavior change from `_append_log()` is low risk because "logging.FileHandler also handles file I/O; if the handler fails, logging swallows the error by default (`logging.raiseExceptions = False` in production)." That does not cover the setup code proposed in `_setup_bridge_logging()`.

The proposal performs these operations before the bridge process starts its work:

```python
log_path.parent.mkdir(parents=True, exist_ok=True)
handler = logging.FileHandler(log_path, encoding="utf-8")
```

Those setup failures are not swallowed by `logging.raiseExceptions`. A local reproduction with `logging.raiseExceptions = False` still raised during setup:

```text
FileExistsError [WinError 183] Cannot create a file when that file already exists: 'C:\Users\micha\AppData\Local\Temp\...\not_a_dir'
```

Current poller behavior is explicitly more tolerant: `src/groundtruth_kb/bridge/poller.py:145-153` wraps parent creation and append I/O in `except OSError: pass`. The proposal moves poller logging setup into `main()` before `run()` (`src/groundtruth_kb/bridge/poller.py:688-693` is the current direct entry point), so a log-path setup error can prevent the poller from reaching its actual bridge work.

This matters because the launcher starts bridge workers as hidden/background processes on Windows (`src/groundtruth_kb/bridge/launcher.py:145-148`). A startup crash in logging setup can remove the diagnostic channel and the service at the same time.

**Risk/impact:** A blocked, read-only, or malformed `.claude/hooks` path can turn "diagnostic logging unavailable" into "bridge process does not start." That is a reliability regression for the poller and any newly logged launcher path.

**Required action:** Revise `_setup_bridge_logging()` to be startup-safe. Acceptable options:

- Catch `OSError` around parent creation and `FileHandler` construction, then fall back to a `NullHandler`, stderr handler, or current poller-style silent behavior.
- Add a focused test that simulates a colliding/unwritable log path and proves the bridge entry point does not crash solely because diagnostics cannot be opened.
- Make handler attachment idempotent or explicitly clean handlers in tests, so repeated `_setup_bridge_logging()` calls do not leak file descriptors or duplicate records.

## Conditions For GO

1. Fix the AST print guard path normalization and prove it is baseline-clean on Windows and Ubuntu.
2. Keep `tests/test_no_bare_print.py` and the CI guard behavior synchronized.
3. Make bridge logging setup failure-tolerant, especially for `poller.main()` and `launcher.main()`.
4. Add tests for bridge log setup failure behavior and repeated setup behavior.
5. Preserve the -003 decisions that already addressed -002: same per-project bridge log files, direct entry-point setup for poller/worker/launcher, corrected scan-status scope, and direct bridge-entry smoke criteria.

## Owner Decision Needed

No owner decision is needed. Prime should revise the implementation plan to fix the portability and startup-safety defects before proceeding.
