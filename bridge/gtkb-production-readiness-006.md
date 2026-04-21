# VERIFIED: GroundTruth-KB Production Readiness Phase 1 Verification

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-14
**Reviewed report:** `bridge/gtkb-production-readiness-005.md`
**Review history read:** `bridge/gtkb-production-readiness-001.md` through `bridge/gtkb-production-readiness-005.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Verdict

VERIFIED.

Phase 1 of the GroundTruth-KB production-readiness roadmap is implemented and
the six verification conditions from `bridge/gtkb-production-readiness-004.md`
are satisfied by current evidence. Branch CI is green on commit
`993f31b8d42ac272b9716c191527b599d08ba632` across the base matrix, search
matrix, and cross-platform smoke jobs. The release workflow now contains
independent base/search gates, an exact-release-commit branch CI gate, and a
cross-platform built-wheel smoke gate before PyPI publish. SonarCloud and the
other companion workflows are green on the same SHA. No `v0.4.0` tag, GitHub
Release, or PyPI publish exists yet.

This verification closes Phase 1 only. It does not approve creating the
`v0.4.0` tag, publishing a GitHub Release, publishing to PyPI, changing the
classifier to Beta, or making any v1.0 claim. Those remain separate owner and
bridge gates.

## Evidence

- `git status --short --branch` in `groundtruth-kb` returned
  `## main...origin/main` with only `_site_verify/` untracked.
- `git rev-parse HEAD` and `git rev-parse origin/main` both returned
  `993f31b8d42ac272b9716c191527b599d08ba632`.
- `git log --oneline -5` shows the Phase 1 commits on top of `7984f0e`:
  `2b9d204` test guard fix, `7b1bf1f` CI matrix expansion, and `993f31b`
  publish gate hardening.
- `tests/test_cli.py:203` through `tests/test_cli.py:214` now gate the
  ChromaDB-present runtime fallback assertion with `pytest.importorskip("chromadb")`.
- `tests/test_cli.py:216` through `tests/test_cli.py:235` cover the
  no-ChromaDB output path and assert `chromadb not installed`.
- `.github/workflows/ci.yml:24` through `.github/workflows/ci.yml:51` define
  `test-base` across Python 3.11, 3.12, and 3.13 with `.[dev,web]` and full
  pytest.
- `.github/workflows/ci.yml:70` through `.github/workflows/ci.yml:92` define
  `test-search` across Python 3.11, 3.12, and 3.13 with `.[dev,web,search]`
  and full pytest.
- `.github/workflows/ci.yml:100` through `.github/workflows/ci.yml:146` define
  `test-cross-platform` across Ubuntu, Windows, and macOS in the base
  no-search state, including CLI smoke and the `gt deliberations rebuild-index`
  base-state failure contract.
- `.github/workflows/publish.yml:39` through `.github/workflows/publish.yml:58`
  define `ci-gate-base` with `.[dev,web]`, ruff, format check, full pytest, and
  docs CLI coverage.
- `.github/workflows/publish.yml:65` through `.github/workflows/publish.yml:78`
  define `ci-gate-search` with `.[dev,web,search]` and full pytest.
- `.github/workflows/publish.yml:89` through `.github/workflows/publish.yml:132`
  define `branch-ci-gate`, resolving the release tag with
  `git rev-list -n 1 "$TAG"` and requiring a completed successful `CI` run with
  matching `headSha`.
- `.github/workflows/publish.yml:134` through `.github/workflows/publish.yml:135`
  make `build-verify` depend on `ci-gate-base`, `ci-gate-search`, and
  `branch-ci-gate`.
- `.github/workflows/publish.yml:193` through `.github/workflows/publish.yml:253`
  define cross-platform built-wheel smoke tests in the base no-search state and
  make `publish-pypi` depend on both `build-verify` and
  `smoke-test-cross-platform`.
- `gh run view 24415766721 --repo Remaker-Digital/groundtruth-kb --json headSha,conclusion,status,jobs`
  returned `headSha=993f31b8d42ac272b9716c191527b599d08ba632`,
  `status=completed`, `conclusion=success`, with all nine CI jobs successful:
  `test-base (3.11)`, `test-base (3.12)`, `test-base (3.13)`,
  `test-search (3.11)`, `test-search (3.12)`, `test-search (3.13)`,
  `test-cross-platform (ubuntu-latest)`,
  `test-cross-platform (windows-latest)`, and
  `test-cross-platform (macos-latest)`.
- Latest workflow checks on `main` for SonarCloud, Docs, Security, CodeQL, and
  Docstring Coverage all returned `status=completed`, `conclusion=success`, and
  `headSha=993f31b8d42ac272b9716c191527b599d08ba632`.
- `pyproject.toml:17` still declares `Development Status :: 3 - Alpha`, and
  `pyproject.toml:21` through `pyproject.toml:23` advertise Python 3.11, 3.12,
  and 3.13 support.
- `src/groundtruth_kb/__init__.py:16` remains `__version__ = "0.4.0"`.
- `git tag --list "v0.4.0"` returned no local tag.
- `git ls-remote --tags origin "refs/tags/v0.*"` listed tags only through
  `v0.3.1`.
- `gh release list --repo Remaker-Digital/groundtruth-kb --limit 5` listed
  `v0.3.1` as the latest GitHub Release.
- PyPI JSON lookup returned latest `groundtruth-kb` version `0.3.1`.
- `git ls-remote origin refs/heads/main` returned
  `993f31b8d42ac272b9716c191527b599d08ba632`.

## Findings

### 1. PASS - Branch CI covers both dependency states across advertised Python versions

The base no-search suite and the search-installed suite now run full pytest
across Python 3.11, 3.12, and 3.13. This matches the advertised Python support
in `pyproject.toml:21` through `pyproject.toml:23` and closes the original
blind spot where only `pytest -k "deliberation"` ran in the ChromaDB-installed
state.

**Evidence:** `.github/workflows/ci.yml:24` through `.github/workflows/ci.yml:92`;
CI run `24415766721`, all six `test-base` and `test-search` jobs successful.

**Required action:** None for Phase 1.

### 2. PASS - The original ChromaDB test guard defect is fixed

The ChromaDB-present assertion now skips in the base no-search install state,
and the no-ChromaDB behavior remains covered by a separate test that mocks
ChromaDB import failure.

**Evidence:** `tests/test_cli.py:203` through `tests/test_cli.py:235`;
CI run `24415766721`, full base and search matrices successful.

**Required action:** None for Phase 1.

### 3. PASS - Publish is gated by base, search, and exact-SHA branch CI checks

The release workflow no longer relies on a single ChromaDB-installed gate. It
requires independent base and search gates before `build-verify`, and it checks
that the release tag resolves to a commit whose branch CI run has a matching
successful `headSha`.

**Evidence:** `.github/workflows/publish.yml:39` through
`.github/workflows/publish.yml:135`.

**Required action:** Phase 2 should not remove or weaken these gates. If the
first release run exposes a `checkout`/tag-fetching edge case in
`branch-ci-gate`, fix the workflow before publish rather than bypassing the
gate.

### 4. PASS - Cross-platform base/no-search evidence is present

Branch CI includes base/no-search cross-platform smoke on Ubuntu, Windows, and
macOS. The publish workflow also contains a built-wheel cross-platform
base/no-search smoke gate before PyPI publish.

**Evidence:** `.github/workflows/ci.yml:100` through `.github/workflows/ci.yml:146`;
`.github/workflows/publish.yml:193` through `.github/workflows/publish.yml:253`;
CI run `24415766721`, all three `test-cross-platform` jobs successful.

**Required action:** None for Phase 1. The publish-time smoke job cannot execute
until a release event exists, so Phase 2 must watch it rather than assume it.

### 5. PASS - SonarCloud is no longer blocked by the pytest failure

The latest SonarCloud workflow on `main` completed successfully on the same
commit as the green CI run. This verifies that the previous coverage-step
failure has been cleared.

**Evidence:** `gh run list --repo Remaker-Digital/groundtruth-kb --workflow SonarCloud --branch main --limit 1`
returned success on `993f31b8d42ac272b9716c191527b599d08ba632`.

**Required action:** None for Phase 1. Deeper Sonar and coverage analysis
belongs in the later audit phase already approved by the roadmap.

### 6. PASS - No release or publish was performed

The version text is still `0.4.0`, but there is no `v0.4.0` local or remote
tag, no GitHub Release newer than `v0.3.1`, and PyPI latest remains `0.3.1`.

**Evidence:** `src/groundtruth_kb/__init__.py:16`; local and remote tag checks;
GitHub Release list; PyPI JSON lookup.

**Required action:** Owner approval remains required before creating the
`v0.4.0` tag or publishing to PyPI.

## Required Conditions For Next Phase

1. Phase 2 must use `993f31b8d42ac272b9716c191527b599d08ba632` or a later
   explicitly verified commit as the release commit, not the older `7984f0e`
   version-bump commit alone.
2. Owner approval is required before tag creation.
3. Owner approval is required before GitHub Release/PyPI publish.
4. During the first release run, verify that `branch-ci-gate`,
   `smoke-test-cross-platform`, and `publish-pypi` all execute as intended; do
   not bypass a failing gate without a new bridge review.
5. Keep the package classifier at Alpha until the later Beta phase is reviewed
   and approved.

## Decision Needed From Owner

Approve or reject proceeding to a separate Phase 2 bridge round for the
`v0.4.0` tag and PyPI release. This verification does not imply publish
approval.
