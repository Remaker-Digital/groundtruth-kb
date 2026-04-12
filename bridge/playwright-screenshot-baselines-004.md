NO-GO

# WI-3167 Review: Playwright Screenshot Baselines v2

Reviewed: 2026-04-12

## Verdict

NO-GO. The revised proposal fixes the original unsupported Playwright
`to_have_screenshot` path in principle, but the proposed Python comparator and
CI trigger contract are still not safe to approve as written.

## Rationale

The v2 direction is closer: it uses `page.screenshot(path=...)`, keeps baselines
under `tests/e2e/screenshots/`, separates visual regression from axe-core, and
removes local Windows baseline generation. The remaining blockers are
implementation-level but material: the comparator imports an undeclared runtime
dependency, and the new visual workflow does not run for changes to the
comparison helper or dependency/config files that can directly affect the visual
gate.

## Findings

### F1 - Blocker - Comparator depends on undeclared `numpy`

**Claim:** The proposal says the helper uses Pillow plus numpy and states that
numpy is available.

**Evidence:**

- `bridge/playwright-screenshot-baselines-003.md:35` imports `Image` and
  `ImageChops` from Pillow.
- `bridge/playwright-screenshot-baselines-003.md:36` imports `numpy as np`.
- `bridge/playwright-screenshot-baselines-003.md:57` and
  `bridge/playwright-screenshot-baselines-003.md:58` use `np.array` and
  `np.count_nonzero`.
- `bridge/playwright-screenshot-baselines-003.md:220` claims "Pillow
  dependency" is already present and "numpy is also available."
- `requirements.txt:60` declares `Pillow>=10.0.0`.
- Command result:
  `rg -n "numpy|Pillow" requirements.txt requirements-test.txt pyproject.toml uv.lock`
  returned only `requirements.txt:60:Pillow>=10.0.0`; no repo dependency file
  declares numpy.
- Command result:
  `python -m pip show numpy Pillow playwright pytest-playwright` found numpy in
  the local user Python environment, but it is required by unrelated local
  packages (`contourpy`, `langchain-community`, `llama-index-core`,
  `matplotlib`, `pandas`), not by this repo's declared test stack.

**Risk/impact:** A clean CI runner following the repo dependency manifests can
fail at import time before any screenshots are captured. Visual regression
cannot be a reliable gate if it depends on ambient transitive or workstation
state.

**Required action:** Either remove the numpy dependency from
`tests/e2e/screenshot_compare.py` and implement the pixel count with Pillow-only
APIs, or add an explicit dependency such as `numpy>=...` to the appropriate
requirements file and ensure the visual workflow installs it.

### F2 - Major - Visual workflow path filters omit files that control the visual gate

**Claim:** The proposal creates the comparator in `tests/e2e/screenshot_compare.py`
and a new visual workflow with path filters.

**Evidence:**

- `bridge/playwright-screenshot-baselines-003.md:25` places the comparator at
  `tests/e2e/screenshot_compare.py`.
- `bridge/playwright-screenshot-baselines-003.md:80` imports that comparator
  from the visual test.
- `bridge/playwright-screenshot-baselines-003.md:153` and
  `bridge/playwright-screenshot-baselines-003.md:156` trigger the visual
  workflow only for `admin/**`, `tests/visual/**`, and
  `tests/e2e/screenshots/**`.
- The proposed path filters omit `tests/e2e/screenshot_compare.py`,
  `requirements*.txt`, `pyproject.toml`, and
  `.github/workflows/visual-regression.yml`.
- Existing repo workflow precedent includes dependency/config/workflow paths:
  `.github/workflows/python-tests.yml:21` through
  `.github/workflows/python-tests.yml:27` include `tests/**`,
  `requirements*.txt`, `pyproject.toml`, and the workflow file itself.
- Existing accessibility workflow precedent includes dependency/config/workflow
  paths: `.github/workflows/accessibility.yml:11` through
  `.github/workflows/accessibility.yml:18` include `requirements*.txt`,
  `pyproject.toml`, and `.github/workflows/accessibility.yml`.

**Risk/impact:** A change to the comparator, dependency manifest, pytest config,
or workflow could bypass the visual regression job on pull requests. That makes
the screenshot gate non-authoritative exactly where it needs to be enforced.

**Required action:** Expand both pull-request and push path filters to include
at least `tests/e2e/screenshot_compare.py`, `requirements*.txt`,
`pyproject.toml`, and `.github/workflows/visual-regression.yml`. Using
`tests/**` is also acceptable if the added CI cost is acceptable.

### F3 - Major - Baseline lifecycle still needs an enforceable landing sequence

**Claim:** The proposal creates an initially empty baseline directory and then
generates baselines through a manual CI update run.

**Evidence:**

- `bridge/playwright-screenshot-baselines-003.md:190` says
  `tests/e2e/screenshots/` is initially empty.
- `bridge/playwright-screenshot-baselines-003.md:198` lists only
  `tests/e2e/screenshots/.gitkeep` as a file to create for the baseline
  directory.
- `bridge/playwright-screenshot-baselines-003.md:47` and
  `bridge/playwright-screenshot-baselines-003.md:48` make missing baselines a
  hard comparison failure.
- `bridge/playwright-screenshot-baselines-003.md:210` through
  `bridge/playwright-screenshot-baselines-003.md:216` describe a separate
  generate-download-commit procedure for the 10 PNG baselines.

**Risk/impact:** If pull-request enforcement is enabled in the same change that
only adds `.gitkeep`, the first enforcement run fails by design because all
baselines are missing. The proposal needs to make the handoff from empty
directory to committed baseline PNGs explicit enough that Prime does not land a
permanently red visual workflow.

**Required action:** Specify that the implementation is not complete until the
10 CI-generated PNG baselines are committed alongside the enforcement workflow,
or split the work into two explicit phases: generator-only workflow first, then
enforcement after baselines are committed.

### F4 - Minor - Test snippet would trip the existing blocking lint gate

**Claim:** The proposed visual test imports `Page` from Playwright.

**Evidence:**

- `bridge/playwright-screenshot-baselines-003.md:79` imports
  `Page, expect` from `playwright.sync_api`.
- The snippet does not use `Page` in the shown test body.
- `.github/workflows/lint.yml:44` through `.github/workflows/lint.yml:47`
  run blocking Ruff `E,F` checks over `src/ tests/`; unused imports are an
  `F`-class pyflakes failure.

**Risk/impact:** Implementing the snippet literally can fail the blocking lint
workflow even if the visual behavior is otherwise correct.

**Required action:** Drop the unused `Page` import or use it in a real type
annotation.

## Conditions for GO

1. Make the comparator dependency-closed: no undeclared numpy import, or declare
   and install numpy explicitly.
2. Expand the visual workflow path filters so comparator, dependency, pytest
   config, and workflow changes trigger the visual job.
3. Define a landing sequence that commits the 10 Ubuntu/Chromium baseline PNGs
   before enabling normal pull-request enforcement, or split generation and
   enforcement into separate phases.
4. Clean up the proposed test snippet so it passes the repo's blocking Ruff
   `E,F` lint gate.

## Verification Performed

- Read `.claude/rules/file-bridge-protocol.md`.
- Read `bridge/INDEX.md`.
- Read the full `playwright-screenshot-baselines` index entry and all referenced
  versions: `bridge/playwright-screenshot-baselines-001.md`,
  `bridge/playwright-screenshot-baselines-002.md`, and
  `bridge/playwright-screenshot-baselines-003.md`.
- Inspected `requirements.txt`, `requirements-test.txt`, `pyproject.toml`,
  `.github/workflows/accessibility.yml`, `.github/workflows/python-tests.yml`,
  `.github/workflows/lint.yml`, `tests/accessibility/conftest.py`, and
  `tests/accessibility/test_axe_ci.py`.
- Ran targeted checks:
  `rg -n "numpy|Pillow" requirements.txt requirements-test.txt pyproject.toml uv.lock`,
  `python -m pip show numpy Pillow playwright pytest-playwright`,
  `Get-ChildItem .github/workflows | Select-Object -ExpandProperty Name`, and
  `rg -n "tests/e2e/screenshot_compare|tests/e2e/screenshots|tests/visual|requirements\\*|pyproject|visual-regression\\.yml|workflow_dispatch" bridge/playwright-screenshot-baselines-003.md`.

No full test run was performed because the proposal has not been implemented.
