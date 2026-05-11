# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
Persistent Memory dashboard API — WI#139 capability.

Provides endpoints for viewing memory usage statistics, browsing stored
memory vectors, and managing memory data per customer.

Routes:
    GET    /api/admin/memory/stats             — Memory usage statistics
    GET    /api/admin/memory/customers          — List customers with memory data
    GET    /api/admin/memory/customer/{cid}     — Get memory vectors for a customer
    DELETE /api/admin/memory/customer/{cid}     — Erase all memory for a customer (GDPR)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from src.multi_tenant.middleware import TenantContext, get_tenant_context

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class MemoryStatsResponse(BaseModel):
    """Aggregate memory usage statistics for the tenant."""

    tenant_id: str
    total_vectors: int = 0
    total_customers: int = 0
    total_conversations_indexed: int = 0
    memory_enabled: bool = False
    oldest_vector_date: str | None = None
    newest_vector_date: str | None = None


class CustomerMemorySummary(BaseModel):
    """Summary of memory data for one customer."""

    customer_id: str
    vector_count: int = 0
    conversation_count: int = 0
    latest_date: str | None = None
    topics: list[str] = Field(default_factory=list)


class CustomerMemoryListResponse(BaseModel):
    """Response listing customers with memory data."""

    tenant_id: str
    customers: list[CustomerMemorySummary]
    total: int = 0


class MemoryVectorDetail(BaseModel):
    """Detail of a single memory vector."""

    id: str
    conversation_id: str
    chunk_index: int = 0
    chunk_text: str = ""
    conversation_date: str | None = None
    topics: list[str] = Field(default_factory=list)


class CustomerMemoryDetailResponse(BaseModel):
    """Detailed memory vectors for a customer."""

    tenant_id: str
    customer_id: str
    vectors: list[MemoryVectorDetail]
    total: int = 0


class MemoryDeleteResponse(BaseModel):
    """Response for memory deletion."""

    success: bool
    customer_id: str
    vectors_deleted: int = 0
    message: str = ""


# ---------------------------------------------------------------------------
# Service wiring
# ---------------------------------------------------------------------------

_memory_repo: Any = None
_prefs_repo: Any = None


def configure_memory_dashboard(
    memory_repo: Any,
    prefs_repo: Any | None = None,
) -> None:
    """Wire the memory dashboard to repositories."""
    global _memory_repo, _prefs_repo
    _memory_repo = memory_repo
    _prefs_repo = prefs_repo
    logger.info("Memory dashboard service configured")


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/admin/memory", tags=["admin-memory"])


@router.get("/stats", response_model=MemoryStatsResponse)
async def get_memory_stats(
    ctx: TenantContext = Depends(get_tenant_context),
) -> MemoryStatsResponse:
    """Get aggregate memory usage statistics for the tenant."""
    if _memory_repo is None:
        return MemoryStatsResponse(
            tenant_id=ctx.tenant_id,
            memory_enabled=False,
        )

    # Check if memory is enabled in config
    memory_enabled = False
    if _prefs_repo is not None:
        try:
            active = await _prefs_repo.get_active(ctx.tenant_id)
            if active:
                memory_enabled = bool(active.get("memory_enabled", False))
        except Exception:
            pass

    # Query memory stats
    try:
        # Count total vectors
        total_result = await _memory_repo.query(
            tenant_id=ctx.tenant_id,
            query_text="SELECT VALUE COUNT(1) FROM c",
        )
        total_vectors = total_result[0] if total_result else 0

        # Count distinct customers
        customer_result = await _memory_repo.query(
            tenant_id=ctx.tenant_id,
            query_text="SELECT DISTINCT VALUE c.customer_id FROM c",
        )
        total_customers = len(customer_result) if customer_result else 0

        # Count distinct conversations
        conv_result = await _memory_repo.query(
            tenant_id=ctx.tenant_id,
            query_text="SELECT DISTINCT VALUE c.conversation_id FROM c",
        )
        total_conversations = len(conv_result) if conv_result else 0

        # Date range
        date_result = await _memory_repo.query(
            tenant_id=ctx.tenant_id,
            query_text=(
                "SELECT VALUE MIN(c.conversation_date) FROM c"
            ),
        )
        oldest = date_result[0] if date_result and date_result[0] else None

        newest_result = await _memory_repo.query(
            tenant_id=ctx.tenant_id,
            query_text=(
                "SELECT VALUE MAX(c.conversation_date) FROM c"
            ),
        )
        newest = newest_result[0] if newest_result and newest_result[0] else None

    except Exception as exc:
        logger.warning("Failed to query memory stats: %s", exc)
        return MemoryStatsResponse(
            tenant_id=ctx.tenant_id,
            memory_enabled=memory_enabled,
        )

    return MemoryStatsResponse(
        tenant_id=ctx.tenant_id,
        total_vectors=total_vectors,
        total_customers=total_customers,
        total_conversations_indexed=total_conversations,
        memory_enabled=memory_enabled,
        oldest_vector_date=oldest,
        newest_vector_date=newest,
    )


@router.get("/customers", response_model=CustomerMemoryListResponse)
async def list_memory_customers(
    limit: int = Query(50, ge=1, le=200),
    ctx: TenantContext = Depends(get_tenant_context),
) -> CustomerMemoryListResponse:
    """List customers who have memory data stored."""
    if _memory_repo is None:
        return CustomerMemoryListResponse(
            tenant_id=ctx.tenant_id,
            customers=[],
        )

    try:
        # Get per-customer summary
        result = await _memory_repo.query(
            tenant_id=ctx.tenant_id,
            query_text=(
                "SELECT c.customer_id, COUNT(1) AS vector_count, "
                "COUNT(DISTINCT c.conversation_id) AS conv_count, "
                "MAX(c.conversation_date) AS latest_date "
                "FROM c "
                "GROUP BY c.customer_id"
            ),
        )

        customers = []
        for row in (result or [])[:limit]:
            customers.append(CustomerMemorySummary(
                customer_id=row.get("customer_id", "unknown"),
                vector_count=row.get("vector_count", 0),
                conversation_count=row.get("conv_count", 0),
                latest_date=row.get("latest_date"),
            ))

    except Exception as exc:
        logger.warning("Failed to list memory customers: %s", exc)
        customers = []

    return CustomerMemoryListResponse(
        tenant_id=ctx.tenant_id,
        customers=customers,
        total=len(customers),
    )


@router.get("/customer/{customer_id}", response_model=CustomerMemoryDetailResponse)
async def get_customer_memory(
    customer_id: str,
    limit: int = Query(100, ge=1, le=500),
    ctx: TenantContext = Depends(get_tenant_context),
) -> CustomerMemoryDetailResponse:
    """Get all memory vectors stored for a specific customer."""
    if _memory_repo is None:
        return CustomerMemoryDetailResponse(
            tenant_id=ctx.tenant_id,
            customer_id=customer_id,
            vectors=[],
        )

    try:
        result = await _memory_repo.query(
            tenant_id=ctx.tenant_id,
            query_text=(
                "SELECT c.id, c.conversation_id, c.chunk_index, "
                "c.chunk_text, c.conversation_date, c.topics "
                "FROM c "
                "WHERE c.customer_id = @cid "
                "ORDER BY c.conversation_date DESC "
                "OFFSET 0 LIMIT @limit"
            ),
            parameters=[
                {"name": "@cid", "value": customer_id},
                {"name": "@limit", "value": limit},
            ],
        )

        vectors = []
        for row in (result or []):
            vectors.append(MemoryVectorDetail(
                id=row.get("id", ""),
                conversation_id=row.get("conversation_id", ""),
                chunk_index=row.get("chunk_index", 0),
                chunk_text=row.get("chunk_text", ""),
                conversation_date=row.get("conversation_date"),
                topics=row.get("topics", []),
            ))

    except Exception as exc:
        logger.warning("Failed to get customer memory: %s", exc)
        vectors = []

    return CustomerMemoryDetailResponse(
        tenant_id=ctx.tenant_id,
        customer_id=customer_id,
        vectors=vectors,
        total=len(vectors),
    )


@router.delete("/customer/{customer_id}", response_model=MemoryDeleteResponse)
async def delete_customer_memory(
    customer_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> MemoryDeleteResponse:
    """Erase all memory vectors for a customer (GDPR compliance).

    This permanently deletes all stored memory vectors for the specified
    customer. This action cannot be undone.
    """
    if _memory_repo is None:
        raise HTTPException(
            status_code=503,
            detail="Memory service is not configured.",
        )

    try:
        count = await _memory_repo.delete_by_customer(ctx.tenant_id, customer_id)

        logger.info(
            "Memory erased: tenant=%s customer=%s vectors_deleted=%d",
            ctx.tenant_id[:8], customer_id[:8], count,
        )

        return MemoryDeleteResponse(
            success=True,
            customer_id=customer_id,
            vectors_deleted=count,
            message=f"Deleted {count} memory vectors for customer.",
        )

    except Exception as exc:
        logger.error("Failed to delete customer memory: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete memory: {str(exc)[:100]}",
        )
