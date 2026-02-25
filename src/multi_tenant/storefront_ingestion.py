"""Storefront Ingestion Service (KA-1: Knowledge Automation).

Orchestrates bulk knowledge base population from merchant storefronts.
Supports three ingestion paths:
  - Shopify: Bulk product/collection/policy import via Admin GraphQL API
  - URL: Multi-page web crawl via document_parser.crawl_url()
  - Category template: Industry-specific starter KB content (KA-3)

Jobs are tracked in the ingestion_jobs Cosmos DB collection and processed
by a background loop in background.py.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import uuid

from datetime import datetime, timezone
from typing import Any

from src.multi_tenant.cosmos_schema import (
    COLLECTION_INGESTION_JOBS,
    IngestionJobDocument,
    IngestionJobStatus,
    IngestionJobType,
    KnowledgeBaseDocument,
)

logger = logging.getLogger(__name__)

# Maximum products to ingest from Shopify per job
SHOPIFY_MAX_PRODUCTS = 250
# Maximum pages to crawl per URL job
URL_MAX_PAGES = 50
# Minimum content length (chars) to create a KB article
MIN_CONTENT_LENGTH = 100
# Delay between Shopify API calls (seconds) to respect rate limits
SHOPIFY_API_DELAY = 1.0

# ---------------------------------------------------------------------------
# Shopify GraphQL query constants
# ---------------------------------------------------------------------------

PRODUCTS_QUERY = """
query Products($first: Int!, $after: String) {
    products(first: $first, after: $after) {
        edges {
            cursor
            node {
                id
                title
                description
                descriptionHtml
                productType
                vendor
                tags
                handle
                status
                priceRangeV2 {
                    minVariantPrice {
                        amount
                        currencyCode
                    }
                    maxVariantPrice {
                        amount
                        currencyCode
                    }
                }
                images(first: 1) {
                    edges {
                        node {
                            url
                            altText
                        }
                    }
                }
                variants(first: 1) {
                    edges {
                        node {
                            sku
                        }
                    }
                }
            }
        }
        pageInfo {
            hasNextPage
            endCursor
        }
    }
}
"""

COLLECTIONS_QUERY = """
query Collections($first: Int!) {
    collections(first: $first) {
        edges {
            node {
                id
                title
                description
                descriptionHtml
                handle
                productsCount {
                    count
                }
            }
        }
    }
}
"""

SHOP_POLICIES_QUERY = """
query ShopPolicies {
    shop {
        privacyPolicy {
            title
            body
        }
        refundPolicy {
            title
            body
        }
        shippingPolicy {
            title
            body
        }
        termsOfService {
            title
            body
        }
    }
}
"""


# ---------------------------------------------------------------------------
# IngestionJobRepository
# ---------------------------------------------------------------------------


class IngestionJobRepository:
    """Cosmos DB repository for ingestion job documents."""

    def __init__(self) -> None:
        from src.multi_tenant.repository import TenantScopedRepository

        self._repo = TenantScopedRepository(COLLECTION_INGESTION_JOBS)

    async def create(self, job: IngestionJobDocument) -> dict[str, Any]:
        """Create a new ingestion job document."""
        return await self._repo.create(job.tenant_id, job)

    async def read(self, tenant_id: str, job_id: str) -> dict[str, Any]:
        """Read a specific ingestion job."""
        return await self._repo.read(tenant_id, job_id)

    async def patch(
        self,
        tenant_id: str,
        job_id: str,
        operations: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Apply patch operations to a job document."""
        return await self._repo.patch(tenant_id, job_id, operations)

    async def get_pending_jobs(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get pending jobs ordered by creation time (oldest first).

        Cross-partition query — scans all tenants for pending jobs.
        """
        query = (
            "SELECT * FROM c WHERE c.status = @status "
            "ORDER BY c.created_at ASC OFFSET 0 LIMIT @limit"
        )
        params = [
            {"name": "@status", "value": IngestionJobStatus.PENDING.value},
            {"name": "@limit", "value": limit},
        ]
        items: list[dict[str, Any]] = []
        async for item in self._repo._container.query_items(
            query=query, parameters=params,
        ):
            items.append(item)
        return items

    async def get_latest_for_tenant(
        self,
        tenant_id: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Get the most recent ingestion jobs for a tenant."""
        query = (
            "SELECT * FROM c WHERE c.tenant_id = @tenant_id "
            "ORDER BY c.created_at DESC OFFSET 0 LIMIT @limit"
        )
        params = [
            {"name": "@tenant_id", "value": tenant_id},
            {"name": "@limit", "value": limit},
        ]
        return await self._repo.query(tenant_id, query, params)

    async def get_orphaned_running(self, cutoff_iso: str) -> list[dict[str, Any]]:
        """Find running jobs that started before the cutoff (orphan detection).

        Cross-partition query — scans all tenants for orphaned jobs.
        """
        query = (
            "SELECT * FROM c WHERE c.status = @status "
            "AND c.started_at < @cutoff"
        )
        params = [
            {"name": "@status", "value": IngestionJobStatus.RUNNING.value},
            {"name": "@cutoff", "value": cutoff_iso},
        ]
        items: list[dict[str, Any]] = []
        async for item in self._repo._container.query_items(
            query=query, parameters=params,
        ):
            items.append(item)
        return items


# ---------------------------------------------------------------------------
# StorefrontIngestionService
# ---------------------------------------------------------------------------


class StorefrontIngestionService:
    """Orchestrates bulk KB population from merchant storefronts.

    Usage:
        service = StorefrontIngestionService()
        job_id = await service.start_ingestion(tenant_id, source_config)
        # ... background loop calls process_job(job_id) ...
        status = await service.get_job_status(tenant_id, job_id)
    """

    def __init__(self) -> None:
        self._job_repo = IngestionJobRepository()

    async def start_ingestion(
        self,
        tenant_id: str,
        job_type: str,
        source_config: dict[str, Any],
    ) -> str:
        """Create a new ingestion job and return the job_id.

        The job is created in PENDING status. The background processor
        will pick it up and execute it.
        """
        job_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        job = IngestionJobDocument(
            id=job_id,
            tenant_id=tenant_id,
            job_type=job_type,
            status=IngestionJobStatus.PENDING.value,
            source_config=source_config,
            created_at=now,
        )

        await self._job_repo.create(job)
        logger.info(
            "Ingestion job created: %s (type=%s, tenant=%s)",
            job_id[:8], job_type, tenant_id[:8],
        )
        return job_id

    async def get_job_status(
        self,
        tenant_id: str,
        job_id: str,
    ) -> dict[str, Any]:
        """Get the current status of an ingestion job."""
        return await self._job_repo.read(tenant_id, job_id)

    async def get_latest_job(
        self,
        tenant_id: str,
    ) -> dict[str, Any] | None:
        """Get the most recent ingestion job for a tenant."""
        jobs = await self._job_repo.get_latest_for_tenant(tenant_id, limit=1)
        return jobs[0] if jobs else None

    async def cancel_job(self, tenant_id: str, job_id: str) -> dict[str, Any]:
        """Cancel a pending or running job."""
        now = datetime.now(timezone.utc).isoformat()
        return await self._job_repo.patch(
            tenant_id,
            job_id,
            [
                {"op": "set", "path": "/status", "value": IngestionJobStatus.CANCELLED.value},
                {"op": "set", "path": "/completed_at", "value": now},
            ],
        )

    async def process_job(self, job_id: str, tenant_id: str) -> None:
        """Execute an ingestion job. Called by the background processor.

        Updates job status to RUNNING, processes based on job_type,
        then marks COMPLETED or FAILED.
        """
        now = datetime.now(timezone.utc).isoformat()

        # Mark as running
        try:
            await self._job_repo.patch(
                tenant_id,
                job_id,
                [
                    {"op": "set", "path": "/status", "value": IngestionJobStatus.RUNNING.value},
                    {"op": "set", "path": "/started_at", "value": now},
                ],
            )
        except Exception:
            logger.warning("Failed to mark job %s as running", job_id[:8], exc_info=True)
            return

        try:
            job = await self._job_repo.read(tenant_id, job_id)

            # Check for cancellation
            if job.get("status") == IngestionJobStatus.CANCELLED.value:
                logger.info("Job %s was cancelled before processing", job_id[:8])
                return

            job_type = job["job_type"]
            source_config = job.get("source_config", {})

            if job_type == IngestionJobType.SHOPIFY.value:
                result = await self._process_shopify(tenant_id, job_id, source_config)
            elif job_type == IngestionJobType.URL.value:
                result = await self._process_url(tenant_id, job_id, source_config)
            elif job_type == IngestionJobType.CATEGORY_TEMPLATE.value:
                result = await self._process_template(tenant_id, job_id, source_config)
            elif job_type == IngestionJobType.WEBSITE_REFRESH.value:
                result = await self._process_website_refresh(tenant_id, job_id, source_config)
            else:
                raise ValueError(f"Unknown job type: {job_type}")

            # Mark completed
            completed_at = datetime.now(timezone.utc).isoformat()
            await self._job_repo.patch(
                tenant_id,
                job_id,
                [
                    {"op": "set", "path": "/status", "value": IngestionJobStatus.COMPLETED.value},
                    {"op": "set", "path": "/completed_at", "value": completed_at},
                    {"op": "set", "path": "/progress_percent", "value": 100},
                    {"op": "set", "path": "/articles_created", "value": result["articles_created"]},
                    {"op": "set", "path": "/articles_failed", "value": result["articles_failed"]},
                    {"op": "set", "path": "/total_chars", "value": result["total_chars"]},
                    {"op": "set", "path": "/pages_crawled", "value": result["pages_crawled"]},
                    {"op": "set", "path": "/entry_ids", "value": result["entry_ids"]},
                ],
            )

            logger.info(
                "Ingestion job %s completed: %d articles, %d chars",
                job_id[:8], result["articles_created"], result["total_chars"],
            )

        except Exception as exc:
            # Mark failed
            failed_at = datetime.now(timezone.utc).isoformat()
            try:
                await self._job_repo.patch(
                    tenant_id,
                    job_id,
                    [
                        {"op": "set", "path": "/status", "value": IngestionJobStatus.FAILED.value},
                        {"op": "set", "path": "/completed_at", "value": failed_at},
                        {"op": "set", "path": "/error_message", "value": f"{type(exc).__name__}: {exc}"[:500]},
                    ],
                )
            except Exception:
                logger.warning(
                    "Failed to mark job %s as failed", job_id[:8], exc_info=True,
                )
            logger.error("Ingestion job %s failed: %s", job_id[:8], exc, exc_info=True)

    # -------------------------------------------------------------------
    # Shopify ingestion path
    # -------------------------------------------------------------------

    async def _process_shopify(
        self,
        tenant_id: str,
        job_id: str,
        source_config: dict[str, Any],
    ) -> dict[str, Any]:
        """Ingest products, collections, and policies from Shopify Admin API."""
        import asyncio

        from src.integrations.shopify_client import ShopifyGraphQLClient

        shop_domain = source_config["shop_domain"]
        access_token = source_config["access_token"]

        result = {
            "articles_created": 0,
            "articles_failed": 0,
            "total_chars": 0,
            "pages_crawled": 0,
            "entry_ids": [],
        }

        async with ShopifyGraphQLClient(shop_domain, access_token) as client:
            # 1. Ingest products (paginated)
            products_result = await self._ingest_shopify_products(
                client, tenant_id, job_id,
            )
            self._merge_result(result, products_result)

            # 2. Ingest collections
            collections_result = await self._ingest_shopify_collections(
                client, tenant_id,
            )
            self._merge_result(result, collections_result)

            # Delay between API sections
            await asyncio.sleep(SHOPIFY_API_DELAY)

            # 3. Ingest shop policies
            policies_result = await self._ingest_shopify_policies(
                client, tenant_id,
            )
            self._merge_result(result, policies_result)

        # 4. Vectorize all created articles
        await self._vectorize_entries(tenant_id, result["entry_ids"])

        return result

    async def _ingest_shopify_products(
        self,
        client: Any,
        tenant_id: str,
        job_id: str,
    ) -> dict[str, Any]:
        """Fetch and convert Shopify products to KB articles."""
        import asyncio

        result = {
            "articles_created": 0,
            "articles_failed": 0,
            "total_chars": 0,
            "pages_crawled": 0,
            "entry_ids": [],
        }

        cursor: str | None = None
        total_fetched = 0
        page_size = 50

        while total_fetched < SHOPIFY_MAX_PRODUCTS:
            variables: dict[str, Any] = {"first": page_size}
            if cursor:
                variables["after"] = cursor

            data = await client.execute(PRODUCTS_QUERY, variables)
            products = data.get("products", {})
            edges = products.get("edges", [])

            if not edges:
                break

            for edge in edges:
                node = edge.get("node", {})
                try:
                    entry = self._shopify_product_to_kb_entry(tenant_id, node)
                    if entry:
                        entry_id = await self._create_kb_article(tenant_id, entry)
                        if entry_id:
                            result["entry_ids"].append(entry_id)
                            result["articles_created"] += 1
                            result["total_chars"] += len(entry.get("content", ""))
                        else:
                            result["articles_failed"] += 1
                except Exception:
                    result["articles_failed"] += 1
                    logger.debug(
                        "Failed to convert product %s",
                        node.get("title", "unknown"),
                        exc_info=True,
                    )

            total_fetched += len(edges)
            result["pages_crawled"] += 1

            # Update progress
            progress = min(60, int(total_fetched / SHOPIFY_MAX_PRODUCTS * 60))
            try:
                await self._job_repo.patch(
                    tenant_id, job_id,
                    [{"op": "set", "path": "/progress_percent", "value": progress}],
                )
            except Exception:
                pass

            page_info = products.get("pageInfo", {})
            if not page_info.get("hasNextPage"):
                break
            cursor = page_info.get("endCursor")
            await asyncio.sleep(SHOPIFY_API_DELAY)

        return result

    def _shopify_product_to_kb_entry(
        self,
        tenant_id: str,
        product: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Convert a Shopify product GraphQL node to a KB entry dict."""
        title = product.get("title", "").strip()
        description = product.get("description", "").strip()

        if not title or len(description) < MIN_CONTENT_LENGTH:
            return None

        # Build rich content
        content_parts = [description]

        product_type = product.get("productType", "")
        if product_type:
            content_parts.append(f"Product type: {product_type}")

        vendor = product.get("vendor", "")
        if vendor:
            content_parts.append(f"Brand/Vendor: {vendor}")

        price_range = product.get("priceRangeV2", {})
        min_price = price_range.get("minVariantPrice", {})
        max_price = price_range.get("maxVariantPrice", {})
        if min_price.get("amount") is not None:
            currency = min_price.get("currencyCode", "USD")
            min_amt = min_price["amount"]
            max_amt = max_price.get("amount", min_amt)
            if min_amt == max_amt:
                content_parts.append(f"Price: {min_amt} {currency}")
            else:
                content_parts.append(f"Price: {min_amt} – {max_amt} {currency}")

        content = "\n\n".join(content_parts)
        now = datetime.now(timezone.utc).isoformat()

        # Extract metadata
        tags = product.get("tags", [])
        images = product.get("images", {}).get("edges", [])
        image_url = None
        if images:
            first_image = images[0]
            if isinstance(first_image, dict):
                node = first_image.get("node", {})
                image_url = node.get("url") if isinstance(node, dict) else None

        sku = None
        variants = product.get("variants", {}).get("edges", [])
        if variants:
            sku = variants[0].get("node", {}).get("sku")

        return {
            "id": str(uuid.uuid4()),
            "tenant_id": tenant_id,
            "entry_type": "product",
            "title": title,
            "content": content,
            "metadata": {
                "shopify_product_id": product.get("id", ""),
                "product_type": product_type,
                "vendor": vendor,
                "handle": product.get("handle", ""),
                "image_url": image_url,
                "sku": sku,
            },
            "tags": tags[:20],  # Cap tags
            "language": "en",
            "category": "Products",
            "status": "published",
            "is_active": True,
            "source_type": "shopify",
            "source_url": f"https://{product.get('handle', '')}",
            "created_at": now,
            "updated_at": now,
        }

    async def _ingest_shopify_collections(
        self,
        client: Any,
        tenant_id: str,
    ) -> dict[str, Any]:
        """Fetch and convert Shopify collections to KB articles."""
        result = {
            "articles_created": 0,
            "articles_failed": 0,
            "total_chars": 0,
            "pages_crawled": 0,
            "entry_ids": [],
        }

        try:
            data = await client.execute(COLLECTIONS_QUERY, {"first": 50})
            edges = data.get("collections", {}).get("edges", [])
            result["pages_crawled"] += 1

            for edge in edges:
                node = edge.get("node", {})
                title = node.get("title", "").strip()
                description = node.get("description", "").strip()

                if not title or len(description) < 30:
                    continue

                now = datetime.now(timezone.utc).isoformat()
                entry = {
                    "id": str(uuid.uuid4()),
                    "tenant_id": tenant_id,
                    "entry_type": "article",
                    "title": f"Collection: {title}",
                    "content": description,
                    "metadata": {
                        "shopify_collection_id": node.get("id", ""),
                        "handle": node.get("handle", ""),
                        "products_count": node.get("productsCount", {}).get("count", 0),
                    },
                    "tags": ["collection"],
                    "language": "en",
                    "category": "Products",
                    "status": "published",
                    "is_active": True,
                    "source_type": "shopify",
                    "created_at": now,
                    "updated_at": now,
                }

                entry_id = await self._create_kb_article(tenant_id, entry)
                if entry_id:
                    result["entry_ids"].append(entry_id)
                    result["articles_created"] += 1
                    result["total_chars"] += len(description)
                else:
                    result["articles_failed"] += 1

        except Exception:
            logger.debug("Failed to ingest Shopify collections", exc_info=True)

        return result

    async def _ingest_shopify_policies(
        self,
        client: Any,
        tenant_id: str,
    ) -> dict[str, Any]:
        """Fetch and convert Shopify shop policies to KB articles."""
        result = {
            "articles_created": 0,
            "articles_failed": 0,
            "total_chars": 0,
            "pages_crawled": 0,
            "entry_ids": [],
        }

        try:
            data = await client.execute(SHOP_POLICIES_QUERY)
            shop = data.get("shop", {})
            result["pages_crawled"] += 1

            policy_fields = [
                ("privacyPolicy", "Privacy Policy", "Legal"),
                ("refundPolicy", "Return & Refund Policy", "Returns"),
                ("shippingPolicy", "Shipping Policy", "Shipping"),
                ("termsOfService", "Terms of Service", "Legal"),
            ]

            for field_name, title, category in policy_fields:
                policy = shop.get(field_name)
                if not policy:
                    continue

                body = policy.get("body", "").strip()
                if len(body) < MIN_CONTENT_LENGTH:
                    continue

                now = datetime.now(timezone.utc).isoformat()
                entry = {
                    "id": str(uuid.uuid4()),
                    "tenant_id": tenant_id,
                    "entry_type": "policy",
                    "title": policy.get("title", title),
                    "content": body,
                    "metadata": {"policy_type": field_name},
                    "tags": ["policy", category.lower()],
                    "language": "en",
                    "category": category,
                    "status": "published",
                    "is_active": True,
                    "source_type": "shopify",
                    "created_at": now,
                    "updated_at": now,
                }

                entry_id = await self._create_kb_article(tenant_id, entry)
                if entry_id:
                    result["entry_ids"].append(entry_id)
                    result["articles_created"] += 1
                    result["total_chars"] += len(body)
                else:
                    result["articles_failed"] += 1

        except Exception:
            logger.debug("Failed to ingest Shopify policies", exc_info=True)

        return result

    # -------------------------------------------------------------------
    # URL crawl ingestion path
    # -------------------------------------------------------------------

    async def _process_url(
        self,
        tenant_id: str,
        job_id: str,
        source_config: dict[str, Any],
    ) -> dict[str, Any]:
        """Ingest KB content by crawling a URL."""
        from src.multi_tenant.document_parser import crawl_url, chunks_to_kb_entries

        start_url = source_config["start_url"]
        max_pages = min(source_config.get("max_pages", 10), URL_MAX_PAGES)
        entry_type = source_config.get("entry_type", "article")

        result = {
            "articles_created": 0,
            "articles_failed": 0,
            "total_chars": 0,
            "pages_crawled": 0,
            "entry_ids": [],
        }

        # Crawl
        parse_results = await crawl_url(start_url, max_pages=max_pages)

        if not parse_results:
            raise ValueError(f"No pages could be parsed from {start_url}")

        # Convert to KB entries
        for i, parse_result in enumerate(parse_results):
            if not parse_result.success:
                continue

            result["pages_crawled"] += 1
            entries = chunks_to_kb_entries(parse_result, tenant_id, entry_type)

            for entry_dict in entries:
                content = entry_dict.get("content", "")
                if len(content) < MIN_CONTENT_LENGTH:
                    continue

                try:
                    entry_id = await self._create_kb_article(tenant_id, entry_dict)
                    if entry_id:
                        result["entry_ids"].append(entry_id)
                        result["articles_created"] += 1
                        result["total_chars"] += len(content)
                    else:
                        result["articles_failed"] += 1
                except Exception:
                    result["articles_failed"] += 1
                    logger.debug(
                        "Failed to create KB entry from URL chunk",
                        exc_info=True,
                    )

            # Update progress
            progress = min(80, int((i + 1) / len(parse_results) * 80))
            try:
                await self._job_repo.patch(
                    tenant_id, job_id,
                    [{"op": "set", "path": "/progress_percent", "value": progress}],
                )
            except Exception:
                pass

        # Vectorize
        await self._vectorize_entries(tenant_id, result["entry_ids"])

        return result

    # -------------------------------------------------------------------
    # Category template ingestion path (KA-3)
    # -------------------------------------------------------------------

    async def _process_template(
        self,
        tenant_id: str,
        job_id: str,
        source_config: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply a category template to populate the KB.

        Delegates to TemplateLoader.apply_template() for the actual
        article creation and vectorization.
        """
        from src.multi_tenant.template_loader import get_template_loader

        category_id = source_config.get("category_id")
        if not category_id:
            raise ValueError("source_config must include 'category_id'")

        merge_mode = source_config.get("merge_mode", "append")
        loader = get_template_loader()

        # Update progress
        try:
            await self._job_repo.patch(
                tenant_id, job_id,
                [{"op": "set", "path": "/progress_percent", "value": 10}],
            )
        except Exception:
            pass

        result = await loader.apply_template(
            tenant_id,
            category_id,
            merge_mode=merge_mode,
        )

        return {
            "articles_created": result.get("articles_created", 0),
            "articles_failed": result.get("articles_failed", 0),
            "total_chars": result.get("total_chars", 0),
            "pages_crawled": 0,
            "entry_ids": result.get("entry_ids", []),
        }

    # -------------------------------------------------------------------
    # Website refresh ingestion path
    # -------------------------------------------------------------------

    async def _process_website_refresh(
        self,
        tenant_id: str,
        job_id: str,
        source_config: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a website source re-crawl via the crawl service."""
        from src.multi_tenant.website_crawl_service import crawl_website_source

        source_id = source_config.get("source_id")
        if not source_id:
            raise ValueError("source_config must include 'source_id'")

        try:
            await self._job_repo.patch(
                tenant_id, job_id,
                [{"op": "set", "path": "/progress_percent", "value": 10}],
            )
        except Exception:
            pass

        result = await crawl_website_source(tenant_id, source_id)

        if "error" in result:
            raise RuntimeError(result["error"])

        return {
            "articles_created": result.get("articles_created", 0),
            "articles_failed": result.get("failed_pages", 0),
            "total_chars": result.get("total_chars", 0),
            "pages_crawled": result.get("pages_crawled", 0),
            "entry_ids": [],
        }

    # -------------------------------------------------------------------
    # Shared helpers
    # -------------------------------------------------------------------

    async def _create_kb_article(
        self,
        tenant_id: str,
        entry_dict: dict[str, Any],
    ) -> str | None:
        """Create a single KB article. Returns entry_id or None on failure."""
        from src.multi_tenant.repositories.knowledge import KnowledgeBaseRepository

        try:
            doc = KnowledgeBaseDocument(**entry_dict)
            repo = KnowledgeBaseRepository()
            await repo.create(tenant_id, doc)
            return doc.id
        except Exception:
            logger.debug(
                "Failed to create KB article: %s",
                entry_dict.get("title", "unknown")[:50],
                exc_info=True,
            )
            return None

    async def _vectorize_entries(
        self,
        tenant_id: str,
        entry_ids: list[str],
    ) -> int:
        """Batch-vectorize created KB articles. Returns count of embedded."""
        if not entry_ids:
            return 0

        try:
            from src.multi_tenant.knowledge_vectorizer import get_knowledge_vectorizer

            vectorizer = get_knowledge_vectorizer()
            from src.multi_tenant.repositories.knowledge import KnowledgeBaseRepository

            repo = KnowledgeBaseRepository()
            entries = []
            for eid in entry_ids:
                try:
                    entry = await repo.read(tenant_id, eid)
                    entries.append(entry)
                except Exception:
                    pass

            if entries:
                count = await vectorizer.embed_batch(tenant_id, entries)
                logger.info(
                    "Vectorized %d/%d entries for tenant %s",
                    count, len(entry_ids), tenant_id[:8],
                )
                return count
        except Exception:
            logger.warning(
                "Vectorization failed for tenant %s (non-fatal)",
                tenant_id[:8],
                exc_info=True,
            )
        return 0

    @staticmethod
    def _merge_result(
        target: dict[str, Any],
        source: dict[str, Any],
    ) -> None:
        """Merge ingestion sub-results into the main result dict."""
        target["articles_created"] += source.get("articles_created", 0)
        target["articles_failed"] += source.get("articles_failed", 0)
        target["total_chars"] += source.get("total_chars", 0)
        target["pages_crawled"] += source.get("pages_crawled", 0)
        target["entry_ids"].extend(source.get("entry_ids", []))


# ---------------------------------------------------------------------------
# Singleton access
# ---------------------------------------------------------------------------

_ingestion_service: StorefrontIngestionService | None = None


def get_ingestion_service() -> StorefrontIngestionService:
    """Get or create the singleton StorefrontIngestionService."""
    global _ingestion_service  # noqa: PLW0603
    if _ingestion_service is None:
        _ingestion_service = StorefrontIngestionService()
    return _ingestion_service
