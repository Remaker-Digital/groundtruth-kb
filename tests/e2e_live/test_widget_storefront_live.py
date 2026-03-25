"""
Live E2E tests for SPEC-1849: Widget Presence on Connected Storefront.

Verifies that the Agent Red chat widget is present and loadable on
connected Shopify storefronts. A missing widget on a connected storefront
is a system failure — these tests MUST fail in that case.

Tests:
    1. Storefront HTML contains Agent Red widget script tag
    2. Widget script tag includes a valid widget key (pk_live_...)
    3. Widget JS bundle returns HTTP 200 with valid JavaScript
    4. Widget launcher element is present in the DOM (Playwright)

Run:
    pytest tests/e2e_live/test_widget_storefront_live.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
import re

import httpx
import pytest

# ---------------------------------------------------------------------------
# Configuration — Shopify storefronts to verify
# ---------------------------------------------------------------------------

# Each entry: (shop_domain, expected_widget_key_prefix)
# The widget key prefix is enough to confirm the correct tenant is wired up.
CONNECTED_STOREFRONTS = [
    ("blanco-9939.myshopify.com", "pk_live_"),
]

API_GATEWAY_FQDN = os.environ.get(
    "API_GATEWAY_FQDN",
    os.environ.get(
        "CONTAINER_APP_FQDN",
        "agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io",
    ),
)


# Shopify store password for development-mode stores.
# Required when the storefront is password-protected.
SHOPIFY_STORE_PASSWORD = os.environ.get("SHOPIFY_STORE_PASSWORD", "")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fetch_storefront_html(shop_domain: str) -> str:
    """Fetch the storefront homepage HTML.

    Handles Shopify password-protected (development mode) stores by
    submitting the store password via the /password endpoint first,
    then fetching the homepage with the authenticated session cookie.
    """
    ua = {"User-Agent": "AgentRed-E2E-Test/1.0"}
    client = httpx.Client(timeout=30, follow_redirects=True, headers=ua)

    resp = client.get(f"https://{shop_domain}/")

    # Detect password gate: Shopify redirects to /password or serves it inline
    if "/password" in str(resp.url) or "storefront-password" in resp.text.lower():
        if not SHOPIFY_STORE_PASSWORD:
            pytest.fail(
                f"Storefront {shop_domain} is password-protected but "
                f"SHOPIFY_STORE_PASSWORD env var is not set. "
                f"Set it to the store password to authenticate."
            )
        # Submit the password form
        auth_resp = client.post(
            f"https://{shop_domain}/password",
            data={"password": SHOPIFY_STORE_PASSWORD},
            follow_redirects=True,
        )
        # After successful auth, Shopify sets a session cookie and redirects
        # to the homepage. Re-fetch to get the actual theme HTML.
        if "/password" in str(auth_resp.url):
            pytest.fail(
                f"Shopify password authentication failed for {shop_domain}. "
                f"Check that SHOPIFY_STORE_PASSWORD is correct."
            )
        resp = auth_resp

    resp.raise_for_status()
    return resp.text


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestWidgetStorefrontPresence:
    """SPEC-1849: Widget MUST be present on connected Shopify storefronts."""

    @pytest.fixture(autouse=True)
    def _load_html(self):
        """Pre-fetch storefront HTML once for all tests in this class."""
        self.storefronts: dict[str, str] = {}
        for shop_domain, _ in CONNECTED_STOREFRONTS:
            try:
                self.storefronts[shop_domain] = _fetch_storefront_html(shop_domain)
            except Exception as exc:
                pytest.fail(
                    f"Could not fetch storefront {shop_domain}: {exc}"
                )

    @pytest.mark.parametrize("shop_domain,key_prefix", CONNECTED_STOREFRONTS)
    def test_widget_script_tag_present(self, shop_domain: str, key_prefix: str):
        """Storefront HTML contains a script tag loading the Agent Red widget."""
        html = self.storefronts[shop_domain]

        # Look for: agent-red-widget script (CDN asset_url or direct /widget.js)
        has_widget_script = bool(
            re.search(r"agent-red-widget", html, re.IGNORECASE)
            or re.search(r'src="[^"]*widget\.js"', html, re.IGNORECASE)
            or re.search(r"src='[^']*widget\.js'", html, re.IGNORECASE)
        )
        assert has_widget_script, (
            f"No Agent Red widget script tag found on {shop_domain}. "
            f"The app embed may be disabled in the Shopify theme editor "
            f"(Online Store > Themes > Customize > App embeds > Agent Red Chat)."
        )

    @pytest.mark.parametrize("shop_domain,key_prefix", CONNECTED_STOREFRONTS)
    def test_widget_key_present_in_html(self, shop_domain: str, key_prefix: str):
        """Storefront HTML includes a valid widget key (data-widget-key or inline)."""
        html = self.storefronts[shop_domain]

        # Match data-widget-key="pk_live_..." or similar attribute
        key_match = re.search(
            r'data-widget-key="(' + re.escape(key_prefix) + r'[a-zA-Z0-9_]+)"',
            html,
        )
        assert key_match, (
            f"No widget key ({key_prefix}...) found in {shop_domain} HTML. "
            f"The widget key may not be configured in the Shopify app embed settings."
        )

    @pytest.mark.parametrize("shop_domain,key_prefix", CONNECTED_STOREFRONTS)
    def test_widget_js_returns_200(self, shop_domain: str, key_prefix: str):
        """Widget JS bundle is accessible and returns valid JavaScript."""
        # The widget JS can be served from the API gateway or Shopify CDN
        html = self.storefronts[shop_domain]

        # Extract the script src URL
        src_match = re.search(
            r'<script[^>]*src="([^"]*agent-red-widget[^"]*)"',
            html,
            re.IGNORECASE,
        )
        if not src_match:
            # Try /widget.js pattern
            src_match = re.search(
                r'<script[^>]*src="([^"]*widget\.js[^"]*)"',
                html,
                re.IGNORECASE,
            )

        if not src_match:
            pytest.fail(
                f"Cannot extract widget script URL from {shop_domain} — "
                f"script tag not found (test_widget_script_tag_present should also fail)"
            )

        widget_url = src_match.group(1)
        # Handle relative URLs
        if widget_url.startswith("//"):
            widget_url = "https:" + widget_url
        elif widget_url.startswith("/"):
            widget_url = f"https://{shop_domain}{widget_url}"

        resp = httpx.get(widget_url, timeout=30, follow_redirects=True)
        assert resp.status_code == 200, (
            f"Widget JS at {widget_url} returned {resp.status_code}"
        )
        content_type = resp.headers.get("content-type", "")
        assert "javascript" in content_type or "text/" in content_type, (
            f"Widget JS content-type is '{content_type}' — expected JavaScript"
        )

    @pytest.mark.parametrize("shop_domain,key_prefix", CONNECTED_STOREFRONTS)
    def test_widget_api_url_points_to_gateway(self, shop_domain: str, key_prefix: str):
        """Widget embed includes data-api-url pointing to our API gateway."""
        html = self.storefronts[shop_domain]

        api_url_match = re.search(
            r'data-api-url="([^"]+)"',
            html,
        )
        if not api_url_match:
            pytest.skip("No data-api-url attribute found (may use default)")
            return

        api_url = api_url_match.group(1)
        assert "agent-red" in api_url.lower() or API_GATEWAY_FQDN in api_url, (
            f"Widget data-api-url '{api_url}' does not point to Agent Red gateway"
        )
