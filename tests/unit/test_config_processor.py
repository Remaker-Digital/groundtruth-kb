"""
Tests for TenantConfigProcessor — validation, cleansing, versioning,
caching, named configurations, rollback, and widget appearances.

Covers:
    - Config read with caching (get_config, _get_cached, _set_cache)
    - Config updates (update_config, reset_to_defaults)
    - Named configurations CRUD (save, list, activate, delete)
    - Named widget appearances CRUD
    - Versioning (list_versions, get_version, rollback)
    - Utilities (validate_only, get_resolved_preferences, invalidate_all)
    - Cache TTL behavior
    - Unconfigured-service error paths

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.cosmos_schema import TenantTier
from src.multi_tenant.config.processor import (
    TenantConfigProcessor,
    get_config_processor,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TENANT_ID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
TIER = TenantTier.PROFESSIONAL


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_prefs_repo(
    current_doc: dict | None = None,
    named_doc: dict | None = None,
    versions: list | None = None,
    version_doc: dict | None = None,
    appearance_doc: dict | None = None,
):
    """Create a mock PreferencesRepository."""
    repo = MagicMock()
    repo.get_current = AsyncMock(return_value=current_doc)
    repo.create_version = AsyncMock()
    repo.get_by_name = AsyncMock(return_value=named_doc)
    repo.list_named = AsyncMock(return_value=versions or [])
    repo.get_version = AsyncMock(return_value=version_doc)
    repo.patch = AsyncMock()
    repo.create = AsyncMock()
    repo.get_by_appearance_name = AsyncMock(return_value=appearance_doc)
    repo.list_named_appearances = AsyncMock(return_value=[])
    repo.list_versions = AsyncMock(return_value=versions or [])
    return repo


def _make_audit_repo():
    repo = MagicMock()
    repo.log_event = AsyncMock()
    return repo


def _make_configured_processor(
    current_doc: dict | None = None,
    named_doc: dict | None = None,
    versions: list | None = None,
    version_doc: dict | None = None,
    appearance_doc: dict | None = None,
):
    """Create a TenantConfigProcessor with mocked repos."""
    proc = TenantConfigProcessor()
    prefs = _make_prefs_repo(current_doc, named_doc, versions, version_doc, appearance_doc)
    audit = _make_audit_repo()
    proc.configure(prefs, audit)
    return proc, prefs, audit


# ---------------------------------------------------------------------------
# Configuration / Setup
# ---------------------------------------------------------------------------


class TestConfigure:
    """Tests for TenantConfigProcessor.configure."""

    def test_configure_sets_repos(self):
        proc = TenantConfigProcessor()
        assert proc._is_configured is False
        proc.configure(MagicMock(), MagicMock())
        assert proc._is_configured is True

    def test_unconfigured_by_default(self):
        proc = TenantConfigProcessor()
        assert proc._is_configured is False


# ---------------------------------------------------------------------------
# Cache management
# ---------------------------------------------------------------------------


class TestCacheManagement:
    """Tests for internal cache methods."""

    def test_set_and_get_cache(self):
        proc = TenantConfigProcessor()
        proc._set_cache(TENANT_ID, {"brand_name": "Test"}, 5, TIER)
        cached = proc._get_cached(TENANT_ID)
        assert cached is not None
        assert cached.version == 5
        assert cached.resolved["brand_name"] == "Test"

    def test_cache_miss(self):
        proc = TenantConfigProcessor()
        assert proc._get_cached("nonexistent") is None

    def test_cache_expiry(self):
        proc = TenantConfigProcessor()
        proc._set_cache(TENANT_ID, {"brand_name": "Test"}, 1, TIER)
        # Manually expire the entry
        proc._cache[TENANT_ID].expires_at = time.monotonic() - 1
        assert proc._get_cached(TENANT_ID) is None
        assert TENANT_ID not in proc._cache

    def test_invalidate_cache(self):
        proc = TenantConfigProcessor()
        proc._set_cache(TENANT_ID, {"brand_name": "Test"}, 1, TIER)
        proc._invalidate_cache(TENANT_ID)
        assert proc._get_cached(TENANT_ID) is None

    def test_invalidate_all(self):
        proc = TenantConfigProcessor()
        proc._set_cache("t1", {"a": 1}, 1, TIER)
        proc._set_cache("t2", {"b": 2}, 1, TIER)
        assert proc.cache_size == 2
        proc.invalidate_all()
        assert proc.cache_size == 0


# ---------------------------------------------------------------------------
# get_config
# ---------------------------------------------------------------------------


class TestGetConfig:
    """Tests for get_config."""

    @pytest.mark.asyncio
    async def test_get_config_from_db(self):
        proc, prefs, _ = _make_configured_processor(
            current_doc={"version": 3, "brand_name": "MyBrand"},
        )

        with patch(
            "src.multi_tenant.config.processor.resolve_defaults",
            return_value={"brand_name": "Default", "formality_level": "balanced"},
        ), patch(
            "src.multi_tenant.config.processor._preferences_to_config",
            return_value={"brand_name": "MyBrand"},
        ):
            result = await proc.get_config(TENANT_ID, TIER)

        assert result.tenant_id == TENANT_ID
        assert result.version == 3
        assert result.from_cache is False
        assert result.config["brand_name"] == "MyBrand"

    @pytest.mark.asyncio
    async def test_get_config_from_cache(self):
        proc, prefs, _ = _make_configured_processor()
        proc._set_cache(TENANT_ID, {"brand_name": "Cached"}, 5, TIER)

        result = await proc.get_config(TENANT_ID, TIER)
        assert result.from_cache is True
        assert result.config["brand_name"] == "Cached"
        assert result.version == 5
        # DB should not be hit
        prefs.get_current.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_get_config_unconfigured_returns_defaults(self):
        proc = TenantConfigProcessor()

        with patch(
            "src.multi_tenant.config.processor.resolve_defaults",
            return_value={"brand_name": "Default"},
        ):
            result = await proc.get_config(TENANT_ID, TIER)

        assert result.version == 0
        assert result.config["brand_name"] == "Default"


# ---------------------------------------------------------------------------
# get_config_diff
# ---------------------------------------------------------------------------


class TestGetConfigDiff:
    """Tests for get_config_diff."""

    @pytest.mark.asyncio
    async def test_returns_only_changed_fields(self):
        """get_config_diff calls _resolve_config (which calls resolve_defaults
        once + mutates the result), then calls resolve_defaults a second time.
        side_effect returns a fresh dict each call to avoid mutation aliasing."""
        proc, _, _ = _make_configured_processor(
            current_doc={"version": 1, "brand_name": "Custom"},
        )

        with patch(
            "src.multi_tenant.config.processor.resolve_defaults",
            side_effect=lambda _tier: {"brand_name": "Default", "formality_level": "balanced"},
        ), patch(
            "src.multi_tenant.config.processor._preferences_to_config",
            return_value={"brand_name": "Custom"},
        ):
            diff = await proc.get_config_diff(TENANT_ID, TIER)

        assert "brand_name" in diff
        assert diff["brand_name"]["current"] == "Custom"
        assert diff["brand_name"]["default"] == "Default"
        # formality_level should NOT be in diff (matches default)
        assert "formality_level" not in diff


# ---------------------------------------------------------------------------
# update_config
# ---------------------------------------------------------------------------


class TestUpdateConfig:
    """Tests for update_config."""

    @pytest.mark.asyncio
    async def test_validation_failure_aborts(self):
        proc, _, _ = _make_configured_processor()
        from src.multi_tenant.tenant_config_schema import ConfigValidationResult

        invalid = ConfigValidationResult(
            valid=False,
            errors=[{"field": "brand_name", "message": "too long"}],
        )
        with patch(
            "src.multi_tenant.config.processor.validate_config",
            return_value=invalid,
        ):
            result = await proc.update_config(TENANT_ID, TIER, {"brand_name": "x" * 500})

        assert result.success is False

    @pytest.mark.asyncio
    async def test_no_actual_changes_returns_success(self):
        proc, _, _ = _make_configured_processor(
            current_doc={"version": 2, "brand_name": "Same"},
        )
        from src.multi_tenant.tenant_config_schema import ConfigValidationResult

        valid = ConfigValidationResult(valid=True, sanitized={"brand_name": "Same"})
        with patch(
            "src.multi_tenant.config.processor.validate_config",
            return_value=valid,
        ), patch(
            "src.multi_tenant.config.processor.resolve_defaults",
            return_value={"brand_name": "Same"},
        ), patch(
            "src.multi_tenant.config.processor._preferences_to_config",
            return_value={"brand_name": "Same"},
        ):
            result = await proc.update_config(TENANT_ID, TIER, {"brand_name": "Same"})

        assert result.success is True
        assert result.version == 2  # unchanged
        assert result.changes == {}

    @pytest.mark.asyncio
    async def test_successful_update(self):
        proc, prefs, audit = _make_configured_processor(
            current_doc={"version": 2, "brand_name": "Old"},
        )
        from src.multi_tenant.tenant_config_schema import ConfigValidationResult

        valid = ConfigValidationResult(valid=True, sanitized={"brand_name": "New"})
        with patch(
            "src.multi_tenant.config.processor.validate_config",
            return_value=valid,
        ), patch(
            "src.multi_tenant.config.processor.resolve_defaults",
            return_value={"brand_name": "Old"},
        ), patch(
            "src.multi_tenant.config.processor._preferences_to_config",
            return_value={"brand_name": "Old"},
        ), patch(
            "src.multi_tenant.config.processor._config_to_preferences",
            return_value=MagicMock(),
        ):
            result = await proc.update_config(
                TENANT_ID, TIER, {"brand_name": "New"}, actor="user:admin",
            )

        assert result.success is True
        assert result.version == 3
        assert "brand_name" in result.changes
        prefs.create_version.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_unconfigured_rejected(self):
        proc = TenantConfigProcessor()  # NOT configured
        from src.multi_tenant.tenant_config_schema import ConfigValidationResult

        valid = ConfigValidationResult(valid=True, sanitized={"brand_name": "New"})
        with patch(
            "src.multi_tenant.config.processor.validate_config",
            return_value=valid,
        ), patch(
            "src.multi_tenant.config.processor.resolve_defaults",
            return_value={"brand_name": "Old"},
        ), patch(
            "src.multi_tenant.config.processor._preferences_to_config",
            return_value={"brand_name": "Old"},
        ), patch(
            "src.multi_tenant.config.processor._config_to_preferences",
            return_value=MagicMock(),
        ):
            result = await proc.update_config(TENANT_ID, TIER, {"brand_name": "New"})

        assert result.success is False


# ---------------------------------------------------------------------------
# reset_to_defaults
# ---------------------------------------------------------------------------


class TestResetToDefaults:
    """Tests for reset_to_defaults."""

    @pytest.mark.asyncio
    async def test_reset_creates_new_version(self):
        proc, prefs, audit = _make_configured_processor(
            current_doc={"version": 3, "brand_name": "Custom"},
        )

        with patch(
            "src.multi_tenant.config.processor.resolve_defaults",
            return_value={"brand_name": "Default"},
        ), patch(
            "src.multi_tenant.config.processor._preferences_to_config",
            return_value={"brand_name": "Custom"},
        ), patch(
            "src.multi_tenant.config.processor._config_to_preferences",
            return_value=MagicMock(),
        ):
            result = await proc.reset_to_defaults(TENANT_ID, TIER, actor="user:admin")

        assert result.success is True
        assert result.version == 4
        prefs.create_version.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_reset_unconfigured_returns_failure(self):
        proc = TenantConfigProcessor()

        with patch(
            "src.multi_tenant.config.processor.resolve_defaults",
            return_value={"brand_name": "Default"},
        ), patch(
            "src.multi_tenant.config.processor._preferences_to_config",
            return_value={},
        ):
            result = await proc.reset_to_defaults(TENANT_ID, TIER)

        assert result.success is False


# ---------------------------------------------------------------------------
# Named configurations
# ---------------------------------------------------------------------------


class TestNamedConfigurations:
    """Tests for save/list/activate/delete named configurations."""

    @pytest.mark.asyncio
    async def test_save_named_config_success(self):
        proc, prefs, audit = _make_configured_processor(
            current_doc={"version": 2, "brand_name": "Live"},
        )

        with patch(
            "src.multi_tenant.config.processor.resolve_defaults",
            return_value={"brand_name": "Default"},
        ), patch(
            "src.multi_tenant.config.processor._preferences_to_config",
            return_value={"brand_name": "Live"},
        ), patch(
            "src.multi_tenant.config.processor._config_to_preferences",
            return_value=MagicMock(),
        ):
            result = await proc.save_named_config(
                TENANT_ID, TIER, "Holiday Mode", actor="user:admin",
            )

        assert result.success is True
        assert result.version == 3
        audit.log_event.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_save_named_config_replaces_existing(self):
        proc, prefs, audit = _make_configured_processor(
            current_doc={"version": 2},
            named_doc={"id": "old-doc-id", "config_name": "Holiday Mode"},
        )

        with patch(
            "src.multi_tenant.config.processor.resolve_defaults",
            return_value={},
        ), patch(
            "src.multi_tenant.config.processor._preferences_to_config",
            return_value={},
        ), patch(
            "src.multi_tenant.config.processor._config_to_preferences",
            return_value=MagicMock(),
        ):
            result = await proc.save_named_config(TENANT_ID, TIER, "Holiday Mode")

        assert result.success is True
        # Should have patched the old doc to clear its name
        prefs.patch.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_save_named_config_unconfigured(self):
        proc = TenantConfigProcessor()
        result = await proc.save_named_config(TENANT_ID, TIER, "Test")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_list_named_configs_empty(self):
        proc, _, _ = _make_configured_processor()
        proc._prefs_repo.list_named = AsyncMock(return_value=[])
        proc._prefs_repo.get_current = AsyncMock(return_value={"version": 1})
        result = await proc.list_named_configs(TENANT_ID)
        assert result == []

    @pytest.mark.asyncio
    async def test_list_named_configs_unconfigured(self):
        proc = TenantConfigProcessor()
        result = await proc.list_named_configs(TENANT_ID)
        assert result == []

    @pytest.mark.asyncio
    async def test_activate_named_config_success(self):
        proc, prefs, audit = _make_configured_processor(
            named_doc={"id": "doc-5", "version": 5, "brand_name": "Saved"},
        )
        prefs.get_current.return_value = {"version": 7}

        with patch(
            "src.multi_tenant.config.processor.resolve_defaults",
            return_value={"brand_name": "Default"},
        ), patch(
            "src.multi_tenant.config.processor._preferences_to_config",
            return_value={"brand_name": "Saved"},
        ), patch(
            "src.multi_tenant.config.processor._config_to_preferences",
            return_value=MagicMock(),
        ):
            result = await proc.activate_named_config(
                TENANT_ID, TIER, "Holiday Mode", actor="user:admin",
            )

        assert result.success is True
        assert result.version == 8

    @pytest.mark.asyncio
    async def test_activate_named_config_not_found(self):
        proc, prefs, _ = _make_configured_processor()
        prefs.get_by_name.return_value = None
        result = await proc.activate_named_config(TENANT_ID, TIER, "Missing")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_activate_named_config_unconfigured(self):
        proc = TenantConfigProcessor()
        result = await proc.activate_named_config(TENANT_ID, TIER, "Test")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_get_named_config_values_found(self):
        proc, prefs, _ = _make_configured_processor(
            named_doc={"brand_name": "Saved"},
        )

        with patch(
            "src.multi_tenant.config.processor.resolve_defaults",
            return_value={"brand_name": "Default"},
        ), patch(
            "src.multi_tenant.config.processor._preferences_to_config",
            return_value={"brand_name": "Saved"},
        ):
            result = await proc.get_named_config_values(TENANT_ID, TIER, "My Config")

        assert result["brand_name"] == "Saved"

    @pytest.mark.asyncio
    async def test_get_named_config_values_not_found(self):
        proc, prefs, _ = _make_configured_processor()
        prefs.get_by_name.return_value = None
        result = await proc.get_named_config_values(TENANT_ID, TIER, "Missing")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_named_config_values_unconfigured(self):
        proc = TenantConfigProcessor()
        result = await proc.get_named_config_values(TENANT_ID, TIER, "Test")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_named_config_success(self):
        proc, prefs, audit = _make_configured_processor(
            named_doc={"id": "doc-5", "version": 5},
        )
        result = await proc.delete_named_config(TENANT_ID, "Holiday Mode", actor="user:admin")
        assert result is True
        prefs.patch.assert_awaited_once()
        audit.log_event.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_named_config_default_protected(self):
        proc, prefs, _ = _make_configured_processor()
        result = await proc.delete_named_config(TENANT_ID, "Default")
        assert result is False
        prefs.patch.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_delete_named_config_not_found(self):
        proc, prefs, _ = _make_configured_processor()
        prefs.get_by_name.return_value = None
        result = await proc.delete_named_config(TENANT_ID, "Missing")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_named_config_unconfigured(self):
        proc = TenantConfigProcessor()
        result = await proc.delete_named_config(TENANT_ID, "Test")
        assert result is False


# ---------------------------------------------------------------------------
# Named widget appearances
# ---------------------------------------------------------------------------


class TestNamedAppearances:
    """Tests for save/list/activate/delete named widget appearances."""

    @pytest.mark.asyncio
    async def test_save_named_appearance_success(self):
        proc, prefs, audit = _make_configured_processor(
            current_doc={"version": 2},
        )

        with patch(
            "src.multi_tenant.config.processor.resolve_defaults",
            return_value={"widget_primary_color": "#ff0000"},
        ), patch(
            "src.multi_tenant.config.processor._preferences_to_config",
            return_value={"widget_primary_color": "#ff0000"},
        ), patch(
            "src.multi_tenant.config.processor._WIDGET_APPEARANCE_FIELDS",
            {"widget_primary_color"},
        ):
            result = await proc.save_named_appearance(TENANT_ID, TIER, "Dark Theme")

        assert result.success is True

    @pytest.mark.asyncio
    async def test_save_named_appearance_unconfigured(self):
        proc = TenantConfigProcessor()
        result = await proc.save_named_appearance(TENANT_ID, TIER, "Dark")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_get_named_appearance_values(self):
        proc, prefs, _ = _make_configured_processor(
            appearance_doc={"widget_primary_color": "#ff0000"},
        )

        with patch(
            "src.multi_tenant.config.processor.resolve_defaults",
            return_value={},
        ), patch(
            "src.multi_tenant.config.processor._WIDGET_APPEARANCE_FIELDS",
            {"widget_primary_color"},
        ):
            result = await proc.get_named_appearance_values(TENANT_ID, TIER, "Dark")

        assert result == {"widget_primary_color": "#ff0000"}

    @pytest.mark.asyncio
    async def test_get_named_appearance_not_found(self):
        proc, prefs, _ = _make_configured_processor()
        prefs.get_by_appearance_name.return_value = None
        result = await proc.get_named_appearance_values(TENANT_ID, TIER, "Missing")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_named_appearance_unconfigured(self):
        proc = TenantConfigProcessor()
        result = await proc.get_named_appearance_values(TENANT_ID, TIER, "Test")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_named_appearances_unconfigured(self):
        proc = TenantConfigProcessor()
        result = await proc.list_named_appearances(TENANT_ID)
        assert result == []

    @pytest.mark.asyncio
    async def test_delete_named_appearance_default_protected(self):
        proc, _, _ = _make_configured_processor()
        result = await proc.delete_named_appearance(TENANT_ID, "Default")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_named_appearance_not_found(self):
        proc, prefs, _ = _make_configured_processor()
        prefs.get_by_appearance_name.return_value = None
        result = await proc.delete_named_appearance(TENANT_ID, "Missing")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_named_appearance_success(self):
        proc, prefs, audit = _make_configured_processor(
            appearance_doc={"id": "doc-5", "version": 5},
        )
        result = await proc.delete_named_appearance(TENANT_ID, "Dark Theme", actor="user:admin")
        assert result is True
        prefs.patch.assert_awaited_once()
        audit.log_event.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_named_appearance_unconfigured(self):
        proc = TenantConfigProcessor()
        result = await proc.delete_named_appearance(TENANT_ID, "Test")
        assert result is False

    @pytest.mark.asyncio
    async def test_activate_named_appearance_unconfigured(self):
        proc = TenantConfigProcessor()
        result = await proc.activate_named_appearance(TENANT_ID, TIER, "Test")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_activate_named_appearance_not_found(self):
        proc, prefs, _ = _make_configured_processor()
        prefs.get_by_appearance_name.return_value = None
        result = await proc.activate_named_appearance(TENANT_ID, TIER, "Missing")
        assert result.success is False


# ---------------------------------------------------------------------------
# Versioning & Rollback
# ---------------------------------------------------------------------------


class TestVersioning:
    """Tests for list_versions, get_version, rollback."""

    @pytest.mark.asyncio
    async def test_list_versions_unconfigured(self):
        proc = TenantConfigProcessor()
        result = await proc.list_versions(TENANT_ID)
        assert result == []

    @pytest.mark.asyncio
    async def test_list_versions_returns_summaries(self):
        proc, prefs, _ = _make_configured_processor(
            versions=[
                {"version": 2, "is_current": True, "created_at": "2026-01-01T00:00:00Z"},
                {"version": 1, "is_current": False, "created_at": "2025-12-01T00:00:00Z"},
            ],
        )
        result = await proc.list_versions(TENANT_ID)
        assert len(result) == 2
        assert result[0].version == 2
        assert result[0].is_current is True

    @pytest.mark.asyncio
    async def test_get_version_unconfigured(self):
        proc = TenantConfigProcessor()
        result = await proc.get_version(TENANT_ID, TIER, 3)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_version_not_found(self):
        proc, prefs, _ = _make_configured_processor()
        prefs.get_version.return_value = None
        result = await proc.get_version(TENANT_ID, TIER, 99)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_version_found(self):
        proc, prefs, _ = _make_configured_processor(
            version_doc={"version": 3, "brand_name": "V3"},
        )

        with patch(
            "src.multi_tenant.config.processor.resolve_defaults",
            return_value={"brand_name": "Default"},
        ), patch(
            "src.multi_tenant.config.processor._preferences_to_config",
            return_value={"brand_name": "V3"},
        ):
            result = await proc.get_version(TENANT_ID, TIER, 3)

        assert result is not None
        assert result.version == 3
        assert result.config["brand_name"] == "V3"

    @pytest.mark.asyncio
    async def test_rollback_unconfigured(self):
        proc = TenantConfigProcessor()
        result = await proc.rollback(TENANT_ID, TIER, target_version=1)
        assert result.success is False

    @pytest.mark.asyncio
    async def test_rollback_target_not_found(self):
        proc, prefs, _ = _make_configured_processor()
        prefs.get_version.return_value = None
        result = await proc.rollback(TENANT_ID, TIER, target_version=99)
        assert result.success is False
        assert "not found" in result.message

    @pytest.mark.asyncio
    async def test_rollback_same_version(self):
        proc, prefs, _ = _make_configured_processor()
        prefs.get_version.return_value = {"version": 5}
        prefs.get_current.return_value = {"version": 5}
        result = await proc.rollback(TENANT_ID, TIER, target_version=5)
        assert result.success is True
        assert "Already at" in result.message

    @pytest.mark.asyncio
    async def test_rollback_creates_new_version(self):
        proc, prefs, audit = _make_configured_processor()
        prefs.get_version.return_value = {"version": 2, "brand_name": "V2"}
        prefs.get_current.return_value = {"version": 5}

        with patch(
            "src.multi_tenant.config.processor.resolve_defaults",
            return_value={"brand_name": "Default"},
        ), patch(
            "src.multi_tenant.config.processor._preferences_to_config",
            return_value={"brand_name": "V2"},
        ), patch(
            "src.multi_tenant.config.processor._config_to_preferences",
            return_value=MagicMock(),
        ):
            result = await proc.rollback(
                TENANT_ID, TIER, target_version=2, actor="user:admin",
            )

        assert result.success is True
        assert result.from_version == 5
        assert result.to_version == 2
        assert result.new_version == 6
        prefs.create_version.assert_awaited_once()
        audit.log_event.assert_awaited_once()


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


class TestUtilities:
    """Tests for validate_only and get_resolved_preferences."""

    @pytest.mark.asyncio
    async def test_validate_only(self):
        proc = TenantConfigProcessor()
        from src.multi_tenant.tenant_config_schema import ConfigValidationResult

        mock_result = ConfigValidationResult(valid=True, sanitized={"brand_name": "OK"})
        with patch(
            "src.multi_tenant.config.processor.validate_config",
            return_value=mock_result,
        ):
            result = await proc.validate_only(TIER, {"brand_name": "OK"})
        assert result.valid is True

    def test_get_resolved_preferences_cached(self):
        proc = TenantConfigProcessor()
        proc._set_cache(TENANT_ID, {"brand_name": "Test"}, 5, TIER)

        with patch(
            "src.multi_tenant.config.processor._config_to_preferences",
            return_value=MagicMock(brand_name="Test"),
        ) as mock_c2p:
            result = proc.get_resolved_preferences(TENANT_ID)
            assert result is not None
            mock_c2p.assert_called_once()

    def test_get_resolved_preferences_not_cached(self):
        proc = TenantConfigProcessor()
        result = proc.get_resolved_preferences(TENANT_ID)
        assert result is None


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------


class TestGetConfigProcessor:
    """Tests for get_config_processor singleton."""

    def test_returns_instance(self):
        import src.multi_tenant.config.processor as mod
        old = mod._processor
        try:
            mod._processor = None
            proc = get_config_processor()
            assert isinstance(proc, TenantConfigProcessor)
        finally:
            mod._processor = old

    def test_returns_same_instance(self):
        import src.multi_tenant.config.processor as mod
        old = mod._processor
        try:
            mod._processor = None
            a = get_config_processor()
            b = get_config_processor()
            assert a is b
        finally:
            mod._processor = old
