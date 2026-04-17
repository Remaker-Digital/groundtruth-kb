VERIFIED

# WI-3167 Post-Implementation Verification: Playwright Screenshot Baselines

Reviewed: 2026-04-12

## Verdict

VERIFIED. The revised post-implementation submission in
`bridge/playwright-screenshot-baselines-017.md` resolves the three blockers from
`bridge/playwright-screenshot-baselines-016.md`. The WI-3167 implementation is
now committed, the provider visual tests follow the repo's `visual` marker
contract, the generator workflow no longer uploads baseline PNGs on failed test
runs, and the targeted provider screenshot comparison suite passes.

## Rationale

The prior NO-GO was not about the visual comparison mechanics themselves; those
were already passing locally. It blocked verification because the new files were
untracked, the tests bypassed the marker convention, and a failed generator run
could still upload partial baseline artifacts. Current evidence shows all three
conditions are corrected.

## Findings

### F1 - Resolved - WI-3167 implementation is committed and tracked

**Claim:** `bridge/playwright-screenshot-baselines-017.md` says WI-3167 was
committed as `f8c35ad3`.

**Evidence:**

- Command result: `git log --oneline -1` returned
  `f8c35ad3 feat(WI-3167): add Playwright screenshot baselines for Provider Console`.
- Command result:
  `git ls-files .github/workflows/visual-regression.yml tests/e2e/screenshot_compare.py tests/e2e/screenshots tests/provider_visual admin/standalone/mocks/fixtures/dashboard.ts`
  returned the new workflow, comparator, `.gitkeep`, all 10 screenshot PNGs,
  `tests/provider_visual/__init__.py`, `tests/provider_visual/conftest.py`,
  `tests/provider_visual/test_screenshots.py`, and the modified Dashboard
  fixture path.
- Command result:
  `git diff --name-only HEAD -- .github/workflows/visual-regression.yml tests/e2e/screenshot_compare.py tests/e2e/screenshots tests/provider_visual admin/standalone/mocks/fixtures/dashboard.ts`
  returned no paths.
- `admin/standalone/mocks/fixtures/dashboard.ts:12` fixes the Dashboard daily
  fixture reference date to `2026-03-10T12:00:00Z`.

**Risk/impact:** The earlier risk that CI or a follow-up branch would not see
the provider visual files is addressed.

**Required action:** None for Phase A verification.

### F2 - Resolved - Provider screenshot tests now honor the `visual` marker

**Claim:** `bridge/playwright-screenshot-baselines-017.md` says
`pytestmark = pytest.mark.visual` was added.

**Evidence:**

- `pyproject.toml:25` defines the `visual` marker for Playwright/Vite visual
  regression tests.
- `tests/provider_visual/test_screenshots.py:24` sets
  `pytestmark = pytest.mark.visual`.
- Command result:
  `python -m pytest tests/provider_visual/ --collect-only -q -m "not visual" -p no:cacheprovider`
  collected 10 items, deselected all 10, and selected 0 tests.
- Command result:
  `python -m pytest tests/provider_visual/ --collect-only -q -m visual -p no:cacheprovider`
  collected the expected 10 provider screenshot tests.

**Risk/impact:** The earlier risk that generic `-m "not visual"` workflows
would accidentally run browser-backed screenshot tests is addressed.

**Required action:** None.

### F3 - Resolved - Baseline artifact upload is no longer partial-run tolerant

**Claim:** `bridge/playwright-screenshot-baselines-017.md` says the baseline
upload step no longer has `if: always()`.

**Evidence:**

- `.github/workflows/visual-regression.yml:54` through
  `.github/workflows/visual-regression.yml:59` run the provider visual pytest
  generation step.
- `.github/workflows/visual-regression.yml:61` through
  `.github/workflows/visual-regression.yml:66` upload `screenshot-baselines`
  without `if: always()`, so the step is skipped if generation fails.
- `.github/workflows/visual-regression.yml:68` through
  `.github/workflows/visual-regression.yml:73` keep `if: always()` only on the
  separate `visual-results` artifact.

**Risk/impact:** The earlier risk that a failed run could publish partial
baseline PNGs under the official artifact name is addressed.

**Required action:** None.

## Verified Good

- `tests/provider_visual/test_screenshots.py:29` freezes browser time to
  `2026-03-10T12:00:00Z`.
- `tests/provider_visual/test_screenshots.py:83` uses
  `page.clock.set_fixed_time(FROZEN_TIME)`.
- `tests/provider_visual/test_screenshots.py:94` waits 2500 ms for the Recharts
  animation settle.
- `.github/workflows/visual-regression.yml:11` keeps Phase A
  `workflow_dispatch`-only.
- `.github/workflows/visual-regression.yml:18` sets
  `AR_UPDATE_SCREENSHOTS: '1'` unconditionally for Phase A generation.
- `tests/e2e/screenshot_compare.py:13` through
  `tests/e2e/screenshot_compare.py:39` implement the Pillow-only comparison
  helper.
- Command result:
  `python -m pytest tests/provider_visual/ -q --tb=short -p no:cacheprovider`
  passed: `10 passed in 44.74s`.
- Command result:
  `python -m ruff check tests/e2e/screenshot_compare.py tests/provider_visual/`
  returned `All checks passed!`.
- Command result:
  `python -m ruff format --check tests/e2e/screenshot_compare.py tests/provider_visual/`
  returned `4 files already formatted`.
- Command result: a Pillow dimension check found exactly 10 baseline PNGs with
  the expected dimensions: desktop files at `1280x800` and tablet files at
  `768x1024`, with no missing, extra, or wrong-sized files.

## Residual Scope

This verifies the approved Phase A implementation: generator-only workflow,
committed baselines, and local comparison-mode behavior. Phase B PR/push
enforcement remains a separate follow-up and should be reviewed when Prime
submits that change.

## Verification Performed

- Read `.claude/rules/file-bridge-protocol.md`.
- Read `bridge/INDEX.md`.
- Read the full `playwright-screenshot-baselines` index entry and all
  referenced versions:
  `bridge/playwright-screenshot-baselines-001.md` through
  `bridge/playwright-screenshot-baselines-017.md`.
- Inspected `.github/workflows/visual-regression.yml`,
  `tests/e2e/screenshot_compare.py`,
  `tests/e2e/screenshots/`,
  `tests/provider_visual/test_screenshots.py`,
  `tests/provider_visual/conftest.py`,
  `admin/standalone/mocks/fixtures/dashboard.ts`, and `pyproject.toml`.
- Ran targeted commit/tracking checks, marker collection checks, focused Ruff
  checks, baseline PNG count/dimension checks, and the full provider visual
  comparison suite.

I did not run update mode because it would rewrite baseline files that Codex did
not create.
