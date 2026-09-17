"""Tests for groundtruth_kb.design_import (O-7 R21: local inspection without the archive pipeline).

Covers the package-level pipeline that backs ``gt design inspect``: inspection, SPEC-CD-HANDOFF-FORMAT-001
validation, deterministic content formatting, catalog redaction and the complete local report. The report is
computed and returned; the module stores nothing and opens no database.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from groundtruth_kb.design_import import (
    build_inspection_report,
    format_inspection_content,
    inspect_handoff,
    redact_inspection_content,
    validate_handoff_format,
)


def _build_minimal_handoff_zip(zip_path: Path) -> None:
    """Write a minimal D1-conformant handoff zip at ``zip_path``."""
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("ar-widget/README.md", "Claude Design handoff README.\n")
        zf.writestr(
            "ar-widget/project/index.html",
            "<!doctype html><html><body><div id='root'></div></body></html>",
        )
        zf.writestr("ar-widget/project/styles.css", ":root { --accent: #6366f1; }\n")
        zf.writestr("ar-widget/project/widget.jsx", "export const Widget = () => <div/>;\n")


def _build_malformed_handoff_zip(zip_path: Path) -> None:
    """Write a zip missing the D1 mandatory entries."""
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("random.txt", "nothing to see\n")


# ---------------------------------------------------------------------------
# Inspection
# ---------------------------------------------------------------------------


class TestInspectHandoff:
    def test_inspect_zip_lists_entries(self, tmp_path: Path) -> None:
        zip_path = tmp_path / "ar-widget-handoff.zip"
        _build_minimal_handoff_zip(zip_path)
        inspection = inspect_handoff(zip_path)
        assert inspection.source_kind == "zip"
        assert inspection.sha256 is not None and len(inspection.sha256) == 64
        assert len(inspection.entries) == 4
        assert inspection.total_bytes == sum(e.size_bytes for e in inspection.entries)
        assert {e.path for e in inspection.entries} == {
            "ar-widget/README.md",
            "ar-widget/project/index.html",
            "ar-widget/project/styles.css",
            "ar-widget/project/widget.jsx",
        }

    def test_inspect_directory_lists_entries(self, tmp_path: Path) -> None:
        handoff = tmp_path / "handoff"
        (handoff / "project").mkdir(parents=True)
        (handoff / "README.md").write_text("readme\n", encoding="utf-8")
        (handoff / "project" / "index.html").write_text("<html></html>", encoding="utf-8")
        inspection = inspect_handoff(handoff)
        assert inspection.source_kind == "directory"
        assert inspection.sha256 is None
        assert [e.path for e in inspection.entries] == ["README.md", "project/index.html"]

    def test_inspect_missing_path_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            inspect_handoff(tmp_path / "missing.zip")

    def test_inspect_unsupported_file_raises(self, tmp_path: Path) -> None:
        bad = tmp_path / "handoff.txt"
        bad.write_text("nope", encoding="utf-8")
        with pytest.raises(ValueError, match="must be a .zip file or a directory"):
            inspect_handoff(bad)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


class TestValidateHandoffFormat:
    def test_conformant_handoff_has_no_warnings(self, tmp_path: Path) -> None:
        zip_path = tmp_path / "handoff.zip"
        _build_minimal_handoff_zip(zip_path)
        assert validate_handoff_format(inspect_handoff(zip_path)) == []

    def test_malformed_handoff_warns_on_missing_files(self, tmp_path: Path) -> None:
        zip_path = tmp_path / "handoff.zip"
        _build_malformed_handoff_zip(zip_path)
        warnings = validate_handoff_format(inspect_handoff(zip_path))
        assert len(warnings) == 4
        assert any("README.md" in w for w in warnings)
        assert any("project/index.html" in w for w in warnings)
        assert any(".css" in w for w in warnings)
        assert any("jsx" in w for w in warnings)


# ---------------------------------------------------------------------------
# Content formatting
# ---------------------------------------------------------------------------


class TestFormatInspectionContent:
    def test_content_is_deterministic(self, tmp_path: Path) -> None:
        zip_path = tmp_path / "handoff.zip"
        _build_minimal_handoff_zip(zip_path)
        inspection = inspect_handoff(zip_path)
        warnings = validate_handoff_format(inspection)
        kwargs = dict(
            inspection=inspection,
            date="2026-04-18",
            session_id="S302",
            owner_decision="token-only-candidate",
            notes=None,
            warnings=warnings,
        )
        assert format_inspection_content(**kwargs) == format_inspection_content(**kwargs)

    def test_content_mentions_date_and_session(self, tmp_path: Path) -> None:
        zip_path = tmp_path / "handoff.zip"
        _build_minimal_handoff_zip(zip_path)
        inspection = inspect_handoff(zip_path)
        content = format_inspection_content(
            inspection=inspection,
            date="2026-04-18",
            session_id="S302",
            owner_decision=None,
            notes=None,
            warnings=[],
        )
        assert "Handoff date: 2026-04-18" in content
        assert "Session: S302" in content
        assert "OK — all D1 mandatory files present." in content

    def test_content_omits_session_when_none_is_supplied(self, tmp_path: Path) -> None:
        zip_path = tmp_path / "handoff.zip"
        _build_minimal_handoff_zip(zip_path)
        content = format_inspection_content(
            inspection=inspect_handoff(zip_path),
            date="2026-04-18",
            session_id=None,
            owner_decision=None,
            notes="looked at the tokens",
            warnings=[],
        )
        assert "Session:" not in content
        assert "## Inspection notes\nlooked at the tokens" in content

    def test_content_mentions_warnings_when_present(self, tmp_path: Path) -> None:
        zip_path = tmp_path / "handoff.zip"
        _build_malformed_handoff_zip(zip_path)
        inspection = inspect_handoff(zip_path)
        warnings = validate_handoff_format(inspection)
        content = format_inspection_content(
            inspection=inspection,
            date="2026-04-18",
            session_id="S302",
            owner_decision=None,
            notes=None,
            warnings=warnings,
        )
        assert "WARNINGS" in content
        assert any(w in content for w in warnings)


# ---------------------------------------------------------------------------
# The complete local report
# ---------------------------------------------------------------------------


class TestInspectionReport:
    def test_report_hash_is_deterministic(self, tmp_path: Path) -> None:
        zip_path = tmp_path / "handoff.zip"
        _build_minimal_handoff_zip(zip_path)
        first = build_inspection_report(zip_path, date="2026-04-18", session_id="S302", owner_decision="first run")
        second = build_inspection_report(zip_path, date="2026-04-18", session_id="S302", owner_decision="first run")
        assert first == second
        assert len(first.content_hash) == 64
        assert first.warnings == () and first.redaction_notes is None
        assert first.to_json_dict()["file_count"] == 4

    def test_report_redacts_credentials_from_the_catalog(self, tmp_path: Path) -> None:
        zip_path = tmp_path / "handoff.zip"
        _build_minimal_handoff_zip(zip_path)
        report = build_inspection_report(zip_path, date="2026-04-18", notes="uses key AKIAABCDEFGHIJKLMNOP")
        assert "AKIAABCDEFGHIJKLMNOP" not in report.content
        assert "[REDACTED:aws_key]" in report.content
        assert report.redaction_notes == "aws_key: 1 occurrence(s)"
        assert redact_inspection_content("nothing sensitive") == ("nothing sensitive", None)

    def test_report_reads_no_database(self, tmp_path: Path) -> None:
        zip_path = tmp_path / "handoff.zip"
        _build_minimal_handoff_zip(zip_path)
        before = set(tmp_path.iterdir())
        report = build_inspection_report(zip_path, date="2026-04-18")
        assert set(tmp_path.iterdir()) == before
        assert set(report.to_json_dict()) == {
            "source_path",
            "source_kind",
            "sha256",
            "total_bytes",
            "file_count",
            "entries",
            "warnings",
            "content",
            "content_hash",
            "redaction_notes",
        }
