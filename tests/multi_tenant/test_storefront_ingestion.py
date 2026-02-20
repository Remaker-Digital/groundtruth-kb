"""Tests for KA-1: Storefront Ingestion Service.

Verifies:
- IngestionJobDocument schema, enums, and field defaults
- IngestionJobRepository CRUD operations
- StorefrontIngestionService job lifecycle (start, process, cancel)
- Shopify product-to-KB conversion (product, collection, policy)
- URL crawl ingestion path
- Background processor orphan recovery
- Error handling and failure states
- Progress tracking and result merging

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.cosmos_schema import (
    COLLECTION_INGESTION_JOBS,
    IngestionJobDocument,
    IngestionJobStatus,
    IngestionJobType,
)
from src.multi_tenant.storefront_ingestion import (
    MIN_CONTENT_LENGTH,
    PRODUCTS_QUERY,
    COLLECTIONS_QUERY,
    SHOP_POLICIES_QUERY,
    SHOPIFY_MAX_PRODUCTS,
    StorefrontIngestionService,
    IngestionJobRepository,
    get_ingestion_service,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_job(**overrides) -> IngestionJobDocument:
    """Create a minimal IngestionJobDocument with overrides."""
    defaults = {
        "id": str(uuid.uuid4()),
        "tenant_id": "test-tenant",
        "job_type": IngestionJobType.URL.value,
        "status": IngestionJobStatus.PENDING.value,
        "source_config": {"start_url": "https://example.com", "max_pages": 5},
        "created_at": _now_iso(),
    }
    defaults.update(overrides)
    return IngestionJobDocument(**defaults)


def _make_shopify_product(
    title: str = "Premium Widget",
    description: str | None = None,
    product_type: str = "Gadgets",
    vendor: str = "WidgetCo",
    tags: list[str] | None = None,
    handle: str = "premium-widget",
    min_price: str = "29.99",
    max_price: str = "49.99",
    image_url: str | None = "https://cdn.shopify.com/widget.jpg",
    sku: str | None = "WDG-001",
) -> dict[str, Any]:
    """Build a Shopify product GraphQL node for testing."""
    if description is None:
        description = "A premium widget for all your widgeting needs. " * 5  # >100 chars
    if tags is None:
        tags = ["gadget", "premium"]

    product: dict[str, Any] = {
        "id": "gid://shopify/Product/12345",
        "title": title,
        "description": description,
        "descriptionHtml": f"<p>{description}</p>",
        "productType": product_type,
        "vendor": vendor,
        "tags": tags,
        "handle": handle,
        "status": "ACTIVE",
        "priceRangeV2": {
            "minVariantPrice": {"amount": min_price, "currencyCode": "USD"},
            "maxVariantPrice": {"amount": max_price, "currencyCode": "USD"},
        },
        "images": {"edges": []},
        "variants": {"edges": []},
    }

    if image_url:
        product["images"] = {
            "edges": [{"node": {"url": image_url, "altText": title}}],
        }
    if sku:
        product["variants"] = {
            "edges": [{"node": {"sku": sku}}],
        }
    return product


# ---------------------------------------------------------------------------
# IngestionJobDocument schema tests
# ---------------------------------------------------------------------------

class TestIngestionJobDocument:
    """Test the IngestionJobDocument Pydantic model."""

    def test_creates_with_required_fields(self):
        job = _make_job()
        assert job.status == IngestionJobStatus.PENDING.value
        assert job.progress_percent == 0
        assert job.articles_created == 0

    def test_default_status_is_pending(self):
        job = _make_job()
        assert job.status == "pending"

    def test_default_progress_is_zero(self):
        job = _make_job()
        assert job.progress_percent == 0
        assert job.articles_created == 0
        assert job.articles_failed == 0
        assert job.total_chars == 0

    def test_entry_ids_default_empty(self):
        job = _make_job()
        assert job.entry_ids == []

    def test_all_job_types_valid(self):
        for jt in IngestionJobType:
            job = _make_job(job_type=jt.value)
            assert job.job_type == jt.value

    def test_all_statuses_valid(self):
        for st in IngestionJobStatus:
            job = _make_job(status=st.value)
            assert job.status == st.value

    def test_source_config_accepts_shopify_config(self):
        config = {"shop_domain": "test.myshopify.com", "access_token": "shpat_test"}
        job = _make_job(job_type="shopify", source_config=config)
        assert job.source_config["shop_domain"] == "test.myshopify.com"

    def test_source_config_accepts_url_config(self):
        config = {"start_url": "https://example.com", "max_pages": 10, "entry_type": "article"}
        job = _make_job(job_type="url", source_config=config)
        assert job.source_config["start_url"] == "https://example.com"

    def test_source_config_accepts_template_config(self):
        config = {"category_id": "apparel_fashion", "merge_mode": "append"}
        job = _make_job(job_type="category_template", source_config=config)
        assert job.source_config["category_id"] == "apparel_fashion"

    def test_timestamps_optional_except_created_at(self):
        job = _make_job()
        assert job.created_at is not None
        assert job.started_at is None
        assert job.completed_at is None

    def test_error_message_optional(self):
        job = _make_job()
        assert job.error_message is None

    def test_ttl_set(self):
        job = _make_job()
        assert job.ttl > 0  # 30 days in seconds


# ---------------------------------------------------------------------------
# IngestionJobRepository tests
# ---------------------------------------------------------------------------

class TestIngestionJobRepository:
    """Test IngestionJobRepository methods with mocked TenantScopedRepository."""

    @pytest.fixture(autouse=True)
    def _setup_repo(self):
        """Create a repository with mocked internals."""
        with patch("src.multi_tenant.storefront_ingestion.IngestionJobRepository.__init__", return_value=None):
            self.repo = IngestionJobRepository()
            self.repo._repo = AsyncMock()

    @pytest.mark.asyncio
    async def test_create_delegates_to_repo(self):
        job = _make_job()
        self.repo._repo.create = AsyncMock(return_value={"id": job.id})
        result = await self.repo.create(job)
        self.repo._repo.create.assert_called_once_with(job.tenant_id, job)

    @pytest.mark.asyncio
    async def test_read_delegates(self):
        self.repo._repo.read = AsyncMock(return_value={"id": "j1"})
        result = await self.repo.read("t1", "j1")
        self.repo._repo.read.assert_called_once_with("t1", "j1")

    @pytest.mark.asyncio
    async def test_patch_delegates(self):
        ops = [{"op": "set", "path": "/status", "value": "running"}]
        self.repo._repo.patch = AsyncMock(return_value={"id": "j1"})
        await self.repo.patch("t1", "j1", ops)
        self.repo._repo.patch.assert_called_once_with("t1", "j1", ops)

    @pytest.mark.asyncio
    async def test_get_pending_jobs_queries_pending_status(self):
        mock_container = MagicMock()

        async def _empty_iter(**kwargs):
            return
            yield  # noqa: unreachable — makes this an async generator

        mock_container.query_items = MagicMock(side_effect=_empty_iter)
        self.repo._repo._container = mock_container
        await self.repo.get_pending_jobs(limit=5)
        call_kwargs = mock_container.query_items.call_args[1]
        assert "status = @status" in call_kwargs["query"]
        assert any(p["value"] == "pending" for p in call_kwargs["parameters"])

    @pytest.mark.asyncio
    async def test_get_latest_for_tenant(self):
        self.repo._repo.query = AsyncMock(return_value=[])
        await self.repo.get_latest_for_tenant("t1", limit=3)
        call_args = self.repo._repo.query.call_args
        # First positional arg is tenant_id, second is query text
        assert call_args[0][0] == "t1"
        query = call_args[0][1]
        assert "tenant_id = @tenant_id" in query
        assert "ORDER BY c.created_at DESC" in query

    @pytest.mark.asyncio
    async def test_get_orphaned_running(self):
        mock_container = MagicMock()

        async def _empty_iter(**kwargs):
            return
            yield  # noqa: unreachable — makes this an async generator

        mock_container.query_items = MagicMock(side_effect=_empty_iter)
        self.repo._repo._container = mock_container
        await self.repo.get_orphaned_running("2026-01-01T00:00:00Z")
        call_kwargs = mock_container.query_items.call_args[1]
        assert "status = @status" in call_kwargs["query"]
        assert "started_at < @cutoff" in call_kwargs["query"]


# ---------------------------------------------------------------------------
# Shopify product conversion tests
# ---------------------------------------------------------------------------

class TestShopifyProductConversion:
    """Test _shopify_product_to_kb_entry conversion logic."""

    def setup_method(self):
        self.service = StorefrontIngestionService.__new__(StorefrontIngestionService)

    def test_converts_valid_product(self):
        product = _make_shopify_product()
        entry = self.service._shopify_product_to_kb_entry("t1", product)

        assert entry is not None
        assert entry["entry_type"] == "product"
        assert entry["title"] == "Premium Widget"
        assert "premium widget" in entry["content"].lower()
        assert entry["tenant_id"] == "t1"
        assert entry["status"] == "published"
        assert entry["is_active"] is True
        assert entry["source_type"] == "shopify"
        assert entry["metadata"]["product_type"] == "Gadgets"
        assert entry["metadata"]["vendor"] == "WidgetCo"
        assert entry["metadata"]["sku"] == "WDG-001"

    def test_includes_price_range(self):
        product = _make_shopify_product(min_price="10.00", max_price="50.00")
        entry = self.service._shopify_product_to_kb_entry("t1", product)
        assert "10.00" in entry["content"]
        assert "50.00" in entry["content"]

    def test_single_price_no_range(self):
        product = _make_shopify_product(min_price="25.00", max_price="25.00")
        entry = self.service._shopify_product_to_kb_entry("t1", product)
        assert "25.00" in entry["content"]
        assert "–" not in entry["content"]

    def test_skips_empty_title(self):
        product = _make_shopify_product(title="")
        entry = self.service._shopify_product_to_kb_entry("t1", product)
        assert entry is None

    def test_skips_short_description(self):
        product = _make_shopify_product(description="Too short")
        entry = self.service._shopify_product_to_kb_entry("t1", product)
        assert entry is None

    def test_includes_image_url_in_metadata(self):
        product = _make_shopify_product(image_url="https://cdn.example.com/img.jpg")
        entry = self.service._shopify_product_to_kb_entry("t1", product)
        assert entry["metadata"]["image_url"] == "https://cdn.example.com/img.jpg"

    def test_no_image_sets_none(self):
        product = _make_shopify_product(image_url=None)
        entry = self.service._shopify_product_to_kb_entry("t1", product)
        assert entry["metadata"]["image_url"] is None

    def test_tags_capped_at_20(self):
        product = _make_shopify_product(tags=[f"tag{i}" for i in range(30)])
        entry = self.service._shopify_product_to_kb_entry("t1", product)
        assert len(entry["tags"]) == 20

    def test_category_set_to_products(self):
        product = _make_shopify_product()
        entry = self.service._shopify_product_to_kb_entry("t1", product)
        assert entry["category"] == "Products"

    def test_includes_vendor_and_type(self):
        product = _make_shopify_product(vendor="TestBrand", product_type="Electronics")
        entry = self.service._shopify_product_to_kb_entry("t1", product)
        assert "TestBrand" in entry["content"]
        assert "Electronics" in entry["content"]


# ---------------------------------------------------------------------------
# StorefrontIngestionService lifecycle tests
# ---------------------------------------------------------------------------

class TestIngestionServiceLifecycle:
    """Test start_ingestion, get_job_status, cancel_job."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        self.service = StorefrontIngestionService.__new__(StorefrontIngestionService)
        self.service._job_repo = AsyncMock(spec=IngestionJobRepository)

    @pytest.mark.asyncio
    async def test_start_ingestion_creates_pending_job(self):
        self.service._job_repo.create = AsyncMock(return_value={"id": "j1"})

        job_id = await self.service.start_ingestion(
            "t1", "url", {"start_url": "https://example.com"},
        )

        assert job_id is not None
        call_args = self.service._job_repo.create.call_args[0][0]
        assert call_args.status == IngestionJobStatus.PENDING.value
        assert call_args.job_type == "url"
        assert call_args.tenant_id == "t1"

    @pytest.mark.asyncio
    async def test_get_job_status_delegates_to_read(self):
        self.service._job_repo.read = AsyncMock(return_value={"id": "j1", "status": "running"})
        result = await self.service.get_job_status("t1", "j1")
        assert result["status"] == "running"

    @pytest.mark.asyncio
    async def test_cancel_job_sets_cancelled_status(self):
        self.service._job_repo.patch = AsyncMock(return_value={"id": "j1"})
        await self.service.cancel_job("t1", "j1")

        call_args = self.service._job_repo.patch.call_args
        ops = call_args[0][2]
        status_op = next(op for op in ops if op["path"] == "/status")
        assert status_op["value"] == IngestionJobStatus.CANCELLED.value


# ---------------------------------------------------------------------------
# process_job tests (URL path)
# ---------------------------------------------------------------------------

class TestProcessJobUrl:
    """Test process_job with URL ingestion path."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        self.service = StorefrontIngestionService.__new__(StorefrontIngestionService)
        self.service._job_repo = AsyncMock(spec=IngestionJobRepository)

    @pytest.mark.asyncio
    async def test_url_job_calls_crawl_url(self):
        """URL job should use crawl_url and create KB entries."""
        from dataclasses import dataclass

        @dataclass
        class MockChunk:
            text: str = "A" * 200
            title: str = "Test Page"
            chunk_index: int = 0
            metadata: dict = None

            def __post_init__(self):
                if self.metadata is None:
                    self.metadata = {}

        @dataclass
        class MockParseResult:
            source_type: str = "url"
            source_filename: str | None = None
            source_url: str = "https://example.com"
            chunks: list = None
            total_chars: int = 200
            error: str | None = None

            @property
            def success(self):
                return self.error is None and len(self.chunks or []) > 0

            def __post_init__(self):
                if self.chunks is None:
                    self.chunks = [MockChunk()]

        self.service._job_repo.read = AsyncMock(return_value={
            "id": "j1",
            "tenant_id": "t1",
            "job_type": "url",
            "status": "running",
            "source_config": {"start_url": "https://example.com", "max_pages": 5},
        })

        with (
            patch("src.multi_tenant.storefront_ingestion.StorefrontIngestionService._create_kb_article",
                  new_callable=AsyncMock, return_value="entry-1") as mock_create,
            patch("src.multi_tenant.storefront_ingestion.StorefrontIngestionService._vectorize_entries",
                  new_callable=AsyncMock, return_value=1),
            patch("src.multi_tenant.document_parser.crawl_url",
                  new_callable=AsyncMock, return_value=[MockParseResult()]),
            patch("src.multi_tenant.document_parser.chunks_to_kb_entries",
                  return_value=[{"id": "e1", "tenant_id": "t1", "content": "A" * 200, "title": "Test"}]),
        ):
            await self.service.process_job("j1", "t1")

        # Should have marked completed
        patch_calls = self.service._job_repo.patch.call_args_list
        last_patch = patch_calls[-1][0][2]
        status_op = next(op for op in last_patch if op["path"] == "/status")
        assert status_op["value"] == "completed"

    @pytest.mark.asyncio
    async def test_url_job_marks_failed_on_error(self):
        """If crawl_url raises, job should be marked failed."""
        self.service._job_repo.read = AsyncMock(return_value={
            "id": "j1",
            "tenant_id": "t1",
            "job_type": "url",
            "status": "running",
            "source_config": {"start_url": "https://bad-url.test", "max_pages": 5},
        })

        with patch(
            "src.multi_tenant.document_parser.crawl_url",
            new_callable=AsyncMock,
            return_value=[],
        ):
            await self.service.process_job("j1", "t1")

        # Should have marked failed
        patch_calls = self.service._job_repo.patch.call_args_list
        last_patch = patch_calls[-1][0][2]
        status_op = next(op for op in last_patch if op["path"] == "/status")
        assert status_op["value"] == "failed"


# ---------------------------------------------------------------------------
# process_job tests (Shopify path)
# ---------------------------------------------------------------------------

class TestProcessJobShopify:
    """Test process_job with Shopify ingestion path (mocked GraphQL)."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        self.service = StorefrontIngestionService.__new__(StorefrontIngestionService)
        self.service._job_repo = AsyncMock(spec=IngestionJobRepository)

    @pytest.mark.asyncio
    async def test_shopify_job_processes_products(self):
        """Shopify job should fetch products, collections, policies."""
        product = _make_shopify_product()

        mock_client = AsyncMock()
        mock_client.execute = AsyncMock(side_effect=[
            # Products query
            {"products": {
                "edges": [{"cursor": "c1", "node": product}],
                "pageInfo": {"hasNextPage": False, "endCursor": "c1"},
            }},
            # Collections query
            {"collections": {"edges": []}},
            # Policies query
            {"shop": {}},
        ])
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        self.service._job_repo.read = AsyncMock(return_value={
            "id": "j1",
            "tenant_id": "t1",
            "job_type": "shopify",
            "status": "running",
            "source_config": {"shop_domain": "test.myshopify.com", "access_token": "shpat_test"},
        })

        with (
            patch("src.multi_tenant.storefront_ingestion.StorefrontIngestionService._create_kb_article",
                  new_callable=AsyncMock, return_value="entry-1"),
            patch("src.multi_tenant.storefront_ingestion.StorefrontIngestionService._vectorize_entries",
                  new_callable=AsyncMock, return_value=1),
            patch("src.integrations.shopify_client.ShopifyGraphQLClient",
                  return_value=mock_client),
        ):
            await self.service.process_job("j1", "t1")

        # Should have marked completed
        patch_calls = self.service._job_repo.patch.call_args_list
        last_patch = patch_calls[-1][0][2]
        status_op = next(op for op in last_patch if op["path"] == "/status")
        assert status_op["value"] == "completed"
        articles_op = next(op for op in last_patch if op["path"] == "/articles_created")
        assert articles_op["value"] >= 1


# ---------------------------------------------------------------------------
# Result merging tests
# ---------------------------------------------------------------------------

class TestResultMerging:
    """Test _merge_result helper."""

    def test_merges_counts(self):
        target = {
            "articles_created": 5,
            "articles_failed": 1,
            "total_chars": 1000,
            "pages_crawled": 3,
            "entry_ids": ["a", "b"],
        }
        source = {
            "articles_created": 3,
            "articles_failed": 2,
            "total_chars": 500,
            "pages_crawled": 1,
            "entry_ids": ["c"],
        }
        StorefrontIngestionService._merge_result(target, source)

        assert target["articles_created"] == 8
        assert target["articles_failed"] == 3
        assert target["total_chars"] == 1500
        assert target["pages_crawled"] == 4
        assert target["entry_ids"] == ["a", "b", "c"]

    def test_handles_empty_source(self):
        target = {
            "articles_created": 5,
            "articles_failed": 0,
            "total_chars": 100,
            "pages_crawled": 1,
            "entry_ids": [],
        }
        StorefrontIngestionService._merge_result(target, {})
        assert target["articles_created"] == 5


# ---------------------------------------------------------------------------
# Singleton access test
# ---------------------------------------------------------------------------

class TestSingleton:
    """Test get_ingestion_service singleton."""

    def test_returns_instance(self):
        with patch("src.multi_tenant.storefront_ingestion.IngestionJobRepository"):
            service = get_ingestion_service()
            assert isinstance(service, StorefrontIngestionService)


# ---------------------------------------------------------------------------
# GraphQL query constant tests
# ---------------------------------------------------------------------------

class TestGraphQLQueries:
    """Verify GraphQL query constants are well-formed."""

    def test_products_query_has_pagination(self):
        assert "$first" in PRODUCTS_QUERY
        assert "$after" in PRODUCTS_QUERY
        assert "pageInfo" in PRODUCTS_QUERY
        assert "hasNextPage" in PRODUCTS_QUERY

    def test_collections_query_fetches_metadata(self):
        assert "title" in COLLECTIONS_QUERY
        assert "description" in COLLECTIONS_QUERY
        assert "productsCount" in COLLECTIONS_QUERY

    def test_policies_query_fetches_all_four(self):
        assert "privacyPolicy" in SHOP_POLICIES_QUERY
        assert "refundPolicy" in SHOP_POLICIES_QUERY
        assert "shippingPolicy" in SHOP_POLICIES_QUERY
        assert "termsOfService" in SHOP_POLICIES_QUERY


# ---------------------------------------------------------------------------
# Template ingestion integration test
# ---------------------------------------------------------------------------

class TestTemplateIngestion:
    """Test that category template ingestion delegates to TemplateLoader."""

    @pytest.mark.asyncio
    async def test_template_ingestion_completes_successfully(self):
        service = StorefrontIngestionService.__new__(StorefrontIngestionService)
        service._job_repo = AsyncMock(spec=IngestionJobRepository)

        service._job_repo.read = AsyncMock(return_value={
            "id": "j1",
            "tenant_id": "t1",
            "job_type": "category_template",
            "status": "running",
            "source_config": {"category_id": "apparel_fashion"},
        })

        mock_loader = MagicMock()
        mock_loader.apply_template = AsyncMock(return_value={
            "articles_created": 15,
            "articles_failed": 0,
            "total_chars": 5000,
            "entry_ids": [f"e{i}" for i in range(15)],
            "config_suggestions": {"brand_voice": "trendy"},
        })

        with patch(
            "src.multi_tenant.template_loader.get_template_loader",
            return_value=mock_loader,
        ):
            await service.process_job("j1", "t1")

        # Verify job marked as completed
        patch_calls = service._job_repo.patch.call_args_list
        last_patch = patch_calls[-1][0][2]
        status_op = next(op for op in last_patch if op["path"] == "/status")
        assert status_op["value"] == "completed"
        articles_op = next(op for op in last_patch if op["path"] == "/articles_created")
        assert articles_op["value"] == 15

    @pytest.mark.asyncio
    async def test_template_ingestion_missing_category_id(self):
        service = StorefrontIngestionService.__new__(StorefrontIngestionService)
        service._job_repo = AsyncMock(spec=IngestionJobRepository)

        service._job_repo.read = AsyncMock(return_value={
            "id": "j1",
            "tenant_id": "t1",
            "job_type": "category_template",
            "status": "running",
            "source_config": {},  # No category_id
        })

        await service.process_job("j1", "t1")

        # Should mark as failed due to missing category_id
        patch_calls = service._job_repo.patch.call_args_list
        last_patch = patch_calls[-1][0][2]
        status_op = next(op for op in last_patch if op["path"] == "/status")
        assert status_op["value"] == "failed"
