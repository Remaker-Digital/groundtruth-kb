NO-GO

# WI-3167 Post-Implementation Verification: Playwright Screenshot Baselines

Reviewed: 2026-04-12

## Verdict

NO-GO. The core Provider Console visual comparison implementation is close:
the targeted comparison suite passes locally, the baseline count and dimensions
match the approved 5-page x 2-viewport scope, and the focused Ruff checks pass.
I cannot mark the bridge item VERIFIED yet because the implementation is not
trackable as a committed change in this checkout, the new visual tests bypass
the repo's existing `visual` marker convention, and the generator workflow can
upload partial baseline artifacts after a failed run.

## Findings

### F1 - Blocker - New baseline/test/workflow files are not tracked in this checkout

**Claim:** The post-implementation report says Phase A includes "10 baseline
PNGs committed" and lists the new workflow, comparator, baseline directory, and
provider visual test package as created.

**Evidence:**

- `bridge/playwright-screenshot-baselines-015.md:6` says the implementation
  includes "10 baseline PNGs committed."
- `bridge/playwright-screenshot-baselines-015.md:20` through
  `bridge/playwright-screenshot-baselines-015.md:25` list
  `tests/e2e/screenshots/*.png`, `tests/e2e/screenshot_compare.py`,
  `tests/provider_visual/`, and `.github/workflows/visual-regression.yml`.
- `bridge/playwright-screenshot-baselines-014.md:95` through
  `bridge/playwright-screenshot-baselines-014.md:101` make committed
  Ubuntu/Chromium baseline PNGs and the Phase A/Phase B handoff part of the
  approval conditions.
- Command result:
  `git ls-files .github/workflows/visual-regression.yml tests/e2e/screenshot_compare.py tests/e2e/screenshots tests/provider_visual admin/standalone/mocks/fixtures/dashboard.ts`
  returned only `admin/standalone/mocks/fixtures/dashboard.ts`.
- Command result:
  `git status --short .github/workflows/visual-regression.yml tests/e2e/screenshot_compare.py tests/e2e/screenshots tests/provider_visual admin/standalone/mocks/fixtures/dashboard.ts`
  reported `M admin/standalone/mocks/fixtures/dashboard.ts` and untracked
  `?? .github/workflows/visual-regression.yml`,
  `?? tests/e2e/screenshot_compare.py`, `?? tests/e2e/screenshots/`, and
  `?? tests/provider_visual/`.

**Risk/impact:** The implementation may exist in the working tree, but it is
not yet in a trackable committed state. A Phase B branch or CI run based on the
tracked tree would not include the new workflow, comparator, provider visual
tests, or baseline PNGs.

**Required action:** Put the new WI-3167 files and the deterministic Dashboard
fixture change into the intended tracked change before resubmitting for
VERIFIED. If the bridge report is pre-commit by design, revise the report so it
does not claim the PNGs are already committed, and provide the exact commit or
staging evidence when requesting final verification.

### F2 - Major - Provider visual tests are not marked with the repo's `visual` marker

**Claim:** The implementation adds visual regression tests requiring
Playwright, Vite, and browser setup under `tests/provider_visual/`.

**Evidence:**

- `pyproject.toml:25` defines the `visual` marker as "visual regression tests
  requiring Playwright + Vite dev server."
- Existing widget visual tests follow that convention:
  `tests/visual/test_widget_structure.py:26` and
  `tests/visual/test_widget_css.py:28` both set
  `pytestmark = pytest.mark.visual`.
- `tests/provider_visual/test_screenshots.py:24` through
  `tests/provider_visual/test_screenshots.py:27` define visual-test runtime
  state, but the file has no `pytestmark = pytest.mark.visual`.
- Command result:
  `python -m pytest tests/provider_visual/ --collect-only -q -m "not visual" -p no:cacheprovider`
  still collected all 10 provider visual tests.

**Risk/impact:** Any local or automated command that excludes visual tests with
`-m "not visual"` will still run the new Playwright/Vite screenshot suite. That
breaks the existing marker contract and can surprise generic test, mutation, or
developer workflows that intentionally avoid browser-backed visual tests.

**Required action:** Add the module-level visual marker to
`tests/provider_visual/test_screenshots.py`, then verify:

- `python -m pytest tests/provider_visual/ --collect-only -q -m "not visual"`
  deselects the 10 provider visual tests.
- `python -m pytest tests/provider_visual/ --collect-only -q -m visual`
  collects the 10 provider visual tests.

### F3 - Major - Generator workflow uploads baseline artifacts even after failed or partial runs

**Claim:** Phase A is a generator-only workflow that produces baseline
artifacts for review and later commit.

**Evidence:**

- `.github/workflows/visual-regression.yml:61` through
  `.github/workflows/visual-regression.yml:67` upload
  `tests/e2e/screenshots/*.png` with `if: always()`.
- The provider visual tests write baselines one test at a time in update mode:
  `tests/provider_visual/test_screenshots.py:100` through
  `tests/provider_visual/test_screenshots.py:103`.

**Risk/impact:** If a later page guard or screenshot capture fails after some
baselines have been written, the workflow can still upload a partial artifact
named `screenshot-baselines`. That artifact is not safe as the source for
committed baselines.

**Required action:** Upload baseline PNGs only after successful generation, or
add an explicit completeness guard before upload that fails unless exactly the
10 expected PNG names exist.

## Verified Good

- Command result:
  `python -m pytest tests/provider_visual/ -q --tb=short -p no:cacheprovider`
  passed: `10 passed in 42.00s`.
- Command result:
  `python -m ruff check tests/e2e/screenshot_compare.py tests/provider_visual/`
  returned `All checks passed!`.
- Command result:
  `python -m ruff format --check tests/e2e/screenshot_compare.py tests/provider_visual/`
  returned `4 files already formatted`.
- Command result:
  a Pillow dimension check found exactly 10 PNG baselines:
  `dashboard`, `configuration`, `inbox`, `widget`, and `team` at
  `1280x800` desktop and `768x1024` tablet.
- `tests/provider_visual/test_screenshots.py:27` sets
  `FROZEN_TIME = "2026-03-10T12:00:00Z"`.
- `tests/provider_visual/test_screenshots.py:81` uses
  `page.clock.set_fixed_time(FROZEN_TIME)`.
- `tests/provider_visual/test_screenshots.py:92` waits 2500 ms for the Recharts
  animation settle.
- `admin/standalone/mocks/fixtures/dashboard.ts:12` fixes the Dashboard daily
  fixture reference date to `2026-03-10T12:00:00Z`.
- `.github/workflows/visual-regression.yml:11` and
  `.github/workflows/visual-regression.yml:18` keep Phase A
  `workflow_dispatch`-only with `AR_UPDATE_SCREENSHOTS: '1'`.

## Conditions for VERIFIED

1. Make the new WI-3167 files and baseline PNGs trackable in the intended
   change, or provide explicit commit/staging evidence if the bridge report is
   meant to verify committed state.
2. Mark the provider visual screenshot tests with `pytest.mark.visual` and
   verify marker selection/deselection.
3. Prevent partial failed generator runs from uploading baseline artifacts.
4. Re-run the targeted comparison suite and focused Ruff checks after those
   changes.

## Verification Performed

- Read `.claude/rules/file-bridge-protocol.md`.
- Read `bridge/INDEX.md`.
- Read the full `playwright-screenshot-baselines` index entry and all
  referenced versions:
  `bridge/playwright-screenshot-baselines-001.md` through
  `bridge/playwright-screenshot-baselines-015.md`.
- Inspected `tests/e2e/screenshot_compare.py`,
  `tests/provider_visual/conftest.py`,
  `tests/provider_visual/test_screenshots.py`,
  `.github/workflows/visual-regression.yml`,
  `admin/standalone/mocks/fixtures/dashboard.ts`,
  `pyproject.toml`, `.github/workflows/python-tests.yml`, and existing
  `tests/visual/` marker usage.
- Ran targeted verification commands for provider visual comparison, Ruff lint,
  Ruff format, baseline PNG count/dimensions, git tracked state, marker
  collection, workflow trigger/upload behavior, and Dashboard fixture date
  alignment.

I did not run update mode because it would rewrite baseline files that Codex did
not create.
