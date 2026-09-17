"""CLI tests for ``gt design inspect`` (O-7 R21: retain the local handoff inspection; retire the DELIB publication).

Carries the retained duties of the ``gt design import`` cases: a local .zip or directory handoff is inspected (file
list, sizes, archive sha256, D1 format warnings) as text or JSON, warnings are surfaced without failing the command,
a path that is neither a .zip file nor a directory is refused, and a missing path is a usage error. The retired duty
is not reasserted: the command publishes nothing, opens no database and reports no archive action.
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

from click.testing import CliRunner

from groundtruth_kb.cli import main

DATE = ["--date", "2026-04-18"]


def _build_minimal_handoff_zip(zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("ar-widget/README.md", "Claude Design handoff README.\n")
        zf.writestr(
            "ar-widget/project/index.html",
            "<!doctype html><html><body><div id='root'></div></body></html>",
        )
        zf.writestr("ar-widget/project/styles.css", ":root { --accent: #6366f1; }\n")
        zf.writestr("ar-widget/project/widget.jsx", "export const Widget = () => <div/>;\n")


def _build_malformed_handoff_zip(zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("random.txt", "nothing to see\n")


def test_inspect_reports_file_list_and_conformance(tmp_path: Path) -> None:
    zip_path = tmp_path / "handoff.zip"
    _build_minimal_handoff_zip(zip_path)
    result = CliRunner().invoke(main, ["design", "inspect", str(zip_path), *DATE, "--session-id", "S302"])
    assert result.exit_code == 0, result.output
    assert result.output.startswith("# Claude Design Handoff Inspection")
    assert "Handoff date: 2026-04-18" in result.output
    assert "Session: S302" in result.output
    assert "- ar-widget/project/index.html (" in result.output
    assert "OK — all D1 mandatory files present." in result.output


def test_inspect_json_output(tmp_path: Path) -> None:
    zip_path = tmp_path / "handoff.zip"
    _build_minimal_handoff_zip(zip_path)
    result = CliRunner().invoke(main, ["design", "inspect", str(zip_path), *DATE, "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["source_kind"] == "zip"
    assert len(payload["sha256"]) == 64
    assert payload["file_count"] == 4 and len(payload["entries"]) == 4
    assert payload["warnings"] == []
    assert len(payload["content_hash"]) == 64
    assert payload["redaction_notes"] is None
    assert "action" not in payload and "delib_id" not in payload and "source_ref" not in payload


def test_inspect_surfaces_format_warnings(tmp_path: Path) -> None:
    zip_path = tmp_path / "handoff.zip"
    _build_malformed_handoff_zip(zip_path)
    result = CliRunner().invoke(main, ["design", "inspect", str(zip_path), *DATE, "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert any("README.md" in w for w in payload["warnings"])
    assert "WARNINGS:" in payload["content"]


def test_inspect_directory_handoff(tmp_path: Path) -> None:
    handoff = tmp_path / "ar-widget"
    (handoff / "project").mkdir(parents=True)
    (handoff / "README.md").write_text("Claude Design handoff README.\n", encoding="utf-8")
    (handoff / "project" / "index.html").write_text("<!doctype html>", encoding="utf-8")
    (handoff / "project" / "styles.css").write_text(":root {}\n", encoding="utf-8")
    (handoff / "project" / "widget.tsx").write_text("export const Widget = () => null;\n", encoding="utf-8")
    result = CliRunner().invoke(main, ["design", "inspect", str(handoff), *DATE, "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["source_kind"] == "directory" and payload["sha256"] is None
    assert [e["path"] for e in payload["entries"]] == [
        "README.md",
        "project/index.html",
        "project/styles.css",
        "project/widget.tsx",
    ]
    assert payload["warnings"] == []


def test_unsupported_path_is_refused(tmp_path: Path) -> None:
    bad = tmp_path / "not-a-handoff.txt"
    bad.write_text("nope", encoding="utf-8")
    result = CliRunner().invoke(main, ["design", "inspect", str(bad), *DATE])
    assert result.exit_code == 2, result.output
    assert "Error" in result.output and "must be a .zip file or a directory" in result.output


def test_missing_path_is_usage_error(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist.zip"
    result = CliRunner().invoke(main, ["design", "inspect", str(missing), *DATE])
    assert result.exit_code == 2, result.output
    assert "does not exist" in result.output


def test_inspect_publishes_nothing(tmp_path: Path) -> None:
    zip_path = tmp_path / "handoff.zip"
    _build_minimal_handoff_zip(zip_path)
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path) as workdir:
        first = runner.invoke(main, ["design", "inspect", str(zip_path), *DATE, "--json"])
        second = runner.invoke(main, ["design", "inspect", str(zip_path), *DATE, "--json"])
        assert first.exit_code == 0 and second.exit_code == 0, first.output + second.output
        assert list(Path(workdir).iterdir()) == []
    assert json.loads(first.output)["content_hash"] == json.loads(second.output)["content_hash"]
    assert not (tmp_path / "groundtruth.db").exists()
    from groundtruth_kb import design_import

    source = Path(design_import.__file__).read_text(encoding="utf-8")
    for forbidden in ("KnowledgeDB", "sqlite3", "upsert_deliberation", "current_deliberations", "_load_kb"):
        assert forbidden not in source, forbidden
