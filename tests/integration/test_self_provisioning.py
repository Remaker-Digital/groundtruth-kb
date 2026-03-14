"""Tests for WI-1107: Self-provisioning test infrastructure.

Verifies:
- Test provisioning endpoint exists and is gated by environment
- Production environment returns 403
- Non-production environments return keys in response
- TestProvisionResponse model has correct fields
- _self_provision helper module works correctly
- Pipeline --self-provision flag integration

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Endpoint registration tests
# ---------------------------------------------------------------------------


class TestProvisionEndpointExists:
    """Verify the test provisioning endpoint is registered on the router."""

    def test_endpoint_registered(self) -> None:
        """POST /test/provision-tenant must be a registered route."""
        from src.multi_tenant.superadmin_api._tenants import router
        route_paths = [r.path for r in router.routes]
        assert "/api/superadmin/test/provision-tenant" in route_paths

    def test_endpoint_method_is_post(self) -> None:
        """Endpoint must accept POST method."""
        from src.multi_tenant.superadmin_api._tenants import router
        for route in router.routes:
            if getattr(route, "path", "") == "/api/superadmin/test/provision-tenant":
                assert "POST" in route.methods
                break
        else:
            pytest.fail("Route /test/provision-tenant not found")

    def test_response_model_has_key_fields(self) -> None:
        """TestProvisionResponse must include user_api_key and widget_key."""
        from src.multi_tenant.superadmin_api._tenants import TestProvisionResponse
        fields = TestProvisionResponse.model_fields
        assert "user_api_key" in fields
        assert "widget_key" in fields
        assert "tenant_id" in fields
        assert "status" in fields
        assert "tier" in fields

    def test_response_model_keys_are_optional(self) -> None:
        """Keys should be optional (provisioning may partially fail)."""
        from src.multi_tenant.superadmin_api._tenants import TestProvisionResponse
        resp = TestProvisionResponse(
            tenant_id="test-123",
            status="active",
            tier="starter",
            superadmin_email="test@example.com",
        )
        assert resp.user_api_key is None
        assert resp.widget_key is None


# ---------------------------------------------------------------------------
# Production gate tests
# ---------------------------------------------------------------------------


class TestProductionGate:
    """Verify endpoint is blocked in production."""

    @pytest.mark.asyncio
    async def test_production_returns_403(self) -> None:
        """ENVIRONMENT=production must return 403."""
        from src.multi_tenant.superadmin_api._tenants import test_provision_tenant
        from src.multi_tenant.superadmin_api._tenants import CreateTenantRequest
        from src.multi_tenant.auth import TenantContext

        body = CreateTenantRequest(
            merchant_name="Test",
            superadmin_email="test@example.com",
            tier="starter",
        )
        ctx = TenantContext(
            tenant_id="__platform__",
            is_platform_admin=True,
        )

        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            from fastapi import HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await test_provision_tenant(body, ctx)
            assert exc_info.value.status_code == 403
            assert "SPEC-1673" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_staging_does_not_return_403(self) -> None:
        """ENVIRONMENT=staging must NOT raise 403 (may fail for other reasons)."""
        from src.multi_tenant.superadmin_api._tenants import test_provision_tenant
        from src.multi_tenant.superadmin_api._tenants import CreateTenantRequest
        from src.multi_tenant.auth import TenantContext

        body = CreateTenantRequest(
            merchant_name="Test",
            superadmin_email="test@example.com",
            tier="starter",
        )
        ctx = TenantContext(
            tenant_id="__platform__",
            is_platform_admin=True,
        )

        with patch.dict(os.environ, {"ENVIRONMENT": "staging"}):
            from fastapi import HTTPException
            # Will raise 503 (service not initialized) — NOT 403
            with pytest.raises(HTTPException) as exc_info:
                await test_provision_tenant(body, ctx)
            assert exc_info.value.status_code != 403

    @pytest.mark.asyncio
    async def test_development_does_not_return_403(self) -> None:
        """ENVIRONMENT=development (default) must NOT raise 403."""
        from src.multi_tenant.superadmin_api._tenants import test_provision_tenant
        from src.multi_tenant.superadmin_api._tenants import CreateTenantRequest
        from src.multi_tenant.auth import TenantContext

        body = CreateTenantRequest(
            merchant_name="Test",
            superadmin_email="test@example.com",
            tier="starter",
        )
        ctx = TenantContext(
            tenant_id="__platform__",
            is_platform_admin=True,
        )

        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            from fastapi import HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await test_provision_tenant(body, ctx)
            # Must NOT be 403 (production gate) — may be 500/503 (not initialized)
            assert exc_info.value.status_code != 403


# ---------------------------------------------------------------------------
# Self-provision helper module tests
# ---------------------------------------------------------------------------


class TestProvisionedTenantModel:
    """Verify the ProvisionedTenant dataclass."""

    def test_dataclass_fields(self) -> None:
        """ProvisionedTenant must have required credential fields."""
        from scripts._self_provision import ProvisionedTenant
        t = ProvisionedTenant(
            tenant_id="test-123",
            user_api_key="ar_user_test_key",
            widget_key="pk_live_test_widget",
            tier="starter",
            email="test@example.com",
        )
        assert t.tenant_id == "test-123"
        assert t.user_api_key == "ar_user_test_key"
        assert t.widget_key == "pk_live_test_widget"
        assert t.warnings == []

    def test_warnings_default_empty(self) -> None:
        """Warnings must default to empty list."""
        from scripts._self_provision import ProvisionedTenant
        t = ProvisionedTenant(
            tenant_id="x", user_api_key="x", widget_key="x",
            tier="starter", email="x@x.com",
        )
        assert isinstance(t.warnings, list)
        assert len(t.warnings) == 0


class TestProvisionTestTenant:
    """Test the provision_test_tenant function."""

    def test_raises_on_403(self) -> None:
        """Must raise RuntimeError with SPEC-1673 message on 403."""
        from scripts._self_provision import provision_test_tenant
        import httpx

        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.text = "Forbidden"

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.return_value = mock_resp
            mock_client_cls.return_value = mock_client

            with pytest.raises(RuntimeError, match="production"):
                provision_test_tenant("https://example.com", "ar_spa_plat_test")

    def test_raises_on_non_201(self) -> None:
        """Must raise RuntimeError on non-201 status."""
        from scripts._self_provision import provision_test_tenant

        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal error"

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.return_value = mock_resp
            mock_client_cls.return_value = mock_client

            with pytest.raises(RuntimeError, match="HTTP 500"):
                provision_test_tenant("https://example.com", "ar_spa_plat_test")

    def test_raises_on_missing_key(self) -> None:
        """Must raise RuntimeError if response has no user API key."""
        from scripts._self_provision import provision_test_tenant

        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {
            "tenantId": "test-123",
            "status": "active",
            "tier": "starter",
            "superadminEmail": "test@example.com",
            "userApiKey": "",  # empty
            "widgetKey": "pk_live_test",
            "warnings": ["Superadmin provisioning failed"],
        }

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.return_value = mock_resp
            mock_client_cls.return_value = mock_client

            with pytest.raises(RuntimeError, match="no user API key"):
                provision_test_tenant("https://example.com", "ar_spa_plat_test")

    def test_success_returns_provisioned_tenant(self) -> None:
        """Successful provisioning returns ProvisionedTenant with keys."""
        from scripts._self_provision import provision_test_tenant

        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {
            "tenantId": "test-abc123",
            "status": "active",
            "tier": "professional",
            "superadminEmail": "test@pipeline.agentredcx.com",
            "userApiKey": "ar_user_test_abc123_secretkey",
            "widgetKey": "pk_live_test_abc123_widgetkey",
            "warnings": [],
        }

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.return_value = mock_resp
            mock_client_cls.return_value = mock_client

            result = provision_test_tenant("https://example.com", "ar_spa_plat_test",
                                          tier="professional")
            assert result.tenant_id == "test-abc123"
            assert result.user_api_key == "ar_user_test_abc123_secretkey"
            assert result.widget_key == "pk_live_test_abc123_widgetkey"
            assert result.tier == "professional"

    def test_auto_generates_email_and_name(self) -> None:
        """When email/name not provided, auto-generates unique values."""
        from scripts._self_provision import provision_test_tenant

        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {
            "tenantId": "generated-123",
            "status": "active",
            "tier": "starter",
            "superadminEmail": "auto@test.com",
            "userApiKey": "ar_user_gen_key",
            "widgetKey": "pk_live_gen_key",
            "warnings": [],
        }

        captured_body = {}
        def capture_post(url, json=None, headers=None):
            captured_body.update(json or {})
            return mock_resp

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post = capture_post
            mock_client_cls.return_value = mock_client

            result = provision_test_tenant("https://example.com", "ar_spa_plat_test")
            # Should have auto-generated merchantName and superadminEmail
            assert "merchantName" in captured_body
            assert "superadminEmail" in captured_body
            assert "@pipeline.agentredcx.com" in captured_body["superadminEmail"]


class TestCleanupTestTenant:
    """Test the cleanup_test_tenant function."""

    def test_cleanup_returns_true_on_success(self) -> None:
        """Cleanup returns True when expiry set successfully."""
        from scripts._self_provision import cleanup_test_tenant

        mock_resp = MagicMock()
        mock_resp.status_code = 200

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.patch.return_value = mock_resp
            mock_client_cls.return_value = mock_client

            assert cleanup_test_tenant("https://example.com", "ar_spa_plat_test", "tenant-123")

    def test_cleanup_returns_false_on_failure(self) -> None:
        """Cleanup returns False on HTTP error."""
        from scripts._self_provision import cleanup_test_tenant

        mock_resp = MagicMock()
        mock_resp.status_code = 500

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.patch.return_value = mock_resp
            mock_client_cls.return_value = mock_client

            assert not cleanup_test_tenant("https://example.com", "ar_spa_plat_test", "tenant-123")

    def test_cleanup_returns_false_on_exception(self) -> None:
        """Cleanup returns False on network error (never raises)."""
        from scripts._self_provision import cleanup_test_tenant

        with patch("httpx.Client") as mock_client_cls:
            mock_client_cls.side_effect = ConnectionError("Network unreachable")
            assert not cleanup_test_tenant("https://example.com", "ar_spa_plat_test", "tenant-123")


# ---------------------------------------------------------------------------
# Pipeline integration tests
# ---------------------------------------------------------------------------


class TestPipelineSelfProvisionFlag:
    """Verify test_pipeline.py accepts --self-provision flag."""

    def test_argparser_accepts_self_provision(self) -> None:
        """Pipeline main() source must contain --self-provision flag."""
        import inspect
        # Import the module carefully — avoid triggering argparse
        import importlib
        spec = importlib.util.find_spec("scripts.test_pipeline")
        assert spec is not None, "scripts.test_pipeline must be importable"
        source = spec.origin
        with open(source, "r", encoding="utf-8") as f:
            content = f.read()
        assert "--self-provision" in content

    def test_self_provision_function_exists(self) -> None:
        """_self_provision_tenants function must be defined in test_pipeline."""
        import importlib
        spec = importlib.util.find_spec("scripts.test_pipeline")
        with open(spec.origin, "r", encoding="utf-8") as f:
            content = f.read()
        assert "def _self_provision_tenants(" in content

    def test_cleanup_function_exists(self) -> None:
        """_cleanup_provisioned_tenants function must be defined in test_pipeline."""
        import importlib
        spec = importlib.util.find_spec("scripts.test_pipeline")
        with open(spec.origin, "r", encoding="utf-8") as f:
            content = f.read()
        assert "def _cleanup_provisioned_tenants(" in content


class TestSeedMidflightSelfProvision:
    """Verify seed_midflight.py accepts --self-provision flag."""

    def test_run_seed_accepts_self_provision(self) -> None:
        """run_seed() must accept self_provision parameter."""
        import inspect
        from scripts.seed_midflight import run_seed
        sig = inspect.signature(run_seed)
        assert "self_provision" in sig.parameters
        assert "spa_key" in sig.parameters

    def test_main_function_has_self_provision_arg(self) -> None:
        """seed_midflight main() must accept --self-provision CLI flag."""
        from scripts.seed_midflight import main
        import inspect
        source = inspect.getsource(main)
        assert "--self-provision" in source


# ---------------------------------------------------------------------------
# SPEC-1673 compliance tests
# ---------------------------------------------------------------------------


class TestSpec1673Compliance:
    """Verify SPEC-1673 compliance of the self-provisioning design."""

    def test_regular_create_tenant_has_no_key_fields(self) -> None:
        """CreateTenantResponse must NOT have key fields (SPEC-1673)."""
        from src.multi_tenant.superadmin_api._tenants import CreateTenantResponse
        fields = CreateTenantResponse.model_fields
        assert "user_api_key" not in fields
        assert "widget_key" not in fields
        assert "superadmin_api_key" not in fields
        assert "keys_delivered_via_email" in fields

    def test_test_provision_has_key_fields(self) -> None:
        """TestProvisionResponse must have key fields for automation."""
        from src.multi_tenant.superadmin_api._tenants import TestProvisionResponse
        fields = TestProvisionResponse.model_fields
        assert "user_api_key" in fields
        assert "widget_key" in fields

    def test_endpoints_are_separate(self) -> None:
        """Regular and test provisioning must be separate endpoints."""
        from src.multi_tenant.superadmin_api._tenants import router
        paths = [r.path for r in router.routes if hasattr(r, "path")]
        assert "/api/superadmin/tenants" in paths  # Regular (SPEC-1673 compliant)
        assert "/api/superadmin/test/provision-tenant" in paths  # Test-only

    def test_helper_module_sends_to_test_endpoint(self) -> None:
        """_self_provision must POST to /test/provision-tenant, not /tenants."""
        import inspect
        from scripts._self_provision import provision_test_tenant
        source = inspect.getsource(provision_test_tenant)
        assert "/api/superadmin/test/provision-tenant" in source
        assert "/api/superadmin/test/provision-tenant" in source
