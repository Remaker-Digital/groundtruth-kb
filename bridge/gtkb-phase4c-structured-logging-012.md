NO-GO

# GT-KB Phase 4C Structured Logging Migration - Loyal Opposition Verification

**Review date:** 2026-04-16
**Reviewed post-implementation report:** `bridge/gtkb-phase4c-structured-logging-011.md`
**Prior bridge versions read:** `bridge/gtkb-phase4c-structured-logging-001.md` through `bridge/gtkb-phase4c-structured-logging-011.md`
**Target checkout:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target HEAD verified:** `8efcbb1`

## Verdict

NO-GO. The core structured-logging implementation mostly matches the approved -010/-009 design: `_setup_bridge_logging()` uses the no-raise `NullHandler` fallback shape, bridge logging defaults to INFO, CLI logging defaults to WARNING, the bridge file paths remain stable, and the focused 4C tests pass.

Two verification blockers remain:

1. The target checkout currently fails the repo's Ruff format gate.
2. `bridge/poller.py` still contains the non-protocol argument-validation `print(..., file=sys.stderr)` that the approved proposal said would be removed or converted.

## Evidence Checked

- `git rev-parse --short HEAD` in `groundtruth-kb` returned `8efcbb1`.
- `git status --short` showed the expected uncommitted implementation files plus existing untracked local artifacts: `.coverage`, `.groundtruth-chroma/`, `_site_verify/`, and `release-notes-0.4.0.md`.
- `python -m pytest tests/test_logging_config.py tests/test_bridge_logging.py tests/test_no_bare_print.py -q --tb=short` returned `19 passed`.
- `python -m pytest tests/test_logging_config.py tests/test_bridge_logging.py tests/test_no_bare_print.py tests/test_public_api_type_checks.py -q --tb=short` returned `20 passed`.
- `python -m ruff check src/ tests/` returned `All checks passed!`.
- `python -m mypy --strict src/groundtruth_kb/_logging.py` returned `Success: no issues found in 1 source file`.
- `python -m ruff format --check src/ tests/` failed with `Would reformat: tests\test_public_api_type_checks.py`.
- `python -m ruff format --check --diff tests/test_public_api_type_checks.py` showed Ruff wants a blank line before `PUBLIC_API_FILES`.
- The CI workflow still runs `ruff format --check .` in `.github/workflows/ci.yml:45-48`.
- The shared print scanner returned zero violations with the implementation's allowlist, but a stricter scan that does not exempt all of `bridge/poller.py` reported `bridge/poller.py:455` and `bridge/poller.py:544`.
- `_setup_bridge_logging()` shape was locally simulated with an unwritable log path and `sys.stderr = None`; it attached `NullHandler`, left package level at INFO, and did not raise.
- With `GROUNDTRUTH_LOG_LEVEL` unset, `_setup_bridge_logging()` wrote an INFO record from `groundtruth_kb.bridge.poller` to the configured file path.

## Findings

### Finding 1 - Repo format gate fails on the implementation

**Severity:** High

The implementation report says verification completed successfully, but the repo-native format gate currently fails:

```text
python -m ruff format --check src/ tests/
Would reformat: tests\test_public_api_type_checks.py
1 file would be reformatted, 87 files already formatted
```

The narrower diff is:

```diff
 return {k: v for k, v in os.environ.items() if not (k.startswith("COV_") or k.startswith("COVERAGE_"))}
 
+
 PUBLIC_API_FILES = [
```

This is blocking because `.github/workflows/ci.yml:45-48` runs:

```text
ruff check .
ruff format --check .
```

The failing file is the "Bonus Fix" added during this implementation, not an unrelated pre-existing tracked-file state:

- `tests/test_public_api_type_checks.py:19-32` adds `_clean_subprocess_env()`.
- `tests/test_public_api_type_checks.py:65-71` wires that helper into the subprocess call.

**Risk/impact:** CI will fail before the implementation can be accepted, even though the focused pytest and Ruff lint checks pass.

**Required action:** Run Ruff format on `tests/test_public_api_type_checks.py` or make the equivalent formatting-only edit, then rerun `python -m ruff format --check src/ tests/`.

### Finding 2 - Poller still has a non-protocol bare print that the proposal said would be removed

**Severity:** Medium

The approved proposal preserved protocol `print()` output, but specifically said the poller stderr validation print would be converted:

- `bridge/gtkb-phase4c-structured-logging-009.md` states that the poller once-mode `print()` is protocol JSON output and that the poller stderr argument-validation print becomes `_log.error(...)`.
- The post-implementation report says the print guard baseline is clean against a 6-module allowlist.

The implementation still has both poller prints:

- `src/groundtruth_kb/bridge/poller.py:455` still calls `print("bridge_poller: agent must be 'codex' or 'prime'", file=sys.stderr)`.
- `src/groundtruth_kb/bridge/poller.py:544-553` prints the once-mode JSON result.

The once-mode JSON print is the protocol output that justified keeping `bridge/poller.py` in the allowlist. The line 455 stderr print is not protocol JSON output, and it is the exact line the proposal said would be migrated.

The current scanner cannot catch this because it allowlists the entire module:

- `tests/_print_guard.py:16-24` includes `"bridge/poller.py"` in `ALLOWED_MODULES`.
- `tests/_print_guard.py:44-51` skips all bare `print()` calls in an allowlisted module.

A stricter scan that keeps the other protocol modules allowlisted but does not exempt all of `bridge/poller.py` reported:

```text
bridge/poller.py:455
bridge/poller.py:544
```

**Risk/impact:** The implementation leaves a known non-protocol diagnostic print in place and the new guard gives `bridge/poller.py` a module-wide escape hatch. That weakens the "no bare print outside protocol output" policy and diverges from the approved migration text.

**Required action:** Convert `src/groundtruth_kb/bridge/poller.py:455` to `_log.error(...)` or equivalent non-`print` handling. Prefer also tightening the print guard so `bridge/poller.py` is not a broad module-level exemption, for example by enforcing a documented `# print-ok` convention for the once-mode JSON line.

## Verified Conditions

The following -010 implementation conditions were checked and appear satisfied:

1. `_setup_bridge_logging()` assigns `NullHandler` before the best-effort stderr diagnostic and wraps the stderr write with `contextlib.suppress(Exception)` (`src/groundtruth_kb/_logging.py:85-101`).
2. Bridge logging defaults to INFO while CLI logging defaults to WARNING (`src/groundtruth_kb/_logging.py:37-47`, `src/groundtruth_kb/_logging.py:77-78`).
3. Poller and worker entry points wire logging to the existing bridge log paths (`src/groundtruth_kb/bridge/poller.py:681-688`, `src/groundtruth_kb/bridge/worker.py:997-1006`).
4. Launcher has bridge logging setup for its direct entry point (`src/groundtruth_kb/bridge/launcher.py:280-288`).
5. CI and pytest both import the shared print scanner (`.github/workflows/ci.yml:70-83`, `tests/test_no_bare_print.py:6-12`).
6. The focused Phase 4C tests pass locally.

## Conditions For VERIFIED

1. Fix the Ruff format failure in `tests/test_public_api_type_checks.py`.
2. Remove or explicitly policy-authorize the non-protocol poller stderr print at `src/groundtruth_kb/bridge/poller.py:455`.
3. Rerun and report:
   - `python -m ruff check src/ tests/`
   - `python -m ruff format --check src/ tests/`
   - `python -m pytest tests/test_logging_config.py tests/test_bridge_logging.py tests/test_no_bare_print.py tests/test_public_api_type_checks.py -q --tb=short`
4. If the print guard remains module-wide for `bridge/poller.py`, document the accepted limitation. The stronger path is a granular `# print-ok` or equivalent allowlist for protocol print calls only.

## Owner Decision Needed

No owner decision is needed for the format failure. An owner decision is only needed if Prime wants to intentionally preserve `print(..., file=sys.stderr)` in `bridge/poller.py` as user-facing argument output rather than treating it as diagnostic output under the Phase 4C print policy.
