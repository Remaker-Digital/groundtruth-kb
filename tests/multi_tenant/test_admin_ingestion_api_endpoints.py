"""Endpoint-level tests for Admin Ingestion API.

Covers 6 specs:
    1. Router prefix /api/admin/knowledge
    2. start_ingestion — patch get_ingestion_service, mock service
    3. get_ingestion_status — patch get_ingestion_service, returns None
    4. cancel_ingestion — patch get_ingestion_service, mock service
    5. list_templates — patch get_template_loader, mock loader
    6. apply_template — patch get_template_loader, mock loader

Note: The ingestion API uses lazy imports inside each endpoint function body
(``from src.multi_tenant.storefront_ingestion import get_ingestion_service``).
Therefore we must patch at the SOURCE module, not the consumer module.

(C) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.admin_ingestion_api import router


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TENANT_ID = "test-tenant-001"
NOW_ISO = "2026-02-27T12:00:00+00:00"


def _ctx(**overrides):
    ctx = MagicMock()
    ctx.tenant_id = overrides.get("tenant_id", TENANT_ID)
    ctx.tier = overrides.get("tier", "professional")
    ctx.user_id = overrides.get("user_id", "user-001")
    ctx.team_member_email = overrides.get("team_member_email", "admin@test.com")
    ctx.team_member_role = overrides.get("team_member_role", None)
    ctx.team_member_id = overrides.get("team_member_id", "member-001")
    ctx.auth_method = overrides.get("auth_method", "tenant_api_key")
    return ctx


def _job_dict(**overrides) -> dict:
    """Build a minimal ingestion job response dict."""
    job = {
        "id": "job-001",
        "tenant_id": TENANT_ID,
        "job_type": "url",
        "status": "pending",
        "progress_percent": 0,
        "articles_created": 0,
        "articles_failed": 0,
        "total_chars": 0,
        "pages_crawled": 0,
        "error_message": None,
        "created_at": NOW_ISO,
        "started_at": None,
        "completed_at": None,
    }
    job.update(overrides)
    return job


# Patch targets: source modules for lazy imports inside endpoint functions
_INGESTION_SVC_PATCH = "src.multi_tenant.storefront_ingestion.get_ingestion_service"
_TEMPLATE_LOADER_PATCH = "src.multi_tenant.template_loader.get_template_loader"


# ---------------------------------------------------------------------------
# 1. Router prefix
# ---------------------------------------------------------------------------


class TestRouterPrefix:
    """Spec: Router has prefix /api/admin/knowledge."""

    def test_router_prefix_is_correct(self):
        assert router.prefix == "/api/admin/knowledge"

    def test_router_tags(self):
        assert "knowledge-automation" in router.tags


# ---------------------------------------------------------------------------
# 2. start_ingestion — patch get_ingestion_service
# ---------------------------------------------------------------------------


class TestStartIngestionEndpoint:
    """Spec: POST /api/admin/knowledge/ingest starts ingestion job."""

    @pytest.mark.asyncio
    async def test_starts_url_ingestion(self):
        from src.multi_tenant.admin_ingestion_api import (
            StartIngestionRequest,
            start_ingestion,
        )

        mock_service = MagicMock()
        mock_service.start_ingestion = AsyncMock(return_value=_job_dict(
            id="job-url-1", job_type="url",
        ))

        body = StartIngestionRequest(
            source_type="url",
            url="https://example.com",
            max_pages=10,
        )
        ctx = _ctx()

        with patch(_INGESTION_SVC_PATCH, return_value=mock_service):
            result = await start_ingestion(body, ctx=ctx)

        assert result.id == "job-url-1"
        assert result.job_type == "url"
        assert result.status == "pending"
        mock_service.start_ingestion.assert_called_once()

    @pytest.mark.asyncio
    async def test_rejects_invalid_source_type(self):
        from fastapi import HTTPException
        from src.multi_tenant.admin_ingestion_api import (
            StartIngestionRequest,
            start_ingestion,
        )

        body = StartIngestionRequest(source_type="invalid")
        ctx = _ctx()

        with pytest.raises(HTTPException) as exc_info:
            await start_ingestion(body, ctx=ctx)
        assert exc_info.value.status_code == 400
        assert "Invalid source_type" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_rejects_url_without_url_field(self):
        from fastapi import HTTPException
        from src.multi_tenant.admin_ingestion_api import (
            StartIngestionRequest,
            start_ingestion,
        )

        body = StartIngestionRequest(source_type="url")
        ctx = _ctx()

        with pytest.raises(HTTPException) as exc_info:
            await start_ingestion(body, ctx=ctx)
        assert exc_info.value.status_code == 400
        assert "URL is required" in exc_info.value.detail


# ---------------------------------------------------------------------------
# 3. get_ingestion_status — returns None
# ---------------------------------------------------------------------------


class TestGetIngestionStatusEndpoint:
    """Spec: GET /api/admin/knowledge/ingest/status returns latest job or None."""

    @pytest.mark.asyncio
    async def test_returns_none_when_no_jobs(self):
        from src.multi_tenant.admin_ingestion_api import get_ingestion_status

        mock_service = MagicMock()
        mock_service.get_latest_job = AsyncMock(return_value=None)

        ctx = _ctx()

        with patch(_INGESTION_SVC_PATCH, return_value=mock_service):
            result = await get_ingestion_status(ctx=ctx)

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_job_when_exists(self):
        from src.multi_tenant.admin_ingestion_api import get_ingestion_status

        mock_service = MagicMock()
        mock_service.get_latest_job = AsyncMock(return_value=_job_dict(
            id="job-latest", status="completed", articles_created=15,
        ))

        ctx = _ctx()

        with patch(_INGESTION_SVC_PATCH, return_value=mock_service):
            result = await get_ingestion_status(ctx=ctx)

        assert result is not None
        assert result.id == "job-latest"
        assert result.status == "completed"
        assert result.articles_created == 15


# ---------------------------------------------------------------------------
# 4. cancel_ingestion — patch get_ingestion_service
# ---------------------------------------------------------------------------


class TestCancelIngestionEndpoint:
    """Spec: POST /api/admin/knowledge/ingest/cancel cancels running job."""

    @pytest.mark.asyncio
    async def test_cancels_running_job(self):
        from src.multi_tenant.admin_ingestion_api import cancel_ingestion

        mock_service = MagicMock()
        mock_service.get_latest_job = AsyncMock(return_value={
            "id": "job-run-1",
            "tenant_id": TENANT_ID,
            "status": "running",
        })
        mock_service.cancel_job = AsyncMock()

        ctx = _ctx()

        with patch(_INGESTION_SVC_PATCH, return_value=mock_service):
            result = await cancel_ingestion(ctx=ctx)

        assert result.status == "cancelled"
        assert result.job_id == "job-run-1"
        mock_service.cancel_job.assert_called_once_with(TENANT_ID, "job-run-1")

    @pytest.mark.asyncio
    async def test_raises_404_when_no_job(self):
        from fastapi import HTTPException
        from src.multi_tenant.admin_ingestion_api import cancel_ingestion

        mock_service = MagicMock()
        mock_service.get_latest_job = AsyncMock(return_value=None)

        ctx = _ctx()

        with patch(_INGESTION_SVC_PATCH, return_value=mock_service):
            with pytest.raises(HTTPException) as exc_info:
                await cancel_ingestion(ctx=ctx)
            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_rejects_cancel_completed_job(self):
        from fastapi import HTTPException
        from src.multi_tenant.admin_ingestion_api import cancel_ingestion

        mock_service = MagicMock()
        mock_service.get_latest_job = AsyncMock(return_value={
            "id": "job-done-1",
            "tenant_id": TENANT_ID,
            "status": "completed",
        })

        ctx = _ctx()

        with patch(_INGESTION_SVC_PATCH, return_value=mock_service):
            with pytest.raises(HTTPException) as exc_info:
                await cancel_ingestion(ctx=ctx)
            assert exc_info.value.status_code == 400
            assert "Cannot cancel" in exc_info.value.detail


# ---------------------------------------------------------------------------
# 5. list_templates — patch get_template_loader
# ---------------------------------------------------------------------------


class TestListTemplatesEndpoint:
    """Spec: GET /api/admin/knowledge/templates returns category list."""

    @pytest.mark.asyncio
    async def test_returns_empty_list(self):
        from src.multi_tenant.admin_ingestion_api import list_templates

        mock_loader = MagicMock()
        mock_loader.list_categories.return_value = []

        with patch(_TEMPLATE_LOADER_PATCH, return_value=mock_loader):
            result = await list_templates()

        assert result == []
        mock_loader.list_categories.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_template_list(self):
        from src.multi_tenant.admin_ingestion_api import list_templates

        mock_loader = MagicMock()
        mock_loader.list_categories.return_value = [
            {
                "id": "apparel_fashion",
                "name": "Apparel & Fashion",
                "description": "Clothing and accessories",
                "article_count": 15,
                "suggested_brand_voice": "trendy",
                "suggested_escalation_keywords": ["damaged", "defective"],
            },
        ]

        with patch(_TEMPLATE_LOADER_PATCH, return_value=mock_loader):
            result = await list_templates()

        assert len(result) == 1
        assert result[0].id == "apparel_fashion"
        assert result[0].name == "Apparel & Fashion"
        assert result[0].article_count == 15


# ---------------------------------------------------------------------------
# 6. apply_template — patch get_template_loader
# ---------------------------------------------------------------------------


class TestApplyTemplateEndpoint:
    """Spec: POST /api/admin/knowledge/templates/{id}/apply applies template."""

    @pytest.mark.asyncio
    async def test_applies_template_successfully(self):
        from src.multi_tenant.admin_ingestion_api import apply_template

        mock_loader = MagicMock()
        mock_loader.get_template.return_value = {
            "id": "apparel_fashion",
            "articles": [],
        }
        mock_loader.apply_template = AsyncMock(return_value={
            "articles_created": 10,
            "articles_failed": 1,
            "total_chars": 3000,
            "config_suggestions": {"brand_voice": "trendy"},
        })

        ctx = _ctx()

        with patch(_TEMPLATE_LOADER_PATCH, return_value=mock_loader):
            result = await apply_template("apparel_fashion", ctx=ctx)

        assert result.articles_created == 10
        assert result.articles_failed == 1
        assert result.total_chars == 3000
        assert result.config_suggestions == {"brand_voice": "trendy"}
        mock_loader.get_template.assert_called_once_with("apparel_fashion")
        mock_loader.apply_template.assert_called_once_with(
            TENANT_ID, "apparel_fashion",
        )

    @pytest.mark.asyncio
    async def test_raises_404_for_unknown_template(self):
        from fastapi import HTTPException
        from src.multi_tenant.admin_ingestion_api import apply_template

        mock_loader = MagicMock()
        mock_loader.get_template.return_value = None

        ctx = _ctx()

        with patch(_TEMPLATE_LOADER_PATCH, return_value=mock_loader):
            with pytest.raises(HTTPException) as exc_info:
                await apply_template("nonexistent", ctx=ctx)
            assert exc_info.value.status_code == 404
            assert "Template not found" in exc_info.value.detail
