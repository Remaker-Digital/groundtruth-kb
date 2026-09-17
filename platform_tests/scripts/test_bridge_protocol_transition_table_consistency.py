"""Static bridge-guidance consistency for TEST-11783.

Read the authored neutral baseline and the selected package vocabulary. These
checks establish documented status, routing and successor agreement only;
test_native_bridge.py separately exercises the native service and its guards.
Headings, wrapping and grouped rows are presentation choices, not authority.
"""

from __future__ import annotations

import re
from pathlib import Path

from groundtruth_kb.bridge.vocabulary import (
    CANONICAL_STATUSES,
    HISTORICAL_INERT_STATUSES,
    LOYAL_OPPOSITION_ACTIONABLE_STATUSES,
    LOYAL_OPPOSITION_AUTHORED_STATUSES,
    NON_DISPATCHABLE_STATUSES,
    PERMITTED_ON_WRITE,
    PRIME_ACTIONABLE_STATUSES,
    PRIME_AUTHORED_STATUSES,
    THREAD_START_STATUSES,
    TRANSITIONS,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASELINE_DOC = PROJECT_ROOT / ".harness-baseline-configuration" / "rules" / "file-bridge-protocol.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _parse_table(text: str, headers: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
    """Read one named table, expanding grouped keys and rejecting duplicates."""
    rows: dict[str, tuple[str, ...]] = {}
    active = False
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            if active:
                break
            continue
        cells = tuple(cell.strip().strip("`") for cell in line.strip("|").split("|"))
        if cells == headers:
            assert not active, "Duplicate table header"
            active = True
            continue
        if not active or all(re.fullmatch(r":?-+:?", cell) for cell in cells):
            continue
        assert len(cells) == len(headers), f"Malformed table row: {line}"
        for key in cells[0].split(","):
            key = key.strip().strip("`")
            assert key and key not in rows, f"Duplicate or empty status: {key}"
            rows[key] = cells[1:]
    assert rows, f"Missing table: {headers}"
    return rows


def _documented_transitions() -> dict[str, frozenset[str]]:
    rows = _parse_table(_read(BASELINE_DOC), ("Current status", "Permitted next status"))
    return {
        status: frozenset() if cells[0] == "None" else frozenset(s.strip() for s in cells[0].split(","))
        for status, cells in rows.items()
    }


def test_baseline_table_matches_the_single_vocabulary() -> None:
    """All successors, including starts and empty terminal rows, are documented."""
    rendered = _documented_transitions()
    assert rendered.pop("start") == THREAD_START_STATUSES
    assert rendered == TRANSITIONS
    assert not rendered["WITHDRAWN"]
    assert not rendered["SUPERSEDED"]


def test_report_phase_and_proposal_phase_share_no_token() -> None:
    """The point of the READY/NOT-READY pair, asserted mechanically.

    Canon section 6: NOT-READY "exists so that no token is lawful in both the
    proposal phase and the report phase."
    """
    proposal_phase = {"NEW", "REVISED", "GO", "NO-GO"}
    report_phase = {"READY", "NOT-READY"}
    assert not (proposal_phase & report_phase)
    assert "READY" not in TRANSITIONS["NO-GO"], "canon rejects NO-GO -> READY"
    # SUPERSEDED is a terminal closer lawful after any non-terminal status; it
    # belongs to neither phase, so it is excluded from the phase-disjointness claim.
    assert TRANSITIONS["GO"] == frozenset({"READY", "VERDICT-REJECTED", "SUPERSEDED"})
    assert TRANSITIONS["READY"] == frozenset({"VERIFIED", "NOT-READY", "SUPERSEDED"})


def test_no_go_row_never_allows_new_or_ready() -> None:
    for table in (TRANSITIONS, _documented_transitions()):
        assert "NEW" not in table["NO-GO"]
        assert "READY" not in table["NO-GO"]
        assert table["NO-GO"] == frozenset({"REVISED", "WITHDRAWN", "VERDICT-REJECTED", "SUPERSEDED"})


def test_vocabulary_is_exactly_canon_twelve() -> None:
    expected = frozenset(
        {
            "NEW",
            "REVISED",
            "READY",
            "VERDICT-REJECTED",
            "BLOCKED",
            "GO",
            "NO-GO",
            "NOT-READY",
            "SUPERSEDED",
            "VERIFIED",
            "WITHDRAWN",
            "ADVISORY",
        }
    )
    assert expected == CANONICAL_STATUSES
    assert PERMITTED_ON_WRITE == CANONICAL_STATUSES
    rows = _parse_table(_read(BASELINE_DOC), ("Status", "Author", "Next responder"))
    assert set(rows) == CANONICAL_STATUSES
    for status, (author, responder) in rows.items():
        expected_authors = set()
        if status in PRIME_AUTHORED_STATUSES:
            expected_authors.add("Prime Builder")
        if status in LOYAL_OPPOSITION_AUTHORED_STATUSES:
            expected_authors.add("Loyal Opposition")
        actual_authors = {"Prime Builder", "Loyal Opposition"} if author == "Either role" else {author}
        assert actual_authors == expected_authors, status
        if status in PRIME_ACTIONABLE_STATUSES:
            assert responder == "Prime Builder", status
        elif status in LOYAL_OPPOSITION_ACTIONABLE_STATUSES:
            assert responder == "Loyal Opposition", status
        else:
            assert status in NON_DISPATCHABLE_STATUSES and responder == "None", status


def test_obsolete_statuses_are_inert_and_never_writable() -> None:
    rows = _parse_table(_read(BASELINE_DOC), ("Status", "Author", "Next responder"))
    for obsolete in HISTORICAL_INERT_STATUSES:
        assert obsolete not in PERMITTED_ON_WRITE
        assert obsolete not in CANONICAL_STATUSES
        assert obsolete not in TRANSITIONS
        assert all(obsolete not in targets for targets in TRANSITIONS.values())
        assert obsolete not in rows
    text = " ".join(_read(BASELINE_DOC).split())
    assert "NO-ACTION and DEFERRED" in text
    assert "Obsolete statuses do not become current aliases or grant claims" in text


def test_post_implementation_section_names_ready() -> None:
    text = " ".join(_read(BASELINE_DOC).split())
    assert "NEW proposal, GO, implementation, READY report, independent verification and VERIFIED" in text
    assert "NOT-READY rejects a report and requires corrected READY" in text
    assert "READY carries `bridge_kind: implementation_report`" in text
    assert "NEW is never an implementation report" in text
    assert "VERIFIED to VERIFIED requires canonical fresh-verification work" in text
    assert "preserving its membership and existing artifact bytes" in text
