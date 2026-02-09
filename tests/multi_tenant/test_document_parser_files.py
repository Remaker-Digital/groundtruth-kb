"""
Document parser real-file tests (MT-1006→MT-1008).

Tests parsing of actual PDF, DOCX, and CSV files from the test fixtures
directory to prevent regressions like the DOCX upload HTTP 500 bug
discovered during LUIT-SA Run 1 (python-docx not installed).

Master Test Plan: §4 Gap Register — Document Parser Real Files (1.0-required)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from src.multi_tenant.document_parser import (
    ParseResult,
    parse_csv,
    parse_docx,
    parse_pdf,
    validate_file,
)


# ---------------------------------------------------------------------------
# Fixture paths — real files in tests/rag-documents-upload/
# ---------------------------------------------------------------------------

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "rag-documents-upload"

PDF_FILE = FIXTURES_DIR / "PDF-document.pdf"
DOCX_FILE = FIXTURES_DIR / "DOCX-document.docx"
CSV_FILE = FIXTURES_DIR / "CSV-document.csv"
TXT_FILE = FIXTURES_DIR / "TEXT-document.txt"


# ---------------------------------------------------------------------------
# Precondition: fixture files exist
# ---------------------------------------------------------------------------


class TestFixtureFilesExist:
    """Verify test fixture files are present before running parser tests."""

    def test_pdf_fixture_exists(self):
        assert PDF_FILE.exists(), f"PDF fixture missing: {PDF_FILE}"

    def test_docx_fixture_exists(self):
        assert DOCX_FILE.exists(), f"DOCX fixture missing: {DOCX_FILE}"

    def test_csv_fixture_exists(self):
        assert CSV_FILE.exists(), f"CSV fixture missing: {CSV_FILE}"

    def test_txt_fixture_exists(self):
        assert TXT_FILE.exists(), f"TXT fixture missing: {TXT_FILE}"


# ---------------------------------------------------------------------------
# MT-1006: Parse real PDF file → non-empty chunks
# ---------------------------------------------------------------------------


class TestParsePDFFile:
    """MT-1006: Parse a real PDF file and verify structured output."""

    @pytest.mark.asyncio
    async def test_parse_pdf_produces_chunks(self):
        """Real PDF file → ParseResult with success=True and non-empty chunks."""
        content = PDF_FILE.read_bytes()
        result = await parse_pdf(content, "PDF-document.pdf")

        assert isinstance(result, ParseResult)
        assert result.success, f"PDF parsing failed: {result.error}"
        assert result.source_type == "pdf"
        assert result.source_filename == "PDF-document.pdf"
        assert len(result.chunks) > 0, "PDF produced no chunks"
        assert result.total_chars > 0

    @pytest.mark.asyncio
    async def test_parse_pdf_chunks_have_text(self):
        """Each PDF chunk contains non-empty text content."""
        content = PDF_FILE.read_bytes()
        result = await parse_pdf(content, "PDF-document.pdf")

        assert result.success
        for chunk in result.chunks:
            assert chunk.text.strip(), f"Chunk {chunk.chunk_index} has empty text"
            assert chunk.title, f"Chunk {chunk.chunk_index} has no title"

    @pytest.mark.asyncio
    async def test_parse_pdf_metadata_includes_page_count(self):
        """PDF chunks include page_count in metadata."""
        content = PDF_FILE.read_bytes()
        result = await parse_pdf(content, "PDF-document.pdf")

        assert result.success
        # At least the first chunk should have page_count metadata
        first_chunk = result.chunks[0]
        assert "page_count" in first_chunk.metadata
        assert first_chunk.metadata["page_count"] >= 1


# ---------------------------------------------------------------------------
# MT-1007: Parse real DOCX file → non-empty chunks
# ---------------------------------------------------------------------------


class TestParseDOCXFile:
    """MT-1007: Parse a real DOCX file — regression test for python-docx dependency."""

    @pytest.mark.asyncio
    async def test_parse_docx_produces_chunks(self):
        """Real DOCX file → ParseResult with success=True and non-empty chunks.

        This is a direct regression test for the LUIT-SA Run 1 failure:
        DOCX upload returned HTTP 500 because python-docx was imported
        but not installed in the production Docker container.
        """
        content = DOCX_FILE.read_bytes()
        result = await parse_docx(content, "DOCX-document.docx")

        assert isinstance(result, ParseResult)
        assert result.success, f"DOCX parsing failed: {result.error}"
        assert result.source_type == "docx"
        assert result.source_filename == "DOCX-document.docx"
        assert len(result.chunks) > 0, "DOCX produced no chunks"
        assert result.total_chars > 0

    @pytest.mark.asyncio
    async def test_parse_docx_chunks_have_text(self):
        """Each DOCX chunk contains non-empty text content."""
        content = DOCX_FILE.read_bytes()
        result = await parse_docx(content, "DOCX-document.docx")

        assert result.success
        for chunk in result.chunks:
            assert chunk.text.strip(), f"Chunk {chunk.chunk_index} has empty text"

    @pytest.mark.asyncio
    async def test_parse_docx_metadata_includes_paragraph_count(self):
        """DOCX chunks include paragraph_count in metadata."""
        content = DOCX_FILE.read_bytes()
        result = await parse_docx(content, "DOCX-document.docx")

        assert result.success
        first_chunk = result.chunks[0]
        assert "paragraph_count" in first_chunk.metadata
        assert first_chunk.metadata["paragraph_count"] >= 1


# ---------------------------------------------------------------------------
# MT-1008: Parse real CSV file → structured entries
# ---------------------------------------------------------------------------


class TestParseCSVFile:
    """MT-1008: Parse a real CSV file with title/content columns."""

    @pytest.mark.asyncio
    async def test_parse_csv_produces_entries(self):
        """Real CSV file → ParseResult with success=True and entries from rows."""
        content = CSV_FILE.read_bytes()
        result = await parse_csv(content, "CSV-document.csv")

        assert isinstance(result, ParseResult)
        assert result.success, f"CSV parsing failed: {result.error}"
        assert result.source_type == "csv"
        assert result.source_filename == "CSV-document.csv"
        assert len(result.chunks) > 0, "CSV produced no entries"

    @pytest.mark.asyncio
    async def test_parse_csv_entry_titles(self):
        """CSV entries preserve titles from the title column."""
        content = CSV_FILE.read_bytes()
        result = await parse_csv(content, "CSV-document.csv")

        assert result.success
        # The test CSV has "Test FAQ" and "Shipping Policy" rows
        titles = [chunk.title for chunk in result.chunks]
        assert len(titles) >= 2
        # Verify at least one expected title is present
        assert any("FAQ" in t for t in titles) or any("Shipping" in t for t in titles), \
            f"Expected FAQ or Shipping in titles, got: {titles}"

    @pytest.mark.asyncio
    async def test_parse_csv_entries_have_content(self):
        """Each CSV entry has non-empty text content from the content column."""
        content = CSV_FILE.read_bytes()
        result = await parse_csv(content, "CSV-document.csv")

        assert result.success
        for chunk in result.chunks:
            assert chunk.text.strip(), f"Entry '{chunk.title}' has empty content"


# ---------------------------------------------------------------------------
# File validation tests (bonus — complements MT-1006→MT-1008)
# ---------------------------------------------------------------------------


class TestFileValidation:
    """Validate file extension and size checks before parsing."""

    def test_validate_supported_extensions(self):
        """validate_file accepts .pdf, .docx, .csv, .txt files."""
        for ext in ["test.pdf", "test.docx", "test.csv", "test.txt"]:
            error = validate_file(ext, file_size=1000)
            assert error is None, f"Expected {ext} to be accepted, got: {error}"

    def test_validate_rejects_unsupported_extension(self):
        """validate_file rejects unsupported file types."""
        error = validate_file("test.exe", file_size=1000)
        assert error is not None
        assert "supported" in error.lower() or "extension" in error.lower()

    def test_validate_rejects_oversized_file(self):
        """validate_file rejects files exceeding size limit."""
        # PDF max is 50MB
        error = validate_file("huge.pdf", file_size=60 * 1024 * 1024)
        assert error is not None
        assert "size" in error.lower() or "large" in error.lower()
