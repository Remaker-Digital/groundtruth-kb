"""
Memory vector repository — memory_vectors collection (Layer 2 + vector search).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from typing import Any

from src.multi_tenant.cosmos_schema import COLLECTION_MEMORY_VECTORS
from src.multi_tenant.repositories.base import TenantScopedRepository


class MemoryVectorRepository(TenantScopedRepository):
    """Repository for the memory_vectors collection (Layer 2).

    Provides vector similarity search using Cosmos DB DiskANN index.
    """

    # SPEC-1843 / WI-1627: Fields encrypted at rest with tenant DEK
    _encryption_fields = frozenset({
        "text", "context", "summary",
    })

    def __init__(self) -> None:
        super().__init__(COLLECTION_MEMORY_VECTORS)

    async def vector_search(
        self,
        tenant_id: str,
        embedding: list[float],
        customer_id: str | None = None,
        top_k: int = 10,
        since: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search for similar memory vectors using DiskANN.

        Args:
            tenant_id: Tenant partition key.
            embedding: Query embedding (3072 dimensions).
            customer_id: Optional filter to a specific customer.
            top_k: Number of results to return.
            since: Optional date filter (ISO 8601) — only chunks
                   from conversations after this date.

        Returns:
            List of matching chunks with similarity scores, ordered
            by similarity (most similar first).
        """
        # Build WHERE clause
        conditions = ["c.tenant_id = @tenant_id"]
        params: list[dict[str, Any]] = [
            {"name": "@tenant_id", "value": tenant_id},
            {"name": "@embedding", "value": embedding},
        ]

        if customer_id:
            conditions.append("c.customer_id = @customer_id")
            params.append({"name": "@customer_id", "value": customer_id})

        if since:
            conditions.append("c.conversation_date >= @since")
            params.append({"name": "@since", "value": since})

        where_clause = " AND ".join(conditions)

        query_text = (
            f"SELECT c.id, c.customer_id, c.conversation_id, "
            f"c.chunk_text, c.chunk_index, c.conversation_date, c.topics, "
            f"VectorDistance(c.embedding, @embedding) AS similarity "
            f"FROM c "
            f"WHERE {where_clause} "
            f"ORDER BY VectorDistance(c.embedding, @embedding) "
            f"OFFSET 0 LIMIT @top_k"
        )
        params.append({"name": "@top_k", "value": top_k})

        # Vector search must use partition key for single-partition scope
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

    async def list_by_conversation(
        self, tenant_id: str, conversation_id: str,
    ) -> list[dict[str, Any]]:
        """Get all chunks for a conversation, ordered by position."""
        return await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.conversation_id = @conv_id "
                "ORDER BY c.chunk_index ASC"
            ),
            parameters=[{"name": "@conv_id", "value": conversation_id}],
        )

    async def delete_by_conversation(
        self, tenant_id: str, conversation_id: str,
    ) -> int:
        """Delete all chunks for a conversation. Returns count deleted."""
        chunks = await self.list_by_conversation(tenant_id, conversation_id)
        for chunk in chunks:
            await self.delete(tenant_id, chunk["id"])
        return len(chunks)

    async def delete_by_customer(
        self, tenant_id: str, customer_id: str,
    ) -> int:
        """Delete all vectors for a customer (GDPR erasure). Returns count."""
        chunks = await self.query(
            tenant_id=tenant_id,
            query_text="SELECT c.id FROM c WHERE c.customer_id = @cid",
            parameters=[{"name": "@cid", "value": customer_id}],
        )
        for chunk in chunks:
            await self.delete(tenant_id, chunk["id"])
        return len(chunks)
