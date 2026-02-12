"""Tenant configuration tests — schema, processor, API (TC-01 to TC-30).

Tests TC-01 through TC-30 from COMPREHENSIVE-TEST-PLAN.md (P1 pre-launch).

Validates:
    - TenantConfigSchema field definitions and validation
    - TenantConfigProcessor merge order, versioning, caching
    - Configuration API HTTP endpoints (10 routes)
    - Auth enforcement, tier gating, rollback

Work Items #63-65 (Decision #22).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.multi_tenant.cosmos_schema import TenantTier
from src.multi_tenant.tenant_config_processor import (
    ConfigReadResult,
    ConfigUpdateResult,
    ConfigValidationResult,
    TenantConfigProcessor,
    _CacheEntry,
    get_config_processor,
)
from src.multi_tenant.tenant_config_schema import (
    ConfigFieldType,
    ConfigValidationError,
    OnboardingStep,
    TierGate,
    export_schema_for_api,
    get_field_registry,
    get_fields_by_step,
    get_fields_for_tier,
    resolve_defaults,
    validate_config,
    validate_field,
)
from tests.conftest import (
    ENTERPRISE_TENANT_ID,
    PROFESSIONAL_TENANT_ID,
    STARTER_TENANT_ID,
    TEST_API_KEY_ENTERPRISE,
    TEST_API_KEY_PROFESSIONAL,
    TEST_API_KEY_STARTER,
)


# ---------------------------------------------------------------------------
# TC-01 to TC-04: Schema validation
# ---------------------------------------------------------------------------


class TestSchemaValidation:
    """Tests for tenant_config_schema validation rules."""

    def test_tc01_brand_name_required(self):
        """TC-01: brand_name is a required field."""
        result = validate_config({"brand_voice": "friendly"}, TenantTier.STARTER)

        # brand_name has a platform default, so no error
        # But if we validate just brand_name = None with required=True
        registry = get_field_registry()
        field_def = registry["brand_name"]
        assert field_def.validation.required is True

    def test_tc02_string_max_length(self):
        """TC-02: String fields enforce max_length."""
        long_name = "A" * 200  # Exceeds MAX_BRAND_NAME_LENGTH (100)

        result = validate_field("brand_name", long_name, TenantTier.STARTER)

        is_valid, error, _ = result
        assert is_valid is False
        assert "100 characters" in error

    def test_tc03_enum_validation(self):
        """TC-03: Enum fields validate against allowed_values."""
        result = validate_field("response_length", "invalid_value", TenantTier.STARTER)

        is_valid, error, _ = result
        assert is_valid is False
        assert "one of:" in error

    def test_tc04_tier_gating(self):
        """TC-04: Fields with tier gates reject lower tiers."""
        # custom_instructions is PROFESSIONAL_PLUS
        result = validate_field(
            "custom_instructions",
            "Some custom instructions",
            TenantTier.STARTER,
        )

        is_valid, error, _ = result
        assert is_valid is False
        assert "pro+" in error.lower() or "professional" in error.lower()

    def test_integer_range_validation(self):
        """Integer fields enforce min/max values."""
        # escalation_threshold is 0.0-1.0 (float), but let's test widget_offset_x (0-100)
        is_valid, error, _ = validate_field("widget_offset_x", -10, TenantTier.STARTER)
        assert is_valid is False
        assert ">=" in error

        is_valid, error, _ = validate_field("widget_offset_x", 150, TenantTier.STARTER)
        assert is_valid is False
        assert "<=" in error

    def test_string_list_validation(self):
        """String list fields validate item count and individual items."""
        # additional_languages has max_items = 10
        too_many = ["en", "es", "fr", "de", "it", "nl", "ja", "ko", "zh", "ar", "hi", "ru"]  # 12 items

        result = validate_field("additional_languages", too_many, TenantTier.STARTER)

        is_valid, error, _ = result
        assert is_valid is False
        assert "10 items" in error

    def test_hex_color_pattern(self):
        """widget_primary_color validates hex color pattern."""
        is_valid, _, sanitized = validate_field("widget_primary_color", "#ff3621", TenantTier.STARTER)
        assert is_valid is True
        assert sanitized == "#ff3621"

        is_valid, error, _ = validate_field("widget_primary_color", "not-a-color", TenantTier.STARTER)
        assert is_valid is False
        assert "format" in error.lower()


# ---------------------------------------------------------------------------
# TC-05 to TC-10: Config processor merge order
# ---------------------------------------------------------------------------


class TestConfigProcessorMerge:
    """Tests for TenantConfigProcessor inheritance and merge order."""

    def test_tc05_platform_defaults_baseline(self):
        """TC-05: Platform defaults are the base layer."""
        defaults = resolve_defaults(TenantTier.STARTER)

        assert "brand_name" in defaults
        assert defaults["brand_name"] == "My Store"  # platform_default

    def test_tc06_tier_defaults_override_platform(self):
        """TC-06: Tier defaults override platform defaults."""
        starter_defaults = resolve_defaults(TenantTier.STARTER)
        pro_defaults = resolve_defaults(TenantTier.PROFESSIONAL)

        # escalation_threshold has different tier defaults
        assert starter_defaults["escalation_threshold"] == 0.7
        assert pro_defaults["escalation_threshold"] == 0.6

    def test_tc07_tenant_overrides_tier_defaults(self):
        """TC-07: Tenant overrides are the highest priority layer."""
        processor = TenantConfigProcessor()
        processor.configure(
            prefs_repo=MagicMock(),
            audit_repo=AsyncMock(),
        )

        # Mock get_current to return a tenant override
        mock_prefs_repo = processor._prefs_repo
        mock_prefs_repo.get_current = AsyncMock(return_value={
            "version": 1,
            "brand_name": "Custom Brand",
            "escalation_threshold": 0.9,
        })

        import asyncio

        resolved, version = asyncio.run(
            processor._resolve_config(STARTER_TENANT_ID, TenantTier.STARTER)
        )

        assert resolved["brand_name"] == "Custom Brand"
        assert resolved["escalation_threshold"] == 0.9

    def test_tc08_partial_overrides_preserve_defaults(self):
        """TC-08: Tenant can override only specific fields."""
        processor = TenantConfigProcessor()
        processor.configure(
            prefs_repo=MagicMock(),
            audit_repo=AsyncMock(),
        )

        mock_prefs_repo = processor._prefs_repo
        mock_prefs_repo.get_current = AsyncMock(return_value={
            "version": 1,
            "brand_name": "Custom Brand",
            # escalation_threshold not overridden
        })

        import asyncio

        resolved, _ = asyncio.run(
            processor._resolve_config(STARTER_TENANT_ID, TenantTier.STARTER)
        )

        assert resolved["brand_name"] == "Custom Brand"
        assert resolved["escalation_threshold"] == 0.7  # tier default preserved

    def test_tc09_empty_tenant_config_returns_all_defaults(self):
        """TC-09: No tenant overrides → all defaults."""
        processor = TenantConfigProcessor()
        processor.configure(
            prefs_repo=MagicMock(),
            audit_repo=AsyncMock(),
        )

        mock_prefs_repo = processor._prefs_repo
        mock_prefs_repo.get_current = AsyncMock(return_value=None)

        import asyncio

        resolved, version = asyncio.run(
            processor._resolve_config(STARTER_TENANT_ID, TenantTier.STARTER)
        )

        assert version == 0
        assert resolved["brand_name"] == "My Store"

    def test_tc10_tier_upgrade_inherits_new_defaults(self):
        """TC-10: Tier upgrade gives access to new defaults."""
        starter_fields = get_fields_for_tier(TenantTier.STARTER)
        pro_fields = get_fields_for_tier(TenantTier.PROFESSIONAL)

        # Pro has more fields (custom_instructions is PROFESSIONAL_PLUS)
        assert "custom_instructions" not in starter_fields
        assert "custom_instructions" in pro_fields


# ---------------------------------------------------------------------------
# TC-11 to TC-18: HTTP endpoint tests
# ---------------------------------------------------------------------------


class TestConfigurationAPI:
    """HTTP-level tests for Configuration API endpoints."""

    def test_tc11_get_config_returns_resolved(self, starter_client):
        """TC-11: GET /api/config returns resolved configuration."""
        # Mock processor
        mock_result = ConfigReadResult(
            tenant_id=STARTER_TENANT_ID,
            tier="starter",
            version=1,
            config={"brand_name": "Test Brand"},
            from_cache=False,
        )

        with patch("src.multi_tenant.tenant_config_api.get_config_processor") as mock_get:
            mock_processor = MagicMock()
            mock_processor.get_config = AsyncMock(return_value=mock_result)
            mock_get.return_value = mock_processor

            resp = starter_client.get("/api/config")

        assert resp.status_code == 200
        data = resp.json()
        assert data["tenant_id"] == STARTER_TENANT_ID
        assert data["version"] == 1
        assert data["config"]["brand_name"] == "Test Brand"

    def test_tc12_put_config_updates_fields(self, starter_client):
        """TC-12: PUT /api/config saves to draft via activation service."""
        from src.multi_tenant.activation_service import DraftSaveResult

        mock_result = DraftSaveResult(
            success=True,
            version=2,
            changes={"brand_name": "New"},
            state="draft",
        )

        with patch("src.multi_tenant.tenant_config_api.get_activation_service") as mock_get:
            mock_svc = MagicMock()
            mock_svc.save_draft = AsyncMock(return_value=mock_result)
            mock_get.return_value = mock_svc

            resp = starter_client.put("/api/config", json={"fields": {"brand_name": "New"}})

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["version"] == 2

    def test_tc13_validate_endpoint_dry_run(self, starter_client):
        """TC-13: POST /api/config/validate runs dry-run validation."""
        mock_result = ConfigValidationResult(
            valid=True,
            sanitized={"brand_name": "Test"},
        )

        with patch("src.multi_tenant.tenant_config_api.get_config_processor") as mock_get:
            mock_processor = MagicMock()
            mock_processor.validate_only = AsyncMock(return_value=mock_result)
            mock_get.return_value = mock_processor

            resp = starter_client.post("/api/config/validate", json={"fields": {"brand_name": "Test"}})

        assert resp.status_code == 200
        data = resp.json()
        assert data["valid"] is True

    def test_tc14_reset_endpoint_clears_overrides(self, starter_client):
        """TC-14: POST /api/config/reset creates draft from tier defaults."""
        from src.multi_tenant.activation_service import DraftSaveResult

        mock_result = DraftSaveResult(
            success=True,
            version=3,
            changes={},
            state="draft",
        )

        with patch("src.multi_tenant.tenant_config_api.get_activation_service") as mock_get:
            mock_svc = MagicMock()
            mock_svc.reinitialize_to_defaults = AsyncMock(return_value=mock_result)
            mock_get.return_value = mock_svc

            resp = starter_client.post("/api/config/reset")

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    def test_tc15_diff_endpoint_shows_overrides(self, starter_client):
        """TC-15: GET /api/config/diff shows tenant overrides vs defaults."""
        mock_diff = {
            "brand_name": {"current": "Custom", "default": "My Store"},
        }

        with patch("src.multi_tenant.tenant_config_api.get_config_processor") as mock_get:
            mock_processor = MagicMock()
            mock_processor.get_config_diff = AsyncMock(return_value=mock_diff)
            mock_get.return_value = mock_processor

            resp = starter_client.get("/api/config/diff")

        assert resp.status_code == 200
        data = resp.json()
        assert data["override_count"] == 1
        assert "brand_name" in data["overrides"]

    def test_tc16_schema_endpoint_returns_metadata(self, starter_client):
        """TC-16: GET /api/config/schema returns field metadata."""
        resp = starter_client.get("/api/config/schema")

        assert resp.status_code == 200
        data = resp.json()
        assert data["tier"] == "starter"
        assert data["total_fields"] > 0
        assert len(data["steps"]) > 0

    def test_tc17_versions_endpoint_lists_history(self, starter_client):
        """TC-17: GET /api/config/versions lists version history."""
        from src.multi_tenant.tenant_config_processor import ConfigVersionInfo

        mock_versions = [
            ConfigVersionInfo(
                version=2,
                is_current=True,
                created_at=datetime.now(timezone.utc).isoformat(),
                field_count=5,
            ),
            ConfigVersionInfo(
                version=1,
                is_current=False,
                created_at=datetime.now(timezone.utc).isoformat(),
                field_count=3,
            ),
        ]

        with patch("src.multi_tenant.tenant_config_api.get_config_processor") as mock_get:
            mock_processor = MagicMock()
            mock_processor.list_versions = AsyncMock(return_value=mock_versions)
            mock_get.return_value = mock_processor

            resp = starter_client.get("/api/config/versions")

        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert data["versions"][0]["version"] == 2
        assert data["versions"][0]["is_current"] is True

    def test_tc18_rollback_endpoint_restores_version(self, starter_client):
        """TC-18: POST /api/config/rollback loads version as draft."""
        from src.multi_tenant.activation_service import DraftSaveResult

        mock_version_config = ConfigReadResult(
            tenant_id=STARTER_TENANT_ID,
            tier="starter",
            version=1,
            config={"brand_name": "Old Name"},
            from_cache=False,
        )
        mock_draft_result = DraftSaveResult(
            success=True,
            version=4,
            changes={"brand_name": "Old Name"},
            state="draft",
        )
        mock_current = ConfigReadResult(
            tenant_id=STARTER_TENANT_ID,
            tier="starter",
            version=3,
            config={"brand_name": "Current"},
            from_cache=False,
        )

        with (
            patch("src.multi_tenant.tenant_config_api.get_config_processor") as mock_proc_get,
            patch("src.multi_tenant.tenant_config_api.get_activation_service") as mock_svc_get,
        ):
            mock_processor = MagicMock()
            mock_processor.get_version = AsyncMock(return_value=mock_version_config)
            mock_processor.get_config = AsyncMock(return_value=mock_current)
            mock_proc_get.return_value = mock_processor

            mock_svc = MagicMock()
            mock_svc.save_draft = AsyncMock(return_value=mock_draft_result)
            mock_svc_get.return_value = mock_svc

            resp = starter_client.post("/api/config/rollback", json={"target_version": 1})

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["new_version"] == 4


# ---------------------------------------------------------------------------
# TC-19 to TC-21: Auth enforcement
# ---------------------------------------------------------------------------


class TestConfigAuthEnforcement:
    """Tests for tenant isolation and auth enforcement on config endpoints."""

    def test_tc19_unauthenticated_request_rejected(self, app_client):
        """TC-19: Unauthenticated request to /api/config → 401."""
        resp = app_client.get("/api/config")
        assert resp.status_code == 401

    def test_tc20_tenant_isolation_enforced(self, starter_client):
        """TC-20: Tenant can only see their own config."""
        # The processor derives tenant_id from TenantContext, not from query params
        # So tenant isolation is enforced at the auth layer

        with patch("src.multi_tenant.tenant_config_api.get_config_processor") as mock_get:
            mock_processor = MagicMock()

            def check_tenant_id(tenant_id, tier):
                assert tenant_id == STARTER_TENANT_ID
                return AsyncMock(return_value=ConfigReadResult(
                    tenant_id=tenant_id,
                    tier=tier.value,
                    version=1,
                    config={},
                    from_cache=False,
                ))()

            mock_processor.get_config = check_tenant_id
            mock_get.return_value = mock_processor

            resp = starter_client.get("/api/config")

        assert resp.status_code == 200

    def test_tc21_tier_gating_in_validation(self, starter_client):
        """TC-21: Starter tenant cannot set Professional+ fields."""
        from src.multi_tenant.activation_service import DraftSaveResult

        # custom_instructions is PROFESSIONAL_PLUS — save_draft returns error
        mock_result = DraftSaveResult(
            success=False,
            errors=[{
                "field": "custom_instructions",
                "message": "Field 'custom_instructions' requires pro+ tier or higher",
            }],
        )

        with patch("src.multi_tenant.tenant_config_api.get_activation_service") as mock_get:
            mock_svc = MagicMock()
            mock_svc.save_draft = AsyncMock(return_value=mock_result)
            mock_get.return_value = mock_svc

            resp = starter_client.put(
                "/api/config",
                json={"fields": {"custom_instructions": "Some custom text"}},
            )

        assert resp.status_code == 422
        data = resp.json()
        assert "errors" in data["detail"]


# ---------------------------------------------------------------------------
# TC-22 to TC-30: Config features
# ---------------------------------------------------------------------------


class TestConfigFeatures:
    """Tests for config processor features: caching, versioning, rollback."""

    def test_tc22_cache_hit_returns_cached_result(self):
        """TC-22: Cache hit returns cached config without DB query."""
        processor = TenantConfigProcessor()
        processor.configure(
            prefs_repo=MagicMock(),
            audit_repo=AsyncMock(),
        )

        # Populate cache
        resolved = {"brand_name": "Cached"}
        processor._set_cache(STARTER_TENANT_ID, resolved, version=1, tier=TenantTier.STARTER)

        import asyncio

        result = asyncio.run(processor.get_config(STARTER_TENANT_ID, TenantTier.STARTER))

        assert result.from_cache is True
        assert result.config == resolved

    def test_tc23_cache_ttl_expiry(self):
        """TC-23: Cache expires after 60 seconds."""
        processor = TenantConfigProcessor()

        # Set cache with expired timestamp
        import time

        processor._cache[STARTER_TENANT_ID] = _CacheEntry(
            resolved={"brand_name": "Old"},
            version=1,
            tier=TenantTier.STARTER,
            expires_at=time.monotonic() - 1,  # 1 second ago
        )

        cached = processor._get_cached(STARTER_TENANT_ID)
        assert cached is None

    def test_tc24_invalidate_cache_on_update(self):
        """TC-24: Cache is invalidated when config is updated."""
        processor = TenantConfigProcessor()
        processor.configure(
            prefs_repo=MagicMock(),
            audit_repo=AsyncMock(),
        )

        # Populate cache
        processor._set_cache(STARTER_TENANT_ID, {"brand_name": "Cached"}, 1, TenantTier.STARTER)

        # Mock update
        mock_prefs_repo = processor._prefs_repo
        mock_prefs_repo.get_current = AsyncMock(return_value={"version": 1, "brand_name": "Old"})
        mock_prefs_repo.create_version = AsyncMock()

        import asyncio

        asyncio.run(processor.update_config(
            STARTER_TENANT_ID,
            TenantTier.STARTER,
            {"brand_name": "New"},
        ))

        # Cache should be invalidated
        assert STARTER_TENANT_ID not in processor._cache

    def test_tc25_version_increments_on_update(self):
        """TC-25: Version number increments with each update."""
        processor = TenantConfigProcessor()
        processor.configure(
            prefs_repo=MagicMock(),
            audit_repo=AsyncMock(),
        )

        mock_prefs_repo = processor._prefs_repo
        mock_prefs_repo.get_current = AsyncMock(return_value={"version": 5, "brand_name": "Old"})
        mock_prefs_repo.create_version = AsyncMock()

        import asyncio

        result = asyncio.run(processor.update_config(
            STARTER_TENANT_ID,
            TenantTier.STARTER,
            {"brand_name": "New"},
        ))

        assert result.version == 6

    def test_tc26_no_change_returns_current_version(self):
        """TC-26: Update with no actual changes returns current version."""
        processor = TenantConfigProcessor()
        processor.configure(
            prefs_repo=MagicMock(),
            audit_repo=AsyncMock(),
        )

        mock_prefs_repo = processor._prefs_repo
        mock_prefs_repo.get_current = AsyncMock(return_value={"version": 3, "brand_name": "Same"})

        import asyncio

        result = asyncio.run(processor.update_config(
            STARTER_TENANT_ID,
            TenantTier.STARTER,
            {"brand_name": "Same"},  # No change
        ))

        assert result.success is True
        assert result.version == 3  # Version not incremented
        assert len(result.changes) == 0

    def test_tc27_rollback_creates_new_version(self):
        """TC-27: Rollback creates a new version (not in-place modification)."""
        processor = TenantConfigProcessor()
        processor.configure(
            prefs_repo=MagicMock(),
            audit_repo=AsyncMock(),
        )

        mock_prefs_repo = processor._prefs_repo
        mock_prefs_repo.get_current = AsyncMock(return_value={"version": 5})
        mock_prefs_repo.get_version = AsyncMock(return_value={"version": 2, "brand_name": "Old"})
        mock_prefs_repo.create_version = AsyncMock()

        import asyncio

        result = asyncio.run(processor.rollback(
            STARTER_TENANT_ID,
            TenantTier.STARTER,
            target_version=2,
        ))

        assert result.success is True
        assert result.from_version == 5
        assert result.to_version == 2
        assert result.new_version == 6  # New version created

    def test_tc28_rollback_to_missing_version_fails(self):
        """TC-28: Rolling back to a non-existent version fails."""
        processor = TenantConfigProcessor()
        processor.configure(
            prefs_repo=MagicMock(),
            audit_repo=AsyncMock(),
        )

        mock_prefs_repo = processor._prefs_repo
        mock_prefs_repo.get_current = AsyncMock(return_value={"version": 5})
        mock_prefs_repo.get_version = AsyncMock(return_value=None)  # Version not found

        import asyncio

        result = asyncio.run(processor.rollback(
            STARTER_TENANT_ID,
            TenantTier.STARTER,
            target_version=99,
        ))

        assert result.success is False
        assert "not found" in result.message

    def test_tc29_audit_log_on_update(self):
        """TC-29: Config update logs CONFIG_UPDATED audit event."""
        processor = TenantConfigProcessor()
        processor.configure(
            prefs_repo=MagicMock(),
            audit_repo=AsyncMock(),
        )

        mock_prefs_repo = processor._prefs_repo
        mock_prefs_repo.get_current = AsyncMock(return_value={"version": 1, "brand_name": "Old"})
        mock_prefs_repo.create_version = AsyncMock()

        mock_audit_repo = processor._audit_repo

        import asyncio

        asyncio.run(processor.update_config(
            STARTER_TENANT_ID,
            TenantTier.STARTER,
            {"brand_name": "New"},
            actor="user:test@example.com",
        ))

        # Verify audit log was called
        mock_audit_repo.log_event.assert_called_once()
        call_args = mock_audit_repo.log_event.call_args
        assert call_args[1]["tenant_id"] == STARTER_TENANT_ID
        assert call_args[1]["actor"] == "user:test@example.com"

    def test_tc30_get_fields_by_step_ordering(self):
        """TC-30: get_fields_by_step returns fields sorted by step_order."""
        fields = get_fields_by_step(OnboardingStep.BRAND_AND_TONE)

        assert len(fields) > 0

        # Verify ordering
        for i in range(1, len(fields)):
            assert fields[i].step_order >= fields[i - 1].step_order
