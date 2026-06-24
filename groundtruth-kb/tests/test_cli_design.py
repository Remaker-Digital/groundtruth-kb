"""CLI tests for `gt design import` (WI-3302).

Covers the cli.py wiring of the Claude Design manual-import slice: dry-run
inspection (the default, no MemBase mutation), JSON output, format-warning
surfacing, unsupported-path error handling, and explicit ``--apply`` semantics
against a temporary KnowledgeDB. The ``--apply`` path monkeypatches
``cli._open_db`` so the tracked MemBase is never mutated by the test run.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

from click.testing import CliRunner

import groundtruth_kb.cli as cli_mod
from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB


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


# ---------------------------------------------------------------------------
# Dry run (default) — no MemBase mutation
# ---------------------------------------------------------------------------


def test_dry_run_reports_inspection(tmp_path: Path) -> None:
    zip_path = tmp_path / "handoff.zip"
    _build_minimal_handoff_zip(zip_path)
    result = CliRunner().invoke(
        main,
        ["design", "import", str(zip_path), "--date", "2026-04-18", "--session-id", "S302"],
    )
    assert result.exit_code == 0, result.output
    assert "would_create" in result.output
    assert "claude-design-handoff:2026-04-18:" in result.output


def test_dry_run_json_output(tmp_path: Path) -> None:
    zip_path = tmp_path / "handoff.zip"
    _build_minimal_handoff_zip(zip_path)
    result = CliRunner().invoke(
        main,
        ["design", "import", str(zip_path), "--date", "2026-04-18", "--session-id", "S302", "--json"],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "would_create"
    assert payload["delib_id"] is None
    assert len(payload["content_hash"]) == 64
    assert payload["warnings"] == []


def test_dry_run_surfaces_format_warnings(tmp_path: Path) -> None:
    zip_path = tmp_path / "handoff.zip"
    _build_malformed_handoff_zip(zip_path)
    result = CliRunner().invoke(
        main,
        ["design", "import", str(zip_path), "--date", "2026-04-18", "--session-id", "S302", "--json"],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "would_create"
    assert any("README.md" in w for w in payload["warnings"])


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


def test_unsupported_path_errors(tmp_path: Path) -> None:
    bad = tmp_path / "not-a-handoff.txt"
    bad.write_text("nope", encoding="utf-8")
    result = CliRunner().invoke(
        main,
        ["design", "import", str(bad), "--date", "2026-04-18", "--session-id", "S302"],
    )
    # inspect_handoff raises ValueError → SystemExit(2)
    assert result.exit_code == 2, result.output
    assert "Error" in result.output


def test_missing_path_is_usage_error(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist.zip"
    result = CliRunner().invoke(
        main,
        ["design", "import", str(missing), "--date", "2026-04-18", "--session-id", "S302"],
    )
    # click.Path(exists=True) rejects before the command body runs.
    assert result.exit_code == 2, result.output


# ---------------------------------------------------------------------------
# Apply (against a temporary DB, idempotent)
# ---------------------------------------------------------------------------


def test_apply_creates_then_skips(tmp_path: Path, monkeypatch) -> None:
    db = KnowledgeDB(db_path=str(tmp_path / "ephemeral.db"))
    monkeypatch.setattr(cli_mod, "_open_db", lambda config, **kwargs: db)

    zip_path = tmp_path / "handoff.zip"
    _build_minimal_handoff_zip(zip_path)
    argv = [
        "design",
        "import",
        str(zip_path),
        "--date",
        "2026-04-18",
        "--session-id",
        "S302",
        "--apply",
        "--json",
    ]

    first = CliRunner().invoke(main, argv)
    assert first.exit_code == 0, first.output
    first_payload = json.loads(first.output)
    assert first_payload["action"] == "created"
    assert first_payload["delib_id"] is not None

    second = CliRunner().invoke(main, argv)
    assert second.exit_code == 0, second.output
    second_payload = json.loads(second.output)
    assert second_payload["action"] == "skipped"
    assert second_payload["content_hash"] == first_payload["content_hash"]
