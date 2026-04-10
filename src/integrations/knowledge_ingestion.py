# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Multi-Source Knowledge Ingestion Pipeline (SPEC-1770).

Extends the knowledge vectorizer with content normalization from diverse
formats and an incremental ingestion pipeline for integration-sourced articles.

Pipeline stages:
1. Normalize → plaintext from HTML, Markdown, Notion blocks, etc.
2. Chunk → 512-token segments with 50-token overlap
3. Hash → content_hash for incremental change detection
4. Embed → text-embedding-3-large (via knowledge_vectorizer)
5. Store → Cosmos DiskANN with source attribution metadata

Integration-sourced articles appear in admin KB alongside manually added ones.
They are distinguished by source field and are read-only in the admin UI.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import html
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_CHUNK_SIZE = 512       # tokens per chunk
DEFAULT_CHUNK_OVERLAP = 50     # overlap tokens between chunks
CHARS_PER_TOKEN = 4            # rough English approximation
MAX_CONTENT_LENGTH = 500_000   # safety limit: 500K chars


# ---------------------------------------------------------------------------
# Content format enum
# ---------------------------------------------------------------------------


class ContentFormat(str, Enum):
    """Supported content formats for normalization."""

    HTML = "html"
    MARKDOWN = "markdown"
    PLAINTEXT = "plaintext"
    NOTION_BLOCKS = "notion_blocks"
    CONFLUENCE_STORAGE = "confluence_storage"
    CSV = "csv"


# ---------------------------------------------------------------------------
# Content Normalizer
# ---------------------------------------------------------------------------


class ContentNormalizer:
    """Normalizes diverse content formats to plaintext for embedding.

    Supports HTML, Markdown, Notion blocks, Confluence storage format,
    and CSV.  Falls back to plaintext passthrough for unknown formats.
    """

    def normalize(
        self,
        content: str,
        fmt: ContentFormat | str = ContentFormat.PLAINTEXT,
        *,
        title: str = "",
    ) -> str:
        """Normalize content to plaintext.

        Args:
            content: Raw content string (or JSON string for Notion blocks).
            fmt: Content format identifier.
            title: Optional title to prepend.

        Returns:
            Cleaned plaintext suitable for embedding.
        """
        if isinstance(fmt, str):
            try:
                fmt = ContentFormat(fmt)
            except ValueError:
                fmt = ContentFormat.PLAINTEXT

        if not content:
            return title.strip() if title else ""

        # Truncate excessively large content
        if len(content) > MAX_CONTENT_LENGTH:
            content = content[:MAX_CONTENT_LENGTH]
            logger.warning(
                "Content truncated to %d chars for normalization",
                MAX_CONTENT_LENGTH,
            )

        normalizer_map = {
            ContentFormat.HTML: self._normalize_html,
            ContentFormat.MARKDOWN: self._normalize_markdown,
            ContentFormat.PLAINTEXT: self._normalize_plaintext,
            ContentFormat.NOTION_BLOCKS: self._normalize_notion,
            ContentFormat.CONFLUENCE_STORAGE: self._normalize_confluence,
            ContentFormat.CSV: self._normalize_csv,
        }

        normalizer = normalizer_map.get(fmt, self._normalize_plaintext)
        text = normalizer(content)

        if title:
            text = f"{title.strip()}\n\n{text}"

        return self._clean_whitespace(text)

    # -- Format-specific normalizers ----------------------------------------

    def _normalize_html(self, content: str) -> str:
        """Strip HTML tags and decode entities."""
        # Remove script and style blocks entirely
        content = re.sub(
            r"<(script|style)[^>]*>.*?</\1>", "", content, flags=re.DOTALL | re.IGNORECASE
        )
        # Replace block elements with newlines
        content = re.sub(
            r"</(p|div|h[1-6]|li|tr|br|hr)[^>]*>", "\n", content, flags=re.IGNORECASE
        )
        content = re.sub(r"<br\s*/?>", "\n", content, flags=re.IGNORECASE)
        # Strip remaining tags
        content = re.sub(r"<[^>]+>", " ", content)
        # Decode HTML entities
        content = html.unescape(content)
        return content

    def _normalize_markdown(self, content: str) -> str:
        """Strip Markdown formatting to plaintext."""
        # Remove images: ![alt](url)
        content = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", content)
        # Convert links: [text](url) -> text
        content = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", content)
        # Remove headers markers
        content = re.sub(r"^#{1,6}\s+", "", content, flags=re.MULTILINE)
        # Remove bold/italic markers
        content = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", content)
        content = re.sub(r"_{1,3}([^_]+)_{1,3}", r"\1", content)
        # Remove code fences
        content = re.sub(r"```[^\n]*\n(.*?)```", r"\1", content, flags=re.DOTALL)
        content = re.sub(r"`([^`]+)`", r"\1", content)
        # Remove blockquote markers
        content = re.sub(r"^>\s?", "", content, flags=re.MULTILINE)
        # Remove horizontal rules
        content = re.sub(r"^[-*_]{3,}\s*$", "", content, flags=re.MULTILINE)
        # Remove list markers
        content = re.sub(r"^[\s]*[-*+]\s+", "", content, flags=re.MULTILINE)
        content = re.sub(r"^[\s]*\d+\.\s+", "", content, flags=re.MULTILINE)
        return content

    def _normalize_plaintext(self, content: str) -> str:
        """Passthrough with basic cleanup."""
        return content

    def _normalize_notion(self, content: str) -> str:
        """Extract text from Notion block JSON (simplified).

        Expects a JSON string of Notion block objects.  Extracts
        rich_text content from paragraph, heading, and list blocks.
        """
        import json

        try:
            blocks = json.loads(content) if isinstance(content, str) else content
        except (json.JSONDecodeError, TypeError):
            return content  # fallback to raw text

        if not isinstance(blocks, list):
            return str(blocks)

        texts: list[str] = []
        for block in blocks:
            if not isinstance(block, dict):
                continue
            block_type = block.get("type", "")
            block_data = block.get(block_type, {})
            if isinstance(block_data, dict):
                rich_texts = block_data.get("rich_text", [])
                for rt in rich_texts:
                    if isinstance(rt, dict):
                        texts.append(rt.get("plain_text", ""))
            # Recurse into children
            children = block.get("children", [])
            if children:
                texts.append(self._normalize_notion(json.dumps(children)))

        return "\n".join(texts)

    def _normalize_confluence(self, content: str) -> str:
        """Normalize Confluence storage format (XHTML subset)."""
        # Confluence storage format is XML/XHTML — treat as HTML
        # Remove Confluence macros
        content = re.sub(
            r"<ac:[^>]+>.*?</ac:[^>]+>", " ", content, flags=re.DOTALL
        )
        content = re.sub(r"<ac:[^>]+/>", " ", content)
        # Remove ri: resource identifiers
        content = re.sub(r"<ri:[^>]+/>", " ", content)
        return self._normalize_html(content)

    def _normalize_csv(self, content: str) -> str:
        """Convert CSV rows to readable text."""
        lines = content.strip().split("\n")
        if not lines:
            return ""

        # First line is headers
        headers = [h.strip().strip('"') for h in lines[0].split(",")]
        texts: list[str] = []

        for line in lines[1:]:
            values = [v.strip().strip('"') for v in line.split(",")]
            row_parts = []
            for h, v in zip(headers, values):
                if v:
                    row_parts.append(f"{h}: {v}")
            if row_parts:
                texts.append(". ".join(row_parts))

        return "\n".join(texts)

    # -- Cleanup -----------------------------------------------------------

    @staticmethod
    def _clean_whitespace(text: str) -> str:
        """Normalize whitespace: collapse runs, trim lines, max 2 newlines."""
        # Replace tabs with spaces
        text = text.replace("\t", " ")
        # Collapse multiple spaces
        text = re.sub(r" {2,}", " ", text)
        # Trim each line
        text = "\n".join(line.strip() for line in text.split("\n"))
        # Collapse 3+ consecutive newlines to 2
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


# ---------------------------------------------------------------------------
# Chunker
# ---------------------------------------------------------------------------


def chunk_text(
    text: str,
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    """Split text into token-approximate chunks with overlap.

    Uses character-based approximation (CHARS_PER_TOKEN) rather than
    a full tokenizer for speed.  Chunks break at sentence boundaries
    when possible to preserve readability.

    Args:
        text: Input plaintext.
        chunk_size: Target tokens per chunk.
        chunk_overlap: Overlap tokens between consecutive chunks.

    Returns:
        List of text chunks.
    """
    if not text.strip():
        return []

    chunk_chars = chunk_size * CHARS_PER_TOKEN
    overlap_chars = chunk_overlap * CHARS_PER_TOKEN

    if len(text) <= chunk_chars:
        return [text]

    # Split into sentences for cleaner boundaries
    sentences = re.split(r"(?<=[.!?])\s+", text)

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for sentence in sentences:
        sent_len = len(sentence)

        if current_len + sent_len > chunk_chars and current:
            # Emit current chunk
            chunk_text_str = " ".join(current)
            chunks.append(chunk_text_str)

            # Build overlap from the tail of current chunk
            overlap: list[str] = []
            overlap_len = 0
            for s in reversed(current):
                if overlap_len + len(s) > overlap_chars:
                    break
                overlap.insert(0, s)
                overlap_len += len(s)

            current = overlap + [sentence]
            current_len = overlap_len + sent_len
        else:
            current.append(sentence)
            current_len += sent_len

    # Final chunk
    if current:
        chunks.append(" ".join(current))

    return chunks


# ---------------------------------------------------------------------------
# Ingestion metadata
# ---------------------------------------------------------------------------


@dataclass
class IngestionMetadata:
    """Metadata attached to each ingested chunk for attribution."""

    integration_id: str
    article_id: str
    title: str
    url: str = ""
    source_format: str = "plaintext"
    chunk_index: int = 0
    total_chunks: int = 1
    content_hash: str = ""


@dataclass
class IngestionResult:
    """Result of ingesting a single article."""

    article_id: str
    integration_id: str
    status: str = "ingested"  # ingested, skipped, failed
    chunks_created: int = 0
    content_hash: str = ""
    error: str = ""


@dataclass
class SyncResult:
    """Result of syncing an entire integration source."""

    integration_id: str
    articles_processed: int = 0
    articles_ingested: int = 0
    articles_skipped: int = 0
    articles_failed: int = 0
    total_chunks: int = 0
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Knowledge Ingestion Pipeline
# ---------------------------------------------------------------------------


class KnowledgeIngestionPipeline:
    """Multi-source knowledge ingestion extending knowledge_vectorizer.

    Pipeline: normalize → chunk → hash → embed → store.

    Supports incremental sync: content hash comparison skips unchanged
    articles to minimize embedding API calls.
    """

    def __init__(
        self,
        normalizer: ContentNormalizer | None = None,
        *,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
        embed_fn: Any = None,
        store_fn: Any = None,
        delete_fn: Any = None,
        get_hash_fn: Any = None,
    ) -> None:
        """Initialize the pipeline.

        Args:
            normalizer: Content normalizer instance.
            chunk_size: Target tokens per chunk.
            chunk_overlap: Overlap tokens between chunks.
            embed_fn: Async callable(texts: list[str]) -> list[list[float]].
            store_fn: Async callable(tenant_id, chunks, metadata) -> None.
            delete_fn: Async callable(tenant_id, article_id) -> int deleted.
            get_hash_fn: Async callable(tenant_id, article_id) -> str | None.
        """
        self._normalizer = normalizer or ContentNormalizer()
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._embed_fn = embed_fn
        self._store_fn = store_fn
        self._delete_fn = delete_fn
        self._get_hash_fn = get_hash_fn
        # In-memory hash cache for testing / simple deployments
        self._hash_cache: dict[str, str] = {}

    def _compute_hash(self, text: str) -> str:
        """Compute content hash for change detection."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    async def _get_stored_hash(
        self, tenant_id: str, article_id: str
    ) -> str | None:
        """Get the previously stored content hash for an article."""
        if self._get_hash_fn:
            return await self._get_hash_fn(tenant_id, article_id)
        cache_key = f"{tenant_id}:{article_id}"
        return self._hash_cache.get(cache_key)

    async def _store_hash(
        self, tenant_id: str, article_id: str, content_hash: str
    ) -> None:
        """Store the content hash after successful ingestion."""
        cache_key = f"{tenant_id}:{article_id}"
        self._hash_cache[cache_key] = content_hash

    async def ingest_article(
        self,
        tenant_id: str,
        *,
        integration_id: str,
        article_id: str,
        title: str,
        content: str,
        content_format: ContentFormat | str = ContentFormat.PLAINTEXT,
        url: str = "",
    ) -> IngestionResult:
        """Ingest a single article through the pipeline.

        Normalizes, chunks, checks content hash for changes, embeds,
        and stores with source attribution metadata.

        Args:
            tenant_id: Tenant identifier.
            integration_id: Source integration ID.
            article_id: External article ID.
            title: Article title.
            content: Raw article content.
            content_format: Format of the content.
            url: Source URL for attribution.

        Returns:
            IngestionResult with status and chunk count.
        """
        try:
            # Stage 1: Normalize
            plaintext = self._normalizer.normalize(
                content, content_format, title=title
            )

            if not plaintext.strip():
                return IngestionResult(
                    article_id=article_id,
                    integration_id=integration_id,
                    status="skipped",
                    error="Empty content after normalization",
                )

            # Stage 2: Hash & check for changes
            content_hash = self._compute_hash(plaintext)
            stored_hash = await self._get_stored_hash(tenant_id, article_id)

            if stored_hash == content_hash:
                return IngestionResult(
                    article_id=article_id,
                    integration_id=integration_id,
                    status="skipped",
                    content_hash=content_hash,
                )

            # Stage 3: Chunk
            chunks = chunk_text(
                plaintext,
                chunk_size=self._chunk_size,
                chunk_overlap=self._chunk_overlap,
            )

            if not chunks:
                return IngestionResult(
                    article_id=article_id,
                    integration_id=integration_id,
                    status="skipped",
                    error="No chunks produced",
                )

            # Stage 4: Delete old chunks (if re-ingesting)
            if stored_hash is not None and self._delete_fn:
                await self._delete_fn(tenant_id, article_id)

            # Stage 5: Embed
            embeddings: list[list[float]] | None = None
            if self._embed_fn:
                embeddings = await self._embed_fn(chunks)

            # Stage 6: Store with metadata
            metadata_list = [
                IngestionMetadata(
                    integration_id=integration_id,
                    article_id=article_id,
                    title=title,
                    url=url,
                    source_format=content_format if isinstance(content_format, str) else content_format.value,
                    chunk_index=i,
                    total_chunks=len(chunks),
                    content_hash=content_hash,
                )
                for i in range(len(chunks))
            ]

            if self._store_fn:
                await self._store_fn(tenant_id, chunks, metadata_list, embeddings)

            # Stage 7: Update hash cache
            await self._store_hash(tenant_id, article_id, content_hash)

            logger.info(
                "Ingested article %s from %s: %d chunks (tenant=%s)",
                article_id, integration_id, len(chunks), tenant_id,
            )

            return IngestionResult(
                article_id=article_id,
                integration_id=integration_id,
                status="ingested",
                chunks_created=len(chunks),
                content_hash=content_hash,
            )

        except Exception as exc:
            logger.error(
                "Failed to ingest article %s from %s: %s",
                article_id, integration_id, exc,
            )
            return IngestionResult(
                article_id=article_id,
                integration_id=integration_id,
                status="failed",
                error=str(exc),
            )

    async def sync_source(
        self,
        tenant_id: str,
        integration_id: str,
        articles: list[dict[str, Any]],
    ) -> SyncResult:
        """Sync all articles from an integration source.

        Each article dict must have: article_id, title, content.
        Optional: content_format (default: plaintext), url.

        Args:
            tenant_id: Tenant identifier.
            integration_id: Source integration ID.
            articles: List of article dicts to sync.

        Returns:
            SyncResult with aggregate stats.
        """
        result = SyncResult(integration_id=integration_id)

        for article in articles:
            result.articles_processed += 1

            ingestion = await self.ingest_article(
                tenant_id,
                integration_id=integration_id,
                article_id=article["article_id"],
                title=article.get("title", ""),
                content=article.get("content", ""),
                content_format=article.get("content_format", ContentFormat.PLAINTEXT),
                url=article.get("url", ""),
            )

            if ingestion.status == "ingested":
                result.articles_ingested += 1
                result.total_chunks += ingestion.chunks_created
            elif ingestion.status == "skipped":
                result.articles_skipped += 1
            elif ingestion.status == "failed":
                result.articles_failed += 1
                result.errors.append(
                    f"{article.get('article_id', '?')}: {ingestion.error}"
                )

        logger.info(
            "Sync complete for %s (tenant=%s): %d processed, %d ingested, "
            "%d skipped, %d failed, %d chunks",
            integration_id, tenant_id,
            result.articles_processed, result.articles_ingested,
            result.articles_skipped, result.articles_failed,
            result.total_chunks,
        )

        return result
