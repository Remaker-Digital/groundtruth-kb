"""SPEC-1777 and SPEC-1770 coverage for Google Docs knowledge ingestion."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

import pytest

from src.integrations.google_docs.adapter import (
    DEFAULT_POLL_INTERVAL,
    DRIVE_API_BASE,
    EXPORT_MIME,
    FULL_SYNC_INTERVAL,
    INTEGRATION_ID,
    SUPPORTED_MIME_TYPES,
    GoogleDocsAdapter,
)
from src.integrations.google_docs.manifest import GOOGLE_DOCS_MANIFEST
from src.integrations.knowledge_ingestion import (
    ContentFormat,
    ContentNormalizer,
    KnowledgeIngestionPipeline,
    chunk_text,
)
from src.integrations.manifest import (
    AuthType,
    Capability,
    IntegrationCategory,
    IntegrationStatus,
    SyncStrategy,
)


@dataclass
class MockResponse:
    status_code: int = 200
    payload: dict[str, Any] | None = None
    text_value: str = ""

    def json(self) -> dict[str, Any]:
        return self.payload or {}

    @property
    def text(self) -> str:
        return self.text_value


@dataclass(frozen=True)
class RecordedCall:
    method: str
    url: str
    headers: dict[str, str]
    params: dict[str, str]


class RecordingHTTP:
    def __init__(self, responses: list[MockResponse]) -> None:
        self._responses = responses
        self._index = 0
        self.calls: list[RecordedCall] = []

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
    ) -> MockResponse:
        self.calls.append(RecordedCall(method, url, headers or {}, params or {}))
        if self._index >= len(self._responses):
            return MockResponse()
        response = self._responses[self._index]
        self._index += 1
        return response


def _adapter(http: RecordingHTTP, *, folder_ids: list[str] | None = None) -> GoogleDocsAdapter:
    return GoogleDocsAdapter(
        "tenant-1",
        access_token="unit-test-token",
        folder_ids=folder_ids,
        http_client=http,
    )


def test_spec1777_manifest_and_constants_cover_google_source_setup() -> None:
    assert GOOGLE_DOCS_MANIFEST.integration_id == "google_docs"
    assert GOOGLE_DOCS_MANIFEST.category == IntegrationCategory.KNOWLEDGE
    assert GOOGLE_DOCS_MANIFEST.auth_type == AuthType.OAUTH2
    assert set(GOOGLE_DOCS_MANIFEST.auth_config.scopes) == {
        "https://www.googleapis.com/auth/drive.readonly",
        "https://www.googleapis.com/auth/documents.readonly",
    }
    assert GOOGLE_DOCS_MANIFEST.auth_config.authorize_url == ("https://accounts.google.com/o/oauth2/v2/auth")
    assert GOOGLE_DOCS_MANIFEST.auth_config.token_url == "https://oauth2.googleapis.com/token"
    assert GOOGLE_DOCS_MANIFEST.auth_config.client_id_env == "GOOGLE_CLIENT_ID"
    assert GOOGLE_DOCS_MANIFEST.auth_config.client_secret_env == "GOOGLE_CLIENT_SECRET"
    assert GOOGLE_DOCS_MANIFEST.has_capability(Capability.SOURCE_ARTICLES)
    assert GOOGLE_DOCS_MANIFEST.sync_strategy == SyncStrategy.POLLING
    assert GOOGLE_DOCS_MANIFEST.poll_interval_seconds == 3600
    assert GOOGLE_DOCS_MANIFEST.tier_gate == "professional"
    assert GOOGLE_DOCS_MANIFEST.status == IntegrationStatus.AVAILABLE

    assert SUPPORTED_MIME_TYPES == {
        "application/vnd.google-apps.document": "google_doc",
        "application/vnd.google-apps.spreadsheet": "google_sheet",
        "application/pdf": "pdf",
        "text/plain": "text",
        "text/markdown": "markdown",
        "text/csv": "csv",
    }
    assert EXPORT_MIME == {
        "application/vnd.google-apps.document": "text/html",
        "application/vnd.google-apps.spreadsheet": "text/csv",
    }
    assert DEFAULT_POLL_INTERVAL == 3600
    assert FULL_SYNC_INTERVAL == 86400


@pytest.mark.asyncio
async def test_spec1777_lists_folder_articles_with_supported_mime_filtering() -> None:
    http = RecordingHTTP(
        [
            MockResponse(
                payload={
                    "files": [
                        {
                            "id": "doc-1",
                            "name": "Returns Policy",
                            "mimeType": "application/vnd.google-apps.document",
                            "modifiedTime": "2026-01-01T00:00:00Z",
                        },
                        {
                            "id": "sheet-1",
                            "name": "Shipping Matrix",
                            "mimeType": "application/vnd.google-apps.spreadsheet",
                        },
                    ],
                    "nextPageToken": "cursor-next",
                }
            )
        ]
    )

    articles, cursor = await _adapter(http).list_articles(
        "tenant-1",
        category="folder-selected",
        cursor="cursor-start",
        limit=500,
    )

    assert cursor == "cursor-next"
    assert [article.external_id for article in articles] == ["doc-1", "sheet-1"]
    assert articles[0].source == INTEGRATION_ID
    assert articles[0].title == "Returns Policy"
    assert articles[0].category == "folder-selected"
    assert articles[0].labels == [
        "google_doc",
        "application/vnd.google-apps.document",
    ]
    assert http.calls[0].url == f"{DRIVE_API_BASE}/files"
    assert http.calls[0].params["pageSize"] == "100"
    assert http.calls[0].params["pageToken"] == "cursor-start"
    assert "'folder-selected' in parents" in http.calls[0].params["q"]
    for mime_type in SUPPORTED_MIME_TYPES:
        assert f"mimeType='{mime_type}'" in http.calls[0].params["q"]


@pytest.mark.asyncio
async def test_spec1777_get_article_exports_google_content_and_hashes() -> None:
    html_body = "<h1>Returns</h1><p>Customers can return items.</p>"
    csv_body = "sku,price\nA-1,10"
    http = RecordingHTTP(
        [
            MockResponse(
                payload={
                    "id": "doc-1",
                    "name": "Returns Policy",
                    "mimeType": "application/vnd.google-apps.document",
                    "modifiedTime": "2026-01-01T00:00:00Z",
                    "webViewLink": "https://docs.google.com/document/d/doc-1",
                }
            ),
            MockResponse(text_value=html_body),
            MockResponse(text_value=csv_body),
        ]
    )
    adapter = _adapter(http)

    article = await adapter.get_article("tenant-1", "doc-1")
    sheet_text, sheet_hash = await adapter._extract_content(
        "sheet-1",
        "application/vnd.google-apps.spreadsheet",
    )

    assert article is not None
    assert article.body_text == html_body
    assert article.metadata["content_hash"] == hashlib.sha256(html_body.encode()).hexdigest()
    assert sheet_text == csv_body
    assert sheet_hash == hashlib.sha256(csv_body.encode()).hexdigest()
    assert http.calls[0].url == f"{DRIVE_API_BASE}/files/doc-1"
    assert http.calls[1].url == f"{DRIVE_API_BASE}/files/doc-1/export"
    assert http.calls[1].params == {"mimeType": "text/html"}
    assert http.calls[1].headers["Accept"] == "text/html"
    assert http.calls[2].url == f"{DRIVE_API_BASE}/files/sheet-1/export"
    assert http.calls[2].params == {"mimeType": "text/csv"}
    assert http.calls[2].headers["Accept"] == "text/csv"


@pytest.mark.asyncio
async def test_spec1777_search_uses_drive_full_text_query() -> None:
    http = RecordingHTTP(
        [
            MockResponse(
                payload={
                    "files": [
                        {
                            "id": "txt-1",
                            "name": "FAQ",
                            "mimeType": "text/plain",
                            "webViewLink": "https://drive.example/faq",
                        }
                    ]
                }
            )
        ]
    )

    results = await _adapter(http).search_articles("tenant-1", "refunds", limit=500)

    assert results[0].external_id == "txt-1"
    assert results[0].labels == ["text"]
    assert http.calls[0].url == f"{DRIVE_API_BASE}/files"
    assert http.calls[0].params["pageSize"] == "100"
    assert "fullText contains 'refunds'" in http.calls[0].params["q"]
    assert "trashed=false" in http.calls[0].params["q"]


@pytest.mark.asyncio
async def test_spec1777_sync_tracks_hashes_and_drive_changes() -> None:
    http = RecordingHTTP(
        [
            MockResponse(
                payload={
                    "files": [
                        {
                            "id": "txt-1",
                            "name": "FAQ",
                            "mimeType": "text/plain",
                        }
                    ]
                }
            ),
            MockResponse(text_value="same content"),
            MockResponse(
                payload={
                    "files": [
                        {
                            "id": "txt-1",
                            "name": "FAQ",
                            "mimeType": "text/plain",
                        }
                    ]
                }
            ),
            MockResponse(text_value="same content"),
            MockResponse(payload={"startPageToken": "token-1"}),
            MockResponse(
                payload={
                    "changes": [
                        {
                            "fileId": "txt-2",
                            "file": {
                                "id": "txt-2",
                                "name": "Changed FAQ",
                                "mimeType": "text/plain",
                                "trashed": False,
                            },
                        },
                        {
                            "fileId": "trash-1",
                            "file": {
                                "id": "trash-1",
                                "mimeType": "text/plain",
                                "trashed": True,
                            },
                        },
                        {
                            "fileId": "unsupported-1",
                            "file": {
                                "id": "unsupported-1",
                                "mimeType": "application/zip",
                                "trashed": False,
                            },
                        },
                    ],
                    "newStartPageToken": "token-2",
                }
            ),
            MockResponse(text_value="changed content"),
        ]
    )
    adapter = _adapter(http)

    first_sync = await adapter.sync_folder("folder-1")
    second_sync = await adapter.sync_folder("folder-1")
    initial_incremental = await adapter.incremental_sync()
    changed_incremental = await adapter.incremental_sync()

    assert first_sync == {
        "folder_id": "folder-1",
        "synced": 1,
        "skipped": 0,
        "failed": 0,
        "total": 1,
    }
    assert second_sync["synced"] == 0
    assert second_sync["skipped"] == 1
    assert initial_incremental == {
        "changes_received": 0,
        "processed": 0,
        "skipped": 0,
    }
    assert changed_incremental == {
        "changes_received": 3,
        "processed": 1,
        "skipped": 2,
    }
    assert adapter._change_token == "token-2"
    assert http.calls[4].url == f"{DRIVE_API_BASE}/changes/startPageToken"
    assert http.calls[5].url == f"{DRIVE_API_BASE}/changes"
    assert http.calls[5].params["pageToken"] == "token-1"
    assert http.calls[6].params == {"alt": "media"}


@pytest.mark.asyncio
async def test_spec1770_ingestion_pipeline_normalizes_chunks_and_skips_unchanged() -> None:
    normalizer = ContentNormalizer()
    normalized_html = normalizer.normalize(
        "<h1>Returns</h1><p>Return&nbsp;window is 30 days.</p>",
        ContentFormat.HTML,
        title="Returns Policy",
    )
    normalized_csv = normalizer.normalize(
        "sku,price\nA-1,10\nB-2,20",
        ContentFormat.CSV,
    )
    chunks = chunk_text(
        "Sentence one is useful. " * 120,
        chunk_size=20,
        chunk_overlap=5,
    )
    embed_calls: list[list[str]] = []
    store_calls: list[tuple[str, list[str], list[Any], list[list[float]] | None]] = []

    async def embed_fn(texts: list[str]) -> list[list[float]]:
        embed_calls.append(texts)
        return [[0.1, 0.2, 0.3] for _ in texts]

    async def store_fn(
        tenant_id: str,
        stored_chunks: list[str],
        metadata: list[Any],
        embeddings: list[list[float]] | None,
    ) -> None:
        store_calls.append((tenant_id, stored_chunks, metadata, embeddings))

    pipeline = KnowledgeIngestionPipeline(
        chunk_size=20,
        chunk_overlap=5,
        embed_fn=embed_fn,
        store_fn=store_fn,
    )

    first = await pipeline.ingest_article(
        "tenant-1",
        integration_id="google_docs",
        article_id="doc-1",
        title="Returns Policy",
        content="<h1>Returns</h1><p>" + ("Customers can return items. " * 80) + "</p>",
        content_format=ContentFormat.HTML,
        url="https://docs.google.com/document/d/doc-1",
    )
    second = await pipeline.ingest_article(
        "tenant-1",
        integration_id="google_docs",
        article_id="doc-1",
        title="Returns Policy",
        content="<h1>Returns</h1><p>" + ("Customers can return items. " * 80) + "</p>",
        content_format=ContentFormat.HTML,
        url="https://docs.google.com/document/d/doc-1",
    )

    assert "Returns Policy" in normalized_html
    assert "Return window is 30 days." in normalized_html.replace("\xa0", " ")
    assert normalized_csv == "sku: A-1. price: 10\nsku: B-2. price: 20"
    assert len(chunks) > 1
    assert first.status == "ingested"
    assert first.chunks_created == len(store_calls[0][1])
    assert first.content_hash
    assert second.status == "skipped"
    assert second.content_hash == first.content_hash
    assert len(embed_calls) == 1
    assert len(store_calls) == 1
    tenant_id, stored_chunks, metadata, embeddings = store_calls[0]
    assert tenant_id == "tenant-1"
    assert len(stored_chunks) == len(metadata)
    assert embeddings is not None
    assert len(embeddings) == len(stored_chunks)
    assert metadata[0].integration_id == "google_docs"
    assert metadata[0].article_id == "doc-1"
    assert metadata[0].title == "Returns Policy"
    assert metadata[0].url == "https://docs.google.com/document/d/doc-1"
    assert metadata[0].source_format == "html"
    assert metadata[0].content_hash == first.content_hash
