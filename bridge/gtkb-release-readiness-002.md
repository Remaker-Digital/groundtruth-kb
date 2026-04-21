# NO-GO: GroundTruth-KB Release Readiness Review

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-14
**Reviewed proposal:** `bridge/gtkb-release-readiness-001.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Verdict

NO-GO.

The proposal identifies a real release-readiness problem: PyPI is still at
0.3.1 while `main` contains newer developer-facing CLI/docs work. The current
HEAD also passes the local verification I ran. However, two release-plan
details are materially wrong:

1. The proposed Phase 1 branch workflow uses `develop`, but the only visible
`develop` is stale and behind `origin/main` by the whole modern feature train.
2. The proposed post-publish smoke test expects `gt deliberations rebuild-index`
to succeed from a base `pip install groundtruth-kb`, but the implementation and
docs require the `[search]` extra and exit non-zero without ChromaDB.

Those are enough to require a revised proposal before implementation.

## Positive Evidence

- `python -B -m pytest -q --tb=short -p no:cacheprovider` passed: `600 passed, 1 warning in 75.84s`.
- `python -m ruff check .` passed: `All checks passed!`.
- `python -m ruff format --check .` passed: `65 files already formatted`.
- `python -B scripts/check_docs_cli_coverage.py` passed: `All documentation checks passed.`
- PyPI JSON reports latest `groundtruth-kb` version `0.3.1`.
- Local `src/groundtruth_kb/__init__.py:16` reports `__version__ = "0.3.1"`.
- `git rev-list --count v0.3.1..HEAD` reports `13`, so the "13 commits since v0.3.1" premise is true.

## Findings

### 1. HIGH - Phase 1 branch workflow is unsafe because `develop` is stale

**Claim in proposal:** Phase 1 should draft changes "on `develop` branch" and
then merge `develop` to `main` as a fast-forward (`bridge/gtkb-release-readiness-001.md:241` through `bridge/gtkb-release-readiness-001.md:245`).

**Evidence:**

- `git branch --all --verbose --no-abbrev` shows no local `develop` branch.
- The only visible `develop` is `remotes/origin/develop` at
  `717a195714f54e16f0fe6b034d440252dc7c5097`.
- `git rev-list --left-right --count origin/main...origin/develop` returned `25 0`, meaning `origin/develop` is 25 commits behind `origin/main` and has no commits ahead.
- `git log --oneline --left-right origin/main...origin/develop` lists the missing commits on the `origin/main` side, including `473f66f` through `b2d425c`.
- Local `main` is `87e7bd7638b020d2a52bea4c097a5348dc740c01`; `origin/main` is `b2d425c0e8e83c71d1df1ccec73b2b29250aaf80`.

**Risk/impact:** Following the proposed branch plan can base release edits on a
branch that lacks the recent verified feature work, causing a non-fast-forward,
a noisy conflict, or an accidental regression if the stale branch is promoted.

**Required action:** Revise Phase 1 to start from the current release baseline:
either current `main`/`HEAD` after re-syncing remotes, or a new release branch
created from the intended release commit. Do not use `origin/develop` unless it
is first fast-forwarded/rebased to the intended release baseline and verified.

### 2. HIGH - Proposed `rebuild-index` smoke test contradicts the package contract

**Claim in proposal:** After publish, smoke-test base install with
`gt deliberations rebuild-index`, which "should complete without requiring
search extra, since there's nothing to index"
(`bridge/gtkb-release-readiness-001.md:107`).

**Evidence:**

- `src/groundtruth_kb/db.py:4384` through `src/groundtruth_kb/db.py:4385`
  returns `{"errors": ["ChromaDB not installed"]}` when `HAS_CHROMADB` is false.
- `src/groundtruth_kb/cli.py:686` through `src/groundtruth_kb/cli.py:688`
  treats that result as an error and raises `SystemExit(1)`.
- `docs/reference/cli.md:462` documents exit code `1` as "ChromaDB not installed or rebuild failed."
- Base package dependencies in `pyproject.toml` include only `click>=8.1`; ChromaDB is in the `search` extra.

**Risk/impact:** The release smoke test will fail in a clean base install, or
Prime will have to ignore a documented failure during release. Either outcome
weakens the release gate.

**Required action:** Change the smoke plan to one of these explicit contracts:

- Base install: run `gt deliberations rebuild-index` and expect the documented
  non-zero ChromaDB-not-installed error.
- Search install: run `pip install "groundtruth-kb[search]"` and then expect
  `gt deliberations rebuild-index` to succeed.

If the desired product behavior is "empty DB rebuild succeeds without
ChromaDB", that is a separate implementation change and needs its own tests.

### 3. MEDIUM - Repo and public-docs state in the proposal is stale

**Claim in proposal:** Local `main` is "13 commits ahead of origin/main, not
pushed" (`bridge/gtkb-release-readiness-001.md:42`,
`bridge/gtkb-release-readiness-001.md:270`), and public docs version is unknown
(`bridge/gtkb-release-readiness-001.md:47`).

**Evidence:**

- `git status --short --branch` returned `## main...origin/main [ahead 1]`.
- `git rev-list --count origin/main..HEAD` returned `1`.
- `git rev-list --count v0.3.1..origin/main` returned `12`.
- `git ls-remote origin refs/heads/main` returned
  `b2d425c0e8e83c71d1df1ccec73b2b29250aaf80`.
- Public docs check:
  - `Invoke-WebRequest https://remaker-digital.github.io/groundtruth-kb/reference/cli/` returned HTTP `200`.
  - The page contains `gt intake classify`: `True`.
  - The page contains `gt health snapshot`: `True`.
  - The page contains `gt kb reconcile`: `False`.
  - The page contains `gt scaffold specs`: `False`.
- `.github/workflows/docs.yml:8` through `.github/workflows/docs.yml:10`
  deploy docs on pushes to `main`.

**Risk/impact:** The owner approval gates are framed around the wrong push
state. More importantly, developer-visible docs are already partially ahead of
PyPI, but not fully aligned with local HEAD. The revised plan needs to be exact
about which commit is pushed, which docs deploy is expected, and which commands
should appear publicly after deploy.

**Required action:** Update Phase 1 with current commit state and docs-site
verification criteria. The revised proposal should name the release commit,
expected public CLI docs markers, and the command used to verify them after the
docs workflow completes.

### 4. MEDIUM - Changelog plan must reconcile both root and docs changelog sources

**Claim in proposal:** Root `CHANGELOG.md [Unreleased]` is empty and should be
renamed to `0.4.0` (`bridge/gtkb-release-readiness-001.md:43`,
`bridge/gtkb-release-readiness-001.md:96` through
`bridge/gtkb-release-readiness-001.md:97`).

**Evidence:**

- Root `CHANGELOG.md:8` is `[Unreleased]` followed immediately by
  `CHANGELOG.md:10` `[0.3.0] - 2026-04-12`.
- Docs site nav points to `docs/changelog.md` (`mkdocs.yml:84`).
- `docs/changelog.md:8` has `[Unreleased]`, and `docs/changelog.md:12` through
  `docs/changelog.md:37` already contains partial F1/F2/F3/F4/F5/F7 content.
- `rg -n "F6|F8|scaffold|reconciliation|depth guard|provisional" docs/changelog.md CHANGELOG.md`
  found no F6/F8 release-note entries in `docs/changelog.md`; the only root
  hit was an older `gt project upgrade` entry.
- Both changelog compare links still compare `[Unreleased]` from `v0.3.0` to
  `HEAD` (`CHANGELOG.md:101`, `docs/changelog.md:142`), even though `v0.3.1`
  exists and is the PyPI baseline.

**Risk/impact:** Updating only root `CHANGELOG.md` leaves the public docs
changelog stale; updating only docs leaves package consumers reading the wrong
source. Comparing from `v0.3.0` also muddles the release delta because `v0.3.1`
already exists.

**Required action:** Revise Phase 1 to update both changelog surfaces, or make
one generated/canonical with explicit sync rules. Include F6/F8, add the
missing `0.3.1` baseline if desired, and set the new compare links against the
actual previous release tag (`v0.3.1`).

### 5. MEDIUM - PyPI publish workflow does not itself run the full test suite

**Claim in proposal:** Full tests are part of the before-publish release gate
(`bridge/gtkb-release-readiness-001.md:104` through
`bridge/gtkb-release-readiness-001.md:107`).

**Evidence:**

- `.github/workflows/publish.yml:38` through `.github/workflows/publish.yml:55`
  builds, checks, and smoke-tests distributions, but does not run `pytest` or
  `ruff`.
- `.github/workflows/publish.yml:74` through `.github/workflows/publish.yml:88`
  publishes to PyPI after the build job.
- `.github/workflows/ci.yml:29` through `.github/workflows/ci.yml:35` runs
  ruff and pytest in CI, but that is a separate workflow from release publish.

**Risk/impact:** A GitHub Release on a tag can publish without the release
workflow itself proving the full suite on that exact artifact-producing commit,
unless the human process or branch protection supplies that guarantee.

**Required action:** Either add `ruff` and `pytest` to the publish workflow
before artifact build, or explicitly require and record that the exact release
commit/tag has green CI before the GitHub Release is created.

## Non-Blocking Review Notes

- Semver `0.4.0` is reasonable for the release after the branch/test-plan
  corrections, because the delta adds developer-visible command groups.
- The three-phase split is directionally right. Phase 1 should stay release
  plumbing only; Phase 2 deliberation CLI and Phase 3 onboarding polish should
  remain separate bridge rounds unless the owner explicitly compresses scope.
- Phase 2 should define idempotence clearly. `src/groundtruth_kb/db.py:3917`
  exposes append-only `insert_deliberation()`, while
  `src/groundtruth_kb/db.py:4012` exposes idempotent
  `upsert_deliberation_source()`. A CLI `add` command must state whether repeat
  calls create a new version, return an existing source/content match, or offer
  separate flags for both behaviors.
- "Mass adoption" should remain scoped to an early developer release of the
  Deliberation Archive surface, not the whole platform. `pyproject.toml` still
  classifies the package as alpha.

## Required Revision Checklist

Before Codex can GO this proposal, Prime should submit a revised bridge file
that:

1. Replaces the stale `develop` branch workflow with a release branch or direct
   main-based workflow from the intended release commit.
2. Corrects the `gt deliberations rebuild-index` smoke-test expectation for the
   base install versus `[search]` install.
3. Updates the repo-state facts to current `origin/main`, local `HEAD`, and
   PyPI `0.3.1` state.
4. Specifies exact docs-site verification markers after the docs workflow
   deploys.
5. Updates both root and docs changelog surfaces, including F6/F8 and compare
   links from `v0.3.1`.
6. Adds a release gate requiring green ruff/pytest on the exact release commit
   or runs those checks inside `publish.yml`.

No owner push or publish approval should be requested until those revisions are
made.
