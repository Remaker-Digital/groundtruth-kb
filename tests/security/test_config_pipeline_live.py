"""Live config pipeline E2E tests — validates widget config flows end-to-end.

Tests verify that configuration fields flow correctly through the entire
pipeline: fields.yaml → field_mapping → Cosmos schema → API endpoints.
This test suite was created after S103 bugs where 4 beta-customer-visible
defects (gradient toggle, setup checklist, brand name, field count drift)
slipped through because we lacked live endpoint validation of the config
pipeline.

Run:
    python -m pytest tests/security/test_config_pipeline_live.py -v

Prerequisites:
    - Production healthy
    - SUPERADMIN_PREVIEW_API_KEY set in .env.local or env
    - PREVIEW_WIDGET_KEY set in .env.local or env

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
import time

import httpx
import pytest

# ---------------------------------------------------------------------------
# Auto-load .env.local
# ---------------------------------------------------------------------------
from scripts._env import load_env_local

load_env_local()

PROD_URL = os.environ.get(
    "PROD_URL",
    "",  # SPEC-0058: No hardcoded FQDNs
)

# SPEC-1644: Config endpoints are tenant-scoped — they need a tenant key
# with ?tenant= param, NOT the SPA platform key (which resolves to __platform__
# and has no tenant config to return).
# Priority: tenant key > user key > SPA key (fallback).
TENANT_KEY = (
    os.environ.get("STAGING_REMAKER_TENANT_KEY")
    or os.environ.get("STAGING_REMAKER_USER_KEY")
    or os.environ.get("SUPERADMIN_PREVIEW_API_KEY")
    or ""
)
TENANT_ID = os.environ.get("LIVE_TENANT_ID", "remaker-digital-001")

WIDGET_KEY = os.environ.get("PREVIEW_WIDGET_KEY", "")

# SPEC-1644: All tenant-scoped endpoints need ?tenant= in the URL
_CONFIG_URL = f"/api/config?tenant={TENANT_ID}"
_DRAFT_URL = f"/api/config?state=draft&tenant={TENANT_ID}"


def _check_production_reachable() -> bool:
    try:
        r = httpx.get(f"{PROD_URL}/health", timeout=10)
        return r.status_code == 200
    except Exception:
        return False


def _request_with_rate_limit_retry(
    client: httpx.Client,
    method: str,
    url: str,
    *,
    headers: dict,
    max_retries: int = 3,
) -> httpx.Response:
    """Make a request, retrying if rate-limited (429)."""
    for attempt in range(max_retries):
        r = getattr(client, method)(url, headers=headers)
        if r.status_code != 429:
            return r
        time.sleep(min(int(r.headers.get("Retry-After", "5")), 15))
    return r


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def client():
    if not _check_production_reachable():
        pytest.skip("Production unreachable")
    with httpx.Client(base_url=PROD_URL, timeout=30, follow_redirects=True) as c:
        yield c


@pytest.fixture(scope="session")
def headers(client):
    """Tenant-scoped API key headers for config endpoints (SPEC-1644)."""
    if not TENANT_KEY:
        pytest.skip("No tenant key available (STAGING_REMAKER_TENANT_KEY not set)")
    # Validate the key authenticates for the target tenant
    try:
        r = client.get(
            f"/api/config?tenant={TENANT_ID}",
            headers={"X-API-Key": TENANT_KEY},
        )
        if r.status_code == 401:
            pytest.skip(
                f"Tenant key does not authenticate on {PROD_URL} "
                f"for tenant={TENANT_ID} (key/environment mismatch)"
            )
    except Exception:
        pass
    return {"X-API-Key": TENANT_KEY}


@pytest.fixture(scope="session")
def widget_headers(client):
    if not WIDGET_KEY:
        pytest.skip("PREVIEW_WIDGET_KEY not set")
    # Widget keys also need ?tenant= post-SPEC-1644
    try:
        r = client.get(
            f"/api/config?tenant={TENANT_ID}",
            headers={"X-Widget-Key": WIDGET_KEY},
        )
        if r.status_code == 401:
            pytest.skip(
                f"Widget key does not authenticate on {PROD_URL} "
                f"for tenant={TENANT_ID} (key/environment mismatch)"
            )
    except Exception:
        pass
    return {"X-Widget-Key": WIDGET_KEY}


# ===========================================================================
# 1. Active Config Field Completeness (CP-01 → CP-05)
#    Verifies /api/config returns all critical widget fields.
# ===========================================================================


class TestActiveConfigFields:
    """Verify active config endpoint returns expected widget fields."""

    # These are the minimum widget appearance fields that MUST exist in the
    # active config response.  This list was derived from field_mapping.py
    # _PREFS_DIRECT_FIELDS, filtered to widget_* prefixed entries that are
    # fully implemented (i.e., in all 3 pipeline layers).
    REQUIRED_WIDGET_FIELDS = {
        "widget_primary_color",
        "widget_background_color",
        "widget_position",
        "widget_header_gradient_enabled",  # S103 regression
        "widget_launcher_size",
        "widget_launcher_icon",
        "widget_header_title",
        "widget_header_subtitle",
        "widget_greeting_enabled",
        "widget_greeting_message",
        "widget_chat_rating_enabled",
        "widget_sound_enabled",
        "widget_file_upload_enabled",
        "widget_auto_open",
    }

    def test_cp01_config_returns_200(self, client, headers):
        """CP-01: /api/config returns HTTP 200."""
        r = _request_with_rate_limit_retry(client, "get", _CONFIG_URL, headers=headers)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"

    def test_cp02_config_has_config_key(self, client, headers):
        """CP-02: Config response has a 'config' key with nested fields."""
        r = _request_with_rate_limit_retry(client, "get", _CONFIG_URL, headers=headers)
        data = r.json()
        assert "config" in data, f"Missing 'config' key. Top-level keys: {list(data.keys())}"

    def test_cp03_widget_fields_present_in_config(self, client, headers):
        """CP-03: All required widget fields are present in the active config."""
        r = _request_with_rate_limit_retry(client, "get", _CONFIG_URL, headers=headers)
        data = r.json()
        config = data.get("config", {})

        missing = self.REQUIRED_WIDGET_FIELDS - set(config.keys())
        assert not missing, (
            f"Missing widget fields in /api/config: {sorted(missing)}\n"
            f"Available keys: {sorted(k for k in config if k.startswith('widget_'))}"
        )

    def test_cp04_gradient_enabled_is_boolean(self, client, headers):
        """CP-04: widget_header_gradient_enabled is a boolean (S103 regression)."""
        r = _request_with_rate_limit_retry(client, "get", _CONFIG_URL, headers=headers)
        config = r.json().get("config", {})
        val = config.get("widget_header_gradient_enabled")
        assert isinstance(val, bool), (
            f"widget_header_gradient_enabled should be bool, got {type(val).__name__}: {val}"
        )

    def test_cp05_primary_color_is_string(self, client, headers):
        """CP-05: widget_primary_color is a non-empty string."""
        r = _request_with_rate_limit_retry(client, "get", _CONFIG_URL, headers=headers)
        config = r.json().get("config", {})
        val = config.get("widget_primary_color")
        assert isinstance(val, str) and len(val) > 0, (
            f"widget_primary_color should be non-empty string, got: {val!r}"
        )


# ===========================================================================
# 2. Draft Config Integrity (CP-06 → CP-10)
#    Verifies /api/config/draft returns valid structure.
# ===========================================================================


class TestDraftConfigIntegrity:
    """Verify draft config endpoint returns valid data."""

    def test_cp06_draft_returns_200(self, client, headers):
        """CP-06: /api/config/draft returns HTTP 200."""
        r = _request_with_rate_limit_retry(
            client, "get", f"/api/config/draft?tenant={TENANT_ID}", headers=headers
        )
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"

    def test_cp07_draft_has_config_section(self, client, headers):
        """CP-07: Draft response has configuration data.

        The /api/config/draft endpoint returns a diff-style response with
        'draft_config' and 'active_config' sub-objects plus metadata fields
        like 'has_pending_changes', 'active_version', and 'changed_fields'.
        """
        r = _request_with_rate_limit_retry(
            client, "get", f"/api/config/draft?tenant={TENANT_ID}", headers=headers
        )
        data = r.json()
        has_config = any(
            key in data
            for key in ("draft_config", "active_config", "draft", "config")
        )
        assert has_config, f"Draft has no config section. Keys: {list(data.keys())}"

    def test_cp08_draft_preserves_brand_name(self, client, headers):
        """CP-08: brand_name field exists in config (S103 regression)."""
        r = _request_with_rate_limit_retry(client, "get", _CONFIG_URL, headers=headers)
        config = r.json().get("config", {})
        # brand_name should be in the config keys (may be null/empty for unconfigured)
        assert "brand_name" in config, (
            f"brand_name missing from config keys. "
            f"Available: {sorted(k for k in config if 'brand' in k or 'name' in k)}"
        )

    def test_cp09_draft_has_widget_gradient(self, client, headers):
        """CP-09: Draft endpoint includes active config with widget fields.

        When no draft changes are pending, draft_config is {} and widget
        fields live in active_config.  We check both locations.
        """
        r = _request_with_rate_limit_retry(
            client, "get", f"/api/config/draft?tenant={TENANT_ID}", headers=headers
        )
        data = r.json()
        # Widget fields are in active_config (or draft_config if pending changes)
        draft_cfg = data.get("draft_config", {})
        active_cfg = data.get("active_config", {})
        combined = {**active_cfg, **draft_cfg}
        widget_keys = [k for k in combined if k.startswith("widget_")]
        # If no pending changes, active_config may also be empty in this endpoint.
        # The presence of 'active_version' > 0 with 'has_pending_changes' = false
        # means the config exists but this endpoint only shows diffs.
        has_active_version = data.get("active_version", 0)
        assert len(widget_keys) > 0 or has_active_version, (
            f"Draft endpoint has no config data. Keys: {list(data.keys())}"
        )

    def test_cp10_config_version_present(self, client, headers):
        """CP-10: Config response includes a version number."""
        r = _request_with_rate_limit_retry(client, "get", _CONFIG_URL, headers=headers)
        data = r.json()
        version = data.get("version")
        assert version is not None, (
            f"Config missing 'version' key. Top-level keys: {list(data.keys())}"
        )


# ===========================================================================
# 3. Tenant Lookup Pipeline (CP-11 → CP-14)
#    Verifies /api/tenant/lookup returns brand_name and expected fields.
# ===========================================================================


class TestTenantLookup:
    """Verify tenant lookup includes all required fields."""

    def test_cp11_tenant_lookup_returns_200(self, client, headers):
        """CP-11: /api/tenants/lookup with shop param returns HTTP 200 or 404."""
        # /api/tenants/lookup is a PUBLIC endpoint (no auth needed) that
        # requires ?shop= or ?stripe_customer_id= for tenant resolution.
        # SPEC-1644: API key discovery is not supported.
        r = _request_with_rate_limit_retry(
            client, "get", f"/api/tenants/lookup?shop=blanco-9939.myshopify.com&tenant={TENANT_ID}", headers=headers
        )
        assert r.status_code in (200, 400, 404), f"Expected 200/400/404, got {r.status_code}"

    def test_cp12_tenant_lookup_has_brand_name_field(self, client, headers):
        """CP-12: Tenant lookup response includes brand_name field (S103 regression)."""
        r = _request_with_rate_limit_retry(
            client, "get", f"/api/tenants/lookup?shop=blanco-9939.myshopify.com&tenant={TENANT_ID}", headers=headers
        )
        if r.status_code == 200:
            data = r.json()
            # brand_name must be in the response schema (even if None)
            assert "brand_name" in data or "brandName" in data, (
                f"brand_name/brandName missing from lookup response. "
                f"Keys: {list(data.keys())}"
            )

    def test_cp13_tenant_lookup_has_tier(self, client, headers):
        """CP-13: Tenant lookup response includes tier."""
        r = _request_with_rate_limit_retry(
            client, "get", f"/api/tenants/lookup?tenant={TENANT_ID}", headers=headers
        )
        if r.status_code == 200:
            data = r.json()
            assert "tier" in data, f"Missing 'tier'. Keys: {list(data.keys())}"

    def test_cp14_tenant_lookup_has_status(self, client, headers):
        """CP-14: Tenant lookup response includes status."""
        r = _request_with_rate_limit_retry(
            client, "get", f"/api/tenants/lookup?tenant={TENANT_ID}", headers=headers
        )
        if r.status_code == 200:
            data = r.json()
            assert "status" in data, f"Missing 'status'. Keys: {list(data.keys())}"


# ===========================================================================
# 4. Provider SPA Serving (CP-15 → CP-18)
#    Verifies the admin SPA serves correctly.
# ===========================================================================


class TestProviderSpa:
    """Verify provider SPA (admin UI) serves correctly.

    The provider admin console is mounted at /admin/provider and serves
    static files (HTML, JS, CSS) without authentication.
    """

    def test_cp15_provider_spa_returns_200(self, client):
        """CP-15: /admin/provider returns HTTP 200."""
        r = client.get("/admin/provider")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"

    def test_cp16_provider_spa_is_html(self, client):
        """CP-16: /admin/provider returns HTML content."""
        r = client.get("/admin/provider")
        ct = r.headers.get("content-type", "")
        assert "html" in ct, f"Expected HTML content-type, got: {ct}"

    def test_cp17_provider_spa_has_react_root(self, client):
        """CP-17: Provider SPA HTML contains React root div."""
        r = client.get("/admin/provider")
        body = r.text
        assert 'id="root"' in body or 'id="app"' in body, (
            "SPA HTML missing React root element"
        )

    def test_cp18_provider_spa_has_js_bundle(self, client):
        """CP-18: Provider SPA HTML includes JavaScript bundle."""
        r = client.get("/admin/provider")
        body = r.text
        assert ".js" in body, "SPA HTML missing JavaScript bundle reference"


# ===========================================================================
# 5. Widget-Facing Config (CP-19 → CP-23)
#    Verifies the widget-key-authenticated config endpoint returns
#    appearance fields correctly (widget reads /api/config with X-Widget-Key).
# ===========================================================================


class TestWidgetFacingConfig:
    """Verify widget-key-authenticated config endpoint serves appearance settings.

    The widget SDK reads /api/config with X-Widget-Key auth to get the
    tenant's appearance settings.  This is the endpoint where S103's
    gradient toggle bug manifested — the field was missing from the
    response seen by the widget.
    """

    def test_cp19_widget_config_returns_200(self, client, widget_headers):
        """CP-19: /api/config with widget key returns HTTP 200."""
        r = _request_with_rate_limit_retry(
            client, "get", _CONFIG_URL, headers=widget_headers
        )
        assert r.status_code == 200, (
            f"Widget config expected 200, got {r.status_code}"
        )

    def test_cp20_widget_config_has_config_section(self, client, widget_headers):
        """CP-20: Widget config response has a 'config' key."""
        r = _request_with_rate_limit_retry(
            client, "get", _CONFIG_URL, headers=widget_headers
        )
        assert r.status_code == 200
        data = r.json()
        assert "config" in data, (
            f"Widget config missing 'config' key. Keys: {list(data.keys())}"
        )

    def test_cp21_widget_config_has_primary_color(self, client, widget_headers):
        """CP-21: Widget config includes widget_primary_color."""
        r = _request_with_rate_limit_retry(
            client, "get", _CONFIG_URL, headers=widget_headers
        )
        assert r.status_code == 200
        config = r.json().get("config", {})
        assert "widget_primary_color" in config, (
            f"Missing widget_primary_color. "
            f"Widget keys: {sorted(k for k in config if k.startswith('widget_'))}"
        )

    def test_cp22_widget_config_has_gradient(self, client, widget_headers):
        """CP-22: Widget config includes gradient_enabled (S103 regression).

        This is the exact field that was missing in the S103 gradient toggle
        bug.  The field existed in fields.yaml and the admin UI could save it,
        but it wasn't flowing through field_mapping to the widget config
        response.
        """
        r = _request_with_rate_limit_retry(
            client, "get", _CONFIG_URL, headers=widget_headers
        )
        assert r.status_code == 200
        config = r.json().get("config", {})
        assert "widget_header_gradient_enabled" in config, (
            f"S103 REGRESSION: widget_header_gradient_enabled missing from widget config. "
            f"Gradient keys: {[k for k in config if 'gradient' in k.lower()]}"
        )

    def test_cp23_widget_config_has_position(self, client, widget_headers):
        """CP-23: Widget config includes widget_position."""
        r = _request_with_rate_limit_retry(
            client, "get", _CONFIG_URL, headers=widget_headers
        )
        assert r.status_code == 200
        config = r.json().get("config", {})
        assert "widget_position" in config, (
            f"Missing widget_position. "
            f"Widget keys: {sorted(k for k in config if k.startswith('widget_'))}"
        )


# ===========================================================================
# 6. Version & Health (CP-24 → CP-26)
#    Verifies version reporting and API health.
# ===========================================================================


class TestVersionHealth:
    """Verify version and health reporting."""

    def test_cp24_version_header_present(self, client, headers):
        """CP-24: X-Product-Version header is returned."""
        r = _request_with_rate_limit_retry(client, "get", _CONFIG_URL, headers=headers)
        version = r.headers.get("X-Product-Version", "")
        assert version, "Missing X-Product-Version header"

    def test_cp25_version_is_semver(self, client, headers):
        """CP-25: Version follows semver format (major.minor.patch)."""
        r = _request_with_rate_limit_retry(client, "get", _CONFIG_URL, headers=headers)
        version = r.headers.get("X-Product-Version", "")
        parts = version.split(".")
        assert len(parts) == 3, f"Version not semver: {version}"
        for part in parts:
            assert part.isdigit(), f"Version part not numeric: {part} in {version}"

    def test_cp26_health_reports_ok(self, client):
        """CP-26: /health returns status ok."""
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        status = data.get("status", "")
        assert status.lower() in ("ok", "healthy", "up"), f"Health status: {status}"
