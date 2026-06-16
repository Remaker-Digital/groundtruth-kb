"""Tests for scripts/wrap_scan_consistency.py."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import wrap_scan_consistency as w2  # noqa: E402


def test_determine_exit_code_zero_when_only_warn() -> None:
    findings = [w2._finding("a", w2.SEVERITY_WARN, "w")]
    assert w2.determine_exit_code(findings) == w2.EXIT_OK


def test_determine_exit_code_two_when_any_error() -> None:
    findings = [
        w2._finding("a", w2.SEVERITY_WARN, "w"),
        w2._finding("b", w2.SEVERITY_ERROR, "e"),
    ]
    assert w2.determine_exit_code(findings) == w2.EXIT_ERROR


def test_check_bridge_numbered_files_have_status_flags_missing_token(tmp_path: Path) -> None:
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "real-001.md").write_text("NEW\n", encoding="utf-8")
    (bridge_dir / "missing-status-001.md").write_text("# Heading first\n", encoding="utf-8")

    findings = w2.check_bridge_numbered_files_have_status(tmp_path)

    missing = [f for f in findings if f["path"] == "bridge/missing-status-001.md"]
    assert len(missing) == 1
    assert missing[0]["check"] == "bridge_numbered_file_missing_status"
    assert missing[0]["severity"] == w2.SEVERITY_ERROR
    assert all(f.get("path") != "bridge/real-001.md" for f in findings)


def test_check_bridge_numbered_files_have_status_clean_when_all_status_bearing(tmp_path: Path) -> None:
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "real-001.md").write_text("NEW\n", encoding="utf-8")
    (bridge_dir / "real-002.md").write_text("GO\n", encoding="utf-8")

    assert w2.check_bridge_numbered_files_have_status(tmp_path) == []


def test_check_bridge_numbered_files_ignores_non_numbered_markdown(tmp_path: Path) -> None:
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "README.md").write_text("# Bridge notes\n", encoding="utf-8")

    assert w2.check_bridge_numbered_files_have_status(tmp_path) == []


def test_render_markdown_clean_state() -> None:
    output = w2.render_markdown([])
    assert "No findings" in output
    assert "intact" in output.lower()


def test_render_markdown_includes_severity_groups() -> None:
    findings = [
        w2._finding("a", w2.SEVERITY_ERROR, "missing status"),
        w2._finding("b", w2.SEVERITY_WARN, "missing ref"),
    ]
    output = w2.render_markdown(findings)
    assert "ERROR (1)" in output
    assert "WARN (1)" in output
