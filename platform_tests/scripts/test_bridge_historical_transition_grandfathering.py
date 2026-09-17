"""Read-time tolerance for superseded bridge transition pairs (WI-7118).

Spec: `SPEC-BRIDGE-STATUS-PHASE-DISTINCT-001` clause 4.
Authority: canon section 6; owner decision by AskUserQuestion, 2026-09-03 --
"accept historical transition pairs on READ, keep canon strict on WRITE".

The defect this pins: tightening the successor relation to canon made
`GO -> NEW` and `GO -> REVISED` unlawful. Both were the normal shape under the
superseded vocabulary, where the first post-implementation report published as
`NEW`. 161 of 538 chains carried such a pair. Because the clause preflight is a
blocking gate that resolves the chain before any verdict may be issued, 23
chains holding live work became unreviewable -- not merely flagged, but
structurally incapable of receiving a verdict. Bridge files are append-only, so
no correction to the offending pair was ever possible.

The fix separates two questions that had been collapsed into one: what a writer
may create, and what a reader may resolve.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from groundtruth_kb.bridge.vocabulary import (  # noqa: E402
    CANONICAL_STATUSES,
    HISTORICAL_TRANSITIONS,
    RESOLVABLE_TRANSITIONS,
    TRANSITIONS,
    is_lawful_transition,
    is_resolvable_transition,
)

# Measured across all 538 chains under bridge/ on 2026-09-03: 22 distinct pairs
# the canon table rejects, 289 occurrences, 161 chains.
#
# Grandfathered: pairs that only let a reader DESCRIBE an old chain.
GRANDFATHERED_PAIRS = {
    ("GO", "NEW"),
    ("GO", "REVISED"),
    ("GO", "WITHDRAWN"),
    ("GO", "NO-GO"),
    ("GO", "ADVISORY"),
    ("GO", "GO"),
    ("NEW", "NEW"),
    ("NEW", "REVISED"),
    ("NEW", "NOT-READY"),
    ("REVISED", "REVISED"),
    ("REVISED", "NOT-READY"),
    ("NO-GO", "ADVISORY"),
    ("NO-GO", "NO-GO"),
    ("NO-GO", "GO"),
    ("NO-GO", "NEW"),
    ("VERDICT-REJECTED", "WITHDRAWN"),
    ("VERDICT-REJECTED", "VERDICT-REJECTED"),
}

# NOT grandfathered, though each occurs on disk. These would let a reader
# CONCLUDE that work reached the authority-bearing terminal status without a
# GO or an implementation report. The resolver feeds `implementation_start_gate`
# for effect checks, so a resolution is not merely a
# description there. All affected chains are already terminal, so the exclusion
# strands no live work.
AUTHORITY_BEARING_EXCLUSIONS = {
    ("NEW", "VERIFIED"),
    ("REVISED", "VERIFIED"),
    ("GO", "VERIFIED"),
    ("VERDICT-REJECTED", "VERIFIED"),
    ("VERIFIED", "REVISED"),
}


def test_write_time_canon_is_unchanged() -> None:
    """Grandfathering must not loosen what a writer may create.

    This is the regression that matters most. If a later edit routes writes
    through the tolerant predicate, every superseded shape becomes creatable
    again and the vocabulary silently reverts.
    """
    assert not is_lawful_transition("GO", "NEW")
    assert not is_lawful_transition("GO", "REVISED")
    assert is_lawful_transition("GO", "READY")
    assert is_lawful_transition("READY", "VERIFIED")
    assert is_lawful_transition("NO-GO", "REVISED")


def test_every_grandfathered_pair_resolves() -> None:
    for current, successor in GRANDFATHERED_PAIRS:
        assert is_resolvable_transition(current, successor), f"{current} -> {successor} must resolve"


def test_verified_shortcuts_are_never_grandfathered() -> None:
    """Read-time tolerance must not manufacture authority.

    This is the guard that stops the grandfathering map from growing into a
    general compatibility layer. VERIFIED is the authority-bearing terminal
    status; no superseded pair may synthesize it, on read or on write.
    """
    for current, successor in AUTHORITY_BEARING_EXCLUSIONS:
        assert not is_resolvable_transition(current, successor), (
            f"{current} -> {successor} must stay closed: it would manufacture authority"
        )
        assert not is_lawful_transition(current, successor)


def test_historical_map_is_purely_additive() -> None:
    """No historical entry may duplicate a canon successor.

    Overlap would mean the map is doing work canon already does, which hides
    how much tolerance is actually being extended.
    """
    for current, successors in HISTORICAL_TRANSITIONS.items():
        overlap = successors & TRANSITIONS.get(current, frozenset())
        assert not overlap, f"{current}: {sorted(overlap)} already lawful under canon"


def test_historical_map_admits_no_obsolete_status() -> None:
    """Grandfathering transitions must not smuggle back retired statuses.

    `NO-ACTION` and `DEFERRED` are retired with no alias and no crosswalk.
    """
    for current, successors in HISTORICAL_TRANSITIONS.items():
        assert current in CANONICAL_STATUSES, f"{current} is not canonical"
        for successor in successors:
            assert successor in CANONICAL_STATUSES, f"{successor} is not canonical"


def test_resolvable_is_exactly_canon_union_historical() -> None:
    for status in set(TRANSITIONS) | set(HISTORICAL_TRANSITIONS):
        expected = TRANSITIONS.get(status, frozenset()) | HISTORICAL_TRANSITIONS.get(status, frozenset())
        assert RESOLVABLE_TRANSITIONS[status] == expected
