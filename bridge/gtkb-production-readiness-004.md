# GO: GroundTruth-KB Production Readiness Roadmap Re-Review

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-14
**Reviewed proposal:** `bridge/gtkb-production-readiness-003.md`
**Review history read:** `bridge/gtkb-production-readiness-001.md`, `bridge/gtkb-production-readiness-002.md`, `bridge/gtkb-production-readiness-003.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Verdict

GO, with the conditions below.

The revised roadmap corrects the blocking release-safety error from the prior
review. It no longer claims the current single `publish.yml` `ci-gate` blocks
the no-search CI failure. It makes base and search dependency states mandatory,
sequences SonarCloud behind the pytest fix, adds cross-platform release evidence,
splits Phase 4 into audit-first and implementation follow-up work, and updates
the v0.4.0 release plan to match the current version/tag state.

This GO approves the roadmap direction and Phase 1 implementation planning. It
does not approve any v0.4.0 tag, GitHub Release, PyPI publish, beta classifier
change, or v1.0 claim. Those remain separate owner/bridge gates.

## Verification Evidence

- `git status --short --branch` in `groundtruth-kb` returned
  `## main...origin/main` with only `_site_verify/` untracked.
- `git rev-parse HEAD` and `git rev-parse origin/main` both returned
  `7984f0e99cc097d3606fc042c584f6aba426719f`.
- `.github/workflows/ci.yml:27` installs `.[dev,web]`; `.github/workflows/ci.yml:35`
  runs full pytest for the base matrix.
- `.github/workflows/ci.yml:64` installs `.[dev,web,search]`; `.github/workflows/ci.yml:67`
  still runs only `pytest -v --tb=short -k "deliberation"` in the current repo.
- `.github/workflows/publish.yml:41` currently installs `.[dev,web,search]` in the
  single `ci-gate`; `.github/workflows/publish.yml:56` has `build-verify` depend
  on only that one gate.
- `.github/workflows/sonarcloud.yml:33` installs `.[dev,web]`; `.github/workflows/sonarcloud.yml:37`
  runs `pytest --cov=groundtruth_kb --cov-report=xml:coverage.xml tests/`.
- `tests/test_cli.py:203` through `tests/test_cli.py:209` still assume ChromaDB is
  importable and assert `"runtime fallback"`.
- `tests/test_cli.py:211` through `tests/test_cli.py:230` already cover a mocked
  no-ChromaDB path, which means the installed-state test needs an import guard
  or equivalent dependency-aware split.
- `src/groundtruth_kb/cli.py:505` through `src/groundtruth_kb/cli.py:510` choose
  between runtime fallback and `chromadb not installed` by attempting
  `import chromadb`.
- `gh run list --repo Remaker-Digital/groundtruth-kb --workflow CI --branch main --limit 5`
  showed the five latest main CI runs failing, with current run `24412460119`
  failing at `7984f0e99cc097d3606fc042c584f6aba426719f`.
- `gh run view 24412460119 --json jobs` showed base `test (3.11)` failed, base
  `test (3.12)` and `test (3.13)` were cancelled after failures, and
  `test (search / 3.12)` succeeded.
- `gh run view 24412460119 --log-failed` showed
  `tests/test_cli.py::TestConfig::test_config_chroma_path_unset_chromadb_installed`
  failing because `"runtime fallback"` was absent and output contained
  `(unset - chromadb not installed)`.
- `gh run list --repo Remaker-Digital/groundtruth-kb --workflow SonarCloud --branch main --limit 3`
  showed the three latest main SonarCloud runs failing, with current run
  `24412460177` failing at the same commit.
- `gh run view 24412460177 --log-failed` showed SonarCloud failing during
  `Run tests with coverage` on the same `tests/test_cli.py:209` assertion before
  any actionable Sonar scan result.
- `rg -n "runs-on:" .github/workflows` returned only `ubuntu-latest` in current
  workflows.
- `src/groundtruth_kb/__init__.py:16` is `__version__ = "0.4.0"`.
- `pyproject.toml:17` still declares `Development Status :: 3 - Alpha`.
- `pyproject.toml:21` through `pyproject.toml:23` advertise Python 3.11, 3.12,
  and 3.13 support; `pyproject.toml:39` through `pyproject.toml:40` define the
  public `search` extra as `chromadb>=1.0.0,<2`.
- `git tag --list "v0.4.0"` returned no local tag.
- `git ls-remote --tags origin "refs/tags/v0.*"` listed tags through `v0.3.1`
  only.
- `gh release list --repo Remaker-Digital/groundtruth-kb --limit 5` showed
  `v0.3.1` as latest.
- PyPI JSON lookup for `groundtruth-kb` returned latest version `0.3.1`.
- `.github/workflows/docstring-coverage.yml:29` enforces
  `interrogate src/groundtruth_kb/ --fail-under 50 -vv`.
- `pyproject.toml:83` through `pyproject.toml:84` still contain dedicated
  `db.py` ruff suppressions.
- `rg -n "except Exception|except BaseException|except:" src/groundtruth_kb`
  returned broad exception sites in `assertions.py`, `db.py`, bridge modules,
  and project modules, supporting the revised Phase 4A audit-first split.
- `docs/reference/cli.md:437` through `docs/reference/cli.md:454` currently
  document only `gt deliberations rebuild-index`; `docs/reference/cli.md:717`
  through `docs/reference/cli.md:718` show only `rebuild-index` under
  `deliberations`.

## Findings

### 1. PASS - The prior publish-gate blocker is addressed

**Claim:** The revised roadmap requires independent release gates for base
no-search and search-installed dependency states, and makes `build-verify`
depend on both.

**Evidence:** Current `publish.yml` has only one gate and it installs
`.[dev,web,search]` (`.github/workflows/publish.yml:41`, `.github/workflows/publish.yml:56`).
The revised proposal explicitly replaces that with `ci-gate-base` and
`ci-gate-search` and proposes an exact-commit GitHub Actions check.

**Risk/impact:** Without this change, a release workflow could still pass while
the branch base-install matrix is red.

**Required action:** Implement both release gates and fail closed. Keep the
head-SHA safety check unless a later bridge proposal justifies removing it.
Because v0.4.0 will be an annotated tag, resolve the tag to the commit SHA before
comparing with a CI run's `headSha`; do not accidentally compare against an
annotated tag object SHA.

### 2. PASS - The matrix/extras gap is now a mandatory Phase 1 exit criterion

**Claim:** The revised roadmap requires full pytest coverage for base and search
states across Python 3.11, 3.12, and 3.13.

**Evidence:** Current `ci.yml` tests base installs across 3.11/3.12/3.13 but
runs search only on 3.12 with `-k "deliberation"` (`.github/workflows/ci.yml:50`
through `.github/workflows/ci.yml:67`). The revised proposal changes that to a
six-job base/search full-suite matrix.

**Risk/impact:** The current narrow search job is exactly why the CLI config
test could be wrong about its dependency state.

**Required action:** Treat the six-job matrix as the default bar. If ChromaDB or
another search dependency cannot support Python 3.13, the fix is to update
package metadata or add an explicit documented exclusion, not to silently leave
the search extra untested for an advertised Python version.

### 3. PASS - SonarCloud is correctly sequenced behind the pytest fix

**Claim:** The revised roadmap treats the current SonarCloud failure as the same
pytest failure, not as an unknown Sonar quality-gate problem.

**Evidence:** The current SonarCloud workflow installs `.[dev,web]` and fails in
`pytest --cov... tests/`; the latest failed log for run `24412460177` shows the
same `tests/test_cli.py:209` assertion before any useful scan result.

**Risk/impact:** Triage before a successful scan would create speculative work
and possible premature suppressions.

**Required action:** Fix pytest/matrix first, rerun SonarCloud, then triage only
actual Sonar findings if the scanner runs and reports a failing gate.

### 4. PASS WITH CONDITION - Cross-platform scope is acceptable only if base/no-search smoke is explicit

**Claim:** The revised roadmap adds cross-platform CI and publish-time smoke
testing before beta.

**Evidence:** Current workflows are Ubuntu-only by `rg -n "runs-on:" .github/workflows`.
The revised proposal adds a targeted `test-cross-platform` job and a
publish-time cross-platform wheel smoke job.

**Risk/impact:** The detailed revised `test-cross-platform` sketch installs
`.[dev,web,search]`. That is useful, but it does not by itself prove the
base/no-search package contract on Windows and macOS. The present failure is a
dependency-state blind spot, so cross-platform smoke must not repeat that blind
spot.

**Required action:** Phase 1 implementation must include cross-platform package
smoke in the base/no-search state on Ubuntu, Windows, and macOS. Minimum smoke:
install the built wheel without `search`, run `gt --version`, `gt project init`,
`gt config`, `gt summary`, and verify the no-search
`gt deliberations rebuild-index` error contract. Search-installed
cross-platform smoke is also
useful, but it is not a substitute for the base/no-search check.

### 5. PASS - Phase 4 is split at the right boundary

**Claim:** Phase 4A is measurement/report-only; Phase 4B+ implements approved
thresholds and gates.

**Evidence:** Current state supports audit-first: docstring enforcement is only
50 percent (`.github/workflows/docstring-coverage.yml:29`), `db.py` has
dedicated ruff suppressions (`pyproject.toml:83` through `pyproject.toml:84`),
and broad exception sites exist across `src/groundtruth_kb`.

**Risk/impact:** Jumping directly to strict mypy, higher coverage thresholds,
and broad exception rewrites would create a large mechanical phase with weak
reviewability.

**Required action:** Keep Phase 4A report-only. Do not enable fail-under gates or
strict mypy until the baseline report and owner-approved thresholds exist.

### 6. PASS - The release-state correction is accurate

**Claim:** v0.4.0 version text already exists on main, but the release tag and
PyPI publish do not.

**Evidence:** `src/groundtruth_kb/__init__.py:16` is `0.4.0`; local and remote
tags have no `v0.4.0`; GitHub Releases and PyPI are at `v0.3.1`.

**Risk/impact:** A release plan that talks as if the version bump is still
pending can tag the wrong commit or obscure what Phase 1 actually adds.

**Required action:** Release commit must be the Phase 1 verified commit on top
of `7984f0e`, not `7984f0e` alone.

## Answers to Revised Review Questions

1. **Two-job publish gate:** Sufficient only if both base and search jobs are
   required by `build-verify` and the exact-SHA safety check resolves annotated
   tags to commit SHAs. Keep the belt-and-suspenders check.
2. **Full base/search matrix:** Correct bar for the package as currently
   advertised. The project declares Python 3.11, 3.12, and 3.13 support and
   exposes `[search]` as a public extra.
3. **Cross-platform subset:** Targeted subset is acceptable for Phase 1. Full
   suite on all OS is not required yet. The subset must include base/no-search
   package smoke, not only search-installed smoke.
4. **Phase 4A scope:** Right size. Seven report files are reviewable and defer
   enforcement until the baseline is known.
5. **Phase 1 size:** Large but still acceptable as one bridge round if the
   implementation remains limited to the failing test guard, matrix definitions,
   publish gate hardening, Sonar rerun, and smoke workflows. Split it if it grows
   into feature work or broad refactoring.
6. **Two-job gate flaws:** Main implementation risks are annotated-tag SHA
   comparison, accidentally making only one gate required, and using a query that
   accepts a green CI run from a different head SHA. Test those failure modes.
7. **Missed checklist items:** The only residual precision issue is the
   cross-platform base/no-search smoke requirement above.

## Required Conditions Before Phase 1 Can Be VERIFIED

1. Branch CI runs full pytest for base and search dependency states across all
   advertised Python versions, or explicitly changes advertised support with
   owner/bridge approval.
2. Publish workflow has independent base and search gates, and build/publish
   jobs cannot run unless both pass.
3. Publish workflow checks that the release tag resolves to a commit with a
   successful CI run at the same `headSha`.
4. Cross-platform package smoke covers the built wheel in base/no-search state
   on Ubuntu, Windows, and macOS; search-installed smoke may be additional.
5. SonarCloud is re-evaluated only after pytest coverage can complete.
6. No v0.4.0 tag or PyPI publish occurs until Phase 1 is implemented, reviewed,
   and explicitly approved for release execution.

## Decision Needed From Owner

Owner approval is still required before any tag or PyPI publish. This GO does
not carry release approval forward by implication.
