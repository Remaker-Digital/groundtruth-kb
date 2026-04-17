# NO-GO: GroundTruth-KB Documentation Completion Verification v3

## Verdict

NO-GO.

The v3 revision fixes the major implementation issues from
`bridge/groundtruth-docs-completion-010.md`: the repo-native checks pass, the
drift checker now scans CLI source and YAML templates, the ChromaDB install
message is corrected in the CLI, and `gt config` now implements the approved
three-case `chroma_path` display.

Verification still cannot be marked VERIFIED because the new no-bare-PyPI
install check allows extras-only PyPI-style installs such as
`pip install "groundtruth-kb[search]"`. GroundTruth-KB is still GitHub-installable
only, and the prior NO-GO required a check equivalent to "all
`pip install ... groundtruth-kb` references must contain `@` outside
changelog/history text."

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
  - `bridge/groundtruth-docs-completion-010.md`
  - `bridge/groundtruth-docs-completion-011.md`
- GroundTruth-KB checkout:
  - `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
- GroundTruth-KB HEAD:
  - `2e35461a8ab34f5d85ea0d9ade29d0e94d7b2140`
- GroundTruth-KB worktree:
  - implementation changes remain uncommitted, matching the bridge report state

## Verification Commands Run

Passing:

- `python -m pytest -q --tb=short -p no:cacheprovider`
  - Result: `421 passed, 1 warning in 46.81s`
- `python -m ruff check .`
  - Result: `All checks passed!`
- `python -m ruff format --check .`
  - Result: `51 files already formatted`
- `python scripts/check_docs_cli_coverage.py`
  - Result: all 8 documentation checks passed:
    CLI command coverage, `gt project init` snippets, mkdocs nav references,
    version consistency, bare PyPI install detection, Python prerequisite,
    `gt --version` output, and ChromaDB install message
- `python -m mkdocs build --strict --site-dir <temp>`
  - Result: documentation built successfully in `0.65 seconds`
  - Notes: emitted the upstream Material for MkDocs 2.0 warning and the existing
    info note that `method/README.md` is outside nav; exit code was 0

Additional verification:

- `scripts.check_docs_cli_coverage.get_cli_commands()` returned 14 commands:
  `assert`, `bootstrap-desktop`, `config`, `deliberations rebuild-index`,
  `export`, `history`, `import`, `init`, `project doctor`, `project init`,
  `project upgrade`, `seed`, `serve`, `summary`
- `_collect_scannable_files()` includes:
  - `README.md`
  - `src/groundtruth_kb/cli.py`
  - `templates/ci/test.yml`
  - `templates/ci/deploy.yml`
- `rg -n "pip install.*groundtruth-kb\b" docs src/groundtruth_kb/cli.py README.md templates | rg -v "@"`
  - Result: no output
- Direct `gt config` verification:
  - explicit `[search].chroma_path` prints the resolved explicit path
  - unset with ChromaDB importable prints `runtime fallback: <absolute path>`
  - unset with a monkeypatched ChromaDB import failure prints
    `chromadb not installed`
- `Get-ChildItem -Path templates -Recurse -File -Force | Measure-Object`
  - Result: `Count: 30`

## Confirmed Fixes

### Prior P1: Drift checker scan scope

Resolved for scan scope.

Evidence:

- `scripts/check_docs_cli_coverage.py:39-63` defines `_collect_scannable_files()`
  over docs, templates with user-facing extensions, `README.md`, and
  `src/groundtruth_kb/cli.py`.
- Direct verification showed the collector includes the previously missed
  `src/groundtruth_kb/cli.py`, `templates/ci/test.yml`, and
  `templates/ci/deploy.yml`.
- `.github/workflows/docs-check.yml:9-31` triggers on docs, templates, README,
  `pyproject.toml`, `src/groundtruth_kb/__init__.py`,
  `src/groundtruth_kb/cli.py`, `mkdocs.yml`, and the docs checker script.

### Prior P1: ChromaDB install message source coverage

Resolved for the current implementation.

Evidence:

- `src/groundtruth_kb/cli.py:650-653` prints the ChromaDB missing-dependency
  message with the GitHub direct-reference `[search]` install form.
- `scripts/check_docs_cli_coverage.py:288-312` checks ChromaDB install syntax
  in the reference docs and `src/groundtruth_kb/cli.py`.

### Prior P2: `gt config` three-case `chroma_path` display

Resolved.

Evidence:

- `src/groundtruth_kb/cli.py:465-474` implements:
  - explicit configured `chroma_path`;
  - unset plus ChromaDB installed, showing the resolved runtime fallback;
  - unset plus ChromaDB absent, showing `chromadb not installed`.
- `tests/test_cli.py:192-230` adds tests for all three display cases.
- Direct Click verification returned exit code 0 for all three checked cases.

## Findings

### P1: No-bare-PyPI install check still permits extras-only PyPI installs

Claim in the revised post-implementation report:

- `bridge/groundtruth-docs-completion-011.md:17-23` says
  `_collect_scannable_files()` covers the required files and that
  `check_no_bare_pypi_install()` scans all scannable files for
  `pip install groundtruth-kb` not followed by `[extra]`, `@`, or ` @`.

Required scope from the prior NO-GO:

- `bridge/groundtruth-docs-completion-010.md:166-168` identified the missing
  no-bare-PyPI check as one equivalent to:
  `rg -n "pip install.*groundtruth-kb\b" docs src/groundtruth_kb/cli.py README.md templates | rg -v "@"`.
- `bridge/groundtruth-docs-completion-010.md:181-187` required a no-bare-PyPI
  install check across README, docs, templates, and CLI source, excluding only
  deliberate changelog/history text.
- `bridge/groundtruth-docs-completion-010.md:247-252` made that check a
  condition for VERIFIED.

Evidence:

- `scripts/check_docs_cli_coverage.py:224-225` defines the bare install regex as:
  `pip\s+install\s+["']?groundtruth-kb(?!\[| @|@)`.
- Because the negative lookahead excludes `[`, the checker treats
  `pip install "groundtruth-kb[search]"` and `pip install "groundtruth-kb[web]"`
  as acceptable even when they have no GitHub direct reference.
- A non-mutating synthetic check against `check_no_bare_pypi_install()` returned:
  - `bare: 1 failure(s)`
  - `extra_only: 0 failure(s)`
  - `direct_ref: 0 failure(s)`
- Current documentation/install text is clean today: the manual `rg ... | rg -v "@"`
  check returned no output. The problem is the drift guard, not the current
  install snippets.

Risk/impact:

- A future invalid install instruction such as
  `pip install "groundtruth-kb[search]"` or `pip install "groundtruth-kb[web]"`
  can pass CI even though the package is not published to PyPI.
- This is especially material because the public docs and CLI already use extras
  forms in valid direct-reference commands, for example:
  - `README.md:60`
  - `docs/start-here.md:171`
  - `docs/reference/cli.md:454`
  - `templates/ci/test.yml:32`
  - `src/groundtruth_kb/cli.py:653`

Required action:

1. Change the no-bare-PyPI install check so any
   `pip install ... groundtruth-kb` line fails unless that same install
   reference contains `@`, excluding only deliberate changelog/history text.
2. Add a targeted checker test or self-test fixture proving:
   - `pip install groundtruth-kb` fails;
   - `pip install "groundtruth-kb[search]"` fails;
   - `pip install "groundtruth-kb[search] @ git+https://...@vX.Y.Z"` passes.
3. Re-run:
   - `python -m pytest -q --tb=short -p no:cacheprovider`
   - `python -m ruff check .`
   - `python -m ruff format --check .`
   - `python scripts/check_docs_cli_coverage.py`
   - `python -m mkdocs build --strict --site-dir <temp>`

## Conditions For VERIFIED

Codex can verify the next revision once Prime tightens the no-bare-PyPI install
check to reject extras-only PyPI installs and includes command output showing
the expanded checker still passes on the current clean tree.

## Decision Needed From Owner

No owner policy decision is required. This is a verification NO-GO with a
targeted drift-checker repair.
