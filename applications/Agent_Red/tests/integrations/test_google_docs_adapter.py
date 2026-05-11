"""Tests for Google Docs Knowledge Source Adapter (SPEC-1777).

Tests cover:
  - Manifest declaration (capabilities, auth, polling config)
  - list_articles from folder
  - get_article with content extraction
  - search_articles by query
  - Content hash tracking (skip unchanged)
  - Incremental sync via changes.list
  - sync_folder with hash-based dedup
  - Supported MIME types
  - HTTP error mapping
  - Health check
  - Factory registration

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from src.integrations.models import (
    AuthenticationError,
    RateLimitError,
)
from src.integrations.google_docs.adapter import (
    DEFAULT_POLL_INTERVAL,
    EXPORT_MIME,
    FULL_SYNC_INTERVAL,
    INTEGRATION_ID,
    SUPPORTED_MIME_TYPES,
    GoogleDocsAdapter,
)
from src.integrations.google_docs.manifest import GOOGLE_DOCS_MANIFEST
from src.integrations.manifest import (
    AuthType,
    Capability,
    IntegrationCategory,
    SyncStrategy,
)


# ---------------------------------------------------------------------------
# Mock HTTP
# ---------------------------------------------------------------------------


@dataclass
class MockResponse:
    status_code: int = 200
    _json: dict[str, Any] | None = None
    _text: str = ""
    headers: dict[str, str] | None = None

    def json(self) -> dict[str, Any]:
        return self._json or {}

    @property
    def text(self) -> str:
        return self._text


class MockHTTP:
    def __init__(self, responses: list[MockResponse] | None = None):
        self._responses = responses or []
        self._idx = 0
        self.calls: list[tuple] = []

    async def request(self, method, url, headers=None, json=None, params=None):
        self.calls.append((method, url, params or {}))
        if self._idx < len(self._responses):
            resp = self._responses[self._idx]
            self._idx += 1
            return resp
        return MockResponse()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def adapter() -> GoogleDocsAdapter:
    return GoogleDocsAdapter(
        tenant_id="t-1",
        access_token="test-token",
        folder_ids=["folder-1"],
        http_client=MockHTTP(),
    )


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------


class TestManifest:
    def test_integration_id(self):
        assert GOOGLE_DOCS_MANIFEST.integration_id == "google_docs"

    def test_category_is_knowledge(self):
        assert GOOGLE_DOCS_MANIFEST.category == IntegrationCategory.KNOWLEDGE

    def test_auth_type_is_oauth2(self):
        assert GOOGLE_DOCS_MANIFEST.auth_type == AuthType.OAUTH2

    def test_sync_strategy_is_polling(self):
        assert GOOGLE_DOCS_MANIFEST.sync_strategy == SyncStrategy.POLLING

    def test_poll_interval_1_hour(self):
        assert GOOGLE_DOCS_MANIFEST.poll_interval_seconds == 3600

    def test_has_source_articles_capability(self):
        assert GOOGLE_DOCS_MANIFEST.has_capability(Capability.SOURCE_ARTICLES)

    def test_capabilities_count(self):
        assert len(GOOGLE_DOCS_MANIFEST.capabilities) == 1

    def test_tier_gate_professional(self):
        assert GOOGLE_DOCS_MANIFEST.tier_gate == "professional"

    def test_scopes_include_drive_readonly(self):
        scopes = GOOGLE_DOCS_MANIFEST.auth_config.scopes
        assert any("drive.readonly" in s for s in scopes)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


class TestConstants:
    def test_supported_mime_types_count(self):
        assert len(SUPPORTED_MIME_TYPES) == 6

    def test_google_doc_in_supported(self):
        assert "application/vnd.google-apps.document" in SUPPORTED_MIME_TYPES

    def test_google_sheet_in_supported(self):
        assert "application/vnd.google-apps.spreadsheet" in SUPPORTED_MIME_TYPES

    def test_export_mime_doc_to_html(self):
        assert EXPORT_MIME["application/vnd.google-apps.document"] == "text/html"

    def test_export_mime_sheet_to_csv(self):
        assert EXPORT_MIME["application/vnd.google-apps.spreadsheet"] == "text/csv"

    def test_default_poll_interval(self):
        assert DEFAULT_POLL_INTERVAL == 3600

    def test_full_sync_interval(self):
        assert FULL_SYNC_INTERVAL == 86400


# ---------------------------------------------------------------------------
# Protocol methods
# ---------------------------------------------------------------------------


class TestKnowledgeProtocol:
    @pytest.mark.asyncio
    async def test_list_articles(self):
        http = MockHTTP([MockResponse(_json={
            "files": [
                {"id": "f1", "name": "Doc A", "mimeType": "application/vnd.google-apps.document", "modifiedTime": "2026-03-01T10:00:00Z"},
                {"id": "f2", "name": "Sheet B", "mimeType": "application/vnd.google-apps.spreadsheet"},
            ],
            "nextPageToken": None,
        })])
        adapter = GoogleDocsAdapter("t-1", access_token="tok", folder_ids=["folder-1"], http_client=http)
        articles, cursor = await adapter.list_articles("t-1")
        assert len(articles) == 2
        assert articles[0].title == "Doc A"
        assert articles[0].source == INTEGRATION_ID

    @pytest.mark.asyncio
    async def test_list_articles_empty_folders(self):
        adapter = GoogleDocsAdapter("t-1", access_token="tok", folder_ids=[], http_client=MockHTTP())
        articles, cursor = await adapter.list_articles("t-1")
        assert articles == []
        assert cursor is None

    @pytest.mark.asyncio
    async def test_get_article_with_content(self):
        http = MockHTTP([
            MockResponse(_json={
                "id": "f1",
                "name": "Test Doc",
                "mimeType": "application/vnd.google-apps.document",
                "modifiedTime": "2026-03-01T10:00:00Z",
                "webViewLink": "https://docs.google.com/document/d/f1",
            }),
            MockResponse(_text="<h1>Hello</h1><p>World</p>"),
        ])
        adapter = GoogleDocsAdapter("t-1", access_token="tok", http_client=http)
        article = await adapter.get_article("t-1", "f1")
        assert article is not None
        assert article.title == "Test Doc"
        assert "content_hash" in article.metadata

    @pytest.mark.asyncio
    async def test_get_article_not_found(self):
        http = MockHTTP([MockResponse(status_code=404)])
        adapter = GoogleDocsAdapter("t-1", access_token="tok", http_client=http)
        article = await adapter.get_article("t-1", "missing")
        assert article is None

    @pytest.mark.asyncio
    async def test_search_articles(self):
        http = MockHTTP([MockResponse(_json={
            "files": [
                {"id": "f1", "name": "FAQ", "mimeType": "text/plain", "webViewLink": "https://example.com"},
            ],
        })])
        adapter = GoogleDocsAdapter("t-1", access_token="tok", http_client=http)
        results = await adapter.search_articles("t-1", "frequently asked")
        assert len(results) == 1
        assert results[0].title == "FAQ"


# ---------------------------------------------------------------------------
# Content hash tracking
# ---------------------------------------------------------------------------


class TestContentHashing:
    def test_first_check_returns_changed(self):
        adapter = GoogleDocsAdapter("t-1")
        assert adapter._is_content_changed("f1", "hash-a") is True

    def test_same_hash_returns_not_changed(self):
        adapter = GoogleDocsAdapter("t-1")
        adapter._is_content_changed("f1", "hash-a")
        assert adapter._is_content_changed("f1", "hash-a") is False

    def test_different_hash_returns_changed(self):
        adapter = GoogleDocsAdapter("t-1")
        adapter._is_content_changed("f1", "hash-a")
        assert adapter._is_content_changed("f1", "hash-b") is True


# ---------------------------------------------------------------------------
# Sync
# ---------------------------------------------------------------------------


class TestSync:
    @pytest.mark.asyncio
    async def test_sync_folder(self):
        http = MockHTTP([
            # list files
            MockResponse(_json={"files": [
                {"id": "f1", "name": "A", "mimeType": "text/plain"},
            ]}),
            # extract content
            MockResponse(_text="content of A"),
        ])
        adapter = GoogleDocsAdapter("t-1", access_token="tok", http_client=http)
        result = await adapter.sync_folder("folder-1")
        assert result["synced"] == 1
        assert result["total"] == 1

    @pytest.mark.asyncio
    async def test_sync_folder_skips_unchanged(self):
        http = MockHTTP([
            MockResponse(_json={"files": [{"id": "f1", "name": "A", "mimeType": "text/plain"}]}),
            MockResponse(_text="same content"),
            # second call
            MockResponse(_json={"files": [{"id": "f1", "name": "A", "mimeType": "text/plain"}]}),
            MockResponse(_text="same content"),
        ])
        adapter = GoogleDocsAdapter("t-1", access_token="tok", http_client=http)
        r1 = await adapter.sync_folder("folder-1")
        assert r1["synced"] == 1

        r2 = await adapter.sync_folder("folder-1")
        assert r2["skipped"] == 1
        assert r2["synced"] == 0

    @pytest.mark.asyncio
    async def test_incremental_sync_gets_start_token(self):
        http = MockHTTP([
            MockResponse(_json={"startPageToken": "token-1"}),
        ])
        adapter = GoogleDocsAdapter("t-1", access_token="tok", http_client=http)
        result = await adapter.incremental_sync()
        assert result["changes_received"] == 0
        assert adapter._change_token == "token-1"


# ---------------------------------------------------------------------------
# Error mapping
# ---------------------------------------------------------------------------


class TestErrorMapping:
    @pytest.mark.asyncio
    async def test_401_raises_auth_error(self):
        http = MockHTTP([MockResponse(status_code=401)])
        adapter = GoogleDocsAdapter("t-1", access_token="tok", http_client=http)
        with pytest.raises(AuthenticationError):
            await adapter.get_article("t-1", "file-1")

    @pytest.mark.asyncio
    async def test_429_raises_rate_limit(self):
        http = MockHTTP([MockResponse(status_code=429)])
        adapter = GoogleDocsAdapter("t-1", access_token="tok", http_client=http)
        with pytest.raises(RateLimitError):
            await adapter.search_articles("t-1", "query")

    @pytest.mark.asyncio
    async def test_missing_token_raises(self):
        adapter = GoogleDocsAdapter("t-1", http_client=MockHTTP())
        with pytest.raises(AuthenticationError):
            await adapter.search_articles("t-1", "query")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


class TestHealthCheck:
    @pytest.mark.asyncio
    async def test_health_check_success(self):
        http = MockHTTP([MockResponse(_json={"user": {"displayName": "Test"}})])
        adapter = GoogleDocsAdapter("t-1", access_token="tok", http_client=http)
        assert await adapter.health_check("t-1") is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        http = MockHTTP([MockResponse(status_code=401)])
        adapter = GoogleDocsAdapter("t-1", access_token="tok", http_client=http)
        assert await adapter.health_check("t-1") is False


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


class TestFactory:
    def test_google_docs_factory_creates_adapter(self):
        from src.integrations.google_docs import google_docs_factory
        adapter = google_docs_factory("t-1")
        assert isinstance(adapter, GoogleDocsAdapter)
        assert adapter.tenant_id == "t-1"
