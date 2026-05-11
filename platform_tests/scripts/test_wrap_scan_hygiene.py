"""Tests for scripts/wrap_scan_hygiene.py (W1 S5 hygiene scanner).

Per bridge/gtkb-wrapup-enhancements-slice1-005.md (REVISED-2, GO at -006).
Tests target the simple exit-code contract: warn-only exits 0; error exits 2.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import wrap_scan_hygiene as w1  # noqa: E402


def test_finding_constructor_includes_required_fields() -> None:
    f = w1._finding("test_check", w1.SEVERITY_WARN, "test message", path="some/path")
    assert f["check"] == "test_check"
    assert f["severity"] == w1.SEVERITY_WARN
    assert f["message"] == "test message"
    assert f["path"] == "some/path"


def test_determine_exit_code_zero_when_only_warn_findings() -> None:
    """Slice 1 simple contract: warn does not fail CI."""
    findings = [
        w1._finding("a", w1.SEVERITY_WARN, "w"),
        w1._finding("b", w1.SEVERITY_INFO, "i"),
    ]
    assert w1.determine_exit_code(findings) == w1.EXIT_OK


def test_determine_exit_code_two_when_any_error_finding() -> None:
    findings = [
        w1._finding("a", w1.SEVERITY_WARN, "w"),
        w1._finding("b", w1.SEVERITY_ERROR, "e"),
    ]
    assert w1.determine_exit_code(findings) == w1.EXIT_ERROR


def test_determine_exit_code_zero_when_no_findings() -> None:
    assert w1.determine_exit_code([]) == w1.EXIT_OK


def test_render_markdown_clean_state() -> None:
    output = w1.render_markdown([])
    assert "No findings" in output
    assert "clean" in output.lower()


def test_render_markdown_groups_by_severity() -> None:
    findings = [
        w1._finding("a", w1.SEVERITY_ERROR, "err msg"),
        w1._finding("b", w1.SEVERITY_WARN, "warn msg"),
    ]
    output = w1.render_markdown(findings)
    assert "ERROR (1)" in output
    assert "WARN (1)" in output
    assert "err msg" in output
    assert "warn msg" in output


def test_check_snapshots_non_manifest_flags_non_manifest_files(tmp_path: Path) -> None:
    """The defense-in-depth check for W0 manifest-only scope."""
    snap_dir = tmp_path / ".groundtruth" / "session" / "snapshots" / "S999"
    snap_dir.mkdir(parents=True)
    (snap_dir / "manifest.json").write_text("{}")
    (snap_dir / "transcript.jsonl").write_text("forbidden\n")  # this should be flagged
    findings = w1.check_snapshots_non_manifest(tmp_path)
    assert any("transcript.jsonl" in f["message"] for f in findings)
    assert all(f["severity"] == w1.SEVERITY_ERROR for f in findings)


def test_check_snapshots_non_manifest_clean_when_only_manifest(tmp_path: Path) -> None:
    snap_dir = tmp_path / ".groundtruth" / "session" / "snapshots" / "S999"
    snap_dir.mkdir(parents=True)
    (snap_dir / "manifest.json").write_text("{}")
    findings = w1.check_snapshots_non_manifest(tmp_path)
    assert findings == []


def test_check_snapshots_non_manifest_skips_when_dir_absent(tmp_path: Path) -> None:
    findings = w1.check_snapshots_non_manifest(tmp_path)
    assert findings == []


def test_check_pyc_without_source_clean_when_source_exists(tmp_path: Path) -> None:
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "mod.py").write_text("x = 1")
    cache = pkg / "__pycache__"
    cache.mkdir()
    (cache / "mod.cpython-314.pyc").write_bytes(b"\x00\x00\x00")
    findings = w1.check_pyc_without_source(tmp_path)
    assert findings == []


def test_check_pyc_without_source_flags_orphan(tmp_path: Path) -> None:
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    cache = pkg / "__pycache__"
    cache.mkdir()
    (cache / "ghost.cpython-314.pyc").write_bytes(b"\x00\x00\x00")
    findings = w1.check_pyc_without_source(tmp_path)
    assert any("ghost" in f["message"] for f in findings)
