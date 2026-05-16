"""Tests for the harness lifecycle finite state machine (WI-3339).

Spec-derived tests for ``REQ-HARNESS-REGISTRY-001`` FR2: the four-state
lifecycle FSM, its deterministic validated transitions, and the terminal
``retired`` state.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import pytest

from groundtruth_kb.harness_lifecycle import (
    HARNESS_STATUSES,
    STATUS_ACTIVE,
    STATUS_REGISTERED,
    STATUS_RETIRED,
    STATUS_SUSPENDED,
    is_terminal,
    is_valid_transition,
    next_states,
    validate_transition,
)

# The four FR2 transition edges.
_VALID_EDGES = [
    (STATUS_REGISTERED, STATUS_ACTIVE),
    (STATUS_ACTIVE, STATUS_SUSPENDED),
    (STATUS_SUSPENDED, STATUS_ACTIVE),
    (STATUS_SUSPENDED, STATUS_RETIRED),
]

# Representative non-edges: skipped states, backward moves, the deliberately
# absent direct active->retired edge, transitions out of the terminal state,
# and same-state pairs.
_INVALID_PAIRS = [
    (STATUS_REGISTERED, STATUS_RETIRED),
    (STATUS_REGISTERED, STATUS_SUSPENDED),
    (STATUS_ACTIVE, STATUS_RETIRED),
    (STATUS_ACTIVE, STATUS_REGISTERED),
    (STATUS_RETIRED, STATUS_ACTIVE),
    (STATUS_RETIRED, STATUS_SUSPENDED),
    (STATUS_REGISTERED, STATUS_REGISTERED),
    (STATUS_ACTIVE, STATUS_ACTIVE),
    (STATUS_SUSPENDED, STATUS_SUSPENDED),
]


def test_four_states_defined() -> None:
    assert HARNESS_STATUSES == {
        STATUS_REGISTERED,
        STATUS_ACTIVE,
        STATUS_SUSPENDED,
        STATUS_RETIRED,
    }
    assert len(HARNESS_STATUSES) == 4


@pytest.mark.parametrize(("src", "dst"), _VALID_EDGES)
def test_valid_transitions_accepted(src: str, dst: str) -> None:
    assert is_valid_transition(src, dst) is True
    # validate_transition returns None (does not raise) on a permitted edge.
    assert validate_transition(src, dst) is None


@pytest.mark.parametrize(("src", "dst"), _INVALID_PAIRS)
def test_invalid_transitions_rejected(src: str, dst: str) -> None:
    assert is_valid_transition(src, dst) is False
    with pytest.raises(ValueError):
        validate_transition(src, dst)


def test_retired_is_terminal() -> None:
    assert is_terminal(STATUS_RETIRED) is True
    assert next_states(STATUS_RETIRED) == frozenset()
    for status in (STATUS_REGISTERED, STATUS_ACTIVE, STATUS_SUSPENDED):
        assert is_terminal(status) is False


def test_validate_transition_raises_on_invalid() -> None:
    with pytest.raises(ValueError, match="invalid harness lifecycle transition"):
        validate_transition(STATUS_ACTIVE, STATUS_RETIRED)
    # The message names the offending states and the permitted successors.
    try:
        validate_transition(STATUS_ACTIVE, STATUS_RETIRED)
    except ValueError as exc:
        text = str(exc)
        assert STATUS_ACTIVE in text
        assert STATUS_RETIRED in text
        assert STATUS_SUSPENDED in text  # the permitted successor of active


def test_unknown_status_rejected() -> None:
    assert is_valid_transition("bogus", STATUS_ACTIVE) is False
    assert is_valid_transition(STATUS_ACTIVE, "bogus") is False
    with pytest.raises(ValueError, match="unknown harness"):
        validate_transition("bogus", STATUS_ACTIVE)
    with pytest.raises(ValueError, match="unknown harness"):
        validate_transition(STATUS_ACTIVE, "bogus")
    with pytest.raises(ValueError, match="unknown harness"):
        next_states("bogus")
    with pytest.raises(ValueError, match="unknown harness"):
        is_terminal("bogus")


def test_next_states_per_state() -> None:
    assert next_states(STATUS_REGISTERED) == frozenset({STATUS_ACTIVE})
    assert next_states(STATUS_ACTIVE) == frozenset({STATUS_SUSPENDED})
    assert next_states(STATUS_SUSPENDED) == frozenset({STATUS_ACTIVE, STATUS_RETIRED})
    assert next_states(STATUS_RETIRED) == frozenset()
