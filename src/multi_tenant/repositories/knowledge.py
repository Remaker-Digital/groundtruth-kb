"""
Knowledge base repository — knowledge_bases collection (product/FAQ data).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.multi_tenant.cosmos_schema import COLLECTION_KNOWLEDGE_BASES
from src.multi_tenant.repositories.base import TenantScopedRepository


class KnowledgeBaseRepository(TenantScopedRepository):
    """Repository for the knowledge_bases collection."""

    # SPEC-1843 / WI-1627: Fields encrypted at rest with tenant DEK
    _encryption_fields = frozenset({
        "content", "title", "description", "source_text",
    })

    def __init__(self) -> None:
        super().__init__(COLLECTION_KNOWLEDGE_BASES)

    async def list_active(
        self,
        tenant_id: str,
        entry_type: str | None = None,
        language: str | None = None,
    ) -> list[dict[str, Any]]:
        """List active knowledge base entries, optionally filtered."""
        query_text = "SELECT * FROM c WHERE c.is_active = true"
        params: list[dict[str, Any]] = []

        if entry_type:
            query_text += " AND c.entry_type = @type"
            params.append({"name": "@type", "value": entry_type})

        if language:
            query_text += " AND c.language = @lang"
            params.append({"name": "@lang", "value": language})

        return await self.query(tenant_id, query_text, params)

    async def list_active_lightweight(
        self,
        tenant_id: str,
        entry_type: str | None = None,
        language: str | None = None,
    ) -> list[dict[str, Any]]:
        """List active KB entries excluding the embedding field.

        Used by BM25 scoring which only needs id, title, content, and tags.
        Excludes the 3072-float embedding array to reduce Cosmos DB response
        payload (~24KB savings per entry).
        """
        query_text = (
            "SELECT c.id, c.tenant_id, c.title, c.content, c.tags, "
            "c.entry_type, c.language, c.metadata, c.source_type, "
            "c.content_hash, c.is_active "
            "FROM c WHERE c.is_active = true"
        )
        params: list[dict[str, Any]] = []

        if entry_type:
            query_text += " AND c.entry_type = @type"
            params.append({"name": "@type", "value": entry_type})

        if language:
            query_text += " AND c.language = @lang"
            params.append({"name": "@lang", "value": language})

        return await self.query(tenant_id, query_text, params)

    async def search_by_tags(
        self, tenant_id: str, tags: list[str],
    ) -> list[dict[str, Any]]:
        """Find entries matching any of the given tags."""
        # ARRAY_CONTAINS with OR logic for each tag
        conditions = " OR ".join(
            f"ARRAY_CONTAINS(c.tags, @tag{i})" for i in range(len(tags))
        )
        params = [
            {"name": f"@tag{i}", "value": tag} for i, tag in enumerate(tags)
        ]

        return await self.query(
            tenant_id=tenant_id,
            query_text=f"SELECT * FROM c WHERE c.is_active = true AND ({conditions})",
            parameters=params,
        )

    # --- Admin knowledge base queries (WI #175) ---

    async def list_filtered(
        self,
        tenant_id: str,
        *,
        entry_type: str | None = None,
        language: str | None = None,
        is_active: bool | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """List knowledge base entries with filters for admin management.

        Args:
            tenant_id: Tenant partition key.
            entry_type: Filter by type (product, faq, policy, custom).
            language: Filter by language code.
            is_active: Filter by active status (None = all).
            search: Substring search on title (case-insensitive via CONTAINS).
            offset: Pagination offset.
            limit: Page size.
        """
        conditions: list[str] = []
        params: list[dict[str, Any]] = []

        if entry_type is not None:
            conditions.append("c.entry_type = @entry_type")
            params.append({"name": "@entry_type", "value": entry_type})

        if language is not None:
            conditions.append("c.language = @language")
            params.append({"name": "@language", "value": language})

        if is_active is not None:
            conditions.append("c.is_active = @is_active")
            params.append({"name": "@is_active", "value": is_active})

        if search is not None:
            conditions.append(
                "(CONTAINS(LOWER(c.title), LOWER(@search))"
                " OR CONTAINS(LOWER(IS_DEFINED(c.content) ? c.content : ''), LOWER(@search)))"
            )
            params.append({"name": "@search", "value": search})

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        params.append({"name": "@offset", "value": offset})
        params.append({"name": "@limit", "value": limit})

        query_text = (
            f"SELECT * FROM c WHERE {where_clause} "
            "ORDER BY c.updated_at DESC "
            "OFFSET @offset LIMIT @limit"
        )

        return await self.query(tenant_id, query_text, params)

    async def count_filtered(
        self,
        tenant_id: str,
        *,
        entry_type: str | None = None,
        language: str | None = None,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> int:
        """Count knowledge base entries matching filters (for pagination)."""
        conditions: list[str] = []
        params: list[dict[str, Any]] = []

        if entry_type is not None:
            conditions.append("c.entry_type = @entry_type")
            params.append({"name": "@entry_type", "value": entry_type})

        if language is not None:
            conditions.append("c.language = @language")
            params.append({"name": "@language", "value": language})

        if is_active is not None:
            conditions.append("c.is_active = @is_active")
            params.append({"name": "@is_active", "value": is_active})

        if search is not None:
            conditions.append(
                "(CONTAINS(LOWER(c.title), LOWER(@search))"
                " OR CONTAINS(LOWER(IS_DEFINED(c.content) ? c.content : ''), LOWER(@search)))"
            )
            params.append({"name": "@search", "value": search})

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query_text = f"SELECT VALUE COUNT(1) FROM c WHERE {where_clause}"

        return await self.query_count(tenant_id, query_text, params)

    async def soft_delete(
        self,
        tenant_id: str,
        document_id: str,
    ) -> dict[str, Any]:
        """Soft-delete a knowledge base entry (set is_active = false)."""
        now = datetime.now(timezone.utc).isoformat()
        return await self.patch(
            tenant_id=tenant_id,
            document_id=document_id,
            operations=[
                {"op": "set", "path": "/is_active", "value": False},
                {"op": "set", "path": "/updated_at", "value": now},
            ],
        )

    # --- Vector search (WI #211) ---

    async def vector_search(
        self,
        tenant_id: str,
        embedding: list[float],
        *,
        top_k: int = 5,
        entry_type: str | None = None,
        language: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search KB entries by vector similarity using DiskANN.

        Args:
            tenant_id: Tenant partition key.
            embedding: Query embedding (3072 dimensions).
            top_k: Number of results to return.
            entry_type: Optional filter by entry type.
            language: Optional filter by language.

        Returns:
            List of matching entries with similarity scores, ordered
            by similarity (most similar first). Only returns active
            entries with embeddings.
        """
        conditions = [
            "c.tenant_id = @tenant_id",
            "c.is_active = true",
            "c.embedding != null",
        ]
        params: list[dict[str, Any]] = [
            {"name": "@tenant_id", "value": tenant_id},
            {"name": "@embedding", "value": embedding},
        ]

        if entry_type:
            conditions.append("c.entry_type = @entry_type")
            params.append({"name": "@entry_type", "value": entry_type})

        if language:
            conditions.append("c.language = @language")
            params.append({"name": "@language", "value": language})

        where_clause = " AND ".join(conditions)

        query_text = (
            f"SELECT c.id, c.tenant_id, c.entry_type, c.title, c.content, "
            f"c.metadata, c.tags, c.language, c.source_type, "
            f"VectorDistance(c.embedding, @embedding) AS similarity "
            f"FROM c "
            f"WHERE {where_clause} "
            f"ORDER BY VectorDistance(c.embedding, @embedding) "
            f"OFFSET 0 LIMIT @top_k"
        )
        params.append({"name": "@top_k", "value": top_k})

        items: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query=query_text,
            parameters=params,
            partition_key=tenant_id,
        ):
            items.append(item)
            if len(items) >= top_k:
                break

        return items

    async def list_unembedded(
        self,
        tenant_id: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """List active entries that have no embedding yet.

        Used by the background embedding pipeline to find entries
        that need vectorization.
        """
        return await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.is_active = true "
                "AND (NOT IS_DEFINED(c.embedding) OR c.embedding = null) "
                "OFFSET 0 LIMIT @limit"
            ),
            parameters=[{"name": "@limit", "value": limit}],
        )

    async def list_stale_embeddings(
        self,
        tenant_id: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """List entries whose content has changed since last embedding.

        Compares current content_hash against stored content_hash to
        detect entries that need re-embedding.
        """
        return await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.is_active = true "
                "AND c.embedding != null "
                "AND c.content_hash != null "
                "ORDER BY c.updated_at DESC "
                "OFFSET 0 LIMIT @limit"
            ),
            parameters=[{"name": "@limit", "value": limit}],
        )

    # --- Website source management ---

    async def list_website_sources(
        self,
        tenant_id: str,
    ) -> list[dict[str, Any]]:
        """List active website sources for a tenant."""
        return await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.doc_type = 'website_source' "
                "AND c.is_active = true "
                "ORDER BY c.created_at DESC"
            ),
        )

    async def count_website_sources(
        self,
        tenant_id: str,
    ) -> int:
        """Count active website sources for tier-limit enforcement."""
        return await self.query_count(
            tenant_id=tenant_id,
            query_text=(
                "SELECT VALUE COUNT(1) FROM c "
                "WHERE c.doc_type = 'website_source' "
                "AND c.is_active = true"
            ),
        )

    async def get_source_by_domain(
        self,
        tenant_id: str,
        domain: str,
    ) -> dict[str, Any] | None:
        """Find an active website source by domain (duplicate check)."""
        results = await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.doc_type = 'website_source' "
                "AND c.domain = @domain "
                "AND c.is_active = true"
            ),
            parameters=[{"name": "@domain", "value": domain}],
            max_items=1,
        )
        return results[0] if results else None

    async def update_website_source(
        self,
        tenant_id: str,
        source_id: str,
        **fields: Any,
    ) -> dict[str, Any]:
        """Patch specific fields on a website source document."""
        now = datetime.now(timezone.utc).isoformat()
        operations = [
            {"op": "set", "path": f"/{key}", "value": value}
            for key, value in fields.items()
        ]
        operations.append({"op": "set", "path": "/updated_at", "value": now})
        return await self.patch(
            tenant_id=tenant_id,
            document_id=source_id,
            operations=operations,
        )

    async def soft_delete_website_source(
        self,
        tenant_id: str,
        source_id: str,
    ) -> dict[str, Any]:
        """Soft-delete a website source (set is_active = false)."""
        return await self.update_website_source(
            tenant_id, source_id, is_active=False, status="paused",
        )

    async def list_kb_entries_by_source(
        self,
        tenant_id: str,
        domain: str,
    ) -> list[dict[str, Any]]:
        """List KB entries created by website crawl for a given domain.

        Used during re-crawl to build the content_hash map for
        incremental change detection (skip unchanged pages).

        Returns lightweight projection: id, source_url, content_hash.
        """
        return await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT c.id, c.source_url, c.content_hash, c.is_active "
                "FROM c "
                "WHERE c.source_type = 'website_crawl' "
                "AND c.is_active = true "
                "AND CONTAINS(c.source_url, @domain)"
            ),
            parameters=[{"name": "@domain", "value": domain}],
        )

    async def soft_delete_kb_entries_by_source(
        self,
        tenant_id: str,
        domain: str,
    ) -> int:
        """Soft-delete all KB entries from a website crawl source.

        Used when deleting a website source to cascade-remove its entries.
        Returns the number of entries soft-deleted.
        """
        entries = await self.list_kb_entries_by_source(tenant_id, domain)
        count = 0
        for entry in entries:
            if entry.get("is_active"):
                await self.soft_delete(tenant_id, entry["id"])
                count += 1
        return count

    async def list_sources_due_for_crawl(
        self,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Find website sources across all tenants that are due for re-crawl.

        Cross-partition query used by the background refresh scheduler.
        Filters: auto_refresh enabled, not currently crawling, past due.
        """
        now = datetime.now(timezone.utc).isoformat()
        return await self.cross_partition_query(
            query_text=(
                "SELECT * FROM c "
                "WHERE c.doc_type = 'website_source' "
                "AND c.is_active = true "
                "AND c.auto_refresh = true "
                "AND c.status != 'crawling' "
                "AND (c.next_crawl_at = null OR c.next_crawl_at <= @now) "
                "OFFSET 0 LIMIT @limit"
            ),
            parameters=[
                {"name": "@now", "value": now},
                {"name": "@limit", "value": limit},
            ],
        )
