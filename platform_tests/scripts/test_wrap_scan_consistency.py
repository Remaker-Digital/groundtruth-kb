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

    # Inject empty HEAD set: both files are "new" (not at HEAD), so missing-status is flagged
    findings = w2.check_bridge_numbered_files_have_status(tmp_path, head_resolver=lambda _: set())

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

    assert w2.check_bridge_numbered_files_have_status(tmp_path, head_resolver=lambda _: set()) == []


def test_check_bridge_numbered_files_ignores_non_numbered_markdown(tmp_path: Path) -> None:
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "README.md").write_text("# Bridge notes\n", encoding="utf-8")

    assert w2.check_bridge_numbered_files_have_status(tmp_path, head_resolver=lambda _: set()) == []


# ---------------------------------------------------------------------------
# Spec-derived tests for the grandfather exemption (GOV-FILE-BRIDGE-AUTHORITY-001)
# ---------------------------------------------------------------------------


def test_missing_status_historical_at_head_not_flagged(tmp_path: Path) -> None:
    """GOV-FILE-BRIDGE-AUTHORITY-001 grandfather clause: a file at HEAD without a
    status token is exempt and must NOT be flagged."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "old-001.md").write_text("# Old heading without status\n", encoding="utf-8")

    # Resolver declares this file is at HEAD → grandfather exemption applies
    findings = w2.check_bridge_numbered_files_have_status(tmp_path, head_resolver=lambda _: {"bridge/old-001.md"})

    assert not any(f.get("path") == "bridge/old-001.md" for f in findings)
    assert not any(f["severity"] == w2.SEVERITY_ERROR for f in findings)


def test_missing_status_new_file_flagged(tmp_path: Path) -> None:
    """GOV-FILE-BRIDGE-AUTHORITY-001: a new file (not at HEAD) without a status token
    MUST be flagged at SEVERITY_ERROR."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "new-001.md").write_text("# New heading without status\n", encoding="utf-8")

    # Empty HEAD set: the file is new, so missing status must be flagged
    findings = w2.check_bridge_numbered_files_have_status(tmp_path, head_resolver=lambda _: set())

    flagged = [f for f in findings if f.get("path") == "bridge/new-001.md"]
    assert len(flagged) == 1
    assert flagged[0]["check"] == "bridge_numbered_file_missing_status"
    assert flagged[0]["severity"] == w2.SEVERITY_ERROR


def test_valid_status_new_file_not_flagged(tmp_path: Path) -> None:
    """DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001: a new file that carries a
    valid status token must NOT be flagged, even though it is not at HEAD."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "new-with-status-001.md").write_text("GO\n\n# Content\n", encoding="utf-8")

    findings = w2.check_bridge_numbered_files_have_status(tmp_path, head_resolver=lambda _: set())

    assert not any(f.get("path") == "bridge/new-with-status-001.md" for f in findings)


def test_head_resolver_unavailable_grandfathers_all(tmp_path: Path) -> None:
    """GOV-SOURCE-OF-TRUTH-FRESHNESS-001 / fallback: when the HEAD resolver returns
    None, all files are grandfathered and a single INFO finding is emitted — no
    SEVERITY_ERROR findings."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "any-001.md").write_text("# No status token\n", encoding="utf-8")

    findings = w2.check_bridge_numbered_files_have_status(tmp_path, head_resolver=lambda _: None)

    # No file-level ERROR findings when the resolver is unavailable
    assert not any(f.get("path") == "bridge/any-001.md" for f in findings)
    assert not any(f["severity"] == w2.SEVERITY_ERROR for f in findings)
    # The unavailability INFO finding must be present
    info = [f for f in findings if f["check"] == "bridge_status_grandfather_unavailable"]
    assert len(info) == 1
    assert info[0]["severity"] == w2.SEVERITY_INFO


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
