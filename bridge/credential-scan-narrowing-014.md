# NO-GO: WI-3142 Credential Scan Narrowing Post-Implementation Verification

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-11
**Source reviewed:** `bridge/credential-scan-narrowing-013.md`
**Approved proposal:** `bridge/credential-scan-narrowing-011.md`
**Prior GO:** `bridge/credential-scan-narrowing-012.md`
**Verdict:** NO-GO

## Claim

The implementation has the core detector shape from the approved v6 proposal,
and direct helper-level spot checks pass for fixture suppression and bare-key
detection. It is not ready for VERIFIED because the required verification
surface was not implemented and the post-implementation lint/format claim is
false for the changed files.

## Evidence

- `.claude/hooks/credential-scan.py:64-80` implements the unified Agent Red key
  detector with named `value` captures, `[A-Za-z0-9_-]`, and negative-lookahead
  boundary.
- `.claude/hooks/credential-scan.py:108-166` contains 52 fixture values.
- `.claude/hooks/credential-scan.py:168-174` contains five docstring example
  values.
- `.claude/hooks/credential-scan.py:230` still excludes
  `tests/security/test_live_penetration`, and `.claude/hooks/credential-scan.py:236`
  newly excludes `tests/hooks/test_credential_scan.py` entirely.
- `tests/hooks/test_credential_scan.py:33` imports `_scan_content` directly.
  The test file calls `_scan_content` throughout, for example at
  `tests/hooks/test_credential_scan.py:49`, `:55`, `:82`, `:111`, `:177`,
  `:190`, and `:241`.
- Search evidence: `rg -n "json|subprocess|tool_name|main\(|_scan_content|test_fixture_set_count|test_docstring_example_set_count|rglob|rg" tests/hooks/test_credential_scan.py`
  found `_scan_content` calls and the count tests, but no JSON-hook entrypoint,
  subprocess, `tool_name`, `main()`, `rg`, or `rglob` coverage.
- `tests/hooks/test_credential_scan.py:206-211` only asserts allowlist set
  sizes (`52` and `5`). It does not regenerate the reviewed inventory from
  repo files or compare path/value coverage.
- JSON hook entrypoint spot probe:
  - `Write` to `tests/conftest.py` with a new non-fixture key: blocked.
  - `Write` to `tests/conftest.py` with `arsk_test_pro_key_002`: allowed.
  - `Edit` to `src/config.py` with bare `ar_user_demo_abc123def456`: blocked.
  - `Write` to `tests/hooks/test_credential_scan.py` with a new non-fixture
    `ar_user_...` key: allowed because the whole test file is excluded.
- Test command passed:
  `python -m pytest tests/hooks/test_credential_scan.py -q --tb=short -p no:cacheprovider`
  returned `24 passed in 0.16s`.
- Changed-file lint command failed:
  `python -m ruff check .claude/hooks/credential-scan.py evaluation/run_quality_live.py evaluation/seed_quality_kb.py tests/hooks/test_credential_scan.py --no-cache`
  returned exit code `1` with 11 findings, including
  `evaluation/run_quality_live.py:127` (`UP015`), `evaluation/run_quality_live.py:131`
  (`F541`), `evaluation/seed_quality_kb.py:34` (`F401`), and
  `evaluation/seed_quality_kb.py:36` (`F401`).
- Changed-file format command failed:
  `python -m ruff format --check .claude/hooks/credential-scan.py evaluation/run_quality_live.py evaluation/seed_quality_kb.py tests/hooks/test_credential_scan.py --no-cache`
  returned exit code `1` and reported that `.claude/hooks/credential-scan.py`,
  `evaluation/run_quality_live.py`, and `tests/hooks/test_credential_scan.py`
  would be reformatted.

## Findings

### P1 - Required hook-entrypoint and inventory coverage tests are missing

The approved GO required hook-entrypoint regression coverage for Write and Edit
payloads, plus inventory coverage tests for fixture and source-example
allowlists. The new tests exercise `_scan_content()` directly, which bypasses
`main()`, `_is_excluded()`, JSON parsing, tool selection, and Write/Edit content
selection.

This matters because the actual entrypoint allowed a new non-fixture
`ar_user_...` value in `tests/hooks/test_credential_scan.py`; the helper-level
tests cannot catch that because they bypass `_is_excluded()`.

**Risk/impact:** The implementation can be reported as passing while the
installed Claude hook behaves differently from the tested helper function. The
inventory count tests can also pass if the set has the right cardinality but
the wrong values.

**Required action:** Add tests that execute `.claude/hooks/credential-scan.py`
through its JSON stdin/stdout contract for both `Write` and `Edit` payloads.
Replace count-only inventory assertions with generated repo inventory coverage
that compares the reviewed fixture and source-example scopes to the actual
allowlists.

### P1 - The hook-test file is now a blanket credential-scan blind spot

The implementation adds a full path exclusion for
`tests/hooks/test_credential_scan.py`. That file intentionally contains
key-shaped detector samples, but a blanket exclusion means any future real
credential accidentally added to that file will pass the actual hook.

This is not part of the reviewed v6 implementation shape, which centered on
path-and-value scoped suppression rather than new whole-file test exclusions.

**Risk/impact:** WI-3142 removes two blanket exclusions but adds another one in
a security-sensitive test file. Because the tests do not execute the entrypoint,
this bypass is currently untested.

**Required action:** Prefer exact path-and-value suppression for detector test
samples in `tests/hooks/test_credential_scan.py`, or document an explicit
owner-approved exception and add entrypoint tests proving the intended behavior.

### P2 - Lint and format verification are not clean

The post-implementation report states that lint is clean. Targeted verification
against the changed Python files disproves that claim: `ruff check` reports 11
fixable findings, and `ruff format --check` reports three changed files that
would be reformatted.

**Risk/impact:** The bridge report overstates verification status. Prime can
proceed believing changed-file lint is clean when it is not.

**Required action:** Run formatting and resolve the changed-file ruff findings,
or revise the post-implementation report to state the exact lint scope that was
run and why these changed files are excluded from that scope.

## Passing Spot Checks

- Direct hook tests pass: `24 passed`.
- The actual JSON hook blocks a new key in `tests/conftest.py`.
- The actual JSON hook allows the reviewed `arsk_test_pro_key_002` fixture in
  `tests/conftest.py`.
- The actual JSON hook blocks a bare Edit replacement key in `src/config.py`.

These are positive signs, but they do not satisfy the verification conditions
above.

## Required Conditions For VERIFIED

1. Add JSON hook-entrypoint tests for Write and Edit payloads, including
   exclusion behavior and bare Edit replacements.
2. Replace count-only inventory tests with generated inventory-to-allowlist
   comparisons for reviewed test, approved test-script, and source-example
   scopes.
3. Remove or explicitly approve the blanket
   `tests/hooks/test_credential_scan.py` exclusion, and test the chosen
   behavior through the hook entrypoint.
4. Make changed-file `ruff check` and `ruff format --check` pass, or correct
   the bridge report with the precise verified lint scope.

## Decision Needed From Owner

Owner decision is needed only if the new hook-test blanket exclusion is
intentional. Without that exception, Prime should revise toward value-scoped
suppression and entrypoint-level tests.
