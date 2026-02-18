"""Tests for KB chunk preview endpoint — C5: Chunking preview.

Verifies the GET /api/admin/knowledge/{entry_id}/chunks endpoint that
returns a preview of how a KB article's content would be chunked by
the document parser.

Test IDs:
    CP-01: Short article (single chunk)
    CP-02: Long article (multiple chunks)
    CP-03: Custom chunk_size parameter
    CP-04: Article not found (404)
    CP-05: Empty content (empty chunks list)
    CP-06: Chunk metadata correctness
    CP-07: Chunk overlap parameter

Run:
    pytest tests/multi_tenant/test_chunking_preview.py -v

(C) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import TenantStatus, TenantTier
from src.multi_tenant.admin_knowledge_api import (
    configure_admin_knowledge_services,
    router,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TENANT_ID = "t-chunk-preview-001"
NOW_ISO = datetime.now(timezone.utc).isoformat()
PREFIX = "/api/admin/knowledge"

# CHARS_PER_TOKEN = 4 in document_parser.py
CHARS_PER_TOKEN = 4

# Short content — fits in one chunk at default 400 tokens (1600 chars)
SHORT_CONTENT = "This is a short article about our return policy. " * 5  # ~250 chars

# Long content — exceeds default chunk size (400 tokens = 1600 chars)
# Build with distinct paragraphs separated by double newlines
_PARAGRAPH = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
    "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
    "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris."
)
LONG_CONTENT = "\n\n".join([f"Paragraph {i + 1}. {_PARAGRAPH}" for i in range(20)])

# Content for overlap testing — needs to be long enough for multiple chunks
OVERLAP_CONTENT = "\n\n".join([f"Section {i + 1}. {_PARAGRAPH}" for i in range(25)])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_tenant_context(
    tenant_id: str = TENANT_ID,
    tier: TenantTier = TenantTier.STARTER,
) -> TenantContext:
    return TenantContext(
        tenant_id=tenant_id,
        tier=tier,
        status=TenantStatus.ACTIVE,
        auth_method="api_key",
    )


def _make_kb_entry(
    entry_id: str | None = None,
    title: str = "Test Article",
    content: str = SHORT_CONTENT,
    entry_type: str = "article",
) -> dict[str, Any]:
    return {
        "id": entry_id or str(uuid.uuid4()),
        "tenant_id": TENANT_ID,
        "entry_type": entry_type,
        "title": title,
        "content": content,
        "metadata": {},
        "tags": [],
        "language": "en",
        "is_active": True,
        "category": None,
        "status": "published",
        "staleness_score": 0.0,
        "last_verified_at": NOW_ISO,
        "created_at": NOW_ISO,
        "updated_at": NOW_ISO,
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_kb_repo():
    """AsyncMock of KnowledgeBaseRepository with in-memory store."""
    repo = AsyncMock()
    repo._entries: list[dict[str, Any]] = []

    async def _read(tenant_id: str, doc_id: str) -> dict[str, Any]:
        for e in repo._entries:
            if e.get("id") == doc_id and e.get("tenant_id") == tenant_id:
                return dict(e)
        from src.multi_tenant.repository import DocumentNotFoundError
        raise DocumentNotFoundError(
            collection="knowledge_base",
            document_id=doc_id,
            tenant_id=tenant_id,
        )

    repo.read = AsyncMock(side_effect=_read)
    return repo


@pytest.fixture()
def chunk_client(mock_kb_repo):
    """FastAPI test client with KB router mounted and mocked services."""
    app = FastAPI()

    from src.multi_tenant.middleware import get_tenant_context
    app.dependency_overrides[get_tenant_context] = lambda: _make_tenant_context()

    app.include_router(router)
    configure_admin_knowledge_services(knowledge_repo=mock_kb_repo)

    client = TestClient(app)
    yield client

    # Cleanup: reset module-level repo reference
    configure_admin_knowledge_services(knowledge_repo=None)


# ===========================================================================
# CP-01: Short article (fits in one chunk) returns single chunk
# ===========================================================================


class TestCP01ShortArticleSingleChunk:
    """A short article that fits within one chunk returns exactly one chunk."""

    def test_short_article_returns_single_chunk(self, chunk_client, mock_kb_repo):
        entry = _make_kb_entry(entry_id="kb-short-1", content=SHORT_CONTENT, title="Return Policy")
        mock_kb_repo._entries.append(entry)

        resp = chunk_client.get(f"{PREFIX}/kb-short-1/chunks")
        assert resp.status_code == 200, resp.text

        data = resp.json()
        assert data["entryId"] == "kb-short-1"
        assert data["title"] == "Return Policy"
        assert data["totalChunks"] == 1
        assert data["totalChars"] == len(SHORT_CONTENT)
        assert len(data["chunks"]) == 1

        chunk = data["chunks"][0]
        assert chunk["chunkIndex"] == 0
        assert chunk["charCount"] > 0
        assert chunk["estimatedTokens"] > 0


# ===========================================================================
# CP-02: Long article returns multiple chunks with correct indices
# ===========================================================================


class TestCP02LongArticleMultipleChunks:
    """A long article is split into multiple chunks with sequential indices."""

    def test_long_article_returns_multiple_chunks(self, chunk_client, mock_kb_repo):
        entry = _make_kb_entry(entry_id="kb-long-1", content=LONG_CONTENT, title="Long Guide")
        mock_kb_repo._entries.append(entry)

        resp = chunk_client.get(f"{PREFIX}/kb-long-1/chunks")
        assert resp.status_code == 200, resp.text

        data = resp.json()
        assert data["totalChunks"] > 1
        assert len(data["chunks"]) == data["totalChunks"]

        # Verify sequential chunk indices
        indices = [c["chunkIndex"] for c in data["chunks"]]
        assert indices == list(range(len(indices)))

    def test_all_chunks_have_content(self, chunk_client, mock_kb_repo):
        entry = _make_kb_entry(entry_id="kb-long-2", content=LONG_CONTENT, title="Long Guide")
        mock_kb_repo._entries.append(entry)

        resp = chunk_client.get(f"{PREFIX}/kb-long-2/chunks")
        data = resp.json()

        for chunk in data["chunks"]:
            assert len(chunk["text"]) > 0
            assert chunk["charCount"] > 0
            assert chunk["estimatedTokens"] > 0


# ===========================================================================
# CP-03: Custom chunk_size parameter works
# ===========================================================================


class TestCP03CustomChunkSize:
    """Custom chunk_size query parameter changes the chunking granularity."""

    def test_smaller_chunk_size_produces_more_chunks(self, chunk_client, mock_kb_repo):
        entry = _make_kb_entry(entry_id="kb-cs-1", content=LONG_CONTENT, title="Guide")
        mock_kb_repo._entries.append(entry)

        # Default chunk size (400 tokens)
        resp_default = chunk_client.get(f"{PREFIX}/kb-cs-1/chunks")
        default_chunks = resp_default.json()["totalChunks"]

        # Smaller chunk size (100 tokens)
        resp_small = chunk_client.get(f"{PREFIX}/kb-cs-1/chunks?chunk_size=100")
        small_data = resp_small.json()

        assert resp_small.status_code == 200
        assert small_data["chunkSize"] == 100
        # Smaller chunk size should produce more (or equal) chunks
        assert small_data["totalChunks"] >= default_chunks

    def test_chunk_size_reflected_in_response(self, chunk_client, mock_kb_repo):
        entry = _make_kb_entry(entry_id="kb-cs-2", content=SHORT_CONTENT, title="Guide")
        mock_kb_repo._entries.append(entry)

        resp = chunk_client.get(f"{PREFIX}/kb-cs-2/chunks?chunk_size=200")
        data = resp.json()
        assert data["chunkSize"] == 200


# ===========================================================================
# CP-04: Article not found returns 404
# ===========================================================================


class TestCP04ArticleNotFound:
    """Requesting chunks for a non-existent article returns 404."""

    def test_missing_entry_returns_404(self, chunk_client):
        resp = chunk_client.get(f"{PREFIX}/nonexistent-id/chunks")
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"].lower()


# ===========================================================================
# CP-05: Empty content returns empty chunks list
# ===========================================================================


class TestCP05EmptyContent:
    """An article with empty content returns zero chunks."""

    def test_empty_content_returns_empty_chunks(self, chunk_client, mock_kb_repo):
        entry = _make_kb_entry(entry_id="kb-empty-1", content="", title="Empty Article")
        mock_kb_repo._entries.append(entry)

        resp = chunk_client.get(f"{PREFIX}/kb-empty-1/chunks")
        assert resp.status_code == 200

        data = resp.json()
        assert data["totalChunks"] == 0
        assert data["chunks"] == []
        assert data["totalChars"] == 0

    def test_whitespace_only_content_returns_empty_chunks(self, chunk_client, mock_kb_repo):
        entry = _make_kb_entry(entry_id="kb-ws-1", content="   \n\n  \t  ", title="Whitespace")
        mock_kb_repo._entries.append(entry)

        resp = chunk_client.get(f"{PREFIX}/kb-ws-1/chunks")
        assert resp.status_code == 200

        data = resp.json()
        assert data["totalChunks"] == 0
        assert data["chunks"] == []


# ===========================================================================
# CP-06: Chunk metadata (char_count, estimated_tokens) is correct
# ===========================================================================


class TestCP06ChunkMetadata:
    """Per-chunk char_count and estimated_tokens are accurately computed."""

    def test_char_count_matches_text_length(self, chunk_client, mock_kb_repo):
        entry = _make_kb_entry(entry_id="kb-meta-1", content=SHORT_CONTENT, title="Meta Test")
        mock_kb_repo._entries.append(entry)

        resp = chunk_client.get(f"{PREFIX}/kb-meta-1/chunks")
        data = resp.json()

        for chunk in data["chunks"]:
            assert chunk["charCount"] == len(chunk["text"])

    def test_estimated_tokens_uses_chars_per_token(self, chunk_client, mock_kb_repo):
        entry = _make_kb_entry(entry_id="kb-meta-2", content=SHORT_CONTENT, title="Meta Test")
        mock_kb_repo._entries.append(entry)

        resp = chunk_client.get(f"{PREFIX}/kb-meta-2/chunks")
        data = resp.json()

        for chunk in data["chunks"]:
            expected_tokens = max(1, len(chunk["text"]) // CHARS_PER_TOKEN)
            assert chunk["estimatedTokens"] == expected_tokens

    def test_total_chars_matches_original_content(self, chunk_client, mock_kb_repo):
        entry = _make_kb_entry(entry_id="kb-meta-3", content=SHORT_CONTENT, title="Meta Test")
        mock_kb_repo._entries.append(entry)

        resp = chunk_client.get(f"{PREFIX}/kb-meta-3/chunks")
        data = resp.json()

        assert data["totalChars"] == len(SHORT_CONTENT)


# ===========================================================================
# CP-07: Chunk overlap parameter works
# ===========================================================================


class TestCP07ChunkOverlap:
    """Custom chunk_overlap query parameter is applied to chunking."""

    def test_overlap_reflected_in_response(self, chunk_client, mock_kb_repo):
        entry = _make_kb_entry(entry_id="kb-ov-1", content=OVERLAP_CONTENT, title="Overlap Test")
        mock_kb_repo._entries.append(entry)

        resp = chunk_client.get(f"{PREFIX}/kb-ov-1/chunks?chunk_overlap=100")
        assert resp.status_code == 200

        data = resp.json()
        assert data["chunkOverlap"] == 100

    def test_zero_overlap_works(self, chunk_client, mock_kb_repo):
        entry = _make_kb_entry(entry_id="kb-ov-2", content=OVERLAP_CONTENT, title="No Overlap")
        mock_kb_repo._entries.append(entry)

        resp = chunk_client.get(f"{PREFIX}/kb-ov-2/chunks?chunk_overlap=0")
        assert resp.status_code == 200

        data = resp.json()
        assert data["chunkOverlap"] == 0
        assert data["totalChunks"] > 0

    def test_overlap_and_chunk_size_combined(self, chunk_client, mock_kb_repo):
        entry = _make_kb_entry(entry_id="kb-ov-3", content=OVERLAP_CONTENT, title="Combined")
        mock_kb_repo._entries.append(entry)

        resp = chunk_client.get(f"{PREFIX}/kb-ov-3/chunks?chunk_size=150&chunk_overlap=30")
        assert resp.status_code == 200

        data = resp.json()
        assert data["chunkSize"] == 150
        assert data["chunkOverlap"] == 30
        assert data["totalChunks"] > 0
