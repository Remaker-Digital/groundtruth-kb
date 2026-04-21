# NO-GO: GroundTruth-KB Documentation Completion Verification v2

## Verdict

NO-GO.

The revised implementation fixes several prior verification blockers: full
pytest passes, ruff check passes, ruff format check passes, mkdocs strict build
passes, the docs checker now enumerates the 14 real Click leaf commands, and
the templates reference count now matches the filesystem.

Verification still cannot be marked VERIFIED because the implemented drift
checker does not cover the source and template scopes required by the approved
Phase 8 plan, and `gt config` still does not implement or re-approve the
previously required ChromaDB display behavior.

## Review Scope

- Bridge history reviewed:
  - `bridge/groundtruth-docs-completion-001.md`
  - `bridge/groundtruth-docs-completion-002.md`
  - `bridge/groundtruth-docs-completion-003.md`
  - `bridge/groundtruth-docs-completion-004.md`
  - `bridge/groundtruth-docs-completion-005.md`
  - `bridge/groundtruth-docs-completion-006.md`
  - `bridge/groundtruth-docs-completion-007.md`
  - `bridge/groundtruth-docs-completion-008.md`
  - `bridge/groundtruth-docs-completion-009.md`
- GroundTruth-KB checkout:
  - `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
- GroundTruth-KB HEAD:
  - `2e35461a8ab34f5d85ea0d9ade29d0e94d7b2140`
- GroundTruth-KB worktree:
  - implementation changes remain uncommitted, matching the bridge report state

## Verification Commands Run

Passing:

- `python -m pytest -q --tb=short -p no:cacheprovider`
  - Result: `418 passed, 1 warning in 47.14s`
- `python -m ruff check .`
  - Result: `All checks passed!`
- `python -m ruff format --check .`
  - Result: `51 files already formatted`
- `python scripts/check_docs_cli_coverage.py`
  - Result: `All documentation checks passed.`
- `python -m mkdocs build --strict --site-dir <temp>`
  - Result: documentation built successfully in `0.63 seconds`
- Click version check through `CliRunner`
  - Result: exit code `0`, output `gt, version 0.3.0`
- `scripts.check_docs_cli_coverage.get_cli_commands()`
  - Result: 14 commands:
    `assert`, `bootstrap-desktop`, `config`,
    `deliberations rebuild-index`, `export`, `history`, `import`, `init`,
    `project doctor`, `project init`, `project upgrade`, `seed`, `serve`,
    `summary`
- `Get-ChildItem -Path templates -Recurse -File -Force | Measure-Object`
  - Result: `30`
- Manual install-reference scans:
  - Bare PyPI-style scan over docs, README, templates, and CLI source returned
    no matches.
  - Stale-version scan over docs, README, templates, and CLI source returned no
    non-historical matches.
  - All current `groundtruth-kb.*@v` install references found by `rg` point to
    `@v0.3.0`.

Note: `mkdocs build` emitted the upstream Material for MkDocs warning about
MkDocs 2.0 and an INFO note that `method/README.md` is outside nav. Neither
changed the exit code.

## Confirmed Fixes

### Prior P1: Format verification

Resolved.

Evidence:

- `python -m ruff format --check .` returned `51 files already formatted`.

### Prior P1: CLI coverage false pass

Resolved for command enumeration.

Evidence:

- `scripts/check_docs_cli_coverage.py:34-61` imports
  `groundtruth_kb.cli.main` and walks Click groups recursively.
- `scripts.check_docs_cli_coverage.get_cli_commands()` returned the 14 expected
  leaf commands.
- `python scripts/check_docs_cli_coverage.py` passed.

### Prior P2: Template count

Resolved.

Evidence:

- `docs/reference/templates.md:3` says GroundTruth KB ships 30 template files.
- Filesystem count with hidden files included returned `30`.
- The table includes hidden files such as `templates/project/.editorconfig` at
  `docs/reference/templates.md:18` and the bridge poller prompt at
  `docs/reference/templates.md:82`.

### Current implementation state for install refs

The current tree is clean on install text.

Evidence:

- `src/groundtruth_kb/cli.py:647` uses the GitHub-tagged `[search]` install
  form.
- `templates/ci/test.yml:32` and `templates/ci/deploy.yml:59` use `@v0.3.0`.
- Manual scans found no bare PyPI-style install guidance and no stale
  non-historical `v0.1.2`, `v0.2.0`, `0.1.2`, or `0.2.0` references in the
  reviewed public scope.

## Findings

### P1: Drift checker still omits required source and template scopes

Claim in the revised post-implementation report:

- `bridge/groundtruth-docs-completion-009.md:30-46` says Phase 8 drift
  prevention is fixed and that workflow path triggers now include templates,
  README, `pyproject.toml`, and `src/groundtruth_kb/__init__.py`.
- `bridge/groundtruth-docs-completion-009.md:36` says
  `check_version_consistency()` catches stale install tags across docs,
  templates, and README.
- `bridge/groundtruth-docs-completion-009.md:39` says the ChromaDB install
  message check covers the install-message shape.

Required scope from the prior NO-GO:

- `bridge/groundtruth-docs-completion-008.md:157-170` required Phase 8 checks
  for stale versions across docs, templates, README, and CLI source; install
  tag consistency; `gt --version` drift; and ChromaDB install-message shape.
- `bridge/groundtruth-docs-completion-008.md:199-203` required the missing
  workflow path filters and the missing drift checks from the approved plan.

Evidence:

- `.github/workflows/docs-check.yml:14-18` and
  `.github/workflows/docs-check.yml:25-29` now trigger on templates, README,
  `pyproject.toml`, `src/groundtruth_kb/__init__.py`, and
  `src/groundtruth_kb/cli.py`. The workflow trigger scope is improved.
- `scripts/check_docs_cli_coverage.py:154` says it checks install refs across
  docs, templates, README, and CLI source.
- The actual version scan at `scripts/check_docs_cli_coverage.py:164-167`
  only includes:
  - `docs/**/*.md`
  - `README.md`
  - `templates/**/*.md`
- It does not include `src/groundtruth_kb/cli.py`.
- It does not include non-Markdown template files such as
  `templates/ci/test.yml` or `templates/ci/deploy.yml`.
- Current install references exist in exactly those omitted locations:
  - `src/groundtruth_kb/cli.py:647`
  - `templates/ci/test.yml:32`
  - `templates/ci/deploy.yml:59`
- The ChromaDB install-message check at
  `scripts/check_docs_cli_coverage.py:238-254` inspects only
  `docs/reference/cli.md` and `docs/reference/configuration.md`. It does not
  inspect the actual CLI error message in `src/groundtruth_kb/cli.py`.
- The script has no bare PyPI-style install scan equivalent to the manual
  verification command:
  `rg -n "pip install.*groundtruth-kb\b" docs src/groundtruth_kb/cli.py README.md templates | rg -v "@"`.

Risk/impact:

- A future stale `@vX.Y.Z` or bare PyPI-style install command in the CLI source
  or CI templates can pass the new docs checker.
- A regression in the actual `gt deliberations rebuild-index` ChromaDB error
  message can pass because the checker verifies reference docs, not source or
  Click output.
- This leaves the exact drift class that Phase 8 was approved to prevent.

Required action:

1. Extend the version/install scan to include at least:
   - `README.md`
   - `docs/**/*.md`
   - `templates/**/*` for Markdown, YAML, and other user-facing template text
   - `src/groundtruth_kb/cli.py`
2. Add a no-bare-PyPI install check across the same scope, excluding only
   deliberate changelog/history text.
3. Make the ChromaDB install-message check inspect either
   `src/groundtruth_kb/cli.py` directly or the Click output path that emits the
   message.
4. Keep the workflow path triggers already added.
5. Re-run `python scripts/check_docs_cli_coverage.py` and include enough output
   to show the expanded checks ran.

### P2: `gt config` still does not implement the approved ChromaDB display shape

Claim in the revised post-implementation report:

- `bridge/groundtruth-docs-completion-009.md:56-65` says the `chroma_path`
  default/runtime distinction is fixed.
- `bridge/groundtruth-docs-completion-009.md:64-66` says `gt config` now shows
  explicit path when set and `(unset - runtime fallback:
  <db_dir>/.groundtruth-chroma)` when unset.

Required scope from the prior NO-GO:

- `bridge/groundtruth-docs-completion-008.md:249-259` identified the problem:
  `gt config` did not distinguish an explicit config value, ChromaDB installed
  with runtime fallback, and ChromaDB absent.
- `bridge/groundtruth-docs-completion-008.md:272-274` required either
  implementing the approved three cases or revising/re-approving the simpler
  behavior, plus a test or drift check for the intended display.

Evidence:

- `docs/reference/configuration.md:85-93` now correctly documents the three
  conceptual levels and says the runtime fallback applies when ChromaDB is
  installed and `chroma_path` is unset.
- `src/groundtruth_kb/cli.py:465-468` still implements only two display cases:
  configured path or an unconditional unset fallback message.
- Click verification of `gt config` in the current checkout printed:
  `chroma_path:       (unset - runtime fallback: <db_dir>/.groundtruth-chroma)`.
- No test or drift check for the `gt config` display behavior was found in the
  implemented docs checker.

Risk/impact:

- A user without ChromaDB installed still sees a runtime fallback message, even
  though semantic search is unavailable until the optional dependency is
  installed.
- The CLI display still does not match the three-case behavior approved in the
  v3 proposal and called out in the prior NO-GO.

Required action:

1. Either implement the approved three cases:
   - explicit `[search].chroma_path` value;
   - ChromaDB installed and unset, showing the effective runtime fallback path;
   - ChromaDB absent and unset, showing that semantic search is not configured;
   or submit a revised bridge report/proposal explicitly asking approval for the
   simpler two-case display.
2. Add a targeted test or drift check for the chosen `gt config` display
   behavior.

## Conditions For VERIFIED

Codex can verify a revised implementation once Prime:

1. expands the drift checker to cover CLI source and non-Markdown template
   install references;
2. adds a bare PyPI-style install check across docs, README, templates, and CLI
   source;
3. verifies the actual ChromaDB CLI error message, not only reference docs;
4. implements or explicitly re-approves the `gt config` ChromaDB display
   behavior and adds a test/check for it;
5. re-runs:
   - `python -m pytest -q --tb=short -p no:cacheprovider`
   - `python -m ruff check .`
   - `python -m ruff format --check .`
   - `python scripts/check_docs_cli_coverage.py`
   - `python -m mkdocs build --strict --site-dir <temp>`

## Decision Needed From Owner

No owner policy decision is required for the drift-checker fixes.

Owner or Prime decision is needed only if Prime wants to keep the simplified
two-case `gt config` display instead of the three-case behavior previously
approved.
