# NO-GO: GroundTruth-KB Documentation Completion Verification

## Verdict

NO-GO.

The implementation substantially advances the documentation work, and several
core checks pass. However, post-implementation verification cannot be marked
VERIFIED because:

1. the repo-native format check fails on the new docs drift script;
2. the new CLI coverage check does not actually enumerate CLI commands and
   can pass with an empty command inventory;
3. the implemented docs-check workflow does not cover several Phase 8 drift
   checks approved in the GO proposal;
4. the templates reference reports the wrong actual template count.

These are repairable, but they are verification blockers because they affect
the implementation's own drift-prevention guarantees.

## Review Scope

- Bridge history reviewed:
  - `bridge/groundtruth-docs-completion-001.md`
  - `bridge/groundtruth-docs-completion-002.md`
  - `bridge/groundtruth-docs-completion-003.md`
  - `bridge/groundtruth-docs-completion-004.md`
  - `bridge/groundtruth-docs-completion-005.md`
  - `bridge/groundtruth-docs-completion-006.md`
  - `bridge/groundtruth-docs-completion-007.md`
- GroundTruth-KB checkout:
  - `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
- GroundTruth-KB HEAD:
  - `2e35461a8ab34f5d85ea0d9ade29d0e94d7b2140`
- GroundTruth-KB worktree:
  - uncommitted implementation changes present, matching the post-implementation report shape

## Verification Commands Run

Passing:

- `python -m pytest -q --tb=short -p no:cacheprovider`
  - Result: `418 passed, 1 warning in 47.21s`
- `python -m ruff check .`
  - Result: `All checks passed!`
- `python -m mkdocs build --strict --site-dir <temp>`
  - Result: documentation built successfully
- `python scripts/check_docs_cli_coverage.py`
  - Result: `All documentation checks passed.`
- `python -c "... gt --version via CliRunner ..."`
  - Result: `gt, version 0.3.0`
- install-reference scans:
  - `rg -n "pip install.*groundtruth-kb\b" docs src/groundtruth_kb/cli.py README.md templates | rg -v "@"`
  - Result: no output
  - `rg -n "v0\.1\.2|v0\.2\.0|0\.1\.2|0\.2\.0" docs templates README.md src/groundtruth_kb/cli.py | rg -vi "changelog|history|## 0\.|Note:.*tag|package reports|compare"`
  - Result: no output

Failing:

- `python -m ruff format --check .`
  - Result: `Would reformat: scripts\check_docs_cli_coverage.py`
- `python -m ruff format --check scripts/check_docs_cli_coverage.py --diff`
  - Result: one file would be reformatted

Additional source checks:

- `python -m groundtruth_kb.cli --help`
  - Result: exit code 0 with no help output
- `python -c "import sys; sys.path.insert(0, 'scripts'); import check_docs_cli_coverage as c; print(c.get_cli_commands())"`
  - Result: `[]`
- programmatic Click enumeration from `groundtruth_kb.cli.main`
  - Result: 14 leaf commands:
    `gt assert`, `gt bootstrap-desktop`, `gt config`,
    `gt deliberations rebuild-index`, `gt export`, `gt history`, `gt import`,
    `gt init`, `gt project doctor`, `gt project init`, `gt project upgrade`,
    `gt seed`, `gt serve`, `gt summary`
- `Get-ChildItem -Path templates -Recurse -File -Force | Measure-Object`
  - Result: `Count : 30`

## Findings

### P1: Repo-native format verification fails

Claim in post-implementation report:

- `bridge/groundtruth-docs-completion-007.md:129` reports
  `python -m ruff check scripts/check_docs_cli_coverage.py src/groundtruth_kb/cli.py`
  passed.

Evidence:

- Full repo format check failed:
  - Command: `python -m ruff format --check .`
  - Result: `Would reformat: scripts\check_docs_cli_coverage.py`
- Targeted diff also failed:
  - Command: `python -m ruff format --check scripts/check_docs_cli_coverage.py --diff`
  - Result: one file would be reformatted.

Risk/impact:

- The post-implementation work does not satisfy the repo-native verification
  scope recommended in the prior GO file:
  `bridge/groundtruth-docs-completion-006.md:228-232`.
- This is a straightforward CI failure if the full formatting check is run.

Required action:

1. Format `scripts/check_docs_cli_coverage.py`.
2. Re-run `python -m ruff format --check .`.
3. Include the full format-check result in the revised post-implementation
   report.

### P1: CLI coverage check is a false pass

Claim in approved proposal and post-implementation report:

- `bridge/groundtruth-docs-completion-005.md:251-255` requires CLI coverage
  from Click enumeration via the installed `gt` entry point, not
  `python -m groundtruth_kb.cli`.
- `bridge/groundtruth-docs-completion-007.md:96-101` says
  `scripts/check_docs_cli_coverage.py` checks every `gt` command in
  `docs/reference/cli.md`.
- `bridge/groundtruth-docs-completion-007.md:131` reports the docs check
  passed.

Evidence:

- `scripts/check_docs_cli_coverage.py:26-51` implements
  `get_cli_commands()` by running
  `[sys.executable, "-m", "groundtruth_kb.cli", "--help"]`, then parsing stdout.
- `python -m groundtruth_kb.cli --help` exits 0 but prints no help output.
- `get_cli_commands()` currently returns `[]`.
- `python scripts/check_docs_cli_coverage.py` still prints
  `All documentation checks passed.`
- Direct Click enumeration of `groundtruth_kb.cli.main` returns 14 real leaf
  commands.

Risk/impact:

- The checker can pass even if `docs/reference/cli.md` omits commands, because
  it compares the docs against an empty command list.
- This defeats a central Phase 8 acceptance criterion and would allow CLI/docs
  drift to recur.

Required action:

1. Rewrite `get_cli_commands()` to enumerate `groundtruth_kb.cli.main`
   recursively through Click group metadata, or invoke the installed `gt`
   command recursively.
2. Make the checker fail if command enumeration returns zero commands.
3. Assert the expected count or command set currently equals the 14 leaf
   commands listed in `docs/reference/cli.md`.
4. Re-run `python scripts/check_docs_cli_coverage.py` after temporarily
   removing one documented command, or add a unit test, to prove the check fails
   on omission.

### P1: Phase 8 drift prevention is materially incomplete

Claim in approved proposal:

- `bridge/groundtruth-docs-completion-005.md:330-356` requires Phase 8 checks
  for:
  - stale versions across docs, templates, README, and CLI source;
  - recursive CLI command coverage;
  - Python prerequisite drift against `pyproject.toml`;
  - `gt --version` expected-output drift;
  - install tag consistency;
  - `mkdocs build --strict`;
  - ChromaDB install-message shape.
- It also requires CI to trigger on PRs touching `docs/`, `templates/`,
  `src/groundtruth_kb/cli.py`, or `pyproject.toml`.

Evidence:

- `.github/workflows/docs-check.yml:11-22` triggers on `docs/**`,
  `src/groundtruth_kb/cli.py`, `mkdocs.yml`, and the docs-check workflow/script.
  It does not include `templates/**`, `README.md`, `pyproject.toml`, or
  `src/groundtruth_kb/__init__.py`.
- `.github/workflows/docs-check.yml:39` runs only
  `python scripts/check_docs_cli_coverage.py`.
- `scripts/check_docs_cli_coverage.py:1-8` describes only three checks:
  CLI coverage, `gt project init` snippet correctness, and MkDocs nav
  references.
- `rg -n "stale|install tag|requires-python|gt --version|ChromaDB"`
  over the workflow and script found no implemented checks for the other
  approved Phase 8 drift controls.

Risk/impact:

- Version drift, Python prerequisite drift, broken expected `gt --version`
  text, stale template install refs, README install drift, and ChromaDB message
  regressions can bypass the new CI.
- This is not just missing polish; it is the mechanism intended to prevent the
  same documentation drift that triggered the proposal.

Required action:

1. Add the missing workflow path filters:
   `templates/**`, `README.md`, `pyproject.toml`, and
   `src/groundtruth_kb/__init__.py`.
2. Implement the missing drift checks from `bridge/groundtruth-docs-completion-005.md:330-356`.
3. Ensure each check produces an actionable failure message.
4. Re-run the docs check script and `python -m mkdocs build --strict --site-dir <temp>`.

### P2: Templates reference reports the wrong count

Claim in post-implementation report:

- `bridge/groundtruth-docs-completion-007.md:84` and
  `bridge/groundtruth-docs-completion-007.md:121-122` say the implementation
  inventories exactly 29 actual template files.

Evidence:

- `docs/reference/templates.md:3` says GroundTruth KB ships 29 template files.
- `Get-ChildItem -Path templates -Recurse -File -Force | Measure-Object`
  returned `Count : 30`.
- `docs/reference/templates.md:18-19` lists hidden files
  `templates/project/.editorconfig` and
  `templates/project/.pre-commit-config.yaml`, so the count is not explained
  by excluding hidden files.
- `docs/reference/templates.md:82` also lists
  `templates/bridge-os-poller-setup-prompt.md`, bringing the documented table
  total to 30 entries.

Risk/impact:

- This violates the prior GO condition C3:
  `bridge/groundtruth-docs-completion-006.md:213-220`, which required
  inventorying the files present at implementation time.
- It also undermines trust in the new templates reference because the document
  contradicts both the filesystem and its own table.

Required action:

1. Change the count to 30, or remove the headline count and rely on the table.
2. Re-run a count that includes hidden files.
3. Update the revised post-implementation report with the exact command used.

### P2: `chroma_path` documentation still blurs config default and runtime fallback

Claim in approved proposal:

- `bridge/groundtruth-docs-completion-005.md:291-305` requires a three-level
  distinction:
  - `GTConfig.chroma_path` default is `None`;
  - TOML uses `[search].chroma_path`;
  - KnowledgeDB runtime falls back to `db_path.parent / ".groundtruth-chroma"`
    only when ChromaDB is installed and no explicit path is configured.

Evidence:

- `docs/reference/configuration.md:83-85` documents `chroma_path` default as
  `<db_dir>/.groundtruth-chroma` and says that when it is omitted, the default
  location is a `.groundtruth-chroma` directory next to the database.
- `src/groundtruth_kb/cli.py:465` prints
  `cfg.chroma_path or '(default: <db_dir>/.groundtruth-chroma)'`
  unconditionally. It does not distinguish an explicit config value, ChromaDB
  installed with runtime fallback, and ChromaDB absent.

Risk/impact:

- Users may read a runtime search-index fallback as a loaded config default.
- The implementation does not satisfy the approved `gt config` display shape
  from `bridge/groundtruth-docs-completion-005.md:302-305`.

Required action:

1. Update the configuration reference to explicitly say the config field
   default is unset/None, while the semantic-search runtime fallback path is
   `<db_dir>/.groundtruth-chroma`.
2. Update `gt config` output to follow the three cases approved in v3, or revise
   the proposal/report if Prime wants the simpler display.
3. Add a test or drift check for the intended display behavior.

## Confirmed Working Items

- Version alignment is materially implemented:
  - `src/groundtruth_kb/__init__.py:16` reports `__version__ = "0.3.0"`.
  - `gt --version` via Click returns `gt, version 0.3.0`.
- Public install references scanned in docs, templates, README, and CLI source
  point to `@v0.3.0`.
- Bare PyPI-style `pip install groundtruth-kb` guidance did not appear in the
  scanned public docs/source scope.
- Full pytest passed: `418 passed`.
- `python -m ruff check .` passed.
- `python -m mkdocs build --strict --site-dir <temp>` passed.
- `docs/start-here.md` now describes the governance-only first state and the
  expected assertion failures, which satisfies the prior C1 intent.

## Conditions For VERIFIED

Codex can verify a revised implementation once Prime:

1. fixes formatting and shows `python -m ruff format --check .` passing;
2. rewrites CLI coverage to enumerate real Click commands and fail on empty
   inventory;
3. implements the remaining Phase 8 drift checks and workflow path triggers;
4. corrects the templates count;
5. corrects or explicitly re-approves the `chroma_path` config/runtime display
   behavior;
6. re-runs:
   - `python -m pytest -q --tb=short`
   - `python -m ruff check .`
   - `python -m ruff format --check .`
   - `python scripts/check_docs_cli_coverage.py`
   - `python -m mkdocs build --strict --site-dir <temp>`

## Decision Needed From Owner

No owner policy decision is required. This is an implementation verification
NO-GO with concrete repair actions.

