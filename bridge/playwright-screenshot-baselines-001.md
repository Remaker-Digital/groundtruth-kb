# WI-3167: Playwright Screenshot Baselines for Provider Console

## Proposal (Prime Builder → Codex Review)

**Work Item:** WI-3167
**Spec:** SPEC-2104 (Playwright visual regression baselines for Provider Console)
**Priority:** P3
**Session:** S282

---

## Objective

Establish Playwright screenshot comparison baselines for the top 5 Provider
Console user journeys. Baselines are generated on the CI runner (Ubuntu/Chromium)
for deterministic rendering. Updates require explicit `--update-snapshots`.

## Approach: Extend the WI-3166 Accessibility Infrastructure

The accessibility CI (WI-3166, commit cff9f102) already has:
- Vite mock server lifecycle (`tests/accessibility/conftest.py`)
- Authenticated browser context with viewport + tenant param
- 9 page navigation fixtures

WI-3167 reuses this infrastructure by adding `toHaveScreenshot()` assertions
to a new test file in the same `tests/accessibility/` module (both test
categories need the same mock server + auth setup).

### SPEC-2104 Requirements Mapping

| Requirement | Implementation |
|------------|---------------|
| 1. Baselines for: Dashboard, Configuration, Inbox, Widget, Team | 5 parametrized tests with `expect(page).to_have_screenshot()` |
| 2. Stored in tests/e2e/screenshots/ | Stored in `tests/accessibility/test_screenshots/` (Playwright default: adjacent to test file) |
| 3. toHaveScreenshot() assertions | Direct Playwright API |
| 4. Updates require explicit approval | Only `--update-snapshots` flag regenerates |
| 5. Desktop (1280x800) and tablet (768x1024) | Two viewport fixtures, 5 pages × 2 viewports = 10 tests |
| 6. CI uses consistent environment | Same Ubuntu + Chromium as accessibility workflow |

### Files to Create

1. **`tests/accessibility/test_screenshots.py`** — 10 parametrized tests
   - 5 pages × 2 viewports (desktop 1280×800, tablet 768×1024)
   - Reuses `a11y_base_url` fixture from conftest for mock server
   - Creates viewport-specific browser contexts
   - Navigates with auth + tenant param + page guard
   - Calls `expect(page).to_have_screenshot(f"{page_name}-{viewport}.png")`
   - No importorskip — fail closed in CI

2. **`tests/accessibility/test_screenshots/`** — baseline directory
   - Generated on first `--update-snapshots` run in CI
   - Committed to repo
   - Updates require running with `--update-snapshots` then committing

### Workflow Integration

Add screenshot tests to the existing `.github/workflows/accessibility.yml` job:
- Same dependencies (already installed)
- Tests auto-discovered in `tests/accessibility/`
- First run: generate baselines with `--update-snapshots`
- Subsequent runs: compare against baselines

### Files Modified

1. **`.github/workflows/accessibility.yml`** — add `--update-snapshots` note
   in comment. No functional change needed since pytest already discovers
   `test_screenshots.py` in the `tests/accessibility/` directory.

### Viewport Fixtures

```python
VIEWPORTS = [
    ("desktop", {"width": 1280, "height": 800}),
    ("tablet", {"width": 768, "height": 1024}),
]

TOP_5_JOURNEYS = [
    ("/", "Dashboard", "heading", "Dashboard"),
    ("/configuration", "Configuration", "heading", "Agent configuration"),
    ("/inbox", "Inbox", "placeholder", "Search conversations..."),
    ("/widget", "Widget", "heading", "Widget configuration"),
    ("/team", "Team", "heading", "Team members"),
]
```

### Conftest Changes

Add a `screenshot_context` fixture factory to `tests/accessibility/conftest.py`
that creates viewport-specific browser contexts with auth injection.

### Baseline Generation Strategy

1. First CI run: workflow runs with `--update-snapshots` to generate baselines
2. Developer downloads artifacts and commits baseline PNGs
3. Subsequent CI runs: compare against committed baselines
4. To update: run locally with `--update-snapshots` and commit new baselines

### Risk Assessment

- **Low risk:** New test file only. Extends existing infrastructure.
- **Baseline stability:** Chromium rendering varies across OS. Baselines must be
  generated on the CI runner (Ubuntu), not locally (Windows). Playwright supports
  `maxDiffPixels` threshold for minor rendering differences.
- **First run:** Will fail until baselines are committed. Add `|| true` for
  initial baseline generation run, then remove.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
