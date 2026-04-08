"""Mutation tests — Admin Knowledge Base endpoints.

Tests: CRUD, bulk operations, file upload, URL import, verify, conflict scan,
config-vs-KB scan.
All endpoints require tenant admin authentication.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch


from tests.conftest import STARTER_TENANT_ID
from tests.multi_tenant.conftest import MutationTestBase


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

BASE = "/api/admin/knowledge"


def _kb_entry_doc(entry_id: str = "kb-001", **overrides) -> dict:
    """A knowledge base entry document as returned by the repository."""
    doc = {
        "id": entry_id,
        "tenant_id": STARTER_TENANT_ID,
        "entry_type": "article",
        "title": "Shipping Policy",
        "content": "We ship within 3 business days.",
        "metadata": {},
        "tags": ["shipping"],
        "language": "en",
        "is_active": True,
        "category": "Shipping",
        "status": "published",
        "staleness_score": 0.1,
        "staleness_category": "fresh",
        "last_verified_at": "2026-03-01T00:00:00+00:00",
        "embedded_at": "2026-03-01T00:00:00+00:00",
        "source_type": "manual",
        "source_filename": None,
        "source_url": None,
        "created_at": "2026-02-01T00:00:00+00:00",
        "updated_at": "2026-03-01T00:00:00+00:00",
    }
    doc.update(overrides)
    return doc


def _create_payload(**overrides) -> dict:
    """Minimal valid payload for POST /api/admin/knowledge."""
    payload = {
        "title": "Test Article",
        "content": "This is test content for the knowledge base.",
    }
    payload.update(overrides)
    return payload


# ---------------------------------------------------------------------------
# POST /api/admin/knowledge — Create entry
# ---------------------------------------------------------------------------


class TestCreateKnowledge(MutationTestBase):
    """POST /api/admin/knowledge"""

    URL = BASE

    def test_requires_auth(self, app_client, knowledge_repos):
        self.assert_requires_auth(app_client, "post", self.URL, json=_create_payload())

    def test_rejects_widget_key(self, widget_client, knowledge_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL, json=_create_payload())

    def test_spa_isolation(self, spa_client, knowledge_repos):
        """SPA keys should be rejected on tenant admin endpoints."""
        resp = spa_client.post(self.URL, json=_create_payload())
        assert resp.status_code in (401, 403)

    @patch("src.multi_tenant.admin_knowledge_api._signal_kb_draft", new_callable=AsyncMock)
    def test_happy_path(self, mock_signal, starter_client, knowledge_repos):
        knowledge_repos["knowledge_repo"].create = AsyncMock(return_value=_kb_entry_doc())
        resp = starter_client.post(self.URL, json=_create_payload())
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data
        assert data["title"] == "Test Article"

    @patch("src.multi_tenant.admin_knowledge_api._signal_kb_draft", new_callable=AsyncMock)
    def test_with_all_fields(self, mock_signal, starter_client, knowledge_repos):
        knowledge_repos["knowledge_repo"].create = AsyncMock(return_value=_kb_entry_doc())
        payload = _create_payload(
            entryType="faq",
            category="Returns",
            status="published",
            tags=["returns", "refunds"],
            language="en",
        )
        resp = starter_client.post(self.URL, json=payload)
        assert resp.status_code == 201

    def test_missing_title(self, starter_client, knowledge_repos):
        resp = starter_client.post(self.URL, json={"content": "Some content"})
        assert resp.status_code == 422

    def test_missing_content(self, starter_client, knowledge_repos):
        resp = starter_client.post(self.URL, json={"title": "A Title"})
        assert resp.status_code == 422

    def test_empty_body(self, starter_client, knowledge_repos):
        resp = starter_client.post(self.URL, json={})
        assert resp.status_code == 422

    @patch("src.multi_tenant.admin_knowledge_api._signal_kb_draft", new_callable=AsyncMock)
    def test_invalid_entry_type(self, mock_signal, starter_client, knowledge_repos):
        payload = _create_payload(entryType="invalid_type")
        resp = starter_client.post(self.URL, json=payload)
        assert resp.status_code == 400

    @patch("src.multi_tenant.admin_knowledge_api._signal_kb_draft", new_callable=AsyncMock)
    def test_triggers_vectorizer(self, mock_signal, starter_client, knowledge_repos):
        knowledge_repos["knowledge_repo"].create = AsyncMock(return_value=_kb_entry_doc())
        knowledge_repos["knowledge_vectorizer"].embed_entry = AsyncMock()
        resp = starter_client.post(self.URL, json=_create_payload())
        assert resp.status_code == 201
        knowledge_repos["knowledge_vectorizer"].embed_entry.assert_called_once()


# ---------------------------------------------------------------------------
# PUT /api/admin/knowledge/{id} — Update entry
# ---------------------------------------------------------------------------


class TestUpdateKnowledge(MutationTestBase):
    """PUT /api/admin/knowledge/{id}"""

    URL = f"{BASE}/kb-001"

    def test_requires_auth(self, app_client, knowledge_repos):
        self.assert_requires_auth(app_client, "put", self.URL, json={"title": "New"})

    def test_rejects_widget_key(self, widget_client, knowledge_repos):
        self.assert_rejects_widget_key(widget_client, "put", self.URL, json={"title": "New"})

    @patch("src.multi_tenant.admin_knowledge_api._signal_kb_draft", new_callable=AsyncMock)
    def test_happy_path(self, mock_signal, starter_client, knowledge_repos):
        knowledge_repos["knowledge_repo"].read = AsyncMock(return_value=_kb_entry_doc())
        knowledge_repos["knowledge_repo"].patch = AsyncMock()
        resp = starter_client.put(self.URL, json={"title": "Updated Title"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Updated Title"

    @patch("src.multi_tenant.admin_knowledge_api._signal_kb_draft", new_callable=AsyncMock)
    def test_partial_update(self, mock_signal, starter_client, knowledge_repos):
        knowledge_repos["knowledge_repo"].read = AsyncMock(return_value=_kb_entry_doc())
        knowledge_repos["knowledge_repo"].patch = AsyncMock()
        resp = starter_client.put(self.URL, json={"tags": ["new-tag"]})
        assert resp.status_code == 200

    def test_not_found(self, starter_client, knowledge_repos):
        from src.multi_tenant.repository import DocumentNotFoundError

        knowledge_repos["knowledge_repo"].read = AsyncMock(
            side_effect=DocumentNotFoundError("knowledge_base", "kb-001", STARTER_TENANT_ID),
        )
        resp = starter_client.put(self.URL, json={"title": "X"})
        assert resp.status_code == 404

    @patch("src.multi_tenant.admin_knowledge_api._signal_kb_draft", new_callable=AsyncMock)
    def test_invalid_entry_type(self, mock_signal, starter_client, knowledge_repos):
        knowledge_repos["knowledge_repo"].read = AsyncMock(return_value=_kb_entry_doc())
        resp = starter_client.put(self.URL, json={"entryType": "bogus"})
        assert resp.status_code == 400

    @patch("src.multi_tenant.admin_knowledge_api._signal_kb_draft", new_callable=AsyncMock)
    def test_re_embeds_on_content_change(self, mock_signal, starter_client, knowledge_repos):
        knowledge_repos["knowledge_repo"].read = AsyncMock(return_value=_kb_entry_doc())
        knowledge_repos["knowledge_repo"].patch = AsyncMock()
        knowledge_repos["knowledge_vectorizer"].embed_entry = AsyncMock()
        resp = starter_client.put(self.URL, json={"content": "Brand new content"})
        assert resp.status_code == 200
        knowledge_repos["knowledge_vectorizer"].embed_entry.assert_called_once()


# ---------------------------------------------------------------------------
# DELETE /api/admin/knowledge/{id} — Soft-delete
# ---------------------------------------------------------------------------


class TestDeleteKnowledge(MutationTestBase):
    """DELETE /api/admin/knowledge/{id}"""

    URL = f"{BASE}/kb-001"

    def test_requires_auth(self, app_client, knowledge_repos):
        self.assert_requires_auth(app_client, "delete", self.URL)

    def test_rejects_widget_key(self, widget_client, knowledge_repos):
        self.assert_rejects_widget_key(widget_client, "delete", self.URL)

    @patch("src.multi_tenant.admin_knowledge_api._signal_kb_draft", new_callable=AsyncMock)
    def test_happy_path(self, mock_signal, starter_client, knowledge_repos):
        knowledge_repos["knowledge_repo"].soft_delete = AsyncMock()
        resp = starter_client.delete(self.URL)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "kb-001"
        assert "deletedAt" in data

    def test_not_found(self, starter_client, knowledge_repos):
        from src.multi_tenant.repository import DocumentNotFoundError

        knowledge_repos["knowledge_repo"].soft_delete = AsyncMock(
            side_effect=DocumentNotFoundError("knowledge_base", "kb-001", STARTER_TENANT_ID),
        )
        resp = starter_client.delete(self.URL)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/admin/knowledge/upload — File upload
# ---------------------------------------------------------------------------


class TestUploadKnowledge(MutationTestBase):
    """POST /api/admin/knowledge/upload"""

    URL = f"{BASE}/upload"

    def test_requires_auth(self, app_client, knowledge_repos):
        self.assert_requires_auth(
            app_client, "post", self.URL,
            files={"file": ("test.csv", b"title,content\nA,B", "text/csv")},
        )

    def test_rejects_widget_key(self, widget_client, knowledge_repos):
        self.assert_rejects_widget_key(
            widget_client, "post", self.URL,
            files={"file": ("test.csv", b"title,content\nA,B", "text/csv")},
        )

    @patch("src.multi_tenant.admin_knowledge_api._signal_kb_draft", new_callable=AsyncMock)
    @patch("src.multi_tenant.document_parser.chunks_to_kb_entries")
    @patch("src.multi_tenant.document_parser.parse_file")
    @patch("src.multi_tenant.document_parser.validate_file", return_value=None)
    def test_happy_path(
        self, mock_validate, mock_parse, mock_chunks, mock_signal,
        starter_client, knowledge_repos,
    ):
        mock_parse_result = MagicMock()
        mock_parse_result.success = True
        mock_parse_result.source_type = "csv"
        mock_parse_result.total_chars = 100
        mock_parse.return_value = mock_parse_result
        mock_chunks.return_value = [
            {
                "id": "kb-100", "tenant_id": STARTER_TENANT_ID,
                "entry_type": "custom", "title": "Row 1", "content": "Content 1",
                "created_at": "2026-03-12T00:00:00+00:00",
                "updated_at": "2026-03-12T00:00:00+00:00",
            },
        ]
        knowledge_repos["knowledge_repo"].create = AsyncMock()

        resp = starter_client.post(
            self.URL,
            files={"file": ("data.csv", b"title,content\nRow 1,Content 1", "text/csv")},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["entriesCreated"] == 1
        assert data["sourceType"] == "csv"

    def test_empty_file(self, starter_client, knowledge_repos):
        resp = starter_client.post(
            self.URL,
            files={"file": ("empty.csv", b"", "text/csv")},
        )
        assert resp.status_code == 400

    @patch("src.multi_tenant.document_parser.validate_file", return_value=None)
    @patch("src.multi_tenant.document_parser.parse_file")
    def test_parse_failure(self, mock_parse, mock_validate, starter_client, knowledge_repos):
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.error = "Corrupt file"
        mock_parse.return_value = mock_result

        resp = starter_client.post(
            self.URL,
            files={"file": ("bad.pdf", b"not-a-pdf", "application/pdf")},
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /api/admin/knowledge/import-url — URL import
# ---------------------------------------------------------------------------


class TestImportUrl(MutationTestBase):
    """POST /api/admin/knowledge/import-url"""

    URL = f"{BASE}/import-url"

    def test_requires_auth(self, app_client, knowledge_repos):
        self.assert_requires_auth(
            app_client, "post", self.URL,
            json={"url": "https://example.com"},
        )

    def test_rejects_widget_key(self, widget_client, knowledge_repos):
        self.assert_rejects_widget_key(
            widget_client, "post", self.URL,
            json={"url": "https://example.com"},
        )

    @patch("src.multi_tenant.admin_knowledge_api._signal_kb_draft", new_callable=AsyncMock)
    @patch("src.multi_tenant.document_parser.chunks_to_kb_entries")
    @patch("src.multi_tenant.document_parser.parse_url")
    def test_happy_path(
        self, mock_parse, mock_chunks, mock_signal,
        starter_client, knowledge_repos,
    ):
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.total_chars = 500
        mock_parse.return_value = mock_result
        mock_chunks.return_value = [
            {
                "id": "kb-200", "tenant_id": STARTER_TENANT_ID,
                "entry_type": "custom", "title": "Page Title", "content": "Page content",
                "created_at": "2026-03-12T00:00:00+00:00",
                "updated_at": "2026-03-12T00:00:00+00:00",
            },
        ]
        knowledge_repos["knowledge_repo"].create = AsyncMock()

        resp = starter_client.post(self.URL, json={"url": "https://example.com/help"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["entriesCreated"] == 1
        assert data["sourceUrl"] == "https://example.com/help"

    def test_invalid_url_scheme(self, starter_client, knowledge_repos):
        resp = starter_client.post(self.URL, json={"url": "ftp://bad-scheme.com"})
        assert resp.status_code == 400

    def test_invalid_entry_type(self, starter_client, knowledge_repos):
        resp = starter_client.post(
            self.URL,
            json={"url": "https://example.com", "entryType": "bogus"},
        )
        assert resp.status_code == 400

    @patch("src.multi_tenant.document_parser.parse_url")
    def test_parse_failure(self, mock_parse, starter_client, knowledge_repos):
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.error = "Connection refused"
        mock_parse.return_value = mock_result

        resp = starter_client.post(self.URL, json={"url": "https://unreachable.example.com"})
        assert resp.status_code == 422

    @patch("src.multi_tenant.admin_knowledge_api._signal_kb_draft", new_callable=AsyncMock)
    @patch("src.multi_tenant.document_parser.chunks_to_kb_entries")
    @patch("src.multi_tenant.document_parser.crawl_url")
    def test_crawl_mode(
        self, mock_crawl, mock_chunks, mock_signal,
        starter_client, knowledge_repos,
    ):
        page1 = MagicMock()
        page1.total_chars = 300
        page2 = MagicMock()
        page2.total_chars = 200
        mock_crawl.return_value = [page1, page2]
        mock_chunks.side_effect = [
            [{
                "id": "kb-300", "tenant_id": STARTER_TENANT_ID,
                "entry_type": "custom", "title": "P1", "content": "C1",
                "created_at": "2026-03-12T00:00:00+00:00",
                "updated_at": "2026-03-12T00:00:00+00:00",
            }],
            [{
                "id": "kb-301", "tenant_id": STARTER_TENANT_ID,
                "entry_type": "custom", "title": "P2", "content": "C2",
                "created_at": "2026-03-12T00:00:00+00:00",
                "updated_at": "2026-03-12T00:00:00+00:00",
            }],
        ]
        knowledge_repos["knowledge_repo"].create = AsyncMock()

        resp = starter_client.post(
            self.URL,
            json={"url": "https://example.com", "crawl": True, "maxPages": 5},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["entriesCreated"] == 2


# ---------------------------------------------------------------------------
# POST /api/admin/knowledge/{id}/verify — Mark as verified
# ---------------------------------------------------------------------------


class TestVerifyEntry(MutationTestBase):
    """POST /api/admin/knowledge/{id}/verify"""

    URL = f"{BASE}/kb-001/verify"

    def test_requires_auth(self, app_client, knowledge_repos):
        self.assert_requires_auth(app_client, "post", self.URL)

    def test_rejects_widget_key(self, widget_client, knowledge_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL)

    def test_happy_path(self, starter_client, knowledge_repos):
        knowledge_repos["staleness_service"].verify_entry = AsyncMock(
            return_value={
                "id": "kb-001",
                "staleness_score": 0.0,
                "staleness_category": "fresh",
                "last_verified_at": "2026-03-12T00:00:00+00:00",
                "embedded_at": "2026-03-01T00:00:00+00:00",
            },
        )
        resp = starter_client.post(self.URL)
        assert resp.status_code == 200
        data = resp.json()
        assert data["stalenessScore"] == 0.0
        assert data["stalenessCategory"] == "fresh"

    def test_not_found(self, starter_client, knowledge_repos):
        knowledge_repos["staleness_service"].verify_entry = AsyncMock(
            side_effect=Exception("Entry not found"),
        )
        resp = starter_client.post(self.URL)
        assert resp.status_code == 404

    def test_staleness_service_unavailable(self, starter_client):
        """503 when staleness service is not configured."""
        from src.multi_tenant.admin_knowledge_api import configure_admin_knowledge_services

        repo_mock = AsyncMock()
        configure_admin_knowledge_services(
            knowledge_repo=repo_mock,
            staleness_service=None,
        )
        try:
            resp = starter_client.post(self.URL)
            assert resp.status_code == 503
        finally:
            configure_admin_knowledge_services(knowledge_repo=None)


# ---------------------------------------------------------------------------
# POST /api/admin/knowledge/scan — Trigger conflict scan
# ---------------------------------------------------------------------------


class TestScanConflicts(MutationTestBase):
    """POST /api/admin/knowledge/scan"""

    URL = f"{BASE}/scan"

    def test_requires_auth(self, app_client, knowledge_repos):
        self.assert_requires_auth(app_client, "post", self.URL)

    def test_rejects_widget_key(self, widget_client, knowledge_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL)

    def test_happy_path(self, starter_client, knowledge_repos):
        scan_result = MagicMock()
        scan_result.tenant_id = STARTER_TENANT_ID
        scan_result.scanned_at = "2026-03-12T00:00:00+00:00"
        scan_result.total_entries_scanned = 10
        scan_result.entries_with_embeddings = 8
        scan_result.entries_without_embeddings = 2
        scan_result.conflicts = []
        scan_result.high_count = 0
        scan_result.medium_count = 0
        scan_result.low_count = 0
        scan_result.scan_duration_ms = 150
        knowledge_repos["conflict_scanner"].scan = AsyncMock(return_value=scan_result)

        resp = starter_client.post(self.URL)
        assert resp.status_code == 200
        data = resp.json()
        assert data["totalEntriesScanned"] == 10
        assert data["conflicts"] == []

    def test_scanner_unavailable(self, starter_client):
        """503 when conflict scanner is not configured."""
        from src.multi_tenant.admin_knowledge_api import configure_admin_knowledge_services

        repo_mock = AsyncMock()
        configure_admin_knowledge_services(
            knowledge_repo=repo_mock,
            conflict_scanner=None,
        )
        try:
            resp = starter_client.post(self.URL)
            assert resp.status_code == 503
        finally:
            configure_admin_knowledge_services(knowledge_repo=None)


# ---------------------------------------------------------------------------
# POST /api/admin/knowledge/scan/config — Config-vs-KB conflict check
# ---------------------------------------------------------------------------


class TestScanConfigConflicts(MutationTestBase):
    """POST /api/admin/knowledge/scan/config"""

    URL = f"{BASE}/scan/config"

    def test_requires_auth(self, app_client, knowledge_repos):
        self.assert_requires_auth(app_client, "post", self.URL, json={})

    def test_rejects_widget_key(self, widget_client, knowledge_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL, json={})

    def test_happy_path(self, starter_client, knowledge_repos):
        config_result = MagicMock()
        config_result.tenant_id = STARTER_TENANT_ID
        config_result.scanned_at = "2026-03-12T00:00:00+00:00"
        config_result.config_fields_checked = 2
        config_result.articles_checked = 5
        config_result.conflicts = []
        config_result.scan_duration_ms = 50
        knowledge_repos["conflict_scanner"].scan_config_conflicts = AsyncMock(
            return_value=config_result,
        )

        resp = starter_client.post(
            self.URL,
            json={"returnPolicy": "30-day returns", "shippingInfo": "Free over $50"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["configFieldsChecked"] == 2
        assert data["articlesChecked"] == 5

    def test_empty_body(self, starter_client, knowledge_repos):
        """Empty body is valid — scanner checks zero fields."""
        config_result = MagicMock()
        config_result.tenant_id = STARTER_TENANT_ID
        config_result.scanned_at = "2026-03-12T00:00:00+00:00"
        config_result.config_fields_checked = 0
        config_result.articles_checked = 0
        config_result.conflicts = []
        config_result.scan_duration_ms = 5
        knowledge_repos["conflict_scanner"].scan_config_conflicts = AsyncMock(
            return_value=config_result,
        )

        resp = starter_client.post(self.URL, json={})
        assert resp.status_code == 200

    def test_scanner_unavailable(self, starter_client):
        """503 when conflict scanner is not configured."""
        from src.multi_tenant.admin_knowledge_api import configure_admin_knowledge_services

        repo_mock = AsyncMock()
        configure_admin_knowledge_services(
            knowledge_repo=repo_mock,
            conflict_scanner=None,
        )
        try:
            resp = starter_client.post(self.URL, json={"returnPolicy": "X"})
            assert resp.status_code == 503
        finally:
            configure_admin_knowledge_services(knowledge_repo=None)
