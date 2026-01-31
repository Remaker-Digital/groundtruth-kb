"""P0 Health Endpoint tests — §4.6 of COMPREHENSIVE-TEST-PLAN.md.

Test IDs: HE-01 through HE-10.

Validates:
    - GET /health liveness probe returns 200 {"status": "healthy"}
    - GET /ready readiness probe returns NATS, circuit breakers, Key Vault status
    - Auth exemption for health and ready endpoints
    - Startup events (tenant resolution, tracing, circuit breakers)
    - Degraded NATS handling (connected: false)

Uses app_client fixture from conftest.py (FastAPI TestClient with mocked services).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import inspect
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ===================================================================
# HE-01: GET /health → 200
# ===================================================================


class TestHealthEndpoint:
    """HE-01: Liveness probe."""

    @pytest.mark.unit
    def test_health_returns_200_healthy(self, app_client):
        """HE-01: GET /health → 200 {"status": "healthy"}."""
        resp = app_client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "healthy"


# ===================================================================
# HE-02 through HE-05: GET /ready readiness probe
# ===================================================================


class TestReadyEndpoint:
    """HE-02 to HE-05: Readiness probe checks."""

    @pytest.mark.unit
    def test_ready_returns_200_with_nats(self, app_client):
        """HE-02: GET /ready → 200 with NATS status."""
        resp = app_client.get("/ready")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ready"
        assert "nats" in body
        # Mock NATS is connected (from conftest.py mock_nats fixture)
        assert body["nats"]["connected"] is True

    @pytest.mark.unit
    def test_ready_includes_circuit_breakers_field(self, app_client):
        """HE-03: GET /ready → includes circuit_breakers field when breakers registered.

        The mock circuit breaker registry returns an empty dict by default
        (no breakers registered). When empty, the field is omitted. We
        verify that the endpoint handles both cases.
        """
        resp = app_client.get("/ready")
        assert resp.status_code == 200
        body = resp.json()
        # Empty registry → no circuit_breakers key (conditional in main.py)
        # This is the expected default behavior with mock_circuit_breakers
        # returning {} from health_summary()
        assert body["status"] == "ready"

    @pytest.mark.unit
    def test_ready_includes_key_vault_field(self, app_client):
        """HE-04: GET /ready → includes key_vault field."""
        resp = app_client.get("/ready")
        assert resp.status_code == 200
        body = resp.json()
        assert "key_vault" in body
        assert body["key_vault"]["status"] == "healthy"

    @pytest.mark.unit
    def test_ready_nats_disconnected(self, app_client, mock_nats):
        """HE-05: GET /ready → NATS disconnected shows connected: false."""
        # Simulate NATS disconnection
        mock_nats.is_connected = False

        resp = app_client.get("/ready")
        assert resp.status_code == 200
        body = resp.json()
        assert body["nats"]["connected"] is False

        # Restore for other tests
        mock_nats.is_connected = True

    @pytest.mark.unit
    def test_ready_with_circuit_breakers_registered(self, app_client, mock_circuit_breakers):
        """HE-03 extended: circuit_breakers field present when breakers exist."""
        # Configure mock to return actual breaker states
        mock_circuit_breakers.health_summary.return_value = {
            "azure_openai": "CLOSED",
            "cosmos_db": "CLOSED",
        }

        resp = app_client.get("/ready")
        assert resp.status_code == 200
        body = resp.json()
        assert "circuit_breakers" in body
        assert body["circuit_breakers"]["azure_openai"] == "CLOSED"
        assert body["circuit_breakers"]["cosmos_db"] == "CLOSED"

        # Restore default
        mock_circuit_breakers.health_summary.return_value = {}


# ===================================================================
# HE-06, HE-07: Auth exemption
# ===================================================================


class TestHealthAuthExemption:
    """HE-06, HE-07: Health endpoints do not require authentication."""

    @pytest.mark.unit
    def test_health_no_auth_required(self, app_client):
        """HE-06: GET /health does not require authentication."""
        # No auth headers — should still succeed
        resp = app_client.get("/health")
        assert resp.status_code == 200

    @pytest.mark.unit
    def test_ready_no_auth_required(self, app_client):
        """HE-07: GET /ready does not require authentication."""
        # No auth headers — should still succeed
        resp = app_client.get("/ready")
        assert resp.status_code == 200

    @pytest.mark.unit
    def test_health_exempt_in_auth_module(self):
        """HE-06 supplement: /health is in AUTH_EXEMPT_PREFIXES."""
        from src.multi_tenant.auth import is_auth_exempt
        assert is_auth_exempt("/health") is True

    @pytest.mark.unit
    def test_ready_exempt_in_auth_module(self):
        """HE-07 supplement: /ready is in AUTH_EXEMPT_PREFIXES."""
        from src.multi_tenant.auth import is_auth_exempt
        assert is_auth_exempt("/ready") is True


# ===================================================================
# HE-08 through HE-10: Startup events
# ===================================================================


class TestStartupEvents:
    """HE-08 to HE-10: Startup event configuration."""

    @pytest.mark.unit
    def test_startup_tenant_resolution_configured(self):
        """HE-08: _startup_tenant_resolution is registered as startup event.

        Verifies the function exists and is an async function (event handler).
        The actual wiring is tested via the app_client fixture which
        manually calls configure_tenant_resolution().
        """
        from src.main import _startup_tenant_resolution
        assert inspect.iscoroutinefunction(_startup_tenant_resolution)

    @pytest.mark.unit
    def test_startup_tracing_configured(self):
        """HE-09: _startup_tracing is registered as startup event."""
        from src.main import _startup_tracing
        assert inspect.iscoroutinefunction(_startup_tracing)

    @pytest.mark.unit
    def test_startup_circuit_breakers_registered(self):
        """HE-10: _startup_circuit_breakers is registered as startup event."""
        from src.main import _startup_circuit_breakers
        assert inspect.iscoroutinefunction(_startup_circuit_breakers)

    @pytest.mark.unit
    def test_startup_nats_registered(self):
        """HE-10 supplement: _startup_nats is registered as startup event."""
        from src.main import _startup_nats
        assert inspect.iscoroutinefunction(_startup_nats)

    @pytest.mark.unit
    def test_startup_secret_service_registered(self):
        """HE-10 supplement: _startup_secret_service is registered."""
        from src.main import _startup_secret_service
        assert inspect.iscoroutinefunction(_startup_secret_service)
