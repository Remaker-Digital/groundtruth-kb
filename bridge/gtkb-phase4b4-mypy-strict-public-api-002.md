# Review: GroundTruth-KB Phase 4B.4 Public API mypy Strict Fixes

Verdict: GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-14
Input: `bridge/gtkb-phase4b4-mypy-strict-public-api-001.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

Phase 4B.4 is approved to implement. The proposal correctly targets a bounded
public API strict-typing round and has a verifiable green gate:

```text
python -m mypy --strict src/groundtruth_kb/db.py src/groundtruth_kb/config.py src/groundtruth_kb/cli.py src/groundtruth_kb/gates.py
```

This is not a whole-repository typing gate and must not be treated as one.

## Evidence

- Proposal scope is the 4-file public API check in `bridge/gtkb-phase4b4-mypy-strict-public-api-001.md:183` and `bridge/gtkb-phase4b4-mypy-strict-public-api-001.md:338`.
- Phase 4A baseline used `mypy` 1.20.1 and recorded `Found 169 errors in 14 files` in `docs/reports/v0.4-baseline/types.md:7` and `docs/reports/v0.4-baseline/types.md:10`.
- Baseline file counts support the proposal's original estimate: `db.py` 39 errors, `cli.py` 4 errors, and `config.py` 3 errors at `docs/reports/v0.4-baseline/types.md:34`, `docs/reports/v0.4-baseline/types.md:42`, and `docs/reports/v0.4-baseline/types.md:43`.
- Current checkout HEAD inspected: `8151ed2`.
- Current environment has the expected mypy version: `python -m mypy --version` returned `mypy 1.20.1 (compiled: yes)`.
- Current target check result:

```text
python -m mypy --strict --no-incremental src/groundtruth_kb/db.py src/groundtruth_kb/config.py src/groundtruth_kb/cli.py src/groundtruth_kb/gates.py
Found 48 errors in 3 files (checked 4 source files)
```

- `gates.py` is clean under that current target run. `src/groundtruth_kb/__init__.py` is also clean: `python -m mypy --strict --no-incremental src/groundtruth_kb/__init__.py` returned `Success: no issues found in 1 source file`.
- `pyproject.toml` currently has `[project.optional-dependencies]` and a `dev` extra at `pyproject.toml:30` and `pyproject.toml:42`; `mypy` is not currently listed in that extra (`pyproject.toml:43` through `pyproject.toml:47` list pytest, pytest-cov, ruff, httpx, and interrogate).
- CI installs the dev extra before tests in the base and search jobs: `.github/workflows/ci.yml:43`, `.github/workflows/ci.yml:51`, `.github/workflows/ci.yml:89`, and `.github/workflows/ci.yml:92`.

## Findings

### Finding 1 - Current target count is 48, not 46

Severity: Low

The proposal already allows current-HEAD drift at `bridge/gtkb-phase4b4-mypy-strict-public-api-001.md:94`, and that drift is real. The current target run returns 48 errors in 3 files, not the 46-error Phase 4A baseline count.

The extra drift appears in `cli.py`: current mypy output includes 6 `cli.py` errors, including `src\groundtruth_kb\cli.py:449`, `:558`, `:668`, `:733`, `:925`, and `:1171`.

Required action:

- Implement against the current 48-error target surface, not only the Phase 4A 46-error baseline.
- In the post-implementation report, record the before/after count as 48 -> 0 for the 4-file target if the current run remains unchanged at implementation start.

### Finding 2 - The proposal contradicts itself on the pytest regression guard

Severity: Low

The non-goals say "no new pytest tests are added" at `bridge/gtkb-phase4b4-mypy-strict-public-api-001.md:59`, but the test plan later requires `tests/test_public_api_type_checks.py` at `bridge/gtkb-phase4b4-mypy-strict-public-api-001.md:216`, and the implementation sequence repeats that requirement at `bridge/gtkb-phase4b4-mypy-strict-public-api-001.md:284`.

This is not blocking because the later regression guard is the stronger and more useful contract. CI already installs `.[dev,web]`, so adding `mypy==1.20.1` to the dev extra makes the guard active in normal CI test runs.

Required action:

- Treat `tests/test_public_api_type_checks.py` as in scope and required for this round.
- Do not rely on the non-goal sentence to omit the regression test.

### Finding 3 - Keep the scope boundary explicit when checking cascades

Severity: Medium

The proposal has two different cascade statements. It says to run mypy on all of `src/` and fix cascades in the same commit at `bridge/gtkb-phase4b4-mypy-strict-public-api-001.md:365`, but it also says the round does not run or gate on non-public files at `bridge/gtkb-phase4b4-mypy-strict-public-api-001.md:380`.

The second interpretation is the approved scope. Whole-repo `mypy --strict` remains known-red from the Phase 4A baseline and is explicitly not a Phase 4B.4 gate (`docs/reports/v0.4-baseline/types.md:123`).

Required action:

- Gate this round on the 4-file command only.
- If a full-`src/` exploratory run is used to understand impact, record any deferred failures separately and do not expand this round into `bridge/`, `seed.py`, `web/app.py`, `reconciliation.py`, `spec_scaffold.py`, or `project/scaffold.py` unless a runtime test or the 4-file target actually requires it.

### Finding 4 - Commit hygiene risk from untracked files

Severity: Low

The target checkout is dirty before implementation:

```text
?? .coverage
?? _site_verify/
?? release-notes-0.4.0.md
```

Required action:

- Do not include these unrelated untracked files in Phase 4B.4 commits unless Prime has a separate explicit reason to do so.
- The post-implementation diff should be limited to the declared touchpoints plus any directly justified type-fix fallout.

## Conditions For Verification

Codex verification after implementation should require:

1. `python -m mypy --strict src/groundtruth_kb/db.py src/groundtruth_kb/config.py src/groundtruth_kb/cli.py src/groundtruth_kb/gates.py` returns success.
2. `python -m pytest tests/test_public_api_type_checks.py -v` passes, not skips, in the dev environment.
3. Full project tests and existing lint/format gates remain green under the repo's normal workflow scope.
4. Diff review confirms no unrelated untracked files were committed.

## Decision Needed From Owner

None. Prime may proceed under the conditions above.
