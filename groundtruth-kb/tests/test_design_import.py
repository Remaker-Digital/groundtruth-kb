"""Tests for groundtruth_kb.design_import (WI-3302).

Covers the package-level handoff pipeline that backs ``gt design import``:
inspection, SPEC-CD-HANDOFF-FORMAT-001 validation, deterministic content
formatting, dry-run semantics, content-hash idempotence, and the
parameterized DA attribution. The end-to-end ``--apply`` path runs against a
temporary KnowledgeDB so the tracked MemBase is never mutated.

These tests exercise the package module directly; the script-level regression
test (platform_tests/scripts/test_archive_claude_design_handoff.py) continues
to exercise the same contract through the compatibility wrapper.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.design_import import (
    archive,
    format_inspection_content,
    inspect_handoff,
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
        paths = {e.path for e in inspection.entries}
        assert "ar-widget/README.md" in paths
        assert "ar-widget/project/index.html" in paths
        assert inspection.sha256 is not None

    def test_inspect_directory_lists_entries(self, tmp_path: Path) -> None:
        (tmp_path / "ar-widget" / "project").mkdir(parents=True)
        (tmp_path / "ar-widget" / "README.md").write_text("hi\n", encoding="utf-8")
        (tmp_path / "ar-widget" / "project" / "index.html").write_text("<!doctype html>", encoding="utf-8")
        (tmp_path / "ar-widget" / "project" / "styles.css").write_text(":root {}", encoding="utf-8")
        (tmp_path / "ar-widget" / "project" / "app.jsx").write_text("export {}", encoding="utf-8")
        inspection = inspect_handoff(tmp_path / "ar-widget")
        assert inspection.source_kind == "directory"
        assert inspection.sha256 is None
        assert len(inspection.entries) == 4

    def test_inspect_missing_path_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            inspect_handoff(tmp_path / "no-such-thing.zip")

    def test_inspect_unsupported_file_raises(self, tmp_path: Path) -> None:
        p = tmp_path / "not-a-zip.txt"
        p.write_text("nope", encoding="utf-8")
        with pytest.raises(ValueError):
            inspect_handoff(p)


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
        assert any("README.md" in w for w in warnings)
        assert any("project/index.html" in w for w in warnings)


# ---------------------------------------------------------------------------
# Content formatting (hash stability)
# ---------------------------------------------------------------------------


class TestFormatInspectionContent:
    def test_content_is_deterministic(self, tmp_path: Path) -> None:
        zip_path = tmp_path / "handoff.zip"
        _build_minimal_handoff_zip(zip_path)
        inspection = inspect_handoff(zip_path)
        kwargs = dict(
            inspection=inspection,
            date="2026-04-18",
            session_id="S302",
            owner_decision="token-only + net-new",
            notes=None,
            warnings=(),
        )
        assert format_inspection_content(**kwargs) == format_inspection_content(**kwargs)

    def test_content_mentions_date_and_session(self, tmp_path: Path) -> None:
        zip_path = tmp_path / "handoff.zip"
        _build_minimal_handoff_zip(zip_path)
        content = format_inspection_content(
            inspection=inspect_handoff(zip_path),
            date="2026-04-18",
            session_id="S302",
            owner_decision=None,
            notes=None,
            warnings=(),
        )
        assert "2026-04-18" in content
        assert "S302" in content

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
# Archive pipeline
# ---------------------------------------------------------------------------


class TestArchiveDryRun:
    def test_dry_run_returns_would_create(self, tmp_path: Path) -> None:
        zip_path = tmp_path / "handoff.zip"
        _build_minimal_handoff_zip(zip_path)
        result = archive(
            handoff_path=zip_path,
            date="2026-04-18",
            session_id="S302",
            owner_decision="dry run test",
            apply=False,
        )
        assert result.action == "would_create"
        assert result.delib_id is None
        assert result.source_ref.startswith("claude-design-handoff:2026-04-18:")
        assert len(result.content_hash) == 64

    def test_dry_run_does_not_require_db(self, tmp_path: Path) -> None:
        # A dry run must never construct or touch a database; passing no db and
        # apply=False must succeed even though _load_kb would fail in a bare env.
        zip_path = tmp_path / "handoff.zip"
        _build_minimal_handoff_zip(zip_path)
        result = archive(handoff_path=zip_path, date="2026-04-18", session_id="S302", apply=False)
        assert result.action == "would_create"


class TestArchiveApply:
    def test_second_apply_is_skipped(self, tmp_path: Path) -> None:
        db = KnowledgeDB(db_path=str(tmp_path / "ephemeral.db"))
        zip_path = tmp_path / "handoff.zip"
        _build_minimal_handoff_zip(zip_path)

        first = archive(
            handoff_path=zip_path,
            date="2026-04-18",
            session_id="S302",
            owner_decision="first run",
            apply=True,
            db=db,
        )
        assert first.action == "created"
        assert first.delib_id is not None

        second = archive(
            handoff_path=zip_path,
            date="2026-04-18",
            session_id="S302",
            owner_decision="first run",  # identical inputs → identical content_hash
            apply=True,
            db=db,
        )
        assert second.action == "skipped"
        assert second.content_hash == first.content_hash
        assert second.delib_id == first.delib_id

    def test_changed_by_attribution_is_recorded(self, tmp_path: Path) -> None:
        db = KnowledgeDB(db_path=str(tmp_path / "ephemeral.db"))
        zip_path = tmp_path / "handoff.zip"
        _build_minimal_handoff_zip(zip_path)

        result = archive(
            handoff_path=zip_path,
            date="2026-04-18",
            session_id="S302",
            apply=True,
            db=db,
            changed_by="gt design import",
        )
        assert result.action == "created"
        row = (
            db._get_conn()
            .execute(
                "SELECT changed_by FROM current_deliberations WHERE source_ref = ?",
                (result.source_ref,),
            )
            .fetchone()
        )
        assert row is not None
        assert row[0] == "gt design import"
