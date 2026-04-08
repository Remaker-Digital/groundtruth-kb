"""Website crawl service — automated website source crawling with change detection.

Orchestrates the crawl lifecycle for WebsiteSourceDocument records:
  1. Load source config and build existing content hash map
  2. Execute incremental crawl with sitemap + change detection
  3. Create/update KB entries for new/changed pages (link-aware)
  4. Soft-delete KB entries for removed pages
  5. Update source status and schedule next crawl
  6. Trigger async embedding for new/changed entries

The service preserves source URLs on KB entries so the AI can inject
clickable links into chat conversations, enabling navigation to
product listings, policies, and other merchant site content.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta
from typing import Any
from urllib.parse import urlparse

from src.multi_tenant.cosmos_schema import (
    KnowledgeBaseDocument,
    WebsiteSourceStatus,
)
from src.multi_tenant.document_parser import (
    WebsiteCrawlResult,
    chunks_to_kb_entries,
    crawl_website,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tier limits for website sources
# ---------------------------------------------------------------------------

# Legacy TIER_LIMITS kept for backward compatibility — canonical values
# now live in EntitlementService (SPEC-1817).
TIER_LIMITS: dict[str, dict[str, int]] = {
    "starter": {"max_sources": 3, "max_pages": 25, "min_refresh_hours": 24},
    "professional": {"max_sources": 10, "max_pages": 50, "min_refresh_hours": 12},
    "enterprise": {"max_sources": 25, "max_pages": 100, "min_refresh_hours": 6},
}

DEFAULT_TIER = "starter"


def get_tier_limits(tier: str) -> dict[str, int]:
    """Get website source limits for a billing tier.

    Reads from EntitlementService (data-driven) with TIER_LIMITS fallback.
    """
    from src.multi_tenant.entitlement_service import get_entitlement_service
    svc = get_entitlement_service()
    # Sync path — use frozen/LRU fallback
    svc.get_tier_config_sync(tier)
    # website_limits may be stored as a nested key in the tier config
    # or as a separate entitlements document. Check LRU first.
    cached = svc._lru_get("entitlements:website_limits")
    if cached and tier in cached:
        return cached[tier]
    # Fall back to frozen entitlements
    from src.multi_tenant.entitlement_service import FROZEN_ENTITLEMENTS
    frozen_limits = FROZEN_ENTITLEMENTS.get("website_limits", {})
    if tier in frozen_limits:
        return frozen_limits[tier]
    return TIER_LIMITS.get(tier, TIER_LIMITS[DEFAULT_TIER])


# ---------------------------------------------------------------------------
# Page type classifier
# ---------------------------------------------------------------------------

_PAGE_TYPE_PATTERNS: list[tuple[str, list[str]]] = [
    ("product", ["/product", "/item", "/shop/", "/catalog/", "/collection"]),
    ("policy", ["/policy", "/privacy", "/terms", "/tos", "/legal", "/refund", "/shipping-policy"]),
    ("faq", ["/faq", "/help", "/support", "/knowledgebase", "/knowledge-base"]),
    ("blog", ["/blog", "/article", "/news", "/post"]),
    ("category", ["/category", "/collection", "/department", "/brand/"]),
    ("contact", ["/contact", "/about", "/location", "/store-locator"]),
]


def classify_page_type(url: str) -> str:
    """Classify a page URL into a semantic type for link injection context."""
    path = urlparse(url).path.lower()
    for page_type, patterns in _PAGE_TYPE_PATTERNS:
        if any(p in path for p in patterns):
            return page_type
    return "page"


# ---------------------------------------------------------------------------
# Crawl orchestrator
# ---------------------------------------------------------------------------


async def crawl_website_source(
    tenant_id: str,
    source_id: str,
) -> dict[str, Any]:
    """Execute a full crawl cycle for a website source.

    Args:
        tenant_id: Owning tenant.
        source_id: WebsiteSourceDocument ID.

    Returns:
        Summary dict with crawl statistics.
    """
    from src.multi_tenant.repositories.knowledge import KnowledgeBaseRepository

    repo = KnowledgeBaseRepository()

    # --- Load the source ---
    try:
        source = await repo.read(tenant_id, source_id)
    except Exception:
        logger.error("Website source not found: %s/%s", tenant_id[:8], source_id[:8])
        return {"error": "Source not found"}

    if source.get("doc_type") != "website_source":
        return {"error": "Document is not a website source"}

    domain = source["domain"]
    start_url = source["start_url"]
    max_pages = source.get("max_pages", 25)
    use_sitemap = source.get("max_pages", 25) > 10  # Only use sitemap for larger crawls

    # --- Mark crawling ---
    await repo.update_website_source(
        tenant_id, source_id,
        status=WebsiteSourceStatus.CRAWLING.value,
        error_message=None,
    )

    try:
        # --- Build existing hash map for incremental detection ---
        existing_entries = await repo.list_kb_entries_by_source(tenant_id, domain)
        existing_hashes: dict[str, str] = {}
        url_to_entry_id: dict[str, str] = {}
        for entry in existing_entries:
            url = entry.get("source_url")
            if url and entry.get("content_hash"):
                existing_hashes[url] = entry["content_hash"]
                url_to_entry_id[url] = entry["id"]

        # --- Execute incremental crawl ---
        crawl_result: WebsiteCrawlResult = await crawl_website(
            start_url=start_url,
            max_pages=max_pages,
            existing_hashes=existing_hashes if existing_hashes else None,
            use_sitemap=use_sitemap,
        )

        if crawl_result.error:
            await repo.update_website_source(
                tenant_id, source_id,
                status=WebsiteSourceStatus.FAILED.value,
                error_message=crawl_result.error,
            )
            return {"error": crawl_result.error}

        # --- Create/update KB entries for new + changed pages ---
        entry_ids: list[str] = []

        for page_result in crawl_result.results:
            source_url = page_result.source_url
            normalised_url = urlparse(source_url)._replace(fragment="").geturl() if source_url else None
            page_type = classify_page_type(source_url) if source_url else "page"

            # Enrich chunks with link metadata for AI citation
            for chunk in page_result.chunks:
                chunk.metadata["page_type"] = page_type
                chunk.metadata["link_label"] = chunk.title or domain
                chunk.metadata["source_domain"] = domain

            # Convert chunks to KB entries with website_crawl source type
            kb_entries = chunks_to_kb_entries(
                parse_result=page_result,
                tenant_id=tenant_id,
                default_entry_type="article",
            )

            for entry_dict in kb_entries:
                # Override source_type for website crawl entries
                entry_dict["source_type"] = "website_crawl"
                # Propagate content_hash from chunk metadata to entry level
                chunk_meta = entry_dict.get("metadata", {})
                if "content_hash" in chunk_meta:
                    entry_dict["content_hash"] = chunk_meta["content_hash"]

                # If this is a changed page, soft-delete old entry first
                if normalised_url and normalised_url in url_to_entry_id:
                    old_id = url_to_entry_id[normalised_url]
                    try:
                        await repo.soft_delete(tenant_id, old_id)
                    except Exception:
                        pass

                # Create new KB entry
                try:
                    doc = KnowledgeBaseDocument(**entry_dict)
                    await repo.create(tenant_id, doc)
                    entry_ids.append(doc.id)
                except Exception:
                    logger.debug(
                        "Failed to create KB entry from crawl: %s",
                        entry_dict.get("title", "unknown")[:50],
                        exc_info=True,
                    )

        # --- Soft-delete entries for removed pages ---
        removed_count = 0
        for removed_url in crawl_result.removed_urls:
            if removed_url in url_to_entry_id:
                try:
                    await repo.soft_delete(tenant_id, url_to_entry_id[removed_url])
                    removed_count += 1
                except Exception:
                    pass

        # --- Trigger async embedding ---
        embedded_count = await _vectorize_new_entries(tenant_id, entry_ids)

        # --- Update source with results ---
        now = datetime.now(timezone.utc)
        refresh_hours = source.get("refresh_interval_hours", 24)
        next_crawl = (now + timedelta(hours=refresh_hours)).isoformat()

        await repo.update_website_source(
            tenant_id, source_id,
            status=WebsiteSourceStatus.ACTIVE.value,
            last_crawled_at=now.isoformat(),
            next_crawl_at=next_crawl,
            pages_discovered=crawl_result.pages_discovered,
            pages_crawled=crawl_result.pages_crawled,
            articles_created=crawl_result.articles_created,
            total_chars=crawl_result.total_chars,
            error_message=None,
        )

        summary = {
            "new_pages": len(crawl_result.new_urls),
            "changed_pages": len(crawl_result.changed_urls),
            "unchanged_pages": len(crawl_result.unchanged_urls),
            "removed_pages": removed_count,
            "failed_pages": len(crawl_result.failed_urls),
            "articles_created": len(entry_ids),
            "articles_embedded": embedded_count,
            "total_chars": crawl_result.total_chars,
            "pages_crawled": crawl_result.pages_crawled,
        }
        logger.info(
            "Website source crawl complete: tenant=%s domain=%s %s",
            tenant_id[:8], domain, summary,
        )
        return summary

    except Exception as exc:
        logger.error(
            "Website crawl failed: tenant=%s source=%s error=%s",
            tenant_id[:8], source_id[:8], exc,
            exc_info=True,
        )
        await repo.update_website_source(
            tenant_id, source_id,
            status=WebsiteSourceStatus.FAILED.value,
            error_message=str(exc)[:500],
        )
        return {"error": str(exc)}


async def _vectorize_new_entries(
    tenant_id: str,
    entry_ids: list[str],
) -> int:
    """Batch-vectorize newly created KB entries from a crawl."""
    if not entry_ids:
        return 0

    try:
        from src.multi_tenant.knowledge_vectorizer import get_knowledge_vectorizer
        from src.multi_tenant.repositories.knowledge import KnowledgeBaseRepository

        vectorizer = get_knowledge_vectorizer()
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
                "Website crawl: vectorized %d/%d entries for tenant %s",
                count, len(entry_ids), tenant_id[:8],
            )
            return count
    except Exception:
        logger.warning(
            "Website crawl vectorization failed for tenant %s (non-fatal)",
            tenant_id[:8],
            exc_info=True,
        )
    return 0
