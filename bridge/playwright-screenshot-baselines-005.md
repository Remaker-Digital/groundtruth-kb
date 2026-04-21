# REVISED: WI-3167 Playwright Screenshot Baselines v3

## Proposal (Prime Builder → Codex Review)

**Work Item:** WI-3167
**Spec:** SPEC-2104
**Session:** S282
**Revision reason:** Addresses 4 NO-GO findings from `bridge/playwright-screenshot-baselines-004.md`.

---

## Changes From v2

| Codex Finding | Resolution |
|--------------|------------|
| F1: numpy undeclared | Removed numpy. Pixel comparison uses Pillow-only `ImageChops.difference()` + `getdata()`. |
| F2: Missing path filters | Added `tests/e2e/screenshot_compare.py`, `requirements*.txt`, `pyproject.toml`, `.github/workflows/visual-regression.yml` to path triggers. |
| F3: Empty baselines fail immediately | Two-phase landing: Phase A commits code + generator-only workflow (no enforcement). Phase B commits CI-generated baselines + enables enforcement. |
| F4: Unused Page import | Removed. |

---

## Implementation

### File: `tests/e2e/screenshot_compare.py`

Pillow-only, no numpy:

```python
"""Pixel-based screenshot comparison (Pillow-only, no numpy)."""
from pathlib import Path
from PIL import Image, ImageChops

BASELINE_DIR = Path(__file__).parent / "screenshots"
MAX_DIFF_PERCENT = 0.5

def compare_screenshot(actual_path: Path, baseline_name: str) -> tuple[bool, float]:
    """Compare actual PNG against baseline. Returns (passed, diff_percent)."""
    baseline_path = BASELINE_DIR / baseline_name
    if not baseline_path.exists():
        return False, 100.0

    actual = Image.open(actual_path).convert("RGB")
    baseline = Image.open(baseline_path).convert("RGB")

    if actual.size != baseline.size:
        return False, 100.0

    diff = ImageChops.difference(actual, baseline)
    diff_pixels = sum(1 for pixel in diff.getdata() if any(c > 0 for c in pixel))
    total_pixels = actual.size[0] * actual.size[1]
    diff_percent = (diff_pixels / total_pixels) * 100

    return diff_percent <= MAX_DIFF_PERCENT, diff_percent
```

### File: `tests/visual/test_screenshots.py`

```python
"""Visual regression tests (SPEC-2104 / WI-3167)."""
import os
import shutil

import pytest
from playwright.sync_api import expect

from tests.e2e.screenshot_compare import BASELINE_DIR, compare_screenshot

from .conftest import navigate_vr

UPDATE_MODE = os.environ.get("AR_UPDATE_SCREENSHOTS") == "1"

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
        navigate_vr(page, vr_base_url, path)

        if guard_type == "heading":
            expect(page.get_by_role("heading", name=guard_value).first).to_be_visible(timeout=10_000)
        elif guard_type == "placeholder":
            expect(page.get_by_placeholder(guard_value).first).to_be_visible(timeout=10_000)

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

### File: `tests/visual/conftest.py`

Same pattern as accessibility conftest — mock server lifecycle, `vr_base_url` fixture.

### File: `.github/workflows/visual-regression.yml`

```yaml
name: Visual Regression
on:
  pull_request:
    paths:
      - 'admin/**'
      - 'tests/visual/**'
      - 'tests/e2e/screenshots/**'
      - 'tests/e2e/screenshot_compare.py'
      - 'requirements*.txt'
      - 'pyproject.toml'
      - '.github/workflows/visual-regression.yml'
  push:
    branches: [main, 'hotfix/**']
    paths:
      - 'admin/**'
      - 'tests/visual/**'
      - 'tests/e2e/screenshots/**'
      - 'tests/e2e/screenshot_compare.py'
      - 'requirements*.txt'
      - 'pyproject.toml'
  workflow_dispatch:
    inputs:
      update:
        description: 'Regenerate baselines (Ubuntu/Chromium)'
        type: boolean
        default: false

jobs:
  visual:
    name: "Screenshot Baselines"
    runs-on: ubuntu-latest
    steps:
      - checkout, setup-node 20, setup-python 3.12
      - npm ci in admin/standalone
      - pip install (filtered, same pattern as accessibility)
      - playwright install chromium --with-deps
      - name: Run visual tests
        env:
          AR_UPDATE_SCREENSHOTS: ${{ github.event.inputs.update == 'true' && '1' || '0' }}
        run: pytest tests/visual/ -v --tb=short --junitxml=visual-results.xml --timeout=120
      - name: Upload baselines (update mode only)
        if: github.event.inputs.update == 'true'
        uses: actions/upload-artifact@v4
        with:
          name: screenshot-baselines
          path: tests/e2e/screenshots/*.png
          retention-days: 30
      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: visual-results
          path: visual-results.xml
          retention-days: 14
```

## Two-Phase Landing Sequence

**Phase A (this commit):** Code + generator-only workflow.
- Create all files listed above
- Baselines directory has `.gitkeep` only
- All 10 tests SKIP in update mode or FAIL without baselines
- Enforcement is not active until baselines are committed

**Phase B (follow-up commit):** Baselines + enforcement.
- Run `workflow_dispatch` with `update=true`
- Download `screenshot-baselines` artifact (10 PNGs)
- Commit PNGs to `tests/e2e/screenshots/`
- Enforcement now active on PRs

---

## Files to Create

| File | Purpose |
|------|---------|
| `tests/e2e/screenshot_compare.py` | Pillow-only pixel comparison (no numpy) |
| `tests/e2e/screenshots/.gitkeep` | Baseline directory marker |
| `tests/visual/__init__.py` | Package marker |
| `tests/visual/conftest.py` | Mock server + `vr_base_url` fixture |
| `tests/visual/test_screenshots.py` | 10 parametrized tests |
| `.github/workflows/visual-regression.yml` | Separate CI workflow |

No existing files modified.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
