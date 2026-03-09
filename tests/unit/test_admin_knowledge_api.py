"""Tests for admin knowledge base API — coverage expansion.

Covers: list, get, create, update, delete, export, upload, URL import,
staleness endpoints, chunk preview, and conflict scan.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.admin_knowledge_api import (
    VALID_ENTRY_TYPES,
    ChunkPreviewResponse,
    DeleteKnowledgeEntryResponse,
    KnowledgeEntryResponse,
    KnowledgeListResponse,
    ScanResultResponse,
    StaleEntriesResponse,
    StalenessSummaryResponse,
    UploadResultResponse,
    _build_entry_response,
    _get_repo,
    _signal_kb_draft,
    configure_admin_knowledge_services,
    router,
)
from src.multi_tenant.repository import DocumentNotFoundError

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_NOW = datetime.now(timezone.utc).isoformat()


def _make_entry(
    entry_id: str = "entry-001",
    title: str = "Test Article",
    entry_type: str = "article",
    content: str = "Some test content for the KB entry.",
    staleness_score: float | None = None,
    **overrides,
) -> dict:
    base = {
        "id": entry_id,
        "tenant_id": "tenant-001",
        "entry_type": entry_type,
        "title": title,
        "content": content,
        "metadata": {},
        "tags": ["test"],
        "language": "en",
        "is_active": True,
        "category": None,
        "status": "draft",
        "created_at": _NOW,
        "updated_at": _NOW,
        "staleness_score": staleness_score,
        "last_verified_at": None,
        "embedded_at": None,
        "source_type": None,
        "source_filename": None,
        "source_url": None,
    }
    base.update(overrides)
    return base


@pytest.fixture
def mock_ctx():
    ctx = MagicMock()
    ctx.tenant_id = "tenant-001"
    ctx.tier = "professional"
    ctx.user_id = "admin-user-001"
    ctx.shop_domain = None
    ctx.auth_method = "api_key"
    return ctx


@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.list_filtered = AsyncMock(return_value=[])
    repo.count_filtered = AsyncMock(return_value=0)
    repo.read = AsyncMock(return_value=_make_entry())
    repo.create = AsyncMock(return_value=_make_entry())
    repo.upsert = AsyncMock(return_value=_make_entry())
    repo.soft_delete = AsyncMock()
    repo.patch = AsyncMock()
    return repo


# ---------------------------------------------------------------------------
# Unit tests: _get_repo
# ---------------------------------------------------------------------------


class TestGetRepo:
    def test_raises_503_when_not_configured(self):
        import src.multi_tenant.admin_knowledge_api as mod

        original = mod._knowledge_repo
        mod._knowledge_repo = None
        try:
            from fastapi import HTTPException

            with pytest.raises(HTTPException) as exc_info:
                _get_repo()
            assert exc_info.value.status_code == 503
        finally:
            mod._knowledge_repo = original

    def test_returns_repo_when_configured(self, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        original = mod._knowledge_repo
        mod._knowledge_repo = mock_repo
        try:
            assert _get_repo() is mock_repo
        finally:
            mod._knowledge_repo = original


# ---------------------------------------------------------------------------
# Unit tests: configure_admin_knowledge_services
# ---------------------------------------------------------------------------


class TestConfigureServices:
    def test_configure_sets_all_globals(self, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        vec = MagicMock()
        stale = MagicMock()
        scanner = MagicMock()
        configure_admin_knowledge_services(mock_repo, vec, stale, scanner)
        assert mod._knowledge_repo is mock_repo
        assert mod._knowledge_vectorizer is vec
        assert mod._staleness_service is stale
        assert mod._conflict_scanner is scanner

    def test_configure_without_optional_services(self, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        configure_admin_knowledge_services(mock_repo)
        assert mod._knowledge_repo is mock_repo
        assert mod._knowledge_vectorizer is None


# ---------------------------------------------------------------------------
# Unit tests: _build_entry_response
# ---------------------------------------------------------------------------


class TestBuildEntryResponse:
    @patch("src.multi_tenant.staleness_service.classify_staleness")
    def test_builds_response_with_staleness(self, mock_classify):
        mock_classify.return_value = "aging"
        entry = _make_entry(staleness_score=0.4)
        resp = _build_entry_response(entry, "tenant-001")
        assert isinstance(resp, KnowledgeEntryResponse)
        assert resp.staleness_score == 0.4
        assert resp.staleness_category == "aging"
        mock_classify.assert_called_once_with(0.4)

    @patch("src.multi_tenant.staleness_service.compute_staleness_score")
    @patch("src.multi_tenant.staleness_service.classify_staleness")
    def test_builds_response_without_staleness(self, mock_classify, mock_compute):
        """When staleness_score is not persisted, compute on-the-fly."""
        mock_compute.return_value = 0.15
        mock_classify.return_value = "fresh"
        entry = _make_entry(staleness_score=None)
        resp = _build_entry_response(entry, "tenant-001")
        # Score is now computed on-the-fly instead of being None
        assert resp.staleness_score == 0.15
        assert resp.staleness_category == "fresh"
        mock_compute.assert_called_once_with(entry)
        mock_classify.assert_called_once_with(0.15)

    @patch("src.multi_tenant.staleness_service.compute_staleness_score", return_value=0.5)
    @patch("src.multi_tenant.staleness_service.classify_staleness", return_value="aging")
    def test_defaults_for_missing_fields(self, mock_classify, mock_compute):
        """Minimal dict still produces a valid response."""
        resp = _build_entry_response({"id": "x", "created_at": _NOW, "updated_at": _NOW}, "t")
        assert resp.id == "x"
        assert resp.entry_type == "custom"
        assert resp.title == ""
        assert resp.language == "en"


# ---------------------------------------------------------------------------
# Unit tests: _signal_kb_draft
# ---------------------------------------------------------------------------


class TestSignalKbDraft:
    @pytest.mark.asyncio
    async def test_signal_succeeds(self, mock_ctx):
        with patch("src.multi_tenant.admin_knowledge_api.get_activation_service") as mock_get:
            mock_svc = MagicMock()
            mock_svc.ensure_draft_for_signal = AsyncMock()
            mock_get.return_value = mock_svc
            with patch("src.multi_tenant.cosmos_schema.TenantTier", return_value="professional"):
                await _signal_kb_draft(mock_ctx)
            mock_svc.ensure_draft_for_signal.assert_called_once()

    @pytest.mark.asyncio
    async def test_signal_failure_is_non_blocking(self, mock_ctx):
        with patch("src.multi_tenant.admin_knowledge_api.get_activation_service") as mock_get:
            mock_get.side_effect = RuntimeError("activation service down")
            # Should not raise
            await _signal_kb_draft(mock_ctx)


# ---------------------------------------------------------------------------
# Unit tests: list_knowledge_entries
# ---------------------------------------------------------------------------


class TestListKnowledgeEntries:
    @pytest.mark.asyncio
    async def test_list_returns_paginated_results(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo
        mock_repo.count_filtered.return_value = 2
        mock_repo.list_filtered.return_value = [
            _make_entry("e1", "Title 1"),
            _make_entry("e2", "Title 2"),
        ]

        from src.multi_tenant.admin_knowledge_api import list_knowledge_entries

        with patch("src.multi_tenant.staleness_service.classify_staleness", return_value=None):
            result = await list_knowledge_entries(
                entry_type=None, language=None, is_active=None,
                search=None, offset=0, limit=50, ctx=mock_ctx,
            )

        assert isinstance(result, KnowledgeListResponse)
        assert result.total_count == 2
        assert len(result.articles) == 2
        assert result.offset == 0
        assert result.limit == 50

    @pytest.mark.asyncio
    async def test_list_filters_by_entry_type(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo

        from src.multi_tenant.admin_knowledge_api import list_knowledge_entries

        with patch("src.multi_tenant.staleness_service.classify_staleness", return_value=None):
            result = await list_knowledge_entries(
                entry_type="faq", language=None, is_active=None,
                search=None, offset=0, limit=50, ctx=mock_ctx,
            )

        mock_repo.list_filtered.assert_called_once()
        call_kwargs = mock_repo.list_filtered.call_args.kwargs
        assert call_kwargs["entry_type"] == "faq"

    @pytest.mark.asyncio
    async def test_list_rejects_invalid_entry_type(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo

        from fastapi import HTTPException

        from src.multi_tenant.admin_knowledge_api import list_knowledge_entries

        with pytest.raises(HTTPException) as exc_info:
            await list_knowledge_entries(
                entry_type="bogus", language=None, is_active=None,
                search=None, offset=0, limit=50, ctx=mock_ctx,
            )

        assert exc_info.value.status_code == 400
        assert "Invalid entry_type" in exc_info.value.detail


# ---------------------------------------------------------------------------
# Unit tests: get_knowledge_entry
# ---------------------------------------------------------------------------


class TestGetKnowledgeEntry:
    @pytest.mark.asyncio
    async def test_get_existing_entry(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo

        from src.multi_tenant.admin_knowledge_api import get_knowledge_entry

        with patch("src.multi_tenant.staleness_service.classify_staleness", return_value=None):
            result = await get_knowledge_entry("entry-001", ctx=mock_ctx)

        assert isinstance(result, KnowledgeEntryResponse)
        assert result.id == "entry-001"

    @pytest.mark.asyncio
    async def test_get_nonexistent_entry_returns_404(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo
        mock_repo.read.side_effect = DocumentNotFoundError("kb", "missing", "tenant-001")

        from fastapi import HTTPException

        from src.multi_tenant.admin_knowledge_api import get_knowledge_entry

        with pytest.raises(HTTPException) as exc_info:
            await get_knowledge_entry("missing", ctx=mock_ctx)

        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# Unit tests: create_knowledge_entry
# ---------------------------------------------------------------------------


class TestCreateKnowledgeEntry:
    @pytest.mark.asyncio
    async def test_create_valid_entry(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo
        mod._knowledge_vectorizer = None

        from src.multi_tenant.admin_knowledge_api import (
            CreateKnowledgeEntryRequest,
            create_knowledge_entry,
        )

        request = CreateKnowledgeEntryRequest(
            entry_type="faq",
            title="How do returns work?",
            content="Return within 30 days for a full refund.",
        )

        with (
            patch("src.multi_tenant.admin_knowledge_api._signal_kb_draft", new_callable=AsyncMock),
            patch("src.multi_tenant.staleness_service.classify_staleness", return_value=None),
            patch("src.multi_tenant.cosmos_schema.KnowledgeBaseDocument"),
        ):
            result = await create_knowledge_entry(request=request, ctx=mock_ctx)

        assert isinstance(result, KnowledgeEntryResponse)
        assert result.title == "How do returns work?"
        mock_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_invalid_entry_type(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo

        from fastapi import HTTPException

        from src.multi_tenant.admin_knowledge_api import (
            CreateKnowledgeEntryRequest,
            create_knowledge_entry,
        )

        request = CreateKnowledgeEntryRequest(
            entry_type="invalid_type",
            title="Test",
            content="Test content",
        )

        with pytest.raises(HTTPException) as exc_info:
            await create_knowledge_entry(request=request, ctx=mock_ctx)

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_create_triggers_vectorizer(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo
        vec = MagicMock()
        vec.embed_entry = AsyncMock()
        mod._knowledge_vectorizer = vec

        from src.multi_tenant.admin_knowledge_api import (
            CreateKnowledgeEntryRequest,
            create_knowledge_entry,
        )

        request = CreateKnowledgeEntryRequest(
            entry_type="article",
            title="Vectorized Article",
            content="Content to embed.",
        )

        with (
            patch("src.multi_tenant.admin_knowledge_api._signal_kb_draft", new_callable=AsyncMock),
            patch("src.multi_tenant.staleness_service.classify_staleness", return_value=None),
            patch("src.multi_tenant.cosmos_schema.KnowledgeBaseDocument"),
        ):
            await create_knowledge_entry(request=request, ctx=mock_ctx)

        vec.embed_entry.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_vectorizer_failure_non_blocking(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo
        vec = MagicMock()
        vec.embed_entry = AsyncMock(side_effect=RuntimeError("embedding failed"))
        mod._knowledge_vectorizer = vec

        from src.multi_tenant.admin_knowledge_api import (
            CreateKnowledgeEntryRequest,
            create_knowledge_entry,
        )

        request = CreateKnowledgeEntryRequest(
            entry_type="article",
            title="Test",
            content="Content",
        )

        # Should not raise
        with (
            patch("src.multi_tenant.admin_knowledge_api._signal_kb_draft", new_callable=AsyncMock),
            patch("src.multi_tenant.staleness_service.classify_staleness", return_value=None),
            patch("src.multi_tenant.cosmos_schema.KnowledgeBaseDocument"),
        ):
            result = await create_knowledge_entry(request=request, ctx=mock_ctx)

        assert isinstance(result, KnowledgeEntryResponse)


# ---------------------------------------------------------------------------
# Unit tests: update_knowledge_entry
# ---------------------------------------------------------------------------


class TestUpdateKnowledgeEntry:
    @pytest.mark.asyncio
    async def test_update_partial_fields(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo
        mod._knowledge_vectorizer = None

        from src.multi_tenant.admin_knowledge_api import (
            UpdateKnowledgeEntryRequest,
            update_knowledge_entry,
        )

        request = UpdateKnowledgeEntryRequest(title="Updated Title")

        with (
            patch("src.multi_tenant.admin_knowledge_api._signal_kb_draft", new_callable=AsyncMock),
            patch("src.multi_tenant.staleness_service.classify_staleness", return_value=None),
        ):
            result = await update_knowledge_entry("entry-001", request=request, ctx=mock_ctx)

        assert result.title == "Updated Title"
        mock_repo.patch.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_invalid_entry_type(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo

        from fastapi import HTTPException

        from src.multi_tenant.admin_knowledge_api import (
            UpdateKnowledgeEntryRequest,
            update_knowledge_entry,
        )

        request = UpdateKnowledgeEntryRequest(entry_type="bogus")

        with pytest.raises(HTTPException) as exc_info:
            await update_knowledge_entry("entry-001", request=request, ctx=mock_ctx)

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_update_nonexistent_entry(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo
        mock_repo.read.side_effect = DocumentNotFoundError("kb", "missing", "tenant-001")

        from fastapi import HTTPException

        from src.multi_tenant.admin_knowledge_api import (
            UpdateKnowledgeEntryRequest,
            update_knowledge_entry,
        )

        request = UpdateKnowledgeEntryRequest(title="New")

        with pytest.raises(HTTPException) as exc_info:
            await update_knowledge_entry("missing", request=request, ctx=mock_ctx)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_triggers_re_embedding(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo
        vec = MagicMock()
        vec.embed_entry = AsyncMock()
        mod._knowledge_vectorizer = vec

        from src.multi_tenant.admin_knowledge_api import (
            UpdateKnowledgeEntryRequest,
            update_knowledge_entry,
        )

        request = UpdateKnowledgeEntryRequest(content="New content for re-embedding")

        with (
            patch("src.multi_tenant.admin_knowledge_api._signal_kb_draft", new_callable=AsyncMock),
            patch("src.multi_tenant.staleness_service.classify_staleness", return_value=None),
        ):
            await update_knowledge_entry("entry-001", request=request, ctx=mock_ctx)

        vec.embed_entry.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_status_and_category(self, mock_ctx, mock_repo):
        """Regression: PUT must persist status and category changes (S95 bug)."""
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo
        mod._knowledge_vectorizer = None

        from src.multi_tenant.admin_knowledge_api import (
            UpdateKnowledgeEntryRequest,
            update_knowledge_entry,
        )

        request = UpdateKnowledgeEntryRequest(status="published", category="FAQ")

        with (
            patch("src.multi_tenant.admin_knowledge_api._signal_kb_draft", new_callable=AsyncMock),
            patch("src.multi_tenant.staleness_service.classify_staleness", return_value=None),
        ):
            result = await update_knowledge_entry("entry-001", request=request, ctx=mock_ctx)

        assert result.status == "published"
        assert result.category == "FAQ"
        # Verify patch was called with status and category operations
        mock_repo.patch.assert_called_once()
        ops = mock_repo.patch.call_args.kwargs.get("operations", [])
        paths = [op["path"] for op in ops]
        assert "/status" in paths, "status not included in patch operations"
        assert "/category" in paths, "category not included in patch operations"


# ---------------------------------------------------------------------------
# Unit tests: delete_knowledge_entry
# ---------------------------------------------------------------------------


class TestDeleteKnowledgeEntry:
    @pytest.mark.asyncio
    async def test_delete_success(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo

        from src.multi_tenant.admin_knowledge_api import delete_knowledge_entry

        with patch("src.multi_tenant.admin_knowledge_api._signal_kb_draft", new_callable=AsyncMock):
            result = await delete_knowledge_entry("entry-001", ctx=mock_ctx)

        assert isinstance(result, DeleteKnowledgeEntryResponse)
        assert result.id == "entry-001"
        assert result.deleted_at is not None

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo
        mock_repo.soft_delete.side_effect = DocumentNotFoundError("kb", "missing", "tenant-001")

        from fastapi import HTTPException

        from src.multi_tenant.admin_knowledge_api import delete_knowledge_entry

        with pytest.raises(HTTPException) as exc_info:
            await delete_knowledge_entry("missing", ctx=mock_ctx)

        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# Unit tests: export_knowledge_entries
# ---------------------------------------------------------------------------


class TestExportKnowledgeEntries:
    @pytest.mark.asyncio
    async def test_export_csv_returns_streaming_response(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo
        mock_repo.list_filtered.return_value = [
            _make_entry("e1", "Title One", content="Content One"),
            _make_entry("e2", "Title Two", content="Content Two"),
        ]

        from src.multi_tenant.admin_knowledge_api import export_knowledge_entries

        result = await export_knowledge_entries(ctx=mock_ctx)

        from fastapi.responses import StreamingResponse

        assert isinstance(result, StreamingResponse)
        assert result.media_type == "text/csv"

    @pytest.mark.asyncio
    async def test_export_empty_kb(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo
        mock_repo.list_filtered.return_value = []

        from src.multi_tenant.admin_knowledge_api import export_knowledge_entries

        result = await export_knowledge_entries(ctx=mock_ctx)
        # Should still return a CSV with just headers
        assert result.media_type == "text/csv"


# ---------------------------------------------------------------------------
# Unit tests: staleness endpoints
# ---------------------------------------------------------------------------


class TestStalenessEndpoints:
    @pytest.mark.asyncio
    async def test_staleness_summary_503_when_no_service(self, mock_ctx):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._staleness_service = None

        from fastapi import HTTPException

        from src.multi_tenant.admin_knowledge_api import get_staleness_summary

        with pytest.raises(HTTPException) as exc_info:
            await get_staleness_summary(ctx=mock_ctx)

        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_staleness_summary_success(self, mock_ctx):
        import src.multi_tenant.admin_knowledge_api as mod

        mock_svc = MagicMock()
        mock_svc.get_summary = AsyncMock(return_value={
            "total_entries": 10,
            "avg_staleness_score": 0.3,
            "fresh_count": 6,
            "aging_count": 2,
            "stale_count": 1,
            "very_stale_count": 1,
            "needs_attention": 2,
        })
        mod._staleness_service = mock_svc

        from src.multi_tenant.admin_knowledge_api import get_staleness_summary

        result = await get_staleness_summary(ctx=mock_ctx)
        assert isinstance(result, StalenessSummaryResponse)
        assert result.total_entries == 10

    @pytest.mark.asyncio
    async def test_list_stale_entries(self, mock_ctx):
        import src.multi_tenant.admin_knowledge_api as mod

        mock_svc = MagicMock()
        mock_svc.list_stale = AsyncMock(return_value=[
            {"id": "e1", "staleness_score": 0.8, "staleness_category": "stale"},
        ])
        mod._staleness_service = mock_svc

        from src.multi_tenant.admin_knowledge_api import list_stale_entries

        result = await list_stale_entries(threshold=0.6, ctx=mock_ctx)
        assert isinstance(result, StaleEntriesResponse)
        assert len(result.entries) == 1
        assert result.threshold == 0.6


# ---------------------------------------------------------------------------
# Unit tests: verify_knowledge_entry
# ---------------------------------------------------------------------------


class TestVerifyKnowledgeEntry:
    @pytest.mark.asyncio
    async def test_verify_success(self, mock_ctx):
        import src.multi_tenant.admin_knowledge_api as mod

        mock_svc = MagicMock()
        mock_svc.verify_entry = AsyncMock(return_value={
            "id": "e1",
            "staleness_score": 0.0,
            "staleness_category": "fresh",
        })
        mod._staleness_service = mock_svc

        from src.multi_tenant.admin_knowledge_api import verify_knowledge_entry

        result = await verify_knowledge_entry("e1", ctx=mock_ctx)
        assert result.staleness_score == 0.0

    @pytest.mark.asyncio
    async def test_verify_503_without_service(self, mock_ctx):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._staleness_service = None

        from fastapi import HTTPException

        from src.multi_tenant.admin_knowledge_api import verify_knowledge_entry

        with pytest.raises(HTTPException) as exc_info:
            await verify_knowledge_entry("e1", ctx=mock_ctx)
        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_verify_not_found(self, mock_ctx):
        import src.multi_tenant.admin_knowledge_api as mod

        mock_svc = MagicMock()
        mock_svc.verify_entry = AsyncMock(side_effect=RuntimeError("entry not found"))
        mod._staleness_service = mock_svc

        from fastapi import HTTPException

        from src.multi_tenant.admin_knowledge_api import verify_knowledge_entry

        with pytest.raises(HTTPException) as exc_info:
            await verify_knowledge_entry("missing", ctx=mock_ctx)
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# Unit tests: scan_for_conflicts
# ---------------------------------------------------------------------------


class TestScanForConflicts:
    @pytest.mark.asyncio
    async def test_scan_503_without_scanner(self, mock_ctx):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._conflict_scanner = None

        from fastapi import HTTPException

        from src.multi_tenant.admin_knowledge_api import scan_for_conflicts

        with pytest.raises(HTTPException) as exc_info:
            await scan_for_conflicts(force=False, ctx=mock_ctx)
        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_scan_returns_result(self, mock_ctx):
        import src.multi_tenant.admin_knowledge_api as mod

        mock_scanner = MagicMock()
        scan_result = MagicMock()
        scan_result.tenant_id = "tenant-001"
        scan_result.scanned_at = _NOW
        scan_result.total_entries_scanned = 5
        scan_result.entries_with_embeddings = 4
        scan_result.entries_without_embeddings = 1
        scan_result.conflicts = []
        scan_result.high_count = 0
        scan_result.medium_count = 0
        scan_result.low_count = 0
        scan_result.scan_duration_ms = 123
        mock_scanner.scan = AsyncMock(return_value=scan_result)
        mod._conflict_scanner = mock_scanner

        from src.multi_tenant.admin_knowledge_api import scan_for_conflicts

        result = await scan_for_conflicts(force=False, ctx=mock_ctx)
        assert isinstance(result, ScanResultResponse)
        assert result.total_entries_scanned == 5

    @pytest.mark.asyncio
    async def test_get_cached_result_404_when_none(self, mock_ctx):
        import src.multi_tenant.admin_knowledge_api as mod

        mock_scanner = MagicMock()
        mock_scanner.get_cached_result.return_value = None
        mod._conflict_scanner = mock_scanner

        from fastapi import HTTPException

        from src.multi_tenant.admin_knowledge_api import get_scan_result

        with pytest.raises(HTTPException) as exc_info:
            await get_scan_result(ctx=mock_ctx)
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# Unit tests: upload_knowledge_document
# ---------------------------------------------------------------------------


class TestUploadKnowledgeDocument:
    @pytest.mark.asyncio
    async def test_upload_invalid_entry_type(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo

        from fastapi import HTTPException, UploadFile

        from src.multi_tenant.admin_knowledge_api import upload_knowledge_document

        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.txt"
        mock_file.read = AsyncMock(return_value=b"content")

        with pytest.raises(HTTPException) as exc_info:
            await upload_knowledge_document(file=mock_file, entry_type="bogus", ctx=mock_ctx)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_upload_missing_filename(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo

        from fastapi import HTTPException, UploadFile

        from src.multi_tenant.admin_knowledge_api import upload_knowledge_document

        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = ""
        mock_file.read = AsyncMock(return_value=b"content")

        with pytest.raises(HTTPException) as exc_info:
            await upload_knowledge_document(file=mock_file, entry_type="custom", ctx=mock_ctx)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_upload_empty_file(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo

        from fastapi import HTTPException, UploadFile

        from src.multi_tenant.admin_knowledge_api import upload_knowledge_document

        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.txt"
        mock_file.read = AsyncMock(return_value=b"")

        with pytest.raises(HTTPException) as exc_info:
            await upload_knowledge_document(file=mock_file, entry_type="custom", ctx=mock_ctx)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_upload_success(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo
        mod._knowledge_vectorizer = None

        from fastapi import UploadFile

        from src.multi_tenant.admin_knowledge_api import upload_knowledge_document
        from src.multi_tenant.document_parser import ParseResult, ParsedChunk

        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.txt"
        mock_file.read = AsyncMock(return_value=b"Hello world content")

        mock_parse = ParseResult(
            source_type="txt",
            source_filename="test.txt",
            chunks=[ParsedChunk(text="Hello world content", title="Test", chunk_index=0)],
            total_chars=19,
        )

        mock_entries = [{"id": "new-id", "title": "Test", "content": "Hello world content"}]

        with (
            patch("src.multi_tenant.document_parser.validate_file", return_value=None),
            patch("src.multi_tenant.document_parser.parse_file", new_callable=AsyncMock, return_value=mock_parse),
            patch("src.multi_tenant.document_parser.chunks_to_kb_entries", return_value=mock_entries),
            patch("src.multi_tenant.admin_knowledge_api._signal_kb_draft", new_callable=AsyncMock),
            patch("src.multi_tenant.cosmos_schema.KnowledgeBaseDocument"),
        ):
            result = await upload_knowledge_document(file=mock_file, entry_type="custom", ctx=mock_ctx)

        assert isinstance(result, UploadResultResponse)
        assert result.entries_created == 1


# ---------------------------------------------------------------------------
# Unit tests: import_knowledge_from_url
# ---------------------------------------------------------------------------


class TestImportKnowledgeFromUrl:
    @pytest.mark.asyncio
    async def test_import_rejects_invalid_url(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo

        from fastapi import HTTPException

        from src.multi_tenant.admin_knowledge_api import (
            URLImportRequest,
            import_knowledge_from_url,
        )

        request = URLImportRequest(url="ftp://bad-scheme.com")

        with pytest.raises(HTTPException) as exc_info:
            await import_knowledge_from_url(request=request, ctx=mock_ctx)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_import_invalid_entry_type(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo

        from fastapi import HTTPException

        from src.multi_tenant.admin_knowledge_api import (
            URLImportRequest,
            import_knowledge_from_url,
        )

        request = URLImportRequest(url="https://example.com", entry_type="bogus")

        with pytest.raises(HTTPException) as exc_info:
            await import_knowledge_from_url(request=request, ctx=mock_ctx)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_import_single_page_success(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo
        mod._knowledge_vectorizer = None

        from src.multi_tenant.admin_knowledge_api import (
            URLImportRequest,
            import_knowledge_from_url,
        )
        from src.multi_tenant.document_parser import ParseResult, ParsedChunk

        request = URLImportRequest(url="https://example.com/article")

        mock_parse = ParseResult(
            source_type="url",
            source_url="https://example.com/article",
            chunks=[ParsedChunk(text="Page content here", title="Example", chunk_index=0)],
            total_chars=17,
        )

        mock_entries = [{"id": "url-entry-1", "title": "Example", "content": "Page content here"}]

        with (
            patch("src.multi_tenant.document_parser.parse_url", new_callable=AsyncMock, return_value=mock_parse),
            patch("src.multi_tenant.document_parser.chunks_to_kb_entries", return_value=mock_entries),
            patch("src.multi_tenant.admin_knowledge_api._signal_kb_draft", new_callable=AsyncMock),
            patch("src.multi_tenant.cosmos_schema.KnowledgeBaseDocument"),
        ):
            result = await import_knowledge_from_url(request=request, ctx=mock_ctx)

        assert isinstance(result, UploadResultResponse)
        assert result.source_type == "url"
        assert result.entries_created == 1

    @pytest.mark.asyncio
    async def test_import_parse_failure(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo

        from fastapi import HTTPException

        from src.multi_tenant.admin_knowledge_api import (
            URLImportRequest,
            import_knowledge_from_url,
        )
        from src.multi_tenant.document_parser import ParseResult

        request = URLImportRequest(url="https://example.com/bad")

        mock_parse = ParseResult(
            source_type="url",
            source_url="https://example.com/bad",
            error="HTTP error 404 fetching URL",
        )

        with patch("src.multi_tenant.document_parser.parse_url", new_callable=AsyncMock, return_value=mock_parse):
            with pytest.raises(HTTPException) as exc_info:
                await import_knowledge_from_url(request=request, ctx=mock_ctx)
        assert exc_info.value.status_code == 422


# ---------------------------------------------------------------------------
# Unit tests: preview_entry_chunks
# ---------------------------------------------------------------------------


class TestPreviewEntryChunks:
    @pytest.mark.asyncio
    async def test_chunk_preview_success(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo
        mock_repo.read.return_value = _make_entry(
            content="A" * 2000,
            title="Long Article",
        )

        from src.multi_tenant.admin_knowledge_api import preview_entry_chunks
        from src.multi_tenant.document_parser import ParsedChunk

        mock_chunks = [
            ParsedChunk(text="A" * 800, title="Long Article (Part 1)", chunk_index=0),
            ParsedChunk(text="A" * 800, title="Long Article (Part 2)", chunk_index=1),
        ]

        with patch("src.multi_tenant.document_parser.chunk_text", return_value=mock_chunks):
            result = await preview_entry_chunks(
                "entry-001", chunk_size=None, chunk_overlap=None, ctx=mock_ctx,
            )

        assert isinstance(result, ChunkPreviewResponse)
        assert result.total_chunks == 2

    @pytest.mark.asyncio
    async def test_chunk_preview_not_found(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_knowledge_api as mod

        mod._knowledge_repo = mock_repo
        mock_repo.read.side_effect = DocumentNotFoundError("kb", "missing", "tenant-001")

        from fastapi import HTTPException

        from src.multi_tenant.admin_knowledge_api import preview_entry_chunks

        with pytest.raises(HTTPException) as exc_info:
            await preview_entry_chunks(
                "missing", chunk_size=None, chunk_overlap=None, ctx=mock_ctx,
            )
        assert exc_info.value.status_code == 404
