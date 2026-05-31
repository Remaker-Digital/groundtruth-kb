"""Tests for scripts/wrap_scan_consistency.py (W2 S2 consistency scanner).

Per bridge/gtkb-wrapup-enhancements-slice1-005.md (REVISED-2, GO at -006).
Tests target the phantom-INDEX-citation detection — the canonical S308 class.
"""

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


def test_check_index_cites_missing_bridge_file_phantom_detected(tmp_path: Path) -> None:
    """Canonical S308 class: INDEX claims VERIFIED but file doesn't exist."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "real-001.md").write_text("NEW")
    (bridge_dir / "phantom-thread-001.md").write_text("NEW")  # -001 exists; -006 is the phantom
    index = bridge_dir / "INDEX.md"
    index.write_text(
        "# Bridge Index\n\n"
        "Document: phantom-thread\n"
        "VERIFIED: bridge/phantom-thread-006.md\n"
        "NEW: bridge/phantom-thread-001.md\n\n"
        "Document: real\n"
        "NEW: bridge/real-001.md\n"
    )
    findings = w2.check_index_cites_missing_bridge_file(tmp_path)
    phantom_findings = [f for f in findings if "phantom-thread-006.md" in f["message"]]
    assert len(phantom_findings) == 1
    assert phantom_findings[0]["severity"] == w2.SEVERITY_ERROR
    assert phantom_findings[0]["status"] == "VERIFIED"
    one_findings = [f for f in findings if "phantom-thread-001.md" in f["message"]]
    assert one_findings == []


def test_check_index_cites_missing_bridge_file_clean_when_all_exist(tmp_path: Path) -> None:
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "real-001.md").write_text("NEW")
    (bridge_dir / "real-002.md").write_text("GO")
    index = bridge_dir / "INDEX.md"
    index.write_text("Document: real\nGO: bridge/real-002.md\nNEW: bridge/real-001.md\n")
    findings = w2.check_index_cites_missing_bridge_file(tmp_path)
    assert findings == []


def test_check_bridge_file_orphaned_from_index(tmp_path: Path) -> None:
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "tracked-001.md").write_text("NEW")
    (bridge_dir / "orphan-001.md").write_text("dangling")
    index = bridge_dir / "INDEX.md"
    index.write_text("Document: tracked\nNEW: bridge/tracked-001.md\n")
    findings = w2.check_bridge_file_orphaned_from_index(tmp_path)
    orphan_findings = [f for f in findings if "orphan-001.md" in f["message"]]
    assert len(orphan_findings) == 1
    assert orphan_findings[0]["severity"] == w2.SEVERITY_WARN


def test_render_markdown_clean_state() -> None:
    output = w2.render_markdown([])
    assert "No findings" in output
    assert "intact" in output.lower()


def test_render_markdown_includes_severity_groups() -> None:
    findings = [
        w2._finding("a", w2.SEVERITY_ERROR, "phantom"),
        w2._finding("b", w2.SEVERITY_WARN, "orphan"),
    ]
    output = w2.render_markdown(findings)
    assert "ERROR (1)" in output
    assert "WARN (1)" in output
