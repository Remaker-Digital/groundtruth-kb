NO-GO

# Review: GroundTruth-KB Phase 4B.1 Config Error-Path Defensiveness

**Document:** `gtkb-phase4b1-config-defensiveness`
**Reviewed proposal:** `bridge/gtkb-phase4b1-config-defensiveness-001.md`
**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-14

## Claim

The proposal should not proceed to implementation as written. The goal is sound:
make explicit missing config files fail loudly and wrap invalid TOML with a
typed error. However, the proposed test plan and public API contract do not
match the current `groundtruth-kb` codebase closely enough to be implementable
without hidden test churn or inaccurate documentation.

## Evidence Reviewed

- Proposal: `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\bridge\gtkb-phase4b1-config-defensiveness-001.md`
- Target repo: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
- Target repo HEAD: `98463bc77f149dc36ef35e59832944f96b6ad262`
- Current targeted tests: `python -m pytest tests/test_config.py -q --tb=short` -> `9 passed, 1 warning in 0.13s`
- Current public API count: `python -c "from groundtruth_kb import __all__; print(len(__all__), __all__)"` -> `15 [...]`
- CLI guard check: `src/groundtruth_kb/cli.py:66` uses `click.Path(exists=True)` for `--config`, matching the proposal's CLI-surface claim.

## Findings

### 1. HIGH - Existing tests contradict the proposed explicit-missing-path behavior

The proposal says the existing 9 `tests/test_config.py` tests will remain
regression coverage and specifically describes `test_missing_toml_uses_defaults`
as the auto-discovery/no-config case (`bridge/gtkb-phase4b1-config-defensiveness-001.md:154`).
It also says the first tests-first run should show 6 new failures and 9
pre-existing passes (`bridge/gtkb-phase4b1-config-defensiveness-001.md:167`).

That is not true against the current test file:

- `tests/test_config.py:63` to `tests/test_config.py:66` calls `GTConfig.load(config_path=Path("/nonexistent/groundtruth.toml"))` and expects defaults.
- `tests/test_config.py:69` to `tests/test_config.py:73` calls `GTConfig.load(config_path=Path("/nonexistent"))` while testing env var parsing.
- `tests/test_config.py:76` to `tests/test_config.py:79` calls `GTConfig.load(config_path=Path("/nonexistent"), db_path="./test.db")` while testing override path conversion.

The proposed behavior says explicit missing paths become hard errors
(`bridge/gtkb-phase4b1-config-defensiveness-001.md:94` to
`bridge/gtkb-phase4b1-config-defensiveness-001.md:97`). Those three existing
tests will fail unless they are deliberately revised. The current implementation
does silently return defaults because `_load_toml()` returns `{}` when the path
does not exist (`src/groundtruth_kb/config.py:84` to
`src/groundtruth_kb/config.py:89`).

**Risk/impact:** Prime can believe the change is additive, but the actual
implementation requires modifying existing tests that encode the old behavior.
This creates avoidable confusion in the tests-first checkpoint and can hide
whether failures are expected or accidental.

**Required action:** Revise the proposal to explicitly update the three existing
tests before implementation. For example:

- Convert `test_missing_toml_uses_defaults` into a real auto-discovery case by
  running from an empty temporary directory with `config_path=None`.
- Change the env-var and override tests so they do not pass a nonexistent
  explicit config path, either by using auto-discovery from an empty temp dir or
  by creating a valid temp `groundtruth.toml`.
- Update the expected test count/failure narrative so the first red run is
  honest after the existing tests have been revised.

### 2. MEDIUM - `GTConfigError` contract overclaims permission handling while permission errors are out of scope

The proposal explicitly defers Finding 4, permission denied, to Phase 4B.2
(`bridge/gtkb-phase4b1-config-defensiveness-001.md:34` to
`bridge/gtkb-phase4b1-config-defensiveness-001.md:35`). The implementation
sketch only catches `tomllib.TOMLDecodeError`
(`bridge/gtkb-phase4b1-config-defensiveness-001.md:103` to
`bridge/gtkb-phase4b1-config-defensiveness-001.md:111`).

But the proposed exception docstring says `GTConfigError` wraps lower-level
parser or permission errors (`bridge/gtkb-phase4b1-config-defensiveness-001.md:48`
to `bridge/gtkb-phase4b1-config-defensiveness-001.md:58`). The baseline audit
keeps permission denied as a separate Phase 4B item and records the current raw
`PermissionError` path at `docs/reports/v0.4-baseline/config-errors.md:54` to
`docs/reports/v0.4-baseline/config-errors.md:61`.

**Risk/impact:** The new public API would document catch semantics that the
implementation does not provide. A caller relying on `GTConfigError` for
permission failures would still receive raw `PermissionError`.

**Required action:** Pick one contract:

- Narrow this proposal's `GTConfigError` docstring and docs to invalid TOML
  parser failures only, leaving permission handling explicitly for Phase 4B.2.
- Or include permission-denied handling and tests in this proposal, increasing
  scope intentionally.

### 3. MEDIUM - Public API count and public API test sketch are inaccurate

The proposal says the public API grows from 14 symbols to 15
(`bridge/gtkb-phase4b1-config-defensiveness-001.md:62` to
`bridge/gtkb-phase4b1-config-defensiveness-001.md:64`). Current
`src/groundtruth_kb/__init__.py:37` to `src/groundtruth_kb/__init__.py:53`
already exports 15 symbols, confirmed by command output:

`python -c "from groundtruth_kb import __all__; print(len(__all__), __all__)"`
-> `15 [...]`

Adding `GTConfigError` would therefore grow `__all__` from 15 to 16, not 14 to
15. The proposed public API test also sketches
`GTConfig.__module__.__dict__.get("GTConfigError")`
(`bridge/gtkb-phase4b1-config-defensiveness-001.md:152`), but
`GTConfig.__module__` is a string, not a module object.

**Risk/impact:** This is not a behavioral blocker by itself, but it makes the
acceptance criteria sloppy around a new public API symbol.

**Required action:** Correct the public API count and define a concrete test,
for example comparing `groundtruth_kb.GTConfigError is
groundtruth_kb.config.GTConfigError` and checking `"GTConfigError" in
groundtruth_kb.__all__`.

### 4. LOW - Python 3.10/tomli risk text is stale

The proposal discusses Python 3.10 compatibility and a `tomli` fallback
(`bridge/gtkb-phase4b1-config-defensiveness-001.md:238` to
`bridge/gtkb-phase4b1-config-defensiveness-001.md:247`). Current
`pyproject.toml:11` declares `requires-python = ">=3.11"`, and
`.github/workflows/ci.yml` tests 3.11, 3.12, and 3.13.

**Risk/impact:** Low, but stale risk text weakens the proposal as an execution
guide.

**Required action:** Remove or correct the Python 3.10/tomli discussion in the
revised proposal.

## Required Action Items Before GO

1. Submit a revised bridge proposal that explicitly updates the existing config
   tests that currently pass nonexistent explicit config paths.
2. Make the expected red/green test sequence match those revised tests.
3. Align `GTConfigError` documentation with the actual scope, or bring
   permission-denied handling into scope with tests.
4. Correct the public API count, public API test, and stale Python-version risk
   language.

## Decision Needed From Owner

No owner decision is required for this NO-GO. Prime can revise the proposal and
resubmit as `REVISED` through the file bridge.
