#!/usr/bin/env python3
"""The single source for the canonical bridge status vocabulary (WI-7118).

`SPEC-BRIDGE-STATUS-PHASE-DISTINCT-001` clause 5 names this module as the one
place the vocabulary is enumerated. Before it existed the vocabulary was
restated in nine places inside `scripts/bridge_lifecycle_resolver.py` alone --
eight top-level definitions plus a hand-maintained regex -- and again across
dozens of consumers. Consumers import from here; they do not re-declare.

Authority is canon section 6 (`AGENTS.md`, "Status vocabulary -- exactly ten"
and "Legal transition table -- complete").

Nine-versus-ten: `DELIB-20260831060001` summarises the settled vocabulary as
nine statuses and omits `NOT-READY`. That record states of itself that it
"carries no authority. Authority lives only in GOV, SPEC, ADR, and DCL." Canon
section 6 is titled "exactly ten", defines `NOT-READY` in full as the
report-phase counterpart of `NO-GO`, and routes it in three further places.
Ten is therefore correct and the deliberation summary is the incomplete record.
"""

from __future__ import annotations

import re

# Canon section 6, in canon's own order. Exactly ten.
CANONICAL_STATUSES: frozenset[str] = frozenset(
    {
        "NEW",
        "REVISED",
        "READY",
        "VERDICT-REJECTED",
        "GO",
        "NO-GO",
        "NOT-READY",
        "VERIFIED",
        "WITHDRAWN",
        "ADVISORY",
    }
)

# Only the canonical ten may be written. Canon section 6 "Obsolete statuses":
# "New writes reject both."
PERMITTED_ON_WRITE: frozenset[str] = CANONICAL_STATUSES

# Superseded tokens that still appear in committed, append-only bridge files.
#
# Canon section 6 is explicit that these are inert: historical files bearing
# them "may be displayed only as inert historical text; they confer no routing,
# lifecycle, claim, lease, or implementation state, are never rewritten or
# normalized, and no alias or crosswalk exists."
#
# They are therefore RECOGNIZED so a historical chain parses and can be
# displayed -- and nothing more. There is deliberately no mapping from these to
# a canonical status: providing one would be the crosswalk canon forbids. They
# carry no entry in TRANSITIONS and no membership in any author set, so a chain
# whose operative status is one of these is non-dispatchable by construction.
HISTORICAL_INERT_STATUSES: frozenset[str] = frozenset({"NO-ACTION", "DEFERRED", "ACCEPTED", "BLOCKED"})

# What a reader may recognize. Recognition is not authority.
ACCEPTED_ON_READ: frozenset[str] = CANONICAL_STATUSES | HISTORICAL_INERT_STATUSES

# Canon section 6, "Legal transition table -- complete", keyed by current status
# alone. `SPEC-BRIDGE-STATUS-PHASE-DISTINCT-001` clause 4 requires the successor
# relation to be a pure function of the current status, so no entry here
# consults thread history.
#
# NO-GO carries canon's two forms in one entry. Canon distinguishes them "by
# author, not by the artifact adjudicated": the Loyal-Opposition form yields
# REVISED | WITHDRAWN | VERDICT-REJECTED, and the Dispatcher finalization form
# yields VERIFIED. The union keeps the relation history-free; the restriction of
# VERIFIED to the Dispatcher form is an authorship check
# (`is_dispatcher_finalization`), not a successor-set difference. Canon's
# explicit rejection of `NO-GO -> READY` holds because READY is absent here.
TRANSITIONS: dict[str, frozenset[str]] = {
    "NEW": frozenset({"GO", "NO-GO", "WITHDRAWN"}),
    "REVISED": frozenset({"GO", "NO-GO", "WITHDRAWN"}),
    "NO-GO": frozenset({"REVISED", "WITHDRAWN", "VERDICT-REJECTED", "VERIFIED"}),
    "GO": frozenset({"READY", "VERDICT-REJECTED"}),
    "READY": frozenset({"VERIFIED", "NOT-READY"}),
    "NOT-READY": frozenset({"READY", "VERDICT-REJECTED"}),
    "VERDICT-REJECTED": frozenset({"GO", "NO-GO", "NOT-READY"}),
    "VERIFIED": frozenset({"NO-GO"}),
    "ADVISORY": frozenset({"ADVISORY"}),
    # Canon: "WITHDRAWN is terminal and has no successors."
    "WITHDRAWN": frozenset(),
}

# Read-time tolerance for pairs written under the superseded vocabulary.
#
# This is the transition-level analogue of HISTORICAL_INERT_STATUSES above, and
# it exists for the same reason: recognition is not authority. TRANSITIONS is
# what canon permits a writer to create; the union below is what a reader may
# resolve without failing closed on history it cannot rewrite.
#
# The set is CLOSED and derived by measurement, not by judgement: on 2026-09-03
# every adjacent pair in all 538 chains under bridge/ was enumerated, and the 22
# pairs below are exactly those the canon table rejects, covering 289
# occurrences across 161 chains. Nothing may be added here for new work. A
# newly-authored pair outside TRANSITIONS is a defect in the artifact, not a
# gap in this map.
#
# Bridge files are append-only and immutable, so every pair a reader sees is
# already history by construction. Write-time canon is enforced where the write
# happens, not here.
HISTORICAL_TRANSITIONS: dict[str, frozenset[str]] = {
    "GO": frozenset({"NEW", "REVISED", "WITHDRAWN", "NO-GO", "ADVISORY", "GO"}),
    "NEW": frozenset({"NEW", "REVISED", "NOT-READY"}),
    "REVISED": frozenset({"REVISED", "NOT-READY"}),
    "NO-GO": frozenset({"ADVISORY", "NO-GO", "GO", "NEW"}),
    "VERDICT-REJECTED": frozenset({"WITHDRAWN", "VERDICT-REJECTED"}),
}

# Deliberately NOT grandfathered, though all four occur on disk:
#
#     NEW -> VERIFIED (38)   REVISED -> VERIFIED (12)
#     GO  -> VERIFIED (3)    VERDICT-REJECTED -> VERIFIED (1)
#
# Tolerance and authority are different axes. Accepting `GO -> REVISED` only
# lets a reader describe an old chain. Accepting `NEW -> VERIFIED` lets it
# conclude that work was verified which never received a GO or an
# implementation report -- and this resolver is consumed by
# `implementation_start_gate` and `check_protected_commit_authorization`, so a
# resolution is not merely a description there.
#
# VERIFIED is the authority-bearing terminal status. No superseded pair may
# synthesize it. These chains are already terminal, so excluding them strands
# no live work; the 2026-09-03 measurement confirmed none of the 23 live
# blocked chains depended on a VERIFIED shortcut.
# What a reader may resolve. The write-time table is TRANSITIONS.
RESOLVABLE_TRANSITIONS: dict[str, frozenset[str]] = {
    status: TRANSITIONS.get(status, frozenset()) | HISTORICAL_TRANSITIONS.get(status, frozenset())
    for status in set(TRANSITIONS) | set(HISTORICAL_TRANSITIONS)
}

# Canon section 4 authorship. ADVISORY is "authored by either role at any time",
# so it appears in both agent sets.
PRIME_AUTHORED_STATUSES: frozenset[str] = frozenset(
    {"NEW", "REVISED", "READY", "VERDICT-REJECTED", "WITHDRAWN", "ADVISORY"}
)
LOYAL_OPPOSITION_AUTHORED_STATUSES: frozenset[str] = frozenset({"GO", "NO-GO", "NOT-READY", "VERIFIED", "ADVISORY"})
# Canon section 7: the finalization-repair NO-GO is the only Dispatcher-authored
# status, and it is addressed to Loyal Opposition rather than Prime Builder.
DISPATCHER_AUTHORED_STATUSES: frozenset[str] = frozenset({"NO-GO"})

# Canon section 0.5 routing.
PRIME_ACTIONABLE_STATUSES: frozenset[str] = frozenset({"GO", "NO-GO", "NOT-READY"})
LOYAL_OPPOSITION_ACTIONABLE_STATUSES: frozenset[str] = frozenset({"NEW", "REVISED", "READY", "VERDICT-REJECTED"})
NON_DISPATCHABLE_STATUSES: frozenset[str] = frozenset({"ADVISORY", "VERIFIED", "WITHDRAWN"})


def status_alternation(statuses: frozenset[str] | None = None) -> str:
    """Return a regex alternation ordered longest-first.

    Order is load-bearing, not cosmetic. Python's alternation is first-match,
    not longest-match, so a shorter token listed first wins outright: `READY`
    ahead of `NOT-READY` would truncate every `NOT-READY` head to `READY`, and
    `NO-GO` ahead of `NO-ACTION` would truncate historical `NO-ACTION` heads.
    Sorting by descending length makes every prefix collision resolve to the
    longer token; the secondary alphabetical key only keeps the output stable
    for equal-length tokens so the pattern is reproducible.
    """
    pool = ACCEPTED_ON_READ if statuses is None else statuses
    return "|".join(sorted(pool, key=lambda s: (-len(s), s)))


def observed_status_pattern(statuses: frozenset[str] | None = None) -> re.Pattern[str]:
    """Compile the head-token matcher used to read a bridge file's first line.

    The trailing lookahead stops a token from matching a longer word that
    merely starts with it.
    """
    return re.compile(rf"^(?P<status>{status_alternation(statuses)})(?=$|[^A-Z0-9-])")


def is_lawful_transition(current: str, successor: str) -> bool:
    """Whether `successor` may follow `current`.

    Canon section 6's table, keyed by current status alone. There is no
    compatibility variant: a chain bearing a superseded pair fails closed and is
    repaired or marked abandoned per canon section 6, tracked as WI-7663.
    """
    return successor in TRANSITIONS.get(current, frozenset())


def is_resolvable_transition(current: str, successor: str) -> bool:
    """Whether a reader may resolve a chain bearing `current` -> `successor`.

    Broader than `is_lawful_transition` by exactly HISTORICAL_TRANSITIONS. Use
    this when reading an existing chain; use `is_lawful_transition` when
    deciding whether a new file may be written.

    The distinction matters because the two questions have different costs. A
    reader that fails closed on a superseded pair cannot report on the chain at
    all, which strands live work behind history no one can rewrite. A writer
    that accepts a superseded pair creates new drift.
    """
    return successor in RESOLVABLE_TRANSITIONS.get(current, frozenset())


def is_writable(status: str) -> bool:
    """Whether a new bridge file may be written bearing `status`."""
    return status in PERMITTED_ON_WRITE


def is_historical_inert(status: str) -> bool:
    """Whether `status` is a superseded token that confers no state."""
    return status in HISTORICAL_INERT_STATUSES
