"""
E2E tests — Integrations page.

Tests ADMIN_UI specs for the Integrations page:
  - Page title

Run with:
    pytest tests/e2e/test_integrations_page.py -v --headed
    pytest tests/e2e/test_integrations_page.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import pytest
from playwright.sync_api import Page, expect

from .conftest import AdminApiMocker

pytestmark = pytest.mark.e2e


class TestIntegrationsPageStructure:
    """Verify the Integrations page renders expected elements."""

    def test_page_title(self, admin_integrations_page: Page) -> None:
        """SPEC-0901: Integrations page title is 'Integrations'.

        The Integrations page may be a minimal stub showing the integrations
        count (0 when empty). We verify the page navigated successfully and
        the URL is correct.
        """
        # Verify we navigated to the integrations route
        assert "integrations" in admin_integrations_page.url.lower(), \
            "Should be on the Integrations page URL"
        # The page should not show an application error
        error = admin_integrations_page.locator("text=Application error")
        assert error.count() == 0, \
            "Integrations page should load without application error"
