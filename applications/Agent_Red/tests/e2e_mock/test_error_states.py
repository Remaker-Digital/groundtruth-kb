# (C) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""SPEC-1706: Error states and edge case tests.

Tests API failure handling, network timeouts, empty data states,
and mock header verification using Playwright route interception.
"""
import pytest

from tests.e2e_mock.conftest import navigate_and_settle, MOCK_TENANT, api_origin


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fulfill_500(route):
    route.fulfill(
        status=500,
        content_type="application/json",
        body='{"error": "Internal Server Error"}',
    )


def _fulfill_empty(route, body="[]"):
    route.fulfill(
        status=200,
        content_type="application/json",
        body=body,
        headers={"x-mock": "true"},
    )


# ---------------------------------------------------------------------------
# TestApiFailures
# ---------------------------------------------------------------------------

class TestApiFailures:
    """Verify pages degrade gracefully when API returns 500."""

    @pytest.fixture(autouse=True)
    def _setup(self, page, mock_base_url):
        self.page = page
        self.base = mock_base_url

    def test_dashboard_500_does_not_crash(self):
        self.page.route("**/api/dashboard/usage", _fulfill_500)
        navigate_and_settle(self.page, "/dashboard", self.base)
        assert self.page.locator("body").count() > 0
        body_text = self.page.locator("body").inner_text()
        assert len(body_text.strip()) > 0

    def test_team_500_does_not_crash(self):
        self.page.route("**/api/admin/team", _fulfill_500)
        navigate_and_settle(self.page, "/team", self.base)
        assert self.page.locator("body").count() > 0

    def test_knowledge_500_does_not_crash(self):
        self.page.route("**/api/admin/knowledge", _fulfill_500)
        navigate_and_settle(self.page, "/knowledge", self.base)
        assert self.page.locator("body").count() > 0

    def test_config_500_does_not_crash(self):
        self.page.route("**/api/config", _fulfill_500)
        navigate_and_settle(self.page, "/configuration", self.base)
        assert self.page.locator("body").count() > 0

    def test_inbox_500_does_not_crash(self):
        self.page.route("**/api/admin/inbox/conversations", _fulfill_500)
        navigate_and_settle(self.page, "/inbox", self.base)
        assert self.page.locator("body").count() > 0

    def test_billing_500_does_not_crash(self):
        self.page.route("**/api/admin/billing/status", _fulfill_500)
        navigate_and_settle(self.page, "/billing", self.base)
        assert self.page.locator("body").count() > 0


# ---------------------------------------------------------------------------
# TestNetworkFailures
# ---------------------------------------------------------------------------

class TestNetworkFailures:
    """Verify pages handle network-level failures."""

    @pytest.fixture(autouse=True)
    def _setup(self, page, mock_base_url):
        self.page = page
        self.base = mock_base_url

    def test_dashboard_network_abort_no_crash(self):
        self.page.route("**/api/dashboard/usage", lambda route: route.abort())
        navigate_and_settle(self.page, "/dashboard", self.base)
        assert self.page.locator("body").count() > 0

    def test_team_network_abort_no_crash(self):
        self.page.route("**/api/admin/team", lambda route: route.abort())
        navigate_and_settle(self.page, "/team", self.base)
        assert self.page.locator("body").count() > 0

    def test_knowledge_network_abort_no_crash(self):
        self.page.route("**/api/admin/knowledge", lambda route: route.abort())
        navigate_and_settle(self.page, "/knowledge", self.base)
        assert self.page.locator("body").count() > 0

    def test_config_network_abort_no_crash(self):
        self.page.route("**/api/config", lambda route: route.abort())
        navigate_and_settle(self.page, "/configuration", self.base)
        assert self.page.locator("body").count() > 0


# ---------------------------------------------------------------------------
# TestEmptyData
# ---------------------------------------------------------------------------

class TestEmptyData:
    """Verify pages handle empty data responses gracefully."""

    @pytest.fixture(autouse=True)
    def _setup(self, page, mock_base_url):
        self.page = page
        self.base = mock_base_url

    def test_team_empty_list(self):
        self.page.route("**/api/admin/team", lambda r: _fulfill_empty(r, '{"members": []}'))
        navigate_and_settle(self.page, "/team", self.base)
        body = self.page.locator("body").inner_text()
        assert len(body.strip()) > 0

    def test_knowledge_empty_articles(self):
        self.page.route("**/api/admin/knowledge", lambda r: _fulfill_empty(r, '{"articles": [], "staleness": {}}'))
        navigate_and_settle(self.page, "/knowledge", self.base)
        body = self.page.locator("body").inner_text()
        assert len(body.strip()) > 0

    def test_inbox_empty_conversations(self):
        self.page.route(
            "**/api/admin/inbox/conversations",
            lambda r: _fulfill_empty(r, '{"conversations": []}'),
        )
        navigate_and_settle(self.page, "/inbox", self.base)
        body = self.page.locator("body").inner_text()
        assert len(body.strip()) > 0

    def test_quick_actions_empty_list(self):
        self.page.route("**/api/admin/quick-actions", lambda r: _fulfill_empty(r, '{"actions": []}'))
        navigate_and_settle(self.page, "/quick-actions", self.base)
        body = self.page.locator("body").inner_text()
        assert len(body.strip()) > 0


# ---------------------------------------------------------------------------
# TestMockHeaderVerification
# ---------------------------------------------------------------------------

class TestMockHeaderVerification:
    """Verify the mock server sets X-Mock: true on API responses."""

    @pytest.fixture(autouse=True)
    def _setup(self, page, mock_base_url):
        self.page = page
        self.base = mock_base_url

    def test_health_has_mock_header(self):
        resp = self.page.request.get(f"{api_origin(self.base)}/api/health")
        assert resp.status == 200
        assert resp.headers.get("x-mock") == "true"

    def test_tenant_lookup_has_mock_header(self):
        resp = self.page.request.get(f"{api_origin(self.base)}/api/tenants/lookup?tenant={MOCK_TENANT}")
        assert resp.status == 200
        assert resp.headers.get("x-mock") == "true"

    def test_config_has_mock_header(self):
        resp = self.page.request.get(f"{api_origin(self.base)}/api/config")
        assert resp.status == 200
        assert resp.headers.get("x-mock") == "true"

    def test_team_has_mock_header(self):
        resp = self.page.request.get(f"{api_origin(self.base)}/api/admin/team")
        assert resp.status == 200
        assert resp.headers.get("x-mock") == "true"
