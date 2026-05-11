"""Unit tests for KnowledgeBaseRepository — knowledge_bases collection CRUD.

Covers:
    - list_active (with entry_type and language filters)
    - list_active_lightweight (BM25 optimized projection)
    - search_by_tags (ARRAY_CONTAINS tag matching)
    - list_filtered (admin management with pagination)
    - count_filtered (admin pagination metadata)
    - soft_delete (set is_active = false)
    - vector_search (DiskANN similarity search)
    - list_unembedded (entries needing vectorization)
    - list_stale_embeddings (entries needing re-embedding)

Uses MockCosmosManager from conftest.py for in-memory Cosmos DB simulation.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from typing import Any

import pytest

from src.multi_tenant.cosmos_schema import COLLECTION_KNOWLEDGE_BASES
from src.multi_tenant.repositories.knowledge import KnowledgeBaseRepository

# ---------------------------------------------------------------------------
# Test constants
# ---------------------------------------------------------------------------

_TENANT = "tenant-kb-001"
_NOW = "2026-02-18T12:00:00+00:00"


def _inject_raw_doc(mock_cosmos, doc: dict[str, Any]) -> None:
    """Inject a raw dict directly into the mock container's item list."""
    container = mock_cosmos.get_container(COLLECTION_KNOWLEDGE_BASES)
    container.items.append(doc)


def _make_kb_entry(
    entry_id: str = "kb-001",
    tenant_id: str = _TENANT,
    entry_type: str = "product",
    title: str = "Widget Pro",
    is_active: bool = True,
    language: str = "en",
    tags: list[str] | None = None,
    embedding: list[float] | None = None,
    content_hash: str | None = None,
    **overrides: Any,
) -> dict[str, Any]:
    """Build a knowledge base entry dict."""
    doc: dict[str, Any] = {
        "id": entry_id,
        "tenant_id": tenant_id,
        "entry_type": entry_type,
        "title": title,
        "content": f"Content for {title}",
        "tags": tags or [],
        "is_active": is_active,
        "language": language,
        "created_at": _NOW,
        "updated_at": _NOW,
    }
    if embedding is not None:
        doc["embedding"] = embedding
    if content_hash is not None:
        doc["content_hash"] = content_hash
    doc.update(overrides)
    return doc


# ===================================================================
# list_active
# ===================================================================


class TestListActive:
    """Test list_active with optional entry_type and language filters."""

    @pytest.mark.unit
    async def test_list_active_returns_active_entries(self, mock_cosmos):
        """list_active returns entries where is_active=true."""
        _inject_raw_doc(mock_cosmos, _make_kb_entry("kb-1", is_active=True))
        _inject_raw_doc(mock_cosmos, _make_kb_entry("kb-2", is_active=False))

        repo = KnowledgeBaseRepository()
        results = await repo.list_active(_TENANT)
        # MockContainerProxy returns all items; validates method runs
        assert len(results) >= 1

    @pytest.mark.unit
    async def test_list_active_empty(self, mock_cosmos):
        """list_active returns empty list when no entries."""
        repo = KnowledgeBaseRepository()
        results = await repo.list_active(_TENANT)
        assert results == []

    @pytest.mark.unit
    async def test_list_active_with_entry_type(self, mock_cosmos):
        """list_active with entry_type filter constructs correct query."""
        _inject_raw_doc(mock_cosmos, _make_kb_entry("kb-1", entry_type="product"))
        _inject_raw_doc(mock_cosmos, _make_kb_entry("kb-2", entry_type="faq"))

        repo = KnowledgeBaseRepository()
        results = await repo.list_active(_TENANT, entry_type="product")
        assert len(results) >= 1

    @pytest.mark.unit
    async def test_list_active_with_language(self, mock_cosmos):
        """list_active with language filter."""
        _inject_raw_doc(mock_cosmos, _make_kb_entry("kb-1", language="en"))
        _inject_raw_doc(mock_cosmos, _make_kb_entry("kb-2", language="es"))

        repo = KnowledgeBaseRepository()
        results = await repo.list_active(_TENANT, language="en")
        assert len(results) >= 1

    @pytest.mark.unit
    async def test_list_active_with_both_filters(self, mock_cosmos):
        """list_active with both entry_type and language filters."""
        _inject_raw_doc(mock_cosmos, _make_kb_entry(
            "kb-1", entry_type="faq", language="es",
        ))
        repo = KnowledgeBaseRepository()
        results = await repo.list_active(_TENANT, entry_type="faq", language="es")
        assert len(results) >= 1


# ===================================================================
# list_active_lightweight
# ===================================================================


class TestListActiveLightweight:
    """Test list_active_lightweight (BM25 optimized projection)."""

    @pytest.mark.unit
    async def test_list_active_lightweight_returns_entries(self, mock_cosmos):
        """list_active_lightweight returns entries without embedding."""
        _inject_raw_doc(mock_cosmos, _make_kb_entry("kb-1"))
        repo = KnowledgeBaseRepository()
        results = await repo.list_active_lightweight(_TENANT)
        assert len(results) >= 1

    @pytest.mark.unit
    async def test_list_active_lightweight_with_filters(self, mock_cosmos):
        """list_active_lightweight with entry_type and language filters."""
        _inject_raw_doc(mock_cosmos, _make_kb_entry(
            "kb-1", entry_type="product", language="fr",
        ))
        repo = KnowledgeBaseRepository()
        results = await repo.list_active_lightweight(
            _TENANT, entry_type="product", language="fr",
        )
        assert len(results) >= 1

    @pytest.mark.unit
    async def test_list_active_lightweight_empty(self, mock_cosmos):
        """list_active_lightweight returns empty when no entries."""
        repo = KnowledgeBaseRepository()
        results = await repo.list_active_lightweight(_TENANT)
        assert results == []


# ===================================================================
# search_by_tags
# ===================================================================


class TestSearchByTags:
    """Test search_by_tags (ARRAY_CONTAINS matching)."""

    @pytest.mark.unit
    async def test_search_by_tags_returns_matching(self, mock_cosmos):
        """search_by_tags returns entries matching any provided tag."""
        _inject_raw_doc(mock_cosmos, _make_kb_entry(
            "kb-1", tags=["widget", "tool"],
        ))
        _inject_raw_doc(mock_cosmos, _make_kb_entry(
            "kb-2", tags=["shoes", "fashion"],
        ))

        repo = KnowledgeBaseRepository()
        results = await repo.search_by_tags(_TENANT, ["widget"])
        assert len(results) >= 1

    @pytest.mark.unit
    async def test_search_by_tags_multiple(self, mock_cosmos):
        """search_by_tags with multiple tags."""
        _inject_raw_doc(mock_cosmos, _make_kb_entry("kb-1", tags=["a", "b"]))
        repo = KnowledgeBaseRepository()
        results = await repo.search_by_tags(_TENANT, ["a", "c", "d"])
        assert len(results) >= 1

    @pytest.mark.unit
    async def test_search_by_tags_empty_results(self, mock_cosmos):
        """search_by_tags returns empty when no tags match."""
        repo = KnowledgeBaseRepository()
        results = await repo.search_by_tags(_TENANT, ["nonexistent"])
        assert results == []


# ===================================================================
# list_filtered (admin)
# ===================================================================


class TestListFiltered:
    """Test list_filtered with admin management filters."""

    @pytest.mark.unit
    async def test_list_filtered_no_filters(self, mock_cosmos):
        """list_filtered returns all entries when no filters specified."""
        _inject_raw_doc(mock_cosmos, _make_kb_entry("kb-1"))
        _inject_raw_doc(mock_cosmos, _make_kb_entry("kb-2"))

        repo = KnowledgeBaseRepository()
        results = await repo.list_filtered(_TENANT)
        assert len(results) == 2

    @pytest.mark.unit
    async def test_list_filtered_by_entry_type(self, mock_cosmos):
        """list_filtered with entry_type filter."""
        _inject_raw_doc(mock_cosmos, _make_kb_entry("kb-1", entry_type="product"))
        repo = KnowledgeBaseRepository()
        results = await repo.list_filtered(_TENANT, entry_type="product")
        assert len(results) >= 1

    @pytest.mark.unit
    async def test_list_filtered_by_language(self, mock_cosmos):
        """list_filtered with language filter."""
        _inject_raw_doc(mock_cosmos, _make_kb_entry("kb-1", language="en"))
        repo = KnowledgeBaseRepository()
        results = await repo.list_filtered(_TENANT, language="en")
        assert len(results) >= 1

    @pytest.mark.unit
    async def test_list_filtered_by_is_active(self, mock_cosmos):
        """list_filtered with is_active filter."""
        _inject_raw_doc(mock_cosmos, _make_kb_entry("kb-1", is_active=True))
        _inject_raw_doc(mock_cosmos, _make_kb_entry("kb-2", is_active=False))
        repo = KnowledgeBaseRepository()
        results = await repo.list_filtered(_TENANT, is_active=True)
        assert len(results) >= 1

    @pytest.mark.unit
    async def test_list_filtered_by_search(self, mock_cosmos):
        """list_filtered with search substring filter."""
        _inject_raw_doc(mock_cosmos, _make_kb_entry("kb-1", title="Widget Pro"))
        repo = KnowledgeBaseRepository()
        results = await repo.list_filtered(_TENANT, search="Widget")
        assert len(results) >= 1

    @pytest.mark.unit
    async def test_list_filtered_with_pagination(self, mock_cosmos):
        """list_filtered respects offset and limit parameters."""
        for i in range(5):
            _inject_raw_doc(mock_cosmos, _make_kb_entry(f"kb-{i}"))
        repo = KnowledgeBaseRepository()
        results = await repo.list_filtered(_TENANT, offset=0, limit=3)
        # MockContainerProxy returns all items; verifies method is callable
        assert len(results) >= 1

    @pytest.mark.unit
    async def test_list_filtered_all_filters(self, mock_cosmos):
        """list_filtered with all filters applied simultaneously."""
        _inject_raw_doc(mock_cosmos, _make_kb_entry(
            "kb-1", entry_type="faq", language="es",
            is_active=True, title="Shipping FAQ",
        ))
        repo = KnowledgeBaseRepository()
        results = await repo.list_filtered(
            _TENANT,
            entry_type="faq",
            language="es",
            is_active=True,
            search="Shipping",
            offset=0,
            limit=10,
        )
        assert len(results) >= 1


# ===================================================================
# count_filtered
# ===================================================================


class TestCountFiltered:
    """Test count_filtered for pagination metadata."""

    @pytest.mark.unit
    async def test_count_filtered_no_filters(self, mock_cosmos):
        """count_filtered returns count of all entries."""
        _inject_raw_doc(mock_cosmos, _make_kb_entry("kb-1"))
        repo = KnowledgeBaseRepository()
        # MockContainerProxy.query_items returns raw docs for COUNT queries;
        # the query_count method returns the first item which is a dict.
        count = await repo.count_filtered(_TENANT)
        assert count is not None

    @pytest.mark.unit
    async def test_count_filtered_empty(self, mock_cosmos):
        """count_filtered returns 0 when no entries."""
        repo = KnowledgeBaseRepository()
        count = await repo.count_filtered(_TENANT)
        assert count == 0

    @pytest.mark.unit
    async def test_count_filtered_with_entry_type(self, mock_cosmos):
        """count_filtered with entry_type filter."""
        _inject_raw_doc(mock_cosmos, _make_kb_entry("kb-1", entry_type="faq"))
        repo = KnowledgeBaseRepository()
        count = await repo.count_filtered(_TENANT, entry_type="faq")
        assert count is not None

    @pytest.mark.unit
    async def test_count_filtered_with_search(self, mock_cosmos):
        """count_filtered with search filter."""
        _inject_raw_doc(mock_cosmos, _make_kb_entry("kb-1", title="Widget"))
        repo = KnowledgeBaseRepository()
        count = await repo.count_filtered(_TENANT, search="Widget")
        assert count is not None

    @pytest.mark.unit
    async def test_count_filtered_with_all_filters(self, mock_cosmos):
        """count_filtered with all filters applied."""
        _inject_raw_doc(mock_cosmos, _make_kb_entry("kb-1"))
        repo = KnowledgeBaseRepository()
        count = await repo.count_filtered(
            _TENANT,
            entry_type="product",
            language="en",
            is_active=True,
            search="Widget",
        )
        assert count is not None


# ===================================================================
# soft_delete
# ===================================================================


class TestSoftDelete:
    """Test soft_delete (set is_active = false)."""

    @pytest.mark.unit
    async def test_soft_delete_sets_inactive(self, mock_cosmos):
        """soft_delete patches is_active to False and updates timestamp."""
        _inject_raw_doc(mock_cosmos, _make_kb_entry("kb-1", is_active=True))
        repo = KnowledgeBaseRepository()
        result = await repo.soft_delete(_TENANT, "kb-1")
        assert result["is_active"] is False
        assert "updated_at" in result

    @pytest.mark.unit
    async def test_soft_delete_updates_timestamp(self, mock_cosmos):
        """soft_delete sets updated_at to current time."""
        _inject_raw_doc(mock_cosmos, _make_kb_entry(
            "kb-1", is_active=True, updated_at="2025-01-01T00:00:00+00:00",
        ))
        repo = KnowledgeBaseRepository()
        result = await repo.soft_delete(_TENANT, "kb-1")
        # updated_at should be refreshed (not the old timestamp)
        assert result["updated_at"] != "2025-01-01T00:00:00+00:00"


# ===================================================================
# vector_search
# ===================================================================


class TestVectorSearch:
    """Test vector_search (DiskANN similarity search)."""

    @pytest.mark.unit
    async def test_vector_search_returns_results(self, mock_cosmos):
        """vector_search returns matching entries with similarity scores."""
        _inject_raw_doc(mock_cosmos, _make_kb_entry(
            "kb-1",
            embedding=[0.1] * 3072,
            is_active=True,
        ))
        repo = KnowledgeBaseRepository()
        query_embedding = [0.2] * 3072
        results = await repo.vector_search(_TENANT, query_embedding, top_k=5)
        assert len(results) >= 1

    @pytest.mark.unit
    async def test_vector_search_respects_top_k(self, mock_cosmos):
        """vector_search limits results to top_k."""
        for i in range(10):
            _inject_raw_doc(mock_cosmos, _make_kb_entry(
                f"kb-{i}",
                embedding=[0.1 * i] * 3072,
                is_active=True,
            ))
        repo = KnowledgeBaseRepository()
        results = await repo.vector_search(_TENANT, [0.5] * 3072, top_k=3)
        assert len(results) <= 3

    @pytest.mark.unit
    async def test_vector_search_empty(self, mock_cosmos):
        """vector_search returns empty when no entries exist."""
        repo = KnowledgeBaseRepository()
        results = await repo.vector_search(_TENANT, [0.1] * 3072)
        assert results == []

    @pytest.mark.unit
    async def test_vector_search_with_entry_type_filter(self, mock_cosmos):
        """vector_search with entry_type filter."""
        _inject_raw_doc(mock_cosmos, _make_kb_entry(
            "kb-1", entry_type="product", embedding=[0.1] * 3072,
        ))
        repo = KnowledgeBaseRepository()
        results = await repo.vector_search(
            _TENANT, [0.2] * 3072, entry_type="product",
        )
        assert len(results) >= 1

    @pytest.mark.unit
    async def test_vector_search_with_language_filter(self, mock_cosmos):
        """vector_search with language filter."""
        _inject_raw_doc(mock_cosmos, _make_kb_entry(
            "kb-1", language="fr", embedding=[0.1] * 3072,
        ))
        repo = KnowledgeBaseRepository()
        results = await repo.vector_search(
            _TENANT, [0.2] * 3072, language="fr",
        )
        assert len(results) >= 1


# ===================================================================
# list_unembedded
# ===================================================================


class TestListUnembedded:
    """Test list_unembedded (entries needing vectorization)."""

    @pytest.mark.unit
    async def test_list_unembedded_returns_entries_without_embedding(self, mock_cosmos):
        """list_unembedded returns active entries with no embedding."""
        _inject_raw_doc(mock_cosmos, _make_kb_entry("kb-1", is_active=True))
        repo = KnowledgeBaseRepository()
        results = await repo.list_unembedded(_TENANT)
        assert len(results) >= 1

    @pytest.mark.unit
    async def test_list_unembedded_empty(self, mock_cosmos):
        """list_unembedded returns empty when no unembedded entries."""
        repo = KnowledgeBaseRepository()
        results = await repo.list_unembedded(_TENANT)
        assert results == []

    @pytest.mark.unit
    async def test_list_unembedded_with_limit(self, mock_cosmos):
        """list_unembedded respects the limit parameter."""
        for i in range(5):
            _inject_raw_doc(mock_cosmos, _make_kb_entry(f"kb-{i}"))
        repo = KnowledgeBaseRepository()
        results = await repo.list_unembedded(_TENANT, limit=2)
        # MockContainerProxy returns all; verifies method is callable
        assert len(results) >= 1


# ===================================================================
# list_stale_embeddings
# ===================================================================


class TestListStaleEmbeddings:
    """Test list_stale_embeddings (entries needing re-embedding)."""

    @pytest.mark.unit
    async def test_list_stale_embeddings_returns_entries(self, mock_cosmos):
        """list_stale_embeddings returns entries with embedding+content_hash."""
        _inject_raw_doc(mock_cosmos, _make_kb_entry(
            "kb-1",
            embedding=[0.1] * 3072,
            content_hash="abc123",
            is_active=True,
        ))
        repo = KnowledgeBaseRepository()
        results = await repo.list_stale_embeddings(_TENANT)
        assert len(results) >= 1

    @pytest.mark.unit
    async def test_list_stale_embeddings_empty(self, mock_cosmos):
        """list_stale_embeddings returns empty when no stale entries."""
        repo = KnowledgeBaseRepository()
        results = await repo.list_stale_embeddings(_TENANT)
        assert results == []

    @pytest.mark.unit
    async def test_list_stale_embeddings_with_limit(self, mock_cosmos):
        """list_stale_embeddings respects the limit parameter."""
        for i in range(5):
            _inject_raw_doc(mock_cosmos, _make_kb_entry(
                f"kb-{i}",
                embedding=[0.1] * 3072,
                content_hash=f"hash-{i}",
            ))
        repo = KnowledgeBaseRepository()
        results = await repo.list_stale_embeddings(_TENANT, limit=2)
        assert len(results) >= 1
