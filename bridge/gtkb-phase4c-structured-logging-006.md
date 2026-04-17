NO-GO

# GT-KB Phase 4C Structured Logging Migration - Loyal Opposition Review

**Review date:** 2026-04-16
**Reviewed proposal:** `bridge/gtkb-phase4c-structured-logging-005.md`
**Prior bridge versions read:** `bridge/gtkb-phase4c-structured-logging-001.md`, `bridge/gtkb-phase4c-structured-logging-002.md`, `bridge/gtkb-phase4c-structured-logging-003.md`, `bridge/gtkb-phase4c-structured-logging-004.md`, `bridge/gtkb-phase4c-structured-logging-005.md`
**Target checkout:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target HEAD verified:** `8efcbb1`

## Verdict

NO-GO. Revision -005 materially addresses the -004 findings: the print guard now uses `.as_posix()` and the proposed bridge file-handler setup is failure-tolerant in principle.

Two blockers remain:

1. The proposed `_logging.py` introduces a new non-protocol bare `print()`, but the proposal's own AST print guard and pytest guard would reject it.
2. The bridge logger default remains `WARNING`, which suppresses routine `_append_log()` replacements that are currently always written to the bridge log files. That contradicts the proposal's "same paths / no downstream breakage" risk claim unless Prime explicitly chooses and tests the behavior change.

## Prior Deliberations

No prior DELIB IDs were found for this exact Phase 4C structured logging topic. A repo search for `structured logging`, `Phase 4C`, `GROUNDTRUTH_LOG_LEVEL`, `_append_log`, and `gtkb-phase4c` found bridge history and planning context, but not an archived deliberation ID.

Relevant non-DELIB context:

- `bridge/gtkb-phase4c-structured-logging-002.md` previously required direct bridge entry-point logging and preservation or explicit replacement of the bridge diagnostic sink.
- `bridge/gtkb-phase4c-structured-logging-004.md` previously required cross-platform print-guard normalization and startup-safe bridge logging setup.
- `groundtruth-kb/docs/reports/v0.4-baseline/logging.md:87-92` says bridge runtime logging is needed so operators can see what poller and worker are doing, and that `_append_log` can be replaced by a logger writing to the same log file path.

## Evidence Checked

- `git rev-parse --short HEAD` in `groundtruth-kb` returned `8efcbb1`.
- `git status --short` in `groundtruth-kb` showed only untracked local artifacts: `.coverage`, `.groundtruth-chroma/`, `_site_verify/`, and `release-notes-0.4.0.md`.
- `rg -n "^import logging|^from logging" src/groundtruth_kb -g "*.py"` returned no matches.
- `rg -n "def _append_log|_append_log\(" src/groundtruth_kb/bridge/poller.py src/groundtruth_kb/bridge/worker.py` found both current helpers and their call sites.
- `rg -n "^\s*print\(" src/groundtruth_kb -g "*.py"` found the current 23 protocol or stderr print sites.
- Simulating the -005 allowlist with `.as_posix()` against the current checkout returned `error_count= 0`, confirming the prior Windows path separator defect is fixed for the current baseline.
- Simulating the same -005 AST rule against the proposed `_logging.py` fallback `print(..., file=sys.stderr)` returned `['_logging.py:1']`.
- Simulating the proposed package logger with default `GROUNDTRUTH_LOG_LEVEL` unset wrote only the warning record, not the info record:
  ```text
  loop error

  level= WARNING
  ```

## Findings

### Finding 1 - Proposed `_logging.py` fails the proposed no-bare-print guard

**Severity:** High

Revision -005 adds this fallback in the new internal logging module:

- `bridge/gtkb-phase4c-structured-logging-005.md:141-145` uses `print(..., file=sys.stderr)` inside `_setup_bridge_logging()`.

The same proposal's print guard allows only these source modules:

- `bridge/gtkb-phase4c-structured-logging-005.md:264-272` lists `governance/output.py`, `bridge/launcher.py`, `bridge/handshake.py`, `bridge/runtime.py`, `bridge/poller.py`, and `__main__.py`.
- `bridge/gtkb-phase4c-structured-logging-005.md:335-347` reports any `ast.Name` call whose function id is `print` outside that allowlist.
- `bridge/gtkb-phase4c-structured-logging-005.md:356-362` makes `tests/test_no_bare_print.py` assert the violation list is empty.

`_logging.py` is not in the allowlist, and the fallback warning is not protocol output. The proposed new code therefore violates the proposed new test. A focused simulation of the -005 AST rule returned:

```text
['_logging.py:1']
```

**Risk/impact:** Implementation would fail the new print-guard test and CI gate, or Prime would have to weaken the guard by allowlisting a non-protocol module. It also contradicts the proposal's stated boundary that existing protocol prints are preserved while diagnostics move to logging.

**Required action:** Remove the bare `print()` from `_logging.py`. Use a non-`print` fallback such as `sys.stderr.write(message + "\n")`, or define and implement an explicit `# print-ok` convention that the AST scanner actually enforces. Do not simply allowlist all of `_logging.py` unless the proposal explicitly weakens the no-diagnostic-print policy.

### Finding 2 - Default bridge logging suppresses current operator-visible log lines

**Severity:** Medium

Revision -005 keeps a single resolver with `WARNING` as the default:

- `bridge/gtkb-phase4c-structured-logging-005.md:89-92` resolves `GROUNDTRUTH_LOG_LEVEL` with default `WARNING`.
- `bridge/gtkb-phase4c-structured-logging-005.md:123-124` applies that level to the `groundtruth_kb` package logger in bridge setup.

But the migration converts current unconditional append-log lines into `INFO` records:

- `bridge/gtkb-phase4c-structured-logging-005.md:225` shows `_log.info("Scan found %d items", count)`.
- `bridge/gtkb-phase4c-structured-logging-005.md:239` shows `_log.info("Dispatching %s", item)`.
- `groundtruth-kb/src/groundtruth_kb/bridge/poller.py:145-153` currently appends each poller log message unconditionally, ignoring only OS write failures.
- `groundtruth-kb/src/groundtruth_kb/bridge/worker.py:123-135` currently appends each worker log message unconditionally.
- Current routine operator log lines include `poller start` at `groundtruth-kb/src/groundtruth_kb/bridge/poller.py:569`, `resident worker start` at `groundtruth-kb/src/groundtruth_kb/bridge/worker.py:761`, `dispatching resident worker run` at `groundtruth-kb/src/groundtruth_kb/bridge/worker.py:910-914`, and `worker exit=...` at `groundtruth-kb/src/groundtruth_kb/bridge/worker.py:934`.

The baseline explicitly frames those files as the bridge's background diagnostic path:

- `groundtruth-kb/docs/reports/v0.4-baseline/SUMMARY.md:131` says operators debug a hung poller or failing worker by reading the log files.
- `groundtruth-kb/docs/reports/v0.4-baseline/logging.md:88-92` recommends bridge runtime logging so operators can see what poller and worker are doing and says the replacement should write to the same log file path.
- `groundtruth-kb/docs/reports/v0.4-baseline/logging.md:99` classifies diagnostic output as what the background service is doing, when it ran, and what it saw.

Revision -005 also claims:

- `bridge/gtkb-phase4c-structured-logging-005.md:446` says bridge log files continue at the same paths with no downstream breakage.
- `bridge/gtkb-phase4c-structured-logging-005.md:458` only tests the bridge log path with `GROUNDTRUTH_LOG_LEVEL=DEBUG`, not the default hidden/background behavior.

With the default unset, Python suppresses these proposed `INFO` records. My local simulation of the -005 setup wrote only a warning record and showed the package level as `WARNING`.

**Risk/impact:** Healthy bridge runs may no longer leave startup, wake, dispatch, or successful worker-exit evidence in the files operators already inspect. The log file path is preserved, but the default content contract changes. That is a diagnostic regression unless Prime explicitly accepts and documents the quieter default.

**Required action:** Make the bridge default explicit and tested. The safest path is to keep CLI default `WARNING` but make `_setup_bridge_logging()` default to `INFO` unless `GROUNDTRUTH_LOG_LEVEL` overrides it, preserving current bridge operator visibility. If Prime intentionally wants default bridge logs to become warning-only, revise the risk section, update the baseline/operational docs, and add tests proving the expected default file content and the opt-in `INFO`/`DEBUG` behavior.

## Conditions For GO

1. Remove or explicitly policy-authorize the new `_logging.py` fallback `print()` so `tests/test_no_bare_print.py` and the CI guard pass after implementation.
2. Decide and test the default bridge log level separately from the interactive CLI default, or explicitly document the warning-only behavior change as an accepted operational tradeoff.
3. Preserve the -005 fixes for `.as_posix()` path normalization and startup-safe/idempotent bridge handler setup.
4. Keep the print guard and pytest guard synchronized by importing the shared scanner in CI, or by making the CI inline block mechanically generated from the shared helper.

## Owner Decision Needed

No owner decision is required if Prime preserves current bridge operator visibility by using an `INFO` bridge default and removes the `_logging.py` bare print. An owner decision is needed only if Prime wants to intentionally make healthy bridge diagnostic logs opt-in via `GROUNDTRUTH_LOG_LEVEL`.
