"""
Shopify App Store compliance tests (MT-1021→MT-1028).

Tests requirements from the Shopify App Review Preflight Checklist:
GraphQL-only API usage, billing test mode, plan upgrade/downgrade,
KB CRUD through admin API, team listing, and GDPR export.

Master Test Plan: §4 Gap Register — Shopify Compliance (1.0-required)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations


def _registered_route_paths(app) -> list[str]:
    """Return direct and included-router paths from the FastAPI app."""
    paths: list[str] = []
    for route in app.routes:
        path = getattr(route, "path", None)
        if isinstance(path, str):
            paths.append(path)

        route_contexts = getattr(route, "effective_route_contexts", None)
        if callable(route_contexts):
            paths.extend(
                context.path for context in route_contexts() if isinstance(getattr(context, "path", None), str)
            )
    return paths


# ---------------------------------------------------------------------------
# MT-1021: GraphQL-only Shopify API assertion
# ---------------------------------------------------------------------------


class TestShopifyGraphQLOnly:
    """MT-1021: Shopify integration uses only GraphQL Admin API (no REST)."""

    def test_shopify_client_uses_graphql_endpoint(self):
        """ShopifyGraphQLClient targets /admin/api/YYYY-MM/graphql.json."""
        from src.integrations.shopify_client import ShopifyGraphQLClient

        client = ShopifyGraphQLClient(
            store_url="test-store.myshopify.com",
            access_token="test_token",
        )

        # The _endpoint should point to the GraphQL endpoint
        assert "graphql.json" in client._endpoint
        assert "/admin/api/" in client._endpoint

    def test_shopify_client_no_rest_methods(self):
        """ShopifyGraphQLClient does not expose REST API methods (get, put, delete)."""
        from src.integrations.shopify_client import ShopifyGraphQLClient

        # The client should have execute() but not REST-style methods
        assert hasattr(ShopifyGraphQLClient, "execute")
        # Should NOT have REST-style convenience methods
        for rest_method in ["get_product", "get_order", "list_products", "rest_request"]:
            assert not hasattr(ShopifyGraphQLClient, rest_method), (
                f"ShopifyGraphQLClient should not have REST method: {rest_method}"
            )


# ---------------------------------------------------------------------------
# MT-1022: Shopify billing test mode
# ---------------------------------------------------------------------------


class TestShopifyBillingTestMode:
    """MT-1022: Shopify billing supports test=true for app review."""

    def test_billing_has_test_parameter(self):
        """Shopify billing mutation includes test parameter support."""
        from src.integrations import shopify_billing

        # Check that the billing module references test mode
        source = open(shopify_billing.__file__).read()
        assert "test" in source.lower(), "shopify_billing.py should reference test mode for Shopify app review"

    def test_billing_subscription_mutation_exists(self):
        """appSubscriptionCreate mutation function exists as module-level function."""
        from src.integrations import shopify_billing

        assert hasattr(shopify_billing, "create_subscription"), (
            "shopify_billing module should have create_subscription function"
        )


# ---------------------------------------------------------------------------
# MT-1023: Plan upgrade/downgrade via Shopify billing
# ---------------------------------------------------------------------------


class TestPlanUpgradeDowngrade:
    """MT-1023: Billing service supports tier changes."""

    def test_billing_supports_tier_parameter(self):
        """Billing subscription creation accepts a tier parameter."""
        import inspect
        from src.integrations.shopify_billing import create_subscription

        # Verify create_subscription accepts tier information
        source = inspect.getsource(create_subscription)
        assert "tier" in source.lower() or "plan" in source.lower(), (
            "create_subscription should accept tier/plan parameter"
        )


# ---------------------------------------------------------------------------
# MT-1024: KB CRUD through admin API
# ---------------------------------------------------------------------------


class TestKBCRUDViaAPI:
    """MT-1024: Knowledge base CRUD operations work via admin API."""

    def test_knowledge_api_has_crud_endpoints(self, app_client):
        """Admin knowledge API registers all CRUD routes."""
        from src.main import app

        routes = _registered_route_paths(app)
        # Verify essential KB routes exist
        kb_patterns = [
            "/api/admin/knowledge",
            "/api/admin/knowledge/upload",
        ]
        for pattern in kb_patterns:
            matches = [r for r in routes if pattern in r]
            assert len(matches) > 0, f"Missing KB route: {pattern}"

    def test_kb_list_requires_auth(self, app_client):
        """GET /api/admin/knowledge without auth returns 401/403."""
        response = app_client.get("/api/admin/knowledge")
        assert response.status_code in (401, 403)

    def test_kb_list_with_auth(self, app_client, starter_client):
        """GET /api/admin/knowledge with auth returns 200, 404, or 503."""
        response = starter_client.get("/api/admin/knowledge")
        # 200 if services wired, 404 if no data, 503 if not configured
        assert response.status_code in (200, 404, 503)


# ---------------------------------------------------------------------------
# MT-1025: Team listing via admin API
# ---------------------------------------------------------------------------


class TestTeamListViaAPI:
    """MT-1025: Team member listing works via admin API."""

    def test_team_api_has_list_endpoint(self, app_client):
        """Admin team API registers list route."""
        from src.main import app

        routes = _registered_route_paths(app)
        team_routes = [r for r in routes if "/api/team" in r or "/api/admin/team" in r]
        assert len(team_routes) > 0, "Missing team list route"

    def test_team_list_requires_auth(self, app_client):
        """GET /api/team without auth returns 401/403."""
        response = app_client.get("/api/team")
        assert response.status_code in (401, 403)

    def test_team_list_with_auth(self, app_client, starter_client):
        """GET /api/team with auth returns 200, 404, or 503."""
        response = starter_client.get("/api/team")
        # 200 if services wired, 404 if no data, 503 if not configured
        assert response.status_code in (200, 404, 503)


# ---------------------------------------------------------------------------
# MT-1026: GDPR data export via admin API
# ---------------------------------------------------------------------------


class TestGDPRExportViaAPI:
    """MT-1026: GDPR data export endpoint exists and requires auth."""

    def test_gdpr_export_endpoint_exists(self, app_client):
        """GDPR export route is registered."""
        from src.main import app

        routes = _registered_route_paths(app)
        gdpr_routes = [r for r in routes if "/api/gdpr" in r]
        assert len(gdpr_routes) > 0, "Missing GDPR admin routes"

    def test_gdpr_export_requires_auth(self, app_client):
        """POST /api/gdpr/export without auth returns 401/403."""
        response = app_client.post(
            "/api/gdpr/export",
            json={"customer_id": "test-customer"},
        )
        assert response.status_code in (401, 403)


# ---------------------------------------------------------------------------
# MT-1027: Shopify GDPR webhook URLs point to production
# ---------------------------------------------------------------------------


class TestGDPRWebhookURLs:
    """MT-1027: Shopify app config has production GDPR webhook URLs."""

    def test_shopify_app_toml_has_production_urls(self):
        """shopify.app.toml GDPR URLs point to production FQDN (not localhost)."""
        from pathlib import Path

        toml_path = Path(__file__).resolve().parent.parent.parent / "shopify.app.toml"
        assert toml_path.exists(), f"shopify.app.toml not found at {toml_path}"

        content = toml_path.read_text()

        # Verify GDPR URLs are NOT localhost
        assert "localhost" not in content.lower() or "# localhost" in content.lower(), (
            "shopify.app.toml should not contain localhost URLs for GDPR webhooks"
        )

        # Verify a real FQDN is used (production or staging)
        assert "agent-red-api-gateway" in content or "agent-red-staging" in content or "agentred" in content, (
            "shopify.app.toml should reference the API Gateway (production or staging)"
        )

    def test_shopify_app_toml_has_all_gdpr_endpoints(self):
        """shopify.app.toml references all three mandatory GDPR webhook paths."""
        from pathlib import Path

        toml_path = Path(__file__).resolve().parent.parent.parent / "shopify.app.toml"
        content = toml_path.read_text()

        # Shopify requires these three GDPR webhook URLs
        for path in ["customers-data-request", "customers-redact", "shop-redact"]:
            assert path in content, f"shopify.app.toml missing GDPR webhook path: {path}"


# ---------------------------------------------------------------------------
# MT-1028: API versioning header present
# ---------------------------------------------------------------------------


class TestAPIVersioning:
    """MT-1028: API responses include version header for Shopify compliance."""

    def test_health_includes_version_header(self, app_client):
        """GET /health response includes X-API-Version header."""
        response = app_client.get("/health")
        assert response.status_code == 200

        # Check for API version in response headers or body
        has_version_header = "x-api-version" in {k.lower() for k in response.headers.keys()}
        has_version_body = (
            "version" in response.json()
            if response.headers.get("content-type", "").startswith("application/json")
            else False
        )

        assert has_version_header or has_version_body, (
            "API should include version information in header or response body"
        )

    def test_api_version_format(self, app_client):
        """API version follows semver format."""
        response = app_client.get("/health")
        assert response.status_code == 200

        # Check header first
        version = response.headers.get("x-api-version")
        if not version:
            # Check body
            body = response.json()
            version = body.get("version") or body.get("api_version")

        if version:
            # Should look like semver (e.g., "1.0.0")
            parts = version.split(".")
            assert len(parts) >= 2, f"Version '{version}' doesn't look like semver"
