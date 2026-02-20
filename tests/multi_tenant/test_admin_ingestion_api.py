"""Tests for KA-2: Admin Ingestion API endpoints.

Tests REST endpoints for storefront ingestion job management and
category template application.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from src.multi_tenant.admin_ingestion_api import (
    router,
    StartIngestionRequest,
    IngestionJobResponse,
    CategoryTemplateResponse,
    TemplateApplyResponse,
)


# ---------------------------------------------------------------------------
# Test app setup
# ---------------------------------------------------------------------------


def _make_test_app():
    """Create a minimal FastAPI app with the ingestion router."""
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)
    return app


def _make_tenant_context(tenant_id: str = "t1"):
    """Create a mock TenantContext."""
    from types import SimpleNamespace
    return SimpleNamespace(tenant_id=tenant_id, tier="starter")


@pytest.fixture
def client():
    """Test client with overridden auth dependency."""
    from src.multi_tenant.middleware import get_tenant_context

    app = _make_test_app()
    app.dependency_overrides[get_tenant_context] = lambda: _make_tenant_context()
    return TestClient(app)


# ---------------------------------------------------------------------------
# POST /api/admin/knowledge/ingest
# ---------------------------------------------------------------------------


class TestStartIngestion:
    """Test the start ingestion endpoint."""

    def test_start_url_ingestion(self, client):
        mock_service = MagicMock()
        mock_service.start_ingestion = AsyncMock(return_value={
            "id": "job-1",
            "tenant_id": "t1",
            "job_type": "url",
            "status": "pending",
            "progress_percent": 0,
            "articles_created": 0,
            "articles_failed": 0,
            "total_chars": 0,
            "pages_crawled": 0,
            "error_message": None,
            "created_at": "2026-02-20T00:00:00Z",
            "started_at": None,
            "completed_at": None,
        })

        with patch(
            "src.multi_tenant.storefront_ingestion.get_ingestion_service",
            return_value=mock_service,
        ):
            resp = client.post("/api/admin/knowledge/ingest", json={
                "sourceType": "url",
                "url": "https://example.com",
                "maxPages": 10,
            })

        assert resp.status_code == 201
        data = resp.json()
        assert data["id"] == "job-1"
        assert data["jobType"] == "url"

    def test_start_shopify_ingestion(self, client):
        mock_service = MagicMock()
        mock_service.start_ingestion = AsyncMock(return_value={
            "id": "job-2",
            "tenant_id": "t1",
            "job_type": "shopify",
            "status": "pending",
            "progress_percent": 0,
            "articles_created": 0,
            "articles_failed": 0,
            "total_chars": 0,
            "pages_crawled": 0,
            "error_message": None,
            "created_at": "2026-02-20T00:00:00Z",
        })

        with patch(
            "src.multi_tenant.storefront_ingestion.get_ingestion_service",
            return_value=mock_service,
        ):
            resp = client.post("/api/admin/knowledge/ingest", json={
                "sourceType": "shopify",
            })

        assert resp.status_code == 201

    def test_start_template_ingestion(self, client):
        mock_service = MagicMock()
        mock_service.start_ingestion = AsyncMock(return_value={
            "id": "job-3",
            "tenant_id": "t1",
            "job_type": "category_template",
            "status": "pending",
            "progress_percent": 0,
            "articles_created": 0,
            "articles_failed": 0,
            "total_chars": 0,
            "pages_crawled": 0,
            "error_message": None,
            "created_at": "2026-02-20T00:00:00Z",
        })

        with patch(
            "src.multi_tenant.storefront_ingestion.get_ingestion_service",
            return_value=mock_service,
        ):
            resp = client.post("/api/admin/knowledge/ingest", json={
                "sourceType": "category_template",
                "categoryId": "apparel_fashion",
            })

        assert resp.status_code == 201

    def test_rejects_invalid_source_type(self, client):
        resp = client.post("/api/admin/knowledge/ingest", json={
            "sourceType": "invalid",
        })
        assert resp.status_code == 400
        assert "Invalid source_type" in resp.json()["detail"]

    def test_rejects_url_without_url_field(self, client):
        resp = client.post("/api/admin/knowledge/ingest", json={
            "sourceType": "url",
        })
        assert resp.status_code == 400
        assert "URL is required" in resp.json()["detail"]

    def test_rejects_template_without_category_id(self, client):
        resp = client.post("/api/admin/knowledge/ingest", json={
            "sourceType": "category_template",
        })
        assert resp.status_code == 400
        assert "category_id is required" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# GET /api/admin/knowledge/ingest/status
# ---------------------------------------------------------------------------


class TestGetIngestionStatus:
    """Test the get ingestion status endpoint."""

    def test_returns_latest_job(self, client):
        mock_service = MagicMock()
        mock_service.get_latest_job = AsyncMock(return_value={
            "id": "job-1",
            "tenant_id": "t1",
            "job_type": "url",
            "status": "completed",
            "progress_percent": 100,
            "articles_created": 15,
            "articles_failed": 0,
            "total_chars": 5000,
            "pages_crawled": 3,
            "error_message": None,
            "created_at": "2026-02-20T00:00:00Z",
            "started_at": "2026-02-20T00:01:00Z",
            "completed_at": "2026-02-20T00:05:00Z",
        })

        with patch(
            "src.multi_tenant.storefront_ingestion.get_ingestion_service",
            return_value=mock_service,
        ):
            resp = client.get("/api/admin/knowledge/ingest/status")

        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "job-1"
        assert data["articlesCreated"] == 15

    def test_returns_null_when_no_jobs(self, client):
        mock_service = MagicMock()
        mock_service.get_latest_job = AsyncMock(return_value=None)

        with patch(
            "src.multi_tenant.storefront_ingestion.get_ingestion_service",
            return_value=mock_service,
        ):
            resp = client.get("/api/admin/knowledge/ingest/status")

        assert resp.status_code == 200
        assert resp.json() is None


# ---------------------------------------------------------------------------
# POST /api/admin/knowledge/ingest/cancel
# ---------------------------------------------------------------------------


class TestCancelIngestion:
    """Test the cancel ingestion endpoint."""

    def test_cancels_running_job(self, client):
        mock_service = MagicMock()
        mock_service.get_latest_job = AsyncMock(return_value={
            "id": "job-1",
            "tenant_id": "t1",
            "status": "running",
        })
        mock_service.cancel_job = AsyncMock()

        with patch(
            "src.multi_tenant.storefront_ingestion.get_ingestion_service",
            return_value=mock_service,
        ):
            resp = client.post("/api/admin/knowledge/ingest/cancel")

        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled"
        mock_service.cancel_job.assert_called_once_with("t1", "job-1")

    def test_cancels_pending_job(self, client):
        mock_service = MagicMock()
        mock_service.get_latest_job = AsyncMock(return_value={
            "id": "job-1",
            "tenant_id": "t1",
            "status": "pending",
        })
        mock_service.cancel_job = AsyncMock()

        with patch(
            "src.multi_tenant.storefront_ingestion.get_ingestion_service",
            return_value=mock_service,
        ):
            resp = client.post("/api/admin/knowledge/ingest/cancel")

        assert resp.status_code == 200

    def test_rejects_cancel_completed_job(self, client):
        mock_service = MagicMock()
        mock_service.get_latest_job = AsyncMock(return_value={
            "id": "job-1",
            "tenant_id": "t1",
            "status": "completed",
        })

        with patch(
            "src.multi_tenant.storefront_ingestion.get_ingestion_service",
            return_value=mock_service,
        ):
            resp = client.post("/api/admin/knowledge/ingest/cancel")

        assert resp.status_code == 400
        assert "Cannot cancel" in resp.json()["detail"]

    def test_rejects_cancel_when_no_job(self, client):
        mock_service = MagicMock()
        mock_service.get_latest_job = AsyncMock(return_value=None)

        with patch(
            "src.multi_tenant.storefront_ingestion.get_ingestion_service",
            return_value=mock_service,
        ):
            resp = client.post("/api/admin/knowledge/ingest/cancel")

        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/admin/knowledge/templates
# ---------------------------------------------------------------------------


class TestListTemplates:
    """Test the list templates endpoint."""

    def test_returns_template_list(self, client):
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

        with patch(
            "src.multi_tenant.template_loader.get_template_loader",
            return_value=mock_loader,
        ):
            resp = client.get("/api/admin/knowledge/templates")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["id"] == "apparel_fashion"
        assert data[0]["articleCount"] == 15


# ---------------------------------------------------------------------------
# POST /api/admin/knowledge/templates/{category_id}/apply
# ---------------------------------------------------------------------------


class TestApplyTemplate:
    """Test the apply template endpoint."""

    def test_applies_template_successfully(self, client):
        mock_loader = MagicMock()
        mock_loader.get_template.return_value = {"id": "apparel_fashion", "articles": []}
        mock_loader.apply_template = AsyncMock(return_value={
            "articles_created": 15,
            "articles_failed": 0,
            "total_chars": 5000,
            "entry_ids": [],
            "config_suggestions": {"brand_voice": "trendy"},
        })

        with patch(
            "src.multi_tenant.template_loader.get_template_loader",
            return_value=mock_loader,
        ):
            resp = client.post("/api/admin/knowledge/templates/apparel_fashion/apply")

        assert resp.status_code == 201
        data = resp.json()
        assert data["articlesCreated"] == 15
        assert data["configSuggestions"]["brand_voice"] == "trendy"

    def test_rejects_unknown_template(self, client):
        mock_loader = MagicMock()
        mock_loader.get_template.return_value = None

        with patch(
            "src.multi_tenant.template_loader.get_template_loader",
            return_value=mock_loader,
        ):
            resp = client.post("/api/admin/knowledge/templates/nonexistent/apply")

        assert resp.status_code == 404
        assert "Template not found" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# Model validation
# ---------------------------------------------------------------------------


class TestRequestModels:
    """Test request model validation."""

    def test_start_request_defaults(self):
        req = StartIngestionRequest(source_type="shopify")
        assert req.max_pages == 50
        assert req.url is None
        assert req.category_id is None

    def test_start_request_max_pages_bounded(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            StartIngestionRequest(source_type="url", max_pages=200)

    def test_ingestion_response_camel_case(self):
        resp = IngestionJobResponse(
            id="j1",
            tenant_id="t1",
            job_type="url",
            status="pending",
            created_at="2026-02-20T00:00:00Z",
        )
        data = resp.model_dump(by_alias=True)
        assert "jobType" in data
        assert "tenantId" in data
        assert "progressPercent" in data
