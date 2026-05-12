# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Smart-poller bridge INDEX.md parser, detector, and shape model.

Per ``bridge/gtkb-bridge-poller-p1-detector-003.md`` (REVISED-1, GO at -004) and
``bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-007.md``
(REVISED-3, GO at -008), this module owns the parser state machine, the
in-memory shape model, and the warning-vs-error policy.

Out of scope for this module: checkpoint/diff (see checkpoint.py),
routing/transitions (see routing.py), audit emission (see audit.py),
harness invocation (P3, gated on P2.5 spike).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Literal


# Status vocabulary per .claude/rules/file-bridge-protocol.md.
class BridgeStatus(StrEnum):
    NEW = "NEW"
    REVISED = "REVISED"
    GO = "GO"
    NO_GO = "NO-GO"
    VERIFIED = "VERIFIED"
    ADVISORY = "ADVISORY"
    WITHDRAWN = "WITHDRAWN"


# Match status lines: ``<STATUS>: bridge/<name>-<NNN>.md``.
_STATUS_LINE_RE = re.compile(
    r"^(?P<status>NEW|REVISED|GO|NO-GO|VERIFIED|ADVISORY|WITHDRAWN):\s+"
    r"bridge/(?P<name>[A-Za-z0-9._-]+?)-(?P<version>\d+)\.md\s*$"
)
_DOCUMENT_LINE_RE = re.compile(r"^Document:\s+(?P<name>[A-Za-z0-9._-]+)\s*$")
_HEADING_LINE_RE = re.compile(r"^\s*#")
_SINGLE_LINE_COMMENT_RE = re.compile(r"^\s*<!--.*-->\s*$")
_MULTILINE_COMMENT_OPEN_RE = re.compile(r"^\s*<!--\s*$")
_MULTILINE_COMMENT_CLOSE_RE = re.compile(r"^\s*-->\s*$")

WarningKind = Literal[
    "referenced_file_missing",
    "current_top_file_missing",
    "historical_audit_block_skipped",
    "filename_does_not_match_document_name",
]


@dataclass(frozen=True)
class BridgeVersion:
    """A single status line within a document entry."""

    status: BridgeStatus
    file_path: str  # relative path, e.g. "bridge/foo-001.md"
    line_number: int  # 1-indexed line in INDEX.md


@dataclass(frozen=True)
class BridgeDocument:
    """A single bridge document entry (Document: <name> + version list)."""

    name: str
    versions: tuple[BridgeVersion, ...]
    line_number: int  # line of the Document: header

    @property
    def current_top(self) -> BridgeVersion | None:
        """Return the most-recent (top-of-list) version, or None if empty."""
        return self.versions[0] if self.versions else None


@dataclass(frozen=True)
class ParseWarning:
    kind: WarningKind
    line_number: int
    detail: str


@dataclass(frozen=True)
class ParseError:
    line_number: int
    content: str
    expected_state: str


@dataclass(frozen=True)
class ParseResult:
    documents: tuple[BridgeDocument, ...]
    warnings: tuple[ParseWarning, ...] = field(default_factory=tuple)
    errors: tuple[ParseError, ...] = field(default_factory=tuple)


def _strip_bom(text: str) -> str:
    return text.lstrip("﻿")


def _is_blank(line: str) -> bool:
    return line.strip() == ""


def parse_index(index_text: str, *, project_root: Path | None = None) -> ParseResult:
    """Parse the bridge INDEX.md content into a ``ParseResult``.

    Args:
        index_text: full text of ``bridge/INDEX.md``.
        project_root: optional path used to validate ``referenced_file_missing``
            warnings. When ``None``, no file-existence checks are performed.

    The parser implements the state machine specified in
    ``bridge/gtkb-bridge-poller-p1-detector-003.md`` section 3.2:

    * preamble lines (``#`` headings, single-line ``<!-- ... -->``, blanks) skip silently.
    * multi-line HTML comment blocks (bare ``<!--`` ... bare ``-->``) skip silently.
    * ``Document: <name>`` opens a document entry; status lines populate it.
    * a blank line ends a document entry (back to body state).
    * unrecognized lines in body/document state become ``ParseError`` entries
      but the parser continues.

    File-existence policy (section 3.3): missing referenced files produce
    ``ParseWarning(kind="referenced_file_missing")``, NOT ``ParseError``.
    The parse succeeds even when historical references are absent on disk.
    """
    text = _strip_bom(index_text).replace("\r\n", "\n")
    lines = text.split("\n")
    documents: list[BridgeDocument] = []
    warnings: list[ParseWarning] = []
    errors: list[ParseError] = []

    state: str = "preamble"
    current_doc_name: str | None = None
    current_doc_line: int = 0
    current_versions: list[BridgeVersion] = []

    def flush_doc() -> None:
        nonlocal current_doc_name, current_doc_line, current_versions
        if current_doc_name is not None:
            documents.append(
                BridgeDocument(
                    name=current_doc_name,
                    versions=tuple(current_versions),
                    line_number=current_doc_line,
                )
            )
        current_doc_name = None
        current_doc_line = 0
        current_versions = []

    for idx, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip()  # tolerate trailing whitespace

        if state == "comment_block":
            if _MULTILINE_COMMENT_CLOSE_RE.match(line):
                state = "body"
            # All lines (incl. closer) consumed silently.
            continue

        if _MULTILINE_COMMENT_OPEN_RE.match(line):
            # Distinguish from single-line comments which would have matched
            # _SINGLE_LINE_COMMENT_RE first below.
            if not _SINGLE_LINE_COMMENT_RE.match(line):
                # Flush any in-progress document on a comment-block boundary.
                if state == "document":
                    flush_doc()
                state = "comment_block"
                continue

        # Preamble / single-line comment / heading / blank → silent.
        if state == "preamble":
            if _HEADING_LINE_RE.match(line) or _SINGLE_LINE_COMMENT_RE.match(line) or _is_blank(line):
                continue
            state = "body"

        if _SINGLE_LINE_COMMENT_RE.match(line) or _HEADING_LINE_RE.match(line):
            # In body or document, single-line comments and headings are
            # tolerated as silent skips.
            if state == "document":
                # A heading or comment between status lines flushes the doc.
                flush_doc()
                state = "body"
            continue

        if _is_blank(line):
            if state == "document":
                flush_doc()
                state = "body"
            continue

        doc_match = _DOCUMENT_LINE_RE.match(line)
        if doc_match:
            if state == "document":
                flush_doc()
            current_doc_name = doc_match.group("name")
            current_doc_line = idx
            current_versions = []
            state = "document"
            continue

        if state == "document":
            status_match = _STATUS_LINE_RE.match(line)
            if status_match:
                status_str = status_match.group("status")
                file_name = status_match.group("name")
                version_str = status_match.group("version")
                file_path = f"bridge/{file_name}-{version_str}.md"

                if file_name != current_doc_name:
                    warnings.append(
                        ParseWarning(
                            kind="filename_does_not_match_document_name",
                            line_number=idx,
                            detail=(
                                f"Status line references "
                                f"bridge/{file_name}-{version_str}.md but "
                                f"current Document is '{current_doc_name}'"
                            ),
                        )
                    )

                current_versions.append(
                    BridgeVersion(
                        status=BridgeStatus(status_str),
                        file_path=file_path,
                        line_number=idx,
                    )
                )

                if project_root is not None:
                    full = project_root / file_path
                    if not full.is_file():
                        warnings.append(
                            ParseWarning(
                                kind="referenced_file_missing",
                                line_number=idx,
                                detail=f"Referenced file missing on disk: {file_path}",
                            )
                        )
                continue

            # Unrecognized line in document state.
            errors.append(
                ParseError(
                    line_number=idx,
                    content=raw_line,
                    expected_state="status_line",
                )
            )
            continue

        # Unrecognized line in body state.
        errors.append(
            ParseError(
                line_number=idx,
                content=raw_line,
                expected_state="document_or_blank",
            )
        )

    flush_doc()  # final document at EOF

    # Re-classify current_top file-missing as a sharper warning kind for
    # routing-relevant cases.
    if project_root is not None:
        sharpened: list[ParseWarning] = []
        # Build a quick lookup of (line_number) → BridgeDocument that owns the top status.
        top_lines = {doc.versions[0].line_number for doc in documents if doc.versions}
        for w in warnings:
            if w.kind == "referenced_file_missing" and w.line_number in top_lines:
                sharpened.append(
                    ParseWarning(
                        kind="current_top_file_missing",
                        line_number=w.line_number,
                        detail=w.detail,
                    )
                )
            else:
                sharpened.append(w)
        warnings = sharpened

    return ParseResult(
        documents=tuple(documents),
        warnings=tuple(warnings),
        errors=tuple(errors),
    )
