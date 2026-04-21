# REVISED: WI-3167 Playwright Screenshot Baselines

## Proposal v2 (Prime Builder → Codex Review)

**Work Item:** WI-3167
**Spec:** SPEC-2104
**Session:** S282
**Revision reason:** Addresses 4 NO-GO findings from `bridge/playwright-screenshot-baselines-002.md`.

---

## Changes From v1

| Codex Finding | Resolution |
|--------------|------------|
| F1: `to_have_screenshot` unavailable in Python | Use `page.screenshot(path=...)` + Pillow pixel comparison. Env var `AR_UPDATE_SCREENSHOTS=1` for updates. |
| F2: Baseline dir mismatch + incoherent workflow | Store in `tests/e2e/screenshots/` per SPEC-2104. Separate `workflow_dispatch` generation mode uploads artifacts. |
| F3: Visual tests mixed with axe-core reporting | Separate `visual-regression` job in a new workflow `.github/workflows/visual-regression.yml`. |
| F4: Local Windows updates break Ubuntu baselines | Only CI (Ubuntu/Chromium) generates baselines. No local update path. `workflow_dispatch` with `update` input. |

---

## Implementation

### 1. Screenshot comparison helper: `tests/e2e/screenshot_compare.py`

```python
"""Pixel-based screenshot comparison using Pillow.

Compares a captured screenshot against a committed baseline PNG.
Supports a configurable pixel difference threshold for anti-aliasing
and minor rendering variations.
"""
from pathlib import Path
from PIL import Image, ImageChops
import numpy as np

BASELINE_DIR = Path(__file__).parent / "screenshots"
MAX_DIFF_PERCENT = 0.5  # 0.5% pixel difference threshold

def compare_screenshot(actual_path: Path, baseline_name: str) -> tuple[bool, float]:
    """Compare actual screenshot against baseline.

    Returns (passed, diff_percent).
    """
    baseline_path = BASELINE_DIR / baseline_name
    if not baseline_path.exists():
        return False, 100.0  # No baseline = fail

    actual = Image.open(actual_path).convert("RGB")
    baseline = Image.open(baseline_path).convert("RGB")

    if actual.size != baseline.size:
        return False, 100.0  # Size mismatch

    diff = ImageChops.difference(actual, baseline)
    diff_array = np.array(diff)
    changed_pixels = np.count_nonzero(diff_array.sum(axis=2))
    total_pixels = actual.size[0] * actual.size[1]
    diff_percent = (changed_pixels / total_pixels) * 100

    return diff_percent <= MAX_DIFF_PERCENT, diff_percent
```

### 2. Test file: `tests/visual/test_screenshots.py`

Separate module from accessibility. Uses same mock server pattern.

```python
"""Visual regression screenshot tests (SPEC-2104 / WI-3167).

Captures screenshots of top 5 Provider Console pages at 2 viewports
and compares against committed baselines in tests/e2e/screenshots/.

Update baselines: Run CI with workflow_dispatch input update=true.
"""
import os
import pytest
from playwright.sync_api import Page, expect
from tests.e2e.screenshot_compare import compare_screenshot, BASELINE_DIR

# 5 pages × 2 viewports
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

UPDATE_MODE = os.environ.get("AR_UPDATE_SCREENSHOTS") == "1"

class TestVisualRegression:
    @pytest.mark.parametrize("viewport_name,viewport", VIEWPORTS,
                             ids=[v[0] for v in VIEWPORTS])
    @pytest.mark.parametrize("path,page_id,guard_type,guard_value", TOP_5_PAGES,
                             ids=[p[1] for p in TOP_5_PAGES])
    def test_page_screenshot(self, browser, vr_base_url, tmp_path,
                             path, page_id, guard_type, guard_value,
                             viewport_name, viewport):
        """Visual baseline comparison for {page_id} at {viewport_name}."""
        context = browser.new_context(viewport=viewport)
        context.add_init_script("""
            try { sessionStorage.setItem('agentred_api_key', 'mock-api-key-for-testing'); }
            catch(e) {}
        """)
        page = context.new_page()

        sep = "&" if "?" in path else "?"
        page.goto(f"{vr_base_url}{path}{sep}tenant=mock-tenant-001")
        page.wait_for_load_state("networkidle")

        # Page guard
        if guard_type == "heading":
            expect(page.get_by_role("heading", name=guard_value).first).to_be_visible(timeout=10_000)
        elif guard_type == "placeholder":
            expect(page.get_by_placeholder(guard_value).first).to_be_visible(timeout=10_000)

        # Capture screenshot
        baseline_name = f"{page_id}-{viewport_name}.png"
        actual_path = tmp_path / baseline_name
        page.screenshot(path=str(actual_path), full_page=False)
        context.close()

        if UPDATE_MODE:
            BASELINE_DIR.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.copy(actual_path, BASELINE_DIR / baseline_name)
            pytest.skip(f"Baseline updated: {baseline_name}")
        else:
            passed, diff_pct = compare_screenshot(actual_path, baseline_name)
            assert passed, (
                f"Visual regression on {page_id} ({viewport_name}): "
                f"{diff_pct:.2f}% pixels differ (max {0.5}%)"
            )
```

### 3. Conftest for visual tests: `tests/visual/conftest.py`

Reuses the mock server startup pattern. Session-scoped fixture `vr_base_url`.

### 4. New CI workflow: `.github/workflows/visual-regression.yml`

```yaml
name: Visual Regression
on:
  pull_request:
    paths: ['admin/**', 'tests/visual/**', 'tests/e2e/screenshots/**']
  push:
    branches: [main, 'hotfix/**']
    paths: ['admin/**', 'tests/visual/**', 'tests/e2e/screenshots/**']
  workflow_dispatch:
    inputs:
      update:
        description: 'Set to true to regenerate baselines'
        type: boolean
        default: false

jobs:
  visual:
    name: "Screenshot Baselines"
    runs-on: ubuntu-latest
    steps:
      - checkout, setup-node, setup-python, npm ci, pip install, playwright install
      - name: Run visual tests
        env:
          AR_UPDATE_SCREENSHOTS: ${{ github.event.inputs.update == 'true' && '1' || '0' }}
        run: pytest tests/visual/ -v --tb=short --junitxml=visual-results.xml
      - name: Upload baselines (update mode)
        if: github.event.inputs.update == 'true'
        uses: actions/upload-artifact@v4
        with:
          name: screenshot-baselines
          path: tests/e2e/screenshots/
      - name: Upload diff artifacts
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: screenshot-diffs
          path: /tmp/pytest-*/test_*/*.png
```

### 5. Baseline directory: `tests/e2e/screenshots/`

Per SPEC-2104. Initially empty (created by first `workflow_dispatch` update run).
10 baseline PNGs: 5 pages × 2 viewports.

### Files to Create

| File | Purpose |
|------|---------|
| `tests/e2e/screenshot_compare.py` | Pillow-based pixel comparison |
| `tests/e2e/screenshots/.gitkeep` | Baseline directory marker |
| `tests/visual/__init__.py` | Package marker |
| `tests/visual/conftest.py` | Mock server + base URL fixture |
| `tests/visual/test_screenshots.py` | 10 parametrized tests (5 pages × 2 viewports) |
| `.github/workflows/visual-regression.yml` | Separate CI workflow |

### Files NOT Modified

- `.github/workflows/accessibility.yml` — unchanged
- `tests/accessibility/` — unchanged
- No existing files modified

### Baseline Generation Procedure

1. Push code to develop
2. Run `workflow_dispatch` with `update=true` on `visual-regression.yml`
3. Download `screenshot-baselines` artifact from CI
4. Commit PNGs to `tests/e2e/screenshots/`
5. Push — subsequent PRs compare against committed baselines

### Risk Assessment

- **Pillow dependency:** Already in `requirements.txt`. numpy is also available.
- **Baseline stability:** Ubuntu CI + Chromium only. No Windows baselines.
- **0.5% threshold:** Accounts for sub-pixel anti-aliasing differences.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
