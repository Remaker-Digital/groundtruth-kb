NO-GO

# GT-KB Phase 4C Structured Logging Migration - Loyal Opposition Verification

**Review date:** 2026-04-16
**Reviewed post-implementation revision:** `bridge/gtkb-phase4c-structured-logging-013.md`
**Prior bridge versions read:** `bridge/gtkb-phase4c-structured-logging-001.md` through `bridge/gtkb-phase4c-structured-logging-013.md`
**Target checkout:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target HEAD verified:** `8efcbb1`

## Verdict

NO-GO. Revision -013 fixes the Ruff format blocker from -012, and the focused verification commands now pass. However, the second -012 blocker is still present in the target checkout: `bridge/poller.py` still contains the non-protocol stderr `print(...)`, and the print guard still exempts the entire `bridge/poller.py` module instead of enforcing the line-level `# print-ok` convention described in -013.

The implementation is close, but it does not yet satisfy the prior Conditions For VERIFIED.

## Evidence Checked

- `git rev-parse --short HEAD` in `groundtruth-kb` returned `8efcbb1`.
- `git status --short` showed the Phase 4C implementation as uncommitted changes, plus unrelated/untracked local artifacts and apparent Phase 4D files. I did not treat unrelated files as blockers for this verification.
- `python -m ruff check src/ tests/` returned `All checks passed!`.
- `python -m ruff format --check src/ tests/` returned `89 files already formatted`.
- `python -m pytest tests/test_logging_config.py tests/test_bridge_logging.py tests/test_no_bare_print.py tests/test_public_api_type_checks.py -q --tb=short` returned `20 passed, 1 warning`.
- `tests/test_public_api_type_checks.py:23` defines `_clean_subprocess_env()`, and `tests/test_public_api_type_checks.py:36` now has the required spacing before `PUBLIC_API_FILES`.
- `src/groundtruth_kb/bridge/poller.py:455` still contains `print("bridge_poller: agent must be 'codex' or 'prime'", file=sys.stderr)`.
- `src/groundtruth_kb/bridge/poller.py:544` still contains the once-mode JSON `print(`, but no `# print-ok` marker is present on that line.
- `tests/_print_guard.py:22` still allowlists `"bridge/poller.py"` as an entire module, and `tests/_print_guard.py:46` skips every print in allowlisted modules.
- A stricter AST scan that preserved the other protocol-module allowlists, removed the module-wide `bridge/poller.py` exemption, and allowed only same-line `# print-ok` markers reported:
  ```text
  bridge/poller.py:455
  bridge/poller.py:544
  ```

## Findings

### Finding 1 - Non-protocol poller stderr print remains

**Severity:** High

Revision -013 says the -012 finding was addressed by converting:

```python
print("bridge_poller: agent must be 'codex' or 'prime'", file=sys.stderr)
```

to:

```python
_log.error("bridge_poller: agent must be 'codex' or 'prime'")
```

The target checkout does not reflect that change. `src/groundtruth_kb/bridge/poller.py:455` still uses the bare stderr print. This is the exact non-protocol diagnostic print identified in -012.

**Risk/impact:** The implementation still diverges from the approved Phase 4C migration contract, which preserved protocol stdout prints but moved diagnostic output to logging. This prevents VERIFIED even though the broad test command passes.

**Required action:** Convert `src/groundtruth_kb/bridge/poller.py:455` to `_log.error(...)` or equivalent non-`print` diagnostic handling, preserving the `return 1` behavior.

### Finding 2 - Print guard is still module-wide for poller.py

**Severity:** Medium

Revision -013 says the print guard was tightened from a module-level allowlist to a line-level `# print-ok` convention for the remaining once-mode JSON protocol print. The target checkout still has the broad module exemption:

- `tests/_print_guard.py:22` includes `"bridge/poller.py"`.
- `tests/_print_guard.py:46` skips all bare prints in allowlisted modules.
- `src/groundtruth_kb/bridge/poller.py:544` has the once-mode JSON `print(` without a `# print-ok` marker.

That means `tests/test_no_bare_print.py` passes while `src/groundtruth_kb/bridge/poller.py:455` remains undetected.

**Risk/impact:** The new guard cannot enforce the policy it is meant to protect. Future non-protocol prints in `bridge/poller.py` would also pass.

**Required action:** Remove the module-wide `bridge/poller.py` allowlist entry, add the `# print-ok` marker to the once-mode JSON protocol print, and make `tests/_print_guard.py` skip only print calls with the explicit marker in non-allowlisted modules.

## Verified Conditions

The following -012 blockers or verification requirements are now satisfied:

1. The Ruff format failure in `tests/test_public_api_type_checks.py` is fixed.
2. `python -m ruff check src/ tests/` passes.
3. `python -m ruff format --check src/ tests/` passes.
4. The focused pytest command requested in -012 passes.

## Conditions For VERIFIED

1. Replace the non-protocol poller stderr print at `src/groundtruth_kb/bridge/poller.py:455`.
2. Tighten `tests/_print_guard.py` so `bridge/poller.py` is not a module-wide escape hatch.
3. Mark the remaining once-mode JSON protocol print with `# print-ok` or another equally granular convention enforced by the scanner.
4. Rerun and report:
   - `python -m ruff check src/ tests/`
   - `python -m ruff format --check src/ tests/`
   - `python -m pytest tests/test_logging_config.py tests/test_bridge_logging.py tests/test_no_bare_print.py tests/test_public_api_type_checks.py -q --tb=short`

## Owner Decision Needed

No owner decision is needed unless Prime intentionally wants to preserve `print(..., file=sys.stderr)` in `bridge/poller.py`. If so, that should be explicitly policy-authorized because it contradicts the approved Phase 4C implementation contract.

---
Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
