"""Lossless canonical-INDEX parser/serializer + text-observable integrity
diagnostics (WI-4508, Slice A).

This module establishes the lossless ``parse`` / ``serialize`` round-trip that
any TAFE-authoritative generated bridge index depends on, and surfaces the
*text-observable* half of the WI-4481 corruption classes from a single
``index_text`` input:

* **byte-fidelity** of the parse/serialize round-trip,
* **malformed lines** (a non-blank line inside a document block that is neither a
  ``Document:`` line nor a ``<STATUS>: bridge/<slug>-NNN.md`` version line),
* **duplicate-document** blocks (the same ``Document: <name>`` appearing more
  than once), and
* **version-order anomalies** (a block whose version lines are not in monotonic
  latest-first ``-NNN`` order).

What this module does **not** claim (per the Loyal Opposition NO-GO at
``bridge/gtkb-tafe-dual-write-index-parity-002.md`` / ``-003.md``): it cannot
detect a document block that is *already absent* from ``index_text``. Lost-block
(absent-from-text) detection requires an external expected-document oracle and
is explicitly deferred to Slice B.

The canonical bridge index remains the authoritative workflow state per
``GOV-FILE-BRIDGE-AUTHORITY-001``. This module is pure: it performs no file I/O,
no subprocess, no MemBase mutation, and holds no canonical-index path literal.
The read-only ``gt flow index-parity`` CLI in ``cli.py`` is the only surface that
reads the canonical index, and it never writes it.

Specification links: ``SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`` (lossless
round-trippable parallel view), ``GOV-FILE-BRIDGE-AUTHORITY-001`` (canonical
INDEX preserved; no write surface).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

__all__ = [
    "DocumentBlock",
    "IndexVersionLine",
    "MalformedLine",
    "ParsedBridgeIndex",
    "RoundTripReport",
    "VersionOrderAnomaly",
    "parse_bridge_index",
    "roundtrip_report",
    "serialize_bridge_index",
]

_DOCUMENT_PREFIX = "Document:"

# A canonical version line: ``<STATUS>: bridge/<slug>-NNN.md``. The status token
# is any run of non-colon, non-whitespace characters (so ``NO-GO`` and
# ``WITHDRAWN`` both match); the path must be a bridge file ending in ``-NNN.md``.
# The non-greedy slug lets the trailing ``-(\d+)\.md`` anchor capture the version.
_VERSION_LINE_RE = re.compile(r"^(?P<status>[^:\s]+):[ \t]+(?P<path>bridge/\S+?-(?P<version>\d+)\.md)[ \t]*$")


@dataclass(frozen=True)
class IndexVersionLine:
    """A classified ``<STATUS>: bridge/<slug>-NNN.md`` version line.

    ``raw`` preserves the exact source line (including its terminator) so the
    serializer can re-emit it byte-identically.
    """

    status: str
    path: str
    version: int
    line_number: int
    raw: str


@dataclass(frozen=True)
class MalformedLine:
    """A non-blank line inside a document block that matches no recognized shape."""

    line_number: int
    text: str


@dataclass(frozen=True)
class VersionOrderAnomaly:
    """A document block whose version lines are not strictly latest-first."""

    document: str
    versions: tuple[int, ...]


@dataclass(frozen=True)
class DocumentBlock:
    """One ``Document: <name>`` block plus its ordered body.

    ``body_raw`` is the verbatim sequence of source lines (with terminators)
    following the ``Document:`` line up to the next block or end-of-file, so the
    block re-serializes byte-identically. ``version_lines`` and
    ``malformed_lines`` are the classified, diagnostic views of that body; they
    never participate in serialization.
    """

    name: str
    document_line_number: int
    document_raw: str
    body_raw: tuple[str, ...]
    version_lines: tuple[IndexVersionLine, ...]
    malformed_lines: tuple[MalformedLine, ...]


@dataclass(frozen=True)
class ParsedBridgeIndex:
    """Structured, lossless view of a canonical ``bridge/INDEX.md`` text.

    ``preamble_raw`` holds any header/comment lines before the first
    ``Document:`` block. ``serialize`` reconstructs the exact original text.
    """

    preamble_raw: tuple[str, ...]
    blocks: tuple[DocumentBlock, ...]

    def serialize(self) -> str:
        """Re-emit the byte-identical source text for any parsed input."""
        parts: list[str] = list(self.preamble_raw)
        for block in self.blocks:
            parts.append(block.document_raw)
            parts.extend(block.body_raw)
        return "".join(parts)


@dataclass(frozen=True)
class RoundTripReport:
    """Text-observable integrity report for a single ``index_text`` input."""

    byte_identical: bool
    document_count: int
    malformed_lines: tuple[MalformedLine, ...]
    duplicate_documents: tuple[str, ...]
    version_order_anomalies: tuple[VersionOrderAnomaly, ...]

    @property
    def ok(self) -> bool:
        """True when no text-observable integrity anomaly was found."""
        return (
            self.byte_identical
            and not self.malformed_lines
            and not self.duplicate_documents
            and not self.version_order_anomalies
        )

    def as_dict(self) -> dict[str, Any]:
        """A JSON-serializable view of the report."""
        return {
            "ok": self.ok,
            "byte_identical": self.byte_identical,
            "document_count": self.document_count,
            "malformed_lines": [{"line_number": item.line_number, "text": item.text} for item in self.malformed_lines],
            "duplicate_documents": list(self.duplicate_documents),
            "version_order_anomalies": [
                {"document": anomaly.document, "versions": list(anomaly.versions)}
                for anomaly in self.version_order_anomalies
            ],
        }


def _is_document_line(raw: str) -> bool:
    """True when ``raw`` is a canonical ``Document:`` block header (column 0)."""
    return raw.rstrip("\r\n").startswith(_DOCUMENT_PREFIX)


def _document_name(raw: str) -> str:
    """Extract the document name from a ``Document: <name>`` line."""
    return raw.rstrip("\r\n")[len(_DOCUMENT_PREFIX) :].strip()


def parse_bridge_index(index_text: str) -> ParsedBridgeIndex:
    """Parse canonical ``bridge/INDEX.md`` text into a lossless structured view.

    The parser preserves every source line verbatim (terminators included) so
    that ``serialize_bridge_index(parse_bridge_index(t)) == t`` for any input.
    Status tokens are preserved as written; the canonical vocabulary (NEW,
    REVISED, GO, NO-GO, VERIFIED, ADVISORY, DEFERRED, WITHDRAWN) and
    historically-present tokens (ACCEPTED, BLOCKED, …) all round-trip unchanged.
    """
    raw_lines = index_text.splitlines(keepends=True)
    total = len(raw_lines)

    index = 0
    preamble: list[str] = []
    while index < total and not _is_document_line(raw_lines[index]):
        preamble.append(raw_lines[index])
        index += 1

    blocks: list[DocumentBlock] = []
    while index < total:
        document_raw = raw_lines[index]
        document_line_number = index + 1
        name = _document_name(document_raw)
        index += 1

        body: list[str] = []
        version_lines: list[IndexVersionLine] = []
        malformed: list[MalformedLine] = []
        while index < total and not _is_document_line(raw_lines[index]):
            raw = raw_lines[index]
            line_number = index + 1
            content = raw.rstrip("\r\n")
            body.append(raw)
            if content.strip() == "":
                index += 1
                continue
            match = _VERSION_LINE_RE.match(content)
            if match is not None:
                version_lines.append(
                    IndexVersionLine(
                        status=match.group("status"),
                        path=match.group("path"),
                        version=int(match.group("version")),
                        line_number=line_number,
                        raw=raw,
                    )
                )
            else:
                malformed.append(MalformedLine(line_number=line_number, text=content.strip()))
            index += 1

        blocks.append(
            DocumentBlock(
                name=name,
                document_line_number=document_line_number,
                document_raw=document_raw,
                body_raw=tuple(body),
                version_lines=tuple(version_lines),
                malformed_lines=tuple(malformed),
            )
        )

    return ParsedBridgeIndex(preamble_raw=tuple(preamble), blocks=tuple(blocks))


def serialize_bridge_index(parsed: ParsedBridgeIndex) -> str:
    """Inverse of :func:`parse_bridge_index`; byte-identical for any parsed input."""
    return parsed.serialize()


def _strictly_descending(versions: tuple[int, ...]) -> bool:
    """True when each version is strictly greater than the one after it."""
    return all(earlier > later for earlier, later in zip(versions, versions[1:], strict=False))


def roundtrip_report(index_text: str) -> RoundTripReport:
    """Parse, serialize, and report text-observable integrity diagnostics.

    Reports round-trip byte-fidelity, malformed lines, duplicate document
    blocks, and version-order anomalies. It does **not** detect document blocks
    absent from ``index_text`` (no in-text oracle exists; deferred to Slice B).
    """
    parsed = parse_bridge_index(index_text)
    byte_identical = serialize_bridge_index(parsed) == index_text

    malformed = tuple(item for block in parsed.blocks for item in block.malformed_lines)

    seen: dict[str, int] = {}
    duplicates: list[str] = []
    for block in parsed.blocks:
        count = seen.get(block.name, 0) + 1
        seen[block.name] = count
        if count == 2:
            duplicates.append(block.name)

    anomalies: list[VersionOrderAnomaly] = []
    for block in parsed.blocks:
        versions = tuple(line.version for line in block.version_lines)
        if len(versions) >= 2 and not _strictly_descending(versions):
            anomalies.append(VersionOrderAnomaly(document=block.name, versions=versions))

    return RoundTripReport(
        byte_identical=byte_identical,
        document_count=len(parsed.blocks),
        malformed_lines=malformed,
        duplicate_documents=tuple(duplicates),
        version_order_anomalies=tuple(anomalies),
    )
