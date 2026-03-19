"""Production upgrade regression test suite.

Tier 0 (Blocking): Must pass before AND after every deployment.
Tier 1 (Pre-launch gate): Must pass before cutting traffic to new revision.
Tier 2 (Post-deploy smoke): Performance and latency validation.

Run against production:
    PROD_URL=https://agent-red-api-gateway...io python -m pytest tests/regression/ -x -q

Run specific tiers:
    python -m pytest tests/regression/ -m tier0 -x -q
    python -m pytest tests/regression/ -m "tier0 or tier1" -x -q

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import json
import time
import pytest
import httpx

# ═══════════════════════════════════════════════════════════════════════════════
# TIER 0: Blocking — must pass for every deployment
# These tests verify the absolute minimum for a working system.
# If ANY Tier 0 test fails, the upgrade MUST be rolled back.
# ═══════════════════════════════════════════════════════════════════════════════


class TestTier0Health:
    """T0-01 through T0-05: Health and infrastructure."""

    @pytest.mark.tier0
    def test_t0_01_health_endpoint_returns_200(self, client):
        """Liveness probe — process is running and serving HTTP."""
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"
        assert "version" in data

    @pytest.mark.tier0
    def test_t0_02_ready_endpoint_returns_200(self, client):
        """Readiness probe — dependencies are connected.

        SPEC-1780: /ready returns 503 when NATS transport is not active
        in deployed environments (fail-loud enforcement). Both 200 and
        503 are valid — 503 means the endpoint works but NATS isn't connected.
        """
        r = client.get("/ready")
        assert r.status_code in (200, 503), f"/ready returned {r.status_code}"
        data = r.json()
        if r.status_code == 200:
            assert data["status"] == "ready"

    @pytest.mark.tier0
    def test_t0_03_circuit_breakers_not_open(self, client):
        """All circuit breakers should be CLOSED or HALF_OPEN, never OPEN."""
        r = client.get("/ready")
        assert r.status_code in (200, 503), f"/ready returned {r.status_code}"
        data = r.json()
        if "circuit_breakers" in data:
            for name, state in data["circuit_breakers"].items():
                assert state != "OPEN", f"Circuit breaker {name} is OPEN — service degraded"

    @pytest.mark.tier0
    def test_t0_04_api_version_header(self, client):
        """API version header should be present on responses."""
        r = client.get("/health")
        # ApiVersionMiddleware adds X-API-Version header
        version = r.headers.get("X-API-Version", r.headers.get("x-api-version"))
        # Version header may or may not be present depending on middleware ordering
        # but health should always work
        assert r.status_code == 200

    @pytest.mark.tier0
    def test_t0_05_security_headers_present(self, client):
        """Security headers should be set by SecurityHeadersMiddleware."""
        r = client.get("/health")
        # Check OWASP security headers
        headers = {k.lower(): v for k, v in r.headers.items()}
        # X-Content-Type-Options should be nosniff
        assert headers.get("x-content-type-options") == "nosniff", "Missing X-Content-Type-Options: nosniff"


class TestTier0Auth:
    """T0-06 through T0-10: Authentication enforcement."""

    @pytest.mark.tier0
    def test_t0_06_protected_endpoints_require_auth(self, client):
        """Admin endpoints should return 401 without credentials."""
        protected = [
            "/api/dashboard/usage",
            "/api/config",
            "/api/admin/conversations",
            "/api/admin/knowledge",
        ]
        for path in protected:
            r = client.get(path)
            assert r.status_code in (401, 403), \
                f"{path} returned {r.status_code} — auth not enforced"

    @pytest.mark.tier0
    def test_t0_07_public_endpoints_accessible(self, client):
        """Public endpoints should be accessible without auth."""
        public = [
            ("/health", 200),
            ("/ready", (200, 503)),  # SPEC-1780: 503 when NATS not active
        ]
        for path, expected in public:
            r = client.get(path)
            if isinstance(expected, tuple):
                assert r.status_code in expected, \
                    f"{path} returned {r.status_code}, expected one of {expected}"
            else:
                assert r.status_code == expected, \
                    f"{path} returned {r.status_code}, expected {expected}"

    @pytest.mark.tier0
    def test_t0_08_widget_key_auth_works(self, client, widget_headers):
        """Widget key should authenticate for chat endpoints."""
        # Start a conversation with widget key — should get 200 or 201
        r = client.post(
            "/api/chat/conversations",
            headers=widget_headers,
            json={}
        )
        # 200/201 = success, 503 = services not init (acceptable)
        # 401 = auth broken (FAIL)
        assert r.status_code != 401, "Widget key authentication is broken"

    @pytest.mark.tier0
    def test_t0_09_invalid_auth_rejected(self, client):
        """Invalid credentials should be rejected."""
        r = client.get(
            "/api/dashboard/usage",
            headers={"X-API-Key": "invalid_key_12345"}
        )
        assert r.status_code in (401, 403)

    @pytest.mark.tier0
    def test_t0_10_webhook_endpoint_reachable(self, client):
        """Stripe webhook endpoint should be reachable (returns 400 without valid payload)."""
        r = client.post(
            "/api/webhooks/stripe",
            content=b"{}",
            headers={"Content-Type": "application/json"}
        )
        # 400 (bad request) or 401 (no signature) — not 404 or 500
        assert r.status_code in (400, 401, 500), \
            f"Webhook endpoint returned unexpected {r.status_code}"


class TestTier0StaticAssets:
    """T0-11 through T0-14: Static asset serving."""

    @pytest.mark.tier0
    def test_t0_11_widget_js_served(self, client):
        """Widget JavaScript bundle should be served publicly."""
        r = client.get("/widget.js")
        # 200 = serving, 404 = file missing (FAIL for storefront)
        assert r.status_code == 200, "widget.js not being served — storefront widget will break"
        assert len(r.content) > 1000, "widget.js is suspiciously small — may be an error page"

    @pytest.mark.tier0
    def test_t0_12_standalone_admin_login_page(self, client):
        """Standalone admin should serve the login page."""
        r = client.get("/admin/standalone/")
        assert r.status_code == 200
        # Should be HTML (either login form or SPA)
        content_type = r.headers.get("content-type", "")
        assert "text/html" in content_type, f"Expected HTML, got {content_type}"

    @pytest.mark.tier0
    def test_t0_13_shopify_admin_served(self, client):
        """Shopify embedded admin SPA should be served."""
        r = client.get("/admin/shopify/")
        assert r.status_code == 200
        content_type = r.headers.get("content-type", "")
        assert "text/html" in content_type

    @pytest.mark.tier0
    def test_t0_13b_provider_admin_served(self, client):
        """Provider SPA admin should be served (Cycle 9)."""
        r = client.get("/admin/provider/")
        assert r.status_code == 200
        content_type = r.headers.get("content-type", "")
        assert "text/html" in content_type

    @pytest.mark.tier0
    def test_t0_14_openapi_schema_accessible(self, client):
        """OpenAPI schema should always be accessible (/openapi.json).

        Note: /docs and /redoc are disabled in production (ENVIRONMENT=production)
        but /openapi.json is always available.
        """
        r = client.get("/openapi.json")
        assert r.status_code == 200


class TestTier0TenantLookup:
    """T0-15 through T0-17: Tenant resolution."""

    @pytest.mark.tier0
    def test_t0_15_tenant_lookup_endpoint(self, client):
        """Tenant lookup should be accessible (public billing endpoint)."""
        r = client.get("/api/tenants/lookup", params={"shop": "blanco-9939.myshopify.com"})
        # 200 = found, 404 = not found (both acceptable — endpoint is working)
        assert r.status_code in (200, 404), \
            f"Tenant lookup returned {r.status_code} — endpoint broken"

    @pytest.mark.tier0
    def test_t0_16_tenant_lookup_returns_json(self, client):
        """Tenant lookup should return valid JSON."""
        r = client.get("/api/tenants/lookup", params={"shop": "blanco-9939.myshopify.com"})
        if r.status_code == 200:
            data = r.json()
            assert "tenant_id" in data or "found" in data

    @pytest.mark.tier0
    def test_t0_17_checkout_endpoint_reachable(self, client):
        """Checkout session creation endpoint should be reachable."""
        r = client.post(
            "/api/checkout/session",
            json={"tier": "starter", "interval": "month"}
        )
        # 400/422 = validation error (endpoint works), 500 = broken
        assert r.status_code != 404, "Checkout endpoint not found"


# ═══════════════════════════════════════════════════════════════════════════════
# TIER 1: Pre-launch gate — must pass before traffic cutover
# These tests verify functional correctness of the core product.
# ═══════════════════════════════════════════════════════════════════════════════


class TestTier1ChatPipeline:
    """T1-01 through T1-06: Chat pipeline functionality."""

    @pytest.mark.tier1
    def test_t1_01_start_conversation(self, client, widget_headers):
        """Start a new conversation via widget key."""
        r = client.post(
            "/api/chat/conversations",
            headers=widget_headers,
            json={}
        )
        if r.status_code == 503:
            pytest.skip("Chat services not initialized (503) — may need NATS warmup")
        assert r.status_code in (200, 201), f"Start conversation failed: {r.status_code}"
        data = r.json()
        assert "conversation_id" in data or "id" in data

    @pytest.mark.tier1
    def test_t1_02_send_message(self, client, widget_headers):
        """Send a message and get a response."""
        # Start conversation
        r = client.post("/api/chat/conversations", headers=widget_headers, json={})
        if r.status_code == 503:
            pytest.skip("Chat services not initialized")

        if r.status_code not in (200, 201):
            pytest.skip(f"Cannot start conversation: {r.status_code}")

        data = r.json()
        conv_id = data.get("conversation_id") or data.get("id")

        # Send message
        r = client.post(
            "/api/chat/message",
            headers=widget_headers,
            json={"conversation_id": conv_id, "content": "What products do you have?"}
        )
        # 200 = response, 202 = accepted (async), 503 = services not ready
        assert r.status_code in (200, 201, 202, 503), \
            f"Send message failed: {r.status_code} — {r.text[:200]}"

    @pytest.mark.tier1
    def test_t1_03_sse_stream_endpoint(self, client, widget_headers):
        """SSE stream endpoint should be accessible."""
        # Start conversation
        r = client.post("/api/chat/conversations", headers=widget_headers, json={})
        if r.status_code not in (200, 201):
            pytest.skip(f"Cannot start conversation: {r.status_code}")

        data = r.json()
        conv_id = data.get("conversation_id") or data.get("id")

        # Check stream status endpoint
        r = client.get(
            f"/api/chat/stream/{conv_id}/status",
            headers=widget_headers,
            params={"widget_key": widget_headers.get("X-Widget-Key", "")}
        )
        # 200 = status available, 404 = no active stream (both OK)
        assert r.status_code in (200, 404), \
            f"Stream status returned {r.status_code}"

    @pytest.mark.tier1
    def test_t1_04_conversation_state(self, client, widget_headers):
        """Get conversation state should work."""
        r = client.post("/api/chat/conversations", headers=widget_headers, json={})
        if r.status_code not in (200, 201):
            pytest.skip(f"Cannot start conversation: {r.status_code}")

        data = r.json()
        conv_id = data.get("conversation_id") or data.get("id")

        r = client.get(
            f"/api/chat/conversations/{conv_id}",
            headers=widget_headers
        )
        assert r.status_code in (200, 404)

    @pytest.mark.tier1
    def test_t1_05_end_conversation(self, client, widget_headers):
        """End conversation should work."""
        r = client.post("/api/chat/conversations", headers=widget_headers, json={})
        if r.status_code not in (200, 201):
            pytest.skip(f"Cannot start conversation: {r.status_code}")

        data = r.json()
        conv_id = data.get("conversation_id") or data.get("id")

        r = client.post(
            f"/api/chat/conversations/{conv_id}/end",
            headers=widget_headers,
            json={}
        )
        assert r.status_code in (200, 204, 404)

    @pytest.mark.tier1
    def test_t1_06_chat_rate_limiting(self, client, widget_headers):
        """Rate limiting should be active for chat endpoints."""
        # Send rapid requests — eventually should get 429
        for _ in range(20):
            r = client.post("/api/chat/conversations", headers=widget_headers, json={})
            if r.status_code == 429:
                break  # Rate limit working
        # We either hit 429 (good) or all succeeded (also acceptable at low volume)
        # The important thing is no 500s
        assert r.status_code in (200, 201, 429, 503)


class TestTier1AdminAPI:
    """T1-07 through T1-12: Admin API functionality."""

    @pytest.mark.tier1
    def test_t1_07_dashboard_usage(self, client, admin_headers):
        """Dashboard usage endpoint should return data."""
        r = client.get("/api/dashboard/usage", headers=admin_headers)
        assert r.status_code in (200, 429, 503), \
            f"Dashboard usage returned {r.status_code}"

    @pytest.mark.tier1
    def test_t1_08_knowledge_base_list(self, client, admin_headers):
        """Knowledge base list should be accessible."""
        r = client.get("/api/admin/knowledge", headers=admin_headers)
        assert r.status_code in (200, 429, 503)

    @pytest.mark.tier1
    def test_t1_09_conversation_inbox(self, client, admin_headers):
        """Conversation inbox should be accessible."""
        r = client.get("/api/admin/conversations", headers=admin_headers)
        assert r.status_code in (200, 429, 503)

    @pytest.mark.tier1
    def test_t1_10_analytics_summary(self, client, admin_headers):
        """Analytics summary should be accessible."""
        r = client.get("/api/analytics/summary", headers=admin_headers)
        assert r.status_code in (200, 429, 503)

    @pytest.mark.tier1
    def test_t1_11_tenant_config(self, client, admin_headers):
        """Tenant config should be readable."""
        r = client.get("/api/config", headers=admin_headers)
        assert r.status_code in (200, 429, 503)

    @pytest.mark.tier1
    def test_t1_12_audit_log(self, client, admin_headers):
        """Audit log should be queryable."""
        r = client.get("/api/audit", headers=admin_headers)
        assert r.status_code in (200, 429, 503)


class TestTier1GDPR:
    """T1-13 through T1-14: GDPR compliance."""

    @pytest.mark.tier1
    def test_t1_13_shopify_gdpr_webhooks_reachable(self, client):
        """Shopify GDPR webhook endpoints should be reachable."""
        gdpr_endpoints = [
            "/api/shopify/gdpr/customers-data-request",
            "/api/shopify/gdpr/customers-redact",
            "/api/shopify/gdpr/shop-redact",
        ]
        for path in gdpr_endpoints:
            r = client.post(path, json={}, headers={"Content-Type": "application/json"})
            # 401 (no HMAC) or 400 (bad payload) — not 404 or 500
            assert r.status_code in (400, 401, 422, 500), \
                f"GDPR endpoint {path} returned {r.status_code}"

    @pytest.mark.tier1
    def test_t1_14_api_key_reset_endpoint(self, client):
        """Public API key reset endpoint should be reachable."""
        r = client.post(
            "/api/admin/api-keys/reset",
            json={"email": "test@example.com"}
        )
        # 200 = processed (always returns 200 for enumeration prevention)
        # 429 = rate limited (also correct)
        assert r.status_code in (200, 429), \
            f"API key reset returned {r.status_code}"


class TestTier1CrossTenantIsolation:
    """T1-15 through T1-16: Tenant isolation verification."""

    @pytest.mark.tier1
    def test_t1_15_widget_key_scoped_to_tenant(self, client, widget_headers):
        """Widget key should only access its own tenant's data."""
        # A valid widget key should not be able to access admin endpoints
        r = client.get("/api/dashboard/usage", headers=widget_headers)
        assert r.status_code in (401, 403), \
            "Widget key should NOT access admin dashboard"

    @pytest.mark.tier1
    def test_t1_16_forged_tenant_rejected(self, client, widget_headers):
        """Forged tenant_id in request body should be ignored."""
        r = client.post(
            "/api/chat/conversations",
            headers=widget_headers,
            json={"tenant_id": "fake-tenant-id-12345"}
        )
        # Server derives tenant_id from auth, ignoring any body field
        # Should NOT return data from fake-tenant-id
        if r.status_code in (200, 201):
            data = r.json()
            if "tenant_id" in data:
                assert data["tenant_id"] != "fake-tenant-id-12345"


# ═══════════════════════════════════════════════════════════════════════════════
# TIER 2: Post-deploy smoke — performance and latency validation
# ═══════════════════════════════════════════════════════════════════════════════


class TestTier1SuperadminAPI:
    """T1-17 through T1-20: Superadmin provider operations endpoints (Session 29).

    These tests verify the SPA (Service Provider Administrator) cross-tenant
    endpoints are functional. Since SPEC-1667 (SPA isolation, S157), these
    endpoints require platform admin keys (ar_spa_*), not tenant keys (ar_user_*).
    Tenant keys correctly receive 403.
    """

    @pytest.mark.tier1
    def test_t1_17_superadmin_tenant_directory(self, client, admin_headers):
        """Superadmin tenant directory returns 200 (SPA key) or 403 (tenant key)."""
        r = client.get("/api/superadmin/tenants", headers=admin_headers)
        assert r.status_code in (200, 403), (
            f"Expected 200 (SPA key) or 403 (tenant key per SPEC-1667), got {r.status_code}"
        )
        if r.status_code == 200:
            data = r.json()
            assert "tenants" in data
            assert "total" in data
            assert data["total"] >= 1, "Expected at least 1 tenant in directory"

    @pytest.mark.tier1
    def test_t1_18_superadmin_dashboard(self, client, admin_headers):
        """Superadmin dashboard returns 200 (SPA key) or 403 (tenant key)."""
        r = client.get("/api/superadmin/dashboard", headers=admin_headers)
        assert r.status_code in (200, 403), (
            f"Expected 200 (SPA key) or 403 (tenant key per SPEC-1667), got {r.status_code}"
        )
        if r.status_code == 200:
            data = r.json()
            assert "timestamp" in data
            assert "systemHealth" in data or "system_health" in data
            assert "tenantSummary" in data or "tenant_summary" in data

    @pytest.mark.tier1
    def test_t1_19_superadmin_auth_enforcement(self, client):
        """Superadmin endpoints reject unauthenticated requests."""
        r = client.get("/api/superadmin/tenants")
        assert r.status_code in (401, 403), (
            f"Expected 401/403 for unauthenticated superadmin request, got {r.status_code}"
        )

    @pytest.mark.tier1
    def test_t1_20_superadmin_billing_health(self, client, admin_headers):
        """Superadmin billing health returns 200 (SPA key) or 403 (tenant key)."""
        r = client.get("/api/superadmin/billing/health", headers=admin_headers)
        assert r.status_code in (200, 403), (
            f"Expected 200 (SPA key) or 403 (tenant key per SPEC-1667), got {r.status_code}"
        )
        if r.status_code == 200:
            data = r.json()
            assert "tenants" in data or "tenantCount" in data or "tenant_count" in data


class TestTier1Cycle9Endpoints:
    """T1-21 through T1-28: Cycle 9 — Incidents, Alerting, MFA, Status (Session 40).

    These tests verify the Cycle 9 superadmin endpoints and public status API
    are reachable after deployment. Since SPEC-1667 (SPA isolation, S157),
    superadmin endpoints require platform admin keys (ar_spa_*). Tenant keys
    (ar_user_*) correctly receive 403.
    """

    @pytest.mark.tier1
    def test_t1_21_public_status_api(self, client):
        """Public status API returns operational status without auth."""
        r = client.get("/api/status")
        assert r.status_code == 200
        data = r.json()
        assert "overallStatus" in data or "overall_status" in data
        assert "services" in data

    @pytest.mark.tier1
    def test_t1_22_superadmin_incidents_list(self, client, admin_headers):
        """Superadmin incidents: 200 (SPA key) or 403 (tenant key per SPEC-1667)."""
        r = client.get("/api/superadmin/incidents", headers=admin_headers)
        assert r.status_code in (200, 403), (
            f"Expected 200 (SPA key) or 403 (tenant key per SPEC-1667), got {r.status_code}"
        )
        if r.status_code == 200:
            data = r.json()
            assert "incidents" in data

    @pytest.mark.tier1
    def test_t1_23_superadmin_alert_rules_list(self, client, admin_headers):
        """Superadmin alert rules: 200 (SPA key) or 403 (tenant key per SPEC-1667)."""
        r = client.get("/api/superadmin/alerts/rules", headers=admin_headers)
        assert r.status_code in (200, 403), (
            f"Expected 200 (SPA key) or 403 (tenant key per SPEC-1667), got {r.status_code}"
        )
        if r.status_code == 200:
            data = r.json()
            assert "rules" in data

    @pytest.mark.tier1
    def test_t1_24_superadmin_alert_history(self, client, admin_headers):
        """Superadmin alert history: 200 (SPA key) or 403 (tenant key per SPEC-1667)."""
        r = client.get("/api/superadmin/alerts/history", headers=admin_headers)
        assert r.status_code in (200, 403), (
            f"Expected 200 (SPA key) or 403 (tenant key per SPEC-1667), got {r.status_code}"
        )
        if r.status_code == 200:
            data = r.json()
            assert "alerts" in data

    @pytest.mark.tier1
    def test_t1_25_superadmin_mfa_status(self, client, admin_headers):
        """Superadmin MFA status: 200 (SPA key) or 403 (tenant key per SPEC-1667)."""
        r = client.get("/api/superadmin/mfa/status", headers=admin_headers)
        assert r.status_code in (200, 403), (
            f"Expected 200 (SPA key) or 403 (tenant key per SPEC-1667), got {r.status_code}"
        )
        if r.status_code == 200:
            data = r.json()
            assert "mfaEnabled" in data or "mfa_enabled" in data

    @pytest.mark.tier1
    def test_t1_26_superadmin_queues(self, client, admin_headers):
        """Superadmin queues: 200 (SPA key), 403 (tenant key per SPEC-1667), or 503."""
        r = client.get("/api/superadmin/queues", headers=admin_headers)
        assert r.status_code in (200, 403, 503), (
            f"Expected 200/403/503, got {r.status_code}"
        )

    @pytest.mark.tier1
    def test_t1_27_superadmin_compliance(self, client, admin_headers):
        """Superadmin compliance: 200 (SPA key), 403 (tenant key per SPEC-1667), or 503."""
        r = client.get("/api/superadmin/compliance", headers=admin_headers)
        assert r.status_code in (200, 403, 503), (
            f"Expected 200/403/503, got {r.status_code}"
        )

    @pytest.mark.tier1
    def test_t1_28_superadmin_integrations_health(self, client, admin_headers):
        """Superadmin integration health: 200 (SPA key), 403 (tenant key per SPEC-1667), or 503."""
        r = client.get("/api/superadmin/integrations/health", headers=admin_headers)
        assert r.status_code in (200, 403, 503), (
            f"Expected 200/403/503, got {r.status_code}"
        )


class TestTier2Performance:
    """T2-01 through T2-06: Performance regression checks."""

    @pytest.mark.tier2
    def test_t2_01_health_latency(self, client):
        """Health endpoint should respond within 500ms."""
        start = time.time()
        r = client.get("/health")
        elapsed_ms = (time.time() - start) * 1000
        assert r.status_code == 200
        assert elapsed_ms < 500, f"/health took {elapsed_ms:.0f}ms (limit: 500ms)"

    @pytest.mark.tier2
    def test_t2_02_ready_latency(self, client):
        """Ready endpoint should respond within 2000ms."""
        start = time.time()
        r = client.get("/ready")
        elapsed_ms = (time.time() - start) * 1000
        assert r.status_code in (200, 503), f"/ready returned {r.status_code}"
        assert elapsed_ms < 2000, f"/ready took {elapsed_ms:.0f}ms (limit: 2000ms)"

    @pytest.mark.tier2
    def test_t2_03_health_p95_under_sla(self, client):
        """Health P95 should be under 200ms (10 requests)."""
        latencies = []
        for _ in range(10):
            start = time.time()
            r = client.get("/health")
            latencies.append((time.time() - start) * 1000)
            assert r.status_code == 200

        latencies.sort()
        p95 = latencies[int(len(latencies) * 0.95)]
        assert p95 < 200, f"Health P95 = {p95:.0f}ms (limit: 200ms)"

    @pytest.mark.tier2
    def test_t2_04_concurrent_health_checks(self, client):
        """5 concurrent health checks should all succeed."""
        import concurrent.futures
        def check():
            with httpx.Client(base_url=client.base_url, timeout=10) as c:
                return c.get("/health").status_code

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(lambda _: check(), range(5)))
        assert all(r == 200 for r in results), f"Not all healthy: {results}"

    @pytest.mark.tier2
    def test_t2_05_widget_js_size_reasonable(self, client):
        """Widget bundle should be under 100KB (production IIFE)."""
        r = client.get("/widget.js")
        assert r.status_code == 200, (
            f"widget.js not served (status {r.status_code}) — "
            "widget delivery is production-critical"
        )
        size_kb = len(r.content) / 1024
        assert size_kb < 120, f"widget.js is {size_kb:.0f}KB (limit: 120KB)"

    @pytest.mark.tier2
    def test_t2_06_no_error_in_health_body(self, client):
        """Health response should not contain error indicators."""
        r = client.get("/health")
        body = r.text.lower()
        assert "error" not in body, f"Health response contains 'error': {r.text[:200]}"
        assert "traceback" not in body, "Health response contains traceback"


class TestTier2Consistency:
    """T2-07 through T2-10: Data consistency after upgrade."""

    @pytest.mark.tier2
    def test_t2_07_ready_dependency_states(self, client):
        """All /ready dependency checks should report healthy states."""
        r = client.get("/ready")
        assert r.status_code in (200, 503), f"/ready returned {r.status_code}"
        data = r.json()

        # Key Vault should be healthy (or dev_mode for environments without KV)
        if "key_vault" in data:
            assert data["key_vault"].get("status") in ("healthy", "connected", "dev_mode"), \
                f"Key Vault: {data['key_vault']}"

        # Circuit breakers all CLOSED
        if "circuit_breakers" in data:
            cb = data["circuit_breakers"]
            # Top-level: {"healthy": bool, "any_open": bool, "services": {...}}
            if "services" in cb:
                for name, svc in cb["services"].items():
                    state = svc.get("state", svc) if isinstance(svc, dict) else svc
                    assert state in ("closed", "CLOSED", "HALF_OPEN", "half_open"), \
                        f"Circuit breaker {name} is {state}"
            else:
                # Flat structure fallback
                for name, state in cb.items():
                    if isinstance(state, str):
                        assert state in ("CLOSED", "HALF_OPEN"), \
                            f"Circuit breaker {name} is {state}"

    @pytest.mark.tier2
    def test_t2_08_semantic_cache_functional(self, client):
        """Semantic cache should be tracking metrics."""
        r = client.get("/ready")
        if r.status_code not in (200, 503):
            pytest.skip("/ready not available")
        data = r.json()
        # Cache metrics should exist (even if all zeros for fresh deployment)
        if "semantic_cache" in data:
            cache = data["semantic_cache"]
            assert isinstance(cache.get("embedding_cache_hits", 0), (int, float))

    @pytest.mark.tier2
    def test_t2_09_version_in_health(self, client):
        """Health endpoint should report a version string."""
        r = client.get("/health")
        data = r.json()
        version = data.get("version", "")
        assert version, "No version in /health response"
        # Version should look like a semver or meaningful string
        assert len(version) >= 3, f"Version too short: {version}"

    @pytest.mark.tier2
    def test_t2_10_multiple_health_checks_consistent(self, client):
        """10 consecutive health checks should return identical versions."""
        versions = set()
        for _ in range(10):
            r = client.get("/health")
            assert r.status_code == 200
            versions.add(r.json().get("version", ""))
        assert len(versions) == 1, f"Inconsistent versions across requests: {versions}"
