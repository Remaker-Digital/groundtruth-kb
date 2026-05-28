"""Unit tests for scripts/archive_claude_design_handoff.py (D7).

Tests cover the pure pipeline functions (inspection, validation, content
formatting) without requiring KB writes. One end-to-end test exercises the
``--apply`` path against a temporary in-memory KB to verify content-hash
idempotence.

The D7 bridge's binding condition #5 says "DA script reuses the existing
redaction/idempotence patterns". These tests lock in that contract.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib.util
import sys
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "archive_claude_design_handoff.py"


def _load_archive_module():
    """Load the script as a module without triggering argparse."""
    spec = importlib.util.spec_from_file_location(
        "archive_claude_design_handoff",
        SCRIPT_PATH,
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["archive_claude_design_handoff"] = module
    spec.loader.exec_module(module)
    return module


def _build_minimal_handoff_zip(zip_path: Path) -> None:
    """Write a minimal D1-conformant handoff zip at ``zip_path``."""
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("ar-widget/README.md", "Claude Design handoff README.\n")
        zf.writestr(
            "ar-widget/project/index.html",
            "<!doctype html><html><body><div id='root'></div></body></html>",
        )
        zf.writestr(
            "ar-widget/project/styles.css",
            ":root { --accent: #6366f1; }\n",
        )
        zf.writestr(
            "ar-widget/project/widget.jsx",
            "export const Widget = () => <div/>;\n",
        )


def _build_malformed_handoff_zip(zip_path: Path) -> None:
    """Write a zip missing the D1 mandatory entries."""
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("random.txt", "nothing to see\n")


# ---------------------------------------------------------------------------
# Inspection + format validation
# ---------------------------------------------------------------------------


class TestInspectHandoff:
    def test_inspect_zip_lists_entries(self, tmp_path: Path) -> None:
        mod = _load_archive_module()
        zip_path = tmp_path / "ar-widget-handoff.zip"
        _build_minimal_handoff_zip(zip_path)
        inspection = mod.inspect_handoff(zip_path)
        assert inspection.source_kind == "zip"
        paths = {e.path for e in inspection.entries}
        assert "ar-widget/README.md" in paths
        assert "ar-widget/project/index.html" in paths
        assert inspection.sha256 is not None

    def test_inspect_directory_lists_entries(self, tmp_path: Path) -> None:
        mod = _load_archive_module()
        (tmp_path / "ar-widget").mkdir()
        (tmp_path / "ar-widget" / "README.md").write_text("hi\n", encoding="utf-8")
        (tmp_path / "ar-widget" / "project").mkdir()
        (tmp_path / "ar-widget" / "project" / "index.html").write_text(
            "<!doctype html>",
            encoding="utf-8",
        )
        (tmp_path / "ar-widget" / "project" / "styles.css").write_text(
            ":root {}",
            encoding="utf-8",
        )
        (tmp_path / "ar-widget" / "project" / "app.jsx").write_text(
            "export {}",
            encoding="utf-8",
        )
        inspection = mod.inspect_handoff(tmp_path)
        assert inspection.source_kind == "directory"
        assert inspection.sha256 is None
        assert len(inspection.entries) == 4

    def test_inspect_missing_path_raises(self, tmp_path: Path) -> None:
        mod = _load_archive_module()
        with pytest.raises(FileNotFoundError):
            mod.inspect_handoff(tmp_path / "no-such-thing.zip")

    def test_inspect_unsupported_file_raises(self, tmp_path: Path) -> None:
        mod = _load_archive_module()
        p = tmp_path / "not-a-zip.txt"
        p.write_text("nope", encoding="utf-8")
        with pytest.raises(ValueError):
            mod.inspect_handoff(p)


class TestValidateHandoffFormat:
    def test_conformant_handoff_has_no_warnings(self, tmp_path: Path) -> None:
        mod = _load_archive_module()
        zip_path = tmp_path / "handoff.zip"
        _build_minimal_handoff_zip(zip_path)
        warnings = mod.validate_handoff_format(mod.inspect_handoff(zip_path))
        assert warnings == []

    def test_malformed_handoff_warns_on_missing_files(self, tmp_path: Path) -> None:
        mod = _load_archive_module()
        zip_path = tmp_path / "handoff.zip"
        _build_malformed_handoff_zip(zip_path)
        warnings = mod.validate_handoff_format(mod.inspect_handoff(zip_path))
        assert any("README.md" in w for w in warnings)
        assert any("project/index.html" in w for w in warnings)


# ---------------------------------------------------------------------------
# Content formatting (hash stability)
# ---------------------------------------------------------------------------


class TestFormatInspectionContent:
    def test_content_is_deterministic(self, tmp_path: Path) -> None:
        mod = _load_archive_module()
        zip_path = tmp_path / "handoff.zip"
        _build_minimal_handoff_zip(zip_path)
        inspection = mod.inspect_handoff(zip_path)
        kwargs = dict(
            inspection=inspection,
            date="2026-04-18",
            session_id="S302",
            owner_decision="token-only + net-new",
            notes=None,
            warnings=(),
        )
        content1 = mod.format_inspection_content(**kwargs)
        content2 = mod.format_inspection_content(**kwargs)
        assert content1 == content2

    def test_content_mentions_date_and_session(self, tmp_path: Path) -> None:
        mod = _load_archive_module()
        zip_path = tmp_path / "handoff.zip"
        _build_minimal_handoff_zip(zip_path)
        content = mod.format_inspection_content(
            inspection=mod.inspect_handoff(zip_path),
            date="2026-04-18",
            session_id="S302",
            owner_decision=None,
            notes=None,
            warnings=(),
        )
        assert "2026-04-18" in content
        assert "S302" in content

    def test_content_mentions_warnings_when_present(self, tmp_path: Path) -> None:
        mod = _load_archive_module()
        zip_path = tmp_path / "handoff.zip"
        _build_malformed_handoff_zip(zip_path)
        inspection = mod.inspect_handoff(zip_path)
        warnings = mod.validate_handoff_format(inspection)
        content = mod.format_inspection_content(
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
# Archive pipeline (dry-run)
# ---------------------------------------------------------------------------


class TestArchiveDryRun:
    def test_dry_run_returns_would_create(self, tmp_path: Path) -> None:
        mod = _load_archive_module()
        zip_path = tmp_path / "handoff.zip"
        _build_minimal_handoff_zip(zip_path)
        result = mod.archive(
            handoff_path=zip_path,
            date="2026-04-18",
            session_id="S302",
            owner_decision="dry run test",
            apply=False,
        )
        assert result.action == "would_create"
        assert result.delib_id is None
        assert result.source_ref.startswith("claude-design-handoff:2026-04-18:")
        # sha256 hex length
        assert len(result.content_hash) == 64


# ---------------------------------------------------------------------------
# Content-hash idempotence (end-to-end with the real KB)
#
# The repo's groundtruth.db is shared state. To avoid mutating it during a
# test run, we point KnowledgeDB at a temporary DB populated only with the
# schema. This proves the idempotence contract end-to-end without affecting
# the tracked DB.
# ---------------------------------------------------------------------------


class TestArchiveIdempotence:
    def _bootstrap_temp_db(self, tmp_path: Path):
        sys.path.insert(0, str(REPO_ROOT / "tools" / "knowledge-db"))
        from db import KnowledgeDB  # noqa: PLC0415 — path must be set first
        from groundtruth_kb.db import SCHEMA_SQL  # noqa: PLC0415

        db_path = tmp_path / "ephemeral.db"
        # Pre-create the schema in the target file so KnowledgeDB can open it.
        import sqlite3  # noqa: PLC0415

        con = sqlite3.connect(db_path)
        con.executescript(SCHEMA_SQL)
        con.commit()
        con.close()
        return KnowledgeDB(db_path=str(db_path))

    def test_second_apply_is_skipped(self, tmp_path: Path) -> None:
        mod = _load_archive_module()
        db = self._bootstrap_temp_db(tmp_path)

        zip_path = tmp_path / "handoff.zip"
        _build_minimal_handoff_zip(zip_path)

        first = mod.archive(
            handoff_path=zip_path,
            date="2026-04-18",
            session_id="S302",
            owner_decision="first run",
            apply=True,
            db=db,
        )
        assert first.action == "created"
        assert first.delib_id is not None

        second = mod.archive(
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
