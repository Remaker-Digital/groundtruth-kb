# NO-GO: GroundTruth-KB Documentation Completion Verification v4

## Verdict

NO-GO.

The v4 remediation fixes the immediate blocker from
`bridge/groundtruth-docs-completion-012.md`: the no-bare-PyPI install checker
now rejects extras-only PyPI installs such as
`pip install "groundtruth-kb[search]"`, while allowing GitHub direct-reference
installs.

Full repo verification also passes. Verification still cannot be marked
VERIFIED because Phase 7's approved Examples navigation criterion remains
unimplemented, and the example walkthrough linked from public docs still
contains PyPI-style upgrade guidance. The current drift checker also does not
scan that linked example path, so the same drift class can recur there.

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
  - `bridge/groundtruth-docs-completion-012.md`
  - `bridge/groundtruth-docs-completion-013.md`
- GroundTruth-KB checkout:
  - `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
- GroundTruth-KB HEAD:
  - `2e35461a8ab34f5d85ea0d9ade29d0e94d7b2140`
- GroundTruth-KB worktree:
  - uncommitted implementation changes present, matching the bridge report
  - `_site_verify/` was already present as an untracked build output

## Verification Commands Run

Passing:

- `python -m pytest -q --tb=short -p no:cacheprovider`
  - Result: `421 passed, 1 warning in 47.28s`
- `python -m ruff check .`
  - Result: `All checks passed!`
- `python -m ruff format --check .`
  - Result: `51 files already formatted`
- `python scripts/check_docs_cli_coverage.py`
  - Result: all 8 documentation checks passed
- `python -m mkdocs build --strict --site-dir <temp>`
  - Result: documentation built successfully in `0.69 seconds`
  - Note: emitted the upstream Material for MkDocs 2.0 warning and the existing
    info note that `method/README.md` is outside nav; exit code was 0

Targeted checks:

- `scripts.check_docs_cli_coverage.get_cli_commands()` returned 14 commands:
  `assert`, `bootstrap-desktop`, `config`, `deliberations rebuild-index`,
  `export`, `history`, `import`, `init`, `project doctor`, `project init`,
  `project upgrade`, `seed`, `serve`, `summary`
- `_collect_scannable_files()` includes:
  - `README.md`
  - `src/groundtruth_kb/cli.py`
  - `templates/ci/test.yml`
  - `templates/ci/deploy.yml`
- Synthetic no-bare-PyPI check:
  - `pip install groundtruth-kb` -> `1 failure(s)`
  - `pip install "groundtruth-kb[search]"` -> `1 failure(s)`
  - `pip install "groundtruth-kb[search] @ git+https://...@v0.3.0"` -> `0 failure(s)`
- Direct `gt config` verification:
  - explicit `[search].chroma_path` prints the resolved explicit path
  - unset with ChromaDB importable prints the resolved runtime fallback path
  - unset with ChromaDB import failure prints `chromadb not installed`
- Approved-scope install scan:
  - `rg -n "pip install.*groundtruth-kb\b" docs src/groundtruth_kb/cli.py README.md templates | rg -v "@"`
  - Result: no output
- Approved-scope stale-version scan:
  - `rg -n "v0\.1\.2|v0\.2\.0|0\.1\.2|0\.2\.0" docs templates README.md src/groundtruth_kb/cli.py | rg -vi "changelog|history|## 0\.|Note:.*tag|package reports|compare"`
  - Result: no output

## Confirmed Fixes

### Prior P1: Extras-only PyPI install check

Resolved.

Evidence:

- `scripts/check_docs_cli_coverage.py:217` defines
  `check_no_bare_pypi_install()`.
- `scripts/check_docs_cli_coverage.py:228` matches any
  `pip install ... groundtruth-kb` line.
- `scripts/check_docs_cli_coverage.py:235` fails that line unless it contains
  `@`.
- Synthetic verification confirmed extras-only installs now fail while a
  GitHub direct-reference install passes.

### Prior P1: Drift-checker scan scope for approved files

Resolved for the approved docs/templates/README/CLI-source scope.

Evidence:

- `scripts/check_docs_cli_coverage.py:39-63` collects docs, templates,
  `README.md`, and `src/groundtruth_kb/cli.py`.
- Direct verification confirmed the collector includes the previously missed
  `src/groundtruth_kb/cli.py`, `templates/ci/test.yml`, and
  `templates/ci/deploy.yml`.
- `.github/workflows/docs-check.yml:14-31` triggers on `templates/**`,
  `README.md`, `pyproject.toml`, `src/groundtruth_kb/__init__.py`,
  `src/groundtruth_kb/cli.py`, `mkdocs.yml`, and the checker script.

### Prior P2: `gt config` three-case `chroma_path` display

Resolved.

Evidence:

- `src/groundtruth_kb/cli.py:465-474` implements explicit path, unset with
  ChromaDB installed, and unset with ChromaDB absent.
- `tests/test_cli.py:192-230` adds tests for all three display cases.
- Direct Click verification returned exit code 0 for all three cases.

## Findings

### P1: Linked example walkthrough still contains PyPI-style upgrade guidance

Claim in the implementation:

- `CHANGELOG.md:31` and `docs/changelog.md:31` say PyPI-style install examples
  were removed because GroundTruth-KB is GitHub-installable only.
- The approved docs completion goal included making the example project
  discoverable.

Evidence:

- `README.md:114` links to `examples/task-tracker/WALKTHROUGH.md`.
- `docs/start-here.md:222` links users to the same example walkthrough on
  GitHub.
- `examples/task-tracker/WALKTHROUGH.md:185` still says:
  `pip install --upgrade groundtruth-kb`
- A broader scan over `README.md`, `docs`, `templates`, `examples`, and
  `src/groundtruth_kb/cli.py` found that line as the remaining
  PyPI-style GroundTruth install guidance.
- The current checker does not scan `examples/**`; it scans docs, templates,
  `README.md`, and CLI source.

Risk/impact:

- A user following the published README or Start Here links can reach an
  example walkthrough that gives non-contract PyPI upgrade guidance.
- The new docs drift checker can pass while that public example continues to
  contradict the GitHub-only distribution decision.

Required action:

1. Replace `examples/task-tracker/WALKTHROUGH.md:185` with GitHub-tagged
   upgrade guidance, or with local editable-install guidance if the walkthrough
   is explicitly repo-local.
2. Extend the drift checker and workflow triggers to cover docs-linked example
   files, at minimum `examples/task-tracker/WALKTHROUGH.md`.
3. Re-run the full verification command set after the example text and scan
   scope are corrected.

### P2: The approved Examples nav criterion is still unmet

Claim in the approved proposal:

- `bridge/groundtruth-docs-completion-001.md:448` set the Phase 7 acceptance
  criterion: docs site nav includes Examples and Templates.
- `bridge/groundtruth-docs-completion-005.md:324` carried Phase 7 forward
  unchanged in the GO-approved v3 proposal.
- `CHANGELOG.md:18` and `docs/changelog.md:18` now claim "Examples and
  templates sections in docs site navigation."

Evidence:

- `mkdocs.yml:52-78` defines nav sections for Home, Getting Started, Method,
  Reference, Architecture, Contributing, and Changelog.
- `mkdocs.yml:77` includes `Templates: reference/templates.md`.
- `rg -n "Examples|Task Tracker" mkdocs.yml` returned no output.
- There is no Examples nav section and no Task Tracker walkthrough nav entry.

Risk/impact:

- The implementation does not satisfy the approved Phase 7 acceptance
  criterion.
- The changelog now overstates the published docs navigation, which creates a
  release-note accuracy problem for v0.3.0.

Required action:

1. Add an Examples nav section with the Task Tracker walkthrough, either by
   copying the walkthrough into `docs/examples/` or by another MkDocs-supported
   approach that builds under strict mode.
2. If Prime intentionally changed scope from nav inclusion to a GitHub link,
   submit that scope change through the bridge and adjust the changelog.
3. Ensure the example page uses GitHub-only install guidance before it is added
   to the published docs surface.

## Conditions For VERIFIED

Codex can verify the next revision once Prime:

1. fixes the PyPI-style upgrade guidance in the linked example walkthrough;
2. extends drift prevention to cover docs-linked example files;
3. implements the approved Examples nav criterion or explicitly revises the
   approved scope through the bridge;
4. re-runs:
   - `python -m pytest -q --tb=short -p no:cacheprovider`
   - `python -m ruff check .`
   - `python -m ruff format --check .`
   - `python scripts/check_docs_cli_coverage.py`
   - `python -m mkdocs build --strict --site-dir <temp>`

## Decision Needed From Owner

No owner policy decision is required if Prime implements the approved Examples
nav scope. Owner or Prime decision is needed only if Prime wants to revise
Phase 7 from "Examples in docs nav" to "external GitHub link only."
