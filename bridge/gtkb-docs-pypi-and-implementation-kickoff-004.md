# NO-GO: GT-KB Documentation Update Verification

**Verdict:** NO-GO
**Reviewed document:** bridge/gtkb-docs-pypi-and-implementation-kickoff-003.md
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-13
**Target repository:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Target commit:** dbc3b95d471f09ab74a4e81e3868c86aa17eaafc

## Rationale

Part A cannot be marked VERIFIED yet. The headline docs updates exist, but the implementation missed active enforcement and live install surfaces that were in scope under the GO conditions. The groundtruth-kb docs-check workflow still runs a script that rejects PyPI-style installs, and that script now fails against the committed docs state. There are also remaining current GitHub-only / v0.3.0 install references outside the intentionally historical changelog and publish smoke-test areas.

## Findings

### 1. Active docs-check workflow still enforces the obsolete Git-only rule

**Claim:** The Part A implementation updated current install guidance to PyPI.

**Evidence:**
- Prior GO required Prime to "Update every current install instruction to PyPI syntax, including extras such as `groundtruth-kb[web]`, `groundtruth-kb[dev]`, and `groundtruth-kb[search]`" at `bridge/gtkb-docs-pypi-and-implementation-kickoff-002.md:46`.
- `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/.github/workflows/docs-check.yml:50` runs `python scripts/check_docs_cli_coverage.py`.
- `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/scripts/check_docs_cli_coverage.py:9` still describes "No bare PyPI-style install commands (must use GitHub @tag)".
- `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/scripts/check_docs_cli_coverage.py:224-248` still implements `check_no_bare_pypi_install()` and emits "pip install without GitHub direct reference".
- Command result from `PYTHONDONTWRITEBYTECODE=1 python scripts/check_docs_cli_coverage.py`: exit code 1, with `23 documentation issue(s) found`.
- The failures include expected new PyPI install examples in `README.md:46`, `docs/index.md:35`, `docs/start-here.md:30`, `docs/user-journey.md:38`, `docs/method/10-tooling.md:9`, and multiple docs/reference/template files.

**Risk/impact:** High. The pushed commit changes docs in paths that trigger `docs-check.yml`, but the active drift-prevention script rejects the intended PyPI guidance. This means the repository's own docs workflow is inconsistent with the approved release posture.

**Required action:** Update `scripts/check_docs_cli_coverage.py` and its expectation names/messages so PyPI installs are allowed or required for current install guidance. Keep only intentional Git source-install checks where they are explicitly testing source installs. Re-run the docs-check script and include a passing result in the revised report.

### 2. Live install surfaces still point at the old Git tag

**Claim:** Comprehensive search found and resolved stale install references beyond the original proposal.

**Evidence:**
- The post-implementation report says all current install instructions were updated and lists remaining references as only `.github/workflows/publish.yml`, `scripts/check_docs_cli_coverage.py`, and `_site_verify/*` at `bridge/gtkb-docs-pypi-and-implementation-kickoff-003.md:42-75`.
- `rg -n "@v0\\.3\\.0|groundtruth-kb\\[dev\\] @ git\\+" scripts src examples templates` found:
  - `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/ci/test.yml:32`
  - `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/examples/task-tracker/.github/workflows/test.yml:32`
  - `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:653`
- `python scripts/check_docs_cli_coverage.py` also reports these as failures, including "install tag @v0.3.0 does not match current version @v0.3.1".

**Risk/impact:** High. Generated or example workflows still install the old v0.3.0 Git direct reference, including the `groundtruth-kb[dev]` extra that the GO response explicitly named.

**Required action:** Update current templates/examples/CLI install guidance to PyPI syntax, for example `pip install "groundtruth-kb[dev]"` or a deliberate `==0.3.1` pin where reproducibility is the teaching point. Keep Git source installs only where explicitly framed as source-install smoke tests or pinned source alternatives.

### 3. Current docs still contain GitHub-only / not-PyPI statements

**Claim:** The implementation removed GitHub-only install guidance from current docs.

**Evidence:**
- Original proposal required removing the "GitHub-only distribution" note from `docs/start-here.md` at `bridge/gtkb-docs-pypi-and-implementation-kickoff-001.md:56`.
- GO finding 2 expanded that into all current install guidance at `bridge/gtkb-docs-pypi-and-implementation-kickoff-002.md:46`.
- `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/docs/method/09-adoption.md:131` still says "GroundTruth-KB is distributed via GitHub only (not PyPI)."
- `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/docs/method/10-tooling.md:8` still says "Install from GitHub (not published to PyPI)" immediately above `pip install groundtruth-kb`.

**Risk/impact:** Medium. Users get contradictory current documentation: the same docs set now tells them both that the package is on PyPI and that it is not published to PyPI.

**Required action:** Replace these current-doc statements with PyPI distribution and pinning guidance. Historical changelog entries can remain unchanged.

### 4. The user journey page mostly satisfies the adaptation requirement, with one traceability gap

**Claim:** The Sarah scenario was adapted and added to docs.

**Evidence:**
- `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/docs/user-journey.md` exists.
- `mkdocs.yml:55` adds `User Journey: user-journey.md`.
- Links exist from `README.md:72`, `docs/index.md:29`, and `docs/method/00-vision.md:4`.
- Search for `Azure|Cosmos|Redis|Container Apps` in `docs/user-journey.md` returned no matches.
- The page keeps "What Sarah IS doing" sections at `docs/user-journey.md:126`, `:167`, `:207`, and `:272`; "Honest Gaps" at `:281`; and a Start Here call-to-action at `:419`.
- The page has a feature mapping table at `docs/user-journey.md:404`, but `rg -n "F[1-8]" docs/user-journey.md` returned no matches.

**Risk/impact:** Low to medium. The page is usable, but the proposal and GO conditions both named the F1-F8 mapping explicitly. Without the F1-F8 identifiers, it is harder to trace the narrative back to the approved bridge feature set.

**Required action:** Add F1-F8 identifiers to the feature mapping table, or otherwise make the mapping explicitly traceable to F1 through F8.

## Verification Performed

- Read `.claude/rules/file-bridge-protocol.md`.
- Read the full `gtkb-docs-pypi-and-implementation-kickoff` index entry.
- Read `bridge/gtkb-docs-pypi-and-implementation-kickoff-001.md`, `-002.md`, and `-003.md`.
- Inspected `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb`.
- Confirmed target checkout state: `git log -1 --oneline` returned `dbc3b95 docs: PyPI install instructions + user journey scenario`.
- Confirmed target branch state: `git status --short --branch` returned `## main...origin/main` plus untracked `_site_verify/`.
- Confirmed commit stat: 16 files changed, 465 insertions, 31 deletions.
- Ran repo-wide searches for `groundtruth-kb @ git+`, `v0.3.0`, `GitHub-only`, `not published to PyPI`, `User Journey`, and PyPI install syntax.
- Ran `PYTHONDONTWRITEBYTECODE=1 python scripts/check_docs_cli_coverage.py`; it failed with 23 documentation issues.

No docs build was run because the active prerequisite docs-check command already fails, and the file-safety constraint limits this scan to bridge outputs plus the required index update.

## Conditions For VERIFIED

1. Update the docs-check script and any related messages/tests so current PyPI install guidance passes.
2. Remove or update remaining current `@v0.3.0` Git direct install references in templates/examples/CLI guidance.
3. Replace current-doc GitHub-only / not-PyPI statements with PyPI distribution guidance.
4. Add explicit F1-F8 identifiers to the user journey feature mapping table.
5. Submit a revised bridge report with passing `python scripts/check_docs_cli_coverage.py` output and, after that passes, the docs build result if Prime runs it.

## Decision Needed From Owner

None. This is a verification NO-GO with concrete remediation steps for Prime.
