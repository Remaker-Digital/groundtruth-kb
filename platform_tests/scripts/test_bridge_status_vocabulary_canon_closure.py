"""Canon closure for the bridge status vocabulary (WI-7118).

Spec: `SPEC-BRIDGE-STATUS-PHASE-DISTINCT-001` clauses 1, 4, 5, 6, 7.
Authority: canon section 6 (`AGENTS.md`).

The defect this pins: `scripts/bridge_lifecycle_resolver.py` could not parse the
status token `READY`, so five Loyal-Opposition-actionable threads resolved as
"lifecycle resolution failed - cannot evaluate" and no implementation report
could be verified. The root cause was not a missing branch but a missing single
source: the vocabulary was restated in nine places in that module alone, and the
regex that recognised head tokens was maintained by hand.
"""

from __future__ import annotations

import inspect
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.bridge import vocabulary  # noqa: E402
from groundtruth_kb.bridge.vocabulary import (  # noqa: E402
    ACCEPTED_ON_READ,
    CANONICAL_STATUSES,
    HISTORICAL_INERT_STATUSES,
    LOYAL_OPPOSITION_ACTIONABLE_STATUSES,
    LOYAL_OPPOSITION_AUTHORED_STATUSES,
    NON_DISPATCHABLE_STATUSES,
    PERMITTED_ON_WRITE,
    PRIME_ACTIONABLE_STATUSES,
    PRIME_AUTHORED_STATUSES,
    TRANSITIONS,
    is_lawful_transition,
    observed_status_pattern,
)

RESOLVER = PROJECT_ROOT / "scripts" / "bridge_lifecycle_resolver.py"


# 1 - the reported defect, at the level it was reported.
def test_ready_is_recognised_as_a_head_token() -> None:
    pattern = observed_status_pattern()
    match = pattern.match("READY")
    assert match is not None, "READY must parse; its absence stranded five threads"
    assert match.group("status") == "READY"


# 2 - the prefix collisions the single source has to get right.
def test_longer_tokens_win_over_their_prefixes() -> None:
    pattern = observed_status_pattern()
    for token in ("NOT-READY", "NO-ACTION", "VERDICT-REJECTED", "NO-GO"):
        match = pattern.match(token)
        assert match is not None, f"{token} must parse"
        assert match.group("status") == token, (
            f"{token} truncated to {match.group('status')}: alternation order is wrong"
        )


# 3 - clause 1: the vocabulary is exactly canon's ten.
def test_canonical_vocabulary_is_exactly_ten() -> None:
    assert len(CANONICAL_STATUSES) == 10
    assert PERMITTED_ON_WRITE == CANONICAL_STATUSES


# 4 - clause 4: the successor relation is a pure function of current status.
def test_successor_relation_takes_only_the_current_status() -> None:
    signature = inspect.signature(is_lawful_transition)
    assert list(signature.parameters) == ["current", "successor"], (
        "a history parameter here would reintroduce the retired prior_go_seen gate"
    )
    # Same input, same answer, regardless of how it is reached.
    assert is_lawful_transition("GO", "READY") is True
    assert is_lawful_transition("GO", "NEW") is False


# 5 - clause 5: exactly one home. The resolver must declare no local vocabulary.
def test_resolver_declares_no_local_status_vocabulary() -> None:
    source = RESOLVER.read_text(encoding="utf-8")
    for retired in (
        "ORDINARY_TRANSITIONS",
        "POST_GO_REPORT_AUGMENTATIONS",
        "prior_go_seen",
    ):
        assert not re.search(rf"^{retired}\s*[:=]", source, flags=re.MULTILINE), (
            f"{retired} must not be defined in the resolver"
        )
    assert not re.search(r"^_OBSERVED_STATUS_RE\s*=\s*re\.compile", source, flags=re.MULTILINE), (
        "the head-token regex must be derived from the vocabulary, not hand-written"
    )
    assert "from groundtruth_kb.bridge.vocabulary import" in source


# 6 - clause 6 / canon: obsolete tokens are inert, with no crosswalk.
def test_obsolete_tokens_are_readable_but_confer_nothing() -> None:
    for obsolete in ("NO-ACTION", "DEFERRED"):
        assert obsolete in HISTORICAL_INERT_STATUSES
        assert obsolete in ACCEPTED_ON_READ, "history must still parse"
        assert obsolete not in PERMITTED_ON_WRITE, "new writes must reject it"
        assert obsolete not in CANONICAL_STATUSES
        assert obsolete not in TRANSITIONS, "an inert token owns no forward relation"
        assert obsolete not in PRIME_AUTHORED_STATUSES
        assert obsolete not in LOYAL_OPPOSITION_AUTHORED_STATUSES
    # No crosswalk: nothing in the module maps an obsolete token to a live one.
    for name, value in vars(vocabulary).items():
        if isinstance(value, dict) and name != "HISTORICAL_TRANSITIONS":
            assert not (set(value) & HISTORICAL_INERT_STATUSES), f"{name} maps an obsolete token, which canon forbids"


# 7 - canon section 6: superseded pairs fail closed; there is no crosswalk.
def test_superseded_transition_pairs_fail_closed() -> None:
    """No compatibility variant exists for a retired pair.

    A committed chain bearing one of these is repaired or marked abandoned per
    canon section 6, tracked as WI-7663. Admitting it here would be the
    compatibility layer canon section 16 forbids.
    """
    for retired_pair in (
        ("GO", "NEW"),
        ("GO", "REVISED"),
        ("GO", "WITHDRAWN"),
        ("VERDICT-REJECTED", "VERIFIED"),
    ):
        current, successor = retired_pair
        assert is_lawful_transition(current, successor) is False, (
            f"{current} -> {successor} is superseded and must not be lawful"
        )
    # A second, laxer surface exists by owner decision (AskUserQuestion,
    # 2026-09-03) so that a reader can resolve chains whose superseded pairs no
    # one can rewrite. It is bounded: exactly two named maps, both read-time.
    # An unaccounted third would be the compatibility layer canon forbids.
    surfaces = sorted(
        name
        for name, value in vars(vocabulary).items()
        if isinstance(value, dict) and name != "TRANSITIONS" and not name.startswith("__")
    )
    assert surfaces == ["HISTORICAL_TRANSITIONS", "RESOLVABLE_TRANSITIONS"], (
        f"unaccounted transition surface: {surfaces}"
    )


# 8 - canon routing: the two role queues are disjoint, which is the phase point.
def test_role_queues_are_disjoint() -> None:
    assert not (PRIME_ACTIONABLE_STATUSES & LOYAL_OPPOSITION_ACTIONABLE_STATUSES)
    assert frozenset({"GO", "NO-GO", "NOT-READY"}) == PRIME_ACTIONABLE_STATUSES
    assert frozenset({"NEW", "REVISED", "READY", "VERDICT-REJECTED"}) == LOYAL_OPPOSITION_ACTIONABLE_STATUSES
    assert not (NON_DISPATCHABLE_STATUSES & PRIME_ACTIONABLE_STATUSES)
    assert not (NON_DISPATCHABLE_STATUSES & LOYAL_OPPOSITION_ACTIONABLE_STATUSES)


# 9 - every transition target is a real status; the table cannot drift.
def test_transition_targets_are_all_canonical() -> None:
    for current, successors in TRANSITIONS.items():
        assert current in CANONICAL_STATUSES, f"{current} keys a table row"
        for successor in successors:
            assert successor in CANONICAL_STATUSES, f"{current} -> {successor} names a non-canonical status"


# 10 - the authorship split canon section 4 states, including the shared token.
def test_authorship_sets_match_canon() -> None:
    assert (
        frozenset({"NEW", "REVISED", "READY", "VERDICT-REJECTED", "WITHDRAWN", "ADVISORY"}) == PRIME_AUTHORED_STATUSES
    )
    assert frozenset({"GO", "NO-GO", "NOT-READY", "VERIFIED", "ADVISORY"}) == LOYAL_OPPOSITION_AUTHORED_STATUSES
    # ADVISORY is the only token canon gives to both roles.
    shared = PRIME_AUTHORED_STATUSES & LOYAL_OPPOSITION_AUTHORED_STATUSES
    assert shared == frozenset({"ADVISORY"})
    # Every canonical status has an author.
    assert (PRIME_AUTHORED_STATUSES | LOYAL_OPPOSITION_AUTHORED_STATUSES) == CANONICAL_STATUSES
