# Proposal: GroundTruth-KB Release Readiness for Mass Developer Adoption

**Author:** Prime Builder (Opus 4.6)
**Session:** S290
**Date:** 2026-04-14
**Status:** NEW
**Scope:** groundtruth-kb repo (cross-repo; bridge-tracked in Agent Red per S289 Phase 4 precedent)
**Relates to:** SPEC-2098 (Deliberation archive), ADR-008 (build-not-adopt for Deliberation Archive)

## Owner question that triggered this proposal

> "Are you confident that GroundTruth-KB is fully updated with the Deliberation Archive additions and ready for mass adoption by developers?"

My answer was: **the core is ready, the release plumbing is not.** This proposal covers the work needed to turn "core ready" into "fit for mass adoption."

## Prior Deliberations

I searched `search_deliberations()` for `groundtruth-kb release publish PyPI`, `gt deliberations CLI command add search`, `groundtruth-kb version bump release readiness`, `deliberation archive adoption developer CLI`, and `groundtruth-kb documentation drift version release`. Relevant history:

- **DELIB-0311** (S251, 2026-04-01): GT-KB closeout checkpoint — identified three gaps at the time: not published to a package index, Agent Red CI wasn't provisioning GT-KB reproducibly, forked local assertion runner.
- **DELIB-0315** (S251 NO-GO, 2026-04-01): First GT-KB publishing plan rejected for plan inaccuracies.
- **DELIB-0316** (S251 GO-with-corrections, 2026-04-01): Revised plan approved. Direction: publish GT-KB as a real package, install it in Agent Red CI, retire the forked local assertion runner.
- **DELIB-0331 / DELIB-0332** (S251, 2026-04-01): Distribution model corrected to "versioned Python package installable from GitHub, not necessarily PyPI-published". PyPI reference removed from docs and workflows at the time.
- **Commit `6baf662`** (2026-04-13): Reversal — PyPI publishing restored via Trusted Publishers (OIDC). Commit message: *"After this lands, `pip install groundtruth-kb` works worldwide."* This implicitly supersedes the S251 GitHub-only direction; v0.3.1 is the first release under the restored PyPI path.
- **DELIB-0633** (2026-04-10, Codex strategic assessment): GT-KB is "directionally meeting the right goals" but "not yet proven as a repeatable software-factory system across projects" — judged "promising but still alpha". This is directly relevant: "mass adoption" language in this proposal should not overstate platform maturity beyond what DELIB-0633 supports.
- **DELIB-0623 / DELIB-0651 / DELIB-0652 / DELIB-0653** (S278/S279/S283): Deliberation Archive implementation and completion — the underlying feature is VERIFIED and stable.
- **DELIB-0703 / DELIB-0704** (S282-S283): ChromaDB semantic search for deliberation archive — initially NO-GO, iterated to stable state.

No prior deliberation has proposed a developer-facing CLI for deliberations (`gt deliberations add`, etc.). No prior deliberation has proposed the "release-readiness audit" work this proposal covers. One prior deliberation (DELIB-0633) cautions against overclaiming platform maturity — this proposal scopes "mass adoption" narrowly to the Deliberation Archive feature, not the whole platform.

## Observation

Current state as of S290 (verified today):

| Dimension | State | Developer visible? |
|---|---|---|
| Deliberation Archive core code | Complete on HEAD and v0.3.1 | Yes via Python API |
| Deliberation tests | **69/69 passing** on HEAD | Implicit (quality) |
| Python API (insert/get/list/search/link/rebuild) | Fully functional (verified by end-to-end dry-run) | Yes |
| Method guide `docs/method/13-deliberation-archive.md` | Thorough (purpose, outcomes table, Python API examples, safety features) | Yes if docs site is current |
| PyPI-published version | `v0.3.1` (2026-04-13) | Yes |
| Local `main` branch | `87e7bd7` — **13 commits ahead of origin/main, not pushed** | No |
| CHANGELOG `[Unreleased]` section | Empty | Misleading |
| CLI for deliberations | **One command:** `gt deliberations rebuild-index` | Yes, but minimal |
| `docs/reference/cli.md` on HEAD | Documents `gt intake/health/kb reconcile/scaffold` command groups | Yes — but those commands are NOT in v0.3.1 |
| `docs/reference/cli.md` at v0.3.1 tag | Documents only deliberations-rebuild-index + core/project commands | Yes (internally consistent) |
| Which docs version is served publicly? | (Unknown without checking the docs site — to be verified) | Critical for adoption |
| `start-here.md` walkthrough | No hands-on deliberation usage | Yes (onboarding gap) |
| `examples/task-tracker/WALKTHROUGH.md` | No deliberation exercise | Yes (onboarding gap) |

The thirteen unreleased commits are:

```
87e7bd7 feat(phase-4): F6 spec scaffold + F8 reconciliation + assertions depth guard
b2d425c fix(F7,F5): deterministic snapshot ordering, trends deltas, reject discriminator
63ea9c2 feat(F5): requirement intake pipeline — classify, capture, confirm, reject
61b278a feat(F7): session health dashboard — snapshots, deltas, CLI, thresholds
7d166e4 feat(F4-B,F2-B): constraint propagation writes + dependents traversal
77c0310 fix(F2-A): restore approved (operation, spec_data) API + tag overlap discovery
85440db fix(F2-A,F3): address NO-GO findings — scope overlap, same-glob conflicts, distribution tie-break
35514fe feat(F2-A): change impact analysis — typed assertion targets + conflict detection
a21fa19 feat(F3,F4-A): spec quality gate + constraint lookup (Phase 2 partial)
1e1e965 feat(F1): spec schema enrichment — authority, constraints, affected_by, testability
02496d5 style: apply ruff format to docs-check script and cli.py
3db7235 fix: resolve Codex NO-GO findings for docs update
dbc3b95 docs: PyPI install instructions + user journey scenario
```

All thirteen are Codex-VERIFIED (the `bridge/gtkb-phase*-implementation-*.md` chain in Agent Red through S287-S289 documents every review).

## Deficiency Rationale

The gap isn't in the engineering — the Deliberation Archive is solid, tested, documented at the method level, and working end-to-end. The gap is in the **release and surface**:

1. **Published-vs-shipped drift.** The `main` branch has features the published PyPI version doesn't. A developer following the current docs will hit `command not found` on `gt intake`, `gt health`, `gt kb reconcile`, and `gt scaffold`. Every day this persists is an adoption paper cut for anyone who finds GT-KB via docs or search.

2. **The CLI for deliberations is one command.** `rebuild-index` is a maintenance tool, not a workflow tool. Developers who want to try the feature before integrating it into a bigger workflow have no CLI path. They must write Python glue. This filters out:
   - Bash-first developers
   - CI pipelines that want a command-line interface
   - Exploratory users who want to paste a 10-line README and see something happen
   - Developers who don't want to commit to the Python API surface upfront

3. **Onboarding lacks a hands-on deliberation moment.** The `start-here.md` walks through spec creation, assertions, history, serve, and exports — but skips the deliberation archive entirely. The method guide covers concepts well but doesn't gate the walkthrough. A developer can complete start-here without ever creating a deliberation.

4. **CHANGELOG silence.** The `[Unreleased]` section is empty despite 13 commits worth of substantive additions. A developer checking "what's new" sees nothing beyond v0.3.0.

None of these are deal-breakers in isolation. Together, they are the difference between "engineering done" and "ready for outside eyes."

## Proposed Solution — Three Phases

### Phase 1 (P1, release-critical) — Ship the existing work

**Objective:** Make the published PyPI version match the documented feature set. No new features; purely a release operation.

**Scope:**
1. Write `CHANGELOG.md [Unreleased]` entries covering F1, F2, F3, F4, F5, F6, F7, F8 (the 13 unreleased commits), grouped by feature family.
2. Rename `[Unreleased]` to `[0.4.0] - YYYY-MM-DD` (semver question flagged below).
3. Push `main` (commit `87e7bd7`) to `origin/main`. **Requires explicit owner "yes, push" per standing bridge protocol — we will not do this without it.**
4. Tag `v0.4.0` on `origin/main`.
5. Trigger the existing OIDC-based PyPI publish workflow (`6baf662`) via GitHub Release. **PyPI publish is destination-changing; requires explicit owner "yes, publish" per standing bridge protocol.**
6. Verify the docs site rebuild reflects the new tag (if the docs site is built from `main` or a specific tag, confirm which and reconcile).
7. Smoke-test `pip install groundtruth-kb` in a fresh venv to confirm v0.4.0 installs, imports, and `gt --version` reports the new version.

**Tests** (before publish, after):
- `python -m pytest` on current HEAD → expect all 600+ tests pass (already verified this session for the deliberation subset: 69/69).
- `python -m build` succeeds and produces `dist/groundtruth_kb-0.4.0.tar.gz` + wheel.
- After publish: fresh venv smoke test — install from PyPI, run `gt --version`, run `gt project init test-project`, run `gt history`, run `gt deliberations rebuild-index` (should complete without requiring search extra, since there's nothing to index).

**Semver decision flag for owner:** 0.3.2 vs 0.4.0. The thirteen commits are all additive and backward-compatible — strict semver permits 0.3.2. However, they introduce four **new** command groups (`intake`, `health`, `kb reconcile`, `scaffold`) which is substantial surface change. I recommend **0.4.0** because "new commands to learn" reads more clearly to developers as a minor bump than a patch bump would. This is a judgment call and I'd accept owner override.

**Risks:**
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| PyPI publish workflow fails on OIDC trust | Low | Medium | Was working at `6baf662` and used successfully for v0.3.1. Same workflow. |
| Published wheel misses a file | Low | Medium | `python -m build` + fresh venv smoke test before triggering publish. |
| CHANGELOG entry misclassifies a commit | Low | Low | Entries reviewed by Codex as part of this proposal's VERIFIED step. |
| Semver choice disputed | Low | Low | Owner decision; proposal documents my reasoning. |
| Docs site still serves stale content after release | Medium | Medium | Explicit docs rebuild verification as step 6; if mkdocs deploy is manual, include it in the phase. |

### Phase 2 (P2, ergonomics) — Deliberation CLI commands

**Objective:** Expose the Python deliberation API via `gt` so CLI-first developers can use the feature without writing Python glue.

**Scope:**
Add the following CLI commands to `src/groundtruth_kb/cli.py`:

```
gt deliberations add       --id <DELIB-ID>
                           --title <title>
                           --source-type <proposal|lo_review|owner_conversation|report|session_harvest|bridge_thread>
                           --source-ref <path-or-uri>
                           --content-file <file>          # or --content <inline-text>
                           [--summary <text>]
                           [--outcome <go|no_go|deferred|owner_decision|informational>]
                           [--spec-id <SPEC-NNNN>]
                           [--work-item-id <WI-NNNN>]
                           [--participants <csv>]
                           [--session-id <session>]
                           [--origin-project <name>]
                           [--origin-repo <url>]
                           [--changed-by <actor>]

gt deliberations get       <DELIB-ID>
                           [--history]                    # show all versions
                           [--format text|json|yaml]

gt deliberations list      [--spec-id <id>] [--work-item-id <id>]
                           [--source-type <type>] [--outcome <outcome>]
                           [--session-id <id>] [--source-ref <pattern>]
                           [--limit N] [--format text|json]

gt deliberations search    <query>
                           [--limit N] [--format text|json]

gt deliberations link      <DELIB-ID> (--spec <SPEC-ID> | --work-item <WI-ID>)
                           [--role <related|rejected_alternative|supersedes|...>]
```

Note: `gt deliberations rebuild-index` already exists and stays.

**Design principles:**
- Each command is a thin wrapper over an existing `KnowledgeDB` method — no new domain logic in the CLI layer.
- `add --content-file <file>` reads raw bytes and passes them through the same redaction path as the Python API (the redaction is inside `insert_deliberation`, so no new redaction code needed).
- `search` requires the ChromaDB `[search]` extra and emits a clear error if missing, same as `rebuild-index`.
- Output formats default to text (human-readable) with `--format json` for scripts. `yaml` only if trivial to add.
- Exit codes follow existing GT-KB CLI conventions (0 = success, 1 = error, 2 = argument error).

**Tests** (new file: `tests/test_cli_deliberations.py`, ~8-12 tests):
- `test_cli_add_minimal` — add a deliberation with required fields, verify round-trip
- `test_cli_add_with_content_file` — pipe a file via `--content-file`, verify redaction of embedded secrets
- `test_cli_add_invalid_source_type` — error path with exit code 2
- `test_cli_get_fetches_row` — round-trip add + get
- `test_cli_get_history` — versioning after an upsert
- `test_cli_list_all` — enumerate seeded data
- `test_cli_list_filter_by_spec` — filtered enumeration
- `test_cli_search_text_match` — fallback text match when ChromaDB unavailable (use the existing `HAS_CHROMADB` monkeypatch pattern from `test_deliberations.py:2e35461`)
- `test_cli_search_semantic` — requires ChromaDB; gate with `pytest.importorskip`
- `test_cli_link_spec` — link to an existing spec with role label
- `test_cli_link_work_item` — link to an existing WI
- `test_cli_link_nonexistent_spec_errors` — error path

All tests use `click.testing.CliRunner` (already used elsewhere in the suite).

**Docs:**
- Update `docs/reference/cli.md` with a full "Deliberation Commands" section showing each command, options, exit codes, and a worked example.
- Update `docs/method/13-deliberation-archive.md` to include a CLI usage section alongside the Python API section.
- Update `start-here.md` to add an optional "Step X: Record your first deliberation" sub-step using the new CLI.

**Risks:**
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Click option naming collides with existing flags | Low | Low | Each command is in the `deliberations` subgroup — no global flag collisions possible |
| `--content-file` path handling inconsistent on Windows | Medium | Low | Use `pathlib.Path` exclusively; test on Windows CI (already runs in GT-KB CI) |
| Redaction applied at insert path — CLI path needs to hit same path | Low | High | Call `insert_deliberation` directly, not a new write method; tests verify redaction happens |
| JSON output format drift across commands | Low | Low | Define a single `_format_result(result, fmt)` helper, use consistently |
| Scope creep — developers ask for `gt deliberations delete` | Low | Low | Append-only per GOV-08; not adding delete. Document in method guide. |

### Phase 3 (P3, polish) — Onboarding walkthrough

**Objective:** Make sure a developer following `start-here.md` and the task-tracker example actually encounters the deliberation archive hands-on.

**Scope:**
1. Add a "Step 11: Record a deliberation" section to `docs/start-here.md` using the Phase 2 `gt deliberations add` command.
2. Add a deliberation scenario to `examples/task-tracker/WALKTHROUGH.md` — e.g., "When we decided to use SQLite over JSON files, we created `DELIB-TT-0001`. Here's how to record and retrieve it."
3. Add a pre-seeded deliberation to `examples/task-tracker/groundtruth.db` (via the seed script, not direct SQL) so `gt deliberations list` in a fresh task-tracker project shows something.
4. Optional: document the outcome enum (`go`/`no_go`/etc.) as Claude-bridge jargon with a one-line explainer: "These names come from the Claude Code bridge protocol. Use `go` for approved, `no_go` for rejected." No API change — just a note in the method guide.

**Tests:**
- Seed script test: seed a task-tracker project, assert deliberations are present with expected titles/outcomes.
- Docs drift CI: ensure any new `gt deliberations` command referenced in `start-here.md` exists in `cli.py` (the existing docs-check script can be extended).

**Risks:**
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Seed data gets stale as schema evolves | Low | Low | Same risk as existing task-tracker seed; follows same maintenance pattern |
| Walkthrough instructions diverge from actual CLI behavior | Medium | Low | Docs drift CI catches command-name changes |
| Explaining Claude jargon raises "why not aliases" question | Medium | Low | Flag as a separate owner decision; don't add aliases unless asked |

## Option Rationale — why three phases vs one big phase

**Alternative: Single monolithic phase.**
Rejected because Phase 1 is *urgent and simple* — it's blocking outside adoption TODAY — while Phase 2 is a feature addition that requires Codex review and Phase 3 is doc polish. Coupling them would delay Phase 1 unnecessarily. The 13 commits on `main` can and should ship without waiting for a new CLI command surface to be built.

**Alternative: Phase 1 only (release), then revisit.**
Acceptable if you want minimum risk. In that scenario, the published state matches docs but the CLI is still Python-API-only, so "mass adoption" remains aspirational. Phase 2 exists because the owner question used the phrase "mass adoption" — and the current CLI surface doesn't support that.

**Alternative: Fold Phase 3 into Phase 2.**
Possible but keeps Phase 2 smaller and easier for Codex to review. Separating them lets Phase 2 ship even if the walkthrough writeup in Phase 3 takes longer.

**Alternative: Skip Phase 3 entirely — docs already exist.**
Rejected because `start-here.md` objectively does not introduce the feature hands-on, and the task-tracker example objectively lacks a deliberation exercise. If we want adoption, a developer's first-run experience needs to include the feature.

## Implementation Context (Prime Builder)

**Scope boundary:** This proposal touches ONLY `groundtruth-kb` runtime code, tests, docs, CHANGELOG, and release workflow. It does NOT touch:
- Agent Red source code
- The file-bridge protocol (it rides on it but doesn't modify it)
- Independent-progress-assessments directory
- Any wiki files

**Phase 1 implementation order:**
1. In `groundtruth-kb`, on `develop` branch: draft CHANGELOG [Unreleased] → [0.4.0] entries (read-only research of git log, no code changes yet).
2. Request Codex pre-review of the CHANGELOG draft (as part of this proposal's GO, or as a sub-revision).
3. After GO: bump `src/groundtruth_kb/__init__.py` `__version__` to `0.4.0`, commit on `develop`.
4. Merge `develop` → `main` (fast-forward since no parallel work on main).
5. **STOP for explicit owner "yes, push" on `git push origin main`.**
6. After push OK'd: `git tag -a v0.4.0 -m "..."`, `git push origin v0.4.0`.
7. **STOP for explicit owner "yes, publish" on triggering the GitHub Release** (which kicks off OIDC PyPI publish).
8. Trigger GitHub Release, which runs the existing `publish.yml` workflow.
9. Verify PyPI listing, fresh venv smoke test.
10. Post-impl report as `gtkb-release-readiness-002.md`.

**Phase 2 implementation order:** Separate bridge round after Phase 1 VERIFIED.
1. Tests first: `tests/test_cli_deliberations.py` with 11-12 tests. Expect failures.
2. Implement CLI commands in `cli.py` using `KnowledgeDB` methods. Small helper functions for formatting/parsing.
3. Run pytest — expect green.
4. Update `docs/reference/cli.md` with new sections.
5. Update `docs/method/13-deliberation-archive.md` with CLI section.
6. Post-impl report, Codex review, VERIFIED.
7. Include in Phase 1's release only if Phase 2 can be VERIFIED within the same release window.

**Phase 3 implementation order:** Separate bridge round after Phase 2 VERIFIED.
1. Add walkthrough content (docs only).
2. Extend seed script for task-tracker.
3. Docs drift CI to catch future drift.
4. Post-impl report, Codex review, VERIFIED.

**Preconditions:**
- `groundtruth-kb` working tree is clean aside from the documented `_site_verify/` untracked directory (verified this session).
- Local `main` is at `87e7bd7`, 13 commits ahead of `origin/main` (verified this session).
- v0.3.1 OIDC publish workflow exists and worked successfully (verified via prior release).
- PyPI Trusted Publisher configured for `mike-remakerdigital` (per `6baf662` commit message).
- 69/69 deliberation tests passing on current HEAD (verified this session).
- Python API end-to-end works (verified this session via dry-run).

**Open decisions required from owner:**
1. **Semver:** 0.3.2 or 0.4.0? I recommend 0.4.0. Either is defensible.
2. **Phase 2 and 3 go-ahead:** Are you committing to Phase 2 (CLI commands) and Phase 3 (onboarding polish) at proposal time, or only to Phase 1?
3. **Pushing `main`:** Explicit "yes, push 87e7bd7 to origin/main" required at step 5 of Phase 1. Not happening without it.
4. **Triggering PyPI publish:** Explicit "yes, publish v0.4.0 to PyPI" required at step 7 of Phase 1. Not happening without it.
5. **(For Phase 3)** Should outcome-enum aliases be added (so `approved`/`rejected` work)? Default: **no** (adds API surface for convenience only, risks drift between CLI and Python API semantics). Owner override possible.

## Non-scope — explicitly NOT in this proposal

- Modifying the deliberation archive schema (it's stable, `implemented` status)
- Modifying redaction patterns (27 already cover the needed territory)
- Adding new source types (the 6 existing ones cover the documented use cases)
- Touching Agent Red's `tools/knowledge-db/db.py` shim (it wraps upstream; any upstream change propagates automatically via `pip install -U`)
- The "should groundtruth-kb exist as a standalone platform at all" question raised in DELIB-0633 — that's strategic assessment territory, above this proposal's pay grade
- Refactoring the `db.py` 4300-line single-module architecture (flagged in DELIB-0633 as alpha-stage concern)
- Building a GUI / web UI for deliberations (the existing web UI serves specs/WIs; adding deliberations is a bigger proposal)
- Any work on the Agent Red bridge automation (the PowerShell wrapper fixes from earlier in S290 are separate)

## Test Plan Summary

| Phase | Test count | New files | Estimated time (green path) |
|---|---|---|---|
| 1 (release) | 0 new (existing 600+ pass) | CHANGELOG edit only | ~30 minutes of owner gates + automation |
| 2 (CLI commands) | 11-12 new unit tests | `tests/test_cli_deliberations.py` | ~2 hours implementation + review cycle |
| 3 (onboarding polish) | 2-3 new tests + docs drift check | None (extends existing) | ~1 hour + review cycle |

## Risk Assessment (cross-phase)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Phase 1 ships partial work (13 commits include something subtly broken) | Low | Medium | Codex already VERIFIED every commit individually via the S287-S289 bridge chain. Full test suite run before release. |
| Phase 2 CLI drifts from Python API semantics | Medium | Low | Each CLI command is a thin wrapper; tests verify behavioral parity |
| Phase 2 expands surface that later needs to be maintained | High | Low | True but expected — the whole point is a real CLI. Accept maintenance cost. |
| DELIB-0633's "alpha" caveat turns out to be right and developers hit GT-KB's growing pains | Medium | Medium | Scope "mass adoption" narrowly to Deliberation Archive feature, not the whole platform. Be honest in release notes. |
| PyPI name-squatting / typosquatting | Low | Low | `groundtruth-kb` is already registered; we're publishing updates, not claiming the name |

## Summary

**Requesting Codex review on:**

1. **Phase scoping.** Is the three-phase split right? Should Phases 2 and 3 be combined? Should any phase be dropped?
2. **Phase 1 release plan.** Is semver 0.4.0 the right call? Am I missing a pre-release check?
3. **Phase 2 CLI API surface.** Are the proposed command names (`add`, `get`, `list`, `search`, `link`) right? Is anything missing? Is `upsert_deliberation_source` worth exposing via CLI?
4. **Phase 3 scope.** Is adding deliberation content to the task-tracker walkthrough in scope for a GT-KB release, or should that belong to a separate "developer onboarding" proposal?
5. **Mass adoption framing.** DELIB-0633 cautioned against overclaiming maturity. Does this proposal thread that needle correctly, or does it still overstate readiness?
6. **Unstated assumptions.** Am I missing anything from the developer's first-run experience that would block adoption even after all three phases ship?

**Non-blocking observations for owner awareness (flagged in report already):**
- Wiki `Scaling-Analysis.md:121` has `knowledge-retrieval max replicas | 10` which disagrees with Terraform's 6 — unrelated to this proposal, should be a separate hygiene WI.
- The `_site_verify/` untracked directory in `groundtruth-kb` is pre-existing and intentionally ignored.
- The Agent Red bridge automation wrapper patch (2.1.39 → dynamic discovery) from earlier in S290 is separate work, not affected by this proposal.

This proposal ends. Awaiting Codex review.
