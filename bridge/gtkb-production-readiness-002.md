# NO-GO: GroundTruth-KB Production Readiness Roadmap Review

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-14
**Reviewed proposal:** `bridge/gtkb-production-readiness-001.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Verdict

NO-GO.

The roadmap is directionally right: CI must be fixed first, the package should
go to beta before any v1.0 claim, and the later phases should be reviewed as
separate bridge rounds. However, the proposal relies on a false release-safety
claim: the current `publish.yml` `ci-gate` does not prove the no-search install
state that is failing on branch CI. A v0.4.0 GitHub Release could still pass the
publish workflow while the main CI workflow is red.

The proposal also treats SonarCloud as an unknown quality-gate failure, but the
current SonarCloud workflow is failing earlier, during pytest coverage, on the
same ChromaDB config test. The roadmap needs a revised Phase 1 gate sequence
before it is safe to approve as the production-readiness plan.

## Verification Evidence

- `git status --short --branch` in `groundtruth-kb` returned `## main...origin/main` with only `_site_verify/` untracked.
- `git rev-parse HEAD` and `git rev-parse origin/main` both returned `7984f0e99cc097d3606fc042c584f6aba426719f`.
- `git tag --list 'v0.4.0'` returned no tag. `git ls-remote --tags origin 'refs/tags/v0.*'` lists tags through `v0.3.1` only.
- `gh release list --repo Remaker-Digital/groundtruth-kb --limit 10` shows `v0.3.1` as latest. PyPI JSON reports latest `groundtruth-kb` version `0.3.1`.
- `src/groundtruth_kb/__init__.py:16` already reports `__version__ = "0.4.0"`, while `pyproject.toml:17` still classifies the package as `Development Status :: 3 - Alpha`.
- `gh run list --repo Remaker-Digital/groundtruth-kb --workflow CI --branch main --limit 15` shows 13 consecutive failing main-branch CI runs from `0fe21c9` through current `7984f0e`, after the prior success at `2e35461`.
- Current CI run `24412460119` on `7984f0e` failed. `gh run view 24412460119 --json jobs` shows the no-search matrix jobs failing or cancelled, while `test (search / 3.12)` succeeded.
- `gh run view 24412460119 --log-failed` shows `tests/test_cli.py::TestConfig::test_config_chroma_path_unset_chromadb_installed` failing because `"runtime fallback"` was not in output; output contained `(unset - chromadb not installed)`.
- Current SonarCloud run `24412460177` failed in the `Run tests with coverage` step, before the Sonar scan, on the same `tests/test_cli.py::TestConfig::test_config_chroma_path_unset_chromadb_installed` assertion.
- `.github/workflows/ci.yml:27` installs `.[dev,web]` for the main matrix and `.github/workflows/ci.yml:35` runs `pytest -v --tb=short`.
- `.github/workflows/ci.yml:64` installs `.[dev,web,search]` for `test-search`, but `.github/workflows/ci.yml:67` runs only `pytest -v --tb=short -k "deliberation"`.
- `.github/workflows/publish.yml:41` installs `.[dev,web,search]` in `ci-gate`, and `.github/workflows/publish.yml:50` runs `python -m pytest -q --tb=short`.
- Local dependency-sensitive check: `python -B -m pytest tests/test_cli.py::TestConfig::test_config_chroma_path_unset_chromadb_installed -q --tb=short -p no:cacheprovider` passed locally on Python 3.14 where ChromaDB is installed.
- `tests/test_cli.py:203` through `tests/test_cli.py:209` assume ChromaDB is importable and assert `"runtime fallback"`.
- `src/groundtruth_kb/cli.py:505` through `src/groundtruth_kb/cli.py:510` chooses between runtime fallback and `chromadb not installed` by attempting `import chromadb`.
- `docs/reference/cli.md:439` documents only `gt deliberations rebuild-index`; `docs/reference/cli.md:718` shows only `rebuild-index` under `deliberations`.

## Findings

### 1. HIGH - The publish self-gate does not currently block the red no-search CI failure

**Claim in proposal:** The new `ci-gate` means a red CI blocks PyPI publication, and "no release can happen, period."

**Evidence:** The failing branch CI path installs `.[dev,web]` (`.github/workflows/ci.yml:27`) and runs the full suite (`.github/workflows/ci.yml:35`). The publish gate installs `.[dev,web,search]` (`.github/workflows/publish.yml:41`) and then runs pytest (`.github/workflows/publish.yml:50`). The failing test is dependency-sensitive: it fails in the no-search GitHub environment and passed locally when ChromaDB was installed.

**Risk/impact:** A v0.4.0 GitHub Release could pass `publish.yml` because the publish gate installs ChromaDB, while the branch CI remains red for the base install state. That contradicts the roadmap's central safety claim and can publish a package whose advertised base-install CI is failing.

**Required action:** Revise Phase 1 so release blocking is self-enforcing for both dependency states. Acceptable fixes:

- Add separate publish jobs for base install (`.[dev,web]`, full pytest) and search install (`.[dev,web,search]`, full pytest or a clearly justified subset), with `build-verify` depending on both.
- Or require the release workflow to query GitHub Actions for a green `CI` run whose `headSha` exactly matches the release tag commit before `publish-pypi`.
- In either case, do not rely only on the current `publish.yml` `ci-gate` as proof that branch CI failures block PyPI.

### 2. HIGH - The matrix/extras gap must be a hard Phase 1 exit criterion, not an optional audit path

**Claim in proposal:** Phase 1 will fix CI and either extend `test-search` to run more tests, add a full search job, or install `[search]` in the main job.

**Evidence:** The current `test-search` job installs ChromaDB but only runs `pytest -k "deliberation"` (`.github/workflows/ci.yml:64` through `.github/workflows/ci.yml:67`). The actual dependency-sensitive failing test lives in `tests/test_cli.py:203`, so the search job never exercises the CLI config behavior with ChromaDB installed.

**Risk/impact:** Fixing only the single assertion can leave the same class of bug in place: tests whose names or assertions assume a dependency state that the CI job does not provide. That is exactly the kind of quality-signal drift this roadmap is meant to eliminate.

**Required action:** Make this a mandatory Phase 1 condition: the CI matrix must intentionally test the full suite in the base no-search state and intentionally test ChromaDB-dependent behavior in a ChromaDB-installed state. If runtime cost forces a subset, the proposal must name the included test files and justify why non-deliberation CLI/config tests are covered elsewhere.

### 3. MEDIUM - SonarCloud is not yet an unknown Sonar quality failure

**Claim in proposal:** SonarCloud fails on `7984f0e` and should be audited for security hotspots, bugs, code smells, or coverage issues.

**Evidence:** `gh run view 24412460177 --log-failed` shows SonarCloud failed during `pytest --cov=groundtruth_kb --cov-report=xml:coverage.xml tests/`, before the Sonar scan. The failure is the same `test_config_chroma_path_unset_chromadb_installed` assertion.

**Risk/impact:** The roadmap may spend time triaging hypothetical Sonar findings before the scanner has actually run on a green coverage test. This can also lead to premature suppressions with no real issue list.

**Required action:** Revise Phase 1 sequencing:

1. Fix the pytest/matrix failure first.
2. Re-run SonarCloud.
3. Only if the scan step runs and the quality gate still fails, triage actual Sonar findings by severity.

Documented suppressions are acceptable for cosmetic findings, but not before there is a concrete Sonar result to suppress.

### 4. MEDIUM - Production-grade release criteria omit cross-platform evidence

**Claim in proposal:** Phase 4 hardening plus Phase 6 beta release is enough to support the production-grade path.

**Evidence:** Current CI, publish, SonarCloud, docstring, docs, docs-check, and security workflows use `runs-on: ubuntu-latest`. The package exposes CLI commands, SQLite path handling, project scaffolding, config-file resolution, and ChromaDB path behavior that are platform-sensitive. The local checkout is Windows, but there is no GitHub Actions Windows or macOS gate.

**Risk/impact:** A beta PyPI release can be green on Linux but broken on Windows or macOS for path, shell, wheel, or optional-dependency behavior. That is below the bar for "production-grade" Python package readiness.

**Required action:** Add an explicit cross-platform gate before the beta classifier change. Minimum acceptable scope: Ubuntu, Windows, and macOS smoke tests for base install, `gt --version`, `gt project init`, and the no-search `gt deliberations rebuild-index` error contract. Preferably include a targeted pytest subset for CLI/config/path behavior on Windows.

### 5. MEDIUM - Phase 4 hardening needs an audit-first split before enforcing thresholds

**Claim in proposal:** Phase 4 should add 80 percent line coverage, 60 percent branch coverage, 80 percent docstring coverage, strict mypy, error-handling audit, config audit, and logging audit.

**Evidence:** The repo currently has no mypy dependency or workflow in `pyproject.toml` or `.github/workflows/`. `docstring-coverage.yml:29` enforces only `interrogate ... --fail-under 50`. `src/groundtruth_kb/db.py` is a large legacy module with dedicated ruff suppressions in `pyproject.toml:82` through `pyproject.toml:86`, and there are many broad `except Exception` sites under `src/`.

**Risk/impact:** Jumping directly to strict mypy and fixed coverage/docstring thresholds can create a large mechanical churn phase that obscures real defects and makes bridge review too broad.

**Required action:** Split Phase 4 into at least two bridge rounds:

- Phase 4A: measure coverage, branch coverage, docstring coverage, type-check baseline, broad exception inventory, config error-path inventory, and logging inventory. Produce a report and proposed thresholds.
- Phase 4B+: implement targeted fixes and gates from that report.

Do not enable fail-under gates or strict mypy until the baseline and owner-approved threshold are recorded.

### 6. LOW - Phase 2 must account for current version/tag state

**Claim in proposal:** Phase 2 will cut v0.4.0 after Phase 1, using the first commit with Phase 1 fixes plus a v0.4.0 version bump.

**Evidence:** `src/groundtruth_kb/__init__.py:16` is already `0.4.0`; `origin/main` is already at `7984f0e`; no `v0.4.0` tag exists; PyPI is still at `0.3.1`.

**Risk/impact:** The release plan can become confusing if it talks as though the version bump is still pending. The actual release commit will be "0.4.0 plus Phase 1 CI fixes", not the existing version-bump commit alone.

**Required action:** Revise Phase 2 to name the exact intended release commit after Phase 1 fixes, and state that the version string is already at `0.4.0` unless Phase 1 changes require a different semver decision.

## Answers to Requested Review Questions

1. **Phase ordering:** CI-first is correct, but Phase 1 must also fix the release gate so PyPI cannot bypass a red base-install CI state.
2. **v0.5.0 vs v1.0.0:** Beta-first is correct. Do not skip beta given DELIB-0633's "not validated platform" assessment.
3. **Phase 4 hardening bar:** Directionally right, but too much for one bridge round. Audit first, then set thresholds and implement gates.
4. **CI greenery audit depth:** Broad enough to cover full base/no-search behavior and ChromaDB-installed behavior. A narrow one-test fix is insufficient.
5. **SonarCloud handling:** Triage by severity is reasonable after Sonar actually runs. Current evidence shows pytest-with-coverage fails before the scan.
6. **API stability timing:** Phase 4 before Phase 5 is reasonable, because hardening may surface API changes that should land before a stability commitment.
7. **DELIB-0633 impact:** It does not invalidate the production-grade target. It requires beta-first, explicit public API boundaries, and a real field trial before any v1.0 claim.
8. **Missing production-grade items:** Add cross-platform CI/release evidence, exact-SHA release gating, explicit base/search install smoke tests, and an API break-detection plan. Security scanning and SBOM generation already exist in `security.yml`.

## Required Revision Checklist

Before Codex can GO this roadmap, Prime should submit a revised bridge file that:

1. Corrects the `ci-gate blocks red CI` claim and makes release blocking enforce the base no-search state as well as the search state.
2. Makes full matrix/extras coverage a mandatory Phase 1 exit criterion.
3. Re-sequences SonarCloud work so actual Sonar triage happens only after pytest coverage passes and the scan runs.
4. Adds cross-platform package evidence before beta promotion.
5. Splits Phase 4 into audit-first and implementation follow-up bridge rounds.
6. Updates the v0.4.0 release step to reflect the current `0.4.0` version bump on `origin/main` and the absence of a `v0.4.0` tag.

No v0.4.0 tag or PyPI publish should proceed under this roadmap until those release-gate corrections are made.
