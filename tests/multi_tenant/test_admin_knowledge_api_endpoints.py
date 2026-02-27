"""Tests for admin_knowledge_api.py — Knowledge Base Management endpoint coverage.

Covers 16 specs: router prefix + 15 endpoint smoke tests verifying each handler
can be called with properly mocked dependencies and returns expected responses.

The admin knowledge API uses configure_admin_knowledge_services() to wire repos,
plus inline KnowledgeBaseRepository() construction for website source endpoints.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ctx() -> MagicMock:
    """Build a mock TenantContext."""
    ctx = MagicMock()
    ctx.tenant_id = "test-tenant-001"
    ctx.tier = "professional"
    ctx.user_id = "user-001"
    ctx.team_member_email = "admin@test.com"
    ctx.team_member_role = None
    ctx.team_member_id = "member-001"
    ctx.auth_method = "tenant_api_key"
    ctx.shop_domain = None
    return ctx


def _sample_entry(**overrides) -> dict[str, Any]:
    """Build a sample KB entry dict."""
    now = datetime.now(timezone.utc).isoformat()
    entry = {
        "id": "entry-001",
        "tenant_id": "test-tenant-001",
        "entry_type": "article",
        "title": "Test Article",
        "content": "This is test content for the knowledge base.",
        "metadata": {},
        "tags": ["test"],
        "language": "en",
        "is_active": True,
        "category": "General",
        "status": "published",
        "created_at": now,
        "updated_at": now,
        "staleness_score": 0.0,
        "last_verified_at": now,
    }
    entry.update(overrides)
    return entry


def _configure_kb_services(
    knowledge_repo=None,
    knowledge_vectorizer=None,
    staleness_service=None,
    conflict_scanner=None,
):
    """Wire mocks into the admin knowledge module."""
    from src.multi_tenant.admin_knowledge_api import configure_admin_knowledge_services

    configure_admin_knowledge_services(
        knowledge_repo=knowledge_repo or MagicMock(),
        knowledge_vectorizer=knowledge_vectorizer,
        staleness_service=staleness_service,
        conflict_scanner=conflict_scanner,
    )


# Patch targets
_PATCH_ACTIVATION = "src.multi_tenant.admin_knowledge_api.get_activation_service"
_PATCH_CLASSIFY = "src.multi_tenant.staleness_service.classify_staleness"


# ---------------------------------------------------------------------------
# Router prefix
# ---------------------------------------------------------------------------


class TestRouterPrefix:
    """SPEC: knowledge router prefix is /api/admin/knowledge."""

    def test_router_prefix(self):
        from src.multi_tenant.admin_knowledge_api import router

        assert router.prefix == "/api/admin/knowledge"


# ---------------------------------------------------------------------------
# GET /api/admin/knowledge — List with filtering & pagination
# ---------------------------------------------------------------------------


class TestListKnowledgeEntries:
    """SPEC: GET '' returns paginated list of KB entries."""

    @pytest.mark.asyncio
    async def test_list_entries_empty(self):
        from src.multi_tenant.admin_knowledge_api import list_knowledge_entries

        repo = MagicMock()
        repo.count_filtered = AsyncMock(return_value=0)
        repo.list_filtered = AsyncMock(return_value=[])
        _configure_kb_services(knowledge_repo=repo)

        result = await list_knowledge_entries(
            entry_type=None,
            language=None,
            is_active=None,
            search=None,
            offset=0,
            limit=50,
            ctx=_ctx(),
        )
        assert result.total_count == 0
        assert result.articles == []

    @pytest.mark.asyncio
    async def test_list_entries_with_results(self):
        from src.multi_tenant.admin_knowledge_api import list_knowledge_entries

        repo = MagicMock()
        repo.count_filtered = AsyncMock(return_value=1)
        repo.list_filtered = AsyncMock(return_value=[_sample_entry()])
        _configure_kb_services(knowledge_repo=repo)

        with patch(_PATCH_CLASSIFY, return_value="fresh"):
            result = await list_knowledge_entries(
                entry_type=None,
                language=None,
                is_active=None,
                search=None,
                offset=0,
                limit=50,
                ctx=_ctx(),
            )
        assert result.total_count == 1
        assert len(result.articles) == 1


# ---------------------------------------------------------------------------
# GET /api/admin/knowledge/export — CSV export
# ---------------------------------------------------------------------------


class TestExportKnowledgeEntries:
    """SPEC: GET /export exports KB as CSV."""

    @pytest.mark.asyncio
    async def test_export_returns_streaming_response(self):
        from src.multi_tenant.admin_knowledge_api import export_knowledge_entries

        repo = MagicMock()
        repo.list_filtered = AsyncMock(return_value=[_sample_entry()])
        _configure_kb_services(knowledge_repo=repo)

        result = await export_knowledge_entries(ctx=_ctx())
        # StreamingResponse objects have media_type
        assert result.media_type == "text/csv"


# ---------------------------------------------------------------------------
# GET /api/admin/knowledge/staleness — Staleness summary
# ---------------------------------------------------------------------------


class TestGetStalenessSummary:
    """SPEC: GET /staleness returns content staleness summary."""

    @pytest.mark.asyncio
    async def test_staleness_summary(self):
        from src.multi_tenant.admin_knowledge_api import get_staleness_summary

        staleness_svc = MagicMock()
        staleness_svc.get_summary = AsyncMock(return_value={
            "total_entries": 10,
            "avg_staleness_score": 0.2,
            "fresh_count": 8,
            "aging_count": 1,
            "stale_count": 1,
            "very_stale_count": 0,
            "needs_attention": 1,
        })
        _configure_kb_services(staleness_service=staleness_svc)

        result = await get_staleness_summary(ctx=_ctx())
        assert result.total_entries == 10
        assert result.fresh_count == 8

    @pytest.mark.asyncio
    async def test_staleness_summary_503_when_no_service(self):
        from fastapi import HTTPException

        from src.multi_tenant.admin_knowledge_api import get_staleness_summary

        _configure_kb_services(staleness_service=None)

        with pytest.raises(HTTPException) as exc_info:
            await get_staleness_summary(ctx=_ctx())
        assert exc_info.value.status_code == 503


# ---------------------------------------------------------------------------
# GET /api/admin/knowledge/stale — List stale entries
# ---------------------------------------------------------------------------


class TestListStaleEntries:
    """SPEC: GET /stale lists entries above staleness threshold."""

    @pytest.mark.asyncio
    async def test_list_stale_entries(self):
        from src.multi_tenant.admin_knowledge_api import list_stale_entries

        staleness_svc = MagicMock()
        staleness_svc.list_stale = AsyncMock(return_value=[
            {
                "id": "entry-001",
                "staleness_score": 0.8,
                "staleness_category": "stale",
            },
        ])
        _configure_kb_services(staleness_service=staleness_svc)

        result = await list_stale_entries(threshold=0.6, ctx=_ctx())
        assert result.threshold == 0.6
        assert len(result.entries) == 1


# ---------------------------------------------------------------------------
# GET /api/admin/knowledge/{entry_id} — Get single entry
# ---------------------------------------------------------------------------


class TestGetKnowledgeEntry:
    """SPEC: GET /{entry_id} returns a single KB entry."""

    @pytest.mark.asyncio
    async def test_get_entry_success(self):
        from src.multi_tenant.admin_knowledge_api import get_knowledge_entry

        repo = MagicMock()
        repo.read = AsyncMock(return_value=_sample_entry())
        _configure_kb_services(knowledge_repo=repo)

        with patch(_PATCH_CLASSIFY, return_value="fresh"):
            result = await get_knowledge_entry(entry_id="entry-001", ctx=_ctx())

        assert result.id == "entry-001"
        assert result.title == "Test Article"

    @pytest.mark.asyncio
    async def test_get_entry_not_found(self):
        from fastapi import HTTPException

        from src.multi_tenant.admin_knowledge_api import get_knowledge_entry
        from src.multi_tenant.repository import DocumentNotFoundError

        repo = MagicMock()
        repo.read = AsyncMock(side_effect=DocumentNotFoundError("knowledge_base", "nonexistent", "test-tenant-001"))
        _configure_kb_services(knowledge_repo=repo)

        with pytest.raises(HTTPException) as exc_info:
            await get_knowledge_entry(entry_id="nonexistent", ctx=_ctx())
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/admin/knowledge/{entry_id}/chunks — Chunk preview
# ---------------------------------------------------------------------------


class TestPreviewEntryChunks:
    """SPEC: GET /{entry_id}/chunks returns chunk preview."""

    @pytest.mark.asyncio
    async def test_chunk_preview(self):
        from src.multi_tenant.admin_knowledge_api import preview_entry_chunks

        repo = MagicMock()
        repo.read = AsyncMock(return_value=_sample_entry(
            content="A" * 2000,
        ))
        _configure_kb_services(knowledge_repo=repo)

        mock_chunk = MagicMock()
        mock_chunk.chunk_index = 0
        mock_chunk.title = "Test Article"
        mock_chunk.text = "A" * 500

        with patch(
            "src.multi_tenant.document_parser.chunk_text",
            return_value=[mock_chunk],
        ), patch(
            "src.multi_tenant.document_parser.CHARS_PER_TOKEN", 4,
        ), patch(
            "src.multi_tenant.document_parser.DEFAULT_CHUNK_SIZE", 400,
        ), patch(
            "src.multi_tenant.document_parser.DEFAULT_CHUNK_OVERLAP", 50,
        ):
            result = await preview_entry_chunks(
                entry_id="entry-001",
                chunk_size=None,
                chunk_overlap=None,
                ctx=_ctx(),
            )

        assert result.entry_id == "entry-001"
        assert result.total_chunks == 1


# ---------------------------------------------------------------------------
# POST /api/admin/knowledge — Create entry
# ---------------------------------------------------------------------------


class TestCreateKnowledgeEntry:
    """SPEC: POST '' creates a new KB entry."""

    @pytest.mark.asyncio
    async def test_create_entry(self):
        from src.multi_tenant.admin_knowledge_api import (
            CreateKnowledgeEntryRequest,
            create_knowledge_entry,
        )

        repo = MagicMock()
        repo.create = AsyncMock(return_value=None)
        _configure_kb_services(knowledge_repo=repo)

        body = CreateKnowledgeEntryRequest(
            title="New Article",
            content="Content goes here.",
            entry_type="article",
        )

        with (
            patch(_PATCH_CLASSIFY, return_value="fresh"),
            patch(
                "src.multi_tenant.admin_knowledge_api._signal_kb_draft",
                new_callable=AsyncMock,
            ),
        ):
            result = await create_knowledge_entry(request=body, ctx=_ctx())

        assert result.title == "New Article"
        assert result.entry_type == "article"


# ---------------------------------------------------------------------------
# PUT /api/admin/knowledge/{entry_id} — Update entry
# ---------------------------------------------------------------------------


class TestUpdateKnowledgeEntry:
    """SPEC: PUT /{entry_id} updates an existing KB entry."""

    @pytest.mark.asyncio
    async def test_update_entry(self):
        from src.multi_tenant.admin_knowledge_api import (
            UpdateKnowledgeEntryRequest,
            update_knowledge_entry,
        )

        repo = MagicMock()
        repo.read = AsyncMock(return_value=_sample_entry())
        repo.patch = AsyncMock()
        _configure_kb_services(knowledge_repo=repo)

        body = UpdateKnowledgeEntryRequest(title="Updated Title")

        with (
            patch(_PATCH_CLASSIFY, return_value="fresh"),
            patch(
                "src.multi_tenant.admin_knowledge_api._signal_kb_draft",
                new_callable=AsyncMock,
            ),
        ):
            result = await update_knowledge_entry(
                entry_id="entry-001", request=body, ctx=_ctx(),
            )

        assert result.title == "Updated Title"


# ---------------------------------------------------------------------------
# DELETE /api/admin/knowledge/{entry_id} — Soft-delete entry
# ---------------------------------------------------------------------------


class TestDeleteKnowledgeEntry:
    """SPEC: DELETE /{entry_id} soft-deletes a KB entry."""

    @pytest.mark.asyncio
    async def test_soft_delete_entry(self):
        from src.multi_tenant.admin_knowledge_api import delete_knowledge_entry

        repo = MagicMock()
        repo.soft_delete = AsyncMock()
        _configure_kb_services(knowledge_repo=repo)

        with patch(
            "src.multi_tenant.admin_knowledge_api._signal_kb_draft",
            new_callable=AsyncMock,
        ):
            result = await delete_knowledge_entry(entry_id="entry-001", ctx=_ctx())

        assert result.id == "entry-001"
        assert result.deleted_at is not None

    @pytest.mark.asyncio
    async def test_soft_delete_not_found(self):
        from fastapi import HTTPException

        from src.multi_tenant.admin_knowledge_api import delete_knowledge_entry
        from src.multi_tenant.repository import DocumentNotFoundError

        repo = MagicMock()
        repo.soft_delete = AsyncMock(side_effect=DocumentNotFoundError("knowledge_base", "nonexistent", "test-tenant-001"))
        _configure_kb_services(knowledge_repo=repo)

        with pytest.raises(HTTPException) as exc_info:
            await delete_knowledge_entry(entry_id="nonexistent", ctx=_ctx())
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/admin/knowledge/{entry_id}/verify — Mark as verified
# ---------------------------------------------------------------------------


class TestVerifyKnowledgeEntry:
    """SPEC: POST /{entry_id}/verify marks entry as verified."""

    @pytest.mark.asyncio
    async def test_verify_entry(self):
        from src.multi_tenant.admin_knowledge_api import verify_knowledge_entry

        staleness_svc = MagicMock()
        staleness_svc.verify_entry = AsyncMock(return_value={
            "id": "entry-001",
            "staleness_score": 0.0,
            "staleness_category": "fresh",
            "last_verified_at": datetime.now(timezone.utc).isoformat(),
        })
        _configure_kb_services(staleness_service=staleness_svc)

        result = await verify_knowledge_entry(entry_id="entry-001", ctx=_ctx())
        assert result.id == "entry-001"
        assert result.staleness_score == 0.0


# ---------------------------------------------------------------------------
# POST /api/admin/knowledge/scan — Trigger conflict scan
# ---------------------------------------------------------------------------


class TestScanForConflicts:
    """SPEC: POST /scan triggers a conflict/duplicate scan."""

    @pytest.mark.asyncio
    async def test_scan_503_when_no_scanner(self):
        from fastapi import HTTPException

        from src.multi_tenant.admin_knowledge_api import scan_for_conflicts

        _configure_kb_services(conflict_scanner=None)

        with pytest.raises(HTTPException) as exc_info:
            await scan_for_conflicts(force=False, ctx=_ctx())
        assert exc_info.value.status_code == 503


# ---------------------------------------------------------------------------
# GET /api/admin/knowledge/scan/result — Get cached scan result
# ---------------------------------------------------------------------------


class TestGetScanResult:
    """SPEC: GET /scan/result returns cached scan result."""

    @pytest.mark.asyncio
    async def test_scan_result_404_when_no_cache(self):
        from fastapi import HTTPException

        from src.multi_tenant.admin_knowledge_api import get_scan_result

        scanner = MagicMock()
        scanner.get_cached_result = MagicMock(return_value=None)
        _configure_kb_services(conflict_scanner=scanner)

        with pytest.raises(HTTPException) as exc_info:
            await get_scan_result(ctx=_ctx())
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# Website Sources — GET /sources
# ---------------------------------------------------------------------------


class TestListWebsiteSources:
    """SPEC: GET /sources lists website sources."""

    @pytest.mark.asyncio
    async def test_list_website_sources(self):
        from src.multi_tenant.admin_knowledge_api import list_website_sources

        mock_repo = MagicMock()
        mock_repo.list_website_sources = AsyncMock(return_value=[])

        with patch(
            "src.multi_tenant.admin_knowledge_api.KnowledgeBaseRepository",
            return_value=mock_repo,
        ):
            result = await list_website_sources(ctx=_ctx())

        assert result.tenant_id == "test-tenant-001"
        assert result.total_count == 0
        assert result.sources == []
