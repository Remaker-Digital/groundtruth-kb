"""Tests for C14: Configuration Optimistic Locking — concurrent edit prevention.

Covers:
    CL-01: Get lock status returns etag for draft config
    CL-02: Get lock status falls back to active config when no draft
    CL-03: Get lock status returns 404 when no config exists
    CL-04: Validate etag succeeds when etag matches
    CL-05: Validate etag returns 409 when etag is stale
    CL-06: Validate etag returns 404 when no config exists
    CL-07: Lock status includes version number
    CL-08: Lock status includes last_modified fields
    CL-09: Service not configured returns 503
    CL-10: CamelCase serialization on response models
    CL-11: Routes are mounted under /api/admin/config/lock
    CL-12: Auth dependency is wired on both endpoints

Total: 12 tests

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from src.multi_tenant.config_locking import (
    ConfigConflictResponse,
    ConfigLockStatus,
    ConfigSaveWithLockRequest,
    configure_config_locking,
    get_lock_status,
    validate_etag,
    router,
)


# ---------------------------------------------------------------------------
# Test data factories
# ---------------------------------------------------------------------------

TENANT_ID = "t-lock-001"
ETAG_V1 = '"00000000-0000-0000-aaaa-000000000001"'
ETAG_V2 = '"00000000-0000-0000-aaaa-000000000002"'


def _make_config_doc(
    config_state: str = "draft",
    version: int = 3,
    etag: str = ETAG_V1,
    last_modified_by: str | None = "admin@remaker.com",
    updated_at: str | None = "2026-02-18T10:00:00+00:00",
) -> dict[str, Any]:
    """Build a mock preferences Cosmos document."""
    return {
        "id": f"prefs-{TENANT_ID}",
        "tenant_id": TENANT_ID,
        "config_state": config_state,
        "version": version,
        "_etag": etag,
        "last_modified_by": last_modified_by,
        "updated_at": updated_at,
    }


DRAFT_DOC = _make_config_doc(config_state="draft", version=3, etag=ETAG_V1)
ACTIVE_DOC = _make_config_doc(config_state="active", version=2, etag=ETAG_V2)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_preferences_repo():
    """Create a mock preferences repository."""
    repo = MagicMock()
    repo.query = AsyncMock(return_value=[])
    return repo


@pytest.fixture()
def tenant_ctx():
    """Create a fake TenantContext."""
    ctx = MagicMock()
    ctx.tenant_id = TENANT_ID
    ctx.team_member_role = "admin"
    ctx.team_member_email = "admin@remaker.com"
    return ctx


@pytest.fixture(autouse=True)
def _wire_services(mock_preferences_repo):
    """Wire mock repo into config locking for every test."""
    configure_config_locking(preferences_repo=mock_preferences_repo)
    yield
    # Reset to prevent leaking between test modules
    configure_config_locking(preferences_repo=None)


# ---------------------------------------------------------------------------
# CL-01: Get lock status returns etag for draft config
# ---------------------------------------------------------------------------


class TestGetLockStatus:
    """Tests for GET /api/admin/config/lock/status."""

    @pytest.mark.asyncio
    async def test_cl01_returns_etag_for_draft(self, mock_preferences_repo, tenant_ctx):
        """CL-01: Returns etag when draft config exists."""
        mock_preferences_repo.query = AsyncMock(return_value=[DRAFT_DOC])

        result = await get_lock_status(ctx=tenant_ctx)

        assert isinstance(result, ConfigLockStatus)
        assert result.etag == ETAG_V1
        assert result.config_state == "draft"
        assert result.tenant_id == TENANT_ID

    @pytest.mark.asyncio
    async def test_cl02_falls_back_to_active(self, mock_preferences_repo, tenant_ctx):
        """CL-02: Falls back to active config when no draft exists."""
        # First query (draft) returns empty, second query (active) returns doc
        mock_preferences_repo.query = AsyncMock(
            side_effect=[[], [ACTIVE_DOC]],
        )

        result = await get_lock_status(ctx=tenant_ctx)

        assert isinstance(result, ConfigLockStatus)
        assert result.etag == ETAG_V2
        assert result.config_state == "active"
        # Verify two queries were made (draft then active)
        assert mock_preferences_repo.query.await_count == 2

    @pytest.mark.asyncio
    async def test_cl03_returns_404_no_config(self, mock_preferences_repo, tenant_ctx):
        """CL-03: Returns 404 when no configuration exists at all."""
        mock_preferences_repo.query = AsyncMock(return_value=[])

        with pytest.raises(HTTPException) as exc_info:
            await get_lock_status(ctx=tenant_ctx)
        assert exc_info.value.status_code == 404
        assert "No configuration found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_cl07_includes_version(self, mock_preferences_repo, tenant_ctx):
        """CL-07: Lock status includes the correct version number."""
        mock_preferences_repo.query = AsyncMock(return_value=[DRAFT_DOC])

        result = await get_lock_status(ctx=tenant_ctx)

        assert result.version == 3

    @pytest.mark.asyncio
    async def test_cl08_includes_last_modified(self, mock_preferences_repo, tenant_ctx):
        """CL-08: Lock status includes last_modified_by and last_modified_at."""
        mock_preferences_repo.query = AsyncMock(return_value=[DRAFT_DOC])

        result = await get_lock_status(ctx=tenant_ctx)

        assert result.last_modified_by == "admin@remaker.com"
        assert result.last_modified_at == "2026-02-18T10:00:00+00:00"

    @pytest.mark.asyncio
    async def test_cl08_null_last_modified(self, mock_preferences_repo, tenant_ctx):
        """CL-08 variant: last_modified fields are None when absent."""
        doc = _make_config_doc(last_modified_by=None, updated_at=None)
        mock_preferences_repo.query = AsyncMock(return_value=[doc])

        result = await get_lock_status(ctx=tenant_ctx)

        assert result.last_modified_by is None
        assert result.last_modified_at is None


# ---------------------------------------------------------------------------
# CL-04/05/06: Validate ETag
# ---------------------------------------------------------------------------


class TestValidateEtag:
    """Tests for POST /api/admin/config/lock/validate."""

    @pytest.mark.asyncio
    async def test_cl04_succeeds_when_matches(self, mock_preferences_repo, tenant_ctx):
        """CL-04: Returns lock status when etag matches current document."""
        mock_preferences_repo.query = AsyncMock(return_value=[DRAFT_DOC])

        result = await validate_etag(etag=ETAG_V1, ctx=tenant_ctx)

        assert isinstance(result, ConfigLockStatus)
        assert result.etag == ETAG_V1
        assert result.config_state == "draft"
        assert result.version == 3

    @pytest.mark.asyncio
    async def test_cl05_returns_409_stale(self, mock_preferences_repo, tenant_ctx):
        """CL-05: Returns 409 Conflict when etag is stale."""
        mock_preferences_repo.query = AsyncMock(return_value=[DRAFT_DOC])

        with pytest.raises(HTTPException) as exc_info:
            await validate_etag(etag="stale-etag-value", ctx=tenant_ctx)

        assert exc_info.value.status_code == 409
        assert "modified by another user" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_cl06_returns_404_no_config(self, mock_preferences_repo, tenant_ctx):
        """CL-06: Returns 404 when no configuration exists."""
        mock_preferences_repo.query = AsyncMock(return_value=[])

        with pytest.raises(HTTPException) as exc_info:
            await validate_etag(etag=ETAG_V1, ctx=tenant_ctx)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_cl04_falls_back_to_active(self, mock_preferences_repo, tenant_ctx):
        """CL-04 variant: Validation falls back to active config when no draft."""
        mock_preferences_repo.query = AsyncMock(
            side_effect=[[], [ACTIVE_DOC]],
        )

        result = await validate_etag(etag=ETAG_V2, ctx=tenant_ctx)

        assert result.etag == ETAG_V2
        assert result.config_state == "active"


# ---------------------------------------------------------------------------
# CL-09: Service not configured
# ---------------------------------------------------------------------------


class TestServiceNotConfigured:
    """Tests for 503 when config locking service is not initialised."""

    @pytest.mark.asyncio
    async def test_get_status_503(self, tenant_ctx):
        """Get lock status returns 503 when repo is None."""
        configure_config_locking(preferences_repo=None)

        with pytest.raises(HTTPException) as exc_info:
            await get_lock_status(ctx=tenant_ctx)
        assert exc_info.value.status_code == 503
        assert "not initialised" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_validate_etag_503(self, tenant_ctx):
        """Validate etag returns 503 when repo is None."""
        configure_config_locking(preferences_repo=None)

        with pytest.raises(HTTPException) as exc_info:
            await validate_etag(etag=ETAG_V1, ctx=tenant_ctx)
        assert exc_info.value.status_code == 503


# ---------------------------------------------------------------------------
# CL-10: CamelCase Serialization
# ---------------------------------------------------------------------------


class TestConfigLockingSerialization:
    """CamelCase serialization and model correctness."""

    def test_lock_status_camel_case(self):
        """ConfigLockStatus serializes field names to camelCase."""
        model = ConfigLockStatus(
            tenant_id=TENANT_ID,
            config_state="draft",
            etag=ETAG_V1,
            version=3,
            last_modified_by="admin@remaker.com",
            last_modified_at="2026-02-18T10:00:00+00:00",
        )
        data = model.model_dump(by_alias=True)

        assert "tenantId" in data
        assert "configState" in data
        assert "etag" in data
        assert "lastModifiedBy" in data
        assert "lastModifiedAt" in data
        assert data["tenantId"] == TENANT_ID
        assert data["configState"] == "draft"

    def test_conflict_response_camel_case(self):
        """ConfigConflictResponse serializes to camelCase."""
        model = ConfigConflictResponse(
            detail="Conflict",
            current_etag=ETAG_V2,
            last_modified_by="other@remaker.com",
            last_modified_at="2026-02-18T11:00:00+00:00",
        )
        data = model.model_dump(by_alias=True)

        assert "currentEtag" in data
        assert "lastModifiedBy" in data
        assert "lastModifiedAt" in data

    def test_save_request_camel_case(self):
        """ConfigSaveWithLockRequest serializes to camelCase."""
        model = ConfigSaveWithLockRequest(
            etag=ETAG_V1,
            changes={"brand_name": "Updated Brand"},
        )
        data = model.model_dump(by_alias=True)

        assert "etag" in data
        assert "changes" in data


# ---------------------------------------------------------------------------
# CL-11/12: Route and Auth wiring
# ---------------------------------------------------------------------------


class TestConfigLockingRoutes:
    """Route mounting and auth dependency verification."""

    def test_cl11_routes_mounted(self):
        """Routes are mounted under /api/admin/config/lock."""
        routes = [r.path for r in router.routes]
        assert "/api/admin/config/lock/status" in routes
        assert "/api/admin/config/lock/validate" in routes

    def test_cl12_get_status_has_auth_dependency(self):
        """get_lock_status has a TenantContext dependency (auth required)."""
        import inspect

        sig = inspect.signature(get_lock_status)
        ctx_param = sig.parameters.get("ctx")
        assert ctx_param is not None
        assert ctx_param.default is not inspect.Parameter.empty

    def test_cl12_validate_etag_has_auth_dependency(self):
        """validate_etag has a TenantContext dependency (auth required)."""
        import inspect

        sig = inspect.signature(validate_etag)
        ctx_param = sig.parameters.get("ctx")
        assert ctx_param is not None
        assert ctx_param.default is not inspect.Parameter.empty
