# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for groundtruth_kb.bridge.checkpoint.

Per ``bridge/gtkb-bridge-poller-p1-detector-003.md`` sections 3.4, 3.7 and
4.1, these tests cover bootstrap mode (zero transitions on first install),
corrupt-checkpoint recovery, write-then-load round trip, and diff behavior
after a real checkpoint is established.
"""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.bridge.checkpoint import (
    CHECKPOINT_FILENAME,
    diff_against_checkpoint,
    load_checkpoint,
    write_checkpoint,
)
from groundtruth_kb.bridge.detector import parse_index


def _fixture_index() -> str:
    return "Document: foo\nGO: bridge/foo-002.md\nNEW: bridge/foo-001.md\n\nDocument: bar\nNEW: bridge/bar-001.md\n"


def test_load_checkpoint_returns_bootstrap_when_no_file(tmp_path: Path) -> None:
    result = load_checkpoint(tmp_path)
    assert result.is_bootstrap is True
    assert result.corrupt_checkpoint_recovered is False
    assert result.checkpoint is None


def test_diff_in_bootstrap_mode_emits_zero_transitions_against_live_shape() -> None:
    parsed = parse_index(_fixture_index())
    transitions = diff_against_checkpoint(parsed.documents, checkpoint=None, is_bootstrap=True)
    assert transitions == ()


def test_diff_in_bootstrap_mode_writes_baseline_checkpoint(tmp_path: Path) -> None:
    parsed = parse_index(_fixture_index())
    write_checkpoint(tmp_path, parsed.documents)
    cp_file = tmp_path / CHECKPOINT_FILENAME
    assert cp_file.is_file()

    loaded = load_checkpoint(tmp_path)
    assert loaded.is_bootstrap is False
    assert loaded.checkpoint is not None
    assert {e.document_name for e in loaded.checkpoint.documents} == {"foo", "bar"}


def test_diff_after_bootstrap_emits_only_actual_changes(tmp_path: Path) -> None:
    initial = parse_index(_fixture_index())
    write_checkpoint(tmp_path, initial.documents)

    # Same content again → zero transitions
    parsed_same = parse_index(_fixture_index())
    loaded = load_checkpoint(tmp_path)
    assert loaded.checkpoint is not None
    transitions_same = diff_against_checkpoint(parsed_same.documents, loaded.checkpoint, is_bootstrap=False)
    assert transitions_same == ()

    # Now bar changes status from NEW to GO → one transition
    changed = (
        "Document: foo\n"
        "GO: bridge/foo-002.md\n"
        "NEW: bridge/foo-001.md\n"
        "\n"
        "Document: bar\n"
        "GO: bridge/bar-002.md\n"
        "NEW: bridge/bar-001.md\n"
    )
    parsed_changed = parse_index(changed)
    transitions_changed = diff_against_checkpoint(parsed_changed.documents, loaded.checkpoint, is_bootstrap=False)
    assert len(transitions_changed) == 1
    t = transitions_changed[0]
    assert t.document_name == "bar"
    assert t.from_status == "NEW"
    assert t.from_file == "bridge/bar-001.md"
    assert t.to_status == "GO"
    assert t.to_file == "bridge/bar-002.md"


def test_diff_emits_transition_for_new_document(tmp_path: Path) -> None:
    initial = parse_index(_fixture_index())
    write_checkpoint(tmp_path, initial.documents)
    loaded = load_checkpoint(tmp_path)
    assert loaded.checkpoint is not None

    with_new_doc = _fixture_index() + ("\nDocument: baz\nNEW: bridge/baz-001.md\n")
    parsed_new = parse_index(with_new_doc)
    transitions = diff_against_checkpoint(parsed_new.documents, loaded.checkpoint, is_bootstrap=False)
    assert len(transitions) == 1
    t = transitions[0]
    assert t.document_name == "baz"
    assert t.from_status is None
    assert t.from_file is None
    assert t.to_status == "NEW"


def test_corrupt_checkpoint_treated_as_bootstrap_with_warning(tmp_path: Path) -> None:
    cp_file = tmp_path / CHECKPOINT_FILENAME
    cp_file.write_text("{not valid json", encoding="utf-8")
    result = load_checkpoint(tmp_path)
    assert result.is_bootstrap is True
    assert result.corrupt_checkpoint_recovered is True
    assert result.checkpoint is None
    assert "parse error" in result.detail.lower()


def test_unknown_schema_version_treated_as_bootstrap_with_warning(tmp_path: Path) -> None:
    cp_file = tmp_path / CHECKPOINT_FILENAME
    cp_file.write_text(
        '{"schema_version": 999, "captured_at": "2026-04-28T00:00:00+00:00", "documents": []}',
        encoding="utf-8",
    )
    result = load_checkpoint(tmp_path)
    assert result.is_bootstrap is True
    assert result.corrupt_checkpoint_recovered is True
    assert "999" in result.detail
