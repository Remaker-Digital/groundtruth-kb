"""Tests for tenant_config_api.py — Configuration API endpoint coverage.

Covers 16 specs: router prefix + 15 endpoint smoke tests verifying each handler
can be called with properly mocked factory functions and returns expected responses.

The tenant config API uses factory functions (get_config_processor,
get_activation_service) rather than module-level variables, so tests patch
those factory functions to return mocks.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ctx() -> MagicMock:
    """Build a mock TenantContext."""
    ctx = MagicMock()
    ctx.tenant_id = "test-tenant-001"
    ctx.tier = "professional"
    ctx.user_id = "user-001"
    ctx.team_member_email = "admin@test.com"
    ctx.team_member_role = None
    ctx.team_member_id = "member-001"
    ctx.auth_method = "tenant_api_key"
    ctx.shop_domain = None
    return ctx


def _mock_config_result(**overrides) -> MagicMock:
    """Build a mock config processor result."""
    result = MagicMock()
    result.tenant_id = overrides.get("tenant_id", "test-tenant-001")
    result.tier = overrides.get("tier", "professional")
    result.version = overrides.get("version", 1)
    result.config = overrides.get("config", {"brand_name": "Test Brand"})
    result.from_cache = overrides.get("from_cache", False)
    return result


def _mock_draft_state(**overrides) -> MagicMock:
    """Build a mock DraftState result from ActivationService."""
    state = MagicMock()
    state.has_pending_changes = overrides.get("has_pending_changes", False)
    state.active_version = overrides.get("active_version", 1)
    state.active_activated_at = overrides.get("active_activated_at", "2026-02-26T00:00:00Z")
    state.draft_version = overrides.get("draft_version", None)
    state.changed_fields = overrides.get("changed_fields", [])
    state.draft_config = overrides.get("draft_config", {})
    state.active_config = overrides.get("active_config", {})
    return state


def _mock_save_result(**overrides) -> MagicMock:
    """Build a mock SaveDraftResult."""
    result = MagicMock()
    result.success = overrides.get("success", True)
    result.version = overrides.get("version", 2)
    result.errors = overrides.get("errors", [])
    result.warnings = overrides.get("warnings", [])
    result.changes = overrides.get("changes", {})
    return result


def _mock_validate_result(**overrides) -> MagicMock:
    """Build a mock validation result."""
    result = MagicMock()
    result.valid = overrides.get("valid", True)
    result.errors = overrides.get("errors", [])
    result.warnings = overrides.get("warnings", [])
    result.sanitized = overrides.get("sanitized", {})
    return result


# Patch targets — source modules
_PATCH_PROCESSOR = "src.multi_tenant.tenant_config_api.get_config_processor"
_PATCH_ACTIVATION = "src.multi_tenant.tenant_config_api.get_activation_service"
_PATCH_SCHEMA = "src.multi_tenant.tenant_config_api.export_schema_for_api"


# ---------------------------------------------------------------------------
# Router prefix
# ---------------------------------------------------------------------------


class TestRouterPrefix:
    """SPEC: config router prefix is /api/config."""

    def test_router_prefix(self):
        from src.multi_tenant.tenant_config_api import router

        assert router.prefix == "/api/config"


# ---------------------------------------------------------------------------
# GET /api/config — Current resolved config
# ---------------------------------------------------------------------------


class TestGetConfig:
    """SPEC: GET '' returns the current resolved configuration."""

    @pytest.mark.asyncio
    async def test_get_active_config(self):
        from src.multi_tenant.tenant_config_api import get_config

        mock_processor = MagicMock()
        mock_processor.get_config = AsyncMock(return_value=_mock_config_result())

        with patch(_PATCH_PROCESSOR, return_value=mock_processor):
            result = await get_config(
                state=None, page_type=None, page_handle=None, ctx=_ctx(),
            )

        assert result.tenant_id == "test-tenant-001"
        assert result.state == "active"

    @pytest.mark.asyncio
    async def test_get_draft_config(self):
        from src.multi_tenant.tenant_config_api import get_config

        mock_processor = MagicMock()
        mock_processor.get_config = AsyncMock(return_value=_mock_config_result())

        mock_activation = MagicMock()
        mock_activation.get_draft_state = AsyncMock(
            return_value=_mock_draft_state(has_pending_changes=False),
        )

        with (
            patch(_PATCH_PROCESSOR, return_value=mock_processor),
            patch(_PATCH_ACTIVATION, return_value=mock_activation),
        ):
            result = await get_config(
                state="draft", page_type=None, page_handle=None, ctx=_ctx(),
            )

        # No pending draft, so returns active
        assert result.state == "active"


# ---------------------------------------------------------------------------
# PUT /api/config — Save config changes to draft
# ---------------------------------------------------------------------------


class TestUpdateConfig:
    """SPEC: PUT '' saves config changes to draft."""

    @pytest.mark.asyncio
    async def test_update_config_success(self):
        from src.multi_tenant.tenant_config_api import (
            ConfigUpdateRequest,
            update_config,
        )

        mock_activation = MagicMock()
        mock_activation.save_draft = AsyncMock(
            return_value=_mock_save_result(),
        )

        with patch(_PATCH_ACTIVATION, return_value=mock_activation):
            body = ConfigUpdateRequest(fields={"brand_name": "New Brand"})
            result = await update_config(body=body, ctx=_ctx())

        assert result.success is True
        assert result.state == "draft"


# ---------------------------------------------------------------------------
# POST /api/config/validate — Dry-run validation
# ---------------------------------------------------------------------------


class TestValidateConfig:
    """SPEC: POST /validate validates config changes without persisting."""

    @pytest.mark.asyncio
    async def test_validate_config(self):
        from src.multi_tenant.tenant_config_api import (
            ConfigValidateRequest,
            validate_config_endpoint,
        )

        mock_processor = MagicMock()
        mock_processor.validate_only = AsyncMock(
            return_value=_mock_validate_result(),
        )

        with patch(_PATCH_PROCESSOR, return_value=mock_processor):
            body = ConfigValidateRequest(fields={"brand_name": "Test"})
            result = await validate_config_endpoint(body=body, ctx=_ctx())

        assert result.valid is True


# ---------------------------------------------------------------------------
# POST /api/config/reset — Reset to tier defaults
# ---------------------------------------------------------------------------


class TestResetConfig:
    """SPEC: POST /reset creates draft from tier defaults."""

    @pytest.mark.asyncio
    async def test_reset_config(self):
        from src.multi_tenant.tenant_config_api import reset_config

        mock_activation = MagicMock()
        mock_activation.reinitialize_to_defaults = AsyncMock(
            return_value=_mock_save_result(),
        )

        with patch(_PATCH_ACTIVATION, return_value=mock_activation):
            result = await reset_config(ctx=_ctx())

        assert result.success is True
        assert result.state == "draft"


# ---------------------------------------------------------------------------
# GET /api/config/diff — Overrides vs defaults
# ---------------------------------------------------------------------------


class TestGetConfigDiff:
    """SPEC: GET /diff shows fields differing from tier defaults."""

    @pytest.mark.asyncio
    async def test_get_config_diff(self):
        from src.multi_tenant.tenant_config_api import get_config_diff

        mock_processor = MagicMock()
        mock_processor.get_config_diff = AsyncMock(return_value={
            "brand_name": {"current": "Custom", "default": "Default"},
        })

        with patch(_PATCH_PROCESSOR, return_value=mock_processor):
            result = await get_config_diff(ctx=_ctx())

        assert result.override_count == 1
        assert "brand_name" in result.overrides


# ---------------------------------------------------------------------------
# GET /api/config/schema — Field schema for UI
# ---------------------------------------------------------------------------


class TestGetConfigSchema:
    """SPEC: GET /schema returns field metadata for UI rendering."""

    @pytest.mark.asyncio
    async def test_get_config_schema(self):
        from src.multi_tenant.tenant_config_api import get_config_schema

        with patch(_PATCH_SCHEMA, return_value={
            "tier": "professional",
            "total_fields": 42,
            "steps": [{"name": "General", "fields": []}],
        }):
            result = await get_config_schema(ctx=_ctx())

        assert result.tier == "professional"
        assert result.total_fields == 42


# ---------------------------------------------------------------------------
# GET /api/config/versions — Version history
# ---------------------------------------------------------------------------


class TestListConfigVersions:
    """SPEC: GET /versions lists configuration versions."""

    @pytest.mark.asyncio
    async def test_list_versions(self):
        from src.multi_tenant.tenant_config_api import list_config_versions

        mock_processor = MagicMock()
        mock_processor.list_versions = AsyncMock(return_value=[])

        with patch(_PATCH_PROCESSOR, return_value=mock_processor):
            result = await list_config_versions(ctx=_ctx())

        assert result.tenant_id == "test-tenant-001"
        assert result.total == 0


# ---------------------------------------------------------------------------
# GET /api/config/versions/{version} — Historical version
# ---------------------------------------------------------------------------


class TestGetConfigVersion:
    """SPEC: GET /versions/{version} returns a specific historical version."""

    @pytest.mark.asyncio
    async def test_get_config_version(self):
        from src.multi_tenant.tenant_config_api import get_config_version

        mock_processor = MagicMock()
        mock_processor.get_version = AsyncMock(
            return_value=_mock_config_result(version=3),
        )

        with patch(_PATCH_PROCESSOR, return_value=mock_processor):
            result = await get_config_version(version=3, ctx=_ctx())

        assert result.version == 3

    @pytest.mark.asyncio
    async def test_get_config_version_not_found(self):
        from fastapi import HTTPException

        from src.multi_tenant.tenant_config_api import get_config_version

        mock_processor = MagicMock()
        mock_processor.get_version = AsyncMock(return_value=None)

        with patch(_PATCH_PROCESSOR, return_value=mock_processor):
            with pytest.raises(HTTPException) as exc_info:
                await get_config_version(version=999, ctx=_ctx())
            assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# Named Configurations (C3)
# ---------------------------------------------------------------------------


class TestListNamedConfigs:
    """SPEC: GET /named lists named configurations."""

    @pytest.mark.asyncio
    async def test_list_named_configs(self):
        from src.multi_tenant.tenant_config_api import list_named_configs

        mock_processor = MagicMock()
        mock_processor.list_named_configs = AsyncMock(return_value=[])

        with patch(_PATCH_PROCESSOR, return_value=mock_processor):
            result = await list_named_configs(ctx=_ctx())

        assert result.total == 0


class TestDeleteNamedConfig:
    """SPEC: DELETE /named/{name} deletes a named configuration."""

    @pytest.mark.asyncio
    async def test_delete_named_config(self):
        from src.multi_tenant.tenant_config_api import delete_named_config

        mock_processor = MagicMock()
        mock_processor.delete_named_config = AsyncMock(return_value=True)

        with patch(_PATCH_PROCESSOR, return_value=mock_processor):
            result = await delete_named_config(name="Holiday Mode", ctx=_ctx())

        assert result.success is True
        assert result.name == "Holiday Mode"

    @pytest.mark.asyncio
    async def test_delete_default_config_rejected(self):
        from fastapi import HTTPException

        from src.multi_tenant.tenant_config_api import delete_named_config

        with pytest.raises(HTTPException) as exc_info:
            await delete_named_config(name="Default", ctx=_ctx())
        assert exc_info.value.status_code == 400


# ---------------------------------------------------------------------------
# Activation Status
# ---------------------------------------------------------------------------


class TestGetActivationStatus:
    """SPEC: GET /activation-status returns lightweight activation state."""

    @pytest.mark.asyncio
    async def test_activation_status(self):
        from src.multi_tenant.tenant_config_api import get_activation_status

        mock_activation = MagicMock()
        mock_activation.get_draft_state = AsyncMock(
            return_value=_mock_draft_state(),
        )
        mock_activation._prefs_repo = MagicMock()
        mock_activation._prefs_repo.get_active = AsyncMock(return_value=None)
        mock_activation._prefs_repo.get_draft = AsyncMock(return_value=None)

        with patch(_PATCH_ACTIVATION, return_value=mock_activation):
            result = await get_activation_status(ctx=_ctx())

        assert isinstance(result.has_pending_changes, bool)


# ---------------------------------------------------------------------------
# Draft Activate
# ---------------------------------------------------------------------------


class TestActivateDraft:
    """SPEC: POST /draft/activate validates and activates the draft."""

    @pytest.mark.asyncio
    async def test_activate_draft_success(self):
        from src.multi_tenant.tenant_config_api import activate_draft

        activate_result = MagicMock()
        activate_result.success = True
        activate_result.version = 5
        activate_result.activated_at = "2026-02-27T00:00:00Z"
        activate_result.errors = []
        activate_result.warnings = []

        mock_activation = MagicMock()
        mock_activation.activate = AsyncMock(return_value=activate_result)

        with patch(_PATCH_ACTIVATION, return_value=mock_activation):
            result = await activate_draft(ctx=_ctx())

        assert result.success is True
        assert result.version == 5


# ---------------------------------------------------------------------------
# Discard Draft
# ---------------------------------------------------------------------------


class TestDiscardDraft:
    """SPEC: POST /draft/discard deletes the draft document."""

    @pytest.mark.asyncio
    async def test_discard_draft(self):
        from src.multi_tenant.tenant_config_api import discard_draft

        mock_activation = MagicMock()
        mock_activation.discard_draft = AsyncMock(return_value=True)

        with patch(_PATCH_ACTIVATION, return_value=mock_activation):
            result = await discard_draft(ctx=_ctx())

        assert result.success is True


# ---------------------------------------------------------------------------
# Restore Previous
# ---------------------------------------------------------------------------


class TestRestorePrevious:
    """SPEC: POST /restore swaps active with previous activation snapshot."""

    @pytest.mark.asyncio
    async def test_restore_previous_success(self):
        from src.multi_tenant.tenant_config_api import restore_previous

        restore_result = MagicMock()
        restore_result.success = True
        restore_result.restored_version = 4
        restore_result.restored_activated_at = "2026-02-25T00:00:00Z"

        mock_activation = MagicMock()
        mock_activation.restore_previous = AsyncMock(return_value=restore_result)

        with patch(_PATCH_ACTIVATION, return_value=mock_activation):
            result = await restore_previous(ctx=_ctx())

        assert result.success is True
        assert result.restored_version == 4
