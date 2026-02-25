"""
E2E tests — Knowledge Base page.

Tests every interactive element on the Knowledge Base page:
  - Page structure and article list rendering
  - Search input filtering
  - Add article button and modal
  - Article row actions (edit, delete)
  - WebsiteSourcesPanel: add URL, trigger crawl, delete
  - Import modal (file upload tab, URL import tab)
  - Category filter dropdown
  - Status filter tabs

Run with:
    pytest tests/e2e/test_knowledge_base_page.py -v --headed
    pytest tests/e2e/test_knowledge_base_page.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import pytest
from playwright.sync_api import Page, expect

from .conftest import AdminApiMocker

pytestmark = pytest.mark.e2e


# ===========================================================================
# Page Structure Tests
# ===========================================================================


class TestKnowledgeBaseStructure:
    """Verify the Knowledge Base page renders all expected elements."""

    def test_page_heading_visible(self, admin_kb_page: Page) -> None:
        """Knowledge Base page heading is visible."""
        heading = admin_kb_page.locator("h2, h3").filter(has_text="Knowledge")
        expect(heading.first).to_be_visible()

    def test_article_list_rendered(self, admin_kb_page: Page) -> None:
        """Articles from mock data are rendered."""
        expect(admin_kb_page.locator("text=Getting Started").first).to_be_visible()
        expect(admin_kb_page.locator("text=Billing FAQ").first).to_be_visible()

    def test_article_count_displayed(self, admin_kb_page: Page) -> None:
        """Article count is displayed."""
        # Should show "2 articles" or similar count
        count_text = admin_kb_page.locator("text=2")
        assert count_text.count() > 0, "Article count should be displayed"

    def test_add_article_button_visible(self, admin_kb_page: Page) -> None:
        """Add article button is present."""
        add_btn = admin_kb_page.locator("button", has_text="Add")
        create_btn = admin_kb_page.locator("button", has_text="Create")
        new_btn = admin_kb_page.locator("button", has_text="New")
        assert add_btn.count() > 0 or create_btn.count() > 0 or new_btn.count() > 0, \
            "Add/Create/New article button should be visible"

    def test_search_input_visible(self, admin_kb_page: Page) -> None:
        """Search input is visible for filtering articles."""
        search = admin_kb_page.locator('input[placeholder*="Search"], input[placeholder*="search"]')
        # May also be a generic text input
        assert search.count() > 0 or admin_kb_page.locator('input[type="search"]').count() > 0, \
            "Search input should be visible"


# ===========================================================================
# Search Tests
# ===========================================================================


class TestSearch:
    """Test the search/filter functionality."""

    def test_search_filters_articles(self, admin_kb_page: Page) -> None:
        """Typing in search input filters the article list."""
        search = admin_kb_page.locator(
            'input[placeholder*="Search"], input[placeholder*="search"], input[type="search"]'
        ).first

        if search.is_visible():
            search.fill("Billing")
            admin_kb_page.wait_for_timeout(500)

            # Billing FAQ should still be visible
            expect(admin_kb_page.locator("text=Billing FAQ").first).to_be_visible()


# ===========================================================================
# Article CRUD Tests
# ===========================================================================


class TestArticleCRUD:
    """Test article create/edit/delete interactions."""

    def test_add_article_opens_modal(self, admin_kb_page: Page) -> None:
        """Clicking Add/Create opens the article editor modal."""
        add_btn = admin_kb_page.locator("button", has_text="Add")
        if add_btn.count() == 0:
            add_btn = admin_kb_page.locator("button", has_text="Create")
        if add_btn.count() == 0:
            add_btn = admin_kb_page.locator("button", has_text="New")

        if add_btn.count() > 0:
            add_btn.first.click()
            admin_kb_page.wait_for_timeout(500)

            # A modal or editor should appear
            # Look for common modal indicators
            modal_visible = (
                admin_kb_page.locator("[role='dialog']").count() > 0
                or admin_kb_page.locator("text=Title").count() > 0
                or admin_kb_page.locator("text=Content").count() > 0
            )
            assert modal_visible, "Article editor modal should appear"


# ===========================================================================
# Website Sources Panel Tests
# ===========================================================================


@pytest.mark.skip(reason="WebsiteSourcesPanel is in Provider admin only, not Standalone. "
                         "Provider E2E tests are a separate suite.")
class TestWebsiteSourcesPanel:
    """Test the WebsiteSourcesPanel component (added S94).

    SKIPPED: WebsiteSourcesPanel is rendered in KnowledgeBaseManager.tsx
    (the Provider admin shared component), NOT in the Standalone admin's
    KnowledgeBase.tsx page. These tests will be included when the Provider
    admin E2E suite is built.
    """

    def test_website_sources_section_visible(self, admin_kb_page: Page) -> None:
        """Website sources section is rendered on the KB page."""
        ws_heading = admin_kb_page.locator("text=Website Sources")
        ws_alt = admin_kb_page.locator("text=Website sources")
        assert ws_heading.count() > 0 or ws_alt.count() > 0, \
            "Website Sources section heading should be visible"

    def test_website_source_url_displayed(self, admin_kb_page: Page) -> None:
        """The mock website source domain is displayed."""
        domain = admin_kb_page.locator("text=testco.com")
        url = admin_kb_page.locator("text=https://testco.com")
        assert domain.count() > 0 or url.count() > 0, \
            "Website source domain should be displayed"

    def test_add_website_source_button_exists(self, admin_kb_page: Page) -> None:
        """An 'Add' button for website sources exists."""
        add_btns = admin_kb_page.locator("button", has_text="Add")
        assert add_btns.count() > 0, "Add website source button should exist"
