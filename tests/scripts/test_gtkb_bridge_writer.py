"""Tests for scripts.gtkb_bridge_writer (GTKB-ISOLATION-015 Slice 1 §B).

Covers:
- stale index rejection
- next_file_number correctness with gap in version sequence
- Prime NEW on new document -> accepted
- Prime NEW after GO -> accepted (post-impl report)
- Prime NEW after NO-GO / REVISED / VERIFIED -> REJECTED
- Prime REVISED after NO-GO -> accepted
- LO GO / NO-GO after NEW or REVISED -> accepted
- LO VERIFIED after NEW (post-impl) -> accepted
- Writer-authority rejection (prime writing GO, LO writing NEW)
- Invalid status transitions (GO->GO, VERIFIED->*)
- Existing-file collision -> BridgeConflictError
- Concurrent index change -> BridgeConflictError via expected_index_raw
- Post-write live-state verification

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.gtkb_bridge_writer import (
    BridgeConflictError,
    BridgeTransitionError,
    LOYAL_OPPOSITION_ROLE_SLOT,
    PRIME_ROLE_SLOT,
    get_block,
    insert_index_status,
    next_file_number,
    parse_index,
    read_index,
    validate_transition,
    write_bridge_file,
)


INDEX_HEADER = (
    "# Bridge Index\n"
    "\n"
    "<!-- Prime inserts new document entries at the top of the list below. -->\n"
    "<!-- Codex scans for NEW/REVISED statuses and adds GO/NO-GO/VERIFIED versions. -->\n"
    "<!-- Statuses: NEW, REVISED, GO, NO-GO, VERIFIED -->\n"
    "\n"
)


def _build_project(tmp_path: Path, index_body: str = "") -> Path:
    (tmp_path / "bridge").mkdir()
    (tmp_path / "bridge" / "INDEX.md").write_text(INDEX_HEADER + index_body, encoding="utf-8")
    return tmp_path


def _doc_block(name: str, entries: list[tuple[str, int]]) -> str:
    lines = [f"Document: {name}\n"]
    for status, version in entries:
        lines.append(f"{status}: bridge/{name}-{version:03d}.md\n")
    lines.append("\n")
    return "".join(lines)


def _make_bridge_file(project_root: Path, name: str, version: int, body: str = "NEW\n") -> None:
    (project_root / "bridge" / f"{name}-{version:03d}.md").write_text(body, encoding="utf-8")


# ---------- parse / read ----------


def test_parse_index_extracts_blocks_and_order(tmp_path: Path) -> None:
    project = _build_project(
        tmp_path,
        _doc_block("foo", [("GO", 2), ("NEW", 1)])
        + _doc_block("bar", [("VERIFIED", 3), ("NEW", 2), ("GO", 1)]),
    )
    raw, blocks = read_index(project)
    assert len(blocks) == 2
    assert blocks[0].name == "foo"
    assert blocks[0].latest_status == "GO"
    assert blocks[0].latest_version == 2
    assert blocks[1].name == "bar"
    assert blocks[1].latest_status == "VERIFIED"


def test_parse_index_skips_comments_and_blank_lines() -> None:
    raw = (
        "# heading\n\n<!-- comment -->\n\nDocument: x\nNEW: bridge/x-001.md\n"
        "<!-- retired note -->\nGO: bridge/x-002.md\n"
    )
    blocks = parse_index(raw)
    assert len(blocks) == 1
    assert blocks[0].entries[0].status == "NEW"
    assert blocks[0].entries[1].status == "GO"


# ---------- next_file_number ----------


def test_next_file_number_new_document(tmp_path: Path) -> None:
    project = _build_project(tmp_path)
    assert next_file_number("brand-new", project) == 1


def test_next_file_number_with_gap_in_index(tmp_path: Path) -> None:
    project = _build_project(
        tmp_path,
        _doc_block("gappy", [("GO", 7), ("NO-GO", 4), ("NEW", 1)]),
    )
    assert next_file_number("gappy", project) == 8


def test_next_file_number_includes_disk_files_not_in_index(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("hybrid", [("NEW", 1)]))
    _make_bridge_file(project, "hybrid", 5, "orphan\n")
    assert next_file_number("hybrid", project) == 6


# ---------- validate_transition: Prime NEW ----------


def test_prime_new_on_new_document_accepted(tmp_path: Path) -> None:
    project = _build_project(tmp_path)
    validate_transition("fresh", "NEW", PRIME_ROLE_SLOT, project)


def test_prime_new_after_go_accepted(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("postimpl", [("GO", 2), ("NEW", 1)]))
    validate_transition("postimpl", "NEW", PRIME_ROLE_SLOT, project)


def test_prime_new_after_no_go_rejected(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("blocked", [("NO-GO", 2), ("NEW", 1)]))
    with pytest.raises(BridgeTransitionError, match="only permitted on new document or after GO"):
        validate_transition("blocked", "NEW", PRIME_ROLE_SLOT, project)


def test_prime_new_after_revised_rejected(tmp_path: Path) -> None:
    project = _build_project(
        tmp_path,
        _doc_block("inflight", [("REVISED", 3), ("NO-GO", 2), ("NEW", 1)]),
    )
    with pytest.raises(BridgeTransitionError):
        validate_transition("inflight", "NEW", PRIME_ROLE_SLOT, project)


def test_prime_new_after_verified_rejected(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("done", [("VERIFIED", 2), ("NEW", 1)]))
    with pytest.raises(BridgeTransitionError, match="VERIFIED"):
        validate_transition("done", "NEW", PRIME_ROLE_SLOT, project)


# ---------- validate_transition: Prime REVISED ----------


def test_prime_revised_after_no_go_accepted(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("fixable", [("NO-GO", 2), ("NEW", 1)]))
    validate_transition("fixable", "REVISED", PRIME_ROLE_SLOT, project)


def test_prime_revised_after_new_rejected(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("stillnew", [("NEW", 1)]))
    with pytest.raises(BridgeTransitionError):
        validate_transition("stillnew", "REVISED", PRIME_ROLE_SLOT, project)


# ---------- validate_transition: LO GO / NO-GO ----------


def test_lo_go_after_new_accepted(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("pending", [("NEW", 1)]))
    validate_transition("pending", "GO", LOYAL_OPPOSITION_ROLE_SLOT, project)


def test_lo_go_after_revised_accepted(tmp_path: Path) -> None:
    project = _build_project(
        tmp_path, _doc_block("revised", [("REVISED", 3), ("NO-GO", 2), ("NEW", 1)])
    )
    validate_transition("revised", "GO", LOYAL_OPPOSITION_ROLE_SLOT, project)


def test_lo_go_after_go_rejected(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("double", [("GO", 2), ("NEW", 1)]))
    with pytest.raises(BridgeTransitionError, match="only permitted after NEW or REVISED"):
        validate_transition("double", "GO", LOYAL_OPPOSITION_ROLE_SLOT, project)


def test_lo_verified_after_new_accepted(tmp_path: Path) -> None:
    project = _build_project(
        tmp_path,
        _doc_block("postimpl", [("NEW", 3), ("GO", 2), ("NEW", 1)]),
    )
    validate_transition("postimpl", "VERIFIED", LOYAL_OPPOSITION_ROLE_SLOT, project)


def test_lo_verified_after_go_rejected(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("go-to-verified", [("GO", 2), ("NEW", 1)]))
    with pytest.raises(BridgeTransitionError, match="only permitted after post-impl NEW"):
        validate_transition("go-to-verified", "VERIFIED", LOYAL_OPPOSITION_ROLE_SLOT, project)


# ---------- writer-authority rejection ----------


def test_prime_cannot_write_go(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("x", [("NEW", 1)]))
    with pytest.raises(BridgeTransitionError, match="prime-builder may not write"):
        validate_transition("x", "GO", PRIME_ROLE_SLOT, project)


def test_lo_cannot_write_new(tmp_path: Path) -> None:
    project = _build_project(tmp_path)
    with pytest.raises(BridgeTransitionError, match="loyal-opposition may not write"):
        validate_transition("x", "NEW", LOYAL_OPPOSITION_ROLE_SLOT, project)


def test_unknown_role_slot_rejected(tmp_path: Path) -> None:
    project = _build_project(tmp_path)
    with pytest.raises(BridgeTransitionError, match="unknown role_slot"):
        validate_transition("x", "NEW", "acting-prime-builder", project)


def test_invalid_status_rejected(tmp_path: Path) -> None:
    project = _build_project(tmp_path)
    with pytest.raises(BridgeTransitionError, match="invalid status"):
        validate_transition("x", "MAYBE", PRIME_ROLE_SLOT, project)


# ---------- VERIFIED thread is closed ----------


def test_any_transition_after_verified_rejected(tmp_path: Path) -> None:
    project = _build_project(
        tmp_path, _doc_block("closed", [("VERIFIED", 2), ("NEW", 1)])
    )
    for status, role in [
        ("REVISED", PRIME_ROLE_SLOT),
        ("GO", LOYAL_OPPOSITION_ROLE_SLOT),
        ("NO-GO", LOYAL_OPPOSITION_ROLE_SLOT),
        ("VERIFIED", LOYAL_OPPOSITION_ROLE_SLOT),
    ]:
        with pytest.raises(BridgeTransitionError, match="VERIFIED"):
            validate_transition("closed", status, role, project)


# ---------- write_bridge_file ----------


def test_write_bridge_file_creates_and_verifies(tmp_path: Path) -> None:
    project = _build_project(tmp_path)
    path = write_bridge_file("docthing", 1, "NEW\n\nhello\n", project)
    assert path.exists()
    assert path.read_text(encoding="utf-8") == "NEW\n\nhello\n"


def test_write_bridge_file_rejects_existing(tmp_path: Path) -> None:
    project = _build_project(tmp_path)
    _make_bridge_file(project, "conflict", 1, "existing\n")
    with pytest.raises(BridgeConflictError, match="already exists"):
        write_bridge_file("conflict", 1, "new body\n", project)


# ---------- insert_index_status ----------


def test_insert_index_status_prepends_in_document_block(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("work", [("NEW", 1)]))
    insert_index_status("work", 2, "GO", project)
    _, blocks = read_index(project)
    block = get_block(blocks, "work")
    assert block is not None
    assert block.latest_status == "GO"
    assert block.latest_version == 2
    assert block.entries[1].status == "NEW"
    assert block.entries[1].version == 1


def test_insert_index_status_detects_stale_snapshot(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("race", [("NEW", 1)]))
    snapshot, _ = read_index(project)
    (project / "bridge" / "INDEX.md").write_text(
        snapshot + _doc_block("intruder", [("NEW", 1)]), encoding="utf-8"
    )
    with pytest.raises(BridgeConflictError, match="stale"):
        insert_index_status("race", 2, "GO", project, expected_index_raw=snapshot)


def test_insert_index_status_fails_when_document_block_missing(tmp_path: Path) -> None:
    project = _build_project(tmp_path)
    with pytest.raises(BridgeConflictError, match="block not found"):
        insert_index_status("ghost", 1, "NEW", project)


def test_insert_index_status_rejects_invalid_status(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("x", [("NEW", 1)]))
    with pytest.raises(BridgeTransitionError, match="invalid status"):
        insert_index_status("x", 2, "MAYBE", project)
