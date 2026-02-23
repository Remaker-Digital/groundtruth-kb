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
        mock_tenant_repo = MagicMock()
        mock_tenant_repo.read = AsyncMock(return_value={
            "id": "t1",
            "tenant_id": "t1",
            "shopify_shop_domain": "test.myshopify.com",
        })

        mock_secret_service = MagicMock()
        mock_secret_service.get_secret = AsyncMock(return_value="shpat_test_token")

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

        with (
            patch(
                "src.multi_tenant.repositories.tenant.TenantRepository",
                return_value=mock_tenant_repo,
            ),
            patch(
                "src.multi_tenant.tenant_secret_service.get_secret_service",
                return_value=mock_secret_service,
            ),
            patch(
                "src.multi_tenant.storefront_ingestion.get_ingestion_service",
                return_value=mock_service,
            ),
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

    def test_template_response_uses_camel_case(self, client):
        """Regression S79: CategoryTemplateResponse extends CamelCaseModel,
        so all field names in the JSON response must be camelCase.

        The wizard's Template interface must use camelCase to match.
        Without this, selectedTemplate.suggestedBrandVoice is undefined
        and the wizard sends empty brand_voice → activation 500.
        """
        mock_loader = MagicMock()
        mock_loader.list_categories.return_value = [
            {
                "id": "home_garden",
                "name": "Home & Garden",
                "description": "Furniture and decor",
                "article_count": 15,
                "suggested_brand_voice": "friendly and practical",
                "suggested_escalation_keywords": ["damaged", "missing parts"],
            },
        ]

        with patch(
            "src.multi_tenant.template_loader.get_template_loader",
            return_value=mock_loader,
        ):
            resp = client.get("/api/admin/knowledge/templates")

        assert resp.status_code == 200
        template = resp.json()[0]

        # All fields MUST be camelCase (CamelCaseModel serialization)
        assert "suggestedBrandVoice" in template, (
            "API must return suggestedBrandVoice (camelCase), not suggested_brand_voice"
        )
        assert template["suggestedBrandVoice"] == "friendly and practical"
        assert "suggestedEscalationKeywords" in template
        assert "articleCount" in template

        # Snake_case keys must NOT be present in the response
        assert "suggested_brand_voice" not in template, (
            "snake_case key leaked into JSON response — CamelCaseModel not applied"
        )
        assert "suggested_escalation_keywords" not in template
        assert "article_count" not in template


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


# ---------------------------------------------------------------------------
# F3: URL source_config uses correct field name
# ---------------------------------------------------------------------------


class TestUrlSourceConfigFieldName:
    """Verify URL ingestion passes 'start_url' (not 'url') in source_config (F3)."""

    def test_url_source_config_uses_start_url(self, client):
        """F3 regression: source_config must use 'start_url', not 'url'."""
        mock_service = MagicMock()
        mock_service.start_ingestion = AsyncMock(return_value={
            "id": "job-f3",
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
        # Verify the source_config dict passed to service.start_ingestion
        call_args = mock_service.start_ingestion.call_args
        source_config = call_args.kwargs.get("source_config") or call_args[1].get("source_config")
        if source_config is None:
            # Positional args: start_ingestion(tenant_id, source_type, source_config)
            source_config = call_args[0][2] if len(call_args[0]) > 2 else call_args[1]["source_config"]
        assert "start_url" in source_config, f"source_config must use 'start_url', got: {source_config}"
        assert source_config["start_url"] == "https://example.com"
        assert "url" not in source_config, "source_config must NOT have bare 'url' key"

    def test_url_source_config_includes_max_pages(self, client):
        """URL source_config should include max_pages."""
        mock_service = MagicMock()
        mock_service.start_ingestion = AsyncMock(return_value={
            "id": "job-mp",
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
        })

        with patch(
            "src.multi_tenant.storefront_ingestion.get_ingestion_service",
            return_value=mock_service,
        ):
            resp = client.post("/api/admin/knowledge/ingest", json={
                "sourceType": "url",
                "url": "https://example.com",
                "maxPages": 25,
            })

        assert resp.status_code == 201
        call_args = mock_service.start_ingestion.call_args
        source_config = call_args[0][2] if len(call_args[0]) > 2 else call_args[1].get("source_config")
        assert source_config["max_pages"] == 25


# ---------------------------------------------------------------------------
# F1/F2: Shopify source_config includes token
# ---------------------------------------------------------------------------


class TestShopifySourceConfig:
    """Verify Shopify ingestion populates shop_domain and access_token (F1/F2)."""

    def test_shopify_requires_shop_domain(self, client):
        """Shopify ingestion should fail if tenant has no shop domain."""
        mock_tenant_repo = MagicMock()
        mock_tenant_repo.read = AsyncMock(return_value={
            "id": "t1",
            "tenant_id": "t1",
            # No shopify_shop_domain
        })

        with patch(
            "src.multi_tenant.repositories.tenant.TenantRepository",
            return_value=mock_tenant_repo,
        ):
            resp = client.post("/api/admin/knowledge/ingest", json={
                "sourceType": "shopify",
            })

        assert resp.status_code == 400
        assert "shop domain" in resp.json()["detail"].lower()

    def test_shopify_requires_access_token(self, client):
        """Shopify ingestion should fail if no access token available (F1)."""
        mock_tenant_repo = MagicMock()
        mock_tenant_repo.read = AsyncMock(return_value={
            "id": "t1",
            "tenant_id": "t1",
            "shopify_shop_domain": "test.myshopify.com",
        })

        mock_secret_service = MagicMock()
        mock_secret_service.get_secret = AsyncMock(return_value=None)

        with (
            patch(
                "src.multi_tenant.repositories.tenant.TenantRepository",
                return_value=mock_tenant_repo,
            ),
            patch(
                "src.multi_tenant.tenant_secret_service.get_secret_service",
                return_value=mock_secret_service,
            ),
            patch.dict("os.environ", {"SHOPIFY_ACCESS_TOKEN": ""}, clear=False),
        ):
            resp = client.post("/api/admin/knowledge/ingest", json={
                "sourceType": "shopify",
            })

        assert resp.status_code == 400
        assert "access token" in resp.json()["detail"].lower()

    def test_shopify_uses_keyvault_token(self, client):
        """Shopify ingestion should use Key Vault token when available (F2)."""
        mock_tenant_repo = MagicMock()
        mock_tenant_repo.read = AsyncMock(return_value={
            "id": "t1",
            "tenant_id": "t1",
            "shopify_shop_domain": "test.myshopify.com",
        })

        mock_secret_service = MagicMock()
        mock_secret_service.get_secret = AsyncMock(return_value="shpat_vault_token")

        mock_service = MagicMock()
        mock_service.start_ingestion = AsyncMock(return_value={
            "id": "job-kv",
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

        with (
            patch(
                "src.multi_tenant.repositories.tenant.TenantRepository",
                return_value=mock_tenant_repo,
            ),
            patch(
                "src.multi_tenant.tenant_secret_service.get_secret_service",
                return_value=mock_secret_service,
            ),
            patch(
                "src.multi_tenant.storefront_ingestion.get_ingestion_service",
                return_value=mock_service,
            ),
        ):
            resp = client.post("/api/admin/knowledge/ingest", json={
                "sourceType": "shopify",
            })

        assert resp.status_code == 201
        # Verify source_config contains the correct token
        call_args = mock_service.start_ingestion.call_args
        source_config = call_args[0][2] if len(call_args[0]) > 2 else call_args[1].get("source_config")
        assert source_config["shop_domain"] == "test.myshopify.com"
        assert source_config["access_token"] == "shpat_vault_token"
