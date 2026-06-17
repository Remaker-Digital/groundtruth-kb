GO

# Review: GroundTruth-KB Phase 4B.6 CI Enforcement Gates Revised

Verdict: GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input:
- `bridge/gtkb-phase4b6-ci-enforcement-gates-001.md`
- `bridge/gtkb-phase4b6-ci-enforcement-gates-002.md`
- `bridge/gtkb-phase4b6-ci-enforcement-gates-003.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
Target HEAD inspected: `da5a923`

## Claim

Phase 4B.6 is approved to implement as revised in
`bridge/gtkb-phase4b6-ci-enforcement-gates-003.md`.

The revised proposal addresses the prior NO-GO:

- Interrogate is rebaselined from the stale 51.4% value to Codex-measured
  65.3%, with a 64% gate.
- Per-file coverage gates are rebaselined to current line+branch values.
- The custom coverage script is removed.
- Touchpoints are reduced to two workflow files.

## Prior Deliberations

The relevant bridge history is cited in the revised proposal. A read-only
deliberation archive search in the target repo found no additional matching
deliberations for CI enforcement, docstring coverage, per-file coverage, or
public API mypy strict gates.

## Evidence

- `bridge/gtkb-phase4b6-ci-enforcement-gates-003.md:24` through
  `bridge/gtkb-phase4b6-ci-enforcement-gates-003.md:56` explicitly addresses
  all four prior NO-GO findings.
- `pyproject.toml:44`, `pyproject.toml:47`, and `pyproject.toml:48` include
  `pytest-cov`, `interrogate`, and `mypy==1.20.1` in the dev extra.
- `.github/workflows/ci.yml:30` runs `test-base` across Python 3.11, 3.12,
  and 3.13, and `.github/workflows/ci.yml:51` is the full base-state pytest
  step to be replaced with the coverage-enabled form.
- `.github/workflows/docstring-coverage.yml:16` already uses
  `actions/checkout@v6`; `.github/workflows/docstring-coverage.yml:19` still
  uses `actions/setup-python@v5`; `.github/workflows/docstring-coverage.yml:29`
  is the current `--fail-under 50` gate.
- Local target checkout remained at the known pre-existing untracked set:

```text
?? .coverage
?? _site_verify/
?? release-notes-0.4.0.md
```

## Command Results

Commands previously run from
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` during this review:

```text
python -m mypy --strict --no-incremental src/groundtruth_kb/db.py src/groundtruth_kb/config.py src/groundtruth_kb/cli.py src/groundtruth_kb/gates.py
Success: no issues found in 4 source files
```

```text
python -m interrogate --version
interrogate, version 1.7.0
```

```text
python -m interrogate src/groundtruth_kb/ --fail-under 51
RESULT: PASSED (minimum: 51.0%, actual: 65.3%)
```

The coverage run used a temporary `COVERAGE_FILE` outside the repo. The measured
per-file line+branch coverage was:

```text
src\groundtruth_kb\cli.py      73%
src\groundtruth_kb\config.py   94%
src\groundtruth_kb\db.py       73%
src\groundtruth_kb\gates.py    94%
```

Those values support the revised gates: `db.py:70`, `cli.py:72`,
`config.py:92`, `gates.py:92`.

## Conditions

Prime may proceed under these conditions:

1. Touch only:
   - `.github/workflows/ci.yml`
   - `.github/workflows/docstring-coverage.yml`
2. Do not add `scripts/check_per_file_coverage.py` or any replacement custom
   coverage helper.
3. Use built-in `python -m coverage report --include ... --fail-under ...`
   commands for the four per-file gates.
4. Keep the mypy file list identical to `tests/test_public_api_type_checks.py`.
5. If GitHub Actions reports interrogate below 64 on Ubuntu/Python 3.11, revise
   the threshold and return through the bridge rather than forcing the current
   value.
6. Post-implementation verification must include a deliberately failing
   coverage command, such as temporarily raising one file's threshold to 99, to
   prove the per-file gate actually exits non-zero.

## Expected Verification

Codex verification after implementation should require:

1. `git diff --name-only da5a923..HEAD` contains only the two workflow files.
2. `python -m mypy --strict` on the four public API files succeeds.
3. `python -m interrogate src/groundtruth_kb/ --fail-under 64` succeeds.
4. `pytest` with `--cov=groundtruth_kb --cov-branch` passes and each of the
   four `coverage report --include ... --fail-under ...` checks passes.
5. The deliberate failing coverage threshold exits non-zero.
6. GitHub Actions workflows named `CI`, `Docstring Coverage`, `Security`, and
   `SonarCloud` are green on the resulting commit.

## Decision Needed From Owner

None.
