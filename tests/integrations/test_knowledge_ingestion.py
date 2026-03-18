"""Tests for Multi-Source Knowledge Ingestion Pipeline (SPEC-1770).

Tests cover: ContentNormalizer (HTML, Markdown, Notion, Confluence, CSV),
chunking with overlap, content hashing for incremental sync, full
ingestion pipeline, and sync_source batch processing.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json

import pytest

from src.integrations.knowledge_ingestion import (
    ContentFormat,
    ContentNormalizer,
    IngestionResult,
    KnowledgeIngestionPipeline,
    SyncResult,
    chunk_text,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    CHARS_PER_TOKEN,
)


# ---------------------------------------------------------------------------
# ContentNormalizer tests
# ---------------------------------------------------------------------------


class TestContentNormalizer:
    """Tests for multi-format content normalization."""

    def setup_method(self):
        self.normalizer = ContentNormalizer()

    def test_html_strips_tags(self):
        html = "<h1>Title</h1><p>Body <b>bold</b> text.</p>"
        result = self.normalizer.normalize(html, ContentFormat.HTML)
        assert "Title" in result
        assert "Body" in result
        assert "bold" in result
        assert "<" not in result

    def test_html_removes_scripts(self):
        html = '<p>Hello</p><script>alert("xss")</script><p>World</p>'
        result = self.normalizer.normalize(html, ContentFormat.HTML)
        assert "Hello" in result
        assert "World" in result
        assert "alert" not in result
        assert "script" not in result

    def test_html_removes_styles(self):
        html = "<style>body{color:red}</style><p>Content</p>"
        result = self.normalizer.normalize(html, ContentFormat.HTML)
        assert "Content" in result
        assert "color" not in result

    def test_html_decodes_entities(self):
        html = "<p>AT&amp;T &lt;hello&gt; &quot;quoted&quot;</p>"
        result = self.normalizer.normalize(html, ContentFormat.HTML)
        assert "AT&T" in result
        assert "<hello>" in result

    def test_html_br_to_newline(self):
        html = "line1<br/>line2<br>line3"
        result = self.normalizer.normalize(html, ContentFormat.HTML)
        assert "line1" in result
        assert "line2" in result

    def test_markdown_strips_formatting(self):
        md = "# Heading\n\n**Bold** and *italic* text.\n\n- Item 1\n- Item 2"
        result = self.normalizer.normalize(md, ContentFormat.MARKDOWN)
        assert "Heading" in result
        assert "Bold" in result
        assert "italic" in result
        assert "**" not in result
        assert "*" not in result or "italic" in result
        assert "#" not in result

    def test_markdown_converts_links(self):
        md = "Visit [our site](https://example.com) for more."
        result = self.normalizer.normalize(md, ContentFormat.MARKDOWN)
        assert "our site" in result
        assert "https://example.com" not in result

    def test_markdown_removes_images(self):
        md = "See ![screenshot](img.png) below."
        result = self.normalizer.normalize(md, ContentFormat.MARKDOWN)
        assert "img.png" not in result

    def test_markdown_removes_code_fences(self):
        md = "```python\nprint('hello')\n```"
        result = self.normalizer.normalize(md, ContentFormat.MARKDOWN)
        assert "print('hello')" in result
        assert "```" not in result

    def test_plaintext_passthrough(self):
        text = "This is plain text.\nWith newlines."
        result = self.normalizer.normalize(text, ContentFormat.PLAINTEXT)
        assert result == text

    def test_notion_blocks_extracts_text(self):
        blocks = [
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"plain_text": "First paragraph."},
                        {"plain_text": " More text."},
                    ]
                },
            },
            {
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"plain_text": "Main Heading"}]
                },
            },
        ]
        result = self.normalizer.normalize(
            json.dumps(blocks), ContentFormat.NOTION_BLOCKS
        )
        assert "First paragraph." in result
        assert "More text." in result
        assert "Main Heading" in result

    def test_notion_blocks_handles_invalid_json(self):
        result = self.normalizer.normalize(
            "not json", ContentFormat.NOTION_BLOCKS
        )
        assert result == "not json"

    def test_confluence_strips_macros(self):
        content = (
            '<ac:structured-macro ac:name="toc"><ac:parameter>3</ac:parameter>'
            "</ac:structured-macro>"
            "<p>Real content here.</p>"
        )
        result = self.normalizer.normalize(content, ContentFormat.CONFLUENCE_STORAGE)
        assert "Real content" in result
        assert "ac:" not in result

    def test_csv_converts_to_readable(self):
        csv_content = '"Name","Age","City"\n"Alice","30","NYC"\n"Bob","25","LA"'
        result = self.normalizer.normalize(csv_content, ContentFormat.CSV)
        assert "Name: Alice" in result
        assert "Age: 30" in result
        assert "City: NYC" in result

    def test_title_prepended(self):
        result = self.normalizer.normalize(
            "Body text", ContentFormat.PLAINTEXT, title="My Article"
        )
        assert result.startswith("My Article")
        assert "Body text" in result

    def test_empty_content_returns_title(self):
        result = self.normalizer.normalize(
            "", ContentFormat.HTML, title="Just Title"
        )
        assert result == "Just Title"

    def test_empty_content_no_title_returns_empty(self):
        result = self.normalizer.normalize("", ContentFormat.HTML)
        assert result == ""

    def test_string_format_accepted(self):
        result = self.normalizer.normalize("<p>Hi</p>", "html")
        assert "Hi" in result

    def test_unknown_format_falls_back_to_plaintext(self):
        result = self.normalizer.normalize("Hello", "unknown_format")
        assert result == "Hello"

    def test_whitespace_cleaned(self):
        text = "   Multiple   spaces   \n\n\n\n\n  and newlines  "
        result = self.normalizer.normalize(text, ContentFormat.PLAINTEXT)
        assert "   " not in result  # no triple spaces
        assert "\n\n\n" not in result  # max 2 consecutive newlines


# ---------------------------------------------------------------------------
# Chunking tests
# ---------------------------------------------------------------------------


class TestChunking:
    """Tests for text chunking with overlap."""

    def test_short_text_single_chunk(self):
        text = "This is a short sentence."
        chunks = chunk_text(text)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_empty_text_no_chunks(self):
        assert chunk_text("") == []
        assert chunk_text("   ") == []

    def test_long_text_produces_multiple_chunks(self):
        # Generate text longer than one chunk
        sentences = [f"Sentence number {i} with some additional words." for i in range(200)]
        text = " ".join(sentences)
        chunks = chunk_text(text, chunk_size=100, chunk_overlap=20)
        assert len(chunks) > 1

    def test_chunks_have_overlap(self):
        sentences = [f"Sentence {i} is about topic {i}." for i in range(100)]
        text = " ".join(sentences)
        chunks = chunk_text(text, chunk_size=50, chunk_overlap=10)
        assert len(chunks) >= 2
        # Check that later chunks share some content with earlier ones
        # (overlap means some sentences appear in both chunks)
        if len(chunks) >= 2:
            words_0 = set(chunks[0].split())
            words_1 = set(chunks[1].split())
            overlap = words_0 & words_1
            assert len(overlap) > 0, "Chunks should have overlapping content"

    def test_custom_chunk_parameters(self):
        # Use sentences so the chunker can find split points
        sentences = [f"This is sentence number {i} with enough words to matter." for i in range(200)]
        text = " ".join(sentences)
        chunks_small = chunk_text(text, chunk_size=50, chunk_overlap=10)
        chunks_large = chunk_text(text, chunk_size=200, chunk_overlap=20)
        assert len(chunks_small) > len(chunks_large)


# ---------------------------------------------------------------------------
# Ingestion pipeline tests
# ---------------------------------------------------------------------------


class TestIngestionPipeline:
    """Tests for the full ingestion pipeline."""

    def _make_pipeline(self, **kwargs) -> KnowledgeIngestionPipeline:
        return KnowledgeIngestionPipeline(**kwargs)

    @pytest.mark.asyncio
    async def test_ingest_article_basic(self):
        pipeline = self._make_pipeline()
        result = await pipeline.ingest_article(
            "tenant-1",
            integration_id="zendesk",
            article_id="ART-100",
            title="Getting Started",
            content="This is a help article about getting started with our product.",
        )
        assert result.status == "ingested"
        assert result.chunks_created >= 1
        assert result.content_hash != ""
        assert result.article_id == "ART-100"

    @pytest.mark.asyncio
    async def test_ingest_skips_unchanged_content(self):
        pipeline = self._make_pipeline()
        content = "This is the article body."

        r1 = await pipeline.ingest_article(
            "t1", integration_id="z", article_id="A1",
            title="T", content=content,
        )
        assert r1.status == "ingested"

        r2 = await pipeline.ingest_article(
            "t1", integration_id="z", article_id="A1",
            title="T", content=content,
        )
        assert r2.status == "skipped"

    @pytest.mark.asyncio
    async def test_ingest_reingests_changed_content(self):
        delete_called = []

        async def mock_delete(tenant_id, article_id):
            delete_called.append((tenant_id, article_id))
            return 1

        pipeline = self._make_pipeline(delete_fn=mock_delete)

        await pipeline.ingest_article(
            "t1", integration_id="z", article_id="A1",
            title="T", content="Version 1",
        )
        r2 = await pipeline.ingest_article(
            "t1", integration_id="z", article_id="A1",
            title="T", content="Version 2 — updated",
        )
        assert r2.status == "ingested"
        assert len(delete_called) == 1

    @pytest.mark.asyncio
    async def test_ingest_empty_content_skipped(self):
        pipeline = self._make_pipeline()
        result = await pipeline.ingest_article(
            "t1", integration_id="z", article_id="A1",
            title="", content="",
        )
        assert result.status == "skipped"
        assert "Empty" in result.error

    @pytest.mark.asyncio
    async def test_ingest_calls_embed_fn(self):
        embed_calls = []

        async def mock_embed(texts):
            embed_calls.append(texts)
            return [[0.1] * 3072 for _ in texts]

        pipeline = self._make_pipeline(embed_fn=mock_embed)
        await pipeline.ingest_article(
            "t1", integration_id="z", article_id="A1",
            title="T", content="Embed this article content.",
        )
        assert len(embed_calls) == 1

    @pytest.mark.asyncio
    async def test_ingest_calls_store_fn_with_metadata(self):
        store_calls = []

        async def mock_store(tenant_id, chunks, metadata_list, embeddings):
            store_calls.append({
                "tenant_id": tenant_id,
                "chunks": chunks,
                "metadata": metadata_list,
            })

        pipeline = self._make_pipeline(store_fn=mock_store)
        await pipeline.ingest_article(
            "t1", integration_id="zendesk", article_id="ART-50",
            title="FAQ", content="Frequently asked questions.",
            url="https://help.example.com/faq",
        )
        assert len(store_calls) == 1
        meta = store_calls[0]["metadata"][0]
        assert meta.integration_id == "zendesk"
        assert meta.article_id == "ART-50"
        assert meta.title == "FAQ"
        assert meta.url == "https://help.example.com/faq"

    @pytest.mark.asyncio
    async def test_ingest_html_article(self):
        pipeline = self._make_pipeline()
        result = await pipeline.ingest_article(
            "t1", integration_id="z", article_id="A1",
            title="HTML Article",
            content="<h1>Welcome</h1><p>This is <b>rich</b> content.</p>",
            content_format=ContentFormat.HTML,
        )
        assert result.status == "ingested"

    @pytest.mark.asyncio
    async def test_ingest_failure_returns_failed_result(self):
        async def failing_store(*args):
            raise RuntimeError("Store failed")

        pipeline = self._make_pipeline(store_fn=failing_store)
        result = await pipeline.ingest_article(
            "t1", integration_id="z", article_id="A1",
            title="T", content="Content",
        )
        assert result.status == "failed"
        assert "Store failed" in result.error


# ---------------------------------------------------------------------------
# Sync source tests
# ---------------------------------------------------------------------------


class TestSyncSource:
    """Tests for batch sync_source processing."""

    @pytest.mark.asyncio
    async def test_sync_multiple_articles(self):
        pipeline = KnowledgeIngestionPipeline()
        articles = [
            {"article_id": f"A-{i}", "title": f"Article {i}", "content": f"Body of article {i}."}
            for i in range(5)
        ]
        result = await pipeline.sync_source("t1", "zendesk", articles)
        assert isinstance(result, SyncResult)
        assert result.articles_processed == 5
        assert result.articles_ingested == 5
        assert result.articles_skipped == 0
        assert result.articles_failed == 0
        assert result.total_chunks >= 5

    @pytest.mark.asyncio
    async def test_sync_skips_unchanged(self):
        pipeline = KnowledgeIngestionPipeline()
        articles = [
            {"article_id": "A-1", "title": "T", "content": "Body"},
        ]
        # First sync
        await pipeline.sync_source("t1", "z", articles)
        # Second sync — same content
        result = await pipeline.sync_source("t1", "z", articles)
        assert result.articles_skipped == 1
        assert result.articles_ingested == 0

    @pytest.mark.asyncio
    async def test_sync_reports_failures(self):
        call_count = 0

        async def sometimes_fail(*args):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("DB down")

        pipeline = KnowledgeIngestionPipeline(store_fn=sometimes_fail)
        articles = [
            {"article_id": "A-1", "title": "T1", "content": "B1"},
            {"article_id": "A-2", "title": "T2", "content": "B2"},
        ]
        result = await pipeline.sync_source("t1", "z", articles)
        assert result.articles_failed == 1
        assert result.articles_ingested == 1
        assert len(result.errors) == 1

    @pytest.mark.asyncio
    async def test_sync_with_mixed_formats(self):
        pipeline = KnowledgeIngestionPipeline()
        articles = [
            {
                "article_id": "A-1", "title": "HTML",
                "content": "<p>HTML body</p>",
                "content_format": "html",
            },
            {
                "article_id": "A-2", "title": "MD",
                "content": "# Markdown\n\nBody text.",
                "content_format": "markdown",
            },
        ]
        result = await pipeline.sync_source("t1", "zendesk", articles)
        assert result.articles_ingested == 2
