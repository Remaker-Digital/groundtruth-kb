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
    LOYAL_OPPOSITION_ROLE_SLOT,
    PRIME_ROLE_SLOT,
    BridgeConflictError,
    BridgeTransitionError,
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

AUTHOR_METADATA = {
    "author_identity": "Codex",
    "author_harness_id": "A",
    "author_session_context_id": "session-123",
    "author_model": "GPT-5.5",
    "author_model_version": "5.5",
    "author_model_configuration": "Extra High",
}


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


def _deferred_body() -> str:
    return (
        "DEFERRED\n\n"
        "# Deferred Thread\n\n"
        "## Owner Decisions / Input\n\n"
        "- DELIB-20260602-DEFERRED-TEST: owner decision sets this deferral.\n\n"
        "## Status\n\n"
        "Deferral reason: waiting for owner sequencing.\n"
        "Clear condition: owner records reactivation approval.\n"
    )


def _clear_body(status: str = "NEW") -> str:
    return (
        f"{status}\n\n"
        "# Reactivated Thread\n\n"
        "## Owner Decisions / Input\n\n"
        "- DELIB-20260602-DEFERRED-CLEAR-TEST: owner decision clears the DEFERRED status "
        "and resumes bridge work.\n\n"
        "## Specification Links\n\n"
        "- GOV-FILE-BRIDGE-AUTHORITY-001\n"
    )


# ---------- parse / read ----------


def test_parse_index_extracts_blocks_and_order(tmp_path: Path) -> None:
    project = _build_project(
        tmp_path,
        _doc_block("foo", [("GO", 2), ("NEW", 1)]) + _doc_block("bar", [("VERIFIED", 3), ("NEW", 2), ("GO", 1)]),
    )
    raw, blocks = read_index(project)
    assert len(blocks) == 2
    assert blocks[0].name == "foo"
    assert blocks[0].latest_status == "GO"
    assert blocks[0].latest_version == 2
    assert blocks[1].name == "bar"
    assert blocks[1].latest_status == "VERIFIED"


def test_parse_index_accepts_deferred_status(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("parked", [("DEFERRED", 2), ("GO", 1)]))

    _, blocks = read_index(project)

    assert blocks[0].name == "parked"
    assert blocks[0].latest_status == "DEFERRED"
    assert blocks[0].latest_version == 2


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


def test_lo_go_rejects_same_session_author_metadata(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("pending", [("NEW", 1)]))
    _make_bridge_file(project, "pending", 1, "NEW\nsession_context_id: s1\n")
    with pytest.raises(BridgeTransitionError, match="same-session review"):
        validate_transition(
            "pending",
            "GO",
            LOYAL_OPPOSITION_ROLE_SLOT,
            project,
            session_id="s1",
        )


def test_lo_go_allows_unrelated_session_author_metadata(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("pending", [("NEW", 1)]))
    _make_bridge_file(project, "pending", 1, "NEW\nauthor_session_id: s1\n")
    validate_transition(
        "pending",
        "GO",
        LOYAL_OPPOSITION_ROLE_SLOT,
        project,
        session_id="s2",
    )


def test_lo_go_after_revised_accepted(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("revised", [("REVISED", 3), ("NO-GO", 2), ("NEW", 1)]))
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


def test_roles_cannot_write_deferred_transition(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("x", [("GO", 1)]))

    with pytest.raises(BridgeTransitionError, match="may not write"):
        validate_transition("x", "DEFERRED", PRIME_ROLE_SLOT, project)
    with pytest.raises(BridgeTransitionError, match="may not write"):
        validate_transition("x", "DEFERRED", LOYAL_OPPOSITION_ROLE_SLOT, project)


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
    project = _build_project(tmp_path, _doc_block("closed", [("VERIFIED", 2), ("NEW", 1)]))
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
    path = write_bridge_file("docthing", 1, "NEW\n\nhello\n", project, author_metadata=AUTHOR_METADATA)
    assert path.exists()
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


def test_insert_index_status_merges_unrelated_snapshot_changes(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("race", [("NEW", 1)]))
    snapshot, _ = read_index(project)
    (project / "bridge" / "INDEX.md").write_text(snapshot + _doc_block("intruder", [("NEW", 1)]), encoding="utf-8")

    insert_index_status("race", 2, "GO", project, expected_index_raw=snapshot)

    _, blocks = read_index(project)
    race = get_block(blocks, "race")
    intruder = get_block(blocks, "intruder")
    assert race is not None
    assert race.latest_status == "GO"
    assert race.latest_version == 2
    assert intruder is not None
    assert intruder.latest_status == "NEW"


def test_insert_index_status_detects_same_document_stale_snapshot(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("race", [("NEW", 1)]))
    snapshot, _ = read_index(project)
    current = INDEX_HEADER + _doc_block("race", [("NO-GO", 2), ("NEW", 1)])
    (project / "bridge" / "INDEX.md").write_text(current, encoding="utf-8")

    with pytest.raises(BridgeConflictError, match="target document changed"):
        insert_index_status("race", 3, "GO", project, expected_index_raw=snapshot)


def test_insert_index_status_fails_when_document_block_missing(tmp_path: Path) -> None:
    project = _build_project(tmp_path)
    with pytest.raises(BridgeConflictError, match="block not found"):
        insert_index_status("ghost", 1, "NEW", project)


def test_insert_index_status_rejects_invalid_status(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("x", [("NEW", 1)]))
    with pytest.raises(BridgeTransitionError, match="invalid status"):
        insert_index_status("x", 2, "MAYBE", project)


def test_insert_index_status_deferred_rejects_missing_owner_evidence(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("work", [("NEW", 1)]))
    _make_bridge_file(project, "work", 2, "DEFERRED\n\nReason: waiting.\nClear condition: owner resumes.\n")

    with pytest.raises(BridgeTransitionError, match="Owner Decisions"):
        insert_index_status("work", 2, "DEFERRED", project)


def test_insert_index_status_deferred_accepts_owner_evidence_for_work_thread(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("work", [("NEW", 1)]))
    _make_bridge_file(project, "work", 2, _deferred_body())

    insert_index_status("work", 2, "DEFERRED", project)

    _, blocks = read_index(project)
    block = get_block(blocks, "work")
    assert block is not None
    assert block.latest_status == "DEFERRED"


def test_insert_index_status_clearing_deferred_requires_owner_clear_evidence(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("work", [("DEFERRED", 2), ("NEW", 1)]))
    _make_bridge_file(project, "work", 2, _deferred_body())
    _make_bridge_file(project, "work", 3, "NEW\n\n## Specification Links\n\n- GOV-FILE-BRIDGE-AUTHORITY-001\n")

    with pytest.raises(BridgeTransitionError, match="clearing DEFERRED"):
        insert_index_status("work", 3, "NEW", project)


def test_insert_index_status_clearing_deferred_accepts_owner_clear_evidence(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("work", [("DEFERRED", 2), ("NEW", 1)]))
    _make_bridge_file(project, "work", 2, _deferred_body())
    _make_bridge_file(project, "work", 3, _clear_body("NEW"))

    insert_index_status("work", 3, "NEW", project)

    _, blocks = read_index(project)
    block = get_block(blocks, "work")
    assert block is not None
    assert block.latest_status == "NEW"
    assert block.latest_version == 3


def test_insert_index_status_deferred_rejects_placeholder_owner_evidence(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("x", [("GO", 1)]))
    _make_bridge_file(project, "x", 2, "DEFERRED\n\n## Owner Decisions / Input\n\nNone\n")

    with pytest.raises(BridgeTransitionError, match="DEFERRED bridge file"):
        insert_index_status("x", 2, "DEFERRED", project)


def test_insert_index_status_deferred_accepts_owner_evidence_for_x_thread(tmp_path: Path) -> None:
    project = _build_project(tmp_path, _doc_block("x", [("GO", 1)]))
    _make_bridge_file(
        project,
        "x",
        2,
        "\n".join(
            [
                "DEFERRED",
                "",
                "## Owner Decisions / Input",
                "",
                "- DELIB-TEST-OWNER-DEFERRAL: owner directive to park.",
                "",
                "## Deferral Reason",
                "",
                "Reason: awaiting owner sequencing decision.",
                "",
                "## Clear Condition",
                "",
                "Clear condition: resume when the owner supplies that decision.",
                "",
            ]
        ),
    )

    insert_index_status("x", 2, "DEFERRED", project)

    _, blocks = read_index(project)
    assert blocks[0].latest_status == "DEFERRED"
    assert blocks[0].latest_version == 2
