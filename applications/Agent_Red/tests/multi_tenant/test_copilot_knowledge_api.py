"""Tests for Co-Pilot Knowledge Management API (SPEC-1570..1577).

Validates CRUD, batch ingestion, URL import, re-embedding, stats,
and test query endpoints.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.superadmin_api import (
    CopilotDocumentCreateRequest,
    CopilotDocumentListResponse,
    CopilotDocumentResponse,
    CopilotDocumentUpdateRequest,
    CopilotIngestionResponse,
    CopilotStatsResponse,
    CopilotTestQueryRequest,
    CopilotTestQueryResponse,
    CopilotURLImportRequest,
    configure_copilot_knowledge_service,
    configure_superadmin_services,
    create_copilot_document,
    copilot_stats,
    delete_copilot_document,
    import_url,
    ingest_docs_site,
    list_copilot_documents,
    re_embed_documents,
    test_copilot_query as _test_copilot_query,
    update_copilot_document,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_DOC = {
    "id": "getting_started:quickstart",
    "document_category": "getting_started",
    "title": "Quick Start Guide",
    "content": "Welcome to Agent Red. This guide walks you through setup.",
    "section": None,
    "tags": ["setup", "onboarding"],
    "is_active": True,
    "content_hash": "abc123",
    "embedding": [0.1] * 3072,
    "embedding_model": "text-embedding-3-large",
    "embedded_at": "2026-02-01T12:00:00Z",
    "source_file": "docs/admin-guide/quickstart.md",
    "created_at": "2026-01-15T10:00:00Z",
    "updated_at": "2026-02-01T12:00:00Z",
}


@pytest.fixture()
def mock_admin_doc_repo():
    repo = MagicMock()
    repo.list_all_active = AsyncMock(return_value=[SAMPLE_DOC])
    repo.list_by_category = AsyncMock(return_value=[SAMPLE_DOC])
    repo.get_by_id = AsyncMock(return_value=SAMPLE_DOC)
    repo.upsert_document = AsyncMock(return_value=None)
    repo.count_all = AsyncMock(return_value=1)
    repo.vector_search_all_categories = AsyncMock(return_value=[
        {**SAMPLE_DOC, "similarity": 0.85},
    ])
    return repo


@pytest.fixture()
def superadmin_ctx():
    ctx = MagicMock()
    ctx.tenant_id = "remaker-digital-001"
    ctx.team_member_role = "superadmin"
    return ctx


@pytest.fixture(autouse=True)
def _configure_services(mock_admin_doc_repo):
    configure_superadmin_services(
        tenant_repo=MagicMock(),
        audit_repo=MagicMock(),
    )
    configure_copilot_knowledge_service(
        admin_doc_repo=mock_admin_doc_repo,
    )


# ---------------------------------------------------------------------------
# TestCopilotDocumentCRUD — SPEC-1570
# ---------------------------------------------------------------------------

class TestCopilotDocumentCRUD:
    """Tests for document CRUD endpoints."""

    @pytest.mark.asyncio
    async def test_list_documents(self, mock_admin_doc_repo, superadmin_ctx):
        """GET /copilot/documents returns document list (TEST-2736)."""
        result = await list_copilot_documents(category=None)
        assert isinstance(result, CopilotDocumentListResponse)
        assert result.total == 1
        assert result.documents[0].title == "Quick Start Guide"
        mock_admin_doc_repo.list_all_active.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_list_documents_by_category(self, mock_admin_doc_repo, superadmin_ctx):
        """GET /copilot/documents?category=... filters by category."""
        result = await list_copilot_documents(
            category="getting_started"
        )
        assert result.total == 1
        mock_admin_doc_repo.list_by_category.assert_awaited_once_with("getting_started")

    @pytest.mark.asyncio
    async def test_create_document(self, mock_admin_doc_repo, superadmin_ctx):
        """POST /copilot/documents creates document (TEST-2737)."""
        body = CopilotDocumentCreateRequest(
            document_category="dashboard",
            title="Dashboard Overview",
            content="The dashboard shows key metrics.",
            tags=["dashboard"],
        )
        result = await create_copilot_document(body=body)
        assert isinstance(result, CopilotDocumentResponse)
        assert result.title == "Dashboard Overview"
        assert result.document_category == "dashboard"
        assert result.is_active is True
        assert result.content_hash is not None
        mock_admin_doc_repo.upsert_document.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_document(self, mock_admin_doc_repo, superadmin_ctx):
        """PUT /copilot/documents/{id} updates document (TEST-2738)."""
        body = CopilotDocumentUpdateRequest(
            title="Updated Quick Start",
            content="Updated content for the guide.",
        )
        result = await update_copilot_document(
            doc_id="getting_started:quickstart",
            body=body,
        )
        assert isinstance(result, CopilotDocumentResponse)
        assert result.title == "Updated Quick Start"
        assert result.content == "Updated content for the guide."
        mock_admin_doc_repo.upsert_document.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_soft_delete_document(self, mock_admin_doc_repo, superadmin_ctx):
        """DELETE /copilot/documents/{id} soft-deletes (TEST-2739)."""
        result = await delete_copilot_document(
            doc_id="getting_started:quickstart",
        )
        assert result["is_active"] is False
        assert result["id"] == "getting_started:quickstart"
        mock_admin_doc_repo.upsert_document.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_nonexistent_returns_404(
        self, mock_admin_doc_repo, superadmin_ctx
    ):
        """PUT on nonexistent document returns 404."""
        mock_admin_doc_repo.get_by_id = AsyncMock(return_value=None)
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await update_copilot_document(
                doc_id="missing:doc",
                body=CopilotDocumentUpdateRequest(title="New"),
            )
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# TestBatchIngestion — SPEC-1571
# ---------------------------------------------------------------------------

class TestBatchIngestion:
    """Tests for docs-site batch ingestion."""

    @pytest.mark.asyncio
    async def test_skip_unchanged_documents(
        self, mock_admin_doc_repo, superadmin_ctx, tmp_path
    ):
        """Unchanged documents are skipped via content_hash (TEST-2741)."""
        import hashlib
        from pathlib import Path as RealPath

        # Create a test markdown file
        md_dir = tmp_path / "docs" / "admin-guide"
        md_dir.mkdir(parents=True)
        content = "# Quick Start Guide\nWelcome to Agent Red."
        (md_dir / "quickstart.md").write_text(content, encoding="utf-8")

        # Set content_hash to match
        expected_hash = hashlib.sha256(
            f"Quick Start Guide\n{content}".encode()
        ).hexdigest()
        mock_admin_doc_repo.get_by_id = AsyncMock(
            return_value={**SAMPLE_DOC, "content_hash": expected_hash}
        )

        # Path is imported inside ingest_docs_site — patch at source
        real_path = RealPath

        def fake_path(p):
            if "docs" in str(p) and "admin-guide" in str(p):
                return real_path(md_dir)
            return real_path(p)

        with patch("pathlib.Path", side_effect=fake_path):
            result = await ingest_docs_site()

        assert isinstance(result, CopilotIngestionResponse)
        assert result.skipped == 1

    @pytest.mark.asyncio
    async def test_ingestion_counts_returned(
        self, mock_admin_doc_repo, superadmin_ctx
    ):
        """Ingestion returns created/updated/skipped counts (TEST-2742)."""
        from fastapi import HTTPException

        # Mock Path so both directory candidates don't exist
        mock_dir = MagicMock()
        mock_dir.exists.return_value = False

        with patch("pathlib.Path", return_value=mock_dir):
            with pytest.raises(HTTPException) as exc_info:
                await ingest_docs_site()
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# TestURLImport — SPEC-1572
# ---------------------------------------------------------------------------

class TestURLImport:
    """Tests for URL import."""

    @pytest.mark.asyncio
    async def test_reject_non_https(self, superadmin_ctx):
        """HTTP URLs are rejected (TEST-2744)."""
        from fastapi import HTTPException

        body = CopilotURLImportRequest(
            url="http://insecure.example.com/doc",
            document_category="getting_started",
        )
        with pytest.raises(HTTPException) as exc_info:
            await import_url(body=body)
        assert exc_info.value.status_code == 400
        assert "HTTPS" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_url_import_creates_document(
        self, mock_admin_doc_repo, superadmin_ctx
    ):
        """URL import fetches and creates document (TEST-2743)."""
        body = CopilotURLImportRequest(
            url="https://example.com/docs/setup",
            document_category="getting_started",
            title="Setup Guide",
            tags=["setup"],
        )

        with patch("httpx.AsyncClient") as MockClient:
            mock_resp = MagicMock()
            mock_resp.text = "# Setup Guide\nFollow these steps..."
            mock_resp.raise_for_status = MagicMock()

            mock_client_inst = AsyncMock()
            mock_client_inst.get = AsyncMock(return_value=mock_resp)
            mock_client_inst.__aenter__ = AsyncMock(return_value=mock_client_inst)
            mock_client_inst.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client_inst

            result = await import_url(body=body)

        assert isinstance(result, CopilotDocumentResponse)
        assert result.title == "Setup Guide"
        assert result.document_category == "getting_started"
        mock_admin_doc_repo.upsert_document.assert_awaited_once()


# ---------------------------------------------------------------------------
# TestReEmbedding — SPEC-1573
# ---------------------------------------------------------------------------

class TestReEmbedding:
    """Tests for re-embedding trigger."""

    @pytest.mark.asyncio
    async def test_re_embed_all_documents(
        self, mock_admin_doc_repo, superadmin_ctx
    ):
        """Re-embed updates embedding and embedded_at (TEST-2745)."""
        fake_embedding = [0.5] * 3072

        with patch(
            "src.multi_tenant.superadmin_api._copilot._generate_embedding",
            new_callable=AsyncMock,
            return_value=fake_embedding,
        ):
            result = await re_embed_documents()

        assert isinstance(result, CopilotIngestionResponse)
        assert result.updated == 1
        assert result.errors == []
        mock_admin_doc_repo.upsert_document.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_content_preserved_after_reembed(
        self, mock_admin_doc_repo, superadmin_ctx
    ):
        """Document content is preserved during re-embedding (TEST-2746)."""
        fake_embedding = [0.5] * 3072
        upserted_docs = []

        async def capture_upsert(doc):
            upserted_docs.append(doc)

        mock_admin_doc_repo.upsert_document = AsyncMock(side_effect=capture_upsert)

        with patch(
            "src.multi_tenant.superadmin_api._copilot._generate_embedding",
            new_callable=AsyncMock,
            return_value=fake_embedding,
        ):
            await re_embed_documents()

        assert len(upserted_docs) == 1
        doc = upserted_docs[0]
        assert doc.title == SAMPLE_DOC["title"]
        assert doc.content == SAMPLE_DOC["content"]


# ---------------------------------------------------------------------------
# TestCollectionStats — SPEC-1574
# ---------------------------------------------------------------------------

class TestCollectionStats:
    """Tests for collection statistics."""

    @pytest.mark.asyncio
    async def test_stats_endpoint(self, mock_admin_doc_repo, superadmin_ctx):
        """GET /copilot/stats returns statistics (TEST-2747)."""
        result = await copilot_stats()
        assert isinstance(result, CopilotStatsResponse)
        assert result.total_documents == 1
        assert result.active_documents == 1
        assert "getting_started" in result.by_category
        assert result.embedded_count == 1

    @pytest.mark.asyncio
    async def test_stale_count_accuracy(self, mock_admin_doc_repo, superadmin_ctx):
        """Stale count reflects documents with outdated embeddings (TEST-2748)."""
        # Doc with mismatched content_hash = stale
        stale_doc = {
            **SAMPLE_DOC,
            "content_hash": "wrong_hash_indicating_content_changed",
        }
        mock_admin_doc_repo.list_all_active = AsyncMock(return_value=[stale_doc])

        result = await copilot_stats()
        assert result.stale_count == 1


# ---------------------------------------------------------------------------
# TestQueryEndpoint — SPEC-1577
# ---------------------------------------------------------------------------

class TestQueryEndpoint:
    """Tests for test query endpoint."""

    @pytest.mark.asyncio
    async def test_query_returns_scored_results(
        self, mock_admin_doc_repo, superadmin_ctx
    ):
        """Test query returns ranked results (TEST-2753)."""
        body = CopilotTestQueryRequest(query="how to set up", top_k=5)

        with patch(
            "src.multi_tenant.superadmin_api._copilot._generate_embedding",
            new_callable=AsyncMock,
            return_value=[0.5] * 3072,
        ):
            result = await _test_copilot_query(body=body)

        assert isinstance(result, CopilotTestQueryResponse)
        assert result.query == "how to set up"
        assert len(result.results) == 1
        assert result.results[0].rrf_score == 0.85
        assert result.total_documents == 1

    @pytest.mark.asyncio
    async def test_503_when_not_configured(self, superadmin_ctx):
        """Returns 503 when Co-Pilot knowledge not configured."""
        from fastapi import HTTPException

        configure_copilot_knowledge_service(admin_doc_repo=None)

        with pytest.raises(HTTPException) as exc_info:
            await list_copilot_documents(category=None)
        assert exc_info.value.status_code == 503
