"""Harness lifecycle finite state machine.

``REQ-HARNESS-REGISTRY-001`` FR2: each harness has a lifecycle ``status``
governed by a four-state finite state machine — ``registered`` -> ``active``
<-> ``suspended`` -> ``retired`` — with deterministic, validated transitions.
``retired`` is terminal; records are never deleted (the append-only
``harnesses`` table guarantees that).

This module is pure logic: the four status constants, the transition graph,
and the functions that decide whether a status transition is permitted. It
imports only the Python standard library and opens no DB connection. The
WI-3340 ``gt harness`` CLI verbs (activate / suspend / resume / retire) consume
these functions to validate every status change.

Transition graph (the literal reading of the FR2 notation)::

    registered --> active
    active     --> suspended
    suspended  --> active
    suspended  --> retired

``retired`` has no outgoing edges. There is no direct ``active -> retired``
edge; retiring an ``active`` harness is the two-step
``active -> suspended -> retired``.

Authority: ``REQ-HARNESS-REGISTRY-001`` (FR2); ``DELIB-2079`` Q3 (four-state
lifecycle FSM, a single enum).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

STATUS_REGISTERED = "registered"
STATUS_ACTIVE = "active"
STATUS_SUSPENDED = "suspended"
STATUS_RETIRED = "retired"

HARNESS_STATUSES: frozenset[str] = frozenset({STATUS_REGISTERED, STATUS_ACTIVE, STATUS_SUSPENDED, STATUS_RETIRED})

# The FR2 transition graph: each status maps to the frozenset of permitted
# successor states. ``retired`` is terminal (empty successor set).
_TRANSITIONS: dict[str, frozenset[str]] = {
    STATUS_REGISTERED: frozenset({STATUS_ACTIVE}),
    STATUS_ACTIVE: frozenset({STATUS_SUSPENDED}),
    STATUS_SUSPENDED: frozenset({STATUS_ACTIVE, STATUS_RETIRED}),
    STATUS_RETIRED: frozenset(),
}


def _require_known_status(status: str, *, role: str = "") -> str:
    """Return ``status`` if it is one of the four FR2 states; else raise.

    ``role`` ("source" / "target") is woven into the error message so a caller
    validating a transition sees which end of the transition was unknown.
    """
    if status not in HARNESS_STATUSES:
        prefix = f"unknown harness {role} status" if role else "unknown harness status"
        raise ValueError(f"{prefix} {status!r}; expected one of {sorted(HARNESS_STATUSES)}")
    return status


def next_states(status: str) -> frozenset[str]:
    """Return the permitted successor states for ``status``.

    Raises ``ValueError`` if ``status`` is not one of the four FR2 states. A
    terminal status (``retired``) returns an empty frozenset.
    """
    _require_known_status(status)
    return _TRANSITIONS[status]


def is_terminal(status: str) -> bool:
    """Return ``True`` iff ``status`` is terminal (no outgoing transitions).

    Raises ``ValueError`` if ``status`` is not one of the four FR2 states.
    """
    return not next_states(status)


def is_valid_transition(from_status: str, to_status: str) -> bool:
    """Return ``True`` iff ``from_status -> to_status`` is a permitted FR2 edge.

    Returns ``False`` — never raises — for an unknown ``from_status`` or
    ``to_status``, and for a same-state pair (a same-state pair is not a
    transition edge).
    """
    if from_status not in HARNESS_STATUSES or to_status not in HARNESS_STATUSES:
        return False
    return to_status in _TRANSITIONS[from_status]


def validate_transition(from_status: str, to_status: str) -> None:
    """Validate a harness status transition; return ``None`` if permitted.

    Raises ``ValueError`` with an informative message when ``from_status`` or
    ``to_status`` is not a known state, or when the transition is not a
    permitted FR2 edge. The message names the offending states and the
    permitted successors of ``from_status``.
    """
    _require_known_status(from_status, role="source")
    _require_known_status(to_status, role="target")
    if to_status not in _TRANSITIONS[from_status]:
        permitted = sorted(_TRANSITIONS[from_status])
        permitted_text = ", ".join(permitted) if permitted else "(none; terminal)"
        raise ValueError(
            f"invalid harness lifecycle transition {from_status!r} -> "
            f"{to_status!r}; permitted transitions from {from_status!r}: "
            f"{permitted_text}"
        )
