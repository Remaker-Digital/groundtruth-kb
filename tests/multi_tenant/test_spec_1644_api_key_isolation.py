"""SPEC-1644: API keys MUST NOT identify tenants — security invariant tests.

These tests enforce the critical security requirement that API keys
are ONLY used for authentication against a known tenant (from the URL),
never for tenant discovery.  Any cross-partition API key query is a
security violation.

Run:
    pytest tests/multi_tenant/test_spec_1644_api_key_isolation.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import inspect
import re
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

# All tests in this module are adversarial security tests (SPEC-1644)
pytestmark = [pytest.mark.security, pytest.mark.unit]

from src.multi_tenant.auth import hash_api_key  # noqa: E402


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
MIDDLEWARE_PATH = SRC_ROOT / "multi_tenant" / "middleware.py"
PROVISIONING_PATH = SRC_ROOT / "integrations" / "provisioning.py"
TENANT_REPO_PATH = SRC_ROOT / "multi_tenant" / "repositories" / "tenant.py"
TEAM_REPO_PATH = SRC_ROOT / "multi_tenant" / "repositories" / "team.py"


# ===================================================================
# 1. Structural tests — verify code CANNOT perform cross-partition
#    queries using API key hashes.
# ===================================================================


class TestNoKeyToTenantDiscovery:
    """Verify that no code path uses an API key hash to FIND a tenant."""

    def test_tenant_repo_has_no_find_by_api_key_hash(self):
        """TenantRepository must not have find_by_api_key_hash method.

        This was the cross-partition query that violated SPEC-1644.
        It has been replaced by verify_key_hash(tenant_id, key_hash).
        """
        from src.multi_tenant.repositories.tenant import TenantRepository
        assert not hasattr(TenantRepository, "find_by_api_key_hash"), (
            "TenantRepository.find_by_api_key_hash still exists — "
            "SPEC-1644 requires partition-scoped verify_key_hash() instead"
        )

    def test_team_repo_has_no_find_by_user_api_key_hash(self):
        """TeamMemberRepository must not have find_by_user_api_key_hash.

        Replaced by verify_user_key_hash(tenant_id, key_hash).
        """
        from src.multi_tenant.repositories.team import TeamMemberRepository
        assert not hasattr(TeamMemberRepository, "find_by_user_api_key_hash"), (
            "TeamMemberRepository.find_by_user_api_key_hash still exists — "
            "SPEC-1644 requires partition-scoped verify_user_key_hash() instead"
        )

    def test_provisioning_has_no_lookup_by_api_key(self):
        """provisioning.py must not have _lookup_by_api_key function.

        This was the handler that resolved API key → tenant across
        all partitions.  It violates SPEC-1644.
        """
        source = PROVISIONING_PATH.read_text()
        assert "_lookup_by_api_key" not in source, (
            "_lookup_by_api_key still exists in provisioning.py — "
            "SPEC-1644 forbids API key → tenant discovery"
        )

    def test_lookup_endpoint_does_not_accept_api_key(self):
        """GET /api/tenants/lookup must not use X-API-Key for discovery.

        The endpoint may still exist for channel lookups (shop/stripe_customer_id)
        but must not accept API keys as a lookup method.
        """
        source = PROVISIONING_PATH.read_text()
        # Find the lookup_tenant_endpoint function
        match = re.search(
            r'async def lookup_tenant_endpoint.*?(?=\nasync def |\nclass |\Z)',
            source,
            re.DOTALL,
        )
        assert match, "lookup_tenant_endpoint not found"
        func_source = match.group(0)

        # Must not contain API key lookup logic
        assert "_lookup_by_api_key" not in func_source, (
            "lookup_tenant_endpoint still calls _lookup_by_api_key"
        )
        assert "X-API-Key" not in func_source, (
            "lookup_tenant_endpoint still reads X-API-Key header — "
            "SPEC-1644 forbids API key tenant discovery"
        )


class TestPartitionScopedMethodsExist:
    """Verify partition-scoped verification methods exist."""

    def test_tenant_repo_has_verify_key_hash(self):
        """TenantRepository.verify_key_hash(tenant_id, key_hash) must exist."""
        from src.multi_tenant.repositories.tenant import TenantRepository
        assert hasattr(TenantRepository, "verify_key_hash"), (
            "TenantRepository.verify_key_hash missing — "
            "required by SPEC-1644 for partition-scoped auth"
        )
        sig = inspect.signature(TenantRepository.verify_key_hash)
        params = list(sig.parameters.keys())
        assert "tenant_id" in params, "verify_key_hash must accept tenant_id"
        assert "api_key_hash" in params or "key_hash" in params, (
            "verify_key_hash must accept a key hash parameter (api_key_hash or key_hash)"
        )

    def test_team_repo_has_verify_user_key_hash(self):
        """TeamMemberRepository.verify_user_key_hash(tenant_id, key_hash) must exist."""
        from src.multi_tenant.repositories.team import TeamMemberRepository
        assert hasattr(TeamMemberRepository, "verify_user_key_hash"), (
            "TeamMemberRepository.verify_user_key_hash missing — "
            "required by SPEC-1644 for partition-scoped user auth"
        )
        sig = inspect.signature(TeamMemberRepository.verify_user_key_hash)
        params = list(sig.parameters.keys())
        assert "tenant_id" in params, "verify_user_key_hash must accept tenant_id"
        assert "key_hash" in params, "verify_user_key_hash must accept key_hash"


class TestValidateKeyEndpointExists:
    """Verify POST /api/tenants/auth/validate-key endpoint exists."""

    def test_validate_key_endpoint_in_provisioning(self):
        """The validate-key endpoint must be declared in provisioning.py."""
        source = PROVISIONING_PATH.read_text()
        assert "validate-key" in source, (
            "POST /api/tenants/auth/validate-key not found in provisioning.py"
        )
        assert "ValidateKeyRequest" in source, (
            "ValidateKeyRequest model not found in provisioning.py"
        )

    def test_validate_key_requires_tenant_in_body(self):
        """ValidateKeyRequest must require a 'tenant' field."""
        from src.integrations.provisioning import ValidateKeyRequest
        fields = ValidateKeyRequest.model_fields
        assert "tenant" in fields, (
            "ValidateKeyRequest must require a 'tenant' field — "
            "SPEC-1644: caller must know the tenant before authenticating"
        )


# ===================================================================
# 2. Middleware behavioral tests — API key auth REQUIRES URL tenant.
# ===================================================================


class TestMiddlewareRequiresUrlTenant:
    """Verify middleware rejects API key auth without URL tenant."""

    def test_auth_api_key_requires_url_tenant_param(self):
        """_auth_api_key must accept url_tenant parameter."""
        from src.multi_tenant.middleware import TenantAuthMiddleware
        sig = inspect.signature(TenantAuthMiddleware._auth_api_key)
        params = list(sig.parameters.keys())
        assert "url_tenant" in params, (
            "_auth_api_key must accept url_tenant — "
            "SPEC-1644: URL tenant is required for partition-scoped auth"
        )

    @pytest.mark.asyncio
    async def test_api_key_without_url_tenant_raises(self):
        """API key auth without url_tenant must raise AuthenticationError."""
        from src.multi_tenant.auth import AuthenticationError
        from src.multi_tenant.middleware import TenantAuthMiddleware

        middleware = TenantAuthMiddleware(app=MagicMock())
        with pytest.raises(AuthenticationError, match="Tenant parameter is required"):
            await middleware._auth_api_key("ar_live_test123", url_tenant=None)

    @pytest.mark.asyncio
    async def test_api_key_with_empty_url_tenant_raises(self):
        """API key auth with empty string url_tenant must raise."""
        from src.multi_tenant.auth import AuthenticationError
        from src.multi_tenant.middleware import TenantAuthMiddleware

        middleware = TenantAuthMiddleware(app=MagicMock())
        with pytest.raises(AuthenticationError, match="Tenant parameter is required"):
            await middleware._auth_api_key("ar_live_test123", url_tenant="")

    @pytest.mark.asyncio
    async def test_spa_key_does_not_require_url_tenant(self):
        """SPA platform admin keys are exempt from URL tenant requirement."""
        from src.multi_tenant.middleware import (
            TenantAuthMiddleware,
            configure_tenant_resolution,
        )

        # Configure a mock SPA resolver
        mock_spa = AsyncMock(return_value={
            "admin_id": "admin-1",
            "email": "admin@test.com",
            "role": "superadmin",
            "is_active": True,
            "api_key_hash": hash_api_key("ar_spa_test123"),
        })
        configure_tenant_resolution(
            resolve_by_shop_domain=AsyncMock(),
            resolve_by_api_key_hash=AsyncMock(),
            resolve_by_spa_key_hash=mock_spa,
        )

        middleware = TenantAuthMiddleware(app=MagicMock())
        # Should NOT raise even without url_tenant
        ctx = await middleware._auth_api_key("ar_spa_test123", url_tenant=None)
        assert ctx.is_platform_admin


# ===================================================================
# 3. Cosmos DB indexing policy tests — key hashes must be excluded
#    from cross-partition indexes.
# ===================================================================


class TestNoCrossPartitionKeyQueries:
    """Verify no cross-partition queries for key hashes remain in code."""

    def test_tenant_repo_no_cross_partition_key_query(self):
        """TenantRepository must not contain cross-partition key hash queries."""
        source = TENANT_REPO_PATH.read_text()
        # Cross-partition queries use enable_cross_partition_query=True
        # combined with key_hash in the same method.  The verify_key_hash
        # method should use partition_key (single-partition read).
        assert "find_by_api_key_hash" not in source, (
            "find_by_api_key_hash found in tenant.py — "
            "cross-partition key discovery violates SPEC-1644"
        )

    def test_team_repo_no_cross_partition_key_query(self):
        """TeamMemberRepository must not contain cross-partition key hash queries."""
        source = TEAM_REPO_PATH.read_text()
        assert "find_by_user_api_key_hash" not in source, (
            "find_by_user_api_key_hash found in team.py — "
            "cross-partition key discovery violates SPEC-1644"
        )


# ===================================================================
# 4. Frontend structural tests — login must use validate-key,
#    not lookup.
# ===================================================================


ADMIN_STANDALONE_DIR = Path(__file__).resolve().parents[2] / "admin" / "standalone"


class TestFrontendApiKeyFlow:
    """Verify frontend uses validate-key, not lookup for API key auth."""

    def test_login_component_uses_validate_key(self):
        """ApiKeyLogin must call /api/tenants/auth/validate-key, not /lookup."""
        login_path = ADMIN_STANDALONE_DIR / "login" / "ApiKeyLogin.tsx"
        if not login_path.exists():
            pytest.skip("ApiKeyLogin.tsx not found")
        source = login_path.read_text()

        # The handleLogin function must use validate-key
        assert "validate-key" in source, (
            "ApiKeyLogin.tsx must call /api/tenants/auth/validate-key"
        )

    def test_login_component_does_not_discover_tenant(self):
        """ApiKeyLogin must not call /api/tenants/lookup with just an API key."""
        login_path = ADMIN_STANDALONE_DIR / "login" / "ApiKeyLogin.tsx"
        if not login_path.exists():
            pytest.skip("ApiKeyLogin.tsx not found")
        source = login_path.read_text()

        # Find handleLogin function and check it doesn't use lookup
        match = re.search(
            r'const handleLogin.*?(?=\n  const |\n  /\*)',
            source,
            re.DOTALL,
        )
        if match:
            func_source = match.group(0)
            assert "/api/tenants/lookup" not in func_source, (
                "handleLogin still calls /api/tenants/lookup — "
                "SPEC-1644: API keys must not discover tenants"
            )

    def test_layout_uses_validate_key_for_resolution(self):
        """StandaloneLayout must use validate-key for tenant resolution."""
        layout_path = ADMIN_STANDALONE_DIR / "layouts" / "StandaloneLayout.tsx"
        if not layout_path.exists():
            pytest.skip("StandaloneLayout.tsx not found")
        source = layout_path.read_text()

        # Find the resolveTenant function
        match = re.search(
            r'async function resolveTenant.*?(?=\n    resolveTenant|\n  \})',
            source,
            re.DOTALL,
        )
        if match:
            func_source = match.group(0)
            assert "validate-key" in func_source, (
                "resolveTenant must use /api/tenants/auth/validate-key"
            )


# ===================================================================
# 5. A/B Testing removal verification
# ===================================================================


class TestABTestingRemoved:
    """Verify A/B testing UI has been completely removed."""

    def test_no_ab_testing_page_file(self):
        """ABTesting.tsx must not exist in admin/standalone/pages/."""
        ab_path = ADMIN_STANDALONE_DIR / "pages" / "ABTesting.tsx"
        assert not ab_path.exists(), (
            "admin/standalone/pages/ABTesting.tsx still exists — "
            "A/B testing UI was removed per owner directive"
        )

    def test_no_experiment_management_page(self):
        """ExperimentManagement.tsx must not exist in admin/provider/pages/."""
        exp_path = Path(__file__).resolve().parents[2] / "admin" / "provider" / "pages" / "ExperimentManagement.tsx"
        assert not exp_path.exists(), (
            "admin/provider/pages/ExperimentManagement.tsx still exists"
        )

    def test_no_ab_testing_module(self):
        """src/chat/ab_testing.py must not exist."""
        ab_path = SRC_ROOT / "chat" / "ab_testing.py"
        assert not ab_path.exists(), (
            "src/chat/ab_testing.py still exists — "
            "standalone A/B testing module was removed"
        )

    def test_no_superadmin_experiments_module(self):
        """src/multi_tenant/superadmin_api/_experiments.py must not exist."""
        exp_path = SRC_ROOT / "multi_tenant" / "superadmin_api" / "_experiments.py"
        assert not exp_path.exists(), (
            "superadmin_api/_experiments.py still exists"
        )

    def test_no_ab_testing_nav_in_standalone(self):
        """No 'A/B Testing' or 'ab-testing' references in standalone layout."""
        layout_path = ADMIN_STANDALONE_DIR / "layouts" / "StandaloneLayout.tsx"
        if not layout_path.exists():
            pytest.skip("StandaloneLayout.tsx not found")
        source = layout_path.read_text().lower()
        assert "ab-testing" not in source, "ab-testing route found in StandaloneLayout"
        assert "a/b testing" not in source, "A/B Testing label found in StandaloneLayout"

    def test_no_ab_testing_route_in_standalone_index(self):
        """No ab-testing routes in standalone index.tsx."""
        index_path = ADMIN_STANDALONE_DIR / "index.tsx"
        if not index_path.exists():
            pytest.skip("index.tsx not found")
        source = index_path.read_text().lower()
        assert "ab-testing" not in source, "ab-testing route found in standalone index"
        assert "abtesting" not in source, "ABTesting import found in standalone index"
