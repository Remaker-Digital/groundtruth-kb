# NO-GO: GroundTruth-KB Documentation Completion Proposal

## Verdict

NO-GO as written.

The proposal targets the right problem and the phase structure is broadly useful, but the current draft would publish incorrect first-run instructions and incomplete drift controls. The blockers are factual mismatches against the current `groundtruth-kb` checkout, not disagreement with the documentation completion goal.

## Review Scope

- Bridge proposal reviewed: `bridge/groundtruth-docs-completion-001.md`
- GroundTruth-KB evidence checkout: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
- Protocol evidence: `.claude/rules/file-bridge-protocol.md`
- Deliberation search source: `tools/knowledge-db/knowledge.db`

## Prior Deliberations

I searched the deliberation archive via `KnowledgeDB.search_deliberations()` before reviewing.

Relevant results found:

- `DELIB-0316`: S251 GroundTruth-KB publishing and Agent Red integration plan review, outcome `go`
- `DELIB-0332`: correction audit confirming the distribution model is GitHub-installable, not PyPI, outcome `informational`
- `DELIB-0474`: GroundTruth Execution Plan for Prime, outcome `informational`
- `DELIB-0633`: GroundTruth-KB Strategic Assessment, outcome `informational`
- `DELIB-0245`: S243 G3e Example Project Proposal Review, outcome `no_go`
- `DELIB-0315`: predecessor S251 publishing/integration NO-GO, apparently superseded by `DELIB-0316`

The proposal cites most of the relevant prior decisions and does not appear to reintroduce the old PyPI publishing plan. The current blockers are implementation accuracy in the new docs plan.

## Findings

### P1: The proposed Start Here command path is not executable as written

Claim in proposal:

- `docs/start-here.md` should provide a zero-to-working-system path.
- Step 3 command: `gt project init --profile local-only`
- Step 7 command: `gt seed --examples`

Evidence:

- `src/groundtruth_kb/cli.py` defines `project init` with required argument `project_name`.
- Click verification:
  - Command: `CliRunner().invoke(main, ['project','init','--profile','local-only'])`
  - Result: exit code `2`; output includes `Error: Missing argument 'PROJECT_NAME'.`
- `src/groundtruth_kb/cli.py` defines `gt seed` with option `--example`, singular.
- Click verification:
  - Command: `CliRunner().invoke(main, ['seed','--examples'])`
  - Result: exit code `2`; output includes `Error: No such option: --examples Did you mean --example?`

Risk/impact:

- The proposed first-run guide would fail for a new user at the exact point it is supposed to reduce support burden.
- This violates the proposal acceptance criterion that a new user can follow the guide from zero to `gt serve` without consulting other documents.

Required action:

1. Change the first-run sequence to use a real project name, for example `gt project init my-project --profile local-only`.
2. State whether later commands run after `cd my-project` or use `gt --config my-project/groundtruth.toml ...`.
3. Change `gt seed --examples` to `gt seed --example`.
4. Verify every command in `docs/start-here.md` with Click or the installed `gt` entry point before claiming acceptance.

### P1: The proposal's version story conflicts with the package-reported version

Claim in proposal:

- `v0.2.1 is current`
- Add `gt_version: "0.2.1"` and `gt_install_tag: "v0.2.1"`
- Start Here expected output: `groundtruth-kb 0.2.1`

Evidence:

- `git tag --list` includes `v0.2.1`.
- `git rev-list -n 1 v0.2.1` equals current `HEAD`.
- `src/groundtruth_kb/__init__.py:16` declares `__version__ = "0.2.0"`.
- `pyproject.toml` uses Hatch dynamic version from `src/groundtruth_kb/__init__.py`.
- Click verification:
  - Command: `CliRunner().invoke(main, ['--version'])`
  - Result: `gt, version 0.2.0`
- `CHANGELOG.md` and `docs/changelog.md` contain `0.2.0` as the latest documented release and have no `0.2.1` section.
- Repo search found no `0.2.1` or `v0.2.1` references in the working tree.

Risk/impact:

- Pinning install commands to tag `v0.2.1` may be valid as a Git ref, but documenting `gt --version` as `0.2.1` is false for the current tag.
- Adding a docs-level `gt_version: "0.2.1"` while the package reports `0.2.0` creates a new source of drift.
- Users will interpret the mismatch as a failed install or stale release.

Required action:

1. Decide whether the documentation should describe the Git tag, the package version, or both.
2. If `v0.2.1` is intended to be a user-visible package version, create a follow-up release/tag that actually updates `__version__` and the changelog; do not pretend the existing `v0.2.1` tag reports `0.2.1`.
3. If `v0.2.1` remains a tag-only patch marker, make `docs/start-here.md` expected output match `gt, version 0.2.0` and explain the distinction.
4. Add a drift check that compares documented expected `gt --version` output with the actual Click version output.

### P1: Version-drift scope misses active files and bare version strings

Claim in proposal:

- Phase 1 affected version-pin files are `docs/bootstrap.md`, `docs/desktop-setup.md`, `docs/method/10-tooling.md`, and two CI templates.
- Acceptance criterion: `grep -r "v0.1.2" docs/ templates/` returns only changelog/history context.

Evidence:

- `README.md:45` and `README.md:60` still install from `@v0.2.0`; README is public user-facing setup documentation.
- `docs/index.md:32` still installs from `@v0.2.0`; this is the docs homepage quick start.
- `docs/architecture/product-split.md:110` contains bare `0.1.2` in a current-status table.
- `docs/method/09-adoption.md:101` contains `pip install --upgrade groundtruth-kb`, which contradicts the GitHub-installable-only decision.
- `docs/method/09-adoption.md:127` contains the PyPI-style range `groundtruth-kb>=0.1.0,<0.2.0`.

Risk/impact:

- The proposed acceptance grep would miss bare `0.1.2`, `0.2.0`, README install examples, the docs homepage quick start, and PyPI-style upgrade guidance.
- The docs could pass the proposed check while still giving users stale or non-contract install instructions.

Required action:

1. Expand Phase 1 scope to include README install commands, `docs/index.md`, `docs/architecture/product-split.md`, and all PyPI-style adoption commands.
2. Replace the acceptance check with a stricter allowlist-based scan for `v0.1.2`, `0.1.2`, `v0.2.0`, `0.2.0`, `pip install groundtruth-kb`, and PyPI-style requirement ranges, excluding only intentional changelog/history contexts.
3. Explicitly keep changelog references if they are historical, but make that exclusion exact.

### P1: CLI reference count and generation method are underspecified

Claim in proposal:

- Complete CLI reference covers all `13` commands.

Evidence:

- Programmatic Click metadata enumeration found `14` leaf commands:
  - `init`
  - `bootstrap-desktop`
  - `assert`
  - `seed`
  - `summary`
  - `history`
  - `export`
  - `import`
  - `config`
  - `serve`
  - `project init`
  - `project doctor`
  - `project upgrade`
  - `deliberations rebuild-index`
- `python -m groundtruth_kb.cli --help` exits successfully but prints no help because the module does not call `main()` under `if __name__ == "__main__"`.
- The proposal's own table lists 14 leaf commands while saying 13.

Risk/impact:

- A docs coverage gate based on the wrong count can pass while omitting a command.
- A generator that shells out to `python -m groundtruth_kb.cli --help` will silently produce incomplete output.
- A source-text regex over `cli.py` is brittle for nested Click groups and renamed commands.

Required action:

1. Correct the proposal to 14 leaf commands, or explicitly define a different counting rule.
2. Generate the CLI reference from Click metadata or the installed `gt` console entry point, not `python -m groundtruth_kb.cli`.
3. Make the drift-prevention script recursively enumerate Click groups and nested commands.

### P2: Configuration reference places `chroma_path` under the wrong documented shape

Claim in proposal:

- Example config shows `chroma_path` under `[groundtruth]`.
- Path resolution rules are described as coming from `config.py:70-110`.
- `chroma_path` defaults beside the SQLite DB if not specified.

Evidence:

- `src/groundtruth_kb/config.py:33` declares `GTConfig.chroma_path: Path | None = None`.
- `src/groundtruth_kb/config.py:107-110` reads `chroma_path` from the `[search]` section.
- `tests/test_deliberations.py:1154-1184` explicitly tests `[search].chroma_path` parsing and default `None`.
- `src/groundtruth_kb/db.py:3405-3408` lazily falls back to `db_path.parent / ".groundtruth-chroma"` only when the ChromaDB client is requested and no explicit path was provided.

Risk/impact:

- The proposed config reference blurs config default behavior with database runtime fallback behavior.
- Users may put `chroma_path` under the wrong section or misunderstand when the Chroma directory is created.

Required action:

1. Document `[search].chroma_path` as the canonical TOML shape unless Prime intentionally changes the loader contract.
2. Distinguish `GTConfig.chroma_path` default `None` from the KnowledgeDB semantic-index fallback path.
3. If `gt config` is enhanced to print `chroma_path`, specify whether it prints the raw config value or the effective Chroma persistence path.

### P2: Python prerequisite is too low

Claim in proposal:

- Start Here prerequisites: Python 3.10+

Evidence:

- `pyproject.toml:11` requires `>=3.11`.
- README badge and current docs already say Python 3.11+.

Risk/impact:

- A Python 3.10 user following the new guide will install into an unsupported interpreter and hit packaging/runtime failure.

Required action:

1. Change the proposed prerequisite to Python 3.11+.
2. Add a docs drift check that compares published prerequisite text with `pyproject.toml` `requires-python`.

## Conditions For GO

Codex can approve a revised proposal once it:

1. fixes the Start Here command sequence against real Click behavior;
2. resolves the `v0.2.1` tag versus package-version mismatch;
3. expands version/PyPI drift cleanup to all public docs, especially README and docs homepage;
4. corrects CLI command count and nested command coverage;
5. documents `chroma_path` according to the current config loader/tests;
6. changes Python prerequisite to 3.11+;
7. updates acceptance criteria so these exact regressions are caught automatically.

## Recommended Revision Shape

Keep the eight-phase structure, but revise Phase 1 and Phase 2 before implementation:

- Phase 1 should become "release/install truth alignment" and explicitly cover README, docs homepage, changelog policy, package-reported version, Git tag policy, and PyPI-style text removal.
- Phase 2 should include a preflight verification table showing each proposed command, the verified Click command, the expected output, and whether the command is run from the project directory or with `--config`.
- Phase 8 should include executable docs checks for CLI coverage, install-reference drift, Python requirement drift, and `gt --version` expected-output drift.

## Decision Needed From Owner

Owner decision is needed on one point before revision:

- Should public docs treat `v0.2.1` as the current install tag while the package reports `0.2.0`, or should Prime create a new release/version milestone before the docs completion work lands?

