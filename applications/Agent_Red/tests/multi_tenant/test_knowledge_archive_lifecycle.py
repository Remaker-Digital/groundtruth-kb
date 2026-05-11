"""Tests for knowledge article archive lifecycle.

Verifies that archiving/unarchiving articles correctly manages is_active
and vector embeddings so archived content cannot be retrieved by the RAG
pipeline.

Run:
    pytest tests/multi_tenant/test_knowledge_archive_lifecycle.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
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

TENANT_ID = "t-archive-test-001"
NOW_ISO = datetime.now(timezone.utc).isoformat()
PREFIX = "/api/admin/knowledge"


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
    content: str = "Test content for knowledge base entry.",
    entry_type: str = "faq",
    status: str = "published",
    is_active: bool = True,
    embedding: list[float] | None = None,
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
        "is_active": is_active,
        "category": None,
        "status": status,
        "staleness_score": 0.0,
        "last_verified_at": NOW_ISO,
        "created_at": NOW_ISO,
        "updated_at": NOW_ISO,
        "embedding": embedding,
        "embedding_model": "text-embedding-3-small" if embedding else None,
        "embedded_at": NOW_ISO if embedding else None,
        "content_hash": "abc123" if embedding else None,
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_kb_repo():
    """AsyncMock of KnowledgeBaseRepository with patch tracking."""
    repo = AsyncMock()
    repo._entries: list[dict[str, Any]] = []
    repo._patch_calls: list[tuple[str, str, list]] = []

    async def _create(tenant_id: str, doc: Any) -> dict[str, Any]:
        d = doc.model_dump() if hasattr(doc, "model_dump") else doc
        repo._entries.append(d)
        return d

    async def _read(tenant_id: str, doc_id: str) -> dict[str, Any]:
        for e in repo._entries:
            if e.get("id") == doc_id:
                return dict(e)
        from src.multi_tenant.repository import DocumentNotFoundError
        raise DocumentNotFoundError(f"Not found: {doc_id}")

    async def _patch(tenant_id: str, document_id: str, operations: list) -> None:
        repo._patch_calls.append((tenant_id, document_id, operations))
        for e in repo._entries:
            if e.get("id") == document_id:
                for op in operations:
                    path = op["path"].lstrip("/")
                    e[path] = op["value"]
                return
        from src.multi_tenant.repository import DocumentNotFoundError
        raise DocumentNotFoundError(f"Not found: {document_id}")

    repo.create = AsyncMock(side_effect=_create)
    repo.read = AsyncMock(side_effect=_read)
    repo.patch = AsyncMock(side_effect=_patch)
    return repo


@pytest.fixture()
def mock_vectorizer():
    """AsyncMock of KnowledgeVectorizer."""
    vec = AsyncMock()
    vec.embed_entry = AsyncMock(return_value=None)
    return vec


@pytest.fixture()
def mock_activation_svc():
    """Mock ActivationService for signal tests."""
    svc = MagicMock()
    svc.ensure_draft_for_signal = AsyncMock(
        return_value=MagicMock(success=True, message="ok"),
    )
    return svc


@pytest.fixture()
def client(mock_kb_repo, mock_vectorizer, mock_activation_svc):
    """TestClient with knowledge services configured (vectorizer enabled)."""
    from src.multi_tenant.middleware import get_tenant_context

    configure_admin_knowledge_services(
        knowledge_repo=mock_kb_repo,
        knowledge_vectorizer=mock_vectorizer,
    )
    app = FastAPI()
    app.dependency_overrides[get_tenant_context] = lambda: _make_tenant_context()
    app.include_router(router)

    with patch(
        "src.multi_tenant.admin_knowledge_api.get_activation_service",
        return_value=mock_activation_svc,
    ):
        yield TestClient(app)

    configure_admin_knowledge_services(knowledge_repo=None)


# ---------------------------------------------------------------------------
# Tests — Archiving sets is_active=False
# ---------------------------------------------------------------------------


class TestArchiveSetsInactive:
    """Archiving an article must automatically set is_active=False."""

    def test_archive_from_published(self, client, mock_kb_repo, mock_vectorizer):
        """Published -> archived sets is_active=False."""
        entry = _make_kb_entry(status="published", is_active=True)
        mock_kb_repo._entries.append(entry)

        resp = client.put(
            f"{PREFIX}/{entry['id']}",
            json={"status": "archived"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "archived"
        assert data["isActive"] is False

        # Verify the patch operations included is_active=False
        all_ops = []
        for _, _, ops in mock_kb_repo._patch_calls:
            all_ops.extend(ops)
        is_active_ops = [o for o in all_ops if o["path"] == "/is_active"]
        assert any(o["value"] is False for o in is_active_ops)

    def test_archive_from_draft(self, client, mock_kb_repo, mock_vectorizer):
        """Draft -> archived sets is_active=False."""
        entry = _make_kb_entry(status="draft", is_active=True)
        mock_kb_repo._entries.append(entry)

        resp = client.put(
            f"{PREFIX}/{entry['id']}",
            json={"status": "archived"},
        )
        assert resp.status_code == 200
        assert resp.json()["isActive"] is False

    def test_archive_already_inactive(self, client, mock_kb_repo, mock_vectorizer):
        """Archive still sets is_active=False even if already inactive."""
        entry = _make_kb_entry(status="published", is_active=False)
        mock_kb_repo._entries.append(entry)

        resp = client.put(
            f"{PREFIX}/{entry['id']}",
            json={"status": "archived"},
        )
        assert resp.status_code == 200
        assert resp.json()["isActive"] is False

    def test_archive_does_not_override_explicit_is_active(
        self, client, mock_kb_repo, mock_vectorizer,
    ):
        """Even if caller sends is_active=True with archived status,
        the archive lifecycle forces is_active=False in the response."""
        entry = _make_kb_entry(status="published", is_active=True)
        mock_kb_repo._entries.append(entry)

        resp = client.put(
            f"{PREFIX}/{entry['id']}",
            json={"status": "archived", "is_active": True},
        )
        assert resp.status_code == 200
        assert resp.json()["isActive"] is False


# ---------------------------------------------------------------------------
# Tests — Unarchiving sets is_active=True
# ---------------------------------------------------------------------------


class TestUnarchiveSetsActive:
    """Moving from archived to draft/published must set is_active=True."""

    def test_unarchive_to_published(self, client, mock_kb_repo, mock_vectorizer):
        """Archived -> published sets is_active=True."""
        entry = _make_kb_entry(status="archived", is_active=False)
        mock_kb_repo._entries.append(entry)

        resp = client.put(
            f"{PREFIX}/{entry['id']}",
            json={"status": "published"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "published"
        assert data["isActive"] is True

    def test_unarchive_to_draft(self, client, mock_kb_repo, mock_vectorizer):
        """Archived -> draft sets is_active=True."""
        entry = _make_kb_entry(status="archived", is_active=False)
        mock_kb_repo._entries.append(entry)

        resp = client.put(
            f"{PREFIX}/{entry['id']}",
            json={"status": "draft"},
        )
        assert resp.status_code == 200
        assert resp.json()["isActive"] is True

    def test_unarchive_patch_includes_is_active_true(
        self, client, mock_kb_repo, mock_vectorizer,
    ):
        """Verify the patch operations include is_active=True on unarchive."""
        entry = _make_kb_entry(status="archived", is_active=False)
        mock_kb_repo._entries.append(entry)

        client.put(
            f"{PREFIX}/{entry['id']}",
            json={"status": "published"},
        )

        all_ops = []
        for _, _, ops in mock_kb_repo._patch_calls:
            all_ops.extend(ops)
        is_active_ops = [o for o in all_ops if o["path"] == "/is_active"]
        assert any(o["value"] is True for o in is_active_ops)


# ---------------------------------------------------------------------------
# Tests — Archiving triggers vector deletion
# ---------------------------------------------------------------------------


class TestArchiveDeletesVector:
    """Archiving must clear the vector embedding from the document."""

    def test_archive_clears_embedding_fields(
        self, client, mock_kb_repo, mock_vectorizer,
    ):
        """Archiving triggers a second patch that nulls embedding fields."""
        entry = _make_kb_entry(
            status="published",
            is_active=True,
            embedding=[0.1, 0.2, 0.3],
        )
        mock_kb_repo._entries.append(entry)

        resp = client.put(
            f"{PREFIX}/{entry['id']}",
            json={"status": "archived"},
        )
        assert resp.status_code == 200

        # There should be at least 2 patch calls: the main update + the embedding clear
        assert len(mock_kb_repo._patch_calls) >= 2

        # The second patch should null out embedding fields
        _, _, clear_ops = mock_kb_repo._patch_calls[1]
        cleared_paths = {op["path"] for op in clear_ops}
        assert "/embedding" in cleared_paths
        assert "/embedding_model" in cleared_paths
        assert "/embedded_at" in cleared_paths
        assert "/content_hash" in cleared_paths

        for op in clear_ops:
            assert op["value"] is None

    def test_archive_without_vectorizer_skips_clear(self, mock_kb_repo):
        """When vectorizer is not configured, archiving still sets is_active
        but does not attempt to clear embeddings."""
        from src.multi_tenant.middleware import get_tenant_context

        mock_activation_svc = MagicMock()
        mock_activation_svc.ensure_draft_for_signal = AsyncMock(
            return_value=MagicMock(success=True, message="ok"),
        )

        configure_admin_knowledge_services(
            knowledge_repo=mock_kb_repo,
            knowledge_vectorizer=None,
        )
        app = FastAPI()
        app.dependency_overrides[get_tenant_context] = lambda: _make_tenant_context()
        app.include_router(router)

        with patch(
            "src.multi_tenant.admin_knowledge_api.get_activation_service",
            return_value=mock_activation_svc,
        ):
            tc = TestClient(app)

            entry = _make_kb_entry(
                status="published",
                is_active=True,
                embedding=[0.1, 0.2, 0.3],
            )
            mock_kb_repo._entries.append(entry)

            resp = tc.put(
                f"{PREFIX}/{entry['id']}",
                json={"status": "archived"},
            )
            assert resp.status_code == 200
            assert resp.json()["isActive"] is False

            # Only 1 patch call (no embedding clear without vectorizer)
            assert len(mock_kb_repo._patch_calls) == 1

        configure_admin_knowledge_services(knowledge_repo=None)

    def test_archive_embed_clear_failure_non_blocking(
        self, client, mock_kb_repo, mock_vectorizer,
    ):
        """If clearing the embedding fails, the archive still succeeds."""
        entry = _make_kb_entry(
            status="published",
            is_active=True,
            embedding=[0.1, 0.2, 0.3],
        )
        mock_kb_repo._entries.append(entry)

        # Make the second patch call raise an error
        call_count = 0
        original_patch = mock_kb_repo.patch.side_effect

        async def _failing_second_patch(tenant_id, document_id, operations):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise RuntimeError("Cosmos transient error")
            return await original_patch(tenant_id, document_id, operations)

        mock_kb_repo.patch.side_effect = _failing_second_patch

        resp = client.put(
            f"{PREFIX}/{entry['id']}",
            json={"status": "archived"},
        )
        # Should still succeed — embedding clear is non-blocking
        assert resp.status_code == 200
        assert resp.json()["isActive"] is False


# ---------------------------------------------------------------------------
# Tests — Unarchiving triggers re-embedding
# ---------------------------------------------------------------------------


class TestUnarchiveTriggersReembedding:
    """Unarchiving must trigger re-embedding via the vectorizer."""

    def test_unarchive_calls_embed_entry(
        self, client, mock_kb_repo, mock_vectorizer,
    ):
        """Moving from archived to published triggers embed_entry."""
        entry = _make_kb_entry(status="archived", is_active=False)
        mock_kb_repo._entries.append(entry)

        resp = client.put(
            f"{PREFIX}/{entry['id']}",
            json={"status": "published"},
        )
        assert resp.status_code == 200

        mock_vectorizer.embed_entry.assert_called_once()
        call_args = mock_vectorizer.embed_entry.call_args
        assert call_args[0][0] == TENANT_ID

    def test_unarchive_to_draft_calls_embed_entry(
        self, client, mock_kb_repo, mock_vectorizer,
    ):
        """Moving from archived to draft also triggers embed_entry."""
        entry = _make_kb_entry(status="archived", is_active=False)
        mock_kb_repo._entries.append(entry)

        resp = client.put(
            f"{PREFIX}/{entry['id']}",
            json={"status": "draft"},
        )
        assert resp.status_code == 200
        mock_vectorizer.embed_entry.assert_called_once()

    def test_unarchive_embed_failure_non_blocking(
        self, client, mock_kb_repo, mock_vectorizer,
    ):
        """If re-embedding fails on unarchive, the update still succeeds."""
        entry = _make_kb_entry(status="archived", is_active=False)
        mock_kb_repo._entries.append(entry)

        mock_vectorizer.embed_entry.side_effect = RuntimeError("Embedding service down")

        resp = client.put(
            f"{PREFIX}/{entry['id']}",
            json={"status": "published"},
        )
        assert resp.status_code == 200
        assert resp.json()["isActive"] is True


# ---------------------------------------------------------------------------
# Tests — No-op transitions
# ---------------------------------------------------------------------------


class TestNoOpTransitions:
    """Status changes that are not archive/unarchive must not trigger
    archive lifecycle logic."""

    def test_published_to_draft_no_lifecycle(
        self, client, mock_kb_repo, mock_vectorizer,
    ):
        """Published -> draft does not change is_active automatically."""
        entry = _make_kb_entry(status="published", is_active=True)
        mock_kb_repo._entries.append(entry)

        resp = client.put(
            f"{PREFIX}/{entry['id']}",
            json={"status": "draft"},
        )
        assert resp.status_code == 200
        # is_active stays True (no archive lifecycle triggered)
        assert resp.json()["isActive"] is True
        # Only 1 patch call (no embedding clear)
        assert len(mock_kb_repo._patch_calls) == 1

    def test_archived_to_archived_no_double_clear(
        self, client, mock_kb_repo, mock_vectorizer,
    ):
        """Archived -> archived (no-op) does not trigger lifecycle."""
        entry = _make_kb_entry(status="archived", is_active=False)
        mock_kb_repo._entries.append(entry)

        resp = client.put(
            f"{PREFIX}/{entry['id']}",
            json={"status": "archived"},
        )
        assert resp.status_code == 200
        # Only 1 patch call — no extra embedding clear
        assert len(mock_kb_repo._patch_calls) == 1

    def test_title_update_without_status_no_lifecycle(
        self, client, mock_kb_repo, mock_vectorizer,
    ):
        """Updating title without changing status does not trigger
        archive lifecycle."""
        entry = _make_kb_entry(status="published", is_active=True)
        mock_kb_repo._entries.append(entry)

        resp = client.put(
            f"{PREFIX}/{entry['id']}",
            json={"title": "Updated Title"},
        )
        assert resp.status_code == 200
        assert resp.json()["isActive"] is True
        assert len(mock_kb_repo._patch_calls) == 1
