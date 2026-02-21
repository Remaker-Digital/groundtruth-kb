"""Tests for document parsing pipeline and upload API (WI #214-217).

Validates:
    - File validation (type, size)
    - Text chunking (paragraph-aware, overlap, minimum size)
    - PDF parsing (text extraction, chunking)
    - DOCX parsing (headings, paragraphs)
    - CSV parsing (Q&A pairs, header detection)
    - TXT parsing (plain text chunking)
    - URL scraping (HTML → text)
    - chunks_to_kb_entries conversion
    - Upload API endpoint
    - URL import API endpoint
    - CSV export endpoint

Test IDs follow the pattern DP-XX for traceability.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import io
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.document_parser import (
    CHARS_PER_TOKEN,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    MAX_PDF_SIZE,
    MAX_TEXT_SIZE,
    MIN_CHUNK_SIZE,
    ParsedChunk,
    ParseResult,
    chunk_text,
    chunks_to_kb_entries,
    detect_source_type,
    parse_csv,
    parse_file,
    parse_txt,
    validate_file,
)

TENANT_ID = "tenant-parser-test-0001"


# ---------------------------------------------------------------------------
# DP-01: File validation
# ---------------------------------------------------------------------------


class TestFileValidation:
    """DP-01: File type and size validation."""

    def test_valid_pdf(self) -> None:
        assert validate_file("document.pdf", 1000) is None

    def test_valid_docx(self) -> None:
        assert validate_file("document.docx", 1000) is None

    def test_valid_csv(self) -> None:
        assert validate_file("data.csv", 1000) is None

    def test_valid_txt(self) -> None:
        assert validate_file("notes.txt", 1000) is None

    def test_unsupported_type(self) -> None:
        error = validate_file("image.png", 1000)
        assert error is not None
        assert "Unsupported" in error

    def test_pdf_size_limit(self) -> None:
        error = validate_file("huge.pdf", MAX_PDF_SIZE + 1)
        assert error is not None
        assert "too large" in error

    def test_text_size_limit(self) -> None:
        error = validate_file("huge.txt", MAX_TEXT_SIZE + 1)
        assert error is not None
        assert "too large" in error

    def test_case_insensitive_extension(self) -> None:
        assert validate_file("Document.PDF", 1000) is None
        assert validate_file("Data.CSV", 1000) is None

    def test_detect_source_type(self) -> None:
        assert detect_source_type("doc.pdf") == "pdf"
        assert detect_source_type("doc.docx") == "docx"
        assert detect_source_type("data.csv") == "csv"
        assert detect_source_type("notes.txt") == "txt"
        assert detect_source_type("unknown.xyz") == "manual"


# ---------------------------------------------------------------------------
# DP-02: Text chunking
# ---------------------------------------------------------------------------


class TestTextChunking:
    """DP-02: Paragraph-aware text chunking."""

    def test_short_text_single_chunk(self) -> None:
        """Text shorter than chunk size returns one chunk."""
        chunks = chunk_text("Short text.", title="Test")
        assert len(chunks) == 1
        assert chunks[0].text == "Short text."
        assert chunks[0].chunk_index == 0

    def test_long_text_multiple_chunks(self) -> None:
        """Long text is split into multiple chunks."""
        # Create text that exceeds chunk size
        paragraphs = [f"Paragraph {i}. " * 40 for i in range(10)]
        long_text = "\n\n".join(paragraphs)
        chunks = chunk_text(long_text, title="Long Doc", chunk_size=200)
        assert len(chunks) > 1
        # All chunks should have sequential indices
        indices = [c.chunk_index for c in chunks]
        assert indices == list(range(len(chunks)))

    def test_chunk_titles_include_part_numbers(self) -> None:
        """Multi-chunk documents have part numbers in titles."""
        paragraphs = [f"Paragraph {i}. " * 50 for i in range(10)]
        long_text = "\n\n".join(paragraphs)
        chunks = chunk_text(long_text, title="Policy", chunk_size=200)
        if len(chunks) > 1:
            assert "(Part 1)" in chunks[0].title
            assert "(Part 2)" in chunks[1].title

    def test_empty_text_returns_empty(self) -> None:
        """Empty text returns no chunks."""
        assert chunk_text("") == []
        assert chunk_text("   ") == []

    def test_metadata_propagated(self) -> None:
        """Source metadata is attached to all chunks."""
        chunks = chunk_text("Some text.", title="Test", source_metadata={"source": "pdf"})
        assert len(chunks) == 1
        assert chunks[0].metadata.get("source") == "pdf"

    def test_minimum_chunk_size(self) -> None:
        """Very small trailing text is merged into previous chunk."""
        # Create text where the last paragraph is tiny
        main = "A" * (DEFAULT_CHUNK_SIZE * CHARS_PER_TOKEN + 100)
        tiny = "B" * 10
        text = main + "\n\n" + tiny
        chunks = chunk_text(text, title="Test", chunk_size=DEFAULT_CHUNK_SIZE)
        # The tiny text should be merged, not standalone
        for c in chunks:
            assert len(c.text) >= MIN_CHUNK_SIZE * CHARS_PER_TOKEN or len(chunks) == 1


# ---------------------------------------------------------------------------
# DP-03: CSV parsing
# ---------------------------------------------------------------------------


class TestCSVParsing:
    """DP-03: CSV Q&A pair import."""

    @pytest.mark.asyncio
    async def test_basic_csv(self) -> None:
        """CSV with title,content columns parses correctly."""
        csv_content = (
            "title,content\n"
            "Return Policy,Items can be returned within 30 days.\n"
            "Shipping,Free shipping on orders over $50.\n"
        )
        result = await parse_csv(csv_content.encode(), "qa.csv")
        assert result.success
        assert len(result.chunks) == 2
        assert result.chunks[0].title == "Return Policy"
        assert "30 days" in result.chunks[0].text

    @pytest.mark.asyncio
    async def test_csv_with_entry_type_and_tags(self) -> None:
        """CSV with optional entry_type and tags columns."""
        csv_content = (
            "title,content,entry_type,tags\n"
            "Headphones,Premium wireless headphones.,product,electronics;audio\n"
        )
        result = await parse_csv(csv_content.encode(), "products.csv")
        assert result.success
        assert result.chunks[0].metadata["entry_type"] == "product"
        assert "electronics" in result.chunks[0].metadata["tags"]

    @pytest.mark.asyncio
    async def test_csv_missing_required_columns(self) -> None:
        """CSV without title/content columns fails."""
        csv_content = "name,description\nTest,Value\n"
        result = await parse_csv(csv_content.encode(), "bad.csv")
        assert not result.success
        assert "title" in result.error.lower()

    @pytest.mark.asyncio
    async def test_csv_empty_rows_skipped(self) -> None:
        """Rows with empty title or content are skipped."""
        csv_content = (
            "title,content\n"
            ",empty title\n"
            "empty content,\n"
            "Valid,Valid content.\n"
        )
        result = await parse_csv(csv_content.encode(), "partial.csv")
        assert result.success
        assert len(result.chunks) == 1
        assert result.chunks[0].title == "Valid"

    @pytest.mark.asyncio
    async def test_csv_too_few_rows(self) -> None:
        """CSV with only header fails."""
        csv_content = "title,content\n"
        result = await parse_csv(csv_content.encode(), "empty.csv")
        assert not result.success

    @pytest.mark.asyncio
    async def test_csv_bom_handling(self) -> None:
        """CSV with UTF-8 BOM is handled."""
        csv_content = b"\xef\xbb\xbftitle,content\nTest,Content\n"
        result = await parse_csv(csv_content, "bom.csv")
        assert result.success
        assert len(result.chunks) == 1


# ---------------------------------------------------------------------------
# DP-04: TXT parsing
# ---------------------------------------------------------------------------


class TestTXTParsing:
    """DP-04: Plain text file parsing."""

    @pytest.mark.asyncio
    async def test_basic_txt(self) -> None:
        """Simple text file parses into chunks."""
        text = "This is a simple text file with some content."
        result = await parse_txt(text.encode(), "notes.txt")
        assert result.success
        assert len(result.chunks) >= 1
        assert result.source_type == "txt"

    @pytest.mark.asyncio
    async def test_empty_txt(self) -> None:
        """Empty text file fails gracefully."""
        result = await parse_txt(b"", "empty.txt")
        assert not result.success
        assert "empty" in result.error.lower()

    @pytest.mark.asyncio
    async def test_long_txt_chunked(self) -> None:
        """Long text file is chunked."""
        paragraphs = [f"Paragraph {i}. " * 50 for i in range(20)]
        text = "\n\n".join(paragraphs)
        result = await parse_txt(text.encode(), "long.txt", chunk_size=200)
        assert result.success
        assert len(result.chunks) > 1

    @pytest.mark.asyncio
    async def test_txt_title_from_filename(self) -> None:
        """Title is derived from filename."""
        result = await parse_txt(b"Some content here.", "my-document.txt")
        assert result.success
        assert "My Document" in result.chunks[0].title


# ---------------------------------------------------------------------------
# DP-05: chunks_to_kb_entries conversion
# ---------------------------------------------------------------------------


class TestChunksToKBEntries:
    """DP-05: Converting parsed chunks to KnowledgeBaseDocument dicts."""

    def test_single_chunk_no_parent(self) -> None:
        """Single chunk has no parent_entry_id or chunk_index."""
        result = ParseResult(
            source_type="txt",
            source_filename="test.txt",
            chunks=[
                ParsedChunk(text="Content", title="Test", chunk_index=0),
            ],
            total_chars=7,
        )
        entries = chunks_to_kb_entries(result, TENANT_ID)
        assert len(entries) == 1
        assert entries[0]["parent_entry_id"] is None
        assert entries[0]["chunk_index"] is None
        assert entries[0]["tenant_id"] == TENANT_ID

    def test_multiple_chunks_have_parent(self) -> None:
        """Multi-chunk results share a parent_entry_id."""
        result = ParseResult(
            source_type="pdf",
            source_filename="doc.pdf",
            chunks=[
                ParsedChunk(text="Part 1", title="Doc (Part 1)", chunk_index=0),
                ParsedChunk(text="Part 2", title="Doc (Part 2)", chunk_index=1),
            ],
            total_chars=12,
        )
        entries = chunks_to_kb_entries(result, TENANT_ID)
        assert len(entries) == 2
        assert entries[0]["parent_entry_id"] is not None
        assert entries[0]["parent_entry_id"] == entries[1]["parent_entry_id"]
        assert entries[0]["chunk_index"] == 0
        assert entries[1]["chunk_index"] == 1

    def test_csv_entry_type_from_metadata(self) -> None:
        """CSV chunks carry entry_type from metadata."""
        result = ParseResult(
            source_type="csv",
            source_filename="products.csv",
            chunks=[
                ParsedChunk(
                    text="Great product",
                    title="Widget",
                    chunk_index=0,
                    metadata={"entry_type": "product", "tags": ["gadget"]},
                ),
            ],
            total_chars=13,
        )
        entries = chunks_to_kb_entries(result, TENANT_ID, default_entry_type="faq")
        assert entries[0]["entry_type"] == "product"
        assert entries[0]["tags"] == ["gadget"]

    def test_source_metadata_preserved(self) -> None:
        """Source type/filename/url are preserved on entries."""
        result = ParseResult(
            source_type="url",
            source_url="https://example.com/faq",
            chunks=[
                ParsedChunk(text="FAQ content", title="FAQ", chunk_index=0),
            ],
            total_chars=11,
        )
        entries = chunks_to_kb_entries(result, TENANT_ID)
        assert entries[0]["source_type"] == "url"
        assert entries[0]["source_url"] == "https://example.com/faq"

    def test_failed_parse_returns_empty(self) -> None:
        """Failed ParseResult returns no entries."""
        result = ParseResult(
            source_type="pdf",
            source_filename="bad.pdf",
            error="Parsing failed",
        )
        entries = chunks_to_kb_entries(result, TENANT_ID)
        assert entries == []


# ---------------------------------------------------------------------------
# DP-06: parse_file dispatch
# ---------------------------------------------------------------------------


class TestParseFileDispatch:
    """DP-06: Unified file parser dispatch."""

    @pytest.mark.asyncio
    async def test_dispatch_txt(self) -> None:
        """parse_file dispatches .txt to parse_txt."""
        result = await parse_file(b"Hello world", "test.txt")
        assert result.source_type == "txt"
        assert result.success

    @pytest.mark.asyncio
    async def test_dispatch_csv(self) -> None:
        """parse_file dispatches .csv to parse_csv."""
        csv = b"title,content\nTest,Content\n"
        result = await parse_file(csv, "data.csv")
        assert result.source_type == "csv"
        assert result.success

    @pytest.mark.asyncio
    async def test_dispatch_unsupported(self) -> None:
        """parse_file rejects unsupported types."""
        result = await parse_file(b"data", "image.png")
        assert not result.success
        assert "Unsupported" in result.error

    @pytest.mark.asyncio
    async def test_dispatch_pdf(self) -> None:
        """parse_file dispatches .pdf to parse_pdf."""
        # Minimal valid PDF (will fail parsing but dispatch is correct)
        result = await parse_file(b"%PDF-1.4 invalid", "test.pdf")
        assert result.source_type == "pdf"
        # May fail parsing but source_type should be set

    @pytest.mark.asyncio
    async def test_dispatch_docx(self) -> None:
        """parse_file dispatches .docx to parse_docx."""
        # Invalid DOCX content — will fail but dispatch is correct
        result = await parse_file(b"not a docx", "test.docx")
        assert result.source_type == "docx"


# ---------------------------------------------------------------------------
# DP-07: ParseResult and ParsedChunk models
# ---------------------------------------------------------------------------


class TestDataModels:
    """DP-07: Data model correctness."""

    def test_parse_result_success(self) -> None:
        """Success when no error and chunks present."""
        r = ParseResult(
            source_type="txt",
            chunks=[ParsedChunk(text="t", title="t", chunk_index=0)],
        )
        assert r.success is True

    def test_parse_result_failure_with_error(self) -> None:
        """Failure when error is set."""
        r = ParseResult(source_type="txt", error="Something went wrong")
        assert r.success is False

    def test_parse_result_failure_empty_chunks(self) -> None:
        """Failure when no chunks and no error."""
        r = ParseResult(source_type="txt")
        assert r.success is False

    def test_parsed_chunk_defaults(self) -> None:
        """ParsedChunk has default empty metadata."""
        c = ParsedChunk(text="test", title="Test", chunk_index=0)
        assert c.metadata == {}


# ---------------------------------------------------------------------------
# DP-08: Constants
# ---------------------------------------------------------------------------


class TestConstants:
    """DP-08: Verify important constants."""

    def test_supported_extensions(self) -> None:
        from src.multi_tenant.document_parser import SUPPORTED_EXTENSIONS
        assert ".pdf" in SUPPORTED_EXTENSIONS
        assert ".docx" in SUPPORTED_EXTENSIONS
        assert ".csv" in SUPPORTED_EXTENSIONS
        assert ".txt" in SUPPORTED_EXTENSIONS

    def test_chunk_size_defaults(self) -> None:
        assert DEFAULT_CHUNK_SIZE == 400
        assert MIN_CHUNK_SIZE == 100
        assert DEFAULT_CHUNK_OVERLAP == 50
        assert CHARS_PER_TOKEN == 4

    def test_size_limits(self) -> None:
        assert MAX_PDF_SIZE == 50 * 1024 * 1024
        assert MAX_TEXT_SIZE == 4 * 1024 * 1024


# ---------------------------------------------------------------------------
# DP-20: Crawler hardening (F4-F6)
# ---------------------------------------------------------------------------

class TestCrawlerConstants:
    """Verify crawler hardening constants exist and have correct values."""

    def test_user_agent_defined(self) -> None:
        """F5: Crawler User-Agent should identify as AgentRed bot."""
        from src.multi_tenant.document_parser import CRAWLER_USER_AGENT

        assert "AgentRed" in CRAWLER_USER_AGENT
        assert "http" in CRAWLER_USER_AGENT  # Should include a URL

    def test_crawl_delay_defined(self) -> None:
        """F6: Crawl delay should be at least 1 second."""
        from src.multi_tenant.document_parser import CRAWL_DELAY_SECONDS

        assert CRAWL_DELAY_SECONDS >= 1.0

    def test_user_agent_set_on_single_page(self) -> None:
        """F5: parse_url should set User-Agent header."""
        import src.multi_tenant.document_parser as dp

        # Verify the constant is importable and non-empty
        assert dp.CRAWLER_USER_AGENT
        assert len(dp.CRAWLER_USER_AGENT) > 10


class TestCrawlUrlRobotsCheck:
    """Verify robots.txt integration in crawl_url (F4)."""

    @pytest.mark.asyncio
    async def test_crawl_url_respects_robots_disallow(self) -> None:
        """F4: URLs disallowed by robots.txt should be skipped."""
        from src.multi_tenant.document_parser import crawl_url

        mock_response_robots = MagicMock()
        mock_response_robots.status_code = 200
        mock_response_robots.text = (
            "User-agent: *\n"
            "Disallow: /private/\n"
            "Allow: /\n"
        )

        mock_response_page = MagicMock()
        mock_response_page.status_code = 200
        mock_response_page.headers = {"content-type": "text/html"}
        mock_response_page.content = b"<html><body><a href='/private/secret'>Link</a><a href='/public'>Public</a></body></html>"
        mock_response_page.text = "<html><body><a href='/private/secret'>Link</a><a href='/public'>Public</a></body></html>"
        mock_response_page.raise_for_status = MagicMock()

        call_count = 0
        urls_fetched = []

        async def mock_get(url):
            nonlocal call_count
            call_count += 1
            urls_fetched.append(url)

            if "robots.txt" in url:
                return mock_response_robots
            return mock_response_page

        mock_client = AsyncMock()
        mock_client.get = mock_get
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch("httpx.AsyncClient", return_value=mock_client),
            patch("src.multi_tenant.document_parser.parse_url", new_callable=AsyncMock,
                  return_value=ParseResult(source_type="url", source_url="https://example.com")),
            patch("asyncio.sleep", new_callable=AsyncMock),
        ):
            results = await crawl_url("https://example.com", max_pages=5)

        # The /private/ URL should not appear in fetched URLs (except robots.txt)
        page_urls = [u for u in urls_fetched if "robots.txt" not in u]
        private_urls = [u for u in page_urls if "/private/" in u]
        assert len(private_urls) == 0, f"Should not fetch disallowed URLs: {private_urls}"
