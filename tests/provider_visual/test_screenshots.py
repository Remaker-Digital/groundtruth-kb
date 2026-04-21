"""Visual regression screenshot tests for Provider Console (SPEC-2104 / WI-3167).

Captures screenshots of top 5 Provider Console pages at 2 viewports and
compares against committed baselines in tests/e2e/screenshots/.

Update baselines: Run CI workflow_dispatch (Phase A generates baselines).
Browser time is frozen to match mock fixture dates for deterministic rendering.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
import shutil

import pytest
from playwright.sync_api import expect

from tests.e2e.screenshot_compare import BASELINE_DIR, compare_screenshot

from .conftest import MOCK_API_KEY, navigate_vr

pytestmark = pytest.mark.visual

UPDATE_MODE = os.environ.get("AR_UPDATE_SCREENSHOTS") == "1"

# Frozen to match Dashboard fixture end date (dashboard.ts ref: 2026-03-10)
FROZEN_TIME = "2026-03-10T12:00:00Z"

# Top 5 Provider Console journeys (SPEC-2104 requirement 1)
TOP_5_PAGES = [
    ("/", "dashboard", "heading", "Dashboard"),
    ("/configuration", "configuration", "heading", "Agent configuration"),
    ("/inbox", "inbox", "placeholder", "Search conversations..."),
    ("/widget", "widget", "heading", "Widget configuration"),
    ("/team", "team", "heading", "Team members"),
]

# Desktop and tablet viewports (SPEC-2104 requirement 5)
VIEWPORTS = [
    ("desktop", {"width": 1280, "height": 800}),
    ("tablet", {"width": 768, "height": 1024}),
]


class TestVisualRegression:
    """Visual baseline comparison for top 5 Provider Console pages."""

    @pytest.mark.parametrize(
        "viewport_name,viewport",
        VIEWPORTS,
        ids=[v[0] for v in VIEWPORTS],
    )
    @pytest.mark.parametrize(
        "path,page_id,guard_type,guard_value",
        TOP_5_PAGES,
        ids=[p[1] for p in TOP_5_PAGES],
    )
    def test_page_screenshot(
        self,
        browser,
        vr_base_url,
        tmp_path,
        path,
        page_id,
        guard_type,
        guard_value,
        viewport_name,
        viewport,
    ):
        """Visual baseline for {page_id} at {viewport_name}."""
        context = browser.new_context(viewport=viewport)
        context.add_init_script(
            f"""
            try {{ sessionStorage.setItem('agentred_api_key', '{MOCK_API_KEY}'); }}
            catch(e) {{}}
        """
        )
        page = context.new_page()

        # Freeze browser Date to match fixture end date
        page.clock.set_fixed_time(FROZEN_TIME)

        navigate_vr(page, vr_base_url, path)

        # Page guard: verify intended page rendered
        if guard_type == "heading":
            expect(page.get_by_role("heading", name=guard_value).first).to_be_visible(timeout=10_000)
        elif guard_type == "placeholder":
            expect(page.get_by_placeholder(guard_value).first).to_be_visible(timeout=10_000)

        # Wait for Recharts animation to complete (1500ms default + buffer)
        page.wait_for_timeout(2500)

        # Capture screenshot
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
            assert passed, f"Visual regression on {page_id} ({viewport_name}): {diff_pct:.2f}% pixels differ (max 0.5%)"
