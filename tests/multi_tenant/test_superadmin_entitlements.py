"""Tests for superadmin entitlement CRUD and feature flag endpoints.

Validates SPEC-1816 (Entitlement Management API) and SPEC-1824 (Feature Flags).

Endpoints tested:
  GET  /api/superadmin/entitlements
  GET  /api/superadmin/entitlements/{config_key}
  PUT  /api/superadmin/entitlements/{config_key}
  GET  /api/superadmin/entitlements/diff
  GET  /api/superadmin/entitlements/history
  GET  /api/superadmin/feature-flags
  PUT  /api/superadmin/feature-flags
  GET  /api/superadmin/feature-flags/evaluate

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.superadmin_api._entitlements import (
    EntitlementDocumentResponse,
    EntitlementListResponse,
    EntitlementWriteRequest,
    EntitlementWriteResponse,
    FeatureFlagEntry,
    FeatureFlagsDocument,
    FeatureFlagsResponse,
    _ENTITLEMENT_CONFIG_TYPES,
    _resolve_config_type,
    list_entitlements,
    get_entitlement,
    put_entitlement,
    diff_entitlements,
    list_feature_flags,
    put_feature_flags,
    evaluate_feature_flag,
)
from src.multi_tenant.entitlement_service import EntitlementService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_platform_repo() -> AsyncMock:
    """Mock PlatformConfigRepository."""
    repo = AsyncMock()
    repo.get_config.return_value = None
    repo.set_config.return_value = {}
    repo.list_by_type.return_value = []
    return repo


@pytest.fixture
def mock_audit_repo() -> AsyncMock:
    """Mock AuditLogRepository."""
    repo = AsyncMock()
    repo.log_event.return_value = {}
    return repo


@pytest.fixture
def mock_tenant_ctx() -> MagicMock:
    """Mock TenantContext for SPA admin."""
    ctx = MagicMock()
    ctx.tenant_id = "__platform__"
    ctx.team_member_email = "admin@remaker.digital"
    ctx.tier = "enterprise"
    ctx.api_key_type = "PLATFORM_ADMIN"
    return ctx


@pytest.fixture
def sample_tier_config_doc() -> dict[str, Any]:
    """Sample tier_config:all_tiers document from Cosmos."""
    return {
        "id": "tier_config:all_tiers",
        "config_type": "tier_config",
        "config_key": "all_tiers",
        "value": {
            "trial": {"included_conversations": 5000, "rate_limit_rpm": 300},
            "starter": {"included_conversations": 1000, "rate_limit_rpm": 300},
            "professional": {"included_conversations": 5000, "rate_limit_rpm": 300},
            "enterprise": {"included_conversations": 20000, "rate_limit_rpm": 300},
        },
        "version": 1,
        "updated_at": "2026-03-16T00:00:00+00:00",
        "updated_by": "seed_entitlements.py",
    }


@pytest.fixture
def sample_flags_doc() -> dict[str, Any]:
    """Sample feature_flags:flags document."""
    return {
        "id": "feature_flags:flags",
        "config_type": "feature_flags",
        "config_key": "flags",
        "value": {
            "new_chat_ui": {
                "name": "new_chat_ui",
                "enabled": True,
                "scope": "global",
                "description": "New chat interface redesign",
            },
            "advanced_analytics": {
                "name": "advanced_analytics",
                "enabled": True,
                "scope": "per_tier",
                "tiers": ["professional", "enterprise"],
                "description": "Advanced analytics dashboard",
            },
            "beta_feature": {
                "name": "beta_feature",
                "enabled": True,
                "scope": "per_tenant",
                "tenant_ids": ["tenant-001", "tenant-002"],
                "description": "Beta-only feature",
            },
            "disabled_flag": {
                "name": "disabled_flag",
                "enabled": False,
                "scope": "global",
                "description": "Disabled feature",
            },
        },
        "version": 2,
        "updated_at": "2026-03-16T12:00:00+00:00",
        "updated_by": "admin@remaker.digital",
    }


# ---------------------------------------------------------------------------
# SPEC-1816: Config key resolution
# ---------------------------------------------------------------------------


class TestConfigKeyResolution:
    """SPEC-1816: Valid entitlement config keys resolve to correct config_type."""

    def test_all_tiers_resolves_to_tier_config(self):
        assert _resolve_config_type("all_tiers") == "tier_config"

    def test_pricing_resolves_to_entitlements(self):
        assert _resolve_config_type("pricing") == "entitlements"

    def test_field_gates_resolves_to_entitlements(self):
        assert _resolve_config_type("field_gates") == "entitlements"

    def test_unknown_key_raises_http_error(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            _resolve_config_type("nonexistent_key")
        assert exc_info.value.status_code == 400
        assert "Unknown entitlement config_key" in str(exc_info.value.detail)

    def test_all_known_keys_documented(self):
        """All known config keys have an entry."""
        expected_keys = {
            "all_tiers", "pricing", "pack_pricing", "sla_targets",
            "website_limits", "integration_gates", "field_gates", "global_config",
        }
        assert set(_ENTITLEMENT_CONFIG_TYPES.keys()) == expected_keys


# ---------------------------------------------------------------------------
# SPEC-1816: GET /entitlements
# ---------------------------------------------------------------------------


class TestListEntitlements:
    """SPEC-1816: List all entitlement configuration documents."""

    @pytest.mark.asyncio
    async def test_list_returns_documents(self, mock_platform_repo, sample_tier_config_doc):
        """Returns documents that exist in Cosmos."""
        mock_platform_repo.get_config.side_effect = lambda ct, ck: (
            sample_tier_config_doc if ck == "all_tiers" else None
        )

        with patch(
            "src.multi_tenant.superadmin_api._entitlements._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await list_entitlements()

        assert isinstance(result, EntitlementListResponse)
        assert result.total >= 1
        # The all_tiers doc should be present
        found = [d for d in result.documents if d.config_key == "all_tiers"]
        assert len(found) == 1
        assert found[0].version == 1

    @pytest.mark.asyncio
    async def test_list_empty_when_no_docs(self, mock_platform_repo):
        """Returns empty list when no Cosmos documents exist."""
        mock_platform_repo.get_config.return_value = None

        with patch(
            "src.multi_tenant.superadmin_api._entitlements._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await list_entitlements()

        assert result.total == 0
        assert result.documents == []


# ---------------------------------------------------------------------------
# SPEC-1816: GET /entitlements/{config_key}
# ---------------------------------------------------------------------------


class TestGetEntitlement:
    """SPEC-1816: Read a single entitlement document."""

    @pytest.mark.asyncio
    async def test_get_existing_document(self, mock_platform_repo, sample_tier_config_doc):
        """Returns the document when it exists."""
        mock_platform_repo.get_config.return_value = sample_tier_config_doc

        with patch(
            "src.multi_tenant.superadmin_api._entitlements._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await get_entitlement("all_tiers")

        assert isinstance(result, EntitlementDocumentResponse)
        assert result.config_key == "all_tiers"
        assert result.config_type == "tier_config"
        assert "trial" in result.value

    @pytest.mark.asyncio
    async def test_get_missing_document_returns_404(self, mock_platform_repo):
        """Returns 404 when document not in Cosmos."""
        mock_platform_repo.get_config.return_value = None

        with patch(
            "src.multi_tenant.superadmin_api._entitlements._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            from fastapi import HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await get_entitlement("all_tiers")
            assert exc_info.value.status_code == 404
            assert "frozen fallback" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_get_invalid_key_returns_400(self):
        """Returns 400 for unknown config keys."""
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await get_entitlement("invalid_key")
        assert exc_info.value.status_code == 400


# ---------------------------------------------------------------------------
# SPEC-1816: PUT /entitlements/{config_key}
# ---------------------------------------------------------------------------


class TestPutEntitlement:
    """SPEC-1816: Write (upsert) an entitlement document."""

    @pytest.mark.asyncio
    async def test_put_creates_new_document(self, mock_platform_repo, mock_tenant_ctx):
        """Creates a new document with version 1."""
        mock_platform_repo.get_config.return_value = None

        mock_svc = MagicMock()
        mock_svc.invalidate_cache = MagicMock()
        mock_svc.invalidate_redis = AsyncMock()

        with patch(
            "src.multi_tenant.superadmin_api._entitlements._get_platform_repo",
            return_value=mock_platform_repo,
        ), patch(
            "src.multi_tenant.entitlement_service.get_entitlement_service",
            return_value=mock_svc,
        ), patch(
            "src.multi_tenant.repositories.platform.AuditLogRepository",
        ):
            body = EntitlementWriteRequest(value={"starter": {"rpm": 300}})
            result = await put_entitlement("global_config", body, mock_tenant_ctx)

        assert isinstance(result, EntitlementWriteResponse)
        assert result.version == 1
        assert result.config_key == "global_config"
        assert result.config_type == "entitlements"
        mock_platform_repo.set_config.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_put_increments_version(
        self, mock_platform_repo, mock_tenant_ctx, sample_tier_config_doc,
    ):
        """Increments version when document already exists."""
        mock_platform_repo.get_config.return_value = sample_tier_config_doc

        mock_svc = MagicMock()
        mock_svc.invalidate_cache = MagicMock()
        mock_svc.invalidate_redis = AsyncMock()

        with patch(
            "src.multi_tenant.superadmin_api._entitlements._get_platform_repo",
            return_value=mock_platform_repo,
        ), patch(
            "src.multi_tenant.entitlement_service.get_entitlement_service",
            return_value=mock_svc,
        ), patch(
            "src.multi_tenant.repositories.platform.AuditLogRepository",
        ):
            body = EntitlementWriteRequest(value={"trial": {"rpm": 500}})
            result = await put_entitlement("all_tiers", body, mock_tenant_ctx)

        assert result.version == 2  # was 1, now 2

    @pytest.mark.asyncio
    async def test_put_invalidates_caches(self, mock_platform_repo, mock_tenant_ctx):
        """Cache invalidation is triggered on write."""
        mock_platform_repo.get_config.return_value = None

        mock_svc = MagicMock()
        mock_svc.invalidate_cache = MagicMock()
        mock_svc.invalidate_redis = AsyncMock()

        with patch(
            "src.multi_tenant.superadmin_api._entitlements._get_platform_repo",
            return_value=mock_platform_repo,
        ), patch(
            "src.multi_tenant.entitlement_service.get_entitlement_service",
            return_value=mock_svc,
        ), patch(
            "src.multi_tenant.repositories.platform.AuditLogRepository",
        ):
            body = EntitlementWriteRequest(value={"test": True})
            result = await put_entitlement("pricing", body, mock_tenant_ctx)

        assert result.cache_invalidated is True
        mock_svc.invalidate_cache.assert_called_once_with("pricing")
        mock_svc.invalidate_redis.assert_awaited_once_with("pricing")


# ---------------------------------------------------------------------------
# SPEC-1816: GET /entitlements/diff
# ---------------------------------------------------------------------------


class TestEntitlementDiff:
    """SPEC-1816: Compare live entitlements vs frozen fallback."""

    @pytest.mark.asyncio
    async def test_diff_shows_missing_docs(self, mock_platform_repo):
        """Diff reports when live documents are missing."""
        mock_platform_repo.get_config.return_value = None

        with patch(
            "src.multi_tenant.superadmin_api._entitlements._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await diff_entitlements()

        assert result.total_checked == len(_ENTITLEMENT_CONFIG_TYPES)
        # All entries should report no live doc
        for entry in result.entries:
            assert entry.has_live_doc is False
            assert len(entry.differences) >= 1
            assert "frozen fallback" in entry.differences[0].lower()

    @pytest.mark.asyncio
    async def test_diff_shows_matching_docs(
        self, mock_platform_repo, sample_tier_config_doc,
    ):
        """Diff reports matching when live doc has same keys."""
        # Return a doc that matches frozen for all_tiers
        mock_platform_repo.get_config.side_effect = lambda ct, ck: (
            sample_tier_config_doc if ck == "all_tiers" else None
        )

        with patch(
            "src.multi_tenant.superadmin_api._entitlements._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await diff_entitlements()

        all_tiers_entry = [e for e in result.entries if e.config_key == "all_tiers"]
        assert len(all_tiers_entry) == 1
        assert all_tiers_entry[0].has_live_doc is True


# ---------------------------------------------------------------------------
# SPEC-1824: Feature flag CRUD
# ---------------------------------------------------------------------------


class TestFeatureFlagsCRUD:
    """SPEC-1824: Feature flag document read/write."""

    @pytest.mark.asyncio
    async def test_list_flags_empty(self, mock_platform_repo):
        """Returns empty flags when no document exists."""
        mock_platform_repo.get_config.return_value = None

        with patch(
            "src.multi_tenant.superadmin_api._entitlements._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await list_feature_flags()

        assert isinstance(result, FeatureFlagsResponse)
        assert result.flags == {}
        assert result.version == 0

    @pytest.mark.asyncio
    async def test_list_flags_returns_entries(self, mock_platform_repo, sample_flags_doc):
        """Returns flag entries from Cosmos document."""
        mock_platform_repo.get_config.return_value = sample_flags_doc

        with patch(
            "src.multi_tenant.superadmin_api._entitlements._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await list_feature_flags()

        assert len(result.flags) == 4
        assert "new_chat_ui" in result.flags
        assert result.flags["new_chat_ui"].scope == "global"
        assert result.version == 2

    @pytest.mark.asyncio
    async def test_put_flags_creates_document(self, mock_platform_repo, mock_tenant_ctx):
        """Writing flags creates a new versioned document."""
        mock_platform_repo.get_config.return_value = None

        mock_svc = MagicMock()
        mock_svc.invalidate_cache = MagicMock()
        mock_svc.invalidate_redis = AsyncMock()

        with patch(
            "src.multi_tenant.superadmin_api._entitlements._get_platform_repo",
            return_value=mock_platform_repo,
        ), patch(
            "src.multi_tenant.entitlement_service.get_entitlement_service",
            return_value=mock_svc,
        ), patch(
            "src.multi_tenant.repositories.platform.AuditLogRepository",
        ):
            body = FeatureFlagsDocument(flags={
                "test_flag": FeatureFlagEntry(
                    name="test_flag", enabled=True, scope="global",
                ),
            })
            result = await put_feature_flags(body, mock_tenant_ctx)

        assert result.version == 1
        assert result.config_type == "feature_flags"
        mock_platform_repo.set_config.assert_awaited_once()


# ---------------------------------------------------------------------------
# SPEC-1824: Feature flag evaluation
# ---------------------------------------------------------------------------


class TestFeatureFlagEvaluation:
    """SPEC-1824: Feature flag runtime evaluation."""

    @pytest.mark.asyncio
    async def test_global_flag_enabled_for_all(self, mock_platform_repo, sample_flags_doc):
        """Global flags are enabled for any tenant."""
        mock_platform_repo.get_config.return_value = sample_flags_doc

        with patch(
            "src.multi_tenant.superadmin_api._entitlements._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await evaluate_feature_flag(
                flag_name="new_chat_ui",
                tenant_id="any-tenant",
                tier="starter",
            )

        assert result.enabled is True
        assert "global" in result.reason.lower()

    @pytest.mark.asyncio
    async def test_disabled_flag_returns_false(self, mock_platform_repo, sample_flags_doc):
        """Disabled flags return False regardless of scope."""
        mock_platform_repo.get_config.return_value = sample_flags_doc

        with patch(
            "src.multi_tenant.superadmin_api._entitlements._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await evaluate_feature_flag(
                flag_name="disabled_flag",
                tenant_id="any-tenant",
                tier="enterprise",
            )

        assert result.enabled is False
        assert "disabled" in result.reason.lower()

    @pytest.mark.asyncio
    async def test_per_tier_flag_allowed_tier(self, mock_platform_repo, sample_flags_doc):
        """Per-tier flags enabled for allowed tiers."""
        mock_platform_repo.get_config.return_value = sample_flags_doc

        with patch(
            "src.multi_tenant.superadmin_api._entitlements._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await evaluate_feature_flag(
                flag_name="advanced_analytics",
                tenant_id="any-tenant",
                tier="professional",
            )

        assert result.enabled is True

    @pytest.mark.asyncio
    async def test_per_tier_flag_denied_tier(self, mock_platform_repo, sample_flags_doc):
        """Per-tier flags disabled for non-allowed tiers."""
        mock_platform_repo.get_config.return_value = sample_flags_doc

        with patch(
            "src.multi_tenant.superadmin_api._entitlements._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await evaluate_feature_flag(
                flag_name="advanced_analytics",
                tenant_id="any-tenant",
                tier="starter",
            )

        assert result.enabled is False
        assert "not in allowed tiers" in result.reason.lower()

    @pytest.mark.asyncio
    async def test_per_tenant_flag_allowed_tenant(
        self, mock_platform_repo, sample_flags_doc,
    ):
        """Per-tenant flags enabled for listed tenants."""
        mock_platform_repo.get_config.return_value = sample_flags_doc

        with patch(
            "src.multi_tenant.superadmin_api._entitlements._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await evaluate_feature_flag(
                flag_name="beta_feature",
                tenant_id="tenant-001",
                tier="starter",
            )

        assert result.enabled is True

    @pytest.mark.asyncio
    async def test_per_tenant_flag_denied_tenant(
        self, mock_platform_repo, sample_flags_doc,
    ):
        """Per-tenant flags disabled for unlisted tenants."""
        mock_platform_repo.get_config.return_value = sample_flags_doc

        with patch(
            "src.multi_tenant.superadmin_api._entitlements._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await evaluate_feature_flag(
                flag_name="beta_feature",
                tenant_id="tenant-999",
                tier="enterprise",
            )

        assert result.enabled is False

    @pytest.mark.asyncio
    async def test_unknown_flag_returns_404(self, mock_platform_repo, sample_flags_doc):
        """Unknown flag names return 404."""
        mock_platform_repo.get_config.return_value = sample_flags_doc

        with patch(
            "src.multi_tenant.superadmin_api._entitlements._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            from fastapi import HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await evaluate_feature_flag(
                    flag_name="nonexistent",
                    tenant_id="any",
                    tier="starter",
                )
            assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# SPEC-1824: EntitlementService.is_feature_enabled()
# ---------------------------------------------------------------------------


class TestEntitlementServiceFeatureFlags:
    """SPEC-1824: Runtime feature flag evaluation via EntitlementService."""

    @pytest.mark.asyncio
    async def test_global_flag_enabled(self):
        """Global flags return True for any tenant."""
        svc = EntitlementService()
        svc._lru_set = lambda k, v: None  # suppress caching
        svc._cosmos_repo = None
        svc._redis_client = None

        # Inject flags into LRU
        from src.multi_tenant.entitlement_service import _CacheEntry
        svc._lru["feature_flags:flags"] = _CacheEntry(
            {
                "my_flag": {
                    "enabled": True,
                    "scope": "global",
                },
            },
            ttl_seconds=60,
        )

        result = await svc.is_feature_enabled("my_flag", "tenant-123", "starter")
        assert result is True

    @pytest.mark.asyncio
    async def test_disabled_flag_returns_false(self):
        """Disabled flags always return False."""
        svc = EntitlementService()
        from src.multi_tenant.entitlement_service import _CacheEntry
        svc._lru["feature_flags:flags"] = _CacheEntry(
            {
                "my_flag": {
                    "enabled": False,
                    "scope": "global",
                },
            },
            ttl_seconds=60,
        )

        result = await svc.is_feature_enabled("my_flag", "tenant-123", "starter")
        assert result is False

    @pytest.mark.asyncio
    async def test_per_tier_flag(self):
        """Per-tier flags check the tier list."""
        svc = EntitlementService()
        from src.multi_tenant.entitlement_service import _CacheEntry
        svc._lru["feature_flags:flags"] = _CacheEntry(
            {
                "pro_feature": {
                    "enabled": True,
                    "scope": "per_tier",
                    "tiers": ["professional", "enterprise"],
                },
            },
            ttl_seconds=60,
        )

        assert await svc.is_feature_enabled("pro_feature", "t1", "professional") is True
        assert await svc.is_feature_enabled("pro_feature", "t1", "starter") is False

    @pytest.mark.asyncio
    async def test_per_tenant_flag(self):
        """Per-tenant flags check the tenant_ids list."""
        svc = EntitlementService()
        from src.multi_tenant.entitlement_service import _CacheEntry
        svc._lru["feature_flags:flags"] = _CacheEntry(
            {
                "beta": {
                    "enabled": True,
                    "scope": "per_tenant",
                    "tenant_ids": ["t-001", "t-002"],
                },
            },
            ttl_seconds=60,
        )

        assert await svc.is_feature_enabled("beta", "t-001", "starter") is True
        assert await svc.is_feature_enabled("beta", "t-999", "enterprise") is False

    @pytest.mark.asyncio
    async def test_missing_flag_returns_false(self):
        """Non-existent flags return False."""
        svc = EntitlementService()
        from src.multi_tenant.entitlement_service import _CacheEntry
        svc._lru["feature_flags:flags"] = _CacheEntry({}, ttl_seconds=60)

        result = await svc.is_feature_enabled("nonexistent", "t-001", "starter")
        assert result is False

    @pytest.mark.asyncio
    async def test_no_flags_doc_returns_false(self):
        """Returns False when no flags document exists."""
        svc = EntitlementService()
        # No cache, no Cosmos, no Redis
        result = await svc.is_feature_enabled("anything", "t-001", "starter")
        assert result is False
