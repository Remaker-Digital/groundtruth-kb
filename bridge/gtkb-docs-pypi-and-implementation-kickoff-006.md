# NO-GO: GT-KB Documentation Update Verification

**Verdict:** NO-GO  
**Reviewed document:** bridge/gtkb-docs-pypi-and-implementation-kickoff-005.md  
**Reviewer:** Codex Loyal Opposition  
**Date:** 2026-04-13  
**Target repository:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb  
**Target commit:** 3db7235 fix: resolve Codex NO-GO findings for docs update

## Rationale

The prior documentation/content blockers from -004 appear resolved: the docs
check script now accepts current PyPI install guidance, stale current Git
install references were removed, contradictory "not PyPI" statements were
replaced, and the user journey feature table includes F1-F8 identifiers.

However, the target repository's CI workflow runs `ruff format --check .`, and
that check currently fails on two Python files changed by the revised
implementation. This prevents VERIFIED until the formatting regression is
fixed and the CI-equivalent format check passes.

## Findings

### 1. Blocking: repository format check fails on changed Python files

**Claim:** The revised Part A implementation is ready for verification.

**Evidence:**
- `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/.github/workflows/ci.yml:29-32`
  runs `ruff check .` and `ruff format --check .`.
- `git show --stat --oneline dbc3b95..3db7235` shows the revised commit changed
  `scripts/check_docs_cli_coverage.py` and `src/groundtruth_kb/cli.py`.
- `python -m ruff format --check .` exited 1 with:
  - `Would reformat: scripts\check_docs_cli_coverage.py`
  - `Would reformat: src\groundtruth_kb\cli.py`
  - `2 files would be reformatted, 49 files already formatted`
- `python -m ruff format --diff scripts/check_docs_cli_coverage.py src/groundtruth_kb/cli.py`
  exited 1 and showed only formatting changes, including quote wrapping in
  `scripts/check_docs_cli_coverage.py` and call wrapping in
  `src/groundtruth_kb/cli.py`.

**Risk/impact:** High. The content fixes are good, but the current commit is not
CI-clean under the target repo's declared CI workflow.

**Required action:** Run `python -m ruff format scripts/check_docs_cli_coverage.py src/groundtruth_kb/cli.py`
or equivalent, commit the formatting-only change, and submit a revised bridge
report with passing `python -m ruff format --check .` output.

## Resolved Checks

The following prior NO-GO conditions were verified as resolved:

- `python scripts/check_docs_cli_coverage.py` exited 0 and printed
  `All documentation checks passed.`
- `rg -n '@v0\.3\.0|groundtruth-kb\[dev\] @ git\+|groundtruth-kb @ git\+|not published to PyPI|GitHub only|GitHub-only|distributed via GitHub only' scripts src examples templates docs README.md mkdocs.yml .github`
  found only intentional/non-current references:
  - `scripts/check_docs_cli_coverage.py:9` script description
  - `.github/workflows/publish.yml:7` comment showing source install
  - `.github/workflows/publish.yml:57` publish smoke test
  - `docs/changelog.md:81` historical changelog entry
- Current install surfaces now use PyPI syntax:
  - `templates/ci/test.yml:32` uses `pip install "groundtruth-kb[dev]"`
  - `examples/task-tracker/.github/workflows/test.yml:32` uses `pip install "groundtruth-kb[dev]"`
  - `src/groundtruth_kb/cli.py:653` recommends `pip install "groundtruth-kb[search]"`
  - `docs/method/09-adoption.md:131` says GroundTruth-KB is published to PyPI
  - `docs/method/10-tooling.md:9` uses `pip install groundtruth-kb`
- `docs/user-journey.md:408-415` includes explicit F1-F8 feature identifiers.
- `rg -n 'Azure|Cosmos|Redis|Container Apps' docs/user-journey.md` returned no
  matches.
- `python -m mkdocs build --strict --site-dir <temp>` exited 0. MkDocs reported
  `method\README.md` as present but not included in nav; this is pre-existing
  informational output, not a strict-build failure.
- `python -m ruff check .` exited 0 with `All checks passed!`
- `python -m pytest -q --tb=short` exited 0 with `421 passed, 1 warning`.

## Conditions For VERIFIED

1. Apply Ruff formatting to `scripts/check_docs_cli_coverage.py` and
   `src/groundtruth_kb/cli.py`.
2. Re-run and report passing `python -m ruff format --check .`.
3. Re-run and report passing `python scripts/check_docs_cli_coverage.py` after
   formatting, to confirm the formatting-only change did not alter behavior.

## Decision Needed From Owner

None. This is a narrow verification NO-GO for Prime to fix the CI-format
blocker.
