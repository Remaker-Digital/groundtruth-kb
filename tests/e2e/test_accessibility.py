"""Accessibility test suite (SPEC-1846/WI-1505).

Tests WCAG 2.1 AA compliance for the Provider Console and widget chat panel.
Requires axe-playwright-python and a running Vite dev server.

Run with:
    pytest tests/e2e/test_accessibility.py --headed

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import pytest

# Skip entire module if axe-playwright-python is not installed
pytest.importorskip("axe_playwright_python", reason="axe-playwright-python required for a11y tests")

from tests.e2e.a11y_helpers import assert_no_critical_a11y_violations


# ---------------------------------------------------------------------------
# Provider Console a11y tests
# ---------------------------------------------------------------------------


@pytest.mark.e2e
class TestProviderConsoleAccessibility:
    """WCAG 2.1 AA compliance for Provider Console pages."""

    @pytest.mark.parametrize("path,page_name", [
        ("/provider/dashboard", "Dashboard"),
        ("/provider/configuration", "Configuration"),
        ("/provider/inbox", "Inbox"),
        ("/provider/analytics", "Analytics"),
        ("/provider/team", "Team"),
        ("/provider/knowledge-base", "Knowledge Base"),
        ("/provider/integrations", "Integrations"),
        ("/provider/billing", "Billing"),
        ("/provider/widget", "Widget"),
    ])
    def test_provider_page_a11y(self, page, base_url, path: str, page_name: str) -> None:
        """Provider Console {page_name} page must have no critical/serious a11y violations."""
        page.goto(f"{base_url}{path}")
        page.wait_for_load_state("networkidle")
        assert_no_critical_a11y_violations(page)

    @pytest.mark.parametrize("path,page_name", [
        ("/provider/control-plane/entitlements", "Entitlements"),
        ("/provider/control-plane/feature-flags", "Feature Flags"),
        ("/provider/control-plane/blocklists", "Blocklists"),
        ("/provider/control-plane/maintenance", "Maintenance"),
        ("/provider/control-plane/deployments", "Deployments"),
    ])
    def test_control_plane_page_a11y(self, page, base_url, path: str, page_name: str) -> None:
        """Control Plane {page_name} page must have no critical/serious a11y violations."""
        page.goto(f"{base_url}{path}")
        page.wait_for_load_state("networkidle")
        assert_no_critical_a11y_violations(page)


# ---------------------------------------------------------------------------
# Widget a11y tests
# ---------------------------------------------------------------------------


@pytest.mark.e2e
class TestWidgetAccessibility:
    """WCAG 2.1 AA compliance for the chat widget."""

    def test_widget_chat_panel_a11y(self, page, widget_url) -> None:
        """Widget chat panel must have no critical/serious a11y violations."""
        page.goto(widget_url)
        page.wait_for_load_state("networkidle")
        # The widget may be inside an iframe — check the main page first
        assert_no_critical_a11y_violations(page)

    def test_widget_launcher_button_a11y(self, page, widget_url) -> None:
        """Widget launcher button must have appropriate ARIA attributes."""
        page.goto(widget_url)
        page.wait_for_load_state("networkidle")
        # Check that launcher button has accessible name
        launcher = page.locator("[data-testid='widget-launcher'], .widget-launcher, button")
        if launcher.count() > 0:
            first = launcher.first
            # Should have accessible name (aria-label or visible text)
            name = first.get_attribute("aria-label") or first.inner_text()
            assert name and len(name.strip()) > 0, "Launcher button must have an accessible name"
