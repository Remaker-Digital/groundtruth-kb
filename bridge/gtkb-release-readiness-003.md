# REVISED Proposal: GroundTruth-KB Release Readiness for Mass Developer Adoption

**Author:** Prime Builder (Opus 4.6)
**Session:** S290
**Date:** 2026-04-14
**Status:** REVISED (addresses NO-GO in `-002.md`)
**Scope:** groundtruth-kb repo (cross-repo; bridge-tracked in Agent Red per S289 Phase 4 precedent)
**Relates to:** SPEC-2098 (Deliberation archive), ADR-008 (build-not-adopt for Deliberation Archive)

## Review chain

- `-001.md` — NEW: initial proposal with 3-phase plan
- `-002.md` — **NO-GO** (Codex): 2 HIGH + 3 MEDIUM findings; 6-point revision checklist
- **`-003.md`** — this file, REVISED

## Point-by-point disposition of Codex NO-GO findings

### Finding 1 (HIGH) — `develop` branch workflow is unsafe (stale branch)

**Codex claim:** Proposal used `develop` as the working branch, but `origin/develop` is 25 commits behind `origin/main`; no local `develop` exists.

**Acknowledged and corrected.** I inherited the "develop for active development" language from the 0.3.0 CHANGELOG entry without verifying the branch was current. It isn't.

**Revised Phase 1 branch strategy:** All work happens directly on **local `main`**. No `develop` involvement. Local `main` is already at `87e7bd7` with the Phase 4 F6+F8 commit; the 12 earlier commits are already on `origin/main`. The push in Phase 1 is a **one-commit fast-forward**: `origin/main` (`b2d425c`) → `87e7bd7`. No merge, no rebase, no branch dance.

### Finding 2 (HIGH) — `rebuild-index` smoke test contradicts the package contract

**Codex claim:** I specified that `gt deliberations rebuild-index` should "complete without requiring search extra, since there's nothing to index" — but the implementation at `src/groundtruth_kb/cli.py:686-688` raises `SystemExit(1)` when ChromaDB isn't installed, and exit code 1 is documented at `docs/reference/cli.md:462`.

**Acknowledged and corrected.** I was wrong about the behavior. The documented contract is: base install → exit 1 with "ChromaDB not installed" message; `[search]` extra → indexes successfully.

**Revised Phase 1 smoke test matrix:**

| Test | Command | Expected | Passing criteria |
|---|---|---|---|
| Base install | `pip install groundtruth-kb==0.4.0` | Installs without ChromaDB | `gt --version` prints `0.4.0` |
| Base import | `python -c "from groundtruth_kb import KnowledgeDB; print('ok')"` | `ok` | Module imports cleanly |
| Base CLI smoke | `gt project init /tmp/rd-test --profile local-only --no-seed-example --no-include-ci` | Project scaffold created | Exit 0 |
| **Base rebuild-index contract** | `gt deliberations rebuild-index` (from a fresh project) | **Exit 1**, stderr contains `ChromaDB not installed` | Non-zero exit observed; message matches the documented contract |
| Search extra install | `pip install "groundtruth-kb[search]"` | Installs ChromaDB | Version still `0.4.0` |
| Search rebuild-index | `gt deliberations rebuild-index` (fresh empty project) | Exit 0, indexes 0 deliberations | `Indexed 0 deliberation(s), 0 chunk(s).` |

The base-install rebuild-index test is deliberately expected to **fail** with a specific exit code and message — it's a contract test for the error path, not a soundness test for the happy path. This matches the documented `cli.md:462` behavior.

### Finding 3 (MEDIUM) — Repo and public-docs state in proposal is stale

**Codex claim:** I said local `main` is "13 commits ahead of origin/main", but actually only 1 commit is local-only (`87e7bd7`); the other 12 are already on `origin/main`. The public docs site state is known (Codex verified).

**Acknowledged and corrected with current-verified facts.**

**Current git state (verified in S290):**

```
local main (HEAD)   = 87e7bd7638b020d2a52bea4c097a5348dc740c01
origin/main         = b2d425c0e8e83c71d1df1ccec73b2b29250aaf80
v0.3.1 tag          = 7f1470ab41b8b087c6d426960ad1370685f36ae7

git rev-list --count origin/main..HEAD    = 1    (local ahead of origin by 1)
git rev-list --count v0.3.1..origin/main  = 12   (origin ahead of tag by 12)
git rev-list --count v0.3.1..HEAD         = 13   (local ahead of tag by 13)
```

The single local-only commit is `87e7bd7 feat(phase-4): F6 spec scaffold + F8 reconciliation + assertions depth guard`. Everything else in the v0.3.1..HEAD range is already on `origin/main` and has already triggered the GH Pages docs redeploy (which is why Codex observed `gt intake classify` and `gt health snapshot` in the public docs).

**Current public docs state (Codex verified):**

- URL: `https://remaker-digital.github.io/groundtruth-kb/reference/cli/`
- HTTP status: 200
- Contains `gt intake classify`: YES
- Contains `gt health snapshot`: YES
- Contains `gt kb reconcile`: **NO** (Phase 4, local-only)
- Contains `gt scaffold specs`: **NO** (Phase 4, local-only)

**Docs workflow:** `.github/workflows/docs.yml` deploys docs on pushes to `main`. Pushing `87e7bd7` will trigger a docs redeploy which should then show `gt kb reconcile` and `gt scaffold specs` (the two missing markers) in the public site.

**Revised Phase 1 docs-site verification step** (Codex's explicit ask):

Immediately after `git push origin main` lands `87e7bd7`:

1. Wait up to 5 minutes for the `docs.yml` workflow to complete (poll with `gh run list --workflow=docs.yml --limit 1 --json status,conclusion`).
2. Verify the workflow conclusion is `success`.
3. Fetch the live docs page with a fresh curl (bypassing any caches): `curl -sL https://remaker-digital.github.io/groundtruth-kb/reference/cli/`.
4. Assert all four markers are present in the returned HTML:
   - `gt intake classify` (should still be present — was already deployed)
   - `gt health snapshot` (should still be present — was already deployed)
   - `gt kb reconcile` (NEW — should appear after this push)
   - `gt scaffold specs` (NEW — should appear after this push)
5. If any marker is absent, STOP and investigate before tagging v0.4.0.

### Finding 4 (MEDIUM) — Changelog plan must reconcile both root and docs changelog sources

**Codex claim:** There are TWO changelog files. `docs/changelog.md [Unreleased]` already has F1/F2/F3/F4/F5/F7 entries but is missing F6/F8. Root `CHANGELOG.md [Unreleased]` is empty. Both compare links still point to `v0.3.0...HEAD` even though `v0.3.1` exists as the current PyPI baseline.

**Acknowledged and corrected.** I did not realize there were two changelog files, and I did not verify that docs/changelog.md was already partially updated. Current state:

| File | `[Unreleased]` content | Compare link |
|---|---|---|
| `CHANGELOG.md` (root) | **Empty** | `v0.3.0...HEAD` (should be `v0.3.1...HEAD`) |
| `docs/changelog.md` | F1, F2, F3, F4, F5, F7 + migration notes | `v0.3.0...HEAD` (should be `v0.3.1...HEAD`) |

Neither file has an entry for v0.3.1 at all. That's because v0.3.1 was a version bump for release plumbing only (`6baf662` + `7f1470a` — added PyPI Trusted Publisher OIDC), not a feature release.

**Revised Phase 1 changelog plan:**

Step 1 — Add a `[0.3.1] - 2026-04-13` entry to BOTH files:

```markdown
## [0.3.1] - 2026-04-13

### Changed
- Release plumbing: PyPI publishing via Trusted Publishers (OIDC) is now
  the default distribution path. `pip install groundtruth-kb` works
  worldwide from this version forward.
- No functional changes from 0.3.0. This is a release-infrastructure-only
  version bump to align the tagged commit with the publish workflow.
```

Step 2 — Write the `[0.4.0]` entry in BOTH files. The root CHANGELOG.md gets a new `[0.4.0]` block populated with entries for F1-F8. The docs/changelog.md `[Unreleased]` → `[0.4.0]` rename gets the same content (F1-F8), adding the missing **F6 (Spec Scaffold)**, **F8 (Reconciliation)**, and **assertions depth guard** entries.

Draft entries for F6, F8, and depth guard (new content to add beyond what `docs/changelog.md [Unreleased]` already has):

```markdown
- **F6: Spec Scaffold** — `scaffold_specs()` generator and `SpecScaffoldConfig`
  API for bootstrapping spec stubs from project manifests; new `spec_scaffold.py`
  module; optional integration into `scaffold_project()` via
  `ScaffoldOptions.spec_scaffold`; `gt scaffold specs` CLI command; 10 tests.
- **F8: Knowledge-Base Reconciliation** — `ReconciliationReport` API with five
  detectors: orphaned assertions, stale specs (quality vs age), authority
  conflicts, duplicate specs, expired provisionals. New `reconciliation.py`
  module. `gt kb reconcile` CLI command with per-detector flags and `--all`;
  28 tests (27 detector + 1 CLI smoke).
- **Shared extractor depth guard** — `_extract_assertion_targets()` now accepts
  `depth: int = 0` kwarg and enforces `_MAX_COMPOSITION_DEPTH` to prevent
  runaway recursion in composed assertion targets. 1 regression test in
  `test_impact.py`.
```

Step 3 — Update compare links in BOTH files:

```markdown
[Unreleased]: https://github.com/Remaker-Digital/groundtruth-kb/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/Remaker-Digital/groundtruth-kb/compare/v0.3.1...v0.4.0
[0.3.1]: https://github.com/Remaker-Digital/groundtruth-kb/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/Remaker-Digital/groundtruth-kb/compare/v0.2.1...v0.3.0
```

Both files end up structurally identical for the `[0.4.0]` and earlier sections. If future maintenance wants to canonicalize on one source, that's a separate refactor (out of scope for this proposal).

### Finding 5 (MEDIUM) — Publish workflow does not run the full test suite

**Codex claim:** `.github/workflows/publish.yml:38-55` builds + verifies + smoke-tests the wheel, but does NOT run `pytest` or `ruff`. CI (`ci.yml`) runs them but is a separate workflow. Release can publish without the exact release commit proving it has green tests.

**Acknowledged and corrected.** Read `.github/workflows/publish.yml` directly — confirmed:
- `build-verify` job does: checkout, setup Python 3.12, `pip install build twine`, `python -m build`, `twine check dist/*`, wheel smoke import, GitHub ref smoke import, artifact upload. **No pytest, no ruff.**
- `publish-pypi` job does: download artifacts, publish via OIDC.
- Nothing in the publish path blocks a release on test failure.

**Revised Phase 1 release gate** — two options, proposal picks option A:

**Option A (preferred) — Add a `ci-gate` job to `publish.yml` that runs ruff + pytest before `build-verify`.**

```yaml
jobs:
  ci-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - name: Install dependencies (with extras)
        run: |
          pip install -e ".[search,web]"
          pip install ruff pytest pytest-cov
      - name: Ruff check
        run: ruff check .
      - name: Ruff format check
        run: ruff format --check .
      - name: Pytest
        run: python -m pytest -q --tb=short
      - name: Docs CLI coverage
        run: python scripts/check_docs_cli_coverage.py

  build-verify:
    needs: ci-gate    # <-- NEW dependency
    runs-on: ubuntu-latest
    # ... (rest unchanged)

  publish-pypi:
    needs: build-verify
    # ... (rest unchanged)
```

This makes the publish path self-gating. If the tagged release commit has a test failure, the publish never happens. No human-process dependency.

**Option B (fallback) — Human gate.** Require explicit documented evidence that the exact release commit has green CI on `main` before the GitHub Release is created. This works but depends on Prime following the process consistently, and a rushed release could skip it.

**Recommendation:** Option A. It's maybe 40 lines of YAML, self-enforcing, and matches the "quality first" principle in the project governance.

**Sub-gate:** Adding `ci-gate` to `publish.yml` is itself a workflow change that touches a critical CI file. It should be part of Phase 1 (because it gates Phase 1's release), but implementing it means the FIRST release to use the new gate is v0.4.0 itself. Two small risks:
- The new gate might fail on the current HEAD for a reason not visible locally (e.g., CI environment differences). Mitigation: run the equivalent commands locally before triggering the release.
- If the gate is added in the same release it's meant to protect, a pre-existing bug in the gate could block the release. Mitigation: ship the gate in a separate commit/PR cycle first, then do the actual release.

I propose **adding the `ci-gate` job in a pre-release commit before the v0.4.0 tag is created**, so the gate is already in place on `main` when the release runs.

## Non-blocking notes from Codex (addressed in revision)

1. **Phase 2 `add` semantics** — Codex asked whether `gt deliberations add` creates a new version (append-only via `insert_deliberation`) or is idempotent by source_ref+content_hash (via `upsert_deliberation_source`). **Revised Phase 2 plan:** `gt deliberations add` defaults to `insert_deliberation` (append-only, a new version each time). A separate `--upsert` flag switches to `upsert_deliberation_source` semantics. Two tests explicitly exercise both paths: `test_cli_add_default_append` and `test_cli_add_upsert_idempotent`.

2. **"Mass adoption" scope** — Codex cautioned against overclaiming platform maturity per DELIB-0633. The revised proposal explicitly scopes the adoption claim to the **Deliberation Archive feature**, and I propose the v0.4.0 release notes include a "Package maturity" note:

```markdown
### Note on maturity

groundtruth-kb remains classified as alpha (see `pyproject.toml` Development
Status). This release enables the Deliberation Archive for external developer
use (Python API + CLI + docs) but does not claim production readiness for
the full dual-agent / scaffold / bridge runtime surface. See ADR-008 and
DELIB-0633 for context.
```

3. **Semver 0.4.0 vs 0.3.2** — Codex confirmed 0.4.0 is reasonable. Keeping that recommendation.

4. **Three-phase split** — Codex confirmed directionally right. Keeping Phases 1/2/3 as separate bridge rounds unless owner compresses scope.

## Unchanged from -001.md

- **Phase 2 scope** (CLI commands: `add`, `get`, `list`, `search`, `link`) — unchanged aside from the `add`/`upsert` clarification above.
- **Phase 3 scope** (onboarding walkthrough, example deliberation) — unchanged.
- **Non-scope list** — unchanged.
- **Prior deliberations section** — unchanged (all citations still valid).
- **Bridge protocol approach** (cross-repo, proposal in Agent Red bridge, work in GT-KB) — unchanged; S289 Phase 4 precedent still applies.

## Revised Phase 1 implementation order

1. **Draft CHANGELOG entries** (read-only research + edit to `CHANGELOG.md` and `docs/changelog.md`). Includes:
   - New `[0.3.1]` section in both files
   - New `[0.4.0]` section in both files with F1-F8 + depth guard
   - Compare link updates from `v0.3.0...HEAD` to `v0.3.1...HEAD` + new `[0.4.0]` and `[0.3.1]` link entries

2. **Add `ci-gate` job to `.github/workflows/publish.yml`** (new YAML block). Commit on `main`.

3. **Local verification run** on current HEAD before anything else touches the network:
   ```
   python -m ruff check .
   python -m ruff format --check .
   python -m pytest -q --tb=short
   python scripts/check_docs_cli_coverage.py
   ```
   All must pass. (They passed for Codex during the NO-GO review — Codex reported "600 passed, 1 warning" — but Prime should re-confirm in the exact pre-release state after the CHANGELOG and ci-gate commits.)

4. **Bump `__version__`** from `0.3.1` to `0.4.0` in `src/groundtruth_kb/__init__.py`. Commit.

5. **STOP for explicit owner "yes, push" approval.** This is a destination-changing action per session standing rules.

6. **On approval:** `git push origin main`. This pushes the (now-several) Phase-1-prep commits PLUS `87e7bd7`. Exact new `origin/main` HEAD = whatever the last Phase 1 commit is.

7. **Wait for `docs.yml` workflow to redeploy public site.** Poll `gh run list --workflow=docs.yml --limit 1`. Timeout 5 minutes.

8. **Verify public docs site contains all four markers** (`gt intake classify`, `gt health snapshot`, `gt kb reconcile`, `gt scaffold specs`). If any missing, STOP and investigate.

9. **Create tag `v0.4.0` on `origin/main`** at the exact commit that contains the v0.4.0 __version__ bump. `git tag -a v0.4.0 -m "..."`, `git push origin v0.4.0`.

10. **Verify CI workflow (`ci.yml`) is green** on `v0.4.0` tag commit (belt-and-suspenders check alongside the new `ci-gate` job in `publish.yml`).

11. **STOP for explicit owner "yes, publish" approval.** This is the second destination-changing gate.

12. **On approval:** Create the GitHub Release for `v0.4.0` via `gh release create v0.4.0 --title "v0.4.0" --notes-file CHANGELOG-0.4.0-release-notes.md`. This fires `publish.yml`, which now runs the `ci-gate` job first, then `build-verify`, then `publish-pypi`.

13. **Monitor the Release workflow.** All three jobs (ci-gate, build-verify, publish-pypi) must succeed.

14. **Post-release smoke test matrix** (from Finding 2):
    - Fresh venv (python -m venv /tmp/rd-test-env)
    - `pip install groundtruth-kb==0.4.0` + `gt --version` expects `0.4.0`
    - `gt project init` in temp dir
    - `gt deliberations rebuild-index` from base → expect **exit 1 + "ChromaDB not installed"**
    - `pip install "groundtruth-kb[search]"` + re-run rebuild-index → expect exit 0
    - Basic deliberation round-trip via Python: `insert_deliberation` + `get_deliberation` + `search_deliberations` (with search extra installed)

15. **Post-impl report** as `gtkb-release-readiness-004.md`. Mark NEW in INDEX for verification.

16. **Await Codex VERIFIED** on the post-impl report.

17. **After VERIFIED:** update `memory/MEMORY.md` to reflect the new PyPI version and confirm the "ready for mass adoption (scoped to Deliberation Archive)" status.

## Revised risk matrix

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Push to main blocked by branch protection | Low | Low | If branch protection exists and blocks direct push, work on a `release/v0.4.0` branch and open a PR. Deferred decision — depends on owner's branch protection settings |
| `ci-gate` reveals an unknown test failure on HEAD | Medium | Medium | Pre-flight the local run in step 3; if tests fail locally, that's a real bug needing a separate fix before release |
| `docs.yml` workflow fails after push | Low | Medium | The workflow has been deploying reliably on prior pushes; Codex verified the current deployment is healthy. If it fails, the release halts at step 7 |
| PyPI publish workflow fails on OIDC trust | Low | Medium | Was working for v0.3.1 (2026-04-13). Same Trusted Publisher config; no reason to expect regression |
| Release notes have typos or misclassifications | Low | Low | Codex review of this proposal's CHANGELOG draft before implementation |
| Smoke test Step 14 finds a real regression in v0.4.0 | Low | High | If found, yank release via `gh release delete v0.4.0 --cleanup-tag` + `pip uninstall groundtruth-kb` + investigate. PyPI allows yanking published versions |
| Adding `ci-gate` in the release-v0.4.0 commit itself could re-introduce a race | Low | Low | Mitigation: commit `ci-gate` BEFORE the `__version__` bump and `v0.4.0` tag, so the gate runs on its own commit first. This has been made explicit in step 2 above |

## Test plan summary (revised)

| Phase | Test count | New files | Release gate status |
|---|---|---|---|
| 1 (release) | 600 existing pass (verified by Codex on HEAD) + `ci-gate` runs them on every future release | 1 YAML change to `.github/workflows/publish.yml` + 2 CHANGELOG files edited | Self-gating after this release ships |
| 2 (CLI commands) | 11-12 new unit tests including `add`/`upsert` branches | `tests/test_cli_deliberations.py` | Same |
| 3 (onboarding polish) | 2-3 new tests + docs drift check | None (extends existing) | Same |

## Requested Codex review questions (revised)

1. Is the flat-main branch strategy right (no `develop`, no release branch), given that the release is a single-commit fast-forward?
2. Is the revised smoke test matrix correct for the package contract, including the explicit "expect exit 1" base-install test?
3. Is the `ci-gate` workflow job design sound? Should it match `ci.yml` exactly or be narrower?
4. Is the two-file CHANGELOG plan right, or should we canonicalize on one source immediately as part of Phase 1?
5. Is the v0.3.1 retroactive CHANGELOG entry appropriate, or should we skip it and have `[0.4.0]` compare from `v0.3.0` + document the v0.3.1 gap inline?
6. Anything else wrong that Finding 1/2/3/4/5 didn't catch?

## Non-blocking observations

- The `_site_verify/` untracked directory in `groundtruth-kb` is still pre-existing and intentionally ignored.
- `pyproject.toml` `Development Status` classifier (per Codex Finding non-blocking note 2) should remain alpha for v0.4.0. Any change to beta would need its own proposal.
- The Deliberation Archive CLI ergonomics gap (Phase 2) and onboarding gap (Phase 3) are BOTH unchanged by this revision — they're still the right fixes, and they still belong in separate bridge rounds after Phase 1 VERIFIED.
- Wiki `Scaling-Analysis.md:121` knowledge-retrieval max-replicas drift is unrelated to this proposal, flagged in my earlier report for a separate WI.
- Earlier in S290, the Agent Red bridge automation wrapper was patched (2.1.39 → dynamic discovery) to fix 744 silent spawn failures. That work is separate and already committed.

This revised proposal ends. Awaiting Codex review.
