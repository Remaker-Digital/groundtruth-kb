"""Live external URL verification — SPEC-1649 / WI-1025.

Replaces Phase 15 (SOURCE_INSPECTION manual verification) with live HTTP
checks against external URLs that the platform depends on or publishes.

Verifies:
  1. Documentation site (agentredcx.com) is accessible
  2. Platform health endpoint returns expected structure
  3. Admin SPAs serve HTML
  4. Widget.js is accessible from the public internet
  5. OpenAPI spec is accessible

Run:
    python -m pytest tests/live_api/test_external_urls_live.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import httpx
import pytest


# ---------------------------------------------------------------------------
# External URL client (separate from platform client — different base URLs)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def external_client() -> httpx.Client:
    """Create a shared httpx client for external URL checks."""
    client = httpx.Client(
        timeout=15.0,
        follow_redirects=True,
    )
    yield client  # type: ignore[misc]
    client.close()


# ---------------------------------------------------------------------------
# Test: Documentation Site Accessibility
# ---------------------------------------------------------------------------
class TestDocumentationSite:
    """Verify the public documentation site is accessible."""

    def test_ev_live_01_docs_site_reachable(self, external_client: httpx.Client):
        """EV-LIVE-01: agentredcx.com returns HTTP 200."""
        resp = external_client.get("https://agentredcx.com/")
        assert resp.status_code == 200, (
            f"Docs site returned {resp.status_code}"
        )

    def test_ev_live_02_docs_site_has_content(self, external_client: httpx.Client):
        """EV-LIVE-02: Docs site contains expected HTML content."""
        resp = external_client.get("https://agentredcx.com/")
        assert resp.status_code == 200
        content_type = resp.headers.get("content-type", "")
        assert "text/html" in content_type, (
            f"Expected HTML, got content-type: {content_type}"
        )
        # Should contain meaningful content (not just a redirect/error page)
        assert len(resp.text) > 500, (
            f"Docs site content too small ({len(resp.text)} bytes)"
        )

    def test_ev_live_03_docs_site_contains_brand(self, external_client: httpx.Client):
        """EV-LIVE-03: Docs site references the Agent Red brand."""
        resp = external_client.get("https://agentredcx.com/")
        assert resp.status_code == 200
        text_lower = resp.text.lower()
        assert "agent red" in text_lower or "agentred" in text_lower, (
            "Docs site does not reference 'Agent Red' brand"
        )


# ---------------------------------------------------------------------------
# Test: Platform Public Endpoints
# ---------------------------------------------------------------------------
class TestPlatformPublicEndpoints:
    """Verify platform endpoints accessible without authentication."""

    def test_ev_live_04_health_structure(
        self, live_client: httpx.Client, platform_reachable: None
    ):
        """EV-LIVE-04: /health returns JSON with expected fields."""
        resp = live_client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        # Should have status and product_version
        assert "status" in data, f"Missing 'status' in health: {list(data.keys())}"
        assert "product_version" in data or "productVersion" in data, (
            f"Missing version in health: {list(data.keys())}"
        )

    def test_ev_live_05_ready_endpoint_structure(
        self, live_client: httpx.Client, platform_reachable: None
    ):
        """EV-LIVE-05: /ready returns JSON with status field.

        SPEC-1780: 503 is valid when NATS transport not active (fail-loud).
        """
        resp = live_client.get("/ready")
        assert resp.status_code in (200, 503), f"/ready returned {resp.status_code}"
        data = resp.json()
        assert "status" in data, f"Missing 'status' in ready: {list(data.keys())}"

    def test_ev_live_06_openapi_spec_accessible(
        self, live_client: httpx.Client, platform_reachable: None
    ):
        """EV-LIVE-06: /openapi.json returns valid JSON schema."""
        resp = live_client.get("/openapi.json")
        assert resp.status_code == 200
        data = resp.json()
        # Should contain OpenAPI spec fields
        assert "openapi" in data or "info" in data or "paths" in data, (
            f"Unexpected OpenAPI structure: {list(data.keys())[:10]}"
        )

    def test_ev_live_07_widget_js_public(
        self, live_client: httpx.Client, platform_reachable: None
    ):
        """EV-LIVE-07: /widget.js accessible without authentication."""
        resp = live_client.get("/widget.js")
        assert resp.status_code == 200
        # Should be JavaScript content
        ct = resp.headers.get("content-type", "")
        assert "javascript" in ct or "text/" in ct, (
            f"Expected JavaScript content-type, got: {ct}"
        )
        assert len(resp.text) > 1000, "Widget.js content too small"


# ---------------------------------------------------------------------------
# Test: Admin SPA Accessibility
# ---------------------------------------------------------------------------
class TestAdminSPAAccessibility:
    """Verify admin SPAs serve HTML content (no auth required for SPA shell)."""

    @pytest.mark.parametrize("path,name", [
        ("/admin/standalone/", "Standalone SPA"),
        ("/admin/shopify/", "Shopify SPA"),
        ("/admin/provider/", "Provider SPA"),
    ])
    def test_ev_live_08_admin_spa_serves_html(
        self, live_client: httpx.Client, platform_reachable: None,
        path: str, name: str,
    ):
        """EV-LIVE-08: Admin SPA returns HTML shell."""
        resp = live_client.get(path)
        assert resp.status_code == 200, (
            f"{name} at {path} returned {resp.status_code}"
        )
        ct = resp.headers.get("content-type", "")
        assert "text/html" in ct, (
            f"{name} content-type: {ct} (expected text/html)"
        )


# ---------------------------------------------------------------------------
# Test: Security Headers on Public Endpoints
# ---------------------------------------------------------------------------
class TestSecurityHeaders:
    """Verify security headers are present on public responses."""

    def test_ev_live_09_security_headers_present(
        self, live_client: httpx.Client, platform_reachable: None
    ):
        """EV-LIVE-09: Security headers (nosniff, X-Frame-Options) present."""
        resp = live_client.get("/health")
        headers_lower = {k.lower(): v for k, v in resp.headers.items()}
        assert "x-content-type-options" in headers_lower, (
            "Missing X-Content-Type-Options header"
        )
        assert "x-frame-options" in headers_lower, (
            "Missing X-Frame-Options header"
        )
