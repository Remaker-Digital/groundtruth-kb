GO

# Review: GroundTruth-KB Phase 4B.1 Config Error-Path Defensiveness

**Document:** `gtkb-phase4b1-config-defensiveness`
**Reviewed proposal:** `bridge/gtkb-phase4b1-config-defensiveness-003.md`
**Prior bridge versions read:** `bridge/gtkb-phase4b1-config-defensiveness-001.md`, `bridge/gtkb-phase4b1-config-defensiveness-002.md`
**Verdict:** GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-14

## Claim

The revised proposal is approved for implementation. It directly addresses the
four NO-GO findings from `bridge/gtkb-phase4b1-config-defensiveness-002.md`
and now matches the current `groundtruth-kb` codebase closely enough to proceed
with tests-first implementation.

## Evidence Reviewed

- Bridge proposal: `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\bridge\gtkb-phase4b1-config-defensiveness-003.md`
- Prior NO-GO: `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\bridge\gtkb-phase4b1-config-defensiveness-002.md`
- Target repo: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
- Target repo HEAD: `98463bc77f149dc36ef35e59832944f96b6ad262`
- Target repo status: no tracked modifications; untracked `.coverage`, `_site_verify/`, and `release-notes-0.4.0.md` present.
- Current focused tests: `python -m pytest tests/test_config.py -q --tb=short` -> `9 passed, 1 warning in 0.15s`
- Current full suite: `python -m pytest -q --tb=short -p no:cacheprovider` -> `624 passed, 1 warning in 93.44s`
- Lint: `python -m ruff check .` -> `All checks passed!`
- Format: `python -m ruff format --check .` -> `68 files already formatted`
- Current public API count: `python -c "from groundtruth_kb import __all__; print(len(__all__), __all__)"` -> `15 [...]`
- Current explicit-missing-path behavior: `GTConfig.load(config_path=Path('/no/such/file'))` returns defaults (`GroundTruth KB`), confirming the proposal targets an existing silent failure.
- Current invalid-TOML behavior: `GTConfig.load(config_path=<bad toml>)` raises raw `tomllib.TOMLDecodeError`, confirming the proposal targets the audited error path.

## Rationale

The revised proposal fixes the prior HIGH finding by naming the three current
tests that encode the old silent-default behavior:

- `tests/test_config.py:63` `test_missing_toml_uses_defaults`
- `tests/test_config.py:69` `test_env_governance_gates_string`
- `tests/test_config.py:76` `test_db_path_string_converted_to_path`

It also gives concrete replacement behavior for each test at
`bridge/gtkb-phase4b1-config-defensiveness-003.md:146` through
`bridge/gtkb-phase4b1-config-defensiveness-003.md:236`, then updates the
red/green arithmetic at lines 256 through 284. That removes the hidden test
churn problem from the original proposal.

The revised `GTConfigError` contract is now scoped to TOML parser failures,
while permission-denied behavior remains raw and explicitly deferred to Phase
4B.2. That matches the current implementation path where `_load_toml()` opens
the config file and calls `tomllib.load(f)` without a catch
(`src/groundtruth_kb/config.py:84` through `src/groundtruth_kb/config.py:92`)
and matches the audit's separate permission finding in
`docs/reports/v0.4-baseline/config-errors.md:56` through
`docs/reports/v0.4-baseline/config-errors.md:60`.

The public API acceptance criteria are now accurate. Current
`src/groundtruth_kb/__init__.py:37` through `src/groundtruth_kb/__init__.py:52`
exports 15 names, so adding `GTConfigError` will grow `__all__` to 16, not 15.
The revised test compares `groundtruth_kb.GTConfigError` with
`groundtruth_kb.config.GTConfigError`, and the current package already exposes
`groundtruth_kb.config` after import.

The stale Python 3.10 risk text has been removed. Current
`pyproject.toml:11` requires Python `>=3.11`, and
`.github/workflows/ci.yml:30` and `.github/workflows/ci.yml:76` exercise
3.11, 3.12, and 3.13.

## Findings

No blocking findings remain.

## Required Conditions For Implementation

1. Keep the implementation within the revised touchpoint list unless a new
   bridge revision is submitted: `tests/test_config.py`,
   `src/groundtruth_kb/config.py`, `src/groundtruth_kb/__init__.py`,
   `docs/reference/configuration.md`, and `CHANGELOG.md`.
2. Preserve the revised tests-first checkpoint: existing test revisions plus
   the six new tests should produce the documented red state before
   implementation, then `15 passed` for `tests/test_config.py` after
   implementation.
3. Do not bundle permission-denied wrapping, `db.py`, CLI command changes, CI
   workflow changes, or baseline report edits into this sub-round.
4. After implementation, submit the post-implementation bridge report with the
   command outputs needed for Codex verification, including focused config
   tests, full suite, ruff, format check, docs CLI coverage, and public API
   smoke checks.

## Decision Needed From Owner

No owner decision is required for this GO. Prime may proceed with the revised
tests-first implementation and return through the file bridge for verification.
