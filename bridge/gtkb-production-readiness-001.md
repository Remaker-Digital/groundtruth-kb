# Proposal: GroundTruth-KB — Complete to Production-Grade and Publish to PyPI

**Author:** Prime Builder (Opus 4.6)
**Session:** S290
**Date:** 2026-04-14
**Status:** NEW
**Scope:** groundtruth-kb repo, full production-readiness roadmap
**Successor to:** `gtkb-release-readiness-001.md` … `-004.md` (partial execution — main pushed at `7984f0e`, tag/publish blocked on CI failure)
**Relates to:** SPEC-2098 (Deliberation archive), ADR-008, DELIB-0633 (strategic assessment — alpha)

## Owner direction that triggered this proposal

> "Please prepare an implementation proposal to complete GT-KB and make it production-grade and publish to PyPI. Send this to Codex for review."

The owner has expanded scope from the narrow Phase 1 release (which was blocked on a latent CI failure discovered during push verification earlier this turn) to a full production-readiness roadmap ending in a PyPI publish.

## Prior Deliberations

Searches for `groundtruth-kb production ready release`, `gt-kb alpha beta stable semver`, `groundtruth-kb CI failure test`, `gt kb deliberation CLI adoption`, `production-grade Python package classifier`:

- **DELIB-0633** (2026-04-10, Codex strategic assessment): GT-KB is "directionally meeting the right goals", "promising but still alpha", **not yet proven as a repeatable software-factory system across projects**. The Codex verdict was explicit: "not validated platform." The proposal must take this as the starting ceiling, not the starting floor.
- **DELIB-0311/0315/0316** (S251, 2026-04-01): Earlier GT-KB publishing plan review cycle. The decision at the time was "GitHub-installable, not PyPI-published", later reversed by commit `6baf662` (2026-04-13 PyPI Trusted Publishers).
- **DELIB-0331/0332** (S251, 2026-04-01): GT-KB distribution model audit.
- **DELIB-0651/0652/0653** (S279-S283): Deliberation Archive implementation — code is VERIFIED, stable.
- **DELIB-0703/0704** (S282-S283): ChromaDB semantic search — iterated to stable.
- **bridge/gtkb-release-readiness-001.md through -004.md** (current session): Phase 1 release plan, NO-GO and revised, now GO with 5 conditions. Partially implemented (push done, tag/publish blocked).

No prior deliberation has proposed a comprehensive path from alpha to production-grade. No prior deliberation has addressed the "always-red CI" problem. No prior deliberation has set explicit exit criteria for platform maturity.

## Observation — Current state vs production-grade

### What works

| Dimension | State |
|---|---|
| Deliberation Archive core | Stable, 69/69 tests pass, Python API fully functional |
| Spec Pipeline F1-F8 | Feature-complete on HEAD, Codex VERIFIED across S287-S289 |
| Test count | 600 on Python 3.14 (local), ~588 passing on 3.11 matrix |
| Ruff lint | Clean on HEAD |
| Docs method guides | Comprehensive (method 13 = deliberation archive, with Mermaid diagrams + Python API examples) |
| Docs site | Deploys from `main` via `docs.yml` |
| PyPI v0.3.1 | Published via Trusted Publishers OIDC (2026-04-13) |
| Release gate | `ci-gate` job added to publish.yml in this session (commit `879bb0c`) |
| Security | Credential redaction (27 patterns), CodeQL clean, SonarCloud security clean |

### What's broken (blockers)

| Dimension | State | Severity |
|---|---|---|
| **CI main matrix** | **Red for 11+ consecutive commits** (at least since `3db7235`, 2026-04-13) | **HARD BLOCKER** |
| Specific failing test | `tests/test_cli.py::TestConfig::test_config_chroma_path_unset_chromadb_installed` asserts `"runtime fallback"` in output but runs in `.[dev,web]` env (no chromadb). Output is `"(unset — chromadb not installed)"` | Surfaces a matrix / guard bug |
| `test-search` job scope | Only runs `pytest -k "deliberation"`, so the failing `test_cli.py` test is never exercised with chromadb available | Test coverage gap |
| SonarCloud | Fails on `7984f0e` (this turn) and on every prior commit in the range | Unknown root cause yet |

### What's incomplete (production-grade gaps)

| Dimension | Current | Production-grade target |
|---|---|---|
| CLI surface for deliberations | `gt deliberations rebuild-index` only | Full `add`/`get`/`list`/`search`/`link` (from `gtkb-release-readiness-003.md` Phase 2) |
| Start-here walkthrough | Doesn't exercise deliberations hands-on | Walked-through step including `gt deliberations add` |
| Task-tracker example | No deliberation scenario | Seeded deliberation + walkthrough step |
| Package classifier | `Development Status :: 3 - Alpha` in pyproject.toml | `Development Status :: 4 - Beta` minimum |
| Test coverage | Unknown number (SonarCloud may have the number but is currently red) | Measured + reported + published threshold |
| Docstring coverage | ≥ 50% (interrogate check) | ≥ 80% on public APIs |
| API stability commitment | None stated | Explicit "public surface" doc + semver policy |
| Public docs CHANGELOG canonicalization | Two files (root + `docs/`) | Single source OR documented sync rule |
| CI matrix coverage | 3.11/3.12/3.13 with search extra tested only on 3.12/deliberation subset | 3.11/3.12/3.13 full matrix with and without search extra |
| Release gate signal | `ci-gate` added but CI is red, so gate is unusable | `ci-gate` passes end-to-end on release commit |
| Migration guide | Embedded in CHANGELOG | Standalone `docs/migration/0.3-to-0.5.md` (or similar) |

## Deficiency Rationale

**The engineering is substantial, the release plumbing is fragile, and the quality signal is silenced.**

- **The CI has been red for days** and no prior session acted on it. Under the new `ci-gate` added in `gtkb-release-readiness`, a red CI blocks PyPI publication. Without fixing CI, **no release can happen**, period. MEMORY.md's "9/11 shards GREEN" status line is an acceptance of persistent red — that's exactly the pattern that erodes release confidence in an alpha project.
- **The test-guard bug is small but revealing.** A test named `_chromadb_installed` runs in an environment where chromadb is not installed, and the matrix split means nobody's CI exercises the correct state. This is the kind of bug that accumulates in alpha projects and must be audited for production-grade.
- **The CLI surface for the flagship feature (deliberation archive) is one maintenance command.** A developer who finds GT-KB via docs or search and tries `gt deliberations --help` gets one option: `rebuild-index`. That's not a production feature — that's a back-office tool. Production-grade means the primary feature has a primary interface.
- **The alpha classifier is accurate today and wrong by tomorrow's standard.** Upgrading it to Beta without the underlying work is overclaiming; doing the underlying work is what this proposal is about.
- **Two-file CHANGELOG drift** is an ongoing maintenance debt that has already caused one CI cycle this session (docs/changelog.md had F1-F5/F7 but not F6/F8). Either canonicalize or enforce sync programmatically.

None of these are architectural holes. They are execution debt from a project that grew fast, with the deliberation archive and spec pipeline landing in rapid succession on top of an already-alpha foundation.

## Proposed Solution — Seven Phases

Scope ordering is driven by blocker resolution: fix CI first (because nothing else can release until it's green), then ship existing v0.4.0 work (as an intermediate release) to prove the gate works, then fill the production gaps, then cut a beta release.

### Phase 1 (P0, blocker) — Fix CI to green across the matrix

**Objective:** Make `CI` workflow pass on 3.11/3.12/3.13 with and without `search` extra, on a clean commit, with zero tolerance for "expected" failures.

**Scope:**
1. **Fix `test_config_chroma_path_unset_chromadb_installed`:** Either gate it with `pytest.importorskip("chromadb")`, split it into two parameterized tests (one gated on chromadb, one on its absence), or rewrite it to assert the correct output for the actual env. Most likely fix is parameterization: the test name says `_chromadb_installed` so there should also be a companion `_chromadb_not_installed` variant with the correct assertion.
2. **Audit all `test_cli.py` tests for chromadb gating** — this is unlikely to be the only mis-guarded test.
3. **Fix the matrix / extras interaction:** Either extend `test-search` to run the full suite (not just `-k deliberation`) so chromadb-dependent tests everywhere get exercised, or add a `test-search-full` job, or install `[search]` in the main `test` job and skip tests that specifically need the "no chromadb" path.
4. **Audit SonarCloud failure:** Read the SonarCloud report, categorize the failures (security hotspots vs bugs vs code smells vs coverage), and either fix or suppress with documented rationale.
5. **Document in the project:** Add a "Known red signals" section to README or CONTRIBUTING if any failures must remain intentionally acceptable (for example, Python 3.13 incompatibility with a dependency).

**Tests:**
- Re-run CI on the Phase 1 commit. Exit criteria: all matrix jobs green (including `test` × 3 Python versions, `test-search`, `Docs`, `Docs Check`, `Security`, `CodeQL`, `Docstring Coverage`, `SonarCloud`).
- Re-run SonarCloud with documented thresholds. Exit criteria: all thresholds met OR explicit documented exemptions.

**Bridge round:** Dedicated — `gtkb-ci-greenery-001.md` or integrate into Phase 1 of this proposal. Proposed as its own review to limit scope creep.

### Phase 2 (P1) — Cut intermediate release v0.4.0

**Objective:** Ship the F1-F8 Spec Pipeline work to PyPI as a Beta-candidate release, using the now-green CI and the self-gating `ci-gate` job added earlier this session.

**Scope:**
1. After Phase 1 confirms CI green on HEAD, proceed with the tag + publish gates from `gtkb-release-readiness-003.md` Phase 1 steps 9-14:
   - `git tag -a v0.4.0 <sha>` (sha = first commit with Phase 1 fixes + v0.4.0 version bump)
   - `git push origin v0.4.0` (after explicit owner approval)
   - `gh release create v0.4.0 --title "v0.4.0" --notes-file CHANGELOG-0.4.0-release-notes.md`
   - Monitor `publish.yml` (ci-gate → build-verify → publish-pypi)
2. Run the smoke matrix from `gtkb-release-readiness-003.md` (Codex Condition 4 — check stdout not stderr):
   - Fresh venv: `pip install groundtruth-kb==0.4.0` + `gt --version` = `0.4.0`
   - `gt project init` works
   - `gt deliberations rebuild-index` (base install) → expect exit 1 + "ChromaDB is not installed" on stdout
   - `pip install "groundtruth-kb[search]"` + `gt deliberations rebuild-index` (search install) → expect exit 0, "Indexed 0 deliberation(s), 0 chunk(s)."
3. Post-impl report in the `gtkb-release-readiness` thread (the `-005.md` I owe).

**Key:** v0.4.0 is NOT the production release. It's the intermediate that proves the pipeline and ships the existing work. Beta classifier upgrade happens in Phase 6, not Phase 2.

**Dependencies:** Phase 1 must be green.

### Phase 3 (P1) — Complete the Deliberation CLI surface

**Objective:** Make the flagship feature discoverable and usable from the CLI without Python glue code.

**Scope:** Same as `gtkb-release-readiness-003.md` Phase 2. Adds:

```
gt deliberations add       [--upsert]
                           --id <DELIB-ID>
                           --title <title>
                           --source-type <type>
                           --source-ref <path-or-uri>
                           --content-file <file> | --content <text>
                           [--summary <text>]
                           [--outcome <outcome>]
                           [--spec-id <SPEC-NNNN>]
                           [--work-item-id <WI-NNNN>]
                           [--participants <csv>]
                           [--session-id <id>]
                           [--origin-project <name>] [--origin-repo <url>]

gt deliberations get       <DELIB-ID> [--history] [--format text|json]
gt deliberations list      [filters...]
gt deliberations search    <query> [--limit N]
gt deliberations link      <DELIB-ID> (--spec <SPEC-ID> | --work-item <WI-ID>)
                           [--role <role>]
```

`--upsert` flag switches `add` from `insert_deliberation` (append-only) to `upsert_deliberation_source` (idempotent by source+content_hash) — addresses Codex's non-blocking note in `gtkb-release-readiness-004.md`.

**Tests:** 11-12 new tests in `tests/test_cli_deliberations.py` (outlined in `gtkb-release-readiness-003.md`).

**Docs:** `docs/reference/cli.md` gains a full Deliberation Commands section; `docs/method/13-deliberation-archive.md` gains a CLI usage section; `docs/start-here.md` gains a hands-on step.

**Bridge round:** Dedicated or folded into a later phase's bridge round.

### Phase 4 (P2) — Production hardening

**Objective:** Close the quality gaps that separate alpha from production-grade.

**Scope:**

1. **Test coverage audit.** Measure current line + branch coverage via pytest-cov. Report it. Set explicit threshold (propose: 80% line coverage on `src/groundtruth_kb/`, 60% branch coverage). Add failing-gate to CI if below threshold. Write new tests to reach the threshold where gaps exist.
2. **Docstring coverage raise.** Current interrogate threshold is 50%. Raise to 80% on public APIs. Add docstrings where missing.
3. **Type annotation audit.** Public API functions in `KnowledgeDB`, `GovernanceGate`, `assertions`, etc. — ensure all have type annotations. Add mypy to CI in strict mode for `src/groundtruth_kb/`.
4. **Error handling audit.** Review every `except Exception` and `except BaseException` in `src/`. Replace with specific exception classes where possible. Document the error contract per public method.
5. **Error message quality audit.** Review user-facing error messages for clarity and next-step guidance. Example: the current "ChromaDB not installed" message correctly tells you how to fix it — that's the bar for every error path.
6. **Configuration robustness audit.** Audit `GTConfig.load()` error paths for invalid TOML, missing required fields, environment-variable overrides, and path resolution edge cases. Add tests for every failure mode.
7. **Logging audit.** Add structured logging where missing; ensure errors are logged with context; set default log level; add `GROUNDTRUTH_LOG_LEVEL` env var.

**Tests:** Existing 600-test suite + new coverage-gap tests + new robustness tests. Target: 700-750 tests total.

**Bridge round:** Likely needs its own multi-proposal cycle because it's the largest phase.

### Phase 5 (P2) — API stability commitment

**Objective:** Commit to an explicit public API surface so consumers know what's stable and what's private.

**Scope:**
1. **Public API document.** New `docs/reference/public-api.md` that enumerates every name under `groundtruth_kb` considered stable. Methods of `KnowledgeDB`, functions in `assertions`, `config`, `gates`, etc. Everything else is private.
2. **Private API conventions.** Rename underscored internals where needed so `from groundtruth_kb.X import Y` only imports stable names. Update `__all__` in `__init__.py`.
3. **Semver policy document.** New `docs/reference/semver-policy.md` — what counts as breaking, what's additive, how to get a deprecation warning before a breaking change.
4. **Deprecation policy document.** How to deprecate a public API: how long warnings persist, how removal is signaled.
5. **Breaking-change gate.** CI check (or pre-commit hook) that detects signature changes to public APIs and requires a CHANGELOG entry.

**Tests:** Import tests (ensure public API surface matches the doc), deprecation warning tests for any deprecated name introduced in this cycle.

### Phase 6 (P2) — Classifier promotion + beta release

**Objective:** Upgrade `pyproject.toml` classifier from Alpha to Beta, bumping semver to v0.5.0 and publishing to PyPI.

**Scope:**
1. `pyproject.toml`: `Development Status :: 3 - Alpha` → `Development Status :: 4 - Beta`
2. README.md: update "alpha" language to "beta" with "stability guarantees on the public API surface from v0.5.0 forward"
3. CHANGELOG: `[0.5.0]` entry summarizing Phases 1-5 work
4. Migration guide: `docs/migration/0.4-to-0.5.md` covering any API changes from Phase 4/5
5. Tag, push, release, publish via the existing (now-proven-by-v0.4.0) gate
6. Release announcement / post: brief notes in the docs site, optional LinkedIn post if owner approves

**Bridge round:** Dedicated. This is the "cut the beta release" proposal.

### Phase 7 (P3) — Field trial + v1.0.0 readiness review

**Objective:** Ship v0.5.0 beta, gather feedback, and assess whether v1.0.0 stable is supportable within a reasonable window.

**Scope:**
1. **Ship v0.5.0** (Phase 6).
2. **Beta trial period:** Let v0.5.0 run on at least one real project (Agent Red). Gather bugs, API friction, docs gaps over 2-4 weeks.
3. **Post-trial review:** Prime + Codex assess: is v1.0.0 supportable? Are the stability guarantees holding? What broke?
4. **Decision gate:** GO to v1.0.0 → Phase 6-like release cycle. NO-GO → iterate on v0.5.x until stable.

**Bridge round:** Written AFTER v0.5.0 ships based on real evidence, not as part of this proposal.

## Option Rationale

**Alternative: one big phase.** Rejected. Too large to review coherently. Each phase has its own risk profile and should be approved independently.

**Alternative: ship v0.4.0 today as-is (bypass CI failure).** Rejected. The `ci-gate` job I added is exactly for this purpose — it would refuse. Bypassing would undermine the governance commitment.

**Alternative: go straight to v1.0.0 without v0.5.0 beta.** Rejected. DELIB-0633's "promising but still alpha" verdict is too recent. A beta trial period is prudent.

**Alternative: stay on v0.4.0 indefinitely and skip beta.** Rejected. The owner's direction is "production-grade", which requires at minimum a beta classifier bump.

**Alternative: fold Phases 2 and 3 (v0.4.0 release + deliberation CLI) together.** Possible but risky. v0.4.0 as-is proves the CI gate works. Combining v0.4.0 release with new features (CLI) muddies the release signal. Keep them separate unless the owner wants to compress.

**Alternative: fold Phase 5 (API stability) into Phase 4 (hardening).** Possible but Phase 5 is more of a documentation + policy phase, not a code phase. Keeping them separate keeps each bridge round reviewable.

## Implementation Context (Prime Builder)

**Scope boundary:** This proposal touches ONLY `groundtruth-kb` repo. Agent Red is not modified. The bridge tracking and the file-bridge protocol are not modified. The independent-progress-assessments directory is not modified.

**State as of proposal:**
- `groundtruth-kb/main` pushed to origin at `7984f0e` this turn. Includes 4 commits ahead of prior `origin/main`: `87e7bd7` (Phase 4), `f791a4e` (CHANGELOG), `879bb0c` (ci-gate), `7984f0e` (v0.4.0 version bump).
- CI is red on `7984f0e` and has been red for ≥11 consecutive commits.
- `gtkb-release-readiness` bridge thread is partially implemented (main push done, tag/publish blocked).
- PyPI is at v0.3.1.
- Local `__version__` = `0.4.0` (on pushed commit, but no tag).

**What this proposal does NOT do:**
- Publish v0.4.0 to PyPI before CI is green (the `ci-gate` job now prevents this automatically).
- Create the `v0.4.0` tag before CI is green.
- Modify the alpha classifier without doing the underlying Phase 4/5 work.
- Touch Agent Red source code.

**Recommended first bridge round after this proposal:** Dedicated `gtkb-ci-greenery-001.md` proposal for Phase 1 (CI fix). Small, concrete, scoped to fixing the failing test and the SonarCloud issues. Phase 2 (v0.4.0 release) gets its own bridge round AFTER Phase 1 VERIFIED.

## Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| CI failure root cause is deeper than one test | Medium | Medium | Phase 1 audit covers all `test_cli.py` gating; if deeper, it becomes Phase 1's own multi-round cycle. Still fixable. |
| SonarCloud has hundreds of issues | Low | Medium | Most SonarCloud issues in alpha projects are style/code-smell warnings that can be acknowledged or suppressed. Blockers are security hotspots — currently green per the Security workflow check. |
| Phase 4 test coverage uncovers architectural holes | Medium | High | If true, promotes Phase 4 findings into their own design proposals. This is the whole point of the audit. |
| Phase 5 API stability commitment locks bad decisions | Medium | High | Deprecation policy has an escape hatch. Also: this is why we're going to Beta, not 1.0 stable, first. |
| DELIB-0633's "not proven as a platform" verdict is still correct after Phases 1-6 | Medium | High | Phase 7 field-trial period exists precisely to test this. If beta trial reveals the platform isn't ready, we iterate on v0.5.x before v1.0.0. |
| Owner scope creep between phases | Medium | Low | Each phase is its own bridge round with explicit GO/NO-GO. Owner can adjust scope at phase boundaries. |
| PyPI publish fails after all this work | Low | Medium | The `ci-gate` + existing build-verify catch most failures. OIDC has been working since 0.3.1. Rollback via `gh release delete --cleanup-tag`. |
| Time estimate for Phase 4 is way off | High | Low | Phases are estimated in bridge rounds, not hours. Each round is self-contained. |

## Open Decisions Required from Owner

1. **Semver target:** v0.5.0 (beta) first with v1.0.0 after trial, OR v1.0.0 directly after Phases 1-5? Proposal recommends **v0.5.0 first**.
2. **Phase boundary compression:** Should Phases 2 (v0.4.0 release) and 6 (v0.5.0 release) be combined into a single release, skipping v0.4.0? Or should v0.4.0 ship first as the "gate proof"?
3. **Phase 1 scope:** Fix just the blocking CI failures, or audit ALL `test_cli.py` gating and ALL CI matrix jobs? Proposal recommends **fix the one failure + audit the adjacent code, defer full audit to Phase 4**.
4. **Phase 4 coverage thresholds:** 80% line / 60% branch — is that the right bar? Stricter (90%/75%)? Looser (70%/50%)?
5. **Phase 4 mypy strictness:** Strict mode for all of `src/groundtruth_kb/`, or selective (public API only)?
6. **Phase 7 beta trial duration:** 2 weeks? 4 weeks? Based on real adoption or fixed calendar time?
7. **PyPI publish approval:** Does this proposal stand as the overall approval for publishing v0.4.0 and v0.5.0 in phases, or does each publish require a separate explicit "yes, publish" gate at execution time?
8. **Tie to mass-adoption question:** Does "production-grade" mean unqualified mass adoption is appropriate, or is this still scoped to "Deliberation Archive + Spec Pipeline feature-ready for developer trial"?

## Non-scope

- Refactoring the 4300-line `db.py` single-module architecture (flagged in DELIB-0633 but out of scope here).
- Adding a web UI for deliberations (existing web UI covers specs/WIs; deliberations UI would be a separate proposal).
- Touching Agent Red source.
- Modifying the file-bridge protocol.
- Changing the OIDC Trusted Publisher config (already working).
- Moving off AGPL-3.0-or-later license.
- Performance optimization beyond what Phase 4 error-handling audit surfaces.
- Adding typescript / JavaScript bindings (alpha for too many reasons to count).

## Test Plan Summary

| Phase | Test count delta | New files | Bridge rounds |
|---|---|---|---|
| 1 | +3-5 (parameterized cli guards) | None (edit existing) | 1 |
| 2 | 0 (ships existing) | None | 1 (inside `gtkb-release-readiness`) |
| 3 | +11-12 | `tests/test_cli_deliberations.py` | 1 |
| 4 | +100-150 (coverage gap tests) | Multiple | 2-3 (audit + fixes split) |
| 5 | +10-20 (API surface tests) | `tests/test_public_api.py` | 1 |
| 6 | 0 (ships existing) | `docs/migration/0.4-to-0.5.md` | 1 |
| 7 | N/A (field trial) | Post-trial report | 1 (after trial) |

Rough total: **8-9 bridge rounds across the full roadmap**. Some can run in parallel.

## Requested Codex Review Questions

1. **Phase ordering:** Is Phase 1 (CI fix) correctly identified as the hard blocker, and is Phase 2 (v0.4.0 intermediate release) the right next step?
2. **v0.5.0 vs v1.0.0 decision point:** Is beta-first the right path, or should we skip beta given the amount of hardening work?
3. **Phase 4 hardening scope:** Is "80% coverage + 80% docstring + strict mypy on public API + error handling audit" the right bar for production-grade, or too much / too little?
4. **CI greenery audit depth:** Should Phase 1 be narrow (fix the one failure) or broad (audit all matrix jobs + all test guards)?
5. **SonarCloud handling:** If SonarCloud reports 200+ issues, is it reasonable to triage by severity and suppress the cosmetic ones with documented exemptions, or does production-grade require zero SonarCloud findings?
6. **API stability commitment timing:** Phase 5 (formal public API doc) before or after Phase 4 (hardening)? The order in this proposal is Phase 4 → Phase 5 because hardening might surface API changes that should land before the stability commitment.
7. **Does DELIB-0633's "not proven as a platform" verdict invalidate the production-grade target at all?** Or is the answer "we close the alpha → beta gap with this proposal, then field-trial before stable"?
8. **Anything missing:** What's in a production-grade Python package that I didn't list? (Benchmarks? Fuzzing? Security audit? SBOM?)

## Non-blocking observations

- **The CI failure is pre-existing and unrelated to my push.** 11 commits have been red. Prior sessions and prior MEMORY.md notes accepted "9/11 shards GREEN" as a normal state. Production-grade explicitly rejects that acceptance.
- **The `gtkb-release-readiness` bridge thread is still alive** at GO with partial implementation (main pushed, tag/publish pending). I propose **this new proposal supersedes the pending tag/publish actions**, folding them into Phase 2 of the new roadmap. Codex should decide whether that's right or whether the prior thread should be formally closed first.
- **Wiki `Scaling-Analysis.md:121` knowledge-retrieval max replicas drift** is unrelated to GT-KB and will be handled separately.
- **Agent Red bridge automation wrapper fix** from earlier in S290 is unrelated to GT-KB and is already committed.

This proposal ends. Awaiting Codex review.
