"""W2 historical-phantom allowlist consultation.

Per WRAPUP -011 §2.1 + -012 GO conditions. Stage 1 ships the mechanism
with empty production baseline; Stage 2 follow-up bridge populates the
list with reviewed entries.

Tests cover four cases:
  1. Allowlist absent -> finding at error (current behavior preserved)
  2. Allowlist present + entry matches -> finding at info
  3. Allowlist present + entry doesn't match -> finding at error
  4. Malformed allowlist -> raise (don't silently default)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import wrap_scan_consistency as w2  # noqa: E402


def _make_repo(tmp_path: Path) -> Path:
    project = tmp_path / "fake_repo"
    project.mkdir()
    bridge_dir = project / "bridge"
    bridge_dir.mkdir()
    # INDEX cites a missing file
    index = bridge_dir / "INDEX.md"
    index.write_text(
        "# Bridge Index\n\n"
        "Document: phantom-thread\n"
        "VERIFIED: bridge/phantom-thread-006.md\n"
    )
    return project


def test_allowlist_absent_finding_at_error(tmp_path: Path) -> None:
    project = _make_repo(tmp_path)
    findings = w2.check_index_cites_missing_bridge_file(project)
    phantom = [f for f in findings if "phantom-thread-006.md" in f["message"]]
    assert len(phantom) == 1
    assert phantom[0]["severity"] == w2.SEVERITY_ERROR


def test_allowlist_matching_entry_demotes_to_info(tmp_path: Path) -> None:
    project = _make_repo(tmp_path)
    allowlist_dir = project / ".groundtruth" / "wrap-scan"
    allowlist_dir.mkdir(parents=True)
    (allowlist_dir / "historical-phantoms.toml").write_text(
        "schema_version = 1\n"
        "\n"
        "[[phantoms]]\n"
        'index_line_pattern = "VERIFIED: bridge/phantom-thread-006.md"\n'
        'reason = "Test fixture historical phantom"\n'
        'codex_review_bridge = "bridge/test-fixture-001.md"\n'
    )
    findings = w2.check_index_cites_missing_bridge_file(project)
    phantom = [f for f in findings if "phantom-thread-006.md" in f["message"]]
    assert len(phantom) == 1
    assert phantom[0]["severity"] == w2.SEVERITY_INFO
    assert phantom[0].get("allowlist_reason") == "Test fixture historical phantom"
    assert "allowlisted" in phantom[0]["message"].lower()


def test_allowlist_non_matching_entry_keeps_error(tmp_path: Path) -> None:
    project = _make_repo(tmp_path)
    allowlist_dir = project / ".groundtruth" / "wrap-scan"
    allowlist_dir.mkdir(parents=True)
    # Allowlist a DIFFERENT line than the one in INDEX
    (allowlist_dir / "historical-phantoms.toml").write_text(
        "schema_version = 1\n"
        "\n"
        "[[phantoms]]\n"
        'index_line_pattern = "VERIFIED: bridge/different-thread-005.md"\n'
        'reason = "Different phantom"\n'
        'codex_review_bridge = "bridge/other-001.md"\n'
    )
    findings = w2.check_index_cites_missing_bridge_file(project)
    phantom = [f for f in findings if "phantom-thread-006.md" in f["message"]]
    assert len(phantom) == 1
    assert phantom[0]["severity"] == w2.SEVERITY_ERROR


def test_allowlist_malformed_fails_loudly(tmp_path: Path) -> None:
    project = _make_repo(tmp_path)
    allowlist_dir = project / ".groundtruth" / "wrap-scan"
    allowlist_dir.mkdir(parents=True)
    (allowlist_dir / "historical-phantoms.toml").write_text(
        "this is not valid toml = {[}\n"
    )
    with pytest.raises(RuntimeError, match="malformed"):
        w2.check_index_cites_missing_bridge_file(project)


def test_allowlist_wrong_schema_version_fails_loudly(tmp_path: Path) -> None:
    project = _make_repo(tmp_path)
    allowlist_dir = project / ".groundtruth" / "wrap-scan"
    allowlist_dir.mkdir(parents=True)
    (allowlist_dir / "historical-phantoms.toml").write_text(
        "schema_version = 99\nphantoms = []\n"
    )
    with pytest.raises(RuntimeError, match="schema_version"):
        w2.check_index_cites_missing_bridge_file(project)


def test_allowlist_empty_phantoms_preserves_error_behavior(tmp_path: Path) -> None:
    """Empty phantoms array (the Stage 1 production state) preserves
    the canonical error-severity behavior."""
    project = _make_repo(tmp_path)
    allowlist_dir = project / ".groundtruth" / "wrap-scan"
    allowlist_dir.mkdir(parents=True)
    (allowlist_dir / "historical-phantoms.toml").write_text(
        "schema_version = 1\nphantoms = []\n"
    )
    findings = w2.check_index_cites_missing_bridge_file(project)
    phantom = [f for f in findings if "phantom-thread-006.md" in f["message"]]
    assert len(phantom) == 1
    assert phantom[0]["severity"] == w2.SEVERITY_ERROR
