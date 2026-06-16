"""Tests for the no-index bridge file writer.

The writer only creates status-bearing numbered bridge files. Dispatcher/TAFE
state and helper-level latest-status validation live above this module.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.gtkb_bridge_writer import BridgeConflictError, BridgeTransitionError, write_bridge_file

AUTHOR_METADATA = {
    "author_identity": "Codex",
    "author_harness_id": "A",
    "author_session_context_id": "session-123",
    "author_model": "GPT-5.5",
    "author_model_version": "5.5",
    "author_model_configuration": "Extra High",
}


def test_write_bridge_file_creates_numbered_file_with_metadata(tmp_path: Path) -> None:
    path = write_bridge_file("docthing", 1, "NEW\n\nhello\n", tmp_path, author_metadata=AUTHOR_METADATA)

    assert path == tmp_path / "bridge" / "docthing-001.md"
    assert path.read_text(encoding="utf-8") == (
        "NEW\n"
        "author_identity: Codex\n"
        "author_harness_id: A\n"
        "author_session_context_id: session-123\n"
        "author_model: GPT-5.5\n"
        "author_model_version: 5.5\n"
        "author_model_configuration: Extra High\n"
        "\nhello\n"
    )
    assert not (tmp_path / "bridge" / "INDEX.md").exists()


def test_write_bridge_file_rejects_existing_numbered_file(tmp_path: Path) -> None:
    target = tmp_path / "bridge" / "conflict-001.md"
    target.parent.mkdir()
    target.write_text("NEW\nexisting\n", encoding="utf-8")

    with pytest.raises(BridgeConflictError, match="already exists"):
        write_bridge_file("conflict", 1, "NEW\nnew body\n", tmp_path, require_author_metadata=False)

    assert target.read_text(encoding="utf-8") == "NEW\nexisting\n"


def test_write_bridge_file_rejects_non_positive_version(tmp_path: Path) -> None:
    with pytest.raises(BridgeTransitionError, match="version must be positive"):
        write_bridge_file("bad", 0, "NEW\n", tmp_path, require_author_metadata=False)


def test_write_bridge_file_can_skip_author_metadata_for_test_fixtures(tmp_path: Path) -> None:
    path = write_bridge_file("fixture", 2, "GO\n\nfixture body\n", tmp_path, require_author_metadata=False)

    assert path.read_text(encoding="utf-8") == "GO\n\nfixture body\n"
