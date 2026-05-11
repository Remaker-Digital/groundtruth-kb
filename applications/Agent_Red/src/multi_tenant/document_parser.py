# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Document parsing pipeline for Knowledge Base uploads (WI #214-216).

Parses uploaded files (PDF, DOCX, CSV, TXT) and web pages (URL) into
knowledge base entries with intelligent chunking.

Capabilities:
    1. File type detection and validation
    2. Text extraction from PDF, DOCX, CSV, TXT
    3. URL content scraping (HTML → text)
    4. Intelligent chunking (paragraph-aware, configurable size)
    5. Metadata extraction (page numbers, headings, row indices)

Architecture references:
    - RAG-GAP-ANALYSIS.md: WI #214 (upload API), #215 (parsing), #216 (chunking)
    - cosmos_schema.py: KnowledgeBaseDocument (source_type, source_filename,
      chunk_index, parent_entry_id)
    - Competitive reference: Intercom (PDF/DOCX, 100MB limit, 10-min processing)

Dependencies:
    - pypdf >= 4.0.0 (PDF text extraction)
    - python-docx >= 1.1.0 (DOCX paragraph extraction)
    - beautifulsoup4 >= 4.12.0 (HTML parsing for URL scraping)
    - httpx (already in requirements.txt, used for URL fetching)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import csv
import hashlib
import io
import logging
import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Supported file types and their MIME types
SUPPORTED_EXTENSIONS: dict[str, str] = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".csv": "text/csv",
    ".txt": "text/plain",
}

# File size limits (bytes)
MAX_PDF_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_TEXT_SIZE = 4 * 1024 * 1024  # 4 MB (DOCX, CSV, TXT)
MAX_URL_SIZE = 4 * 1024 * 1024  # 4 MB response body

# Chunking defaults
DEFAULT_CHUNK_SIZE = 400  # tokens (target)
MIN_CHUNK_SIZE = 100  # tokens (minimum viable chunk)
MAX_CHUNK_SIZE = 800  # tokens (hard cap)
DEFAULT_CHUNK_OVERLAP = 50  # tokens
CHARS_PER_TOKEN = 4  # approximation for English text

# URL scraping
URL_FETCH_TIMEOUT = 30  # seconds
MAX_URL_REDIRECTS = 5
CRAWL_DEFAULT_MAX_PAGES = 10
CRAWL_MAX_PAGES_HARD_LIMIT = 100
CRAWLER_USER_AGENT = "AgentRed-KnowledgeBot/1.0 (+https://agentredcx.com/bot)"
CRAWL_DELAY_SECONDS = 1.0  # Polite delay between page fetches


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class ParsedChunk:
    """A single chunk extracted from a document."""

    text: str
    title: str
    chunk_index: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ParseResult:
    """Result of parsing a document."""

    source_type: str  # pdf | docx | csv | txt | url
    source_filename: str | None = None
    source_url: str | None = None
    chunks: list[ParsedChunk] = field(default_factory=list)
    total_chars: int = 0
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.error is None and len(self.chunks) > 0


# ---------------------------------------------------------------------------
# File validation
# ---------------------------------------------------------------------------


def validate_file(filename: str, file_size: int) -> str | None:
    """Validate file type and size.

    Returns None if valid, or an error message string.
    """
    _, ext = os.path.splitext(filename.lower())

    if ext not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS.keys()))
        return f"Unsupported file type '{ext}'. Supported: {supported}"

    if ext == ".pdf":
        if file_size > MAX_PDF_SIZE:
            return f"PDF file too large ({file_size:,} bytes). Maximum: {MAX_PDF_SIZE:,} bytes (50 MB)"
    else:
        if file_size > MAX_TEXT_SIZE:
            return f"File too large ({file_size:,} bytes). Maximum: {MAX_TEXT_SIZE:,} bytes (4 MB)"

    return None


def detect_source_type(filename: str) -> str:
    """Detect source type from filename extension."""
    _, ext = os.path.splitext(filename.lower())
    type_map = {
        ".pdf": "pdf",
        ".docx": "docx",
        ".csv": "csv",
        ".txt": "txt",
    }
    return type_map.get(ext, "manual")


# ---------------------------------------------------------------------------
# Text chunking (WI #216)
# ---------------------------------------------------------------------------


def chunk_text(
    text: str,
    title: str = "",
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    source_metadata: dict[str, Any] | None = None,
) -> list[ParsedChunk]:
    """Split text into chunks respecting paragraph boundaries.

    Strategy:
        1. Split on double-newlines (paragraph boundaries)
        2. Accumulate paragraphs until chunk_size reached
        3. Start new chunk with overlap from previous
        4. Never split mid-sentence when possible

    Args:
        text: Full text to chunk.
        title: Document title (used as chunk title prefix).
        chunk_size: Target chunk size in tokens.
        chunk_overlap: Overlap between consecutive chunks in tokens.
        source_metadata: Additional metadata to attach to each chunk.

    Returns:
        List of ParsedChunk instances.
    """
    if not text or not text.strip():
        return []

    # Convert token targets to character targets
    char_target = chunk_size * CHARS_PER_TOKEN
    char_overlap = chunk_overlap * CHARS_PER_TOKEN
    char_min = MIN_CHUNK_SIZE * CHARS_PER_TOKEN

    # Split into paragraphs
    paragraphs = _split_paragraphs(text)

    if not paragraphs:
        return []

    # If text fits in one chunk, return as-is
    if len(text) <= char_target:
        chunk_title = title if title else "Document"
        return [
            ParsedChunk(
                text=text.strip(),
                title=chunk_title,
                chunk_index=0,
                metadata=source_metadata or {},
            )
        ]

    chunks: list[ParsedChunk] = []
    current_text = ""
    chunk_idx = 0

    for para in paragraphs:
        # If adding this paragraph would exceed target
        if current_text and len(current_text) + len(para) > char_target:
            # Save current chunk if it's big enough
            if len(current_text.strip()) >= char_min:
                chunk_title = f"{title} (Part {chunk_idx + 1})" if title else f"Part {chunk_idx + 1}"
                chunks.append(
                    ParsedChunk(
                        text=current_text.strip(),
                        title=chunk_title,
                        chunk_index=chunk_idx,
                        metadata=source_metadata or {},
                    )
                )
                chunk_idx += 1

                # Start new chunk with overlap
                overlap_text = _get_overlap(current_text, char_overlap)
                current_text = overlap_text + para
            else:
                # Too small to save — just keep accumulating
                current_text += para
        else:
            current_text += para

    # Final chunk
    if current_text.strip() and len(current_text.strip()) >= char_min:
        chunk_title = f"{title} (Part {chunk_idx + 1})" if title else f"Part {chunk_idx + 1}"
        chunks.append(
            ParsedChunk(
                text=current_text.strip(),
                title=chunk_title,
                chunk_index=chunk_idx,
                metadata=source_metadata or {},
            )
        )
    elif current_text.strip() and chunks:
        # Too small on its own — append to previous chunk
        chunks[-1] = ParsedChunk(
            text=chunks[-1].text + "\n\n" + current_text.strip(),
            title=chunks[-1].title,
            chunk_index=chunks[-1].chunk_index,
            metadata=chunks[-1].metadata,
        )

    return chunks


def _split_paragraphs(text: str) -> list[str]:
    """Split text into paragraphs, preserving double-newline boundaries."""
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Split on double-newlines
    raw_paras = re.split(r"\n\s*\n", text)
    # Filter empty and re-add separators
    result = []
    for p in raw_paras:
        stripped = p.strip()
        if stripped:
            result.append(stripped + "\n\n")
    return result


def _get_overlap(text: str, char_overlap: int) -> str:
    """Get the last char_overlap characters of text, breaking at sentence boundary."""
    if char_overlap <= 0 or len(text) <= char_overlap:
        return ""

    tail = text[-char_overlap:]
    # Try to start at a sentence boundary
    sentence_break = tail.find(". ")
    if sentence_break > 0 and sentence_break < len(tail) // 2:
        tail = tail[sentence_break + 2 :]
    return tail


# ---------------------------------------------------------------------------
# PDF parsing
# ---------------------------------------------------------------------------


async def parse_pdf(
    file_content: bytes,
    filename: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> ParseResult:
    """Parse a PDF file into chunked text.

    Extracts text page-by-page, then applies intelligent chunking.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        return ParseResult(
            source_type="pdf",
            source_filename=filename,
            error="PDF parsing requires 'pypdf' package. Install: pip install pypdf>=4.0.0",
        )

    try:
        reader = PdfReader(io.BytesIO(file_content))
        pages: list[str] = []
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                pages.append(text.strip())

        if not pages:
            return ParseResult(
                source_type="pdf",
                source_filename=filename,
                error="No text content found in PDF. The file may be image-based (OCR not supported).",
            )

        full_text = "\n\n".join(pages)
        total_chars = len(full_text)

        # Derive title from filename
        title = os.path.splitext(filename)[0].replace("-", " ").replace("_", " ").title()

        chunks = chunk_text(
            text=full_text,
            title=title,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            source_metadata={"page_count": len(reader.pages), "source": "pdf"},
        )

        return ParseResult(
            source_type="pdf",
            source_filename=filename,
            chunks=chunks,
            total_chars=total_chars,
        )

    except Exception as exc:
        logger.error("PDF parsing failed for %s: %s", filename, exc)
        return ParseResult(
            source_type="pdf",
            source_filename=filename,
            error=f"PDF parsing failed: {exc}",
        )


# ---------------------------------------------------------------------------
# DOCX parsing
# ---------------------------------------------------------------------------


async def parse_docx(
    file_content: bytes,
    filename: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> ParseResult:
    """Parse a DOCX file into chunked text.

    Extracts paragraphs preserving heading structure.
    """
    try:
        from docx import Document
    except ImportError:
        return ParseResult(
            source_type="docx",
            source_filename=filename,
            error="DOCX parsing requires 'python-docx' package. Install: pip install python-docx>=1.1.0",
        )

    try:
        doc = Document(io.BytesIO(file_content))
        paragraphs: list[str] = []

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            # Check if this is a heading
            if para.style and para.style.name and para.style.name.startswith("Heading"):
                # Add heading marker for chunking awareness
                level = para.style.name.replace("Heading ", "").replace("Heading", "1")
                try:
                    h_level = int(level)
                except ValueError:
                    h_level = 1
                prefix = "#" * min(h_level, 3)
                paragraphs.append(f"{prefix} {text}")
            else:
                paragraphs.append(text)

        if not paragraphs:
            return ParseResult(
                source_type="docx",
                source_filename=filename,
                error="No text content found in DOCX file.",
            )

        full_text = "\n\n".join(paragraphs)
        total_chars = len(full_text)

        title = os.path.splitext(filename)[0].replace("-", " ").replace("_", " ").title()

        # Also try to extract title from document properties
        if doc.core_properties and doc.core_properties.title:
            title = doc.core_properties.title

        chunks = chunk_text(
            text=full_text,
            title=title,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            source_metadata={"paragraph_count": len(paragraphs), "source": "docx"},
        )

        return ParseResult(
            source_type="docx",
            source_filename=filename,
            chunks=chunks,
            total_chars=total_chars,
        )

    except Exception as exc:
        logger.error("DOCX parsing failed for %s: %s", filename, exc)
        return ParseResult(
            source_type="docx",
            source_filename=filename,
            error=f"DOCX parsing failed: {exc}",
        )


# ---------------------------------------------------------------------------
# CSV parsing — Q&A pairs
# ---------------------------------------------------------------------------


async def parse_csv(
    file_content: bytes,
    filename: str,
) -> ParseResult:
    """Parse a CSV file into KB entries.

    Expected format: title,content[,entry_type][,tags]
    First row is treated as header if it contains "title" and "content".
    Each row becomes a separate KB entry (not chunked).
    """
    try:
        text = file_content.decode("utf-8-sig")  # Handle BOM
    except UnicodeDecodeError:
        try:
            text = file_content.decode("latin-1")
        except UnicodeDecodeError:
            return ParseResult(
                source_type="csv",
                source_filename=filename,
                error="Cannot decode CSV file. Ensure UTF-8 or Latin-1 encoding.",
            )

    try:
        reader = csv.reader(io.StringIO(text))
        rows = list(reader)

        if len(rows) < 2:
            return ParseResult(
                source_type="csv",
                source_filename=filename,
                error="CSV file must have at least a header row and one data row.",
            )

        # Detect header
        header = [h.strip().lower() for h in rows[0]]
        if "title" not in header or "content" not in header:
            return ParseResult(
                source_type="csv",
                source_filename=filename,
                error="CSV header must include 'title' and 'content' columns. "
                f"Found columns: {', '.join(header)}",
            )

        title_idx = header.index("title")
        content_idx = header.index("content")
        type_idx = header.index("entry_type") if "entry_type" in header else None
        tags_idx = header.index("tags") if "tags" in header else None

        chunks: list[ParsedChunk] = []
        total_chars = 0

        for row_num, row in enumerate(rows[1:], start=2):
            if len(row) <= max(title_idx, content_idx):
                continue  # Skip malformed rows

            title = row[title_idx].strip()
            content = row[content_idx].strip()

            if not title or not content:
                continue

            entry_type = "faq"
            if type_idx is not None and len(row) > type_idx:
                et = row[type_idx].strip().lower()
                if et in ("product", "faq", "policy", "custom"):
                    entry_type = et

            tags: list[str] = []
            if tags_idx is not None and len(row) > tags_idx:
                raw_tags = row[tags_idx].strip()
                if raw_tags:
                    tags = [t.strip() for t in raw_tags.split(";") if t.strip()]

            total_chars += len(title) + len(content)

            chunks.append(
                ParsedChunk(
                    text=content,
                    title=title,
                    chunk_index=row_num - 2,
                    metadata={
                        "entry_type": entry_type,
                        "tags": tags,
                        "csv_row": row_num,
                        "source": "csv",
                    },
                )
            )

        if not chunks:
            return ParseResult(
                source_type="csv",
                source_filename=filename,
                error="No valid data rows found in CSV.",
            )

        return ParseResult(
            source_type="csv",
            source_filename=filename,
            chunks=chunks,
            total_chars=total_chars,
        )

    except csv.Error as exc:
        return ParseResult(
            source_type="csv",
            source_filename=filename,
            error=f"CSV parsing error: {exc}",
        )


# ---------------------------------------------------------------------------
# TXT parsing
# ---------------------------------------------------------------------------


async def parse_txt(
    file_content: bytes,
    filename: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> ParseResult:
    """Parse a plain text file into chunked entries."""
    try:
        text = file_content.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            text = file_content.decode("latin-1")
        except UnicodeDecodeError:
            return ParseResult(
                source_type="txt",
                source_filename=filename,
                error="Cannot decode text file. Ensure UTF-8 or Latin-1 encoding.",
            )

    text = text.strip()
    if not text:
        return ParseResult(
            source_type="txt",
            source_filename=filename,
            error="Text file is empty.",
        )

    title = os.path.splitext(filename)[0].replace("-", " ").replace("_", " ").title()

    chunks = chunk_text(
        text=text,
        title=title,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        source_metadata={"source": "txt"},
    )

    return ParseResult(
        source_type="txt",
        source_filename=filename,
        chunks=chunks,
        total_chars=len(text),
    )


# ---------------------------------------------------------------------------
# URL scraping
# ---------------------------------------------------------------------------


async def parse_url(
    url: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> ParseResult:
    """Scrape a web page and extract text content.

    Uses httpx for fetching and BeautifulSoup for HTML parsing.
    Extracts main content, strips navigation/footer/scripts.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return ParseResult(
            source_type="url",
            source_url=url,
            error="URL scraping requires 'beautifulsoup4' package. Install: pip install beautifulsoup4>=4.12.0",
        )

    import httpx

    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            max_redirects=MAX_URL_REDIRECTS,
            timeout=URL_FETCH_TIMEOUT,
            headers={"User-Agent": CRAWLER_USER_AGENT},
        ) as client:
            response = await client.get(url)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                return ParseResult(
                    source_type="url",
                    source_url=url,
                    error=f"URL returned non-HTML content type: {content_type}",
                )

            if len(response.content) > MAX_URL_SIZE:
                return ParseResult(
                    source_type="url",
                    source_url=url,
                    error=f"Page content too large ({len(response.content):,} bytes). Maximum: {MAX_URL_SIZE:,} bytes",
                )

            html = response.text

    except httpx.HTTPStatusError as exc:
        return ParseResult(
            source_type="url",
            source_url=url,
            error=f"HTTP error {exc.response.status_code} fetching URL",
        )
    except httpx.RequestError as exc:
        return ParseResult(
            source_type="url",
            source_url=url,
            error=f"Failed to fetch URL: {exc}",
        )

    try:
        soup = BeautifulSoup(html, "html.parser")

        # Remove non-content elements
        for tag in soup.find_all(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
            tag.decompose()

        # Try to find main content
        main = soup.find("main") or soup.find("article") or soup.find("div", {"role": "main"})
        if main:
            text = main.get_text(separator="\n\n", strip=True)
        else:
            body = soup.find("body")
            text = body.get_text(separator="\n\n", strip=True) if body else soup.get_text(separator="\n\n", strip=True)

        if not text or len(text.strip()) < 50:
            return ParseResult(
                source_type="url",
                source_url=url,
                error="No meaningful text content found on the page.",
            )

        # Extract title
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else url

        # Clean up excessive whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.strip()

        chunks = chunk_text(
            text=text,
            title=title,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            source_metadata={"url": url, "source": "url"},
        )

        return ParseResult(
            source_type="url",
            source_url=url,
            chunks=chunks,
            total_chars=len(text),
        )

    except Exception as exc:
        logger.error("HTML parsing failed for %s: %s", url, exc)
        return ParseResult(
            source_type="url",
            source_url=url,
            error=f"HTML parsing failed: {exc}",
        )


# ---------------------------------------------------------------------------
# URL crawling — multi-page import (C5)
# ---------------------------------------------------------------------------


async def crawl_url(
    start_url: str,
    max_pages: int = CRAWL_DEFAULT_MAX_PAGES,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[ParseResult]:
    """Crawl a website starting from *start_url*, following same-domain links.

    Fetches the start page, extracts all ``<a href="...">`` links on the
    same domain, then recursively follows them up to *max_pages* total pages.

    Each successfully fetched page is parsed independently via :func:`parse_url`
    and returned as a separate :class:`ParseResult`.  Pages that fail to fetch
    or parse are silently skipped (logged as warnings).

    Args:
        start_url: The seed URL to begin crawling from.
        max_pages: Maximum number of pages to fetch (1-50).  Clamped to
            ``CRAWL_MAX_PAGES_HARD_LIMIT``.
        chunk_size: Target chunk size in tokens for each page's text.
        chunk_overlap: Overlap between consecutive chunks in tokens.

    Returns:
        A list of :class:`ParseResult` instances, one per successfully
        parsed page.  The first element is always the start page (if it
        succeeded).
    """
    try:
        from bs4 import BeautifulSoup  # noqa: F811
    except ImportError:
        return [
            ParseResult(
                source_type="url",
                source_url=start_url,
                error="URL crawling requires 'beautifulsoup4'. Install: pip install beautifulsoup4>=4.12.0",
            )
        ]

    from urllib.parse import urljoin, urlparse

    import httpx

    max_pages = max(1, min(max_pages, CRAWL_MAX_PAGES_HARD_LIMIT))
    start_parsed = urlparse(start_url)
    base_domain = start_parsed.netloc.lower()

    visited: set[str] = set()
    queue: list[str] = [start_url]
    results: list[ParseResult] = []

    async with httpx.AsyncClient(
        follow_redirects=True,
        max_redirects=MAX_URL_REDIRECTS,
        timeout=URL_FETCH_TIMEOUT,
        headers={"User-Agent": CRAWLER_USER_AGENT},
    ) as client:
        # Fetch and parse robots.txt before crawling (F4)
        from urllib.robotparser import RobotFileParser

        rp = RobotFileParser()
        robots_url = f"{start_parsed.scheme}://{base_domain}/robots.txt"
        try:
            robots_resp = await client.get(robots_url)
            if robots_resp.status_code == 200:
                rp.parse(robots_resp.text.splitlines())
                logger.info("Crawl: loaded robots.txt from %s", robots_url)
            else:
                logger.debug(
                    "Crawl: no robots.txt at %s (status %d)",
                    robots_url, robots_resp.status_code,
                )
        except Exception:
            logger.debug("Crawl: could not fetch robots.txt from %s", robots_url)

        pages_fetched = 0
        while queue and len(results) < max_pages:
            url = queue.pop(0)
            # Normalise for dedup (strip fragment)
            normalised = urlparse(url)._replace(fragment="").geturl()
            if normalised in visited:
                continue
            visited.add(normalised)

            # Respect robots.txt (F4)
            if not rp.can_fetch(CRAWLER_USER_AGENT, url):
                logger.debug("Crawl: robots.txt disallows %s", url)
                continue

            # Polite crawl delay between requests (F6)
            if pages_fetched > 0:
                import asyncio

                await asyncio.sleep(CRAWL_DELAY_SECONDS)

            try:
                response = await client.get(url)
                response.raise_for_status()
                pages_fetched += 1
            except Exception as fetch_exc:
                logger.warning("Crawl: failed to fetch %s: %s", url, fetch_exc)
                continue

            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                logger.debug("Crawl: skipping non-HTML %s (%s)", url, content_type)
                continue

            if len(response.content) > MAX_URL_SIZE:
                logger.warning("Crawl: page too large %s (%d bytes)", url, len(response.content))
                continue

            html = response.text

            # --- Extract same-domain links for the queue ---
            try:
                soup = BeautifulSoup(html, "html.parser")
                for anchor in soup.find_all("a", href=True):
                    href = anchor["href"]
                    absolute = urljoin(url, href)
                    link_parsed = urlparse(absolute)
                    # Same domain only, HTTP(S) only, strip fragment for dedup
                    if (
                        link_parsed.scheme in ("http", "https")
                        and link_parsed.netloc.lower() == base_domain
                    ):
                        clean = link_parsed._replace(fragment="").geturl()
                        if clean not in visited:
                            queue.append(clean)
            except Exception as link_exc:
                logger.warning("Crawl: link extraction error on %s: %s", url, link_exc)

            # --- Parse this page ---
            page_result = await parse_url(
                url,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
            if page_result.success:
                results.append(page_result)
                logger.info(
                    "Crawl: parsed %s (%d chunks, %d chars)",
                    url,
                    len(page_result.chunks),
                    page_result.total_chars,
                )
            else:
                logger.warning("Crawl: parse failed for %s: %s", url, page_result.error)

    logger.info(
        "Crawl complete: start=%s pages_fetched=%d/%d",
        start_url,
        len(results),
        max_pages,
    )
    return results


# ---------------------------------------------------------------------------
# Website crawl — incremental with sitemap + change detection
# ---------------------------------------------------------------------------


def compute_content_hash(text: str) -> str:
    """SHA-256 hex digest of text content for change detection."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass
class WebsiteCrawlResult:
    """Result of an incremental website crawl with change tracking."""

    results: list[ParseResult] = field(default_factory=list)
    new_urls: list[str] = field(default_factory=list)
    changed_urls: list[str] = field(default_factory=list)
    unchanged_urls: list[str] = field(default_factory=list)
    removed_urls: list[str] = field(default_factory=list)
    failed_urls: list[str] = field(default_factory=list)
    pages_discovered: int = 0
    pages_crawled: int = 0
    total_chars: int = 0
    error: str | None = None

    @property
    def articles_created(self) -> int:
        return len(self.new_urls) + len(self.changed_urls)


async def parse_sitemap(
    base_url: str,
    client: Any,
) -> list[str]:
    """Parse sitemap.xml to discover crawlable URLs.

    Handles both standard sitemaps and sitemap index files.
    Returns empty list if no sitemap exists (graceful fallback).
    """
    from urllib.parse import urlparse

    parsed = urlparse(base_url)
    sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
    domain = parsed.netloc.lower()

    try:
        resp = await client.get(sitemap_url)
        if resp.status_code != 200:
            logger.debug("No sitemap at %s (status %d)", sitemap_url, resp.status_code)
            return []

        content_type = resp.headers.get("content-type", "")
        if "xml" not in content_type and "text" not in content_type:
            logger.debug("Sitemap at %s has unexpected content-type: %s", sitemap_url, content_type)
            return []

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(resp.text, "html.parser")
        urls: list[str] = []

        # Check for sitemap index (contains <sitemap><loc> entries)
        sitemap_tags = soup.find_all("sitemap")
        if sitemap_tags:
            # Recurse into child sitemaps (limit to 5 to avoid explosion)
            for sitemap_tag in sitemap_tags[:5]:
                loc = sitemap_tag.find("loc")
                if loc and loc.string:
                    child_urls = await _parse_sitemap_single(loc.string.strip(), client, domain)
                    urls.extend(child_urls)
        else:
            # Standard sitemap with <url><loc> entries
            urls = _extract_sitemap_urls(soup, domain)

        logger.info("Sitemap: found %d URLs from %s", len(urls), sitemap_url)
        return urls

    except Exception as exc:
        logger.debug("Sitemap parsing failed for %s: %s", sitemap_url, exc)
        return []


async def _parse_sitemap_single(
    sitemap_url: str,
    client: Any,
    domain: str,
) -> list[str]:
    """Parse a single sitemap XML file."""
    try:
        resp = await client.get(sitemap_url)
        if resp.status_code != 200:
            return []
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(resp.text, "html.parser")
        return _extract_sitemap_urls(soup, domain)
    except Exception:
        return []


def _extract_sitemap_urls(soup: Any, domain: str) -> list[str]:
    """Extract <url><loc> entries filtered to the target domain."""
    from urllib.parse import urlparse

    urls: list[str] = []
    for url_tag in soup.find_all("url"):
        loc = url_tag.find("loc")
        if loc and loc.string:
            href = loc.string.strip()
            parsed = urlparse(href)
            if parsed.netloc.lower() == domain and parsed.scheme in ("http", "https"):
                urls.append(href)
    return urls


async def crawl_website(
    start_url: str,
    max_pages: int = CRAWL_DEFAULT_MAX_PAGES,
    existing_hashes: dict[str, str] | None = None,
    use_sitemap: bool = True,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> WebsiteCrawlResult:
    """Crawl a website with incremental change detection and sitemap support.

    Enhanced version of crawl_url() for the automated website source feature.
    When existing_hashes is provided, pages with matching content hashes
    are skipped (unchanged), enabling efficient incremental re-crawls.

    Args:
        start_url: Seed URL to begin crawling from.
        max_pages: Maximum pages to fetch (clamped to hard limit).
        existing_hashes: Map of URL → content_hash from previous crawl.
            If None, all pages are treated as new.
        use_sitemap: Whether to try sitemap.xml for URL discovery.
        chunk_size: Target chunk size in tokens.
        chunk_overlap: Overlap between chunks.

    Returns:
        WebsiteCrawlResult with parsed pages and change tracking stats.
    """
    try:
        from bs4 import BeautifulSoup  # noqa: F811
    except ImportError:
        return WebsiteCrawlResult(
            error="Website crawling requires 'beautifulsoup4'. "
                  "Install: pip install beautifulsoup4>=4.12.0",
        )

    import asyncio
    from urllib.parse import urljoin, urlparse

    import httpx

    max_pages = max(1, min(max_pages, CRAWL_MAX_PAGES_HARD_LIMIT))
    start_parsed = urlparse(start_url)
    base_domain = start_parsed.netloc.lower()
    existing = existing_hashes or {}

    result = WebsiteCrawlResult()
    visited: set[str] = set()
    queue: list[str] = [start_url]

    async with httpx.AsyncClient(
        follow_redirects=True,
        max_redirects=MAX_URL_REDIRECTS,
        timeout=URL_FETCH_TIMEOUT,
        headers={"User-Agent": CRAWLER_USER_AGENT},
    ) as client:
        # --- robots.txt ---
        from urllib.robotparser import RobotFileParser

        rp = RobotFileParser()
        robots_url = f"{start_parsed.scheme}://{base_domain}/robots.txt"
        try:
            robots_resp = await client.get(robots_url)
            if robots_resp.status_code == 200:
                rp.parse(robots_resp.text.splitlines())
        except Exception:
            pass

        # --- Sitemap discovery ---
        if use_sitemap:
            sitemap_urls = await parse_sitemap(start_url, client)
            for surl in sitemap_urls:
                normalised = urlparse(surl)._replace(fragment="").geturl()
                if normalised not in visited:
                    queue.append(surl)

        # --- BFS crawl loop ---
        pages_fetched = 0
        crawled_urls: set[str] = set()

        while queue and len(result.results) + len(result.unchanged_urls) < max_pages:
            url = queue.pop(0)
            normalised = urlparse(url)._replace(fragment="").geturl()
            if normalised in visited:
                continue
            visited.add(normalised)
            result.pages_discovered += 1

            if not rp.can_fetch(CRAWLER_USER_AGENT, url):
                continue

            if pages_fetched > 0:
                await asyncio.sleep(CRAWL_DELAY_SECONDS)

            try:
                response = await client.get(url)
                response.raise_for_status()
                pages_fetched += 1
            except Exception as fetch_exc:
                logger.warning("Website crawl: failed to fetch %s: %s", url, fetch_exc)
                result.failed_urls.append(normalised)
                continue

            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                continue

            if len(response.content) > MAX_URL_SIZE:
                continue

            html = response.text
            crawled_urls.add(normalised)

            # --- Extract same-domain links for the queue ---
            try:
                soup = BeautifulSoup(html, "html.parser")
                for anchor in soup.find_all("a", href=True):
                    href = anchor["href"]
                    absolute = urljoin(url, href)
                    link_parsed = urlparse(absolute)
                    if (
                        link_parsed.scheme in ("http", "https")
                        and link_parsed.netloc.lower() == base_domain
                    ):
                        clean = link_parsed._replace(fragment="").geturl()
                        if clean not in visited:
                            queue.append(clean)
            except Exception:
                pass

            # --- Change detection ---
            # Strip non-content for hash (same cleanup as parse_url)
            for tag in soup.find_all(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
                tag.decompose()
            main = soup.find("main") or soup.find("article") or soup.find("div", {"role": "main"})
            raw_text = (main or soup.find("body") or soup).get_text(separator="\n\n", strip=True)
            content_hash = compute_content_hash(raw_text)

            if normalised in existing and existing[normalised] == content_hash:
                result.unchanged_urls.append(normalised)
                result.pages_crawled += 1
                continue

            # --- Parse this page (new or changed) ---
            page_result = await parse_url(
                url, chunk_size=chunk_size, chunk_overlap=chunk_overlap,
            )
            if page_result.success:
                # Attach content_hash to each chunk's metadata for storage
                for chunk in page_result.chunks:
                    chunk.metadata["content_hash"] = content_hash
                    chunk.metadata["crawl_source_url"] = normalised

                result.results.append(page_result)
                result.total_chars += page_result.total_chars
                result.pages_crawled += 1

                if normalised in existing:
                    result.changed_urls.append(normalised)
                else:
                    result.new_urls.append(normalised)
            else:
                result.failed_urls.append(normalised)

    # --- Detect removed pages ---
    if existing:
        for old_url in existing:
            if old_url not in crawled_urls and old_url not in result.unchanged_urls:
                result.removed_urls.append(old_url)

    logger.info(
        "Website crawl complete: start=%s new=%d changed=%d unchanged=%d "
        "removed=%d failed=%d total_pages=%d",
        start_url,
        len(result.new_urls),
        len(result.changed_urls),
        len(result.unchanged_urls),
        len(result.removed_urls),
        len(result.failed_urls),
        result.pages_crawled,
    )
    return result


# ---------------------------------------------------------------------------
# Unified parser dispatch
# ---------------------------------------------------------------------------


async def parse_file(
    file_content: bytes,
    filename: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> ParseResult:
    """Parse any supported file type into chunks.

    Dispatches to the appropriate parser based on file extension.
    """
    _, ext = os.path.splitext(filename.lower())

    parsers = {
        ".pdf": parse_pdf,
        ".docx": parse_docx,
        ".txt": parse_txt,
    }

    parser = parsers.get(ext)
    if parser is None:
        if ext == ".csv":
            return await parse_csv(file_content, filename)
        return ParseResult(
            source_type="manual",
            source_filename=filename,
            error=f"Unsupported file type: {ext}",
        )

    return await parser(file_content, filename, chunk_size, chunk_overlap)


def chunks_to_kb_entries(
    parse_result: ParseResult,
    tenant_id: str,
    default_entry_type: str = "custom",
    parent_entry_id: str | None = None,
) -> list[dict[str, Any]]:
    """Convert parsed chunks into KnowledgeBaseDocument-compatible dicts.

    Args:
        parse_result: Result from parse_file or parse_url.
        tenant_id: Owning tenant.
        default_entry_type: Default entry type if not specified in metadata.
        parent_entry_id: ID of parent document (for multi-chunk documents).

    Returns:
        List of dicts ready for KnowledgeBaseRepository.create().
    """
    if not parse_result.success:
        return []

    now = datetime.now(UTC).isoformat()
    entries: list[dict[str, Any]] = []

    # For single-chunk results, use the parent_entry_id as the ID itself
    # For multi-chunk, generate a parent ID if not provided
    if len(parse_result.chunks) > 1 and parent_entry_id is None:
        parent_entry_id = str(uuid.uuid4())

    for chunk in parse_result.chunks:
        entry_id = str(uuid.uuid4())
        metadata = dict(chunk.metadata)

        # CSV rows carry their own entry_type
        entry_type = metadata.pop("entry_type", default_entry_type)
        tags = metadata.pop("tags", [])

        entry: dict[str, Any] = {
            "id": entry_id,
            "tenant_id": tenant_id,
            "entry_type": entry_type,
            "title": chunk.title,
            "content": chunk.text,
            "metadata": metadata,
            "tags": tags if isinstance(tags, list) else [],
            "language": "en",
            "is_active": True,
            "source_type": parse_result.source_type,
            "source_filename": parse_result.source_filename,
            "source_url": parse_result.source_url,
            "chunk_index": chunk.chunk_index if len(parse_result.chunks) > 1 else None,
            "parent_entry_id": parent_entry_id if len(parse_result.chunks) > 1 else None,
            "created_at": now,
            "updated_at": now,
        }

        entries.append(entry)

    return entries
