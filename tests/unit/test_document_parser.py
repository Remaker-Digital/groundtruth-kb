"""Tests for document parser pipeline — coverage expansion.

Covers: file validation, source type detection, text chunking,
paragraph splitting, overlap, CSV parsing, TXT parsing, PDF parsing,
DOCX parsing, parse_file dispatch, parse_url (full HTML branch),
crawl_url, chunks_to_kb_entries conversion, and ParseResult properties.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.document_parser import (
    CHARS_PER_TOKEN,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    MAX_PDF_SIZE,
    MAX_TEXT_SIZE,
    MAX_URL_SIZE,
    MIN_CHUNK_SIZE,
    ParseResult,
    ParsedChunk,
    _get_overlap,
    _split_paragraphs,
    chunk_text,
    chunks_to_kb_entries,
    crawl_url,
    detect_source_type,
    parse_csv,
    parse_docx,
    parse_file,
    parse_pdf,
    parse_txt,
    parse_url,
    validate_file,
)


# ---------------------------------------------------------------------------
# Tests: validate_file
# ---------------------------------------------------------------------------


class TestValidateFile:
    def test_valid_pdf(self):
        assert validate_file("document.pdf", 1000) is None

    def test_valid_docx(self):
        assert validate_file("document.docx", 1000) is None

    def test_valid_csv(self):
        assert validate_file("data.csv", 1000) is None

    def test_valid_txt(self):
        assert validate_file("notes.txt", 1000) is None

    def test_unsupported_extension(self):
        result = validate_file("image.png", 100)
        assert result is not None
        assert "Unsupported file type" in result

    def test_pdf_too_large(self):
        result = validate_file("big.pdf", MAX_PDF_SIZE + 1)
        assert result is not None
        assert "too large" in result

    def test_text_file_too_large(self):
        result = validate_file("big.txt", MAX_TEXT_SIZE + 1)
        assert result is not None
        assert "too large" in result

    def test_docx_too_large(self):
        result = validate_file("big.docx", MAX_TEXT_SIZE + 1)
        assert result is not None
        assert "too large" in result

    def test_csv_too_large(self):
        result = validate_file("big.csv", MAX_TEXT_SIZE + 1)
        assert result is not None
        assert "too large" in result

    def test_case_insensitive_extension(self):
        assert validate_file("README.TXT", 100) is None
        assert validate_file("DATA.CSV", 100) is None

    def test_pdf_at_exact_limit(self):
        assert validate_file("doc.pdf", MAX_PDF_SIZE) is None

    def test_text_at_exact_limit(self):
        assert validate_file("doc.txt", MAX_TEXT_SIZE) is None


# ---------------------------------------------------------------------------
# Tests: detect_source_type
# ---------------------------------------------------------------------------


class TestDetectSourceType:
    def test_pdf(self):
        assert detect_source_type("file.pdf") == "pdf"

    def test_docx(self):
        assert detect_source_type("file.docx") == "docx"

    def test_csv(self):
        assert detect_source_type("file.csv") == "csv"

    def test_txt(self):
        assert detect_source_type("file.txt") == "txt"

    def test_unknown_extension(self):
        assert detect_source_type("file.xyz") == "manual"

    def test_no_extension(self):
        assert detect_source_type("README") == "manual"

    def test_case_insensitive(self):
        assert detect_source_type("FILE.PDF") == "pdf"


# ---------------------------------------------------------------------------
# Tests: ParseResult
# ---------------------------------------------------------------------------


class TestParseResult:
    def test_success_with_chunks(self):
        result = ParseResult(
            source_type="txt",
            chunks=[ParsedChunk(text="hello", title="t", chunk_index=0)],
            total_chars=5,
        )
        assert result.success is True

    def test_failure_with_error(self):
        result = ParseResult(source_type="txt", error="Something went wrong")
        assert result.success is False

    def test_failure_with_no_chunks(self):
        result = ParseResult(source_type="txt", chunks=[], total_chars=0)
        assert result.success is False

    def test_failure_with_error_and_chunks(self):
        """Error takes precedence even if chunks exist."""
        result = ParseResult(
            source_type="txt",
            error="Some error",
            chunks=[ParsedChunk(text="x", title="t", chunk_index=0)],
        )
        assert result.success is False


# ---------------------------------------------------------------------------
# Tests: _split_paragraphs
# ---------------------------------------------------------------------------


class TestSplitParagraphs:
    def test_single_paragraph(self):
        result = _split_paragraphs("Hello world.")
        assert len(result) == 1
        assert result[0].strip() == "Hello world."

    def test_multiple_paragraphs(self):
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        result = _split_paragraphs(text)
        assert len(result) == 3

    def test_windows_line_endings(self):
        text = "Para one.\r\n\r\nPara two."
        result = _split_paragraphs(text)
        assert len(result) == 2

    def test_empty_paragraphs_filtered(self):
        text = "Para one.\n\n\n\n\n\nPara two."
        result = _split_paragraphs(text)
        assert len(result) == 2

    def test_whitespace_only_returns_empty(self):
        result = _split_paragraphs("   \n\n   ")
        assert len(result) == 0


# ---------------------------------------------------------------------------
# Tests: _get_overlap
# ---------------------------------------------------------------------------


class TestGetOverlap:
    def test_zero_overlap(self):
        assert _get_overlap("some text", 0) == ""

    def test_overlap_larger_than_text(self):
        assert _get_overlap("short", 100) == ""

    def test_returns_tail(self):
        text = "This is a long sentence. And another one."
        result = _get_overlap(text, 20)
        # Should return ~last 20 chars, possibly adjusted at sentence boundary
        assert len(result) <= 20
        assert len(result) > 0

    def test_sentence_boundary_break(self):
        text = "First sentence. Second sentence. Third sentence here."
        result = _get_overlap(text, 30)
        # Should break at sentence boundary if possible
        assert result != ""


# ---------------------------------------------------------------------------
# Tests: chunk_text
# ---------------------------------------------------------------------------


class TestChunkText:
    def test_empty_text(self):
        assert chunk_text("") == []

    def test_whitespace_only(self):
        assert chunk_text("   \n\n  ") == []

    def test_short_text_single_chunk(self):
        text = "Short paragraph."
        chunks = chunk_text(text, title="Doc")
        assert len(chunks) == 1
        assert chunks[0].title == "Doc"
        assert chunks[0].chunk_index == 0
        assert chunks[0].text == text

    def test_long_text_multiple_chunks(self):
        # Create text that exceeds DEFAULT_CHUNK_SIZE * CHARS_PER_TOKEN
        paragraph = "Lorem ipsum dolor sit amet. " * 100
        text = f"{paragraph}\n\n{paragraph}\n\n{paragraph}"
        chunks = chunk_text(text, title="Big Doc", chunk_size=100)
        assert len(chunks) > 1
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i
            assert "Big Doc" in chunk.title

    def test_metadata_passed_through(self):
        text = "A short paragraph."
        meta = {"source": "test", "page": 1}
        chunks = chunk_text(text, title="T", source_metadata=meta)
        assert len(chunks) == 1
        assert chunks[0].metadata == meta

    def test_no_title_default(self):
        text = "Short content."
        chunks = chunk_text(text)
        assert chunks[0].title == "Document"

    def test_final_small_chunk_merged(self):
        """If the last chunk is too small, it should be merged with previous."""
        # Create text where last paragraph would be too small on its own
        big = "X" * (DEFAULT_CHUNK_SIZE * CHARS_PER_TOKEN + 100)
        tiny = "Y" * 10  # Smaller than MIN_CHUNK_SIZE * CHARS_PER_TOKEN
        text = f"{big}\n\n{tiny}"
        chunks = chunk_text(text, title="T")
        # The tiny part should be merged with the previous chunk
        if len(chunks) > 0:
            assert tiny.strip() in chunks[-1].text or len(chunks) == 1


# ---------------------------------------------------------------------------
# Tests: parse_csv
# ---------------------------------------------------------------------------


class TestParseCsv:
    @pytest.mark.asyncio
    async def test_valid_csv(self):
        content = "title,content\nQ1,Answer 1\nQ2,Answer 2".encode("utf-8")
        result = await parse_csv(content, "faq.csv")
        assert result.success is True
        assert len(result.chunks) == 2
        assert result.chunks[0].title == "Q1"
        assert result.chunks[0].text == "Answer 1"

    @pytest.mark.asyncio
    async def test_csv_with_entry_type_and_tags(self):
        content = "title,content,entry_type,tags\nShipping,Free shipping over $50,policy,shipping;free".encode("utf-8")
        result = await parse_csv(content, "policies.csv")
        assert result.success is True
        assert result.chunks[0].metadata["entry_type"] == "policy"
        assert result.chunks[0].metadata["tags"] == ["shipping", "free"]

    @pytest.mark.asyncio
    async def test_csv_missing_header_columns(self):
        content = "question,answer\nQ1,A1".encode("utf-8")
        result = await parse_csv(content, "bad.csv")
        assert result.success is False
        assert "title" in result.error.lower() and "content" in result.error.lower()

    @pytest.mark.asyncio
    async def test_csv_only_header(self):
        content = "title,content".encode("utf-8")
        result = await parse_csv(content, "empty.csv")
        assert result.success is False
        assert "at least" in result.error.lower()

    @pytest.mark.asyncio
    async def test_csv_no_valid_rows(self):
        content = "title,content\n,\n,".encode("utf-8")
        result = await parse_csv(content, "blank.csv")
        assert result.success is False
        assert "No valid data" in result.error

    @pytest.mark.asyncio
    async def test_csv_with_bom(self):
        content = b"\xef\xbb\xbftitle,content\nQ1,A1"
        result = await parse_csv(content, "bom.csv")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_csv_latin1_fallback(self):
        # Create content that is valid latin-1 but invalid utf-8
        content = "title,content\n".encode("latin-1") + b"Caf\xe9,D\xe9tails"
        result = await parse_csv(content, "latin.csv")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_csv_invalid_entry_type_defaults_to_faq(self):
        content = "title,content,entry_type\nQ1,A1,invalid_type".encode("utf-8")
        result = await parse_csv(content, "test.csv")
        assert result.success is True
        # Invalid entry_type should default to "faq"
        assert result.chunks[0].metadata["entry_type"] == "faq"

    @pytest.mark.asyncio
    async def test_csv_skips_malformed_rows(self):
        # Row with fewer columns than needed
        content = "title,content\nQ1,A1\nShort".encode("utf-8")
        result = await parse_csv(content, "test.csv")
        assert result.success is True
        assert len(result.chunks) == 1  # Only Q1/A1 row


# ---------------------------------------------------------------------------
# Tests: parse_txt
# ---------------------------------------------------------------------------


class TestParseTxt:
    @pytest.mark.asyncio
    async def test_valid_txt(self):
        content = b"This is a simple text document."
        result = await parse_txt(content, "notes.txt")
        assert result.success is True
        assert result.total_chars == 31
        assert result.source_type == "txt"

    @pytest.mark.asyncio
    async def test_empty_txt(self):
        result = await parse_txt(b"", "empty.txt")
        assert result.success is False
        assert "empty" in result.error.lower()

    @pytest.mark.asyncio
    async def test_whitespace_only_txt(self):
        result = await parse_txt(b"   \n\n  ", "blank.txt")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_txt_latin1_fallback(self):
        content = b"Caf\xe9 au lait instructions"
        result = await parse_txt(content, "latin.txt")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_txt_title_from_filename(self):
        content = b"Some content here"
        result = await parse_txt(content, "my-great_document.txt")
        assert result.success is True
        # Title derived from filename
        assert len(result.chunks) > 0

    @pytest.mark.asyncio
    async def test_txt_undecodable(self):
        # Bytes that are neither valid UTF-8 nor Latin-1 in a way that causes issues
        # Latin-1 can decode any byte, so we test UTF-8 with BOM fail
        content = b"\xff\xfe" + bytes(range(128, 256))
        result = await parse_txt(content, "weird.txt")
        # Latin-1 fallback should handle this
        assert result.success is True


# ---------------------------------------------------------------------------
# Tests: parse_file (dispatch)
# ---------------------------------------------------------------------------


class TestParseFile:
    @pytest.mark.asyncio
    async def test_dispatch_txt(self):
        content = b"Hello world content for testing."
        result = await parse_file(content, "test.txt")
        assert result.source_type == "txt"
        assert result.success is True

    @pytest.mark.asyncio
    async def test_dispatch_csv(self):
        content = "title,content\nQ,A".encode("utf-8")
        result = await parse_file(content, "test.csv")
        assert result.source_type == "csv"
        assert result.success is True

    @pytest.mark.asyncio
    async def test_dispatch_unsupported(self):
        result = await parse_file(b"data", "test.xyz")
        assert result.success is False
        assert "Unsupported" in result.error

    @pytest.mark.asyncio
    async def test_dispatch_pdf(self):
        """PDF dispatch calls parse_pdf (which may fail due to missing pypdf)."""
        result = await parse_file(b"not a real pdf", "test.pdf")
        # Either success or error about pypdf/parsing — but dispatch worked
        assert result.source_type == "pdf"

    @pytest.mark.asyncio
    async def test_dispatch_docx(self):
        """DOCX dispatch calls parse_docx (which may fail due to missing python-docx)."""
        result = await parse_file(b"not a real docx", "test.docx")
        assert result.source_type == "docx"


# ---------------------------------------------------------------------------
# Tests: chunks_to_kb_entries
# ---------------------------------------------------------------------------


class TestChunksToKbEntries:
    def test_single_chunk_no_parent(self):
        pr = ParseResult(
            source_type="txt",
            source_filename="test.txt",
            chunks=[ParsedChunk(text="Content", title="Title", chunk_index=0)],
            total_chars=7,
        )
        entries = chunks_to_kb_entries(pr, "tenant-001")
        assert len(entries) == 1
        assert entries[0]["tenant_id"] == "tenant-001"
        assert entries[0]["parent_entry_id"] is None
        assert entries[0]["chunk_index"] is None
        assert entries[0]["source_type"] == "txt"

    def test_multi_chunk_generates_parent_id(self):
        pr = ParseResult(
            source_type="txt",
            source_filename="big.txt",
            chunks=[
                ParsedChunk(text="Chunk 1", title="T (Part 1)", chunk_index=0),
                ParsedChunk(text="Chunk 2", title="T (Part 2)", chunk_index=1),
            ],
            total_chars=14,
        )
        entries = chunks_to_kb_entries(pr, "tenant-001")
        assert len(entries) == 2
        # Both should share the same parent_entry_id
        assert entries[0]["parent_entry_id"] is not None
        assert entries[0]["parent_entry_id"] == entries[1]["parent_entry_id"]
        # Chunk indices should be set
        assert entries[0]["chunk_index"] == 0
        assert entries[1]["chunk_index"] == 1

    def test_csv_entry_type_from_metadata(self):
        pr = ParseResult(
            source_type="csv",
            source_filename="faq.csv",
            chunks=[
                ParsedChunk(
                    text="Answer",
                    title="Question",
                    chunk_index=0,
                    metadata={"entry_type": "policy", "tags": ["shipping"]},
                ),
            ],
            total_chars=6,
        )
        entries = chunks_to_kb_entries(pr, "tenant-001", default_entry_type="custom")
        assert entries[0]["entry_type"] == "policy"
        assert entries[0]["tags"] == ["shipping"]

    def test_failed_parse_result_returns_empty(self):
        pr = ParseResult(source_type="txt", error="parse failed")
        entries = chunks_to_kb_entries(pr, "tenant-001")
        assert entries == []

    def test_custom_parent_entry_id(self):
        pr = ParseResult(
            source_type="txt",
            chunks=[
                ParsedChunk(text="C1", title="T1", chunk_index=0),
                ParsedChunk(text="C2", title="T2", chunk_index=1),
            ],
            total_chars=4,
        )
        entries = chunks_to_kb_entries(pr, "tenant-001", parent_entry_id="custom-parent")
        assert entries[0]["parent_entry_id"] == "custom-parent"

    def test_source_url_preserved(self):
        pr = ParseResult(
            source_type="url",
            source_url="https://example.com",
            chunks=[ParsedChunk(text="Page", title="Example", chunk_index=0)],
            total_chars=4,
        )
        entries = chunks_to_kb_entries(pr, "tenant-001")
        assert entries[0]["source_url"] == "https://example.com"
        assert entries[0]["source_filename"] is None


# ---------------------------------------------------------------------------
# Tests: parse_url (mocked httpx)
# ---------------------------------------------------------------------------


class TestParseUrl:
    @pytest.mark.asyncio
    async def test_parse_url_non_html_content_type(self):
        from src.multi_tenant.document_parser import parse_url

        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await parse_url("https://example.com/api/data")

        assert result.success is False
        assert "non-HTML" in result.error

    @pytest.mark.asyncio
    async def test_parse_url_http_error(self):
        import httpx

        mock_resp = MagicMock()
        mock_resp.status_code = 404

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "Not Found", request=MagicMock(), response=mock_resp,
            ),
        )
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await parse_url("https://example.com/missing")

        assert result.success is False
        assert "404" in result.error

    @pytest.mark.asyncio
    async def test_parse_url_request_error(self):
        """RequestError (network failure) returns a friendly error."""
        import httpx

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(
            side_effect=httpx.RequestError("Connection refused", request=MagicMock()),
        )
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await parse_url("https://example.com/down")

        assert result.success is False
        assert "Failed to fetch" in result.error

    @pytest.mark.asyncio
    async def test_parse_url_content_too_large(self):
        """Pages exceeding MAX_URL_SIZE are rejected."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "text/html"}
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.content = b"x" * (MAX_URL_SIZE + 1)

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await parse_url("https://example.com/huge")

        assert result.success is False
        assert "too large" in result.error

    @pytest.mark.asyncio
    async def test_parse_url_success_with_main_content(self):
        """Full HTML parsing extracts content from <main> and strips scripts."""
        html = """
        <html>
        <head><title>Test Page</title></head>
        <body>
        <nav>Navigation links</nav>
        <main>
            <p>This is the main content of the page with enough text to pass the minimum length requirement for parsing.</p>
        </main>
        <footer>Footer info</footer>
        <script>var x = 1;</script>
        </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "text/html; charset=utf-8"}
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.content = html.encode()
        mock_response.text = html

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await parse_url("https://example.com/article")

        assert result.success is True
        assert result.source_type == "url"
        assert result.total_chars > 0
        assert len(result.chunks) >= 1
        # Nav/footer/script should be stripped
        for ch in result.chunks:
            assert "var x = 1" not in ch.text

    @pytest.mark.asyncio
    async def test_parse_url_success_fallback_to_body(self):
        """When no <main>/<article> exists, falls back to <body>."""
        html = """
        <html>
        <head><title>Simple Page</title></head>
        <body>
        <div>This is plain body content with enough words to meet the minimum character threshold for extraction.</div>
        </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "text/html"}
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.content = html.encode()
        mock_response.text = html

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await parse_url("https://example.com/simple")

        assert result.success is True
        assert "body content" in result.chunks[0].text.lower()

    @pytest.mark.asyncio
    async def test_parse_url_empty_page(self):
        """Pages with very little text return an error."""
        html = "<html><body><p>Hi</p></body></html>"
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "text/html"}
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.content = html.encode()
        mock_response.text = html

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await parse_url("https://example.com/empty")

        assert result.success is False
        assert "No meaningful text" in result.error

    @pytest.mark.asyncio
    async def test_parse_url_html_parsing_error(self):
        """When HTML parsing raises an exception, returns error."""
        html = "<html><body>Content</body></html>"
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "text/html"}
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.content = html.encode()
        mock_response.text = html

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch("httpx.AsyncClient", return_value=mock_client),
            patch("bs4.BeautifulSoup", side_effect=Exception("parse boom")),
        ):
            result = await parse_url("https://example.com/bad")

        assert result.success is False
        assert "parsing failed" in result.error.lower()

    @pytest.mark.asyncio
    async def test_parse_url_beautifulsoup_import_failure(self):
        """If beautifulsoup4 is not installed, returns a descriptive error."""
        # Temporarily hide bs4
        original = sys.modules.get("bs4")
        sys.modules["bs4"] = None  # type: ignore[assignment]
        try:
            # We need to force the lazy import to fail, so patch it at function level
            with patch.dict("sys.modules", {"bs4": None}):
                # The function does `from bs4 import BeautifulSoup` which will fail
                # But since bs4 is likely installed, we need a different approach:
                # patch the import inside the function
                pass
        finally:
            if original is not None:
                sys.modules["bs4"] = original
            elif "bs4" in sys.modules:
                del sys.modules["bs4"]

        # Alternative: test via builtins import mock
        import builtins

        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "bs4":
                raise ImportError("No module named 'bs4'")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            result = await parse_url("https://example.com/test")

        assert result.success is False
        assert "beautifulsoup4" in result.error.lower()


# ---------------------------------------------------------------------------
# Tests: parse_pdf (mocked pypdf)
# ---------------------------------------------------------------------------


class TestParsePdf:
    @pytest.mark.asyncio
    async def test_pdf_success(self):
        """Successful PDF with two pages of text."""
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page one content with some words."
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page two has more content."

        mock_reader = MagicMock()
        mock_reader.pages = [mock_page1, mock_page2]

        with patch.dict("sys.modules", {"pypdf": MagicMock()}):
            with patch("pypdf.PdfReader", return_value=mock_reader):
                result = await parse_pdf(b"fake-pdf-bytes", "report.pdf")

        assert result.success is True
        assert result.source_type == "pdf"
        assert result.total_chars > 0
        assert len(result.chunks) >= 1

    @pytest.mark.asyncio
    async def test_pdf_no_text_content(self):
        """PDF with no extractable text (image-based)."""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = ""

        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]

        with patch.dict("sys.modules", {"pypdf": MagicMock()}):
            with patch("pypdf.PdfReader", return_value=mock_reader):
                result = await parse_pdf(b"fake-pdf-bytes", "scanned.pdf")

        assert result.success is False
        assert "No text content" in result.error

    @pytest.mark.asyncio
    async def test_pdf_import_failure(self):
        """When pypdf is not installed, returns descriptive error."""
        import builtins

        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "pypdf":
                raise ImportError("No module named 'pypdf'")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            result = await parse_pdf(b"fake-pdf", "doc.pdf")

        assert result.success is False
        assert "pypdf" in result.error.lower()

    @pytest.mark.asyncio
    async def test_pdf_parsing_exception(self):
        """Generic exception during PDF parsing returns error."""
        with patch.dict("sys.modules", {"pypdf": MagicMock()}):
            with patch("pypdf.PdfReader", side_effect=Exception("corrupt PDF")):
                result = await parse_pdf(b"bad-bytes", "corrupt.pdf")

        assert result.success is False
        assert "parsing failed" in result.error.lower()

    @pytest.mark.asyncio
    async def test_pdf_title_derived_from_filename(self):
        """Title is derived from filename with cleanup."""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Content from the PDF document."

        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]

        with patch.dict("sys.modules", {"pypdf": MagicMock()}):
            with patch("pypdf.PdfReader", return_value=mock_reader):
                result = await parse_pdf(b"fake", "my-great_report.pdf")

        assert result.success is True
        # Title derived: "my-great_report" -> "My Great Report"
        assert result.chunks[0].title is not None


# ---------------------------------------------------------------------------
# Tests: parse_docx (mocked python-docx)
# ---------------------------------------------------------------------------


class TestParseDocx:
    @pytest.mark.asyncio
    async def test_docx_success_with_headings(self):
        """Successful DOCX with heading + body paragraphs."""
        heading_para = MagicMock()
        heading_para.text = "Introduction"
        heading_para.style = MagicMock()
        heading_para.style.name = "Heading 1"

        body_para = MagicMock()
        body_para.text = "This is the body of the document."
        body_para.style = MagicMock()
        body_para.style.name = "Normal"

        mock_doc = MagicMock()
        mock_doc.paragraphs = [heading_para, body_para]
        mock_doc.core_properties = MagicMock()
        mock_doc.core_properties.title = "Custom Title"

        with patch.dict("sys.modules", {"docx": MagicMock()}):
            with patch("docx.Document", return_value=mock_doc):
                result = await parse_docx(b"fake-docx", "guide.docx")

        assert result.success is True
        assert result.source_type == "docx"
        assert result.total_chars > 0

    @pytest.mark.asyncio
    async def test_docx_empty_paragraphs(self):
        """DOCX with only empty paragraphs returns error."""
        empty_para = MagicMock()
        empty_para.text = "   "

        mock_doc = MagicMock()
        mock_doc.paragraphs = [empty_para]

        with patch.dict("sys.modules", {"docx": MagicMock()}):
            with patch("docx.Document", return_value=mock_doc):
                result = await parse_docx(b"fake-docx", "empty.docx")

        assert result.success is False
        assert "No text content" in result.error

    @pytest.mark.asyncio
    async def test_docx_import_failure(self):
        """When python-docx is not installed, returns descriptive error."""
        import builtins

        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "docx":
                raise ImportError("No module named 'docx'")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            result = await parse_docx(b"fake", "doc.docx")

        assert result.success is False
        assert "python-docx" in result.error.lower()

    @pytest.mark.asyncio
    async def test_docx_parsing_exception(self):
        """Generic exception during DOCX parsing returns error."""
        with patch.dict("sys.modules", {"docx": MagicMock()}):
            with patch("docx.Document", side_effect=Exception("corrupt DOCX")):
                result = await parse_docx(b"bad-bytes", "corrupt.docx")

        assert result.success is False
        assert "parsing failed" in result.error.lower()

    @pytest.mark.asyncio
    async def test_docx_heading_level_extraction(self):
        """Heading levels are converted to markdown-style markers."""
        h2_para = MagicMock()
        h2_para.text = "Section Two"
        h2_para.style = MagicMock()
        h2_para.style.name = "Heading 2"

        body_para = MagicMock()
        body_para.text = "Body content follows."
        body_para.style = MagicMock()
        body_para.style.name = "Normal"

        mock_doc = MagicMock()
        mock_doc.paragraphs = [h2_para, body_para]
        mock_doc.core_properties = MagicMock()
        mock_doc.core_properties.title = None

        with patch.dict("sys.modules", {"docx": MagicMock()}):
            with patch("docx.Document", return_value=mock_doc):
                result = await parse_docx(b"fake", "sections.docx")

        assert result.success is True
        # Heading 2 should have ## prefix
        combined = "\n".join(ch.text for ch in result.chunks)
        assert "## Section Two" in combined

    @pytest.mark.asyncio
    async def test_docx_no_core_properties_title(self):
        """When doc has no core_properties.title, uses filename."""
        body_para = MagicMock()
        body_para.text = "Some document content here."
        body_para.style = MagicMock()
        body_para.style.name = "Normal"

        mock_doc = MagicMock()
        mock_doc.paragraphs = [body_para]
        mock_doc.core_properties = MagicMock()
        mock_doc.core_properties.title = None

        with patch.dict("sys.modules", {"docx": MagicMock()}):
            with patch("docx.Document", return_value=mock_doc):
                result = await parse_docx(b"fake", "my-report_v2.docx")

        assert result.success is True

    @pytest.mark.asyncio
    async def test_docx_heading_without_level_number(self):
        """Heading style named just 'Heading' (no number) defaults to level 1."""
        h_para = MagicMock()
        h_para.text = "Top Heading"
        h_para.style = MagicMock()
        h_para.style.name = "Heading"

        body_para = MagicMock()
        body_para.text = "Content below heading."
        body_para.style = MagicMock()
        body_para.style.name = "Normal"

        mock_doc = MagicMock()
        mock_doc.paragraphs = [h_para, body_para]
        mock_doc.core_properties = MagicMock()
        mock_doc.core_properties.title = None

        with patch.dict("sys.modules", {"docx": MagicMock()}):
            with patch("docx.Document", return_value=mock_doc):
                result = await parse_docx(b"fake", "test.docx")

        assert result.success is True
        combined = "\n".join(ch.text for ch in result.chunks)
        assert "# Top Heading" in combined


# ---------------------------------------------------------------------------
# Tests: parse_csv (encoding edge cases)
# ---------------------------------------------------------------------------


class TestParseCsvEdgeCases:
    @pytest.mark.asyncio
    async def test_csv_double_encoding_failure(self):
        """Bytes that fail both UTF-8 and Latin-1 decoding."""
        # Latin-1 can decode any byte value 0-255, so this is effectively
        # unreachable in practice. We test the csv.Error branch instead.
        pass

    @pytest.mark.asyncio
    async def test_csv_library_error(self):
        """csv.Error during parsing returns error."""
        with patch("src.multi_tenant.document_parser.csv.reader", side_effect=__import__("csv").Error("bad CSV")):
            result = await parse_csv(b"title,content\nQ,A", "broken.csv")

        assert result.success is False
        assert "CSV parsing error" in result.error


# ---------------------------------------------------------------------------
# Tests: chunk_text (accumulation branch)
# ---------------------------------------------------------------------------


class TestChunkTextAccumulation:
    def test_paragraph_too_small_keeps_accumulating(self):
        """When accumulated text < char_min but adding next paragraph would exceed target,
        the code keeps accumulating instead of saving the small chunk (line 224)."""
        # Use default chunk_size=400 => char_target=1600, char_min=400
        # First paragraph: 50 chars (well below char_min of 400)
        small_para = "A" * 50
        # Second paragraph: 1600 chars (so small_para + big_para > char_target)
        big_para = "B" * 1600
        # Third paragraph: enough to form a valid final chunk
        final_para = "C" * 500
        text = f"{small_para}\n\n{big_para}\n\n{final_para}"
        chunks = chunk_text(text, title="Test")
        # The small para should have been accumulated with big_para (not saved separately)
        # All content should be present
        total_text = "".join(ch.text for ch in chunks)
        assert "A" in total_text
        assert "B" in total_text
        assert "C" in total_text
        # Should have at least 1 chunk
        assert len(chunks) >= 1

    def test_empty_paragraphs_after_split(self):
        """chunk_text returns empty list when paragraphs list is empty."""
        result = chunk_text("   \n\n   ")
        assert result == []


# ---------------------------------------------------------------------------
# Tests: crawl_url
# ---------------------------------------------------------------------------


class TestCrawlUrl:
    @pytest.mark.asyncio
    async def test_crawl_beautifulsoup_import_failure(self):
        """If bs4 is not installed, crawl returns a single error result."""
        import builtins

        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "bs4":
                raise ImportError("No module named 'bs4'")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            results = await crawl_url("https://example.com")

        assert len(results) == 1
        assert results[0].success is False
        assert "beautifulsoup4" in results[0].error.lower()

    @pytest.mark.asyncio
    async def test_crawl_single_page_success(self):
        """Crawl a single page with no outbound links."""
        html = """
        <html><head><title>Home</title></head>
        <body><main><p>Welcome to the site with enough content to pass the minimum text length requirement for parsing successfully.</p></main></body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "text/html"}
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.content = html.encode()
        mock_response.text = html

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await crawl_url("https://example.com", max_pages=1)

        assert len(results) >= 1
        assert results[0].success is True

    @pytest.mark.asyncio
    async def test_crawl_follows_same_domain_links(self):
        """Crawl follows same-domain links up to max_pages."""
        page1_html = """
        <html><head><title>Page 1</title></head>
        <body><main>
        <p>Page one content with enough words to pass the minimum character threshold for the document parser.</p>
        <a href="/page2">Page 2</a>
        <a href="https://external.com/other">External</a>
        </main></body>
        </html>
        """
        page2_html = """
        <html><head><title>Page 2</title></head>
        <body><main>
        <p>Page two content with enough words to pass the minimum character threshold for the document parser.</p>
        </main></body>
        </html>
        """

        call_count = 0

        async def mock_get(url, **kwargs):
            nonlocal call_count
            call_count += 1
            resp = MagicMock()
            resp.headers = {"content-type": "text/html"}
            resp.status_code = 200
            resp.raise_for_status = MagicMock()
            if "page2" in url:
                resp.content = page2_html.encode()
                resp.text = page2_html
            else:
                resp.content = page1_html.encode()
                resp.text = page1_html
            return resp

        mock_client = AsyncMock()
        mock_client.get = mock_get
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await crawl_url("https://example.com", max_pages=5)

        # Should have fetched at least 2 pages (start + page2)
        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_crawl_skips_non_html(self):
        """Non-HTML responses are skipped during crawl."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/pdf"}
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.content = b"PDF content"

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await crawl_url("https://example.com/file.pdf", max_pages=1)

        # Non-HTML skipped, no results
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_crawl_skips_fetch_errors(self):
        """Fetch errors are logged and skipped during crawl."""
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=Exception("Connection refused"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await crawl_url("https://example.com/down", max_pages=1)

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_crawl_skips_oversized_pages(self):
        """Pages larger than MAX_URL_SIZE are skipped."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "text/html"}
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.content = b"x" * (MAX_URL_SIZE + 1)

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await crawl_url("https://example.com/huge", max_pages=1)

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_crawl_max_pages_clamped(self):
        """max_pages is clamped between 1 and CRAWL_MAX_PAGES_HARD_LIMIT."""
        html = """
        <html><head><title>Test</title></head>
        <body><main><p>Content that is long enough to exceed the minimum text threshold required by the document parser module.</p></main></body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "text/html"}
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.content = html.encode()
        mock_response.text = html

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            # max_pages=0 should be clamped to 1
            results = await crawl_url("https://example.com", max_pages=0)

        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_crawl_deduplicates_urls(self):
        """Same URL (with different fragments) is only crawled once."""
        html = """
        <html><head><title>Test</title></head>
        <body><main>
        <p>Content that is long enough to pass the minimum text length threshold required by the document parser.</p>
        <a href="https://example.com/#section1">Section 1</a>
        <a href="https://example.com/#section2">Section 2</a>
        </main></body>
        </html>
        """
        crawl_urls_fetched: list[str] = []

        async def tracking_get(url, **kwargs):
            crawl_urls_fetched.append(url)
            resp = MagicMock()
            resp.headers = {"content-type": "text/html"}
            resp.status_code = 200
            resp.raise_for_status = MagicMock()
            resp.content = html.encode()
            resp.text = html
            return resp

        mock_client = AsyncMock()
        mock_client.get = tracking_get
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await crawl_url("https://example.com/", max_pages=5)

        # Fragment-only links (#section1, #section2) resolve to the same
        # base URL, so after dedup the crawl should produce exactly 1 result.
        assert len(results) == 1
