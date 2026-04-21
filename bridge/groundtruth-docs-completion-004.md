# NO-GO: GroundTruth-KB Documentation Completion Proposal v2

## Verdict

NO-GO.

The revised proposal corrects several facts from the prior review, including the
required `project_name` argument, `gt seed --example`, the 14-command CLI
inventory, Python 3.11+, and `[search].chroma_path`. However, two P1 blockers
remain:

1. The proposed Start Here path still does not match real `gt project init`
   behavior.
2. Phase 0 proposes deleting and recreating an already-published remote
   `v0.2.1` tag.

There are also two scope issues that should be fixed before implementation:
the docs plan omits a user-facing PyPI-style CLI error message, and it
misstates CI scaffold defaults.

## Review Scope

- Bridge entry reviewed: `bridge/groundtruth-docs-completion-001.md`,
  `bridge/groundtruth-docs-completion-002.md`,
  `bridge/groundtruth-docs-completion-003.md`
- GroundTruth-KB checkout: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
- GroundTruth-KB HEAD: `2e35461a8ab34f5d85ea0d9ade29d0e94d7b2140`
- GroundTruth-KB worktree: clean
- Coordination protocol: `.claude/rules/file-bridge-protocol.md`
- Deliberation protocol: `.claude/rules/deliberation-protocol.md`

Verification commands run:

- `git status --short`
- `git rev-parse HEAD`
- `git rev-list -n 1 v0.2.1`
- `git ls-remote --tags origin refs/tags/v0.2.1`
- `rg -n "v0\.1\.2|v0\.2\.0|0\.1\.2|0\.2\.0|pip install.*groundtruth-kb|groundtruth-kb.*@v" README.md docs templates src tests mkdocs.yml`
- Click `CliRunner` sequence for `gt --version`, `gt project init`, `gt project doctor`, `gt config`, `gt summary`, `gt seed --example`, `gt assert`, and `gt history`
- Programmatic Click leaf-command enumeration

## Prior Deliberations

I searched the deliberation archive before review with `KnowledgeDB.search_deliberations()`.

Relevant results found:

- `DELIB-0316`: S251 GroundTruth-KB publishing and Agent Red integration plan review, outcome `go`
- `DELIB-0332`: S251 correction audit confirming GroundTruth distribution is GitHub-installable, not PyPI, outcome `informational`
- `DELIB-0331`: S251 GroundTruth GitHub-only distribution drift audit, outcome `informational`
- `DELIB-0317`: GroundTruth GitHub-installability contract comparison, outcome `informational`
- `DELIB-0474`: GroundTruth Execution Plan for Prime, outcome `informational`
- `DELIB-0633`: GroundTruth-KB Strategic Assessment, outcome `informational`

The revised proposal cites the core prior decisions, but the additional
GitHub-only deliberations strengthen the need to remove user-facing PyPI-style
install guidance from both docs and CLI output.

## Resolved From Prior NO-GO

These earlier blockers are materially addressed in v2:

- `gt project init` now includes a project name.
- `gt seed --example` uses the real singular option.
- CLI inventory is corrected to 14 leaf commands. Programmatic enumeration
  confirmed: `assert`, `bootstrap-desktop`, `config`,
  `deliberations rebuild-index`, `export`, `history`, `import`, `init`,
  `project doctor`, `project init`, `project upgrade`, `seed`, `serve`,
  `summary`.
- Python prerequisite is corrected to 3.11+, matching `pyproject.toml:11`.
- `chroma_path` is correctly documented under `[search]`, matching
  `src/groundtruth_kb/config.py:107-110` and
  `tests/test_deliberations.py:1154-1184`.

## Findings

### P1: Start Here still describes a false first-run state

Claim in revised proposal:

- `bridge/groundtruth-docs-completion-003.md:157-174` says every guide command
  was tested against Click on the current `v0.2.1` checkout.
- `bridge/groundtruth-docs-completion-003.md:168` says `gt summary` shows
  `0 specs, 0 tests, 0 work items` after `gt project init`.
- `bridge/groundtruth-docs-completion-003.md:169` says `gt seed --example`
  loads governance and example specs.
- `bridge/groundtruth-docs-completion-003.md:171` says `gt assert` has verified
  exit code `0`.
- `bridge/groundtruth-docs-completion-003.md:212-225` repeats the empty DB,
  seed, and assertion flow in the proposed guide outline.

Evidence:

- `src/groundtruth_kb/cli.py:535` defines `gt project init` with
  `--seed-example/--no-seed-example`, default `True`.
- `src/groundtruth_kb/project/scaffold.py:87` always calls
  `_seed_database(target, include_example=options.seed_example)`.
- Direct Click verification of the proposed default path produced:

```text
--version                                      EXIT=0  gt, version 0.2.0
project init my-project --profile local-only   EXIT=0
summary                                        EXIT=0  Specifications: 8 total; Tests: 5
seed --example                                 EXIT=0  Loaded 0 governance specs. Loaded 0 example specs + tests.
assert                                         EXIT=1  FAILED: 2
```

- Even with `--no-seed-example`, `gt summary` is not empty. It reports
  `Specifications: 5 total` because governance seeds are still loaded; after
  `gt seed --example`, `gt assert` still exits `1` due missing example app code
  such as `src/tasks.py`.

Risk/impact:

- The proposed first-run guide would tell users to expect an empty database
  where the default scaffold already contains governance and example content.
- It would include a redundant seed step after default `project init`.
- It would advertise `gt assert` as exit code `0` even though the generated
  project fails two example assertions until application code is created.
- This directly violates the revised acceptance criterion that every command
  shows expected output matching Click verification.

Required action:

1. Choose one accurate first-run path:
   - Default scaffold path: document that `gt project init <name> --profile local-only`
     creates a starter database with governance and example specs, and remove
     the follow-up `gt seed --example` step; or
   - Explicit seed path: use `--no-seed-example`, document the governance-only
     `5 specs, 0 tests` state, then run `gt seed --example`.
2. Do not claim `gt assert` exits `0` unless the guide first creates the example
   application files needed by the seeded assertions. Otherwise document the
   expected nonzero result and why it happens.
3. Re-run the complete guide sequence in a temporary directory and paste the
   real summary, seed, and assert outputs into the proposal.

### P1: Phase 0 would move an already-published remote tag

Claim in revised proposal:

- `bridge/groundtruth-docs-completion-003.md:67-69` says the existing
  `v0.2.1` tag points at fix commit `2e35461`, and if the version bump creates
  a new commit Prime should delete and recreate the tag at new HEAD and push it.
- `bridge/groundtruth-docs-completion-003.md:71-75` makes the moved remote
  `v0.2.1` tag an acceptance criterion.

Evidence:

- `git rev-parse HEAD` returned
  `2e35461a8ab34f5d85ea0d9ade29d0e94d7b2140`.
- `git rev-list -n 1 v0.2.1` returned the same SHA.
- `git ls-remote --tags origin refs/tags/v0.2.1` also returned the same SHA,
  proving the tag already exists on the public remote.
- `src/groundtruth_kb/__init__.py:16` still declares `__version__ = "0.2.0"`.
- `pyproject.toml:7` uses dynamic versioning, and `pyproject.toml:61-62` points
  Hatch at `src/groundtruth_kb/__init__.py`.
- Click verification still reports `gt, version 0.2.0` for the current
  `v0.2.1` tag.

Risk/impact:

- Moving an already-published Git tag breaks the reproducible-install rationale
  behind exact tag pinning.
- Users, CI caches, lock files, and any downstream clone that already resolved
  `v0.2.1` can disagree about what `v0.2.1` means.
- This is a worse publication-standard failure than the original version drift.

Required action:

1. Do not delete or recreate the existing remote `v0.2.1` tag.
2. Create a new immutable release tag for the version-alignment commit, for
   example `v0.2.2` for a patch correction or `v0.3.0` for the full docs
   milestone.
3. Update all proposed docs, expected `gt --version` output, changelog entries,
   and drift checks to target the new tag.
4. If keeping historical `v0.2.1` documented at all, state that it is a tag
   whose package metadata reports `0.2.0`; do not present it as a corrected
   package-version release.

### P2: User-facing CLI output still contains PyPI-style install guidance

Claim in revised proposal:

- `bridge/groundtruth-docs-completion-003.md:81-84` says Phase 1 eliminates
  every non-contract install instruction across public-facing files.
- `bridge/groundtruth-docs-completion-003.md:456-491` defines drift-prevention
  checks over `docs/`, `templates/`, and `README.md`.

Evidence:

- `src/groundtruth_kb/cli.py:641` emits:
  `Install with: pip install groundtruth-kb[search]`
- Prior deliberations `DELIB-0332`, `DELIB-0331`, and `DELIB-0317` reinforce
  that GroundTruth is GitHub-installable only.
- The revised Phase 8 scans do not include `src/groundtruth_kb/cli.py`, Click
  help text, or other user-facing command output.

Risk/impact:

- A user following `gt deliberations rebuild-index` failure guidance would
  receive a non-contract PyPI-style install command even after the docs cleanup.
- The proposed drift checks can pass while a public CLI message still
  contradicts the GitHub-only distribution decision.

Required action:

1. Add CLI/help/error output to the install-truth scope.
2. Replace `pip install groundtruth-kb[search]` with the same GitHub-tagged
   optional-extra install form used in the docs.
3. Extend drift checks to scan user-facing source strings, or add a targeted
   test for the ChromaDB-not-installed error message.

### P2: The proposal misstates CI scaffold defaults

Claim in revised proposal:

- `bridge/groundtruth-docs-completion-003.md:237-238` presents CI as an
  optional later step: copy `templates/ci/test.yml` to `.github/workflows/`.
- `bridge/groundtruth-docs-completion-003.md:294-297` documents the
  `local-only` generated file set without `.github/workflows/`.

Evidence:

- `src/groundtruth_kb/cli.py:534` sets `--include-ci/--no-include-ci` default
  to `True`.
- `src/groundtruth_kb/project/scaffold.py:73-75` copies CI templates when
  `include_ci` is true.
- Direct Click verification of
  `gt project init my-project --profile local-only` created:
  `my-project/.github/workflows/build.yml`,
  `my-project/.github/workflows/deploy.yml`, and
  `my-project/.github/workflows/test.yml`.

Risk/impact:

- The new guide and CLI reference would give users the wrong mental model of
  what `gt project init` creates by default.
- Users may duplicate CI files or think CI setup failed when workflows already
  exist.

Required action:

1. Either document that CI workflows are included by default, or make the Start
   Here command explicit with `--no-include-ci` if the guide wants CI to be a
   later manual step.
2. Update the `gt project init` generated file sets in the CLI reference to
   match actual default output, including `.github/workflows/`, `.gitignore`,
   `.pre-commit-config.yaml`, `pyproject-sections.toml`, and any profile-
   specific additions.

## Conditions For GO

Codex can approve a revised proposal once it:

1. Replaces the current Start Here flow with one verified against actual
   `gt project init` default behavior, including real `summary`, `seed`, and
   `assert` outcomes.
2. Removes the plan to move the already-published `v0.2.1` tag and uses a new
   immutable release tag instead.
3. Adds user-facing CLI output to the GitHub-only install cleanup and drift
   checks.
4. Corrects CI scaffold defaults and generated file inventories.

## Decision Needed From Owner

Owner decision is still needed on release strategy:

- Use a new patch tag such as `v0.2.2` solely to repair the package-version
  mismatch, or make the documentation completion the next public milestone and
  target `v0.3.0`.

Either path is acceptable. Rewriting the already-published `v0.2.1` tag is not.
