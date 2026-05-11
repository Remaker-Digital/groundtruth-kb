# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Google Docs/Drive Knowledge Source Adapter (SPEC-1777).

KnowledgeAdapter implementation for Google Docs and Drive.
Auth: OAuth2 with drive.readonly + documents.readonly scopes.
Sync: Polling via Drive changes.list (incremental), daily full sweep.

Supported file types:
  - Google Docs  → export as HTML → normalize → chunk
  - Google Sheets → export as CSV → normalize
  - PDF, TXT, MD, CSV → download raw content

Content-hash tracking prevents re-processing unchanged documents.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime
from typing import Any

from src.integrations.models import (
    AuthenticationError,
    IntegrationError,
    NormalizedArticle,
    RateLimitError,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

INTEGRATION_ID = "google_docs"
DRIVE_API_BASE = "https://www.googleapis.com/drive/v3"
DOCS_API_BASE = "https://docs.googleapis.com/v1"

# MIME types we can ingest
SUPPORTED_MIME_TYPES: dict[str, str] = {
    "application/vnd.google-apps.document": "google_doc",
    "application/vnd.google-apps.spreadsheet": "google_sheet",
    "application/pdf": "pdf",
    "text/plain": "text",
    "text/markdown": "markdown",
    "text/csv": "csv",
}

# Export MIME for Google native formats
EXPORT_MIME: dict[str, str] = {
    "application/vnd.google-apps.document": "text/html",
    "application/vnd.google-apps.spreadsheet": "text/csv",
}

# Default polling interval (seconds)
DEFAULT_POLL_INTERVAL = 3600  # 1 hour
FULL_SYNC_INTERVAL = 86400  # 24 hours (daily full sweep)


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------


class GoogleDocsAdapter:
    """Knowledge source adapter for Google Docs/Drive (SPEC-1777).

    Implements KnowledgeAdapter protocol.  All Google API calls go
    through ``_request()`` which handles auth and error mapping.
    """

    def __init__(
        self,
        tenant_id: str,
        *,
        access_token: str = "",
        folder_ids: list[str] | None = None,
        http_client: Any = None,
    ) -> None:
        self.tenant_id = tenant_id
        self.access_token = access_token
        self.folder_ids = folder_ids or []
        self._http = http_client
        self._change_token: str | None = None  # Drive changes.list page token
        self._content_hashes: dict[str, str] = {}  # file_id → sha256 of content

    # -- HTTP layer ---------------------------------------------------------

    async def _request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, str] | None = None,
        accept: str = "application/json",
    ) -> Any:
        """Execute an authenticated Google API request."""
        if not self.access_token:
            raise AuthenticationError(
                "Google Docs not configured (missing access token)",
                integration_id=INTEGRATION_ID,
            )

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": accept,
        }

        if self._http is not None:
            response = await self._http.request(
                method, url, headers=headers, params=params or {}
            )
        else:
            raise IntegrationError(
                "No HTTP client configured",
                integration_id=INTEGRATION_ID,
            )

        status = getattr(response, "status_code", getattr(response, "status", 0))

        if status == 401 or status == 403:
            raise AuthenticationError(
                f"Google auth failed ({status})",
                integration_id=INTEGRATION_ID,
            )
        if status == 429:
            raise RateLimitError(
                "Google API rate limit exceeded",
                integration_id=INTEGRATION_ID,
                retry_after_seconds=60.0,
            )
        if status >= 400:
            raise IntegrationError(
                f"Google API error ({status}): {url}",
                integration_id=INTEGRATION_ID,
                status_code=status,
                retryable=status >= 500,
            )

        if accept == "application/json":
            return getattr(response, "json", lambda: {})()
        return getattr(response, "text", "")

    # -- File listing -------------------------------------------------------

    async def _list_files_in_folder(
        self,
        folder_id: str,
        *,
        page_token: str | None = None,
        page_size: int = 100,
    ) -> tuple[list[dict[str, Any]], str | None]:
        """List files in a Drive folder."""
        mime_filter = " or ".join(
            f"mimeType='{m}'" for m in SUPPORTED_MIME_TYPES
        )
        query = f"'{folder_id}' in parents and ({mime_filter}) and trashed=false"

        params: dict[str, str] = {
            "q": query,
            "pageSize": str(min(page_size, 100)),
            "fields": "nextPageToken,files(id,name,mimeType,modifiedTime,md5Checksum,size)",
        }
        if page_token:
            params["pageToken"] = page_token

        data = await self._request("GET", f"{DRIVE_API_BASE}/files", params=params)
        return data.get("files", []), data.get("nextPageToken")

    async def _get_changes(
        self,
    ) -> tuple[list[dict[str, Any]], str | None]:
        """Get incremental changes via Drive changes.list API."""
        if not self._change_token:
            # Get initial start page token
            data = await self._request(
                "GET",
                f"{DRIVE_API_BASE}/changes/startPageToken",
            )
            self._change_token = data.get("startPageToken", "")
            return [], self._change_token

        params = {
            "pageToken": self._change_token,
            "fields": "nextPageToken,newStartPageToken,changes(fileId,file(id,name,mimeType,modifiedTime,trashed))",
            "pageSize": "100",
        }
        data = await self._request(
            "GET", f"{DRIVE_API_BASE}/changes", params=params
        )

        new_token = data.get("newStartPageToken", data.get("nextPageToken"))
        if new_token:
            self._change_token = new_token

        return data.get("changes", []), new_token

    # -- Content extraction -------------------------------------------------

    async def _extract_content(
        self, file_id: str, mime_type: str
    ) -> tuple[str, str]:
        """Extract text content from a file.

        Returns (body_text, content_hash).
        """
        export_mime = EXPORT_MIME.get(mime_type)

        if export_mime:
            # Google native format → export
            content = await self._request(
                "GET",
                f"{DRIVE_API_BASE}/files/{file_id}/export",
                params={"mimeType": export_mime},
                accept=export_mime,
            )
        else:
            # Binary/text file → download
            content = await self._request(
                "GET",
                f"{DRIVE_API_BASE}/files/{file_id}",
                params={"alt": "media"},
                accept="text/plain",
            )

        text = str(content) if content else ""
        content_hash = hashlib.sha256(text.encode()).hexdigest()
        return text, content_hash

    def _is_content_changed(self, file_id: str, content_hash: str) -> bool:
        """Check if content has changed since last sync."""
        previous = self._content_hashes.get(file_id)
        if previous == content_hash:
            return False
        self._content_hashes[file_id] = content_hash
        return True

    # -- KnowledgeAdapter protocol ------------------------------------------

    async def list_articles(
        self,
        tenant_id: str,
        *,
        cursor: str | None = None,
        limit: int = 100,
        category: str | None = None,
    ) -> tuple[list[NormalizedArticle], str | None]:
        """List articles from configured Drive folders."""
        all_articles: list[NormalizedArticle] = []
        next_cursor: str | None = None

        folder_ids = [category] if category else self.folder_ids
        if not folder_ids:
            return [], None

        for folder_id in folder_ids:
            files, page_token = await self._list_files_in_folder(
                folder_id, page_token=cursor, page_size=limit
            )
            for f in files:
                mime_type = f.get("mimeType", "")
                file_type = SUPPORTED_MIME_TYPES.get(mime_type, "unknown")

                all_articles.append(
                    NormalizedArticle(
                        external_id=f.get("id", ""),
                        source=INTEGRATION_ID,
                        title=f.get("name", ""),
                        body_text="",  # Populated on get_article()
                        url=f"https://docs.google.com/document/d/{f.get('id', '')}",
                        category=folder_id,
                        labels=[file_type, mime_type],
                        last_modified=_parse_dt(f.get("modifiedTime")),
                    )
                )

            if page_token:
                next_cursor = page_token

        return all_articles[:limit], next_cursor

    async def get_article(
        self, tenant_id: str, article_id: str
    ) -> NormalizedArticle | None:
        """Get a single article with full content."""
        try:
            # Get file metadata
            params = {"fields": "id,name,mimeType,modifiedTime,webViewLink"}
            data = await self._request(
                "GET", f"{DRIVE_API_BASE}/files/{article_id}", params=params
            )

            mime_type = data.get("mimeType", "")
            if mime_type not in SUPPORTED_MIME_TYPES:
                return None

            body_text, content_hash = await self._extract_content(
                article_id, mime_type
            )

            file_type = SUPPORTED_MIME_TYPES.get(mime_type, "unknown")

            return NormalizedArticle(
                external_id=data.get("id", article_id),
                source=INTEGRATION_ID,
                title=data.get("name", ""),
                body_text=body_text,
                url=data.get("webViewLink", ""),
                labels=[file_type, mime_type],
                last_modified=_parse_dt(data.get("modifiedTime")),
                metadata={"content_hash": content_hash},
            )
        except IntegrationError as e:
            if e.status_code == 404:
                return None
            raise

    async def search_articles(
        self, tenant_id: str, query: str, *, limit: int = 25
    ) -> list[NormalizedArticle]:
        """Search Drive files by query string."""
        mime_filter = " or ".join(
            f"mimeType='{m}'" for m in SUPPORTED_MIME_TYPES
        )
        full_query = f"fullText contains '{query}' and ({mime_filter}) and trashed=false"

        params: dict[str, str] = {
            "q": full_query,
            "pageSize": str(min(limit, 100)),
            "fields": "files(id,name,mimeType,modifiedTime,webViewLink)",
        }

        data = await self._request(
            "GET", f"{DRIVE_API_BASE}/files", params=params
        )

        articles = []
        for f in data.get("files", []):
            file_type = SUPPORTED_MIME_TYPES.get(f.get("mimeType", ""), "unknown")
            articles.append(
                NormalizedArticle(
                    external_id=f.get("id", ""),
                    source=INTEGRATION_ID,
                    title=f.get("name", ""),
                    url=f.get("webViewLink", ""),
                    labels=[file_type],
                    last_modified=_parse_dt(f.get("modifiedTime")),
                )
            )
        return articles

    async def health_check(self, tenant_id: str) -> bool:
        """Check connectivity by listing Drive about info."""
        try:
            await self._request(
                "GET",
                f"{DRIVE_API_BASE}/about",
                params={"fields": "user"},
            )
            return True
        except Exception:
            return False

    # -- Sync helpers -------------------------------------------------------

    async def sync_folder(
        self, folder_id: str
    ) -> dict[str, Any]:
        """Sync a single folder: extract content, track hashes.

        Returns sync summary with counts.
        """
        articles_synced = 0
        articles_skipped = 0
        articles_failed = 0

        files, _ = await self._list_files_in_folder(folder_id, page_size=100)

        for f in files:
            file_id = f.get("id", "")
            mime_type = f.get("mimeType", "")

            try:
                body_text, content_hash = await self._extract_content(
                    file_id, mime_type
                )
                if self._is_content_changed(file_id, content_hash):
                    articles_synced += 1
                else:
                    articles_skipped += 1
            except Exception:
                articles_failed += 1
                logger.exception(
                    "Failed to sync file %s from folder %s",
                    file_id,
                    folder_id,
                )

        return {
            "folder_id": folder_id,
            "synced": articles_synced,
            "skipped": articles_skipped,
            "failed": articles_failed,
            "total": len(files),
        }

    async def incremental_sync(self) -> dict[str, Any]:
        """Run an incremental sync using Drive changes.list.

        Returns sync summary.
        """
        changes, _ = await self._get_changes()
        processed = 0
        skipped = 0

        for change in changes:
            file_info = change.get("file", {})
            if file_info.get("trashed"):
                skipped += 1
                continue

            mime_type = file_info.get("mimeType", "")
            if mime_type not in SUPPORTED_MIME_TYPES:
                skipped += 1
                continue

            file_id = change.get("fileId", "")
            try:
                body_text, content_hash = await self._extract_content(
                    file_id, mime_type
                )
                if self._is_content_changed(file_id, content_hash):
                    processed += 1
                else:
                    skipped += 1
            except Exception:
                logger.exception("Failed to process change for %s", file_id)

        return {
            "changes_received": len(changes),
            "processed": processed,
            "skipped": skipped,
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_dt(value: str | None) -> datetime | None:
    """Parse an ISO 8601 datetime string, returning None on failure."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None
