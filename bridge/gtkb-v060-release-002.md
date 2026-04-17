GO

# GT-KB v0.6.0 Release Bundle Review

**Status:** GO with required release-execution conditions
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-v060-release-001.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Verdict

GO. The release-prep plan is sound: make one release-prep commit that bumps
`__version__`, updates the changelog, and adds v0.6.0 release notes, then tag
that release-prep commit. Do not tag the current Phase A #5 commit directly.

This approval is conditional on the required action items below, especially
waiting for branch CI to complete successfully on the release-prep commit before
publishing the GitHub Release.

## Evidence Reviewed

- `git rev-parse HEAD` in `groundtruth-kb`: `962909133e2a1172c834fbd546114412e22919eb`.
- `git show --no-patch --format='%H%n%h%n%s' v0.5.0`: `64e59e3345186b66203202f168cf883010b00858`, subject `fix(mypy): add untyped-decorator to type ignore for mcp.resource`.
- `git rev-list --count v0.5.0..HEAD`: `13`.
- `git log --oneline v0.5.0..HEAD`: confirms the 13 proposed commits are present.
- `git rev-list --count origin/main..HEAD`: `8`; local `main` is ahead of `origin/main` by 8 before release prep.
- `git tag --list 'v0.6.0'` and `git ls-remote --tags origin refs/tags/v0.6.0 refs/tags/v0.6.0^{}`: no existing local or remote v0.6.0 tag returned.
- `git status --short --branch`: `main...origin/main [ahead 8]` plus untracked `.coverage`, `.groundtruth-chroma/`, `_site_verify/`, `release-notes-0.4.0.md`, and `uv.lock`.
- `python -m ruff check .`: passed.
- `python -m ruff format --check .`: passed, `127 files already formatted`.
- `python -m pytest -q --tb=short`: passed, `1209 passed, 1 warning in 253.87s`.

## Rationale

1. **Commit grouping is correct.** The release should point at a
   ready-to-ship snapshot, not at the last feature commit. The repo currently
   has 13 commits in `v0.5.0..HEAD`; adding exactly one release-prep commit
   produces the intended 14-commit release range.

2. **Version bump only is sufficient.** Packaging uses dynamic version metadata
   from `src/groundtruth_kb/__init__.py`: `pyproject.toml:7` declares
   `dynamic = ["version"]`, and `pyproject.toml:62-63` points Hatch at
   `src/groundtruth_kb/__init__.py`. The current version source remains
   `src/groundtruth_kb/__init__.py:16`, `__version__ = "0.5.0"`.

3. **No dependency or constraint bump is required for this release bundle.**
   `pyproject.toml:26` starts the runtime dependency list and the proposed
   release prep does not change that surface. The verified commit range adds
   governance hooks, templates, tests, docs, and quality work, not a new
   runtime dependency requirement.

4. **Retrospective v0.5.0 changelog hygiene is acceptable.** Current
   `CHANGELOG.md:8` is still `## [Unreleased]`, and the next released section
   is `CHANGELOG.md:175`, `## [0.4.0] - 2026-04-14`. `git show
   v0.5.0:CHANGELOG.md` confirms v0.5.0 shipped with that material still under
   Unreleased, so converting the existing section to `## [0.5.0] - 2026-04-15`
   is corrective release hygiene and does not need a separate bridge.

5. **Publishing via GitHub Release remains the right path.** The workflow
   triggers on published releases at `.github/workflows/publish.yml:18-20` and
   publishes to PyPI via `pypa/gh-action-pypi-publish@release/v1` at
   `.github/workflows/publish.yml:265-266`. No workflow change is needed for
   this release.

6. **Post-implementation verification scope is sufficient with one naming
   correction.** The actual console script is `gt` per `pyproject.toml`
   `[project.scripts]`, so the CLI check should be `gt --help` and/or
   `gt --version` rather than assuming a `groundtruth-kb` command exists.

## Findings and Conditions

### Finding 1 - Medium - Avoid the known branch-CI race instead of treating it as normal

**Evidence:** `.github/workflows/publish.yml:80-89` defines `branch-ci-gate`.
The gate queries the CI workflow for the exact release commit at
`.github/workflows/publish.yml:106`, then fails if the CI run is not completed
at `.github/workflows/publish.yml:125` or not successful at
`.github/workflows/publish.yml:129`. The workflow is triggered by a published
GitHub Release at `.github/workflows/publish.yml:18-20`.

**Risk/impact:** If Prime pushes the release-prep commit and immediately
publishes the GitHub Release before the `CI` workflow has completed on that
commit, `publish.yml` can fail by design. Manual rerun is a valid fallback, but
the clean release path should avoid a predictable red workflow.

**Required action:** After pushing `main` and `v0.6.0`, wait until the `CI`
workflow run whose `headSha` is the release-prep commit SHA is `completed` with
`success`. Only then publish the GitHub Release that triggers PyPI publishing.

### Finding 2 - Low - Stage exact files only

**Evidence:** `git status --short --branch` shows untracked local artifacts:
`.coverage`, `.groundtruth-chroma/`, `_site_verify/`,
`release-notes-0.4.0.md`, and `uv.lock`. The proposal scope is only
`src/groundtruth_kb/__init__.py`, `CHANGELOG.md`, and
`release-notes-0.6.0.md`.

**Risk/impact:** A broad `git add .` or `git add release-notes-*` could pull
unrelated local artifacts into the release-prep commit.

**Required action:** Stage only the three intended paths explicitly:
`src/groundtruth_kb/__init__.py`, `CHANGELOG.md`, and
`release-notes-0.6.0.md`.

### Finding 3 - Low - Correct release-plan wording during execution/reporting

**Evidence:** The proposal says "Phase A Tier A (6 commits)" but lists seven
Phase A commit bullets, because one is a post-implementation fix. The proposal
also says pushing `main` pushes all 14 commits, but current local state is
`origin/main..HEAD = 8`; the earlier five commits in `v0.5.0..origin/main`
are already on origin.

**Risk/impact:** No release correctness issue, but inaccurate reporting makes
the post-implementation audit harder.

**Required action:** In the post-implementation report, describe the release
range as `v0.5.0..v0.6.0` containing 14 commits after release prep. If breaking
down Phase A, say "six Phase A bridge items represented by seven commits" or
equivalent.

## Required Post-Implementation Verification

Prime's proposed post-impl verification is sufficient if it includes:

1. Fresh venv install: `pip install groundtruth-kb==0.6.0`.
2. Version check: `python -c "import groundtruth_kb; print(groundtruth_kb.__version__)"` prints `0.6.0`.
3. CLI check using the actual console script: `gt --help` and/or `gt --version`.
4. Wheel content check confirms the three skill trees are packaged:
   `decision-capture`, `bridge-propose`, and `spec-intake`, each with
   `SKILL.md` and helper file.
5. PyPI project page shows `0.6.0` as latest.
6. Local and remote `v0.6.0` tag resolve to the release-prep commit, and the
   tag is annotated as planned.

## Decision Needed From Owner

None. Proceed with the release-prep implementation under the conditions above.

