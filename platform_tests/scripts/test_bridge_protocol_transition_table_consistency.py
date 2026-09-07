"""Doc-code consistency test for the bridge transition table.

WI-5827 / TEST-11783, re-sourced by WI-7118 (spec `GOV-FILE-BRIDGE-AUTHORITY-001`,
`SPEC-BRIDGE-STATUS-PHASE-DISTINCT-001`).

Two things changed at WI-7118 and both matter to this test:

* The code of record moved. It is now the single `TRANSITIONS` constant in
  `groundtruth_kb.bridge.vocabulary`, not `ORDINARY_TRANSITIONS` plus
  `POST_GO_REPORT_AUGMENTATIONS` in the resolver. The augmentation map is
  retired, not relocated: it was the only mechanism by which the successor
  relation consulted thread history, which clause 4 forbids.
* The document of record moved. This test now reads the neutral baseline at
  `.harness-baseline-configuration/rules/file-bridge-protocol.md`. It
  previously read `config/agent-control/gtkb-file-bridge-protocol.md`, which
  canon section 8 classifies as forbidden drift, and additionally asserted
  against the generated `.claude` projection. Binding a test to generated
  output makes the projection authoritative, which is exactly the inversion
  canon section 8 prohibits; the projector's own `--check` verifies that
  projections match the baseline.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.bridge.vocabulary import (  # noqa: E402
    CANONICAL_STATUSES,
    PERMITTED_ON_WRITE,
    TRANSITIONS,
)

BASELINE_DOC = PROJECT_ROOT / ".harness-baseline-configuration" / "rules" / "file-bridge-protocol.md"

TABLE_HEADING = "## Post-Verdict Transition Table"
STATUS_HEADING = "## Statuses"
POST_IMPL_HEADING = "## Post-Implementation Verification"

_ROW_RE = re.compile(r"^\|\s*([A-Z][A-Z-]*)\s*\|\s*([A-Z, -]+?)\s*\|\s*$")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    start = text.index(heading)
    end = text.find("\n## ", start + len(heading))
    return text[start:end] if end != -1 else text[start:]


def _parse_table(section: str) -> dict[str, frozenset[str]]:
    table: dict[str, frozenset[str]] = {}
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        if line.replace("|", "").replace("-", "").strip() == "":
            continue  # separator row
        match = _ROW_RE.match(line)
        if match is None:
            continue  # header row, or a prose row this table does not own
        key = match.group(1).strip()
        values = frozenset(v.strip() for v in match.group(2).split(",") if v.strip())
        table[key] = values
    return table


def test_baseline_table_matches_the_single_vocabulary() -> None:
    """The rendered table equals the code of record.

    `WITHDRAWN` is compared out: canon gives it no successors, the constant
    holds an empty frozenset for it, and an empty markdown cell is not a
    renderable row. The document says so in prose instead.
    """
    rendered = _parse_table(_section(_read(BASELINE_DOC), TABLE_HEADING))
    expected = {k: v for k, v in TRANSITIONS.items() if v}
    assert rendered == expected
    assert "`WITHDRAWN` and `SUPERSEDED` are terminal and have no successors" in _section(
        _read(BASELINE_DOC), TABLE_HEADING
    )


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
    assert "NEW" not in TRANSITIONS["NO-GO"]
    assert "READY" not in TRANSITIONS["NO-GO"]
    rendered = _parse_table(_section(_read(BASELINE_DOC), TABLE_HEADING))
    assert "NEW" not in rendered["NO-GO"]
    assert "READY" not in rendered["NO-GO"]


def test_vocabulary_is_exactly_canon_twelve() -> None:
    assert len(CANONICAL_STATUSES) == 12
    assert (
        frozenset(
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
        == CANONICAL_STATUSES
    )
    assert PERMITTED_ON_WRITE == CANONICAL_STATUSES
    status_section = _section(_read(BASELINE_DOC), STATUS_HEADING)
    for status in CANONICAL_STATUSES:
        assert f"| {status} |" in status_section, f"{status} missing from baseline table"


def test_obsolete_statuses_are_inert_and_never_writable() -> None:
    """Canon section 6: no alias or crosswalk exists for NO-ACTION or DEFERRED."""
    for obsolete in ("NO-ACTION", "DEFERRED"):
        assert obsolete not in PERMITTED_ON_WRITE
        assert obsolete not in CANONICAL_STATUSES
        # Inert means it has no forward transitions of its own beyond the
        # read-time compatibility set, and never appears as a canonical target.
        assert obsolete not in TRANSITIONS
    status_section = _section(_read(BASELINE_DOC), STATUS_HEADING)
    assert "no alias or crosswalk exists" in status_section


def test_post_implementation_section_names_ready() -> None:
    section = _section(_read(BASELINE_DOC), POST_IMPL_HEADING)
    assert "publishes as a `READY` entry" in section
    assert "`bridge_kind: implementation_report`" in section
    assert "It replaces the historical\n   use of `NEW` for reports." in section
    assert "the corrected report publishes as `READY` again" in section
