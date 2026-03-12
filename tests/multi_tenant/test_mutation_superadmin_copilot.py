"""Mutation tests for superadmin Co-Pilot knowledge management endpoints.

Covers all 9 mutation endpoints in src/multi_tenant/superadmin_api/_copilot.py:
    POST   /api/superadmin/copilot/documents
    PUT    /api/superadmin/copilot/documents/{doc_id}
    DELETE /api/superadmin/copilot/documents/{doc_id}
    POST   /api/superadmin/copilot/ingest/docs-site
    POST   /api/superadmin/copilot/ingest/url
    POST   /api/superadmin/copilot/re-embed
    POST   /api/superadmin/copilot/test-query
    PUT    /api/superadmin/copilot/config/schedule
    PUT    /api/superadmin/copilot/config/retrieval

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.multi_tenant.conftest import MutationTestBase


# ---------------------------------------------------------------------------
# Helper: existing document fixture data
# ---------------------------------------------------------------------------

EXISTING_DOC = {
    "id": "getting_started:test-doc",
    "document_category": "getting_started",
    "title": "Test Doc",
    "content": "Hello world",
    "section": None,
    "tags": ["intro"],
    "is_active": True,
    "content_hash": "abc123",
    "embedded_at": None,
    "embedding": None,
    "embedding_model": None,
    "source_file": None,
    "created_at": "2026-01-01T00:00:00+00:00",
    "updated_at": "2026-01-01T00:00:00+00:00",
}


# ---------------------------------------------------------------------------
# 1. POST /api/superadmin/copilot/documents — Create document
# ---------------------------------------------------------------------------


class TestCreateCopilotDocument(MutationTestBase):
    URL = "/api/superadmin/copilot/documents"
    BODY = {
        "document_category": "getting_started",
        "title": "Test Doc",
        "content": "Hello world",
    }

    def test_requires_auth(self, app_client, copilot_repos):
        self.assert_requires_auth(app_client, "post", self.URL, json=self.BODY)

    def test_rejects_widget_key(self, widget_client, copilot_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL, json=self.BODY)

    def test_spa_isolation(self, starter_client, copilot_repos):
        self.assert_spa_isolation(starter_client, "post", self.URL, json=self.BODY)

    def test_happy_path(self, spa_client, copilot_repos):
        copilot_repos["admin_doc_repo"].upsert_document = AsyncMock()
        resp = spa_client.post(self.URL, json=self.BODY)
        assert resp.status_code == 201
        data = resp.json()
        assert "documentCategory" in data
        assert data["title"] == "Test Doc"
        assert data["isActive"] is True
        copilot_repos["admin_doc_repo"].upsert_document.assert_awaited_once()


# ---------------------------------------------------------------------------
# 2. PUT /api/superadmin/copilot/documents/{doc_id} — Update document
# ---------------------------------------------------------------------------


class TestUpdateCopilotDocument(MutationTestBase):
    URL = "/api/superadmin/copilot/documents/getting_started:test-doc"
    BODY = {"title": "Updated Title"}

    def test_requires_auth(self, app_client, copilot_repos):
        self.assert_requires_auth(app_client, "put", self.URL, json=self.BODY)

    def test_rejects_widget_key(self, widget_client, copilot_repos):
        self.assert_rejects_widget_key(widget_client, "put", self.URL, json=self.BODY)

    def test_spa_isolation(self, starter_client, copilot_repos):
        self.assert_spa_isolation(starter_client, "put", self.URL, json=self.BODY)

    def test_happy_path(self, spa_client, copilot_repos):
        copilot_repos["admin_doc_repo"].get_by_id = AsyncMock(return_value=EXISTING_DOC)
        copilot_repos["admin_doc_repo"].upsert_document = AsyncMock()
        resp = spa_client.put(self.URL, json=self.BODY)
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Updated Title"
        assert data["content"] == "Hello world"  # preserved from existing

    def test_invalid_doc_id_format(self, spa_client, copilot_repos):
        url = "/api/superadmin/copilot/documents/no-colon-here"
        resp = spa_client.put(url, json=self.BODY)
        assert resp.status_code == 400

    def test_not_found(self, spa_client, copilot_repos):
        copilot_repos["admin_doc_repo"].get_by_id = AsyncMock(return_value=None)
        resp = spa_client.put(self.URL, json=self.BODY)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 3. DELETE /api/superadmin/copilot/documents/{doc_id} — Soft-delete
# ---------------------------------------------------------------------------


class TestDeleteCopilotDocument(MutationTestBase):
    URL = "/api/superadmin/copilot/documents/getting_started:test-doc"

    def test_requires_auth(self, app_client, copilot_repos):
        self.assert_requires_auth(app_client, "delete", self.URL)

    def test_rejects_widget_key(self, widget_client, copilot_repos):
        self.assert_rejects_widget_key(widget_client, "delete", self.URL)

    def test_spa_isolation(self, starter_client, copilot_repos):
        self.assert_spa_isolation(starter_client, "delete", self.URL)

    def test_happy_path(self, spa_client, copilot_repos):
        copilot_repos["admin_doc_repo"].get_by_id = AsyncMock(return_value=EXISTING_DOC)
        copilot_repos["admin_doc_repo"].upsert_document = AsyncMock()
        resp = spa_client.delete(self.URL)
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_active"] is False

    def test_invalid_doc_id_format(self, spa_client, copilot_repos):
        url = "/api/superadmin/copilot/documents/no-colon"
        resp = spa_client.delete(url)
        assert resp.status_code == 400

    def test_not_found(self, spa_client, copilot_repos):
        copilot_repos["admin_doc_repo"].get_by_id = AsyncMock(return_value=None)
        resp = spa_client.delete(self.URL)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 4. POST /api/superadmin/copilot/ingest/docs-site — Ingest from docs-site
# ---------------------------------------------------------------------------


class TestIngestDocsSite(MutationTestBase):
    URL = "/api/superadmin/copilot/ingest/docs-site"

    def test_requires_auth(self, app_client, copilot_repos):
        self.assert_requires_auth(app_client, "post", self.URL)

    def test_rejects_widget_key(self, widget_client, copilot_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL)

    def test_spa_isolation(self, starter_client, copilot_repos):
        self.assert_spa_isolation(starter_client, "post", self.URL)

    @patch("pathlib.Path")
    def test_happy_path(self, mock_path_cls, spa_client, copilot_repos):
        # First Path("docs/admin-guide") exists
        mock_dir = MagicMock()
        mock_dir.exists.return_value = True
        mock_file = MagicMock()
        mock_file.stem = "getting-started"
        mock_file.read_text.return_value = "# Quick Start\nSome content"
        mock_dir.glob.return_value = [mock_file]
        mock_path_cls.return_value = mock_dir

        copilot_repos["admin_doc_repo"].get_by_id = AsyncMock(return_value=None)
        copilot_repos["admin_doc_repo"].upsert_document = AsyncMock()

        resp = spa_client.post(self.URL)
        assert resp.status_code == 200
        data = resp.json()
        assert data["created"] == 1

    @patch("pathlib.Path")
    def test_dir_not_found(self, mock_path_cls, spa_client, copilot_repos):
        mock_dir = MagicMock()
        mock_dir.exists.return_value = False
        mock_path_cls.return_value = mock_dir
        resp = spa_client.post(self.URL)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 5. POST /api/superadmin/copilot/ingest/url — Import URL
# ---------------------------------------------------------------------------


class TestImportUrl(MutationTestBase):
    URL = "/api/superadmin/copilot/ingest/url"
    BODY = {
        "url": "https://example.com/docs/page",
        "document_category": "getting_started",
        "title": "Example Page",
    }

    def test_requires_auth(self, app_client, copilot_repos):
        self.assert_requires_auth(app_client, "post", self.URL, json=self.BODY)

    def test_rejects_widget_key(self, widget_client, copilot_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL, json=self.BODY)

    def test_spa_isolation(self, starter_client, copilot_repos):
        self.assert_spa_isolation(starter_client, "post", self.URL, json=self.BODY)

    @patch("httpx.AsyncClient")
    def test_happy_path(self, mock_client_cls, spa_client, copilot_repos):
        mock_resp = MagicMock()
        mock_resp.text = "# Hello\nTest content"
        mock_resp.raise_for_status = MagicMock()
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client_cls.return_value = mock_client

        copilot_repos["admin_doc_repo"].upsert_document = AsyncMock()

        resp = spa_client.post(self.URL, json=self.BODY)
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Example Page"
        assert data["documentCategory"] == "getting_started"

    def test_rejects_http_url(self, spa_client, copilot_repos):
        body = {**self.BODY, "url": "http://insecure.com/page"}
        resp = spa_client.post(self.URL, json=body)
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# 6. POST /api/superadmin/copilot/re-embed — Re-embed all active docs
# ---------------------------------------------------------------------------


class TestReEmbedDocuments(MutationTestBase):
    URL = "/api/superadmin/copilot/re-embed"

    def test_requires_auth(self, app_client, copilot_repos):
        self.assert_requires_auth(app_client, "post", self.URL)

    def test_rejects_widget_key(self, widget_client, copilot_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL)

    def test_spa_isolation(self, starter_client, copilot_repos):
        self.assert_spa_isolation(starter_client, "post", self.URL)

    @patch(
        "src.multi_tenant.superadmin_api._copilot._generate_embedding",
        new_callable=AsyncMock,
        return_value=[0.1] * 3072,
    )
    def test_happy_path(self, mock_embed, spa_client, copilot_repos):
        copilot_repos["admin_doc_repo"].list_all_active = AsyncMock(
            return_value=[EXISTING_DOC]
        )
        copilot_repos["admin_doc_repo"].upsert_document = AsyncMock()

        resp = spa_client.post(self.URL)
        assert resp.status_code == 200
        data = resp.json()
        assert data["updated"] == 1


# ---------------------------------------------------------------------------
# 7. POST /api/superadmin/copilot/test-query — Test retrieval query
# ---------------------------------------------------------------------------


class TestCopilotTestQuery(MutationTestBase):
    URL = "/api/superadmin/copilot/test-query"
    BODY = {"query": "how do I configure the widget?", "top_k": 3}

    def test_requires_auth(self, app_client, copilot_repos):
        self.assert_requires_auth(app_client, "post", self.URL, json=self.BODY)

    def test_rejects_widget_key(self, widget_client, copilot_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL, json=self.BODY)

    def test_spa_isolation(self, starter_client, copilot_repos):
        self.assert_spa_isolation(starter_client, "post", self.URL, json=self.BODY)

    @patch(
        "src.multi_tenant.superadmin_api._copilot._generate_embedding",
        new_callable=AsyncMock,
        return_value=[0.1] * 3072,
    )
    def test_happy_path(self, mock_embed, spa_client, copilot_repos):
        copilot_repos["admin_doc_repo"].vector_search_all_categories = AsyncMock(
            return_value=[
                {
                    "id": "getting_started:test",
                    "title": "Widget Setup",
                    "document_category": "widget_configuration",
                    "content": "Configure the widget by...",
                    "similarity": 0.95,
                },
            ]
        )
        copilot_repos["admin_doc_repo"].count_all = AsyncMock(return_value=10)

        resp = spa_client.post(self.URL, json=self.BODY)
        assert resp.status_code == 200
        data = resp.json()
        assert data["query"] == "how do I configure the widget?"
        assert len(data["results"]) == 1
        assert data["totalDocuments"] == 10


# ---------------------------------------------------------------------------
# 8. PUT /api/superadmin/copilot/config/schedule — Update scan schedule
# ---------------------------------------------------------------------------


class TestUpdateCopilotSchedule(MutationTestBase):
    URL = "/api/superadmin/copilot/config/schedule"
    BODY = {"scanFrequency": "daily", "scanScope": "both"}

    def test_requires_auth(self, app_client, copilot_repos):
        self.assert_requires_auth(app_client, "put", self.URL, json=self.BODY)

    def test_rejects_widget_key(self, widget_client, copilot_repos):
        self.assert_rejects_widget_key(widget_client, "put", self.URL, json=self.BODY)

    def test_spa_isolation(self, starter_client, copilot_repos):
        self.assert_spa_isolation(starter_client, "put", self.URL, json=self.BODY)

    @patch("src.multi_tenant.superadmin_api._copilot._save_copilot_config", new_callable=AsyncMock)
    def test_happy_path(self, mock_save, spa_client, copilot_repos):
        copilot_repos["admin_doc_repo"].get_by_id = AsyncMock(return_value=None)
        resp = spa_client.put(self.URL, json=self.BODY)
        assert resp.status_code == 200
        data = resp.json()
        assert data["scanFrequency"] == "daily"
        assert data["scanScope"] == "both"
        assert data["nextScanAt"] is not None

    def test_invalid_frequency(self, spa_client, copilot_repos):
        copilot_repos["admin_doc_repo"].get_by_id = AsyncMock(return_value=None)
        body = {"scanFrequency": "hourly", "scanScope": "docs-site"}
        resp = spa_client.put(self.URL, json=body)
        assert resp.status_code == 400

    def test_invalid_scope(self, spa_client, copilot_repos):
        copilot_repos["admin_doc_repo"].get_by_id = AsyncMock(return_value=None)
        body = {"scanFrequency": "daily", "scanScope": "invalid"}
        resp = spa_client.put(self.URL, json=body)
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# 9. PUT /api/superadmin/copilot/config/retrieval — Update retrieval params
# ---------------------------------------------------------------------------


class TestUpdateCopilotRetrievalConfig(MutationTestBase):
    URL = "/api/superadmin/copilot/config/retrieval"
    BODY = {
        "vectorWeight": 0.8,
        "bm25Weight": 0.2,
        "rrfK": 50,
        "topK": 10,
        "minScore": 0.05,
    }

    def test_requires_auth(self, app_client, copilot_repos):
        self.assert_requires_auth(app_client, "put", self.URL, json=self.BODY)

    def test_rejects_widget_key(self, widget_client, copilot_repos):
        self.assert_rejects_widget_key(widget_client, "put", self.URL, json=self.BODY)

    def test_spa_isolation(self, starter_client, copilot_repos):
        self.assert_spa_isolation(starter_client, "put", self.URL, json=self.BODY)

    @patch("src.multi_tenant.superadmin_api._copilot._save_copilot_config", new_callable=AsyncMock)
    def test_happy_path(self, mock_save, spa_client, copilot_repos):
        copilot_repos["admin_doc_repo"].get_by_id = AsyncMock(return_value=None)
        resp = spa_client.put(self.URL, json=self.BODY)
        assert resp.status_code == 200
        data = resp.json()
        assert data["vectorWeight"] == 0.8
        assert data["topK"] == 10

    def test_vector_weight_out_of_range(self, spa_client, copilot_repos):
        copilot_repos["admin_doc_repo"].get_by_id = AsyncMock(return_value=None)
        body = {**self.BODY, "vectorWeight": 1.5}
        resp = spa_client.put(self.URL, json=body)
        assert resp.status_code == 400

    def test_rrf_k_out_of_range(self, spa_client, copilot_repos):
        copilot_repos["admin_doc_repo"].get_by_id = AsyncMock(return_value=None)
        body = {**self.BODY, "rrfK": 0}
        resp = spa_client.put(self.URL, json=body)
        assert resp.status_code == 400

    def test_top_k_out_of_range(self, spa_client, copilot_repos):
        copilot_repos["admin_doc_repo"].get_by_id = AsyncMock(return_value=None)
        body = {**self.BODY, "topK": 25}
        resp = spa_client.put(self.URL, json=body)
        assert resp.status_code == 400
