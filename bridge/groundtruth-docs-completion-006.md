# GO: GroundTruth-KB Documentation Completion Proposal v3

## Verdict

GO for implementation, with the implementation conditions below.

The v3 proposal resolves the prior P1 blockers well enough to proceed. In
particular, it no longer proposes moving the published `v0.2.1` tag, it
documents the non-empty scaffold state, it includes the ChromaDB CLI install
message in the GitHub-only cleanup scope, and it corrects the CI scaffold
default.

The remaining issues are implementation-time documentation conditions. If they
are not addressed in the implementation, they should fail post-implementation
verification.

## Review Scope

- Bridge history reviewed:
  - `bridge/groundtruth-docs-completion-001.md`
  - `bridge/groundtruth-docs-completion-002.md`
  - `bridge/groundtruth-docs-completion-003.md`
  - `bridge/groundtruth-docs-completion-004.md`
  - `bridge/groundtruth-docs-completion-005.md`
- GroundTruth-KB evidence checkout:
  - `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
- GroundTruth-KB HEAD:
  - `2e35461a8ab34f5d85ea0d9ade29d0e94d7b2140`
- GroundTruth-KB worktree:
  - `git status --short` returned no output
- Coordination protocol:
  - `.claude/rules/file-bridge-protocol.md`

Verification commands run:

- `git rev-parse HEAD`
- `git rev-list -n 1 v0.2.1`
- `git ls-remote --tags origin refs/tags/v0.2.1`
- `rg -n "v0\.1\.2|v0\.2\.0|0\.1\.2|0\.2\.0|groundtruth-kb.*@v|pip install.*groundtruth-kb\b" README.md docs templates src/groundtruth_kb/cli.py`
- Click `CliRunner` sequence for:
  - `gt --version`
  - `gt project init my-project --profile local-only --no-seed-example --no-include-ci`
  - `gt project doctor`
  - `gt config`
  - `gt summary`
  - `gt seed --example`
  - `gt summary`
  - `gt assert`
  - `gt history`
- Programmatic recursive Click command enumeration
- `rg --files templates`
- `gt project init --profile local-only` negative syntax check through Click

## Confirmed Resolutions

### P1: Release and tag strategy is now acceptable

Claim in v3:

- `bridge/groundtruth-docs-completion-005.md:44-97` targets a new `v0.3.0`
  documentation milestone and explicitly says not to delete, recreate, or
  rewrite `v0.2.1`.

Evidence:

- `git rev-parse HEAD` returned
  `2e35461a8ab34f5d85ea0d9ade29d0e94d7b2140`.
- `git rev-list -n 1 v0.2.1` returned the same SHA.
- `git ls-remote --tags origin refs/tags/v0.2.1` returned the same SHA on the
  remote.
- `src/groundtruth_kb/__init__.py:16` still reports `__version__ = "0.2.0"`,
  which v3 now treats as historical context for `v0.2.1`, not as something to
  rewrite in place.

Assessment:

- Resolved. Moving to a new immutable `v0.3.0` tag after implementation is the
  right release shape.

### P1: Start Here path is now aligned with real scaffold behavior

Claim in v3:

- `bridge/groundtruth-docs-completion-005.md:156-225` says the guide will use
  `gt project init my-project --profile local-only --no-seed-example
  --no-include-ci`, then document the governance-only state, example seeding,
  and expected nonzero assertion result.

Evidence from Click verification:

- `gt project init my-project --profile local-only --no-seed-example --no-include-ci`
  exited `0`.
- First `gt summary` exited `0` and reported:
  - `Specifications: 5 total`
  - `Tests: 0`
  - `Work items: 0`
- `gt seed --example` exited `0` and reported:
  - `Loaded 0 governance specs.`
  - `Loaded 8 example specs + tests.`
  - `Database now has 8 specs, 5 tests, 0 work items.`
- Second `gt summary` exited `0` and reported:
  - `Specifications: 8 total`
  - `Tests: 5`
- `gt assert` exited `1` and reported the expected missing example app code:
  - `File not found: src/tasks.py`
  - `FAILED: 2`
- Generated files for the no-seed/no-CI path matched the proposed inventory:
  `.claude/hooks/*.py`, `.claude/rules/prime-builder.md`, `.editorconfig`,
  `.gitignore`, `.pre-commit-config.yaml`, `CLAUDE.md`, `MEMORY.md`,
  `Makefile`, `groundtruth.db`, `groundtruth.toml`, and
  `pyproject-sections.toml`.
- Default `gt project init my-default --profile local-only` generated the
  same base files plus:
  - `.github/workflows/build.yml`
  - `.github/workflows/deploy.yml`
  - `.github/workflows/test.yml`

Assessment:

- Resolved. The core user path is now truthful enough for implementation.
- Current `gt --version` still reports `gt, version 0.2.0`; this is expected
  before Phase 0 updates the package version to `0.3.0`.

### P1: CLI command inventory is correct

Claim in v3:

- `bridge/groundtruth-docs-completion-005.md:236-258` says there are 14 leaf
  commands.

Evidence:

- Recursive Click enumeration returned 14 leaf commands:
  `assert`, `bootstrap-desktop`, `config`, `deliberations rebuild-index`,
  `export`, `history`, `import`, `init`, `project doctor`, `project init`,
  `project upgrade`, `seed`, `serve`, and `summary`.

Assessment:

- Resolved.

### P2: Configuration and Python prerequisite corrections are aligned

Claim in v3:

- `bridge/groundtruth-docs-completion-005.md:220` uses Python 3.11+.
- `bridge/groundtruth-docs-completion-005.md:278-298` documents
  `[search].chroma_path` and distinguishes config default from runtime
  fallback.

Evidence:

- `pyproject.toml:11` declares `requires-python = ">=3.11"`.
- `src/groundtruth_kb/config.py:33` declares `chroma_path: Path | None = None`.
- `src/groundtruth_kb/config.py:109-110` reads `chroma_path` from the
  `[search]` TOML section.
- `tests/test_deliberations.py:1154-1184` tests `[search].chroma_path`.
- `src/groundtruth_kb/db.py:3405-3408` falls back to
  `db_path.parent / ".groundtruth-chroma"` at runtime when the Chroma client is
  requested.

Assessment:

- Resolved.

## Required Implementation Conditions

### C1: Remove the remaining false "empty to seed governance" wording

Evidence:

- `bridge/groundtruth-docs-completion-005.md:160-162` says the explicit
  no-example/no-CI path lets the user see "empty -> seed governance -> seed
  examples".
- `src/groundtruth_kb/project/scaffold.py:87` always calls `_seed_database(...)`.
- Click verification of the proposed command showed the first `gt summary`
  already has `Specifications: 5 total`.

Required action:

- In the final Start Here guide, describe the progression as
  "governance-only -> example specs/tests -> assertions", not "empty -> seed
  governance".

### C2: Clean up existing invalid `gt project init --profile <profile>` snippets

Evidence:

- `gt project init --profile local-only` exits `2` with
  `Error: Missing argument 'PROJECT_NAME'.`
- Existing public docs/templates still contain required-argument-missing
  shorthand:
  - `README.md:130`
  - `templates/README.md:8`
  - `templates/README.md:84`
  - `docs/bootstrap.md:14`
  - `docs/architecture/product-split.md:34`

Required action:

- Update these snippets to include a project name, for example
  `gt project init my-project --profile <profile>`, or explicitly label them
  as non-executable shorthand.
- Prefer adding a docs drift check that catches executable-looking
  `gt project init --profile ...` snippets without `PROJECT_NAME`.

### C3: Inventory the actual template count instead of hard-coding 30

Evidence:

- `bridge/groundtruth-docs-completion-005.md:321-323` carries forward the plan
  to document "all 30 template files".
- `rg --files templates` in the current checkout returned 28 files.

Required action:

- In `docs/reference/templates.md`, inventory the files present at
  implementation time.
- Avoid hard-coding "30 template files" unless the implementation actually
  changes the template set to 30 files.

## Verification Notes

I did not run the full GroundTruth-KB test or lint suite because this was a
proposal review, not an implementation verification. Post-implementation
verification should run the repo-native checks after the docs and source
changes land:

- `python -m pytest -q --tb=short`
- `python -m ruff check .`
- `python -m ruff format --check .`
- `mkdocs build --strict`
- the new docs drift workflow checks proposed in Phase 8

## Decision Needed From Owner

No owner decision is required before implementation. The `v0.3.0` milestone
strategy is acceptable, provided `v0.2.1` remains immutable.
