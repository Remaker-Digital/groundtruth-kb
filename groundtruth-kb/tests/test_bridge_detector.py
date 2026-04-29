# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for groundtruth_kb.bridge.detector.

Per ``bridge/gtkb-bridge-poller-p1-detector-003.md`` section 4.1, these tests
cover the parser state machine (preamble, single-line comments, multi-line
comments, blank-line separators, CRLF, BOM), status-enum validation, filename
mismatch detection, missing-reference warning policy, malformed-line error
recovery, and the live INDEX.md regression.
"""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.bridge.detector import (
    BridgeStatus,
    parse_index,
)


def test_parser_handles_canonical_index_layout() -> None:
    text = "# Bridge Index\n\nDocument: foo\nGO: bridge/foo-002.md\nNEW: bridge/foo-001.md\n"
    result = parse_index(text)
    assert len(result.documents) == 1
    doc = result.documents[0]
    assert doc.name == "foo"
    assert len(doc.versions) == 2
    assert doc.versions[0].status == BridgeStatus.GO
    assert doc.versions[0].file_path == "bridge/foo-002.md"
    assert doc.versions[1].status == BridgeStatus.NEW
    assert result.errors == ()


def test_parser_handles_markdown_heading_preamble() -> None:
    text = "# Bridge Index\n## Subheading\n\nDocument: foo\nNEW: bridge/foo-001.md\n"
    result = parse_index(text)
    assert result.errors == ()
    assert len(result.documents) == 1


def test_parser_handles_singleline_html_comments() -> None:
    text = (
        "# Bridge Index\n"
        "<!-- Prime inserts new document entries at the top -->\n"
        "<!-- Statuses: NEW, REVISED, GO, NO-GO, VERIFIED -->\n"
        "\n"
        "Document: foo\n"
        "NEW: bridge/foo-001.md\n"
    )
    result = parse_index(text)
    assert result.errors == ()
    assert len(result.documents) == 1


def test_parser_handles_multiline_html_comment_blocks() -> None:
    text = (
        "# Bridge Index\n"
        "\n"
        "Document: foo\n"
        "NEW: bridge/foo-001.md\n"
        "\n"
        "<!--\n"
        "  Multi-line audit trail note about parallel-poller artifacts.\n"
        "  This block must be silently consumed by the parser.\n"
        "-->\n"
        "Document: bar\n"
        "NEW: bridge/bar-001.md\n"
    )
    result = parse_index(text)
    assert result.errors == ()
    assert len(result.documents) == 2
    assert {d.name for d in result.documents} == {"foo", "bar"}


def test_parser_handles_blank_line_separators() -> None:
    text = "Document: foo\nNEW: bridge/foo-001.md\n\n\nDocument: bar\nNEW: bridge/bar-001.md\n"
    result = parse_index(text)
    assert result.errors == ()
    assert len(result.documents) == 2


def test_parser_handles_crlf_line_endings() -> None:
    text = "Document: foo\r\nNEW: bridge/foo-001.md\r\n"
    result = parse_index(text)
    assert result.errors == ()
    assert len(result.documents) == 1


def test_parser_handles_utf8_bom() -> None:
    text = "﻿# Bridge Index\n\nDocument: foo\nNEW: bridge/foo-001.md\n"
    result = parse_index(text)
    assert result.errors == ()
    assert len(result.documents) == 1


def test_parser_validates_status_enum() -> None:
    text = "Document: foo\nBOGUS: bridge/foo-001.md\n"
    result = parse_index(text)
    # BOGUS is not a status; line is unrecognized in document state.
    assert len(result.errors) == 1
    assert result.errors[0].expected_state == "status_line"


def test_parser_validates_filename_matches_document_name() -> None:
    text = "Document: foo\nNEW: bridge/foo-001.md\nGO: bridge/baz-002.md\n"
    result = parse_index(text)
    # baz-002 status line is structurally valid (still recorded as a version),
    # but a warning fires for the filename mismatch.
    assert len(result.documents) == 1
    assert len(result.documents[0].versions) == 2
    assert any(w.kind == "filename_does_not_match_document_name" for w in result.warnings)


def test_parser_returns_warning_not_error_for_missing_referenced_file(
    tmp_path: Path,
) -> None:
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "foo-002.md").write_text("")
    # foo-001.md intentionally missing
    text = "Document: foo\nGO: bridge/foo-002.md\nNEW: bridge/foo-001.md\n"
    result = parse_index(text, project_root=tmp_path)
    assert result.errors == ()
    missing = [w for w in result.warnings if w.kind == "referenced_file_missing"]
    assert len(missing) == 1
    assert "foo-001" in missing[0].detail


def test_parser_returns_errors_continues_on_malformed_lines() -> None:
    text = "Document: foo\nNEW: bridge/foo-001.md\nthis is not a status line\nGO: bridge/foo-002.md\n"
    result = parse_index(text)
    # Parser continues past the malformed line and still captures both
    # status entries.
    assert len(result.documents) == 1
    assert len(result.documents[0].versions) == 2
    assert len(result.errors) == 1
    assert result.errors[0].line_number == 3


def test_parser_against_live_index_md() -> None:
    """Live INDEX regression: parses successfully against frozen snapshot.

    Asserts:
    - ParseResult.documents is non-empty
    - ParseResult.errors == () (no truly malformed lines)
    - ParseResult.warnings may be non-empty (missing historical refs OK)
    - Multi-line comment blocks are consumed silently (neither errors nor warnings)
    """
    fixture = Path(__file__).parent / "fixtures" / "bridge_index_live_snapshot.md"
    assert fixture.is_file(), f"Expected fixture at {fixture}"
    text = fixture.read_text(encoding="utf-8")
    result = parse_index(text)
    assert result.errors == ()
    assert len(result.documents) >= 30, f"Expected ≥30 documents in live INDEX snapshot, got {len(result.documents)}"
    # Multi-line comment lines (bare <!-- and -->) should never produce errors
    # or be misinterpreted as documents.
    for d in result.documents:
        assert not d.name.startswith("<!--")
        assert not d.name.startswith("-->")


def test_current_top_file_missing_warning_kind(tmp_path: Path) -> None:
    """When the current top status file is missing, warning kind sharpens
    to ``current_top_file_missing`` per design §3.3.
    """
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "foo-001.md").write_text("")
    # foo-002 (current top) intentionally missing
    text = "Document: foo\nGO: bridge/foo-002.md\nNEW: bridge/foo-001.md\n"
    result = parse_index(text, project_root=tmp_path)
    assert any(w.kind == "current_top_file_missing" for w in result.warnings)
