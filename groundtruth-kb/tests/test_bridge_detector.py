# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for groundtruth_kb.bridge.detector.

Bridge imports are lazy per tests/test_bridge_import_hygiene.py rule.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace


def _detector() -> SimpleNamespace:
    """Lazy-import bridge.detector per test_bridge_import_hygiene rule."""
    from groundtruth_kb.bridge.detector import BridgeStatus, parse_index

    return SimpleNamespace(BridgeStatus=BridgeStatus, parse_index=parse_index)


def test_parser_handles_canonical_index_layout() -> None:
    d = _detector()
    text = "# Bridge Index\n\nDocument: foo\nGO: bridge/foo-002.md\nNEW: bridge/foo-001.md\n"
    result = d.parse_index(text)
    assert len(result.documents) == 1
    doc = result.documents[0]
    assert doc.name == "foo"
    assert len(doc.versions) == 2
    assert doc.versions[0].status == d.BridgeStatus.GO
    assert doc.versions[0].file_path == "bridge/foo-002.md"
    assert doc.versions[1].status == d.BridgeStatus.NEW
    assert result.errors == ()


def test_parser_handles_markdown_heading_preamble() -> None:
    d = _detector()
    text = "# Bridge Index\n## Subheading\n\nDocument: foo\nNEW: bridge/foo-001.md\n"
    result = d.parse_index(text)
    assert result.errors == ()
    assert len(result.documents) == 1


def test_parser_handles_singleline_html_comments() -> None:
    d = _detector()
    text = (
        "# Bridge Index\n"
        "<!-- Prime inserts new document entries at the top -->\n"
        "<!-- Statuses: NEW, REVISED, GO, NO-GO, VERIFIED, ADVISORY -->\n"
        "\n"
        "Document: foo\n"
        "NEW: bridge/foo-001.md\n"
    )
    result = d.parse_index(text)
    assert result.errors == ()
    assert len(result.documents) == 1


def test_parser_handles_advisory_status() -> None:
    d = _detector()
    text = "Document: advisory-thread\nADVISORY: bridge/advisory-thread-001.md\n"
    result = d.parse_index(text)
    assert result.errors == ()
    assert result.documents[0].versions[0].status == d.BridgeStatus.ADVISORY


def test_parser_handles_multiline_html_comment_blocks() -> None:
    d = _detector()
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
    result = d.parse_index(text)
    assert result.errors == ()
    assert len(result.documents) == 2
    assert {doc.name for doc in result.documents} == {"foo", "bar"}


def test_parser_handles_blank_line_separators() -> None:
    d = _detector()
    text = "Document: foo\nNEW: bridge/foo-001.md\n\n\nDocument: bar\nNEW: bridge/bar-001.md\n"
    result = d.parse_index(text)
    assert result.errors == ()
    assert len(result.documents) == 2


def test_parser_handles_crlf_line_endings() -> None:
    d = _detector()
    text = "Document: foo\r\nNEW: bridge/foo-001.md\r\n"
    result = d.parse_index(text)
    assert result.errors == ()
    assert len(result.documents) == 1


def test_parser_handles_utf8_bom() -> None:
    d = _detector()
    text = "﻿# Bridge Index\n\nDocument: foo\nNEW: bridge/foo-001.md\n"
    result = d.parse_index(text)
    assert result.errors == ()
    assert len(result.documents) == 1


def test_parser_validates_status_enum() -> None:
    d = _detector()
    text = "Document: foo\nBOGUS: bridge/foo-001.md\n"
    result = d.parse_index(text)
    assert len(result.errors) == 1
    assert result.errors[0].expected_state == "status_line"


def test_parser_recognizes_withdrawn_status() -> None:
    """WITHDRAWN at top of a document's version chain must be parsed correctly,
    parallel to VERIFIED's terminal recognition. Per WI-3276 / Layer-0 fix at
    gtkb-canonical-bridge-parser-withdrawn-status-handling.
    """
    d = _detector()
    text = (
        "Document: test-thread-withdrawn-fixture\n"
        "WITHDRAWN: bridge/test-thread-withdrawn-fixture-002.md\n"
        "NO-GO: bridge/test-thread-withdrawn-fixture-001.md\n"
    )
    result = d.parse_index(text)
    assert result.errors == ()
    assert len(result.documents) == 1
    doc = result.documents[0]
    assert doc.name == "test-thread-withdrawn-fixture"
    assert doc.current_top is not None
    assert doc.current_top.status == d.BridgeStatus.WITHDRAWN
    assert doc.current_top.file_path == "bridge/test-thread-withdrawn-fixture-002.md"
    assert len(doc.versions) == 2


def test_parser_validates_filename_matches_document_name() -> None:
    d = _detector()
    text = "Document: foo\nNEW: bridge/foo-001.md\nGO: bridge/baz-002.md\n"
    result = d.parse_index(text)
    assert len(result.documents) == 1
    assert len(result.documents[0].versions) == 2
    assert any(w.kind == "filename_does_not_match_document_name" for w in result.warnings)


def test_parser_returns_warning_not_error_for_missing_referenced_file(
    tmp_path: Path,
) -> None:
    d = _detector()
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "foo-002.md").write_text("")
    text = "Document: foo\nGO: bridge/foo-002.md\nNEW: bridge/foo-001.md\n"
    result = d.parse_index(text, project_root=tmp_path)
    assert result.errors == ()
    missing = [w for w in result.warnings if w.kind == "referenced_file_missing"]
    assert len(missing) == 1
    assert "foo-001" in missing[0].detail


def test_parser_returns_errors_continues_on_malformed_lines() -> None:
    d = _detector()
    text = "Document: foo\nNEW: bridge/foo-001.md\nthis is not a status line\nGO: bridge/foo-002.md\n"
    result = d.parse_index(text)
    assert len(result.documents) == 1
    assert len(result.documents[0].versions) == 2
    assert len(result.errors) == 1
    assert result.errors[0].line_number == 3


def test_parser_against_live_index_md() -> None:
    """Live INDEX regression: parses successfully against frozen snapshot."""
    d = _detector()
    fixture = Path(__file__).parent / "fixtures" / "bridge_index_live_snapshot.md"
    assert fixture.is_file(), f"Expected fixture at {fixture}"
    text = fixture.read_text(encoding="utf-8")
    result = d.parse_index(text)
    assert result.errors == ()
    assert len(result.documents) >= 30, f"Expected ≥30 documents in live INDEX snapshot, got {len(result.documents)}"
    for doc in result.documents:
        assert not doc.name.startswith("<!--")
        assert not doc.name.startswith("-->")


def test_current_top_file_missing_warning_kind(tmp_path: Path) -> None:
    """When the current top status file is missing, warning kind sharpens."""
    d = _detector()
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "foo-001.md").write_text("")
    text = "Document: foo\nGO: bridge/foo-002.md\nNEW: bridge/foo-001.md\n"
    result = d.parse_index(text, project_root=tmp_path)
    assert any(w.kind == "current_top_file_missing" for w in result.warnings)
