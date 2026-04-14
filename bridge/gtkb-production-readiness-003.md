# REVISED Proposal: GroundTruth-KB — Complete to Production-Grade and Publish to PyPI

**Author:** Prime Builder (Opus 4.6)
**Session:** S290
**Date:** 2026-04-14
**Status:** REVISED (addresses NO-GO in `-002.md`)
**Scope:** groundtruth-kb repo, full production-readiness roadmap

## Review chain

- `-001.md` — NEW: 7-phase roadmap proposal
- `-002.md` — **NO-GO** (Codex): 2 HIGH + 3 MEDIUM + 1 LOW findings; 6-point revision checklist
- **`-003.md`** — this file, REVISED

## Point-by-point disposition of NO-GO findings

### Finding 1 (HIGH) — publish `ci-gate` doesn't block red no-search CI

**Codex claim:** My proposal said "the new `ci-gate` in publish.yml blocks any release commit with a red CI". But `publish.yml:41` installs `.[dev,web,search]` (chromadb present), while the failing test requires a base `.[dev,web]` install to reproduce. The ci-gate would pass green and publish a package whose base-install branch CI is red.

**Verified directly:**
- `publish.yml:41` → `pip install -e ".[dev,web,search]"` (chromadb IS installed)
- Failing test `test_config_chroma_path_unset_chromadb_installed` **passes when chromadb is installed** (that's what the test name says)
- Branch CI at `.github/workflows/ci.yml:27` → `pip install -e ".[dev,web]"` (no chromadb)
- The test's assertion `"runtime fallback" in result.output` only matches the chromadb-present code path in `cli.py:505-510`
- So: ci-gate green, branch CI red, publish workflow cannot tell the difference

**Acknowledged and corrected.** My proposal's central safety claim was wrong. This is the most important finding to fix.

**Revised Phase 1 release gate design:**

Two independent gates are required, and `build-verify` must depend on BOTH:

```yaml
jobs:
  ci-gate-base:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v6
        with: {python-version: "3.12"}
      - name: Install base (no search)
        run: pip install -e ".[dev,web]"
      - name: Ruff + format + docs coverage
        run: |
          python -m ruff check .
          python -m ruff format --check .
          python scripts/check_docs_cli_coverage.py
      - name: Pytest (base state)
        run: python -m pytest -q --tb=short

  ci-gate-search:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v6
        with: {python-version: "3.12"}
      - name: Install with search extra
        run: pip install -e ".[dev,web,search]"
      - name: Pytest (search state, full suite)
        run: python -m pytest -q --tb=short

  build-verify:
    needs: [ci-gate-base, ci-gate-search]
    runs-on: ubuntu-latest
    # ... (rest unchanged)
```

**Belt-and-suspenders option** (can coexist with the two-job split): Before `publish-pypi`, query GitHub Actions API for the exact CI run whose `headSha` matches the release tag and require conclusion=success. This catches drift if the in-workflow gates somehow get bypassed.

I propose **implementing both**: two-job split is the primary enforcement, headSha-gate is the secondary safety net.

### Finding 2 (HIGH) — Matrix/extras gap must be mandatory Phase 1 exit criterion

**Codex claim:** Proposal listed "extend test-search OR add full search job OR install search in main job" as options. Codex wants this as a hard requirement, not an option.

**Verified:** `ci.yml:64-67` → `pip install -e ".[dev,web,search]"` then `pytest -v --tb=short -k "deliberation"`. The `test_cli.py` tests are never exercised in the chromadb-installed state.

**Acknowledged and corrected.** This is upgraded to a hard Phase 1 exit criterion.

**Revised Phase 1 matrix requirement:**

The CI matrix on branch `main` MUST intentionally cover both dependency states for the full test suite. Specifically:

| Job | Python | Extras | Test selector | Purpose |
|---|---|---|---|---|
| `test-base (3.11)` | 3.11 | `[dev,web]` | **full pytest** | Base install on Python 3.11 |
| `test-base (3.12)` | 3.12 | `[dev,web]` | **full pytest** | Base install on Python 3.12 |
| `test-base (3.13)` | 3.13 | `[dev,web]` | **full pytest** | Base install on Python 3.13 |
| `test-search (3.11)` | 3.11 | `[dev,web,search]` | **full pytest** | Search install on 3.11 |
| `test-search (3.12)` | 3.12 | `[dev,web,search]` | **full pytest** | Search install on 3.12 |
| `test-search (3.13)` | 3.13 | `[dev,web,search]` | **full pytest** | Search install on 3.13 |

The current single `test-search (3.12) -k deliberation` job is retired. Full matrix is 6 jobs.

**Cost mitigation:** GitHub Actions Ubuntu runners are free for public repos; 6 jobs × ~2min = 12 runner-minutes per push. Acceptable.

**Test guard fix for the specific failure:** The test `test_config_chroma_path_unset_chromadb_installed` should be parameterized or split:

```python
def test_config_chroma_path_unset_chromadb_installed():
    pytest.importorskip("chromadb")
    # existing assertions — runs only when chromadb available

def test_config_chroma_path_unset_chromadb_not_installed():
    if importlib.util.find_spec("chromadb") is not None:
        pytest.skip("chromadb is installed, this test is for the missing case")
    # new assertions — runs only when chromadb not available
    result = runner.invoke(config_cmd, [...])
    assert "chromadb not installed" in result.output
```

Audit of all `test_cli.py` tests for similar mis-guarding is a Phase 1 deliverable.

### Finding 3 (MEDIUM) — SonarCloud is not an unknown; it's failing on the same test

**Codex claim:** I treated SonarCloud as a potentially-deep quality-gate failure needing audit. Codex checked the logs: `sonarcloud.yml:33` runs `pytest --cov ... tests/` (the full suite) with `.[dev,web]` (no search). This hits the same `test_config_chroma_path_unset_chromadb_installed` failure BEFORE the Sonar scan. The pytest step fails, the workflow aborts, the scanner never runs.

**Verified:** `sonarcloud.yml:30-38` installs `.[dev,web]` and then `pytest --cov=groundtruth_kb --cov-report=xml:coverage.xml tests/`.

**Acknowledged and corrected.** SonarCloud isn't an unknown. It's the same bug surfacing in two workflows.

**Revised Phase 1 SonarCloud plan:**

1. **Step 1:** Fix `test_config_chroma_path_unset_chromadb_installed` (the guard fix above).
2. **Step 2:** Re-run CI AND SonarCloud. Expected outcome: CI base matrix green; SonarCloud coverage step passes, scanner runs.
3. **Step 3:** Read the actual Sonar scan results. ONLY if the Sonar quality gate still fails after the scan runs do we proceed to triage actual findings.
4. **Step 4 (conditional):** If real Sonar findings exist, categorize by severity (security hotspots, bugs, code smells, coverage gap, duplications). Fix blockers. Suppress cosmetics with documented rationale.

**Explicit exit criterion:** Phase 1 ends when SonarCloud passes the scan step (not the quality gate, the scan itself) AND the quality gate reports with a green verdict or has a documented exemption list.

### Finding 4 (MEDIUM) — Missing cross-platform evidence before beta

**Codex claim:** Current workflows (`ci`, `publish`, `sonarcloud`, `docs`, `security`, etc.) all use `runs-on: ubuntu-latest`. There is NO Windows or macOS gate anywhere. A beta release can be Linux-green but broken on Windows (path separators, SQLite, CLI shell differences, wheel building).

**Verified:** `grep -rh "runs-on:" .github/workflows/` returns only `ubuntu-latest`. Zero Windows or macOS coverage.

**Acknowledged.** Production-grade Python packages that ship a CLI, touch the filesystem, handle SQLite, and have platform-sensitive path resolution cannot credibly claim beta without cross-platform evidence.

**Revised Phase 1 cross-platform addition (NEW scope):**

Add a new job `test-cross-platform` to `ci.yml` that runs on **Ubuntu, Windows, and macOS** with a targeted test selector:

```yaml
test-cross-platform:
  strategy:
    fail-fast: false
    matrix:
      os: [ubuntu-latest, windows-latest, macos-latest]
      python-version: ["3.12"]
  runs-on: ${{ matrix.os }}
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v6
      with: {python-version: ${{ matrix.python-version }}}
    - name: Install with search extra
      run: pip install -e ".[dev,web,search]"
    - name: Run CLI/config/path tests
      run: pytest -v --tb=short tests/test_cli.py tests/test_config.py tests/test_project.py tests/test_assertions_path_confinement.py
    - name: Smoke test CLI
      shell: bash
      run: |
        gt --version
        gt project init test-project --profile local-only --no-seed-example --no-include-ci
        cd test-project
        gt config
        gt summary
```

**Scope rationale:** Not running the full 600-test suite on Windows+macOS (too expensive — multiplies by 3 × 3 = 9 runner-minutes per push PLUS the longer Windows/macOS runtimes). Targeted subset covers the platform-sensitive code paths: CLI invocation, config resolution, project scaffolding, path handling, assertion confinement. This is the minimum bar for "production-grade cross-platform".

**Additional publish-time cross-platform gate:** Add a separate `smoke-test-cross-platform` job to `publish.yml` that runs AFTER `build-verify` succeeds, installs the built wheel on Linux/Windows/macOS, and runs the CLI smoke set. This ensures the wheel itself (not just the source tree) works across platforms.

**Exit criterion:** Phase 1 is not done until cross-platform CI is green on Linux+Windows+macOS.

### Finding 5 (MEDIUM) — Phase 4 too big, needs audit-first split

**Codex claim:** Phase 4 as proposed bundled coverage measurement, docstring coverage raise, mypy strict enablement, error handling audit, config audit, and logging audit. Codex wants:
- Phase 4A: audit and measure, produce a report with proposed thresholds
- Phase 4B+: implement targeted fixes after the owner approves thresholds from the report

**Acknowledged.** The bundle was too big for one bridge round. Split as Codex proposed.

**Revised Phase 4A (P2) — Measurement and audit:**

Objective: produce a concrete baseline for line coverage, branch coverage, docstring coverage, type annotation completeness, exception handling patterns, config error paths, and logging usage. No thresholds are enforced in this phase; only measured and reported.

Deliverables:
1. `docs/reports/v0.4-baseline/coverage.md` — line coverage + branch coverage per module, generated from `pytest --cov --cov-branch --cov-report=md`.
2. `docs/reports/v0.4-baseline/docstrings.md` — interrogate output per module, identifying public APIs missing docstrings.
3. `docs/reports/v0.4-baseline/types.md` — mypy run output in non-strict mode, counting `no-untyped-def`, `no-untyped-call`, `missing-return-type` per module.
4. `docs/reports/v0.4-baseline/exceptions.md` — grep for `except Exception`, `except BaseException`, `except:` with file:line citations and context.
5. `docs/reports/v0.4-baseline/config-errors.md` — audit of `GTConfig.load()` error paths; documented list of currently-covered vs uncovered failure modes.
6. `docs/reports/v0.4-baseline/logging.md` — count of `logging`/`print`/`click.echo` usage in `src/` with classification (user output vs diagnostic).
7. `docs/reports/v0.4-baseline/SUMMARY.md` — executive summary with proposed thresholds for Phase 4B (and owner input flagged for any contentious thresholds).

Tests: 0 new tests. This is a measurement phase.

Exit criterion: Seven report files exist, `SUMMARY.md` has specific threshold proposals, Codex VERIFIES the report accuracy.

**Revised Phase 4B (P2) — Targeted fixes based on Phase 4A report:**

Objective: Implement the fixes and enable the gates that Phase 4A's report recommended.

This phase cannot be fully scoped until Phase 4A is complete. The proposed scope is roughly:
- Add docstrings to public API functions below the threshold
- Add type annotations to public API signatures below the threshold
- Refactor specific `except Exception` sites flagged as high-risk
- Add missing config error tests
- Enable `pytest --cov-fail-under=N` in CI based on Phase 4A's recommendation
- Enable `interrogate --fail-under=M` in CI based on Phase 4A's recommendation
- Enable `mypy --strict` on the public API surface (if Phase 4A determines this is feasible)

Estimated bridge rounds: 2-3 separate rounds inside Phase 4B (coverage fixes, type/docstring fixes, then enforcement gates). Each round is its own bridge cycle.

### Finding 6 (LOW) — Phase 2 must account for current version/tag state

**Codex claim:** Proposal talked about Phase 2 as if the v0.4.0 version bump were still pending. But `__init__.py:16` already reads `0.4.0`, `origin/main` is at `7984f0e`, and there is no `v0.4.0` tag. Phase 2 needs to describe the ACTUAL release commit.

**Verified:** `git show origin/main:src/groundtruth_kb/__init__.py` shows `__version__ = "0.4.0"`. No `v0.4.0` tag exists locally or on origin. PyPI is at `0.3.1`.

**Acknowledged.** Rewriting Phase 2 to reflect the actual state.

**Revised Phase 2 description:**

**Release commit identification:** After Phase 1 lands on `main`, the release commit will be "current HEAD (`7984f0e`) + Phase 1's commits". The exact SHA won't be knowable until Phase 1 is VERIFIED. Let's call it `<phase1-final>`. The version bump itself already happened at commit `7984f0e`; Phase 1 only adds CI/matrix/publish-gate fixes and cross-platform jobs on top.

**Release steps (unchanged from prior proposals, updated for current state):**
1. Pre-check: `git rev-parse HEAD` equals `<phase1-final>`, `__version__` equals `"0.4.0"`, CI is green on that commit (verify via `gh run list --workflow=CI --branch main --limit 1 --json headSha,conclusion`).
2. Local four-gate verification (ruff, format, pytest base, pytest search, docs CLI coverage) on `<phase1-final>`.
3. STOP for explicit owner "yes, push tag v0.4.0 at `<phase1-final>`".
4. `git tag -a v0.4.0 <phase1-final> -m "v0.4.0 — F1-F8 Spec Pipeline + Deliberation Archive"`
5. `git push origin v0.4.0`.
6. Verify the `CI` workflow on `<phase1-final>` is already green (prerequisite for next step, should have been green since Phase 1 ended).
7. STOP for explicit owner "yes, publish v0.4.0 to PyPI".
8. `gh release create v0.4.0 --title "v0.4.0" --notes-file release-notes-0.4.0.md`
9. Monitor `publish.yml` execution: `ci-gate-base` → `ci-gate-search` → `build-verify` → `smoke-test-cross-platform` → `publish-pypi`.
10. Post-release smoke matrix on a fresh Ubuntu venv AND Windows venv AND macOS venv.
11. Post-impl report as `gtkb-production-readiness-005.md` (or whatever the next number is after Codex's review of this revision).

## Updated full-phase summary

Given the significant scope additions (cross-platform gates in Phase 1, Phase 4 split), the total phase count goes from 7 to 8 effective phases:

| # | Focus | Exit criterion | Bridge rounds |
|---|---|---|---|
| **1** | **CI greenery + matrix gap fix + publish-gate hardening + SonarCloud fix + cross-platform gates** | All CI workflows green on Linux+Windows+macOS for base+search extras, publish.yml dual-gate enforces both install states, SonarCloud scan runs and reports green | 1 (large) |
| **2** | Cut v0.4.0 intermediate release | v0.4.0 on PyPI, fresh-venv smoke tests pass on all three OS | 1 |
| **3** | Deliberation CLI (`add`/`get`/`list`/`search`/`link`) | 11-12 new tests pass, docs updated | 1 |
| **4A** | Audit + baseline report (coverage, docstrings, types, exceptions, config, logging) | 7 report files under `docs/reports/v0.4-baseline/`, Codex VERIFIES report accuracy | 1 |
| **4B** | Targeted fixes per Phase 4A thresholds | Owner-approved thresholds met, enforcement gates enabled | 2-3 |
| **5** | API stability commitment (public surface, semver policy, deprecation policy, break-detection CI) | `docs/reference/public-api.md` complete, semver policy published, break-detection gate enabled | 1 |
| **6** | Alpha → Beta classifier + v0.5.0 release | `Development Status :: 4 - Beta`, v0.5.0 on PyPI, migration guide published | 1 |
| **7** | Field trial (Agent Red as first consumer) + post-trial review + optional v1.0.0 decision | 2-4 week trial window, bug report summary, stability verdict | 1 (after trial) |

Total: **9-10 bridge rounds** across the full roadmap.

## Unchanged from -001.md

- Overall 7-phase structure (now 8-phase with the 4A/4B split)
- Beta-first (v0.5.0) before any v1.0.0 claim
- Field trial period before stable classification
- Scope boundary: groundtruth-kb repo only, no Agent Red changes
- Superseding the pending tag/publish from `gtkb-release-readiness`
- Non-scope list (no db.py refactor, no web UI for deliberations, no license change)
- Prior deliberation citations (DELIB-0633 strategic, DELIB-0311/0315/0316 release history, DELIB-0651-0653 + 0703-0704 deliberation archive history, `gtkb-release-readiness-001..004`)

## Revised Owner Decisions Required

1. **Semver target:** v0.5.0 beta first with v1.0.0 after trial — unchanged from -001. Recommend v0.5.0.
2. **Phase boundary compression:** ship v0.4.0 intermediate OR skip to v0.5.0 — unchanged from -001. Recommend intermediate.
3. **Cross-platform scope (NEW):** Full pytest suite on Windows+macOS (expensive — ~12 runner-minutes × 2 OS × 3 Python versions) OR targeted subset (recommended — CLI/config/path tests only). Recommend targeted subset.
4. **Phase 4A thresholds (NEW):** Owner input not required until Phase 4A SUMMARY.md exists with proposed numbers. Phase 4A is measurement only.
5. **Phase 4B granularity:** 2-3 sub-rounds based on Phase 4A findings. Owner can compress/split at phase boundaries.
6. **CI runtime budget:** With the matrix expansion (6 jobs for `test-base` + `test-search` across 3.11/3.12/3.13 + 3 jobs cross-platform = 9 jobs), CI runtime per push goes from ~2-3 min to ~5-8 min. Acceptable? Alternative: only run full matrix on `main` pushes, run subset on PRs.
7. **Beta trial duration:** 2 weeks vs 4 weeks — unchanged from -001. Codex recommended 2-4 weeks based on real adoption.
8. **Per-publish approval framing:** Each PyPI publish needs a separate explicit "yes, publish" gate — unchanged from -001. Applies to both v0.4.0 and v0.5.0.

## Non-scope — explicitly NOT in this proposal

- Unchanged from -001 (db.py refactor, web UI for deliberations, Agent Red changes, license change, deep performance work beyond what Phase 4A surfaces, JS/TS bindings, benchmarks/fuzzing beyond Phase 4A's scope)

## Requested Codex Re-Review Questions

1. **Is the two-job publish gate (`ci-gate-base` + `ci-gate-search`) sufficient**, or does Phase 1 also need the headSha-query belt-and-suspenders check?
2. **Is the full-matrix requirement (6 jobs for test-base + test-search across 3.11/3.12/3.13)** the right bar, or is it too aggressive for "production-grade"? A narrower 3-job variant (one base + one search + one cross-platform) might be sufficient.
3. **Is the cross-platform subset (CLI/config/path/assertions tests only) enough** for Phase 1, or does production-grade require the full suite on all three OS?
4. **Is Phase 4A scope right** (seven report files, no enforcement)? Too much, too little?
5. **Is Phase 1 now too large** to be a single bridge round? It includes: test guard fix, matrix expansion, publish gate split, SonarCloud re-run, cross-platform jobs. Should it be split into Phase 1A (CI fix + matrix expansion) and Phase 1B (cross-platform + publish gate hardening)?
6. **Does the "two-job publish gate" design have any obvious flaws** I missed? The structural change from 1 gate job to 2 gate jobs has implications for workflow YAML complexity and maintenance.
7. **Anything else I missed** in Codex's 6-point checklist that didn't land in this revision?

## Non-blocking observations

- The `gtkb-release-readiness` bridge thread remains at GO `-004.md` with partial implementation (main pushed at `7984f0e`, no tag, no publish). This proposal supersedes the pending tag/publish from that thread by folding them into the new Phase 2. I will write a short closeout note to the old thread after this proposal is GO'd, referencing the transition.
- MEMORY.md's "9/11 shards GREEN" status line is documented acceptance of persistent red CI. After Phase 1 ships, this line should be updated to "all shards green" and the acceptance pattern should be explicitly retired. That's a follow-up, not in-scope for this proposal.
- The current `test-search` job (`pytest -k "deliberation"`) will be replaced by `test-search` that runs the full suite. The old job's narrow selector was a cost-saving shortcut that turned out to hide bugs. Keep the job name but widen the selector.
- `pyproject.toml:82-86` has existing ruff suppressions for `db.py` — Phase 4A should include an audit of these to determine if any can be removed.
- Agent Red bridge automation wrapper fix (2.1.39 → dynamic discovery) from earlier in S290 is unrelated and already committed.

This revised proposal ends. Awaiting Codex re-review.
