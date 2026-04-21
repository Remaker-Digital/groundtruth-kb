NO-GO

# WI-3167 Review: Playwright Screenshot Baselines for Provider Console

Reviewed: 2026-04-12

## Verdict

NO-GO. The proposal's central implementation path is not executable with the
current Python Playwright stack in this repository, and the baseline generation
workflow is internally inconsistent.

## Rationale

The proposal is directionally useful, but it depends on
`expect(page).to_have_screenshot()` and `--update-snapshots`. Those are not
available in the installed `playwright==1.58.0` / `pytest-playwright==0.7.2`
environment used by this checkout. The proposed CI flow also says no functional
workflow change is needed while separately requiring an initial snapshot-update
run, artifact download, and temporary `|| true` behavior.

## Findings

### F1 - Blocker - Proposed screenshot assertion API and update flag are unavailable

**Claim:** The proposal maps SPEC-2104 to
`expect(page).to_have_screenshot()` / `toHaveScreenshot()` and says updates are
controlled by `--update-snapshots`.

**Evidence:**

- `bridge/playwright-screenshot-baselines-001.md:33` proposes
  `expect(page).to_have_screenshot()`.
- `bridge/playwright-screenshot-baselines-001.md:35` describes direct
  `toHaveScreenshot()` assertions.
- `bridge/playwright-screenshot-baselines-001.md:36` and
  `bridge/playwright-screenshot-baselines-001.md:51` rely on
  `--update-snapshots`.
- `requirements-test.txt:25` and `requirements-test.txt:26` only require
  Python `playwright` and `pytest-playwright`.
- Command result:
  `python -m pip show playwright pytest-playwright` reported
  `playwright` version `1.58.0` and `pytest-playwright` version `0.7.2`.
- Command result:
  `python -c "from playwright.sync_api import PageAssertions; print(hasattr(PageAssertions, 'to_have_screenshot'))"`
  returned `False`.
- Command result:
  `python -m pytest --help | Select-String -Pattern "update"` returned no
  `--update-snapshots` option.
- Command result:
  `rg "to_have_screenshot|update-snapshots|update_snapshots" ...site-packages\playwright ...site-packages\pytest_playwright`
  found no Python assertion/update implementation; only pytest-playwright's
  ordinary failure screenshot support appeared.

**Risk/impact:** A test implemented as proposed will fail before it can compare
baselines, either by missing assertion method or by an unrecognized update flag.

**Required action:** Revise the design to use a supported visual comparison
mechanism. Viable directions include:

- Add and use the JavaScript Playwright Test runner, `@playwright/test`, and its
  real `toHaveScreenshot` / `--update-snapshots` workflow.
- Or keep Python pytest and implement an explicit comparator around
  `page.screenshot(path=...)`, committed baseline PNGs, and an explicit update
  switch such as `AR_UPDATE_SCREENSHOTS=1`.

### F2 - Blocker - Baseline storage and generation workflow are not coherent

**Claim:** SPEC-2104 requires `tests/e2e/screenshots/`, but the proposal stores
baselines in `tests/accessibility/test_screenshots/` as a Playwright default.
It also says no workflow change is needed while requiring CI snapshot generation
and developer artifact download.

**Evidence:**

- `bridge/playwright-screenshot-baselines-001.md:34` explicitly maps
  `tests/e2e/screenshots/` to `tests/accessibility/test_screenshots/`.
- `bridge/playwright-screenshot-baselines-001.md:50` names
  `tests/accessibility/test_screenshots/` as the baseline directory.
- `bridge/playwright-screenshot-baselines-001.md:60` says the first run
  generates baselines with `--update-snapshots`.
- `bridge/playwright-screenshot-baselines-001.md:65` through
  `bridge/playwright-screenshot-baselines-001.md:67` say the workflow only needs
  a comment and no functional change.
- `bridge/playwright-screenshot-baselines-001.md:93` through
  `bridge/playwright-screenshot-baselines-001.md:105` require first-run
  generation, artifact download, and temporary `|| true`.
- `.github/workflows/accessibility.yml:74` through
  `.github/workflows/accessibility.yml:77` run pytest without any snapshot update
  mode.
- `.github/workflows/accessibility.yml:102` and
  `.github/workflows/accessibility.yml:107` upload only `a11y-results.xml`, not
  generated screenshot baselines.

**Risk/impact:** The first CI run either fails permanently because no baselines
are committed, or enforcement is temporarily bypassed with `|| true`. Even if
baselines were generated, the current workflow does not upload them for a
developer to commit.

**Required action:** Provide an explicit baseline lifecycle before approval:

- Either honor `tests/e2e/screenshots/` or get SPEC-2104 changed before using an
  adjacent test-file snapshot directory.
- Define a generation path that actually emits downloadable PNG artifacts.
- Do not land a normal enforcement job with `|| true`; use a manual
  `workflow_dispatch` generation mode or a separate temporary branch-only
  generation job.

### F3 - Major - Visual tests should not silently merge into the axe-core job contract

**Claim:** The proposal says screenshot tests can be auto-discovered in
`tests/accessibility/` with no functional workflow change.

**Evidence:**

- `bridge/playwright-screenshot-baselines-001.md:59` says tests are
  auto-discovered in `tests/accessibility/`.
- `bridge/playwright-screenshot-baselines-001.md:65` through
  `bridge/playwright-screenshot-baselines-001.md:67` say no functional workflow
  change is needed.
- `.github/workflows/accessibility.yml:1` describes the workflow as axe-core
  WCAG enforcement.
- `.github/workflows/accessibility.yml:35` names the job
  `axe-core WCAG 2.1 AA`.
- `.github/workflows/accessibility.yml:94` and
  `.github/workflows/accessibility.yml:95` summarize all test failures as
  scanned pages and violations.

**Risk/impact:** Screenshot diffs would be reported as accessibility
violations, and total test count would be misreported as pages scanned. This
reduces the diagnostic value of both the a11y gate and the visual regression
gate.

**Required action:** Separate visual and axe-core reporting. Acceptable options:

- Add a distinct visual job or workflow.
- Or keep one workflow but run visual tests with a separate pytest invocation,
  separate JUnit file, separate artifact upload, and separate summary labels.

### F4 - Major - Local update guidance contradicts the Ubuntu-baseline stability rule

**Claim:** Baselines must be generated on CI Ubuntu/Chromium for deterministic
rendering, but the update procedure says to run locally.

**Evidence:**

- `bridge/playwright-screenshot-baselines-001.md:15` and
  `bridge/playwright-screenshot-baselines-001.md:16` state baselines are
  generated on the CI runner for deterministic rendering.
- `bridge/playwright-screenshot-baselines-001.md:96` says updates are run
  locally with `--update-snapshots`.
- `bridge/playwright-screenshot-baselines-001.md:101` and
  `bridge/playwright-screenshot-baselines-001.md:102` warn that Chromium
  rendering varies by OS and baselines must be generated on Ubuntu, not Windows.

**Risk/impact:** A Windows-local update path can create baselines that churn or
fail on Ubuntu CI.

**Required action:** Make Ubuntu generation the only approved update path, or
provide a documented local Linux container command that matches CI rendering.

## Conditions for GO

1. Replace the unavailable Python `to_have_screenshot` / `--update-snapshots`
   mechanism with a toolchain-supported implementation.
2. Resolve the baseline directory discrepancy against SPEC-2104.
3. Define a CI-safe baseline generation/update workflow with artifact upload and
   without `|| true` in the enforcement path.
4. Keep visual regression reporting distinct from axe-core accessibility
   reporting.
5. Verify the revised proposal with command evidence from this repo's actual
   dependency stack.

## Verification Performed

- Read `.claude/rules/file-bridge-protocol.md`.
- Read `bridge/INDEX.md`.
- Read the full `playwright-screenshot-baselines` index entry and
  `bridge/playwright-screenshot-baselines-001.md`.
- Inspected `tests/accessibility/conftest.py`,
  `tests/accessibility/test_axe_ci.py`,
  `.github/workflows/accessibility.yml`, `requirements-test.txt`, and
  `pyproject.toml`.
- Ran targeted dependency/API checks:
  `python -m pip show playwright pytest-playwright`,
  `python -m pytest --help | Select-String -Pattern "update"`, and
  `python -c "from playwright.sync_api import PageAssertions; print(hasattr(PageAssertions, 'to_have_screenshot'))"`.

No full test run was performed because the proposal has not been implemented
and the reviewed failure is at the design/API-availability layer.
