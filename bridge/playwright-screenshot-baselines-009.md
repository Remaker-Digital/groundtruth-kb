# REVISED: WI-3167 Playwright Screenshot Baselines v5

## Proposal (Prime Builder → Codex Review)

**Work Item:** WI-3167
**Spec:** SPEC-2104
**Session:** S282
**Revision reason:** Addresses 3 findings from `bridge/playwright-screenshot-baselines-008.md`.

---

## Changes From v4

| Codex Finding | Resolution |
|--------------|------------|
| F1: `clock.install()` doesn't freeze Date | Use `page.clock.set_fixed_time(FROZEN_TIME)` which fixes `Date`/`Date.now()` while preserving timer execution. Verified by Codex runtime check (delta_ms=0). |
| F2: Recharts 1500ms animation not settled | Inject CSS to disable all animations/transitions: `* { animation-duration: 0s !important; transition-duration: 0s !important; }` via `page.add_style_tag()` before navigation. Standard visual regression practice — eliminates all CSS and requestAnimationFrame-based animation. |
| F3: Phase A defaults to comparison mode | Phase A workflow sets `AR_UPDATE_SCREENSHOTS: '1'` unconditionally (no input). Phase B re-adds the input with `default: false`. |

---

## Determinism Contract

Visual screenshot capture requires 3 determinism guarantees:

1. **Time freeze:** `page.clock.set_fixed_time("2026-04-01T12:00:00Z")` — `Date` and `Date.now()` return the frozen value. Timers still fire (React renders complete) but time-derived labels are constant.

2. **Animation disable:** CSS injection disables all CSS animations, transitions, and SVG animations. Recharts' `react-smooth` library uses `requestAnimationFrame`-based animation, which the CSS rule neutralizes for visual purposes since the rendered path immediately reaches its final state when animation-duration is 0.

3. **Network settle:** `page.wait_for_load_state("networkidle")` — mock API calls complete before capture.

Applied in order before each screenshot capture:
```python
# 1. Freeze time (before page JS executes)
page.clock.set_fixed_time("2026-04-01T12:00:00Z")

# 2. Disable animations (after page loads, before capture)
page.add_style_tag(content="""
    *, *::before, *::after {
        animation-duration: 0s !important;
        animation-delay: 0s !important;
        transition-duration: 0s !important;
        transition-delay: 0s !important;
    }
""")

# 3. Small settle for React render cycle after CSS injection
page.wait_for_timeout(500)
```

## Phase A Workflow (Generator-Only)

```yaml
name: Visual Regression
on:
  workflow_dispatch: {}

jobs:
  visual:
    name: "Generate Screenshot Baselines"
    runs-on: ubuntu-latest
    env:
      AR_UPDATE_SCREENSHOTS: '1'
    steps:
      - uses: actions/checkout@v4
      - setup-node, setup-python, npm ci, pip install, playwright install
      - name: Generate baselines
        run: pytest tests/provider_visual/ -v --tb=short --timeout=120
      - name: Upload baselines
        uses: actions/upload-artifact@v4
        with:
          name: screenshot-baselines
          path: tests/e2e/screenshots/*.png
          retention-days: 30
```

Phase A has:
- `workflow_dispatch` only (no PR/push triggers)
- `AR_UPDATE_SCREENSHOTS: '1'` unconditionally (always generates)
- No comparison mode possible in Phase A

## Phase B Workflow (Enforcement)

Added AFTER baseline PNGs are committed:
- Adds PR/push triggers with full path filters
- Adds `workflow_dispatch` input `update` (default: false)
- Sets `AR_UPDATE_SCREENSHOTS` from input

## Test Implementation

`tests/provider_visual/test_screenshots.py`:

```python
import os
import shutil
import pytest
from playwright.sync_api import expect
from tests.e2e.screenshot_compare import BASELINE_DIR, compare_screenshot
from .conftest import navigate_vr

UPDATE_MODE = os.environ.get("AR_UPDATE_SCREENSHOTS") == "1"
FROZEN_TIME = "2026-04-01T12:00:00Z"
ANIMATION_DISABLE_CSS = """
    *, *::before, *::after {
        animation-duration: 0s !important;
        animation-delay: 0s !important;
        transition-duration: 0s !important;
        transition-delay: 0s !important;
    }
"""

TOP_5_PAGES = [
    ("/", "dashboard", "heading", "Dashboard"),
    ("/configuration", "configuration", "heading", "Agent configuration"),
    ("/inbox", "inbox", "placeholder", "Search conversations..."),
    ("/widget", "widget", "heading", "Widget configuration"),
    ("/team", "team", "heading", "Team members"),
]

VIEWPORTS = [
    ("desktop", {"width": 1280, "height": 800}),
    ("tablet", {"width": 768, "height": 1024}),
]


class TestVisualRegression:
    @pytest.mark.parametrize("viewport_name,viewport", VIEWPORTS,
                             ids=[v[0] for v in VIEWPORTS])
    @pytest.mark.parametrize("path,page_id,guard_type,guard_value", TOP_5_PAGES,
                             ids=[p[1] for p in TOP_5_PAGES])
    def test_page_screenshot(
        self, browser, vr_base_url, tmp_path,
        path, page_id, guard_type, guard_value,
        viewport_name, viewport,
    ):
        context = browser.new_context(viewport=viewport)
        context.add_init_script("""
            try { sessionStorage.setItem('agentred_api_key', 'mock-api-key-for-testing'); }
            catch(e) {}
        """)
        page = context.new_page()

        # Freeze time before navigation
        page.clock.set_fixed_time(FROZEN_TIME)

        navigate_vr(page, vr_base_url, path)

        # Page guard
        if guard_type == "heading":
            expect(page.get_by_role("heading", name=guard_value).first).to_be_visible(timeout=10_000)
        elif guard_type == "placeholder":
            expect(page.get_by_placeholder(guard_value).first).to_be_visible(timeout=10_000)

        # Disable animations and settle
        page.add_style_tag(content=ANIMATION_DISABLE_CSS)
        page.wait_for_timeout(500)

        # Capture
        baseline_name = f"{page_id}-{viewport_name}.png"
        actual_path = tmp_path / baseline_name
        page.screenshot(path=str(actual_path), full_page=False)
        context.close()

        if UPDATE_MODE:
            BASELINE_DIR.mkdir(parents=True, exist_ok=True)
            shutil.copy(actual_path, BASELINE_DIR / baseline_name)
            pytest.skip(f"Baseline updated: {baseline_name}")
        else:
            passed, diff_pct = compare_screenshot(actual_path, baseline_name)
            assert passed, (
                f"Visual regression on {page_id} ({viewport_name}): "
                f"{diff_pct:.2f}% pixels differ (max 0.5%)"
            )
```

## Files to Create (same as v4)

| File | Purpose |
|------|---------|
| `tests/e2e/screenshot_compare.py` | Pillow-only pixel comparison (unchanged from v3) |
| `tests/e2e/screenshots/.gitkeep` | Baseline directory marker |
| `tests/provider_visual/__init__.py` | Package marker |
| `tests/provider_visual/conftest.py` | Mock server + `vr_base_url` fixture |
| `tests/provider_visual/test_screenshots.py` | 10 parametrized tests |
| `.github/workflows/visual-regression.yml` | Phase A: `workflow_dispatch`-only, always generates |

No existing files modified.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
