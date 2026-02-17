"""Tests for Admin Knowledge API — draft signal integration (D16).

Verifies that KB write endpoints trigger the ``kb_modified_at`` signal
on the draft PreferencesDocument so the Pending badge appears.

Run:
    pytest tests/multi_tenant/test_admin_knowledge_api.py -v

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

TENANT_ID = "t-kb-test-001"
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
        "status": "draft",
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
    """AsyncMock of KnowledgeBaseRepository."""
    repo = AsyncMock()
    repo._entries: list[dict[str, Any]] = []

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
        for e in repo._entries:
            if e.get("id") == document_id:
                for op in operations:
                    path = op["path"].lstrip("/")
                    e[path] = op["value"]
                return
        from src.multi_tenant.repository import DocumentNotFoundError
        raise DocumentNotFoundError(f"Not found: {document_id}")

    async def _soft_delete(tenant_id: str, doc_id: str) -> None:
        for e in repo._entries:
            if e.get("id") == doc_id:
                e["is_active"] = False
                return
        from src.multi_tenant.repository import DocumentNotFoundError
        raise DocumentNotFoundError(f"Not found: {doc_id}")

    repo.create = AsyncMock(side_effect=_create)
    repo.read = AsyncMock(side_effect=_read)
    repo.patch = AsyncMock(side_effect=_patch)
    repo.soft_delete = AsyncMock(side_effect=_soft_delete)
    return repo


@pytest.fixture()
def mock_activation_svc():
    """Mock ActivationService for signal tests."""
    svc = MagicMock()
    svc.ensure_draft_for_signal = AsyncMock(
        return_value=MagicMock(success=True, message="ok"),
    )
    return svc


@pytest.fixture()
def kb_client(mock_kb_repo, mock_activation_svc):
    """FastAPI test client with KB router and mocked services."""
    app = FastAPI()

    from src.multi_tenant.middleware import get_tenant_context
    app.dependency_overrides[get_tenant_context] = lambda: _make_tenant_context()

    app.include_router(router)
    configure_admin_knowledge_services(knowledge_repo=mock_kb_repo)

    with patch(
        "src.multi_tenant.admin_knowledge_api.get_activation_service",
        return_value=mock_activation_svc,
    ):
        client = TestClient(app)
        yield client, mock_activation_svc

    configure_admin_knowledge_services(knowledge_repo=None)


# ===========================================================================
# Draft Signal Tests (D16)
# ===========================================================================


class TestKBDraftSignal:
    """Verify that KB write endpoints call ensure_draft_for_signal."""

    def test_create_entry_signals_draft(self, kb_client):
        """Creating a KB entry triggers the kb_modified_at signal."""
        client, mock_svc = kb_client
        resp = client.post(
            PREFIX,
            json={
                "title": "Test Article",
                "content": "Article content here.",
                "entryType": "faq",
            },
        )
        assert resp.status_code == 201, resp.text
        mock_svc.ensure_draft_for_signal.assert_called_once()
        call_kwargs = mock_svc.ensure_draft_for_signal.call_args
        assert call_kwargs.kwargs.get("signal_field") == "kb_modified_at"

    def test_update_entry_signals_draft(self, kb_client, mock_kb_repo):
        """Updating a KB entry triggers the kb_modified_at signal."""
        client, mock_svc = kb_client

        entry = _make_kb_entry(entry_id="kb-1")
        mock_kb_repo._entries.append(entry)

        resp = client.put(
            f"{PREFIX}/kb-1",
            json={"title": "Updated Title"},
        )
        assert resp.status_code == 200, resp.text
        mock_svc.ensure_draft_for_signal.assert_called_once()
        call_kwargs = mock_svc.ensure_draft_for_signal.call_args
        assert call_kwargs.kwargs.get("signal_field") == "kb_modified_at"

    def test_delete_entry_signals_draft(self, kb_client, mock_kb_repo):
        """Soft-deleting a KB entry triggers the kb_modified_at signal."""
        client, mock_svc = kb_client

        entry = _make_kb_entry(entry_id="kb-2")
        mock_kb_repo._entries.append(entry)

        resp = client.delete(f"{PREFIX}/kb-2")
        assert resp.status_code == 200, resp.text
        mock_svc.ensure_draft_for_signal.assert_called_once()

    def test_signal_failure_does_not_block_kb_operation(
        self, mock_kb_repo, mock_activation_svc,
    ):
        """If signal fails, KB write still succeeds."""
        mock_activation_svc.ensure_draft_for_signal = AsyncMock(
            side_effect=RuntimeError("Cosmos timeout"),
        )

        app = FastAPI()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: _make_tenant_context()
        app.include_router(router)
        configure_admin_knowledge_services(knowledge_repo=mock_kb_repo)

        with patch(
            "src.multi_tenant.admin_knowledge_api.get_activation_service",
            return_value=mock_activation_svc,
        ):
            client = TestClient(app)
            resp = client.post(
                PREFIX,
                json={
                    "title": "Test Article",
                    "content": "Content here.",
                    "entryType": "faq",
                },
            )

        # KB write should succeed even though signal failed
        assert resp.status_code == 201, resp.text
        assert len(mock_kb_repo._entries) == 1

        configure_admin_knowledge_services(knowledge_repo=None)
